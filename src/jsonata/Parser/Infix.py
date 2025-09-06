# match infix operators
# <expression> <operator> <expression>
# left associative
from .Symbol import Symbol
from ..Tokenizer.Tokenizer import Tokenizer
from .Parser import Parser


class Infix(Symbol):
    _outer_instance: "Parser"

    def __init__(self, outer_instance, id, bp=0):
        super().__init__(
            outer_instance,
            id,
            (bp if bp != 0 else (Tokenizer.operators[id] if id is not None else 0)),
        )
        self._outer_instance = outer_instance

    def led(self, left):
        self.lhs = left
        self.rhs = self._outer_instance.expression(self.bp)
        self.type = "binary"
        return self
