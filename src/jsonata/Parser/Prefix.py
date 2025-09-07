# match prefix operators
# <operator> <expression>
from src.jsonata.Parser.Symbol import Symbol


class Prefix(Symbol):
    """
    Represents a prefix operator in the Jsonata parser.
    Handles unary prefix operations (e.g., -x, !x).
    """

    def __init__(self, outer_instance, id):
        """
        Initialize a Prefix symbol for a prefix operator.
        Args:
            outer_instance: The parser instance.
            id: The operator identifier.
        """
        super().__init__(outer_instance, id)
        self._outer_instance = outer_instance

    def nud(self):
        """
        Handles the null denotation for prefix operators.
        Parses the expression with high precedence and sets type to 'unary'.
        Returns:
            Prefix: The updated instance.
        """
        self.expression = self._outer_instance.expression(70)
        self.type = "unary"
        return self
