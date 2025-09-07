from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.jsonata.Jsonata.Jsonata import Jsonata

from src.jsonata.JException.JException import JException
from src.jsonata.Jsonata.Frame import Frame
from src.jsonata.Parser.Symbol import Symbol


class ComparatorWrapper:
    """
    Comparator for sorting sequences in JSONata, supporting tuple and non-tuple sorts.
    """

    _outer_instance: "Jsonata"
    _expr: Optional[Symbol]
    _environment: Optional[Frame]
    _is_tuple_sort: bool

    def __init__(self, outer_instance, expr, environment, is_tuple_sort):
        """
        Initialize ComparatorWrapper for sorting sequences.
        Args:
            outer_instance: The Jsonata instance.
            expr: The sort expression.
            environment: The evaluation environment.
            is_tuple_sort: Whether sorting tuple streams.
        """
        self._outer_instance = outer_instance
        self._expr = expr
        self._environment = environment
        self._is_tuple_sort = is_tuple_sort

    def compare(self, a, b):
        """
        Compare two items for sorting according to the sort expression.
        Args:
            a: First item to compare.
            b: Second item to compare.
        Returns:
            int: -1 if a < b, 1 if a > b, 0 if equal.
        Raises:
            JException: If types are incompatible for sorting.
        """
        comp = 0
        index = 0
        while comp == 0 and index < len(self._expr.terms):
            term = self._expr.terms[index]
            context = a
            env = self._environment
            if self._is_tuple_sort:
                context = a["@"]
                env = self._outer_instance.create_frame_from_tuple(self._environment, a)
            aa = self._outer_instance.eval(term.expression, context, env)

            context = b
            env = self._environment
            if self._is_tuple_sort:
                context = b["@"]
                env = self._outer_instance.create_frame_from_tuple(self._environment, b)
            bb = self._outer_instance.eval(term.expression, context, env)

            if aa is None:
                comp = 0 if (bb is None) else 1
                index += 1
                continue
            if bb is None:
                comp = -1
                index += 1
                continue

            if not (
                (not isinstance(aa, bool) and isinstance(aa, (int, float)))
                or isinstance(aa, str)
            ) or not (
                (not isinstance(bb, bool) and isinstance(bb, (int, float)))
                or isinstance(bb, str)
            ):
                raise JException("T2008", self._expr.position, aa, bb)

            same_type = False
            if (
                not isinstance(aa, bool)
                and isinstance(aa, (int, float))
                and not isinstance(bb, bool)
                and isinstance(bb, (int, float))
            ):
                same_type = True
            elif issubclass(type(bb), type(aa)) or issubclass(type(aa), type(bb)):
                same_type = True

            if not same_type:
                raise JException("T2007", self._expr.position, aa, bb)
            if aa == bb:
                index += 1
                continue
            if aa < bb:
                comp = -1
            else:
                comp = 1
            if term.descending:
                comp = -comp
            index += 1
        return comp
