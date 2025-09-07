"""
Comparator module for JSONata Python implementation.
Provides utilities for wrapping comparator functions or objects, enabling sorting and grouping in JSONata expressions.
"""

from collections.abc import Callable
from typing import Any, Optional

from src.jsonata.Jsonata.JLambda import JLambda


class Comparator:
    """
    Wraps a comparator function or object for use in Jsonata sorting/grouping.
    """

    _comparator: Optional[Any]

    def __init__(self, comparator):
        """
        Initialize a Comparator with a callable or comparator object.
        Args:
            comparator (Any): A callable or comparator object.
        """
        if isinstance(comparator, Callable):
            self._comparator = JLambda(comparator)
        else:
            self._comparator = comparator

    def compare(self, o1, o2):
        """
        Compare two objects using the wrapped comparator.
        Args:
            o1: First object.
            o2: Second object.
        Returns:
            int: 1 if o1 > o2, -1 if o1 < o2, or result of comparator.
        """
        from src.jsonata.Functions.Functions import Functions

        res = Functions.func_apply(self._comparator, [o1, o2])
        if isinstance(res, bool):
            return 1 if res else -1
        return int(res)
