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
SpecPart module for JSONata Python implementation.
Provides utilities for handling parts of date/time picture format specifications in JSONata expressions.
Adapted from jsonata-java and JSONata4Java projects.
"""


from typing import Optional

from src.jsonata.DateTimeUtils.TCase import TCase
from src.jsonata.DateTimeUtils.Format import Format


class SpecPart:
    """
    Represents a part of a picture format specification for date/time formatting.
    Holds details about type, component, value, width, presentation, and formatting.
    """

    type: str
    value: Optional[str]
    component: str
    width: tuple[int, int]
    presentation1: Optional[str]
    presentation2: Optional[str]
    ordinal: bool
    names: "Optional[TCase]"
    integerFormat: "Optional[Format]"
    n: int

    def __init__(self, part_type, component=None, value=None):
        """
        Initialize a SpecPart with type, component, and value.
        Args:
            part_type (str): The type of the spec part (e.g., 'literal', 'marker').
            component (str, optional): The component specifier.
            value (str, optional): The value for literals.
        """
        self.type = part_type
        self.component = component
        self.value = value

        self.width = None
        self.presentation1 = None
        self.presentation2 = None
        self.ordinal = False
        self.names = None
        self.integerFormat = None
        self.n = 0
