from Infix import Infix
from Parser.Parser import Parser
from Tokenizer.Tokenizer import Tokenizer


class InfixArrayConstructor(Infix):
    _outer_instance: "Parser"

    def __init__(self, outer_instance, get):
        super().__init__(outer_instance, "[", get)
        self._outer_instance = outer_instance

    def nud(self):
        a = []
        if self._outer_instance.node.id != "]":
            while True:
                item = self._outer_instance.expression(0)
                if self._outer_instance.node.id == "..":
                    # range operator
                    range = Parser.Symbol(self._outer_instance)
                    range.type = "binary"
                    range.value = ".."
                    range.position = self._outer_instance.node.position
                    range.lhs = item
                    self._outer_instance.advance("..")
                    range.rhs = self._outer_instance.expression(0)
                    item = range
                a.append(item)
                if self._outer_instance.node.id != ",":
                    break
                self._outer_instance.advance(",")
        self._outer_instance.advance("]", True)
        self.expressions = a
        self.type = "unary"
        return self

    # })

    # filter - predicate or array index
    # register(new Infix("[", tokenizer.Tokenizer.operators.get("[")) {

    def led(self, left):
        if self._outer_instance.node.id == "]":
            # empty predicate means maintain singleton arrays in the output
            step = left
            while step is not None and step.type == "binary" and step.value == "[":
                step = step.lhs
            step.keep_array = True
            self._outer_instance.advance("]")
            return left
        else:
            self.lhs = left
            self.rhs = self._outer_instance.expression(Tokenizer.operators["]"])
            self.type = "binary"
            self._outer_instance.advance("]", True)
            return self
