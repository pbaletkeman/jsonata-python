from src.jsonata.Parser.Infix import Infix
from src.jsonata.Parser.Symbol import Symbol


class InfixCoalesce(Infix):
    _outer_instance: object

    def __init__(self, outer_instance, get):
        super().__init__(outer_instance, "??", get)
        self._outer_instance = outer_instance

    def led(self, left):
        self.type = "condition"
        # condition becomes function exists(left)
        cond = Symbol(self._outer_instance)
        cond.type = "function"
        cond.value = "("
        proc = Symbol(self._outer_instance)
        proc.type = "variable"
        proc.value = "exists"
        cond.procedure = proc
        cond.arguments = [left]
        self.condition = cond
        self.then = left
        self._else = self._outer_instance.expression(0)
        return self
