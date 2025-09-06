from Parser.Infix import Infix
from Parser.Parser import Parser


class InfixCoalesce(Infix):
    _outer_instance: "Parser"

    def __init__(self, outer_instance, get):
        super().__init__(outer_instance, "??", get)
        self._outer_instance = outer_instance

    def led(self, left):
        self.type = "condition"
        # condition becomes function exists(left)
        cond = Parser.Symbol(self._outer_instance)
        cond.type = "function"
        cond.value = "("
        proc = Parser.Symbol(self._outer_instance)
        proc.type = "variable"
        proc.value = "exists"
        cond.procedure = proc
        cond.arguments = [left]
        self.condition = cond
        self.then = left
        self._else = self._outer_instance.expression(0)
        return self
