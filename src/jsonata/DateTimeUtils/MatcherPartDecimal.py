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

# pylint: disable=locally-disabled, multiple-statements, fixme, line-too-long

"""
MatcherPartDecimal module for JSONata Python implementation.
Provides utilities for matching and formatting decimal numbers in JSONata expressions.
Adapted from jsonata-java and JSONata4Java projects.
"""


from src.jsonata.DateTimeUtils.Format import Format
from src.jsonata.DateTimeUtils.MatcherPart import MatcherPart


class MatcherPartDecimal(MatcherPart):
    """
    Matcher part for decimal numbers, supporting formatting and parsing.
    """

    _format_spec: "Format"

    def __init__(self, regex, format_spec):
        """
        Initialize a MatcherPartDecimal with regex and format specification.
        Args:
            regex (str): Regex pattern for matching decimal numbers.
            format_spec (Format): Format specification for parsing.
        """
        super().__init__(regex)
        self._format_spec = format_spec

    def parse(self, value: str) -> int:
        """
        Parse a decimal value using the format specification.
        Args:
            value (str): The string value to parse.
        Returns:
            int: Parsed integer value.
        """
        digits = value
        if self._format_spec.ordinal:
            digits = value[0 : len(value) - 2]
        if self._format_spec.regular:
            digits = "".join(digits.split(","))
        else:
            for sep in self._format_spec.groupingSeparators:
                digits = "".join(digits.split(sep.character))
        if self._format_spec.zeroCode != 0x30:
            chars = list(digits)
            i = 0
            while i < len(chars):
                chars[i] = chr(ord(chars[i]) - self._format_spec.zeroCode + 0x30)
                i += 1
            digits = "".join(chars)
        return int(digits)
