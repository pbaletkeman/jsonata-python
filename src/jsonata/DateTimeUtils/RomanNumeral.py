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
RomanNumeral module for JSONata Python implementation.
Provides utilities for handling Roman numerals, including conversion and representation, in JSONata expressions.
Adapted from jsonata-java and JSONata4Java projects.
"""


class RomanNumeral:
    """
    Represents a Roman numeral with its integer value and letter representation.
    """

    _value: int
    _letters: str

    def __init__(self, value, letters):
        """
        Initialize a RomanNumeral with value and letters.
        Args:
            value (int): The integer value of the Roman numeral.
            letters (str): The Roman numeral letters.
        """
        self._value = value
        self._letters = letters

    def get_value(self) -> int:
        """
        Get the integer value of the Roman numeral.
        Returns:
            int: The value.
        """
        return self._value

    def get_letters(self) -> str:
        """
        Get the letter representation of the Roman numeral.
        Returns:
            str: The Roman numeral letters.
        """
        return self._letters
