from Parser.Infix import Infix
from Parser.Parser import Parser


class InfixAndPrefix(Infix):
    _outer_instance: "Parser"
    prefix: "Parser.Prefix"

    def __init__(self, outer_instance, id, bp=0):
        super().__init__(outer_instance, id, bp)
        self._outer_instance = outer_instance

        self.prefix = Parser.Prefix(outer_instance, id)

    def nud(self):
        return self.prefix.nud()
        # expression(70)
        # type="unary"
        # return this

    def clone(self):
        c = super().clone()
        # IMPORTANT: make sure to allocate a new Prefix!!!
        c.prefix = Parser.Prefix(self._outer_instance, c.id)
        return c
