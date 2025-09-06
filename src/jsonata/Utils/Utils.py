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

import math
from src.jsonata.Utils.JList import JList
from typing import Any, MutableMapping, MutableSequence, Optional, Iterable

from src.jsonata.JException.JException import JException
from src.jsonata.Utils.NullValue import NullValue


class Utils:

    NULL_VALUE = NullValue()

    @staticmethod
    def is_numeric(v: Optional[Any]) -> bool:
        """
        Returns True if v is a numeric type (int or float and not NaN or infinite), False otherwise.
        """
        if isinstance(v, bool):
            return False
        if isinstance(v, int):
            return True
        is_num = False
        if isinstance(v, float):
            is_num = not math.isnan(v)
            if is_num and not math.isfinite(v):
                raise JException("D1001", 0, v)
        return is_num

    @staticmethod
    def is_array_of_strings(v: Optional[Any]) -> bool:
        """
        Returns True if v is a list of strings, False otherwise.
        """
        if isinstance(v, list):
            for o in v:
                if not isinstance(o, str):
                    return False
            return True
        return False

    @staticmethod
    def is_array_of_numbers(v: Optional[Any]) -> bool:
        """
        Returns True if v is a list of numbers, False otherwise.
        """
        if isinstance(v, list):
            for o in v:
                if not Utils.is_numeric(o):
                    return False
            return True
        return False

    @staticmethod
    def is_function(o: Optional[Any]) -> bool:
        """
        Returns True if o is a Jsonata JFunctionCallable, False otherwise.
        """
        from src.jsonata.Jsonata.JFunctionCallable import JFunctionCallable

        return isinstance(o, JFunctionCallable)

    NONE = object()

    @staticmethod
    def create_sequence(el: Optional[Any] = NONE) -> list:
        """
        Create a Jsonata sequence from the given element.
        """
        if el is not Utils.NONE:
            if isinstance(el, list) and len(el) == 1:
                sequence = JList(el)
            else:
                # This case does NOT exist in Javascript! Why?
                sequence = JList([el])
        else:
            sequence = JList()
        sequence.sequence = True
        return sequence

    @staticmethod
    def create_sequence_from_iter(it: Iterable) -> list:
        """
        Create a Jsonata sequence from an iterable.
        """
        sequence = JList(it)
        sequence.sequence = True
        return sequence

    @staticmethod
    def is_sequence(result: Optional[Any]) -> bool:
        """
        Returns True if result is a Jsonata sequence, False otherwise.
        """
        return isinstance(result, JList) and result.sequence

    @staticmethod
    def convert_number(n: float) -> Optional[float]:
        """
        Convert a number to int if not fractional, else float.
        """
        if not Utils.is_numeric(n):
            return None
        if int(n) == float(n):
            v = int(n)
            if int(v) == v:
                return int(v)
            else:
                return v
        return float(n)

    @staticmethod
    def convert_value(val: Optional[Any]) -> Optional[Any]:
        """
        Convert Jsonata NullValue to Python None.
        """
        return val if val is not Utils.NULL_VALUE else None

    @staticmethod
    def convert_dict_nulls(res: MutableMapping[str, Any]) -> None:
        """
        Recursively convert NullValue to None in a dictionary.
        """
        for key, val in res.items():
            v = Utils.convert_value(val)
            if v is not val:
                res[key] = v
            Utils.recurse(val)

    @staticmethod
    def convert_list_nulls(res: MutableSequence[Any]) -> None:
        """
        Recursively convert NullValue to None in a list.
        """
        for i, val in enumerate(res):
            v = Utils.convert_value(val)
            if v is not val:
                res[i] = v
            Utils.recurse(val)

    @staticmethod
    def recurse(val: Optional[Any]) -> None:
        """
        Recursively convert NullValue to None in nested structures.
        """
        if isinstance(val, dict):
            Utils.convert_dict_nulls(val)
        if isinstance(val, list):
            Utils.convert_list_nulls(val)

    @staticmethod
    def convert_nulls(res: Optional[Any]) -> Optional[Any]:
        """
        Recursively convert NullValue to None in any structure.
        """
        Utils.recurse(res)
        return Utils.convert_value(res)
