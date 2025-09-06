# match infix operators
# <expression> <operator> <expression>
# right associative

from src.jsonata.Parser.Symbol import Symbol


class InfixR(Symbol):
    _outer_instance: object

    def __init__(self, outer_instance, symbol_id, bp):
        super().__init__(outer_instance, symbol_id, bp)
        self._outer_instance = outer_instance

    def led(self, left):
        raise NotImplementedError("led not implemented in InfixR")
