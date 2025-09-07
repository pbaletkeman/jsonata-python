# pylint: disable=locally-disabled, multiple-statements, fixme, line-too-long

"""
InfixIn module for Jsonata Python implementation.
Defines the InfixIn class for membership checking operators in the Jsonata parser.
"""


from src.jsonata.Parser.Infix import Infix
from src.jsonata.Parser.Parser import Parser


class InfixIn(Infix):
    """
    Represents the infix 'in' operator in the Jsonata parser.
    Used to check membership of a value in a collection.
    """

    _outer_instance: "Parser"

    def __init__(self, outer_instance):
        """
        Initialize an InfixIn symbol for the 'in' operator.
        Args:
            outer_instance: The parser instance.
        """
        super().__init__(outer_instance, "in")
        self._outer_instance = outer_instance

    def nud(self):
        """
        Handles the null denotation for the 'in' operator.
        Allows 'in' to be used as a terminal symbol.
        Returns:
            InfixIn: The instance itself.
        """
        return self
