# pylint: disable=locally-disabled, multiple-statements, fixme, line-too-long

"""
InfixTernaryOperator module for Jsonata Python implementation.
Defines the InfixTernaryOperator class for handling ternary conditional expressions in the Jsonata parser.
"""


from src.jsonata.Parser.Infix import Infix
from src.jsonata.Parser.Parser import Parser


class InfixTernaryOperator(Infix):
    """
    Represents the infix ternary operator (?) in the Jsonata parser.
    Handles conditional expressions with then/else branches.
    """

    _outer_instance: "Parser"

    def __init__(self, outer_instance, get):
        """
        Initialize an InfixTernaryOperator symbol for the ternary operator.
        Args:
            outer_instance: The parser instance.
            get: Binding power or precedence value.
        """
        super().__init__(outer_instance, "?", get)
        self._outer_instance = outer_instance

    def led(self, left):
        """
        Handles the left denotation for the ternary operator (?).
        Sets up condition, then, and else branches for conditional logic.
        Args:
            left: The left operand (condition).
        Returns:
            InfixTernaryOperator: The updated instance.
        """
        self.type = "condition"
        self.condition = left
        self.then = self._outer_instance.expression(0)
        if self._outer_instance.node.id == ":":
            # else condition
            self._outer_instance.advance(":")
            self._else = self._outer_instance.expression(0)
        return self
