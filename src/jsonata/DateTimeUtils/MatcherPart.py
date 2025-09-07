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
MatcherPart module for JSONata Python implementation.
Provides utilities for regex matching in date/time and number parsing for JSONata expressions.
Adapted from jsonata-java and JSONata4Java projects.
"""


from typing import Optional


class MatcherPart:
    """
    Represents a part of a regex matcher for date/time or number parsing in Jsonata.
    """

    regex: str
    component: Optional[str]

    def __init__(self, regex):
        """
        Initialize a MatcherPart with a regex pattern.
        Args:
            regex (str): The regex pattern for matching.
        """
        self.regex = regex
        self.component = None

    def parse(self, value: str) -> int:
        """
        Parse a value using the matcher part's regex.
        Args:
            value (str): The value to parse.
        Returns:
            int: Parsed integer value.
        Raises:
            NotImplementedError: If not implemented in subclass.
        """
        raise NotImplementedError
