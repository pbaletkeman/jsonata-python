# pylint: disable=locally-disabled, multiple-statements, fixme, line-too-long

"""
Terminal module for Jsonata Python implementation.
Defines the Terminal class for terminal symbols in the Jsonata parser, representing tokens without further denotation.
"""


from src.jsonata.Parser.Symbol import Symbol


class Terminal(Symbol):
    """
    Represents a terminal symbol in the Jsonata parser.
    Used for tokens that do not have further denotation (e.g., literals, end markers).
    """

    _outer_instance: object

    def __init__(self, outer_instance, symbol_id):
        """
        Initialize a Terminal symbol.
        Args:
            outer_instance: The parser instance.
            symbol_id: The identifier for the terminal symbol.
        """
        super().__init__(outer_instance, symbol_id, 0)
        self._outer_instance = outer_instance

    def nud(self):
        """
        Handles the null denotation for terminal symbols.
        Returns:
            Terminal: The instance itself.
        """
        return self

    def led(self, left):
        """
        Terminal symbols do not support left denotation.
        Raises:
            NotImplementedError: Always, since terminals do not have left denotation.
        """
        raise NotImplementedError("led not implemented in Terminal")
