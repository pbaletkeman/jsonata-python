from src.jsonata.Parser.Infix import Infix
from src.jsonata.Parser.Parser import Parser


class InfixFieldWildcard(Infix):
    """
    Represents the infix field wildcard operator ([*]) in the Jsonata parser.
    Used to match all fields in an object or array at a single level.
    """

    _outer_instance: "Parser"

    def __init__(self, outer_instance):
        """
        Initialize an InfixFieldWildcard symbol for the field wildcard operator.
        Args:
            outer_instance: The parser instance.
        """
        super().__init__(outer_instance, "*")
        self._outer_instance = outer_instance

    def nud(self):
        """
        Handles the null denotation for the field wildcard operator ([*]).
        Sets the type to 'wildcard' and returns self.
        Returns:
            InfixFieldWildcard: The updated instance.
        """
        self.type = "wildcard"
        return self
