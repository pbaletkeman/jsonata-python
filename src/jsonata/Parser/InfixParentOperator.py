# pylint: disable=locally-disabled, multiple-statements, fixme, line-too-long

"""
InfixParentOperator module for Jsonata Python implementation.
Defines the InfixParentOperator class for parent context operators in the Jsonata parser.
"""

from src.jsonata.Parser.Infix import Infix
from src.jsonata.Parser.Parser import Parser


class InfixParentOperator(Infix):
    """
    Represents the infix parent operator (%) in the Jsonata parser.
    Used to refer to the parent context in expressions.
    """

    _outer_instance: "Parser"

    def __init__(self, outer_instance):
        """
        Initialize an InfixParentOperator symbol for the parent operator.
        Args:
            outer_instance: The parser instance.
        """
        super().__init__(outer_instance, "%")
        self._outer_instance = outer_instance

    def nud(self):
        """
        Handles the null denotation for the parent operator (%).
        Sets the type to 'parent'.
        Returns:
            InfixParentOperator: The instance itself.
        """
        self.type = "parent"
        return self
