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
PictureMatcher module for JSONata Python implementation.
Provides utilities for matching and parsing date/time picture formats in JSONata expressions.
Adapted from jsonata-java and JSONata4Java projects.
"""


from src.jsonata.DateTimeUtils.MatcherPart import MatcherPart


class PictureMatcher:
    """
    Represents a matcher for a parsed picture format, holding matcher parts.
    Used for matching and parsing date/time strings in Jsonata.
    """

    parts: list["MatcherPart"]

    def __init__(self):
        """
        Initialize a PictureMatcher with an empty list of matcher parts.
        """
        self.parts = []
