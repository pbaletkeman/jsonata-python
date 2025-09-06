from collections.abc import Callable
from typing import Any, Optional

from .Functions import Functions
from ..Jsonata import Jsonata


class Comparator:
    _comparator: Optional[Any]

    def __init__(self, comparator):

        if isinstance(comparator, Callable):
            self._comparator = Jsonata.JLambda(comparator)
        else:
            self._comparator = comparator

    def compare(self, o1, o2):
        res = Functions.func_apply(self._comparator, [o1, o2])
        if isinstance(res, bool):
            return 1 if res else -1
        return int(res)
