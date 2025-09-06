from collections.abc import Callable
from typing import Any, Optional

from src.jsonata.Jsonata import JLambda
from src.jsonata.Functions.Functions import Functions
from src.jsonata.Jsonata import Jsonata


class Comparator:
    _comparator: Optional[Any]

    def __init__(self, comparator):

        if isinstance(comparator, Callable):
            self._comparator = JLambda(comparator)
        else:
            self._comparator = comparator

    def compare(self, o1, o2):
        res = Functions.func_apply(self._comparator, [o1, o2])
        if isinstance(res, bool):
            return 1 if res else -1
        return int(res)
