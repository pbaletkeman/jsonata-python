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

from typing import Optional

from src.jsonata.DateTimeUtils.TCase import TCase
from src.jsonata.DateTimeUtils.Formats import Formats
from src.jsonata.DateTimeUtils.GroupingSeparator import GroupingSeparator


class Format:
    type: str
    primary: "Formats"
    caseType: "TCase"
    ordinal: bool
    zeroCode: int
    mandatoryDigits: int
    optionalDigits: int
    regular: bool
    groupingSeparators: list["GroupingSeparator"]
    token: Optional[str]

    def __init__(self):
        self.type = "integer"
        self.primary = Formats.DECIMAL
        self.case_type = TCase.LOWER
        self.ordinal = False
        self.zeroCode = 0
        self.mandatoryDigits = 0
        self.optionalDigits = 0
        self.regular = False
        self.groupingSeparators = []
        self.token = None
