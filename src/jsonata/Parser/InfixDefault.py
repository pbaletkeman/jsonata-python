from Parser.Infix import Infix
from Parser.Parser import Parser


class InfixDefault(Infix):
    _outer_instance: "Parser"

    def __init__(self, outer_instance, get):
        super().__init__(outer_instance, "?:", get)
        self._outer_instance = outer_instance

    def led(self, left):
        self.type = "condition"
        self.condition = left
        self.then = left
        self._else = self._outer_instance.expression(0)
        return self
