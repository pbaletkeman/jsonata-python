# pylint: disable=locally-disabled, multiple-statements, fixme, line-too-long

"""
InfixDefault module for Jsonata Python implementation.
Defines the InfixDefault class for default value operators in the Jsonata parser.
"""


from src.jsonata.Parser.Infix import Infix
from src.jsonata.Parser.Parser import Parser


class InfixDefault(Infix):
    """
    Represents the default infix operator (?:) in the Jsonata parser.
    Handles conditional logic for default values.
    """

    _outer_instance: "Parser"

    def __init__(self, outer_instance, get):
        """
        Initialize an InfixDefault symbol for the default operator.
        Args:
            outer_instance: The parser instance.
            get: Binding power or precedence value.
        """
        super().__init__(outer_instance, "?:", get)
        self._outer_instance = outer_instance

    def led(self, left):
        """
        Handles the left denotation for the default operator (?:).
        Sets the type to 'condition', assigns left to condition and then, and evaluates the else branch.
        Args:
            left: The left operand.
        Returns:
            InfixDefault: The updated instance.
        """
        self.type = "condition"
        self.condition = left
        self.then = left
        self._else = self._outer_instance.expression(0)
        return self
