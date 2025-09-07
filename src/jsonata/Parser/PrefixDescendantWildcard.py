from src.jsonata.Parser.Prefix import Prefix
from src.jsonata.Parser.Parser import Parser


class PrefixDescendantWildcard(Prefix):
    """
    Represents the prefix descendant wildcard operator (**) in the Jsonata parser.
    Used to match all descendant fields in an object or array.
    """

    _outer_instance: "Parser"

    def __init__(self, outer_instance):
        """
        Initialize a PrefixDescendantWildcard symbol for the descendant wildcard operator.
        Args:
            outer_instance: The parser instance.
        """
        super().__init__(outer_instance, "**")
        self._outer_instance = outer_instance

    def nud(self):
        """
        Handles the null denotation for the descendant wildcard operator (**).
        Sets the type to 'descendant'.
        Returns:
            PrefixDescendantWildcard: The instance itself.
        """
        self.type = "descendant"
        return self
