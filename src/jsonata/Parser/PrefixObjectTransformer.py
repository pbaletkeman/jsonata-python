"""
PrefixObjectTransformer module for JSONata Python implementation.
Handles the prefix object transformer operator (|), enabling object transformation, updates, and deletions in JSONata expressions.
"""

from src.jsonata.Parser.Parser import Parser
from src.jsonata.Parser.Prefix import Prefix


class PrefixObjectTransformer(Prefix):
    """
    Represents the prefix object transformer operator (|) in the Jsonata parser.
    Handles object transformation patterns, updates, and deletions.
    """

    _outer_instance: "Parser"

    def __init__(self, outer_instance):
        """
        Initialize a PrefixObjectTransformer symbol for the object transformer operator.
        Args:
            outer_instance: The parser instance.
        """
        super().__init__(outer_instance, "|")
        self._outer_instance = outer_instance

    def nud(self):
        """
        Handles the null denotation for the object transformer operator (|).
        Parses the pattern, update, and optional delete expressions.
        Returns:
            PrefixObjectTransformer: The updated instance.
        """
        self.type = "transform"
        self.pattern = self._outer_instance.expression(0)
        self._outer_instance.advance("|")
        self.update = self._outer_instance.expression(0)
        if self._outer_instance.node.id == ",":
            self._outer_instance.advance(",")
            self.delete = self._outer_instance.expression(0)
        self._outer_instance.advance("|")
        return self
