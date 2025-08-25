#
# Copyright Robert Yokota
# 
# Licensed under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# 
# Derived from the following code:
#
#   Project name: jsonata-java
#   Copyright Dashjoin GmbH. https://dashjoin.com
#   Licensed under the Apache License, Version 2.0 (the "License")
#
#   Project name: JSONata4Java
#   (c) Copyright 2018, 2019 IBM Corporation
#   Licensed under the Apache License, Version 2.0 (the "License")
#   1 New Orchard Road,
#   Armonk, New York, 10504-1722
#   United States
#   +1 914 499 1900
#   support: Nathaniel Mills wnm3@us.ibm.com
#


# cython: language_level=3
import re
from typing import Optional, Sequence, Any

from jsonata import jexception, utils, functions

cdef class Param:
    cdef str type
    cdef str regex
    cdef bint context
    cdef bint array
    cdef str subtype
    cdef str context_regex

    def __init__(self):
        self.type = None
        self.regex = None
        self.context = False
        self.array = False
        self.subtype = None
        self.context_regex = None

    def __repr__(self):
        return f"Param {self.type} regex={self.regex} ctx={self.context} array={self.array}"

cdef class Signature:
    cdef:
        str signature
        str function_name
        Param _param
        list _params
        Param _prev_param
        object _regex  # re.Pattern, but typed as object for compatibility
        str _signature

    SERIAL_VERSION_UID = -450755246855587271

    def __init__(self, signature: str, function: str):
        self._param = Param()
        self._params = []
        self._prev_param = self._param
        self._regex = None
        self._signature = ""

        self.function_name = function
        self.parse_signature(signature)

    cpdef set_function_name(self, str function_name):
        self.function_name = function_name

    @staticmethod
    def main(args: Sequence[str]) -> None:
        s = Signature("<s-:s>", "test")
        print(s._params)

    cpdef int find_closing_bracket(self, str string, int start, str open_symbol, str close_symbol):
        cdef int depth = 1
        cdef int position = start
        cdef str symbol
        while position < len(string):
            position += 1
            symbol = string[position]
            if symbol == close_symbol:
                depth -= 1
                if depth == 0:
                    break
            elif symbol == open_symbol:
                depth += 1
        return position

    cpdef str get_symbol(self, value: Any):
        if value is None:
            return "m"
        elif utils.Utils.is_function(value) or functions.Functions.is_lambda(value) or isinstance(value, re.Pattern):
            return "f"
        elif isinstance(value, str):
            return "s"
        elif isinstance(value, bool):
            return "b"
        elif isinstance(value, (int, float)):
            return "n"
        elif isinstance(value, list):
            return "a"
        elif isinstance(value, dict):
            return "o"
        else:
            return "m"

    cpdef void next(self):
        self._params.append(self._param)
        self._prev_param = self._param
        self._param = Param()

    #
    # Parses a function signature definition and returns a validation function
    # 
    # @param {string}
    #                 signature - the signature between the <angle brackets>
    # @returns validation pattern
    #  
    cpdef object parse_signature(self, str signature):
        # create a Regex that represents this signature and return a function that when
        # invoked,
        # returns the validated (possibly fixed-up) arguments, or throws a validation
        # error
        # step through the signature, one symbol at a time
        cdef int position = 1
        cdef str symbol, choice, test
        while position < len(signature):
            symbol = signature[position]
            if symbol == ':':
                break

            if symbol in 'snblo':
                self._param.regex = f"[{symbol}m]"
                self._param.type = symbol
                self.next()
            elif symbol == 'a':
                self._param.regex = "[asnblfom]"
                self._param.type = symbol
                self._param.array = True
                self.next()
            elif symbol == 'f':
                self._param.regex = "f"
                self._param.type = symbol
                self.next()
            elif symbol == 'j':
                self._param.regex = "[asnblom]"
                self._param.type = symbol
                self.next()
            elif symbol == 'x':
                self._param.regex = "[asnblfom]"
                self._param.type = symbol
                self.next()
            elif symbol == '-':
                self._prev_param.context = True
                self._prev_param.regex += "?"
            elif symbol in '?+':
                self._prev_param.regex += symbol
            elif symbol == '(':
                end_paren = self.find_closing_bracket(signature, position, '(', ')')
                choice = signature[position + 1:end_paren]
                if "<" not in choice:
                    self._param.regex = f"[{choice}m]"
                else:
                    raise RuntimeError("Choice groups containing parameterized types are not supported")
                self._param.type = f"({choice})"
                position = end_paren
                self.next()
            elif symbol == '<':
                test = self._prev_param.type
                if test:
                    if test in ("a", "f"):
                        end_pos = self.find_closing_bracket(signature, position, '<', '>')
                        self._prev_param.subtype = signature[position + 1:end_pos]
                        position = end_pos
                    else:
                        raise RuntimeError("Type parameters can only be applied to functions and arrays")
                else:
                    raise RuntimeError("Type parameters can only be applied to functions and arrays")
            position += 1

        regex_str = "^"
        for param in self._params:
            regex_str += f"({param.regex})"
        regex_str += "$"

        self._regex = re.compile(regex_str)
        self._signature = regex_str
        return self._regex

    cpdef void throw_validation_error(self, object bad_args, str bad_sig, str function_name):
        # to figure out where this went wrong we need apply each component of the
        # regex to each argument until we get to the one that fails to match
        cdef str partial_pattern = "^"
        cdef int good_to = 0
        for param in self._params:
            partial_pattern += param.regex
            tester = re.compile(partial_pattern)
            match_ = tester.fullmatch(bad_sig)
            if match_ is None:
                raise jexception.JException("T0410", -1, (good_to + 1), function_name)
            good_to = match_.end()

            # if it got this far, it's probably because of extraneous arguments (we
            # haven't added the trailing '$' in the regex yet.

        raise jexception.JException("T0410", -1, (good_to + 1), function_name)

    cpdef object validate(self, object args, object context):
        cdef str supplied_sig = ""
        cdef object arg
        for arg in args:
            supplied_sig += self.get_symbol(arg)

        is_valid = self._regex.fullmatch(supplied_sig)
        if is_valid:
            validated_args = []
            arg_index = 0
            index = 0
            for param in self._params:
                arg = args[arg_index] if arg_index < len(args) else None
                match_ = is_valid.group(index + 1)
                if match_ == "":
                    if param.context and param.regex:
                        # substitute context value for missing arg
                        # first check that the context value is the right type
                        context_type = self.get_symbol(context)
                        # test context_type against the regex for this arg (without the trailing ?)
                        if re.fullmatch(param.regex, context_type):
                            # if (param.contextRegex.test(context_type)) {
                            validated_args.append(context)
                        else:
                            # context value not compatible with this argument
                            raise jexception.JException("T0411", -1, context, arg_index + 1)
                    else:
                        validated_args.append(arg)
                        arg_index += 1
                else:
                    # may have matched multiple args (if the regex ends with a '+'
                    # split into single tokensv
                    singles = list(match_)
                    for single in singles:
			# match.split('').forEach(function (single) {
                        if param.type == "a":
                            if single == "m":
				# missing (undefined)
                                arg = None
                            else:
                                arg = args[arg_index] if arg_index < len(args) else None
                                array_ok = True
                                if param.subtype:
                                    if single != "a" and match_ != param.subtype:
                                        array_ok = False
                                    elif single == "a":
                                        arg_arr = arg
                                        if arg_arr:
                                            item_type = self.get_symbol(arg_arr[0])
                                            if item_type != param.subtype[0]:
                                                array_ok = False
                                            else:
                                                for o in arg_arr:
                                                    if self.get_symbol(o) != item_type:
                                                        array_ok = False
                                                        break
                                if not array_ok:
                                    raise jexception.JException("T0412", -1, arg, param.subtype)
                                if single != "a":
                                    arg = [arg]
                            validated_args.append(arg)
                            arg_index += 1
                        else:
                            arg = args[arg_index] if arg_index < len(args) else None
                            validated_args.append(arg)
                            arg_index += 1
                index += 1
            return validated_args
        self.throw_validation_error(args, supplied_sig, self.function_name)

    cpdef int get_number_of_args(self):
        return len(self._params)

    #
    # Returns the minimum # of arguments.
    # I.e. the # of all non-optional arguments.
    #     

    cpdef int get_min_number_of_args(self):
        cdef int res = 0
        for p in self._params:
            if "?" not in p.regex:
                res += 1
        return res
