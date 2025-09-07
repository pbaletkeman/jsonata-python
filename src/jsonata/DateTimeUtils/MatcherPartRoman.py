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

from src.jsonata.DateTimeUtils.MatcherPart import MatcherPart


class MatcherPartRoman(MatcherPart):
    """
    Matcher part for Roman numeral sequences, supporting upper/lower case.
    """

    _is_upper: bool

    def __init__(self, regex, is_upper):
        """
        Initialize a MatcherPartRoman with regex and case type.
        Args:
            regex (str): Regex pattern for matching Roman numerals.
            is_upper (bool): True if matching uppercase, False for lowercase.
        """
        super().__init__(regex)
        self._is_upper = is_upper

    def parse(self, value: str) -> int:
        """
        Parse a Roman numeral sequence into its decimal value.
        Args:
            value (str): The Roman numeral sequence to parse.
        Returns:
            int: Parsed decimal value.
        """
        from src.jsonata.DateTimeUtils.DateTimeUtils import DateTimeUtils

        return DateTimeUtils.roman_to_decimal(
            value if self._is_upper else value.upper()
        )
