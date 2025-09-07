from src.jsonata.Parser.Infix import Infix
from typing import Optional, Any


class InfixAndPrefix(Infix):
    """
    Represents an infix operator that also supports prefix notation in the Jsonata parser.
    Handles both infix and prefix parsing logic.
    """

    _outer_instance: object
    prefix: Optional[Any]

    def __init__(self, outer_instance, symbol_id, bp=0):
        """
        Initialize an InfixAndPrefix symbol for infix and prefix operators.
        Args:
            outer_instance: The parser instance.
            symbol_id: Operator identifier.
            bp (int): Binding power (precedence).
        """
        super().__init__(outer_instance, symbol_id, bp)
        self._outer_instance = outer_instance
        self.prefix = outer_instance.Prefix(symbol_id)

    def nud(self):
        """
        Handles the null denotation for the and/prefix operator.
        Delegates to the prefix's nud method.
        Returns:
            Result of prefix.nud().
        """
        return self.prefix.nud()
        # expression(70)
        # type="unary"
        # return this

    def clone(self):
        """
        Creates a clone of the current instance, ensuring a new Prefix is allocated.
        Returns:
            InfixAndPrefix: The cloned instance.
        """
        c = super().clone()
        # IMPORTANT: make sure to allocate a new Prefix!!!
        c.prefix = self._outer_instance.Prefix(c.id)
        return c
