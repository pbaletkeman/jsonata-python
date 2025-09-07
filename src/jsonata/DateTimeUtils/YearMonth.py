#
"""
YearMonth module for JSONata Python implementation.
Provides utilities for handling year and month values, including navigation and representation, in JSONata expressions.
Adapted from jsonata-java and JSONata4Java projects.
"""
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

from dataclasses import dataclass


@dataclass
class YearMonth:
    """
    Represents a year and month, with utility methods for navigation.
    """

    year: int
    month: int

    def next_month(self):
        """
        Get the YearMonth for the next month.
        Returns:
            YearMonth: The next month.
        """
        return (
            YearMonth(self.year + 1, 1)
            if self.month == 12
            else YearMonth(self.year, self.month + 1)
        )

    def previous_month(self):
        """
        Get the YearMonth for the previous month.
        Returns:
            YearMonth: The previous month.
        """
        return (
            YearMonth(self.year - 1, 12)
            if self.month == 1
            else YearMonth(self.year, self.month - 1)
        )

    def next_year(self):
        """
        Get the YearMonth for the same month in the next year.
        Returns:
            YearMonth: The next year.
        """
        return YearMonth(self.year + 1, self.month)

    def previous_year(self):
        """
        Get the YearMonth for the same month in the previous year.
        Returns:
            YearMonth: The previous year.
        """
        return YearMonth(self.year - 1, self.month)
