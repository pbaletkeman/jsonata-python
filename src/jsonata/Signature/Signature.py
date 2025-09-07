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

import re
from typing import MutableSequence, Optional, NoReturn, Any

from src.jsonata.JException.JException import JException
from src.jsonata.Utils.Utils import Utils
from src.jsonata.Signature.Param import Param


#
# Manages signature related functions
#
class Signature:
    """
    Manages function signature parsing, validation, and argument type checking for Jsonata functions.
    Parses signature strings, generates regex patterns, and validates arguments against expected types.
    """

    SERIAL_VERSION_UID = -450755246855587271

    signature: str
    function_name: str

    _param: "Param"
    _params: MutableSequence[Param]
    _prev_param: "Param"
    _regex: Optional[re.Pattern]
    _signature: str

    def __init__(self, signature, function):
        """
        Initialize a Signature object and parse the signature string.
        Args:
            signature: The signature string to parse.
            function: The function name.
        """
        self._param = Param()
        self._params = []
        self._prev_param = self._param
        self._regex = None
        self._signature = ""

        self.function_name = function
        self.parse_signature(signature)

    def set_function_name(self, function_name: str) -> None:
        """
        Set the function name for this signature.
        Args:
            function_name: The function name to set.
        """
        self.function_name = function_name

    def find_closing_bracket(
        self, string: str, start: int, open_symbol: str, close_symbol: str
    ) -> int:
        """
        Find the position of the closing symbol in a string that balances the opening symbol.
        Args:
            string: The string to search.
            start: The starting position of the opening symbol.
            open_symbol: The opening symbol character.
            close_symbol: The closing symbol character.
        Returns:
            The position of the closing symbol.
        """
        depth = 1
        position = start
        while position < len(string):
            position += 1
            symbol = string[position]
            if symbol == close_symbol:
                depth -= 1
                if depth == 0:
                    # we're done
                    break  # out of while loop
            elif symbol == open_symbol:
                depth += 1
        return position

    def get_symbol(self, value: Optional[Any]) -> str:
        """
        Get the signature symbol for a given value.
        Args:
            value: The value to get the symbol for.
        Returns:
            The symbol representing the value type.
        """
        from src.jsonata.Functions.Functions import Functions

        if value is None:
            symbol = "m"
        else:
            # first check to see if this is a function
            if (
                Utils.is_function(value)
                or Functions.is_lambda(value)
                or isinstance(value, re.Pattern)
            ):
                symbol = "f"
            elif isinstance(value, str):
                symbol = "s"
            elif isinstance(value, bool):
                symbol = "b"
            elif isinstance(value, (int, float)):
                symbol = "n"
            elif isinstance(value, list):
                symbol = "a"
            elif isinstance(value, dict):
                symbol = "o"
            elif value is None:  # Uli: is this used???
                symbol = "l"
            else:
                # any value can be undefined, but should be allowed to match
                symbol = "m"  # m for missing
        return symbol

    def next(self) -> None:
        """
        Advance to the next parameter in the signature.
        """
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
    def parse_signature(self, signature: str) -> Optional[re.Pattern]:
        """
        Parse a function signature definition and return a validation pattern.
        Args:
            signature: The signature string to parse.
        Returns:
            A regex pattern representing the signature, or None.
        """
        # create a Regex that represents this signature and return a function that when
        # invoked,
        # returns the validated (possibly fixed-up) arguments, or throws a validation
        # error
        # step through the signature, one symbol at a time
        position = 1
        while position < len(signature):
            symbol = signature[position]
            if symbol == ":":
                # TODO figure out what to do with the return type
                # ignore it for now
                break

            if (
                symbol == "s"
                or symbol == "n"
                or symbol == "b"
                or symbol == "l"
                or symbol == "o"
            ):
                self._param.regex = "[" + symbol + "m]"
                self._param.type = str(symbol)
                self.next()
            elif symbol == "a":
                # normally treat any value as singleton array
                self._param.regex = "[asnblfom]"
                self._param.type = str(symbol)
                self._param.array = True
                self.next()
            elif symbol == "f":
                self._param.regex = "f"
                self._param.type = str(symbol)
                self.next()
            elif symbol == "j":
                self._param.regex = "[asnblom]"
                self._param.type = str(symbol)
                self.next()
            elif symbol == "x":
                self._param.regex = "[asnblfom]"
                self._param.type = str(symbol)
                self.next()
            elif symbol == "-":
                self._prev_param.context = True
                self._prev_param.regex += "?"
            elif symbol == "?" or symbol == "+":
                self._prev_param.regex += symbol
            elif symbol == "(":
                # search forward for matching ')'
                end_paren = self.find_closing_bracket(signature, position, "(", ")")
                choice = signature[position + 1 : end_paren]
                if choice.find("<") == -1:
                    # no _parameterized types, simple regex
                    self._param.regex = "[" + choice + "m]"
                else:
                    # TODO harder
                    raise RuntimeError(
                        "Choice groups containing parameterized types are not supported"
                    )
                self._param.type = "(" + choice + ")"
                position = end_paren
                self.next()
            elif symbol == "<":
                test = self._prev_param.type
                if test is not None:
                    # Accept type parameters for arrays and functions
                    if test == "a" or test == "f":
                        # search forward for matching '>'
                        end_pos = self.find_closing_bracket(
                            signature, position, "<", ">"
                        )
                        self._prev_param.subtype = signature[position + 1 : end_pos]
                        position = end_pos
                    else:
                        # Instead of raising, skip type parameter for other types
                        end_pos = self.find_closing_bracket(
                            signature, position, "<", ">"
                        )
                        position = end_pos
                else:
                    # Instead of raising, skip type parameter
                    end_pos = self.find_closing_bracket(signature, position, "<", ">")
                    position = end_pos
            position += 1  # end while processing symbols in signature

        regex_str = "^"
        for param in self._params:
            regex_str += "(" + param.regex + ")"
        regex_str += "$"

        self._regex = re.compile(regex_str)
        self._signature = regex_str
        return self._regex

    def throw_validation_error(
        self,
        # bad_args: Optional[Sequence],
        bad_sig: Optional[str],
        function_name: Optional[str],
    ) -> NoReturn:
        # to figure out where this went wrong we need apply each component of the
        # regex to each argument until we get to the one that fails to match
        partial_pattern = "^"

        good_to = 0
        for param in self._params:
            partial_pattern += param.regex
            tester = re.compile(partial_pattern)
            match_ = tester.fullmatch(bad_sig)
            if match_ is None:
                # failed here
                raise JException("T0410", -1, (good_to + 1), function_name)
            good_to = match_.end()
        # if it got this far, it's probably because of extraneous arguments (we
        # haven't added the trailing '$' in the regex yet.
        raise JException("T0410", -1, (good_to + 1), function_name)

    def validate(self, args: Any, context: Optional[Any]) -> Optional[Any]:
        supplied_sig = ""
        for arg in args:
            supplied_sig += self.get_symbol(arg)

        is_valid = self._regex.fullmatch(supplied_sig)
        if is_valid is not None:
            validated_args = []
            arg_index = 0
            index = 0
            for param in self._params:
                arg = args[arg_index] if arg_index < len(args) else None
                match_ = is_valid.group(index + 1)
                if "" == match_:
                    if param.context and param.regex is not None:
                        # substitute context value for missing arg
                        # first check that the context value is the right type
                        context_type = self.get_symbol(context)
                        # test context_type against the regex for this arg (without the trailing ?)
                        if re.fullmatch(param.regex, context_type):
                            # if (param.contextRegex.test(context_type)) {
                            validated_args.append(context)
                        else:
                            # context value not compatible with this argument
                            raise JException("T0411", -1, context, arg_index + 1)
                    else:
                        validated_args.append(arg)
                        arg_index += 1
                else:
                    # may have matched multiple args (if the regex ends with a '+'
                    # split into single tokens
                    singles = list(match_)  # split on empty separator
                    for single in singles:
                        # match.split('').forEach(function (single) {
                        if param.type == "a":
                            if single == "m":
                                # missing (undefined)
                                arg = None
                            else:
                                arg = args[arg_index] if arg_index < len(args) else None
                                array_ok = True
                                # is there type information on the contents of the array?
                                if param.subtype is not None:
                                    if single != "a" and match_ != param.subtype:
                                        array_ok = False
                                    elif single == "a":
                                        arg_arr = arg
                                        if arg_arr:
                                            item_type = self.get_symbol(arg_arr[0])
                                            if item_type != str(param.subtype[0]):
                                                array_ok = False
                                            else:
                                                # make sure every item in the array is this type
                                                for o in arg_arr:
                                                    if self.get_symbol(o) != item_type:
                                                        array_ok = False
                                                        break
                                if not array_ok:
                                    raise JException("T0412", -1, arg, param.subtype)
                                # the function expects an array. If it's not one, make it so
                                if single != "a":
                                    arg = [arg]
                            validated_args.append(arg)
                            arg_index += 1
                        else:
                            arg = args[arg_index] if arg_index < len(args) else None
                            validated_args.append(arg)
                            arg_index += 1
            return validated_args
        self.throw_validation_error(supplied_sig, self.function_name)

    def get_number_of_args(self) -> int:
        return len(self._params)

    #
    # Returns the minimum # of arguments.
    # I.e. the # of all non-optional arguments.
    #
    def get_min_number_of_args(self) -> int:
        res = 0
        for p in self._params:
            if "?" not in p.regex:
                res += 1
        return res
