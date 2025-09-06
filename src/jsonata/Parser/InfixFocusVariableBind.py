from src.jsonata.Parser.Infix import Infix
from src.jsonata.Parser.Parser import Parser
from src.jsonata.JException.JException import JException
from src.jsonata.Tokenizer.Tokenizer import Tokenizer


class InfixFocusVariableBind(Infix):
    _outer_instance: "Parser"

    def __init__(self, outer_instance, get):
        super().__init__(outer_instance, "@", get)
        self._outer_instance = outer_instance

    def led(self, left):
        self.lhs = left
        self.rhs = self._outer_instance.expression(Tokenizer.operators["@"])
        if self.rhs.type != "variable":
            return self._outer_instance.handle_error(
                JException("S0214", self.rhs.position, "@")
            )
        self.type = "binary"
        return self
