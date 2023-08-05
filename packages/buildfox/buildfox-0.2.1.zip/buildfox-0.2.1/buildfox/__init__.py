#!/usr/bin/env python

# BuildFox ninja generator, v0.2

# The MIT License (MIT)
#
# Copyright (c) 2015 Dmytro Ivanov
#                    Denys Mentiei
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import os
import re
import sys
import uuid
import copy
import glob
import shlex
import shutil
import argparse
import platform
import subprocess
import collections

# parser regexes
re_newline_escaped = re.compile("\$+$")
re_identifier = re.compile("[a-zA-Z0-9\${}_.-]+")
re_path = re.compile(r"(r?\"(?:\\\"|.)*?\")|((\$\||\$ |\$:|[^ :|\n])+)")

class Parser:
	def __init__(self, engine, filename, text = None):
		self.engine = engine
		self.filename = filename
		self.whitespace_nested = None
		self.comments = []
		self.empty_lines = 0
		if text:
			self.lines = text.splitlines()
		else:
			with open(self.filename, "r") as f:
				self.lines = f.read().splitlines()

	# parse everything
	def parse(self):
		self.line_i = 0
		while self.next_line():
			# root objects must have zero whitespace offset
			if self.whitespace != 0:
				raise ValueError("unexpected indentation in '%s' (%s:%i), root entries must have zero whitespace identation" % (
					self.line,
					self.filename,
					self.line_num
				))
			self.parse_line()

	def parse_line(self):
		self.command = self.read_identifier()

		self.engine.current_line = self.line
		self.engine.current_line_i = self.line_num

		if self.empty_lines:
			self.engine.on_empty_lines(self.empty_lines)
			self.empty_lines = 0

		if len(self.comments):
			for comment in self.comments:
				self.engine.on_comment(comment)
			self.comments = []

		if self.command == "rule":
			obj = self.read_rule()
			assigns = self.read_nested_assigns()
			self.engine.on_rule(obj, assigns)

		elif self.command == "build":
			obj = self.read_build()
			assigns = self.read_nested_assigns()
			self.engine.on_build(obj, assigns)

		elif self.command == "default":
			obj = self.read_default()
			self.engine.on_default(obj)

		elif self.command == "pool":
			obj = self.read_pool()
			assigns = self.read_nested_assigns()
			self.engine.on_pool(obj, assigns)

		elif self.command == "include":
			obj = self.read_include()
			self.engine.on_include(obj)

		elif self.command == "subninja" or self.command == "subfox":
			obj = self.read_subninja()
			self.engine.on_subninja(obj)

		elif self.command == "filter":
			obj = self.read_filter()
			need_to_parse = self.engine.filter(obj)
			self.process_filtered(need_to_parse)

		elif self.command == "auto":
			obj = self.read_auto()
			assigns = self.read_nested_assigns()
			self.engine.on_auto(obj, assigns)

		elif self.command == "print":
			obj = self.read_print()
			self.engine.on_print(obj)

		elif self.command == "transformer":
			obj = self.read_transformer()
			self.engine.on_transform(obj)

		else:
			obj = self.read_assign()
			self.engine.on_assign(obj)

	def read_rule(self):
		rule = self.read_identifier()
		self.read_eol()
		return rule

	def read_build(self):
		self.expect_token()
		targets_explicit = []
		targets_implicit = []
		inputs_explicit = []
		inputs_implicit = []
		inputs_order = []

		# read targets explicit
		while self.line_stripped[0] not in ["|", ":"]:
			targets_explicit.append(self.read_path())
			self.expect_token()

		# read targets implicit
		if self.line_stripped[0] == "|":
			self.line_stripped = self.line_stripped[1:].strip()
			self.expect_token()
			while self.line_stripped[0] != ":":
				targets_implicit.append(self.read_path())
				self.expect_token()

		# read rule name
		self.expect_token(":")
		self.line_stripped = self.line_stripped[1:].strip()
		rule = self.read_identifier()

		if self.line_stripped:
			# read inputs explicit
			while self.line_stripped and (self.line_stripped[0] != "|"):
				inputs_explicit.append(self.read_path())

			# read inputs implicit
			if (len(self.line_stripped) >= 2) and (self.line_stripped[0] == "|") and (self.line_stripped[1] != "|"):
				self.line_stripped = self.line_stripped[1:].strip()
				while self.line_stripped and (self.line_stripped[0] != "|"):
					inputs_implicit.append(self.read_path())

			# read inputs order
			if self.line_stripped and (self.line_stripped[0] == "|") and (self.line_stripped[1] == "|"):
				self.line_stripped = self.line_stripped[2:].strip()
				while self.line_stripped:
					inputs_order.append(self.read_path())

		self.read_eol()
		return (
			targets_explicit,
			targets_implicit,
			rule,
			inputs_explicit,
			inputs_implicit,
			inputs_order
		)

	def read_default(self):
		self.expect_token()
		paths = []
		while self.line_stripped:
			paths.append(self.read_path())
		self.read_eol()
		return paths

	def read_pool(self):
		pool = self.read_identifier()
		self.read_eol()
		return pool

	def read_include(self):
		return self.read_one_path()

	def read_subninja(self):
		return self.read_one_path()

	def read_one_path(self):
		path = self.read_path()
		self.read_eol()
		return path

	def read_filter(self):
		self.expect_token()
		filters = []
		while self.line_stripped:
			name = self.read_identifier()
			self.expect_token(":")
			self.line_stripped = self.line_stripped[1:].strip()
			value = self.read_path()
			filters.append((name, value))
		self.read_eol()
		return filters

	def process_filtered(self, need_to_parse, parse_nested_assigns = False, nested_assigns_list = None):
		ws_ref = self.whitespace
		while self.line_i < len(self.lines):
			start_i = self.line_i
			if not self.next_line(preserve_comments = need_to_parse):
				break
			# if offset is less then two spaces
			# then we stop processing
			if self.whitespace <= ws_ref + 1:
				self.line_i = start_i
				break
			if need_to_parse: # if we know that filter is disabled, no need to parse then
				if parse_nested_assigns:
					self.read_nested_assign(nested_assigns_list)
				else:
					self.parse_line()

	def read_auto(self):
		self.expect_token()
		targets = []
		inputs = []

		# read targets
		while self.line_stripped[0] != ":":
			targets.append(self.read_path())
			self.expect_token()

		# read rule name
		self.expect_token(":")
		self.line_stripped = self.line_stripped[1:].strip()
		rule = self.read_identifier()

		# read inputs
		self.expect_token()
		while self.line_stripped:
			inputs.append(self.read_path())
		self.read_eol()
		return (targets, rule, inputs)

	def read_transformer(self):
		self.expect_token()

		name = self.read_identifier()
		self.expect_token(":")
		pattern = self.line_stripped = self.line_stripped[1:].strip()

		return (name, pattern)

	def read_print(self):
		return self.line_stripped.strip()

	def read_assign(self):
		op = self.read_assign_op()
		value = self.line_stripped
		return (self.command, value, op)

	def read_nested_assigns(self):
		all = []
		while self.next_nested():
			self.read_nested_assign(all)
		return all

	def read_nested_assign(self, assign_list):
		name = self.read_identifier()
		if name == "filter" and self.line_stripped and (not self.line_stripped.startswith(("=", "+=", "-="))):
			obj = self.read_filter()
			need_to_parse = self.engine.filter(obj, nested_assigns = assign_list)
			self.process_filtered(need_to_parse, parse_nested_assigns = True, nested_assigns_list = assign_list)
		else:
			op = self.read_assign_op()
			value = self.line_stripped
			assign_list.append((name, value, op))

	def read_assign_op(self):
		# TODO make it nicer
		self.expect_token(("=", "+=", "-="))
		if self.line_stripped[0] == "+":
			# don't strip whitespace here
			# because we want to preserve it so we can process it correctly
			self.line_stripped = self.line_stripped[2:]
			return "+="
		elif self.line_stripped[0] == "-":
			# don't strip whitespace here
			# because we want to preserve it so we can process it correctly
			self.line_stripped = self.line_stripped[2:]
			return "-="
		else:
			self.line_stripped = self.line_stripped[1:].strip()
			return "="

	def read_identifier(self):
		identifier = re_identifier.match(self.line_stripped)
		if not identifier:
			raise ValueError("expected token 'identifier' in '%s' (%s:%i)" % (
				self.line_stripped,
				self.filename,
				self.line_num
			))
		self.line_stripped = self.line_stripped[identifier.span()[1]:].strip()
		return identifier.group()

	def expect_token(self, name = ""):
		if name:
			if (not self.line_stripped) or (not self.line_stripped.startswith(name)):
				raise ValueError("expected token '%s' in '%s' (%s:%i)" % (
					str(name),
					self.line_stripped,
					self.filename,
					self.line_num
				))
		else:
			if not self.line_stripped:
				raise ValueError("expected token(s) in '%s' (%s:%i)" % (
					self.line_stripped,
					self.filename,
					self.line_num
				))

	def read_path(self):
		path = re_path.match(self.line_stripped)
		if not path:
			raise ValueError("expected token 'path' in '%s' (%s:%i)" % (
				self.line_stripped,
				self.filename,
				self.line_num
			))
		self.line_stripped = self.line_stripped[path.span()[1]:].strip()
		return path.group()

	def read_eol(self):
		if self.line_stripped:
			raise ValueError("unexpected token '%s' in '%s' (%s:%i)" % (
				self.line_stripped,
				self.line,
				self.filename,
				self.line_num
			))

	# try to read next nested line, roll-back if not successful
	def next_nested(self):
		start_i = self.line_i
		ws_ref = self.whitespace
		comments_len = len(self.comments)
		empty_lines = self.empty_lines
		if not self.next_line():
			self.whitespace_nested = None
			return False
		if not self.whitespace_nested:
			if self.whitespace > ws_ref + 1: # at least two spaces
				self.whitespace_nested = self.whitespace
				return True
			else:
				self.line_i = start_i
				self.comments = self.comments[:comments_len]
				self.empty_lines = empty_lines
				return False
		else:
			if self.whitespace == self.whitespace_nested:
				return True
			else:
				self.line_i = start_i
				self.whitespace_nested = None
				self.comments = self.comments[:comments_len]
				self.empty_lines = empty_lines
				return False

	def next_line(self, preserve_comments = True):
		if self.line_i >= len(self.lines):
			return False

		self.line_stripped = ""
		while (not self.line_stripped) and (self.line_i < len(self.lines)):
			self.line = ""
			self.line_num = self.line_i + 1

			# dealing with escaped newlines
			newline_escaped = True
			while newline_escaped and (self.line_i < len(self.lines)):
				self.line += self.lines[self.line_i]
				self.line_i += 1
				if self.line.endswith("$"):
					# TODO rewrite this
					newline_escaped = re_newline_escaped.search(self.line)
					#newline_escaped = None
					# TODO replace with proper regex !
					if newline_escaped:
						l, r = newline_escaped.span()
						# in some cases we can have $$, $$$$, etc in the end
						# which are escaped $ combinations, and they don't escape newline
						if (r - l) % 2:
							# in case if they do $, $$$, etc, we need to strip last one
							self.line = self.line[:-1]
						else:
							newline_escaped = None
				else:
					newline_escaped = None

			# line is ready for processing
			self.line_stripped = self.line.strip()

			# skip empty lines
			if not self.line_stripped:
				if preserve_comments:
					self.empty_lines += 1
				continue

			# strip comment
			if self.line_stripped and self.line_stripped[0] == "#":
				if preserve_comments:
					self.comments.append(self.line_stripped[1:])
				self.line_stripped = ""
				continue

		# if we can't skip empty lines, than just return failure
		if not self.line_stripped:
			return False

		# get whitespace
		self.whitespace = self.line[:self.line.index(self.line_stripped)]
		self.whitespace = self.whitespace.replace("\t", "    ")
		self.whitespace = len(self.whitespace)
		return True

def parse(engine, filename, text = None):
	parser = Parser(engine, filename, text)
	parser.parse()

if sys.version_info[0] < 3:
	string_types = basestring
else:
	string_types = str

# match and capture variable and escaping pairs of $$ before variable name
re_var = re.compile("(?<!\$)((?:\$\$)*)\$({)?([a-zA-Z0-9_.-]+)(?(2)})")
re_alphanumeric = re.compile(r"\W+") # match valid parts of filename
re_subst = re.compile(r"(?<!\$)(?:\$\$)*\$\{(param|path|file)\}")
re_non_escaped_space = re.compile(r"(?<!\$)(?:\$\$)* +")
re_path_transform = re.compile(r"^([a-zA-Z0-9_.-]+)\((.*?)(?<!\$)(?:\$\$)*\)$")
re_base_escaped = re.compile(r"\$([\| :()])")

class Engine:
	class Context:
		def __init__(self):
			# key is folder name that ends /, value is set of file names
			self.generated = collections.defaultdict(set)
			# key is folder name, value is set of file names
			self.all_files = collections.defaultdict(set)
			# number of generated subninja files
			self.subninja_num = 0

	def __init__(self, parent = None):
		if not parent:
			self.variables = {} # name: value
			self.auto_presets = {} # name: (inputs, outputs, assigns)
			self.rel_path = "" # this should be prepended to all parsed paths
			self.rules = {} # rule_name: {var_name: var_value}
			self.transformers = {} # target: pattern
			self.excluded_dirs = set()
			self.context = Engine.Context()
		else:
			self.variables = copy.copy(parent.variables)
			self.auto_presets = copy.copy(parent.auto_presets)
			self.rel_path = parent.rel_path
			self.rules = copy.copy(parent.rules)
			self.transformers = copy.copy(parent.transformers)
			self.excluded_dirs = copy.copy(parent.excluded_dirs)
			self.context = parent.context
		self.output = []
		self.need_eval = False
		self.filename = ""
		self.current_line = ""
		self.current_line_i = 0
		self.rules_were_added = False

	# load manifest
	def load(self, filename, logo = True):
		self.filename = filename
		self.rel_path = rel_dir(filename)
		if logo:
			self.output.append("# generated with love by buildfox from %s" % filename)
		self.write_rel_path()
		parse(self, filename)

	# load core definitions
	def load_core(self, fox_core):
		self.filename = "fox_core.fox"
		self.rel_path = ""
		self.write_rel_path()
		parse(self, self.filename, text = fox_core)

	# return output text
	def text(self):
		return "\n".join(self.output) + "\n"

	def save(self, filename):
		if filename:
			with open(filename, "w") as f:
				f.write(self.text())
		else:
			print(self.text())

	def eval(self, text):
		if text == None:
			return None
		elif isinstance(text, string_types):
			raw = text.startswith("r\"")

			# first remove escaped sequences
			if not raw:
				def repl_escaped(matchobj):
					return matchobj.group(1)
				text = re_base_escaped.sub(repl_escaped, text)

			# then do variable substitution
			def repl(matchobj):
				prefix = matchobj.group(1)
				name = matchobj.group(3)
				if matchobj.group(2):
					default = "${%s}" % name
				else:
					default = "$%s" % name
				return prefix + self.variables.get(name, default)

			if "$" in text:
				text = re_var.sub(repl, text)

				# and finally fix escaped $ but escaped variables
				if not raw:
					text = text.replace("$$", "$")

			return text
		else:
			return [self.eval(str) for str in text]

	# evaluate and find files
	def eval_find_files(self, input, output = None):
		return find_files(self.eval_path_transform(input),
						  self.eval_path_transform(output),
						  rel_path = self.rel_path,
						  generated = self.context.generated,
						  excluded_dirs = self.excluded_dirs)

	def add_files(self, files):
		if not files:
			return
		for file in files:
			dir, name = os.path.split(file)
			dir = dir + "/" if dir else "./"
			self.context.all_files[dir].add(name)

	def add_generated_files(self, files):
		if not files:
			return
		for file in files:
			dir = os.path.dirname(file)
			dir = dir + "/" if dir else "./"
			name = os.path.basename(file)
			if name in self.context.generated[dir]:
				raise ValueError("two or more commands generate target '%s' in '%s' (%s:%i), each target must be generated only once" % (
					file,
					self.current_line,
					self.filename,
					self.current_line_i,
				))
			else:
				self.context.generated[dir].add(name)

	def eval_auto(self, inputs, outputs):
		for rule_name, auto in self.auto_presets.items(): # name: (inputs, outputs, assigns)
			# check if all inputs match required auto inputs
			for auto_input in auto[0]:
				regex = wildcard_regex(auto_input)
				if regex:
					re_regex = re.compile(regex)
					match = all(re_regex.match(input) for input in inputs)
				else:
					match = all(input == auto_input for input in inputs)
				if not match:
					break
			if not match:
				continue
			# check if all outputs match required auto outputs
			for auto_output in auto[1]:
				regex = wildcard_regex(auto_output)
				if regex:
					re_regex = re.compile(regex)
					match = all(re_regex.match(output) for output in outputs)
				else:
					match = all(output == auto_output for output in outputs)
				if not match:
					break
			if not match:
				continue
			# if everything match - return rule name and variables
			return rule_name, auto[2]
		# if no rule found then just fail and optionally return None 
		raise ValueError(("unable to deduce auto rule in '%s', " +
			"please check if your file extensions are supported by current toolchain (%s:%i) " +
			"please also mind that file extensions like object files ('.o' and '.obj') and " + 
			"executables may differ between platforms, so you should use transforms to make them work, " +
			"for example 'build objects(*): auto *.cpp' instead of 'build *.obj: auto *.cpp'") % (
			self.current_line,
			self.filename,
			self.current_line_i
		))
		return None, None

	def eval_filter(self, name, regex_or_value):
		value = self.variables.get(name, "")
		regex = wildcard_regex(regex_or_value)
		if regex:
			return re.match(regex, value)
		else:
			return regex_or_value == value

	def eval_assign_op(self, value, prev_value, op):
		if op == "+=":
			return prev_value + value
		elif op == "-=":
			if value in prev_value:
				return prev_value.replace(value, "")
			else:
				return prev_value.replace(value.strip(), "")
		else:
			return value

	def eval_path_transform(self, value):
		if value == None:
			return None
		elif isinstance(value, string_types):
			if value.startswith("r\""):
				return value
			def path_transform(matchobj):
				name = matchobj.group(1)
				value = matchobj.group(2)
				return self.eval_transform(name, value, eval = False)
			if "(" in value:
				value = re_path_transform.sub(path_transform, value)
			return self.eval(value)
		else:
			return [self.eval_path_transform(str) for str in value]

	def eval_transform(self, name, values, eval = True):
		transformer = self.transformers.get(name)
		if transformer is None:
			return self.eval(values) if eval else values

		# transform one value with transformer template
		def transform_one(value):
			if not value:
				return ""
			split = os.path.split(value)
			value_split = {
				"param": value,
				"path": (split[0] + "/" if split[0] else ""),
				"file": split[1]
			}
			value = re_subst.sub(lambda mathobj: value_split.get(mathobj.group(1)), transformer)
			# TODO not sure what effects eval = False give here
			return self.eval(value) if eval else value

		transformed = [transform_one(v) for v in re_non_escaped_space.split(values)]
		return " ".join(transformed)

	def write_assigns(self, assigns):
		local_scope = {}
		for assign in assigns:
			name = self.eval(assign[0])
			value = self.eval_transform(name, assign[1])
			op = assign[2]

			if name in local_scope:
				value = self.eval_assign_op(value, local_scope.get(name), op)
			else:
				value = self.eval_assign_op(value, self.variables.get(name, ""), op)

			self.output.append("  %s = %s" % (name, self.to_esc(value, simple = True)))
			local_scope[name] = value

	def write_rel_path(self):
		self.on_assign(("rel_path", self.rel_path, "="))

	def on_empty_lines(self, lines):
		self.output.extend([""] * lines)

	def on_comment(self, comment):
		self.output.append("#" + comment)

	def on_rule(self, obj, assigns):
		self.rules_were_added = True

		rule_name = self.eval(obj)
		self.output.append("rule " + rule_name)
		vars = {}
		for assign in assigns:
			name = self.eval(assign[0])
			# do not evaluate value here and also do not do any from_esc / to_esc here
			# just pass value as raw string to output
			# TODO but do we need eval_transform here ?
			value = assign[1]
			op = assign[2]

			# only = is supported because += and -= are not native ninja features
			# and rule nested variables are evaluated in ninja
			# so there is no way to implement this in current setup
			if op != "=":
				raise ValueError("only \"=\" is supported in rule nested variables, "\
								 "got invalid assign operation '%s' at rule '%s' (%s:%i)" % (
					op,
					self.current_line,
					self.filename,
					self.current_line_i,
				))
			vars[name] = value
			if name != "expand":
				self.output.append("  %s = %s" % (name, value))
		self.rules[rule_name] = vars

	def on_build(self, obj, assigns):
		inputs_explicit, targets_explicit = self.eval_find_files(obj[3], obj[0])
		targets_implicit = self.eval_find_files(obj[1])
		rule_name = self.eval(obj[2])
		inputs_implicit = self.eval_find_files(obj[4])
		inputs_order = self.eval_find_files(obj[5])

		self.add_files(inputs_explicit)
		self.add_files(inputs_implicit)
		self.add_files(inputs_order)
		self.add_files(targets_explicit)
		self.add_files(targets_implicit)
		self.add_generated_files(targets_explicit)
		self.add_generated_files(targets_implicit)

		# deduce auto rule
		if rule_name == "auto":
			name, vars = self.eval_auto(inputs_explicit, targets_explicit)
			rule_name = name
			assigns = vars + assigns

		# rule should exist
		if rule_name != "phony" and rule_name not in self.rules:
			raise ValueError("unknown rule %s at '%s' (%s:%i), available rules : %s" % (
				rule_name,
				self.current_line,
				self.filename,
				self.current_line_i,
				" ".join(list(self.rules.keys()) + ["auto", "phony"])
			))

		# you probably want to match some files
		def warn_no_files(type):
			print("Warning, no %s input files matched for '%s' (%s:%i)" % (
				type,
				self.current_line,
				self.filename,
				self.current_line_i,
			))
		if (obj[3] and not inputs_explicit):
			warn_no_files("explicit")
		if (obj[4] and not inputs_implicit):
			warn_no_files("implicit")
		if (obj[5] and not inputs_order):
			warn_no_files("order-only")

		# expand this rule
		expand = self.rules.get(rule_name, {}).get("expand", None)

		if expand:
			# TODO probably this expand implementation is not enough

			if len(targets_explicit) != len(inputs_explicit):
				raise ValueError(("cannot expand rule %s because of different amount of explicit generated targets and explicit inputs at '%s' (%s:%i), " +
					"to expand this rule build command must have equal amounts of explicit targets and explicit inputs, for example \"build a b c: rule i j k\"") % (
					rule_name,
					self.current_line,
					self.filename,
					self.current_line_i,
				))

			for target_index, target in enumerate(targets_explicit):
				input = inputs_explicit[target_index]

				self.output.append("build %s: %s %s%s%s" % (
					self.to_esc(target),
					rule_name,
					self.to_esc(input),
					" | " + " ".join(self.to_esc(inputs_implicit)) if inputs_implicit else "",
					" || " + " ".join(self.to_esc(inputs_order)) if inputs_order else "",
				))

				self.write_assigns(assigns)

		else:
			self.output.append("build %s: %s%s%s%s" % (
				" ".join(self.to_esc(targets_explicit)),
				rule_name,
				" " + " ".join(self.to_esc(inputs_explicit)) if inputs_explicit else "",
				" | " + " ".join(self.to_esc(inputs_implicit)) if inputs_implicit else "",
				" || " + " ".join(self.to_esc(inputs_order)) if inputs_order else "",
			))

			self.write_assigns(assigns)

		if targets_implicit: # TODO remove this when https://github.com/martine/ninja/pull/989 is merged
			self.output.append("build %s: phony %s" % (
				" ".join(self.to_esc(targets_implicit)),
				" ".join(self.to_esc(targets_explicit)),
			))

	def on_default(self, obj):
		paths = self.eval_find_files(obj)
		self.output.append("default " + " ".join(self.to_esc(paths)))

	def on_pool(self, obj, assigns):
		name = self.eval(obj)
		self.output.append("pool " + name)
		self.write_assigns(assigns)

	def filter(self, obj, nested_assigns = None):
		nested_names = [self.eval(assign[0]) for assign in nested_assigns] if nested_assigns else []
		for filt in obj:
			name = self.eval(filt[0])
			if name in nested_names:
				raise ValueError(("Warning ! filtering on nested variables ('%s' in this case) is not supported in '%s' (%s:%i), "
					"instead please only filter on global variables") % (
					name,
					self.current_line,
					self.filename,
					self.current_line_i,
				))
				
			value = self.eval(filt[1])
			if not self.eval_filter(name, value):
				return False
		return True

	def on_auto(self, obj, assigns):
		outputs = self.eval(obj[0]) # this shouldn't be find_files !
		name = self.eval(obj[1])
		inputs = self.eval(obj[2]) # this shouldn't be find_files !
		self.auto_presets[name] = (inputs, outputs, assigns)

	def on_print(self, obj):
		print(self.eval(obj))

	def on_assign(self, obj):
		name = self.eval(obj[0])
		value = self.eval_transform(name, obj[1])
		op = obj[2]

		value = self.eval_assign_op(value, self.variables.get(name), op)

		if name == "buildfox_required_version":
			# Checking the version immediately to fail fast.
			version_check(value)
		elif name == "excluded_dirs":
			self.excluded_dirs = set(re_non_escaped_space.split(value))

		self.variables[name] = value
		self.output.append("%s = %s" % (name, self.to_esc(value, simple = True)))

	def on_transform(self, obj):
		target = self.eval(obj[0])
		pattern = obj[1] # do not eval it here
		self.transformers[target] = pattern

	def on_include(self, obj):
		paths = self.eval_find_files([obj])
		for path in paths:
			old_rel_path = self.rel_path
			self.rel_path = rel_dir(path)
			self.write_rel_path()
			parse(self, path)
			self.rel_path = old_rel_path

	def on_subninja(self, obj):
		paths = self.eval_find_files([obj])
		for path in paths:
			gen_filename = "__gen_%i_%s.ninja" % (
				self.context.subninja_num,
				re_alphanumeric.sub("", os.path.splitext(os.path.basename(path))[0])
			)
			self.context.subninja_num += 1

			engine = Engine(self)
			engine.load(path)
			engine.save(gen_filename)

			# we depend on scoped rules so let's enforce 1.6 version if you use rules
			if engine.rules_were_added:
				self.on_assign(("ninja_required_version", "1.6", "="))

			self.rules_were_added = self.rules_were_added or engine.rules_were_added
			self.output.append("subninja " + self.to_esc(gen_filename))

	def to_esc(self, value, simple = False):
		if value == None:
			return None
		elif isinstance(value, string_types):
			value = value.replace("$", "$$")
			if not simple:
				value = value.replace(":", "$:").replace("\n", "$\n").replace(" ", "$ ")
			return value
		else:
			return [self.to_esc(str) for str in value]

def discover():
	vars = {
		"variation": "debug"
	}

	if which("cl") and which("link") and which("lib"):
		vars["toolset_msc"] = "true"
		if os.environ.get("VS140COMNTOOLS"):
			vars["toolset_msc_ver"] = "2015"
		elif os.environ.get("VS130COMNTOOLS"):
			vars["toolset_msc_ver"] = "2013"
		elif os.environ.get("VS120COMNTOOLS"):
			vars["toolset_msc_ver"] = "2012"

	if which("clang"):
		vars["toolset_clang"] = "true"

	if which("gcc") and which("g++"):
		vars["toolset_gcc"] = "true"

	if vars.get("toolset_msc"):
		vars["toolset"] = "msc"
	elif vars.get("toolset_clang"):
		vars["toolset"] = "clang"
	elif vars.get("toolset_gcc"):
		vars["toolset"] = "gcc"
	else:
		raise ValueError("Can't find any compiler, expected cl, clang, gcc executables")

	if not which("ninja"):
		print("Warning ! Can't find ninja executable")

	vars["system"] = platform.system()
	vars["machine"] = platform.machine()
	cwd = os.getcwd().replace("\\", "/")
	if cwd and cwd != "." and not cwd.endswith("/"):
		cwd += "/"
	vars["cwd"] = cwd

	return vars

def selftest_setup():
	with open("__selftest_build.fox", "w") as f:
		f.write("""
build objects(__selftest_src): auto __selftest_src.cpp
build application(__selftest_app): auto objects(__selftest_src)
""")

	with open("__selftest_src.cpp", "w") as f:
		f.write("""
#include <iostream>
int main()
{
	std::cout << "Hello from test app !\\n";
	return 0;
}
""")

	return ("__selftest_build.fox", "__selftest_build.ninja", "__selftest_app")

def selftest_wipe():
	for filename in glob.glob("__selftest_*.*"):
		os.remove(filename)
	os.remove(".ninja_deps")
	os.remove(".ninja_log")

re_folder_part = re.compile(r"^((?:\(\[\^\\\/\]\*\)(?:\(\?\![\w\|]+\))?\(\[\^\\\/\]\*\)|(?:[^\r\n(\[\"\\]|\\.))+)(\\\/|\/|\\).*$") # match folder part in filename regex
re_non_escaped_char = re.compile(r"(?<!\\)\\(.)") # looking for not escaped \ with char
re_capture_group_ref = re.compile(r"(?<!\\)\\(p?)(\d+)") # match regex capture group reference
re_pattern_split = re.compile(r"(?<!\[\^)\/")
re_recursive_glob = re.compile(r"\(\[\^\\\/\]\*\)(\(\?\![\w\|]+\))?\(\[\^\\\/\]\*\)\\\/")
re_recursive_glob_noslash = re.compile(r"\(\[\^\/\]\*\)(\(\?\![\w\|]+\))?\(\[\^\/\]\*\)")

# return relative path to current work dir
def rel_dir(filename):
	path = os.path.relpath(os.path.dirname(os.path.abspath(filename)), os.getcwd()).replace("\\", "/") + "/"
	if path == "./":
		path = ""
	return path

# return regex value in filename for regex or wildcard
# replace_groups replace wildcards with group reference indexes
def wildcard_regex(filename, replace_groups = False, rec_capture_groups = set()):
	if filename.startswith("r\""):
		return filename[2:-1] # strip r" and "

	if filename.startswith("\""):
		filename = filename[1:-1] # strip " and "

	if "!" in filename or "*" in filename or "?" in filename or "[" in filename:
		# based on fnmatch.translate with each wildcard is a capture group
		i, n = 0, len(filename)
		groups = 1
		res = ""
		while i < n:
			c = filename[i]
			i = i + 1
			if c == "*":
				if i < n and filename[i] == "*":
					if replace_groups:
						res += "\\p" + str(groups) # p (path) will mean that it's ok to substitute this group with string that may contain slashes
					else:
						res += "([^\/]*)([^\/]*)"
						rec_capture_groups.add(groups)
					i = i + 1
				else:
					if replace_groups:
						# if inputs have recursive capture groups and output don't use them
						# then prepend recursive group to file name and just switch to next non recursive capture group
						while groups in rec_capture_groups:
							res += "\\" + str(groups) + "_"
							groups += 1
						res += "\\" + str(groups)
					else:
						res += "([^\/]*)"
				groups += 1
			elif c == "?":
				if replace_groups:
					res += "\\" + str(groups)
				else:
					res += "([^\/])"
				groups += 1
			elif replace_groups:
				res += c
			elif c == "!":
				j = i
				if j < n and filename[j] == "(":
					j = j + 1
				while j < n and filename[j] != ")":
					j = j + 1
				if j >= n:
					res += "\!"
				else:
					stuff = filename[i + 1: j].replace("\\", "\\\\")
					i = j + 1
					res += "(?!%s)([^\/]*)" % stuff
			elif c == "[":
				j = i
				if j < n and filename[j] == "!":
					j = j + 1
				if j < n and filename[j] == "]":
					j = j + 1
				while j < n and filename[j] != "]":
					j = j + 1
				if j >= n:
					res += "\\["
				else:
					stuff = filename[i:j].replace("\\", "\\\\")
					i = j + 1
					if stuff[0] == "!":
						stuff = "^" + stuff[1:]
					elif stuff[0] == "^":
						stuff = "\\" + stuff
					res = "%s([%s])" % (res, stuff)
			else:
				res += re.escape(c)
		if replace_groups:
			return res
		else:
			return "%s\Z(?ms)" % res
	else:
		return None

# return list of folders (always ends with /) that match provided pattern
# please note that some result folders may point into non existing location
# because it's too costly here to check if they exist
def glob_folders(pattern, base_path, generated, excluded_dirs):
	if not pattern.endswith("/"): # this shouldn't fail
		raise ValueError("pattern should always end with \"/\", but got \"%s\"" % pattern)

	real_folders = [base_path.rstrip("/")]
	gen_folders = [base_path.rstrip("/")]

	pattern = pattern[2:] if pattern.startswith("./") else pattern

	for folder in re_pattern_split.split(pattern):
		recursive_match = re_recursive_glob_noslash.match(folder)
		if recursive_match:
			regex_filter = recursive_match.group(1)
			re_regex_filter = re.compile("^%s.*$" % regex_filter) if regex_filter else None

			new_real_folders = []
			for real_folder in real_folders:
				new_real_folders.append(real_folder)
				for root, dirs, filenames in os.walk(real_folder, topdown = True): # TODO this is slow, optimize
					dirs[:] = [dir for dir in dirs if dir not in excluded_dirs]
					if re_regex_filter:
						dirs[:] = [dir for dir in dirs if re_regex_filter.match(dir)]
					for dir in dirs:
						result = os.path.join(root, dir).replace("\\", "/")
						new_real_folders.append(result)
			real_folders = new_real_folders

			new_gen_folders = []
			for gen_folder in gen_folders:
				prepend_dot = False
				if gen_folder.startswith("./"):
					prepend_dot = True
					gen_folder = gen_folder[2:] # strip ./

				gen_folder_len = len(gen_folder)
				for folder in generated.keys():
					if folder.startswith(gen_folder):
						root = folder[:gen_folder_len]
						sub_folders = folder[gen_folder_len:]
						sub_folders = sub_folders.lstrip("/").rstrip("/")
						# walk through directories in similar fashion with os.walk
						new_gen_folders.append("./%s" % root if prepend_dot else root)
						for subfolder in sub_folders.split("/"): 
							if subfolder in excluded_dirs:
								break
							if re_regex_filter and not re_regex_filter.match(subfolder):
								break
							root += "/%s" % subfolder
							new_gen_folders.append("./%s" % root if prepend_dot else root)
			gen_folders = list(set(new_gen_folders))
		else:
			real_folders = ["%s/%s" % (p, folder) for p in real_folders]
			gen_folders = ["%s/%s" % (p, folder) for p in gen_folders]

	return (real_folders, gen_folders)

# input can be string or list of strings
# outputs are always lists
def find_files(inputs, outputs = None, rel_path = "", generated = None, excluded_dirs = set()):
	# rename regex back to readable form
	def replace_non_esc(match_group):
		return match_group.group(1)
	rec_capture_groups = set()
	if inputs:
		result = []
		matched = []
		for input in inputs:
			regex = wildcard_regex(input, False, rec_capture_groups)
			if regex:
				# find the folder where to look for files
				base_folder = re_folder_part.match(regex)
				lookup_path = rel_path if rel_path else "./"
				real_folders = [lookup_path]
				gen_folders = [lookup_path]
				if base_folder:
					base_folder = base_folder.group(1) + base_folder.group(2)
					base_folder = re_non_escaped_char.sub(replace_non_esc, base_folder)
					if "\\" in base_folder:
						raise ValueError("please only use forward slashes in path \"%s\"" % input)
					real_folders, gen_folders = glob_folders(base_folder, lookup_path, generated, excluded_dirs)

				# look for files
				fs_files = set()
				for real_folder in real_folders:
					if os.path.isdir(real_folder):
						root = real_folder[len(lookup_path):]
						files = [root + file for file in os.listdir(real_folder) if os.path.isfile(real_folder + "/" + file)]
						fs_files = fs_files.union(files)

				gen_files = set()
				for gen_folder in gen_folders:
					# in case if gen_folder is "./something" then we need to strip ./
					# but if gen_folder is just "./" then we don't need to strip it !
					if len(gen_folder) > 2 and gen_folder.startswith("./"):
						check_folder = gen_folder[2:]
					else:
						check_folder = gen_folder
					if check_folder in generated:
						root = gen_folder[len(lookup_path):]
						files = [root + file for file in generated.get(check_folder)]
						gen_files = gen_files.union(files)

				# we must have stable sort here
				# so output ninja files will be same between runs
				all_files = list(fs_files.union(gen_files))
				all_files = sorted(all_files)

				# while capturing ** we want just to capture */ optionally
				# so we can match files in root folder as well
				# please note that result regex will not have folder ignore semantic
				# we rely on glob_folders to filter all ignored folders
				regex = re_recursive_glob.sub("(?:(.*)\/)?", regex)

				# if you want to match something in local folder
				# then you may write wildcard/regex that starts as ./
				if regex.startswith("\.\/"):
					regex = regex[4:]

				re_regex = re.compile(regex)
				for file in all_files:
					match = re_regex.match(file)
					if match:
						result.append(rel_path + file)
						matched.append(match.groups())
			else:
				result.append(rel_path + input)
		inputs = result

	if outputs:
		result = []
		for output in outputs:
			# we want \number instead of capture groups
			regex = wildcard_regex(output, True, rec_capture_groups)

			if regex:
				for match in matched:
					# replace \number with data
					def replace_group(matchobj):
						index = int(matchobj.group(2)) - 1
						if index >= 0 and index < len(match):
							if matchobj.group(1) == "p":
								return match[index] # if capture group have p suffix then pass string as is
							else:
								return match[index].replace("/", "_") if match[index] else None
						else:
							return ""
					file = re_capture_group_ref.sub(replace_group, regex)
					file = re_non_escaped_char.sub(replace_non_esc, file)
					# in case of **/* mask in output, input capture group
					# for ** can be empty, so we get // in output, so just fix it here
					file = file.replace("//", "/").lstrip("/")

					result.append(rel_path + file)
			else:
				result.append(rel_path + output)

		# normalize results
		result = [os.path.normpath(file).replace("\\", "/") for file in result]

	# normalize inputs
	inputs = [os.path.normpath(file).replace("\\", "/") for file in inputs]

	if outputs:
		return inputs, result
	else:
		return inputs

# finds the file in path
def which(cmd, mode = os.F_OK | os.X_OK, path = None):
	if sys.version_info[0:2] >= (3, 3):
		return shutil.which(cmd, mode, path)
	else:
		def _access_check(fn, mode):
			return (os.path.exists(fn) and os.access(fn, mode)
					and not os.path.isdir(fn))

		if os.path.dirname(cmd):
			if _access_check(cmd, mode):
				return cmd
			return None

		if path is None:
			path = os.environ.get("PATH", os.defpath)
		if not path:
			return None
		path = path.split(os.pathsep)

		if sys.platform == "win32":
			if not os.curdir in path:
				path.insert(0, os.curdir)
			pathext = os.environ.get("PATHEXT", "").split(os.pathsep)
			if any(cmd.lower().endswith(ext.lower()) for ext in pathext):
				files = [cmd]
			else:
				files = [cmd + ext for ext in pathext]
		else:
			files = [cmd]

		seen = set()
		for dir in path:
			normdir = os.path.normcase(dir)
			if not normdir in seen:
				seen.add(normdir)
				for thefile in files:
					name = os.path.join(dir, thefile)
					if _access_check(name, mode):
						return name
		return None

# parses string of generic cxx defines and return list of strings
def cxx_defines(defines):
	dirs = shlex.split(defines)
	dirs = [dir[2:] if dir.startswith("/D") or dir.startswith("-D") else dir for dir in dirs]
	dirs = filter(lambda d: len(d), dirs)
	return list(dirs)

# parses string of generic cxx include dirs and return list of strings
def cxx_includedirs(includedirs):
	dirs = shlex.split(includedirs)
	dirs = [dir[2:] if dir.startswith("/I") or dir.startswith("-I") else dir for dir in dirs]
	dirs = filter(lambda d: len(d), dirs)
	return list(dirs)

# find files of intereset in provided all files dict
def cxx_findfiles(all_files):
	ext_of_interest_src = (".c", ".cpp", ".cxx", ".c++", ".cc", ".h", ".hpp", ".hxx", ".in")
	return ["%s%s" % ("" if folder == "./" else folder, name)
			for folder, names in all_files.items()
				for name in names
					if name.lower().endswith(ext_of_interest_src)]

from xml.sax import saxutils

vs_ext_of_interest_src = (".c", ".cpp", ".cxx", ".c++", ".cc", ".h", ".hpp", ".hxx")
vs_ext_of_interest_bin = (".exe")

vs_reference_sln = r"""Microsoft Visual Studio Solution File, Format Version %%%format_version%%%.00
# Visual Studio %%%studio_version%%%
Project("{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}") = "%%%name%%%", "%%%file%%%", "%%%guid%%%"
EndProject
Global
	GlobalSection(SolutionProperties) = preSolution
		HideSolutionNode = FALSE
	EndGlobalSection
EndGlobal"""

vs_reference_prj = r"""<?xml version="1.0" encoding="utf-8"?>
<Project DefaultTargets="Build" ToolsVersion="%%%tools_version%%%.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
	<ItemGroup Label="ProjectConfigurations">
		<ProjectConfiguration Include="Debug|Win32">
			<Configuration>Debug</Configuration>
			<Platform>Win32</Platform>
		</ProjectConfiguration>
		<ProjectConfiguration Include="Release|Win32">
			<Configuration>Release</Configuration>
			<Platform>Win32</Platform>
		</ProjectConfiguration>
	</ItemGroup>
	<PropertyGroup Label="Globals">
		<ProjectName>%%%name%%%</ProjectName>
		<ProjectGuid>%%%guid%%%</ProjectGuid>
		<Keyword>MakeFileProj</Keyword>
	</PropertyGroup>
	<Import Project="$(VCTargetsPath)\Microsoft.Cpp.Default.props" />
	<PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Debug|Win32'" Label="Configuration">
		<ConfigurationType>Makefile</ConfigurationType>
		<UseDebugLibraries>true</UseDebugLibraries>
		<PlatformToolset>v%%%platform_version%%%0</PlatformToolset>
	</PropertyGroup>
	<PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Release|Win32'" Label="Configuration">
		<ConfigurationType>Makefile</ConfigurationType>
		<UseDebugLibraries>false</UseDebugLibraries>
		<PlatformToolset>v%%%platform_version%%%0</PlatformToolset>
	</PropertyGroup>
	<Import Project="$(VCTargetsPath)\Microsoft.Cpp.props" />
	<ImportGroup Label="ExtensionSettings">
	</ImportGroup>
	<ImportGroup Label="PropertySheets" Condition="'$(Configuration)|$(Platform)'=='Debug|Win32'">
		<Import Project="$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props" Condition="exists('$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props')" Label="LocalAppDataPlatform" />
	</ImportGroup>
	<ImportGroup Label="PropertySheets" Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">
		<Import Project="$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props" Condition="exists('$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props')" Label="LocalAppDataPlatform" />
	</ImportGroup>
	<PropertyGroup Label="UserMacros" />
	<PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Debug|Win32'">
		<NMakeBuildCommandLine>%%%nmake_build%%%</NMakeBuildCommandLine>
		<NMakeOutput>%%%output%%%</NMakeOutput>
		<NMakeCleanCommandLine>%%%nmake_clean%%%</NMakeCleanCommandLine>
		<NMakeReBuildCommandLine>%%%nmake_rebuild%%%</NMakeReBuildCommandLine>
		<NMakePreprocessorDefinitions>%%%defines%%%$(NMakePreprocessorDefinitions)</NMakePreprocessorDefinitions>
		<NMakeIncludeSearchPath>%%%includedirs%%%$(NMakeIncludeSearchPath)</NMakeIncludeSearchPath>
	</PropertyGroup>
	<PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">
		<NMakeBuildCommandLine>%%%nmake_build%%%</NMakeBuildCommandLine>
		<NMakeOutput>%%%output%%%</NMakeOutput>
		<NMakeCleanCommandLine>%%%nmake_clean%%%</NMakeCleanCommandLine>
		<NMakeReBuildCommandLine>%%%nmake_rebuild%%%</NMakeReBuildCommandLine>
		<NMakePreprocessorDefinitions>%%%defines%%%$(NMakePreprocessorDefinitions)</NMakePreprocessorDefinitions>
		<NMakeIncludeSearchPath>%%%includedirs%%%$(NMakeIncludeSearchPath)</NMakeIncludeSearchPath>
	</PropertyGroup>
	<ItemDefinitionGroup>
	</ItemDefinitionGroup>
	<ItemGroup>
%%%item_groups%%%
	</ItemGroup>
	<Import Project="$(VCTargetsPath)\Microsoft.Cpp.targets" />
	<ImportGroup Label="ExtensionTargets">
	</ImportGroup>
</Project>"""

vs_reference_flt = r"""<?xml version="1.0" encoding="utf-8"?>
<Project ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
%%%items%%%
%%%filters%%%
</Project>"""

def gen_vs(all_files, defines, includedirs, prj_name, ide, cmd_env):
	interest_src_files = {}
	interest_bin_files = {}
	for folder, files in all_files.items():
		folder = os.path.abspath(folder).replace("/", "\\") + "\\"
		interest_src = set(filter(lambda n: n.lower().endswith(vs_ext_of_interest_src), files))
		interest_bin = set(filter(lambda n: n.lower().endswith(vs_ext_of_interest_bin), files))
		if interest_src:
			interest_src_files[folder] = interest_src
		if interest_bin:
			interest_bin_files[folder] = interest_bin

	output = ["%s%s" % (folder, name)
		for folder, files in interest_bin_files.items() for name in files]
	if len(output) > 1:
		print("more then one generated file is present, so we are choosing '%s' from all generated files :\n%s" % (output[0], "\n".join(output)))
	output = output[0]
	items = "\n".join(["		<ClCompile Include=\"%s%s\"/>" % (folder, name)
		for folder, files in interest_src_files.items() for name in files])

	defines = ";".join(defines) + ";" if defines else ""
	includedirs = ";".join(includedirs) + ";" if includedirs else ""

	# find common folder
	prefix = os.path.commonprefix([os.path.abspath(folder) for folder in interest_src_files.keys()])
	prefix = os.path.dirname(prefix)
	prefix_len = len(prefix)
	if prefix_len and prefix[-1] != "\\":
		prefix_len += 1 # and add slash to it

	flt_filters = []
	flt_items = []
	all_folder_filters = set()
	for folder in interest_src_files.keys():
		folder = folder[prefix_len:-1]
		path = None
		for subfolder in folder.split("\\"):
			path = "%s\\%s" % (path, subfolder) if path else subfolder
			all_folder_filters.add(path)

	for filter_path in all_folder_filters:
		folder_guid = "{%s}" % str(uuid.uuid5(uuid.NAMESPACE_URL, filter_path)).lower()
		filter_folder  = "		<Filter Include=\"%s\">\n" % filter_path
		filter_folder += "			<UniqueIdentifier>%s</UniqueIdentifier>\n" % folder_guid
		filter_folder += "		</Filter>"
		flt_filters.append(filter_folder)

	for folder, files in interest_src_files.items():
		filter_path = folder[prefix_len:-1]
		flt_items.append("\t<ItemGroup>")
		for name in files:
			item  = "		<ClCompile Include=\"%s%s\">\n" % (folder, name)
			item += "			<Filter>%s</Filter>\n" % filter_path
			item += "		</ClCompile>"
			flt_items.append(item)
		flt_items.append("\t</ItemGroup>")
	flt_filters = "\t<ItemGroup>\n%s\n\t</ItemGroup>\n" % "\n".join(flt_filters)
	flt_items = "\n".join(flt_items)

	cmd_env = cmd_env + " && " if cmd_env else ""

	toolset_ver = {
		"vs": "12",
		"vs2012": "4",
		"vs2013": "12",
		"vs2015": "14"
	}
	platform_ver = {
		"vs": "12",
		"vs2012": "11",
		"vs2013": "12",
		"vs2015": "14"
	}
	format_ver = {
		"vs": "13",
		"vs2012": "12",
		"vs2013": "13",
		"vs2015": "14"
	}
	studio_ver = {
		"vs": "2013",
		"vs2012": "2012",
		"vs2013": "2013",
		"vs2015": "2015"
	}

	prj_file = "%s.vcxproj" % prj_name
	prj_guid = "{%s}" % str(uuid.uuid4()).upper()
	prj_text = vs_reference_prj
	prj_text = prj_text.replace("%%%name%%%", prj_name)
	prj_text = prj_text.replace("%%%guid%%%", prj_guid)
	prj_text = prj_text.replace("%%%output%%%", output)
	prj_text = prj_text.replace("%%%defines%%%", defines)
	prj_text = prj_text.replace("%%%includedirs%%%", includedirs)
	prj_text = prj_text.replace("%%%item_groups%%%", items)
	prj_text = prj_text.replace("%%%tools_version%%%", toolset_ver.get(ide))
	prj_text = prj_text.replace("%%%platform_version%%%", platform_ver.get(ide))
	prj_text = prj_text.replace("%%%nmake_build%%%", saxutils.escape(cmd_env + "ninja"))
	prj_text = prj_text.replace("%%%nmake_clean%%%", saxutils.escape("ninja -t clean"))
	prj_text = prj_text.replace("%%%nmake_rebuild%%%", saxutils.escape(cmd_env + "ninja -t clean && ninja"))

	sln_file = "%s.sln" % prj_name
	sln_text = vs_reference_sln
	sln_text = sln_text.replace("%%%name%%%", prj_name)
	sln_text = sln_text.replace("%%%file%%%", prj_file)
	sln_text = sln_text.replace("%%%guid%%%", prj_guid)
	sln_text = sln_text.replace("%%%format_version%%%", format_ver.get(ide))
	sln_text = sln_text.replace("%%%studio_version%%%", studio_ver.get(ide))

	flt_file = "%s.vcxproj.filters" % prj_name
	flt_text = vs_reference_flt
	flt_text = flt_text.replace("%%%filters%%%", flt_filters)
	flt_text = flt_text.replace("%%%items%%%", flt_items)

	with open(prj_file, "w") as f:
		f.write(prj_text)
	with open(sln_file, "w") as f:
		f.write(sln_text)
	with open(flt_file, "w") as f:
		f.write(flt_text)

def gen_make(buildfox_name, cmd_env, ninja_gen_mode, filename = "Makefile"):
	text = """# generated by BuildFox
%s
compile:
	ninja
clean:
	ninja -t clean
"""

	if ninja_gen_mode:
		all = "all: compile"
	else:
		if cmd_env:
			all = "all: set_env configure compile\n"
			all += "set_env:\n"
			all += "\t%s\n" % cmd_env.replace("#", "\\#").replace("$", "$$")
		else:
			all = "all: configure compile\n"
		bf_cmd = "bf -i " + buildfox_name if buildfox_name != "build.fox" else "bf"
		all += "configure:\n"
		all += "\t%s" % bf_cmd

	with open(filename, "w") as f:
		f.write(text % all)

def gen_cmake(all_files, includedirs, prj_name, buildfox_name, cmd_env, filename = "CMakeLists.txt"):
	text = r"""# generated by BuildFox
cmake_minimum_required(VERSION 2.8.3)
project(%s)
include_directories("%s")
add_custom_target(
  build
  ALL %s
  WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}
  VERBATIM
  %s
)
"""

	if cmd_env:
		for chr in ["\\", "\"", "(", ")", "#", "^"]:
			cmd_env = cmd_env.replace(chr, "\\" + chr)
		cmd_env = cmd_env.replace("$", "\\$")

	all_files = ["\"%s\"" % file for file in cxx_findfiles(all_files)]
	includedirs = ["."] + includedirs

	with open(filename, "w") as f:
		f.write(text % (
			prj_name,
			";".join(includedirs),
			cmd_env + " COMMAND ninja" if cmd_env else "ninja",
			"SOURCES " + " ".join(all_files) if all_files else ""
		))

qtcreator_ext_of_interest_src = (".c", ".cpp", ".cxx", ".c++", ".cc", ".h", ".hpp", ".hxx")

def gen_qtcreator(all_files, defines, includedirs, prj_name, buildfox_name, cmd_env, ninja_gen_mode):
	gen_make(buildfox_name, cmd_env, ninja_gen_mode)

	all_files = ["Makefile", buildfox_name] + cxx_findfiles(all_files)
	includedirs = ["."] + includedirs

	with open("%s.creator" % prj_name, "w") as f:
		f.write("[General]\n")
	with open("%s.config" % prj_name, "w") as f:
		f.write("%s\n" % "\n".join(["#define %s" % define for define in defines]))
	with open("%s.includes" % prj_name, "w") as f:
		f.write("%s\n" % "\n".join(includedirs))
	with open("%s.files" % prj_name, "w") as f:
		f.write("%s\n" % "\n".join(all_files))

MAJOR = 0
MINOR = 2
VERSION = "%d.%d" % (MAJOR, MINOR)

# Simple major.minor matcher
re_version = re.compile(r"^(\d+)\.(\d+)$")

def version_check(required_version):
	match = re_version.match(required_version)

	if match:
		required_major = int(match.group(1))
		required_minor = int(match.group(2))
	else:
		raise ValueError("Specified required version %s has incorrect format, for example correct format is 1.0" % required_version)

	if MAJOR > required_major:
		print("WARNING: BuildFox executable major version %s is greater than 'buildfox_required_version' (%s).\nVersions may be incompatible" % (VERSION, required_version))
	elif (required_major == MAJOR and required_minor > MINOR) or required_major > MAJOR:
		raise RuntimeError("BuildFox version %s is incompatible with the version required %s" % (VERSION, required_version))

# core definitions -----------------------------------------------------------

fox_core = r"""
# buildfox core configuration

# buildfox relies on deps and they were added in ninja v1.3
# please note, if you will use subfox/subninja commands
# then requirement will raise up to ninja v1.6 because we depend on scoped rules
ninja_required_version = 1.3

# some basic ignore folders
excluded_dirs = .git .hg .svn

filter toolset:msc
	# msc support
	cc = cl
	cxx = cl
	lib = lib

	rule cc
		command = $cc $cxxflags $defines $includedirs $disable_warnings /nologo /showIncludes -c $in /Fo$out
		description = cc $in
		deps = msvc
		expand = true

	rule cxx
		command = $cxx $cxxflags $defines $includedirs $disable_warnings /nologo /showIncludes -c $in /Fo$out
		description = cxx $in
		deps = msvc
		expand = true

	rule link
		command = $cxx /nologo @$out.rsp /link $ldflags $libdirs $ignore_default_libs /out:$out
		description = link $out
		rspfile = $out.rsp
		rspfile_content = $in $libs

	rule link_so
		command = $cxx /nologo @$out.rsp /link /DLL $ldflags $libdirs $ignore_default_libs /out:$out
		description = link $out
		rspfile = $out.rsp
		rspfile_content = $in $libs

	rule lib
		command = $lib $libflags @$out.rsp /nologo -OUT:$out
		description = lib $out
		rspfile = $out.rsp
		rspfile_content = $in $libs

	auto r"^(?i).*\.obj$": cxx r"^(?i).*\.(cpp|cxx|cc|c\+\+)$"
	auto r"^(?i).*\.obj$": cc r"^(?i).*\.c$"
	auto r"^(?i).*\.exe$": link r"^(?i).*\.obj$"
	auto r"^(?i).*\.dll$": link_so r"^(?i).*\.obj$"
	auto r"^(?i).*\.lib$": lib r"^(?i).*\.(obj|lib)$"

	# extensions transformers
	transformer application: ${param}.exe
	transformer objects: ${param}.obj
	transformer library: ${param}.lib
	transformer shared_library: ${param}.dll

	# MSC flags
	# more info here https://msdn.microsoft.com/en-us/library/19z1t1wy.aspx

	# optimizations
	cxx_omit_frame_pointer = /Oy
	cxx_disable_optimizations = /Od
	cxx_full_optimizations = /Ox
	cxx_size_optimizations = /O1
	cxx_speed_optimizations = /O2

	# code generation
	cxx_exceptions = /EHsc
	# TODO not sure about this one
	cxx_no_exceptions = /EHsc-
	cxx_seh_exceptions = /EHa
	cxx_whole_program_optimizations = /GL
	cxx_rtti = /GR
	cxx_no_rtti = /GR-
	cxx_clr = /clr
	cxx_clr_pure = /clr:pure
	cxx_clr_safe = /clr:safe
	cxx_multithread_compilation = /MP
	cxx_mimimal_rebuild = /Gm
	cxx_no_mimimal_rebuild = /Gm-
	cxx_floatpoint_fast = /fp:fast
	cxx_floatpoint_strict = /fp:strict
	cxx_cdecl = /Gd
	cxx_fastcall = /Gr
	cxx_stdcall = /Gz
	cxx_vectorcall = /Gv
	cxx_avx = /arch:AVX
	cxx_avx2 = /arch:AVX2
	cxx_sse = /arch:SSE
	cxx_sse2 = /arch:SSE2
	cxx_sse3 = /arch:SSE2
	cxx_ssse3 = /arch:SSE2
	cxx_sse4.1 = /arch:SSE2

	# language
	cxx_symbols = /Z7
	cxx_omit_default_lib = /Zl
	cxx_11 =
	cxx_14 =

	# linking
	cxx_runtime_static_debug = /MTd
	cxx_runtime_dynamic_debug = /MDd
	cxx_runtime_static_release = /MT
	cxx_runtime_dynamic_release = /MD

	# miscellaneous
	cxx_fatal_warnings = /WX
	cxx_extra_warnings = /W4
	cxx_no_warnings = /W0

	# linker flags
	ld_no_incremental_link = /INCREMENTAL:NO
	ld_no_manifest = /MANIFEST:NO
	ld_ignore_default_libs = /NODEFAULTLIB
	ld_symbols = /DEBUG
	ld_shared_lib = /DLL

	# transformers
	defines =
	includedirs =
	disable_warnings =
	libdirs =
	libs =
	ignore_default_libs =
	transformer defines: /D${param}
	transformer includedirs: /I${rel_path}${param}
	transformer disable_warnings: /wd${param}
	transformer libdirs: /LIBPATH:${rel_path}${param}
	transformer libs: ${param}.lib
	transformer ignore_default_libs: /NODEFAULTLIB:${param}

	# main flags
	cxxflags = $cxx_exceptions
	ldflags =
	libflags =
	filter variation:debug
		cxxflags += $cxx_disable_optimizations $cxx_symbols
		ldflags += $ld_symbols
	filter variation:release
		cxxflags += $cxx_speed_optimizations

filter toolset:clang
	# clang suport
	cc = clang
	cxx = clang++

filter toolset:gcc
	# gcc support
	cc = gcc
	cxx = g++

filter toolset: r"gcc|clang"
	rule cc
		command = $cc -c $in -o $out -MMD $cxxflags $defines $includedirs
		description = cc $in
		depfile = $out.d
		deps = gcc
		expand = true

	rule cxx
		command = $cxx -o $out -MMD $cxxflags $defines $includedirs -c $in
		description = cxx $in
		depfile = $out.d
		deps = gcc
		expand = true

	rule lib
		command = ar rcs $out $in
		description = ar $in

	rule link
		command = $cxx $ldflags $frameworks $libdirs $in -o $out $libs
		description = link $out

	rule link_so
		command = $cxx -shared -fPIC $ldflags $frameworks $libdirs -o $out $in $libs
		description = cxx $in

	# extensions transformers and auto
	filter system: r"^(?i)(?!windows).*$"
		auto r"^(?i).*\.o$": cxx r"^(?i).*\.(cpp|cxx|cc|c\+\+)$"
		auto r"^(?i).*\.o$": cc r"^(?i).*\.c$"
		auto r"^(.*\/)?[^.\/]+$": link r"^(?i).*\.o$"
		auto r"^(?i).*\.so$": link_so r"^(?i).*\.o$"
		auto r"^(?i).*\.a$": lib r"^(?i).*\.(o|a)$"
		transformer application: ${param}
		transformer objects: ${param}.o
		transformer library: ${path}lib${file}.a
		transformer shared_library: ${path}lib${file}.so
	filter system: r"^(?i)windows$"
		auto r"^(?i).*\.o$": cxx r"^(?i).*\.(cpp|cxx|cc|c\+\+)$"
		auto r"^(?i).*\.o$": cc r"^(?i).*\.c$"
		auto r"^(?i).*\.exe$": link r"^(?i).*\.o$"
		auto r"^(?i).*\.dll$": link_so r"^(?i).*\.o$"
		auto r"^(?i).*\.a$": lib r"^(?i).*\.(o|a)$"
		transformer application: ${param}.exe
		transformer objects: ${param}.o
		transformer library: ${path}lib${file}.a
		transformer shared_library: ${path}lib${file}.dll

	# Clang flags
	# more info here http://clang.llvm.org/docs/CommandGuide/clang.html
	# TODO:

	# optimizations
	cxx_omit_frame_pointer = -fomit-frame-pointer
	cxx_disable_optimizations = -O0
	cxx_full_optimizations = -O3
	cxx_size_optimizations = -Os
	cxx_speed_optimizations = -Ofast

	# code generation
	cxx_exceptions = -fexceptions
	cxx_no_exceptions = -fno-exceptions
	cxx_whole_program_optimizations = -O4
	cxx_rtti = -frtti
	cxx_no_rtti = -fno-rtti
	cxx_floatpoint_fast = -funsafe-math-optimizations
	cxx_floatpoint_strict = -ffloat-store
	cxx_avx = -mavx
	cxx_avx2 = -mavx2
	cxx_sse = -msse
	cxx_sse2 = -msse2
	cxx_sse3 = -msse3
	cxx_ssse3 = -mssse3
	cxx_sse4.1 = -msse4.1

	# language
	cxx_symbols = -g
	cxx_11 = -std=c++11
	cxx_14 = -std=c++14

	# miscellaneous
	cxx_fatal_warnings = -Werror
	cxx_extra_warnings = -Wall -Wextra
	cxx_no_warnings = -w

	# linker flags
	ld_ignore_default_libs = -nodefaultlibs

	# transformers
	defines =
	includedirs =
	libdirs =
	libs =
	frameworks =
	transformer defines: -D${param}
	transformer includedirs: -I${rel_path}${param}
	transformer libdirs: -L${rel_path}${param}
	transformer libs: -l${param}
	filter system: Darwin
		transformer frameworks: -framework ${param}
	filter system: r"^(?i)(?!darwin).*$"
		# don't enable this with gcc/clang on non Darwins
		transformer frameworks:

	# main flags
	cxxflags =
	filter system: r"^(?i)(?!windows).*$"
		# don't enable this with gcc/clang on Windows
		# TODO: We shouldn't have it enabled for every object file.
		# But we need it to build object files of the shared libraries.
		cxxflags = -fPIC
	ldflags = 
	filter variation:debug
		cxxflags += $cxx_symbols
		ldflags += $cxx_symbols
"""

# main app -----------------------------------------------------------

def main(*argv, **kwargs):
	title = "buildfox ninja generator %s" % VERSION
	argsparser = argparse.ArgumentParser(description = title)
	argsparser.add_argument("-i", "--in", help = "input file", default = "build.fox")
	argsparser.add_argument("-o", "--out", help = "output file", default = "build.ninja")
	argsparser.add_argument("-w", "--workdir", help = "working directory")
	argsparser.add_argument("variables", metavar = "name=value", type = str, nargs = "*", help = "variables with values to setup", default = [])
	#argsparser.add_argument("-v", "--verbose", action = "store_true", help = "verbose output") # TODO
	argsparser.add_argument("--ide", help = "generate ide solution (vs, vs2013)", default = None, dest = "ide")
	argsparser.add_argument("--ide-prj", help = "ide project prefix", default = "build")
	argsparser.add_argument("--ide-env", help = "run provided command to set required environment before calling ninja from the ide", default = None)
	argsparser.add_argument("--no-core", action = "store_false",
		help = "disable parsing fox core definitions", default = True, dest = "core")
	argsparser.add_argument("--no-env", action = "store_false",
		help = "disable environment discovery", default = True, dest = "env")
	argsparser.add_argument("-n", "--ninja-ide-gen", action = "store_true",
		help = "enables ninja ide generator mode (equal to --no-core --no-env)", default = False, dest = "ninja_ide_gen")
	argsparser.add_argument("--selftest", action = "store_true",
		help = "run self test", default = False, dest = "selftest")
	argsparser.add_argument("--ver,--version", action = "store_true",
		help = "shows version", default = False, dest = "show_ver")
	args = vars(argsparser.parse_args())

	if args.get("show_ver"):
		print(title)
		sys.exit(0)

	if args.get("ninja_ide_gen"):
		args["core"] = False
		args["env"] = False
		args["in"] = "build.ninja" if args.get("in") == "build.fox" else args.get("in")
		args["out"] = ""

	if args.get("workdir"):
		os.chdir(args.get("workdir"))

	engine = Engine()

	if args.get("env"):
		env = discover()
		for name in sorted(env.keys()):
			engine.on_assign((name, env.get(name), "="))

	for var in args.get("variables"):
		parts = var.split("=")
		if len(parts) == 2:
			name, value = parts[0], parts[1]
			engine.on_assign((name, value, "="))
		else:
			raise SyntaxError("unknown argument '%s'. you should use name=value syntax to setup a variable" % var)

	if args.get("core"):
		engine.load_core(fox_core)

	if args.get("selftest"):
		fox_filename, ninja_filename, app_filename = selftest_setup()
		engine.load(fox_filename)
		engine.save(ninja_filename)
		result = not subprocess.call(["ninja", "-f", ninja_filename])
		if result:
			result = not subprocess.call(["./" + app_filename])
		if result:
			print("Selftest - ok")
			selftest_wipe()
		else:
			print("Selftest - failed")
			sys.exit(1)
	else:
		engine.load(args.get("in"))
		if len(args.get("out")):
			engine.save(args.get("out"))

		ide = args.get("ide")

		if ide in ["vs", "vs2012", "vs2013", "vs2015"]:
			if ide == "vs":
				ide = "vs" + engine.variables.get("toolset_msc_ver", "")
			gen_vs(
				engine.context.all_files,
				cxx_defines(engine.variables.get("defines", "")),
				cxx_includedirs(engine.variables.get("includedirs", "")),
				args.get("ide_prj"),
				ide,
				args.get("ide_env"))
		elif ide in ["make"]:
			gen_make(
				args.get("in"),
				args.get("ide_env"),
				args.get("ninja_ide_gen"))
		elif ide in ["qtcreator"]:
			gen_qtcreator(
				engine.context.all_files,
				cxx_defines(engine.variables.get("defines", "")),
				cxx_includedirs(engine.variables.get("includedirs", "")),
				args.get("ide_prj"),
				args.get("in"),
				args.get("ide_env"),
				args.get("ninja_ide_gen"))
		elif ide in ["cmake"]:
			gen_cmake(
				engine.context.all_files,
				cxx_includedirs(engine.variables.get("includedirs", "")),
				args.get("ide_prj"),
				args.get("in"),
				args.get("ide_env"))
		elif ide is not None:
			raise ValueError("unknown ide '%s', available ide's : vs, vs2012, vs2013, vs2015, make, qtcreator, cmake" % ide)

if __name__ == "__main__":
	#import cProfile, pstats, io
	#pr = cProfile.Profile()
	#pr.enable()
	main()
	#pr.disable()
	#s = io.StringIO()
	#sortby = "cumulative"
	#ps = pstats.Stats(pr, stream = s).sort_stats(sortby)
	#ps.print_stats()
	#print(s.getvalue())
