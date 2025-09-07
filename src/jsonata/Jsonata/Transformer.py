# pylint: disable=locally-disabled, multiple-statements, fixme, line-too-long

"""
Transformer module for Jsonata Python implementation.
Defines the Transformer class for object transformation operations in Jsonata expressions.
"""


from typing import Any, Optional, Sequence, TYPE_CHECKING

if TYPE_CHECKING:
    from src.jsonata.Jsonata.Jsonata import Jsonata

from src.jsonata.Parser.Symbol import Symbol
from src.jsonata.JException.JException import JException
from src.jsonata.Jsonata.JFunctionCallable import JFunctionCallable
from src.jsonata.Jsonata.Frame import Frame
from src.jsonata.Utils.Utils import Utils


class Transformer(JFunctionCallable):
    """
    Represents a JSONata transformer function for object transformation operations.
    """

    _jsonata: "Jsonata"
    _expr: Optional[Symbol]
    _environment: Optional[Frame]

    def __init__(self, jsonata, expr, environment):
        """
        Initialize a Transformer object.
        Args:
            jsonata: The Jsonata instance.
            expr: The transformation expression.
            environment: The evaluation environment.
        """
        self._jsonata = jsonata
        self._expr = expr
        self._environment = environment

    def call(self, input_: Optional[Any], args: Optional[Sequence]) -> Optional[Any]:
        """
        Call the transformer function to apply object transformations.
        Args:
            input_: The input item (unused).
            args: Arguments to the transformer (expects object to transform).
        Returns:
            The transformed object, or None if input is undefined.
        Raises:
            JException: If update or delete operations are invalid.
        """
        from src.jsonata.Functions.Functions import Functions

        obj = args[0]

        if obj is None or input_ is None:
            return None

        result = Functions.function_clone(obj)

        matches = self._jsonata.eval(self._expr.pattern, result, self._environment)
        if matches is not None:
            if not isinstance(matches, list):
                matches = [matches]
            for match_ in matches:
                update = self._jsonata.eval(
                    self._expr.update, match_, self._environment
                )
                if update is not None:
                    if not isinstance(update, dict):
                        raise JException("T2011", self._expr.update.position, update)
                    for k in update.keys():
                        match_[k] = update[k]

                if self._expr.delete is not None:
                    deletions = self._jsonata.eval(
                        self._expr.delete, match_, self._environment
                    )
                    if deletions is not None:
                        val = deletions
                        if not isinstance(deletions, list):
                            deletions = [deletions]
                        if not Utils.is_array_of_strings(deletions):
                            raise JException("T2012", self._expr.delete.position, val)
                        for item in deletions:
                            if isinstance(match_, dict):
                                match_.pop(item, None)

        return result
