from .Infix import Infix
from .Parser import Parser


class InfixOrderBy(Infix):
    _outer_instance: "Parser"

    def __init__(self, outer_instance, get):
        super().__init__(outer_instance, "^", get)
        self._outer_instance = outer_instance

    def led(self, left):
        self._outer_instance.advance("(")
        terms = []
        while True:
            term = Parser.Symbol(self._outer_instance)
            term.descending = False

            if self._outer_instance.node.id == "<":
                # ascending sort
                self._outer_instance.advance("<")
            elif self._outer_instance.node.id == ">":
                # descending sort
                term.descending = True
                self._outer_instance.advance(">")
            else:
                # unspecified - default to ascending
                pass
            term.expression = self._outer_instance.expression(0)
            terms.append(term)
            if self._outer_instance.node.id != ",":
                break
            self._outer_instance.advance(",")
        self._outer_instance.advance(")")
        self.lhs = left
        self.rhs_terms = terms
        self.type = "binary"
        return self
