# pylint: disable=locally-disabled, multiple-statements, fixme, line-too-long

"""
InfixOr module for Jsonata Python implementation.
Defines the InfixOr class for logical OR operations in the Jsonata parser.
"""


from src.jsonata.Parser.Infix import Infix
from src.jsonata.Parser.Parser import Parser


class InfixOr(Infix):
    """
    Represents the infix 'or' operator in the Jsonata parser.
    Used to perform logical OR operations.
    """

    _outer_instance: "Parser"

    def __init__(self, outer_instance):
        """
        Initialize an InfixOr symbol for the 'or' operator.
        Args:
            outer_instance: The parser instance.
        """
        super().__init__(outer_instance, "or")
        self._outer_instance = outer_instance

    def nud(self):
        """
        Handles the null denotation for the 'or' operator.
        Allows 'or' to be used as a terminal symbol.
        Returns:
            InfixOr: The instance itself.
        """
        return self
