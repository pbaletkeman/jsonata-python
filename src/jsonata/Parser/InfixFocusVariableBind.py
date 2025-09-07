from src.jsonata.Parser.Infix import Infix
from src.jsonata.Parser.Parser import Parser
from src.jsonata.JException.JException import JException
from src.jsonata.Tokenizer.Tokenizer import Tokenizer


class InfixFocusVariableBind(Infix):
    """
    Represents the infix focus variable bind operator (@) in the Jsonata parser.
    Used to bind a focus variable to an expression.
    """

    _outer_instance: "Parser"

    def __init__(self, outer_instance, get):
        """
        Initialize an InfixFocusVariableBind symbol for the focus variable bind operator.
        Args:
            outer_instance: The parser instance.
            get: Binding power or precedence value.
        """
        super().__init__(outer_instance, "@", get)
        self._outer_instance = outer_instance

    def led(self, left):
        """
        Handles the left denotation for the focus variable bind operator (@).
        Binds lhs and rhs, checks rhs type, and sets type to 'binary'.
        Args:
            left: The left operand.
        Returns:
            InfixFocusVariableBind: The updated instance or error handler result.
        """
        self.lhs = left
        self.rhs = self._outer_instance.expression(Tokenizer.operators["@"])
        if self.rhs.type != "variable":
            return self._outer_instance.handle_error(
                JException("S0214", self.rhs.position, "@")
            )
        self.type = "binary"
        return self
