from src.jsonata.JException.JException import JException
from src.jsonata.Parser.Infix import Infix
from src.jsonata.Tokenizer.Tokenizer import Tokenizer
from src.jsonata.Parser.Parser import Parser


class InfixIndexVariableBind(Infix):
    """
    Represents the infix index variable bind operator (#) in the Jsonata parser.
    Used to bind an index variable to an expression.
    """

    _outer_instance: "Parser"

    def __init__(self, outer_instance, get):
        """
        Initialize an InfixIndexVariableBind symbol for the index variable bind operator.
        Args:
            outer_instance: The parser instance.
            get: Binding power or precedence value.
        """
        super().__init__(outer_instance, "#", get)
        self._outer_instance = outer_instance

    def led(self, left):
        """
        Handles the left denotation for the index variable bind operator (#).
        Binds lhs and rhs, checks rhs type, and sets type to 'binary'.
        Args:
            left: The left operand.
        Returns:
            InfixIndexVariableBind: The updated instance or error handler result.
        """
        self.lhs = left
        self.rhs = self._outer_instance.expression(Tokenizer.operators["#"])
        if self.rhs.type != "variable":
            return self._outer_instance.handle_error(
                JException("S0214", self.rhs.position, "#")
            )
        self.type = "binary"
        return self
