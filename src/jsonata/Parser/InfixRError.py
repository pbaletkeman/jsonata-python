# pylint: disable=locally-disabled, multiple-statements, fixme, line-too-long

"""
InfixRError module for Jsonata Python implementation.
Defines the InfixRError class for representing error operators in the Jsonata parser.
"""


from src.jsonata.Parser.Infix import Infix
from src.jsonata.Parser.Parser import Parser


class InfixRError(Infix):
    """
    Represents an infix error operator for the parser.
    """

    _outer_instance: "Parser"

    def __init__(self, outer_instance):
        """
        Initialize the InfixRError operator.
        Args:
            outer_instance: The parser instance.
        """
        super().__init__(outer_instance, "(error)", 10)
        self._outer_instance = outer_instance

    def led(self, left):
        """
        Left denotation method for the error operator.
        Args:
            left: The left operand.
        Raises:
            NotImplementedError: Always, as this is a placeholder.
        """
        raise NotImplementedError("TODO", None)
