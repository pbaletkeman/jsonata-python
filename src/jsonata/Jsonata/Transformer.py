from typing import Any, Optional, Sequence, TYPE_CHECKING

if TYPE_CHECKING:
    from src.jsonata.Jsonata.Jsonata import Jsonata

from src.jsonata.Parser.Symbol import Symbol
from src.jsonata.JException.JException import JException
from src.jsonata.Jsonata.JFunctionCallable import JFunctionCallable
from src.jsonata.Jsonata.Frame import Frame
from src.jsonata.Utils.Utils import Utils


class Transformer(JFunctionCallable):
    _jsonata: "Jsonata"
    _expr: Optional[Symbol]
    _environment: Optional[Frame]

    def __init__(self, jsonata, expr, environment):
        self._jsonata = jsonata
        self._expr = expr
        self._environment = environment

    def call(self, input_: Optional[Any], args: Optional[Sequence]) -> Optional[Any]:
        # /* async */ Object (obj) { // signature <(oa):o>

        from src.jsonata.Functions.Functions import Functions

        obj = args[0]

        # undefined inputs always return undefined
        if obj is None or input_ is None:
            return None

        # this Object returns a copy of obj with changes specified by the pattern/operation
        result = Functions.function_clone(obj)

        matches = self._jsonata.eval(self._expr.pattern, result, self._environment)
        if matches is not None:
            if not (isinstance(matches, list)):
                matches = [matches]
            for match_ in matches:
                # evaluate the update value for each match
                update = self._jsonata.eval(
                    self._expr.update, match_, self._environment
                )
                # update must be an object
                # var updateType = typeof update
                # if(updateType != null)

                if update is not None:
                    if not (isinstance(update, dict)):
                        # throw type error
                        raise JException("T2011", self._expr.update.position, update)
                    # merge the update
                    for k in update.keys():
                        match_[k] = update[k]

                # delete, if specified, must be an array of strings (or single string)
                if self._expr.delete is not None:
                    deletions = self._jsonata.eval(
                        self._expr.delete, match_, self._environment
                    )
                    if deletions is not None:
                        val = deletions
                        if not (isinstance(deletions, list)):
                            deletions = [deletions]
                        if not Utils.is_array_of_strings(deletions):
                            # throw type error
                            raise JException("T2012", self._expr.delete.position, val)
                        for item in deletions:
                            if isinstance(match_, dict):
                                match_.pop(item, None)
                                # delete match[deletions[jj]]

        return result
