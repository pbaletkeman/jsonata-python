# match infix operators
# <expression> <operator> <expression>
# right associative

from src.jsonata.Parser.Symbol import Symbol


class InfixR(Symbol):
    """
    Represents a right-associative infix operator for the parser.
    """

    _outer_instance: object

    def __init__(self, outer_instance, symbol_id, bp):
        """
        Initialize the InfixR operator.
        Args:
            outer_instance: The parser instance.
            symbol_id: The symbol identifier for the operator.
            bp: The binding power of the operator.
        """
        super().__init__(outer_instance, symbol_id, bp)
        self._outer_instance = outer_instance

    def led(self, left):
        """
        Left denotation method for the right-associative operator.
        Args:
            left: The left operand.
        Raises:
            NotImplementedError: Always, as this is a base class.
        """
        raise NotImplementedError("led not implemented in InfixR")
