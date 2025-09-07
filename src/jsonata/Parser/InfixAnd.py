from src.jsonata.Parser.Infix import Infix
from src.jsonata.Parser.Parser import Parser


class InfixAnd(Infix):
    """
    Represents the 'and' infix operator in the Jsonata parser.
    Allows 'and' to be used as a terminal symbol.
    """

    _outer_instance: "Parser"

    def __init__(self, outer_instance):
        """
        Initialize an InfixAnd symbol for the 'and' operator.
        Args:
            outer_instance (Parser): The parser instance.
        """
        super().__init__(outer_instance, "and")
        self._outer_instance = outer_instance

    def nud(self):
        """
        Allow 'and' to be used as a terminal symbol.
        Returns:
            InfixAnd: The current instance.
        """
        return self
