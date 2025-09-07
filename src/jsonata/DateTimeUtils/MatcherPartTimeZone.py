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
MatcherPartTimeZone module for JSONata Python implementation.
Provides utilities for parsing time zone offsets from date/time strings in JSONata expressions.
Adapted from jsonata-java and JSONata4Java projects.
"""


from src.jsonata.DateTimeUtils.MatcherPart import MatcherPart
from src.jsonata.DateTimeUtils.SpecPart import SpecPart


class MatcherPartTimeZone(MatcherPart):
    """
    Matcher part for parsing time zone offsets from date/time strings.
    """

    _part: "SpecPart"
    _separator: bool

    def __init__(self, regex, part, separator):
        """
        Initialize a MatcherPartTimeZone with regex, part spec, and separator flag.
        Args:
            regex (str): Regex pattern for matching time zone.
            part (SpecPart): Specification part for the time zone.
            separator (bool): True if separator is present, False otherwise.
        """
        super().__init__(regex)
        self._part = part
        self._separator = separator

    def parse(self, value: str) -> int:
        """
        Parse a time zone offset string into minutes.
        Args:
            value (str): The time zone string to parse.
        Returns:
            int: Offset in minutes.
        """
        if self._part.component == "z":
            value = value[3:]
        offset_hours = 0
        offset_minutes = 0
        if self._separator:
            offset_hours = int(
                value[
                    0 : value.find(
                        self._part.integerFormat.groupingSeparators[0].character
                    )
                ]
            )
            offset_minutes = int(
                value[
                    value.find(self._part.integerFormat.groupingSeparators[0].character)
                    + 1 :
                ]
            )
        else:
            numdigits = len(value) - 1
            if numdigits <= 2:
                offset_hours = int(value)
            else:
                offset_hours = int(value[0:3])
                offset_minutes = int(value[3:])
        return offset_hours * 60 + offset_minutes
