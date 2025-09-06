# match prefix operators
# <operator> <expression>
from src.jsonata.Parser.Symbol import Symbol


class Prefix(Symbol):

    # public List<Symbol[]> lhs

    def __init__(self, outer_instance, id):
        super().__init__(outer_instance, id)
        self._outer_instance = outer_instance
        # type = "unary"

    # Symbol _expression

    def nud(self):
        self.expression = self._outer_instance.expression(70)
        self.type = "unary"
        return self
