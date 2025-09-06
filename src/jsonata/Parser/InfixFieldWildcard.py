from Parser.Infix import Infix
from Parser.Parser import Parser


class InfixFieldWildcard(Infix):
    _outer_instance: "Parser"

    def __init__(self, outer_instance):
        super().__init__(outer_instance, "*")
        self._outer_instance = outer_instance

    # field wildcard (single level)
    def nud(self):
        self.type = "wildcard"
        return self
