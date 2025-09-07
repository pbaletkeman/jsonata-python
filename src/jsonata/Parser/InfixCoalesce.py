# pylint: disable=locally-disabled, multiple-statements, fixme, line-too-long

"""
This module defines the InfixCoalesce class for handling the coalesce (??) operator in the Jsonata parser.
It provides logic for conditional coalescing of values, integrating with the parser's symbol and infix framework.
"""


from src.jsonata.Parser.Infix import Infix
from src.jsonata.Parser.Symbol import Symbol


class InfixCoalesce(Infix):
    """
    Represents the coalesce infix operator (??) in the Jsonata parser.
    Handles conditional logic for coalescing values.
    """

    _outer_instance: object

    def __init__(self, outer_instance, get):
        """
        Initialize an InfixCoalesce symbol for the coalesce operator.
        Args:
            outer_instance: The parser instance.
            get: Binding power or precedence value.
        """
        super().__init__(outer_instance, "??", get)
        self._outer_instance = outer_instance

    def led(self, left):
        """
        Handles the left denotation for the coalesce operator (??).
        Sets up a condition using the 'exists' function, assigns then/else branches.
        Args:
            left: The left operand.
        Returns:
            InfixCoalesce: The updated instance.
        """
        self.type = "condition"
        # condition becomes function exists(left)
        cond = Symbol(self._outer_instance)
        cond.type = "function"
        cond.value = "("
        proc = Symbol(self._outer_instance)
        proc.type = "variable"
        proc.value = "exists"
        cond.procedure = proc
        cond.arguments = [left]
        self.condition = cond
        self.then = left
        self._else = self._outer_instance.expression(0)
        return self
