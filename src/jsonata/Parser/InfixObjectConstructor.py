from src.jsonata.Parser.Infix import Infix
from src.jsonata.Parser.Parser import Parser


class InfixObjectConstructor(Infix):
    """
    Represents the infix object constructor operator ({) in the Jsonata parser.
    Handles object construction in expressions.
    """

    _outer_instance: "Parser"

    def __init__(self, outer_instance, get):
        """
        Initialize an InfixObjectConstructor symbol for the object constructor operator.
        Args:
            outer_instance: The parser instance.
            get: Binding power or precedence value.
        """
        super().__init__(outer_instance, "{", get)
        self._outer_instance = outer_instance

    def nud(self):
        """
        Handles the null denotation for the object constructor operator ({).
        Invokes the object parser with None as the left operand.
        Returns:
            Result of object_parser(None).
        """
        return self._outer_instance.object_parser(None)

    def led(self, left):
        """
        Handles the left denotation for the object constructor operator ({).
        Invokes the object parser with the left operand.
        Args:
            left: The left operand.
        Returns:
            Result of object_parser(left).
        """
        return self._outer_instance.object_parser(left)
