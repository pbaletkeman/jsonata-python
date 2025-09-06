from src.jsonata.JException.JException import JException
from src.jsonata.Parser.InfixR import InfixR
from src.jsonata.Parser.Parser import Parser
from src.jsonata.Tokenizer.Tokenizer import Tokenizer


class InfixRBindVariable(InfixR):
    """
    Represents the right-associative bind variable operator (:=) for the parser.
    """

    _outer_instance: "Parser"

    def __init__(self, outer_instance, get):
        """
        Initialize the InfixRBindVariable operator.
        Args:
            outer_instance: The parser instance.
            get: The get function or value for the operator.
        """
        super().__init__(outer_instance, ":=", get)
        self._outer_instance = outer_instance

    def led(self, left):
        """
        Left denotation method for the bind variable operator.
        Args:
            left: The left operand.
        Returns:
            The modified operator instance.
        """
        if left.type != "variable":
            return self._outer_instance.handle_error(
                JException("S0212", left.position, left.value)
            )
        self.lhs = left
        self.rhs = self._outer_instance.expression(
            Tokenizer.operators[":="] - 1
        )  # subtract 1 from bindingPower for right associative operators
        self.type = "binary"
        return self
