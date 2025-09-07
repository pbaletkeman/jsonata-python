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

from src.jsonata.DateTimeUtils.SpecPart import SpecPart


class PictureFormat:
    """
    Represents a parsed picture format for date/time formatting in Jsonata.
    Holds a list of SpecPart objects describing the format.
    """

    type: str
    parts: list["SpecPart"]

    def __init__(self):
        """
        Initialize a PictureFormat object with default type and empty parts list.
        """
        self.type = type
        self.parts = []

    def add_literal(self, picture: str, start: int, end: int) -> None:
        """
        Add a literal part to the picture format.
        Args:
            picture (str): The picture format string.
            start (int): Start index of the literal.
            end (int): End index of the literal.
        """
        if end > start:
            literal = picture[start:end]
            if literal == "]]":
                # handle special case where picture ends with ]], split yields empty array
                literal = "]"
            else:
                literal = "]".join(literal.split("]]"))
            self.parts.append(SpecPart("literal", value=literal))
