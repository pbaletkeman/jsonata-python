from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.jsonata.Jsonata.Jsonata import Jsonata

from src.jsonata.JException.JException import JException
from src.jsonata.Jsonata.Frame import Frame
from src.jsonata.Parser.Symbol import Symbol


class ComparatorWrapper:
    _outer_instance: "Jsonata"
    _expr: Optional[Symbol]
    _environment: Optional[Frame]
    _is_tuple_sort: bool

    def __init__(self, outer_instance, expr, environment, is_tuple_sort):
        self._outer_instance = outer_instance
        self._expr = expr
        self._environment = environment
        self._is_tuple_sort = is_tuple_sort

    def compare(self, a, b):

        # expr.terms is an array of order-by in priority order
        comp = 0
        index = 0
        while comp == 0 and index < len(self._expr.terms):
            term = self._expr.terms[index]
            # evaluate the sort term in the context of a
            context = a
            env = self._environment
            if self._is_tuple_sort:
                context = a["@"]
                env = self._outer_instance.create_frame_from_tuple(self._environment, a)
            aa = self._outer_instance.eval(term.expression, context, env)

            # evaluate the sort term in the context of b
            context = b
            env = self._environment
            if self._is_tuple_sort:
                context = b["@"]
                env = self._outer_instance.create_frame_from_tuple(self._environment, b)
            bb = self._outer_instance.eval(term.expression, context, env)

            # type checks
            #  var atype = typeof aa
            #  var btype = typeof bb
            # undefined should be last in sort order
            if aa is None:
                # swap them, unless btype is also undefined
                comp = 0 if (bb is None) else 1
                index += 1
                continue
            if bb is None:
                comp = -1
                index += 1
                continue

            # if aa or bb are not string or numeric values, then throw an error
            if not (
                (not isinstance(aa, bool) and isinstance(aa, (int, float)))
                or isinstance(aa, str)
            ) or not (
                (not isinstance(bb, bool) and isinstance(bb, (int, float)))
                or isinstance(bb, str)
            ):
                raise JException("T2008", self._expr.position, aa, bb)

            # if aa and bb are not of the same type
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
                # both the same - move on to next term
                index += 1
                continue
            elif aa < bb:
                comp = -1
            else:
                comp = 1
            if term.descending:
                comp = -comp
            index += 1
        # only swap a & b if comp equals 1
        # return comp == 1
        return comp
