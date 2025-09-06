# match infix operators
# <expression> <operator> <expression>
# right associative
from .Parser import Parser
from .Symbol import Symbol


class InfixR(Symbol):
    _outer_instance: "Parser"

    def __init__(self, outer_instance, id, bp):
        super().__init__(outer_instance, id, bp)
        self._outer_instance = outer_instance

    # abstract Object led()
