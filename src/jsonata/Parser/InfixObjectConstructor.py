from Parser.Infix import Infix
from Parser.Parser import Parser


class InfixObjectConstructor(Infix):
    _outer_instance: "Parser"

    def __init__(self, outer_instance, get):
        super().__init__(outer_instance, "{", get)
        self._outer_instance = outer_instance

    # merged register(new Prefix("{") {

    def nud(self):
        return self._outer_instance.object_parser(None)

    # })

    # register(new Infix("{", tokenizer.Tokenizer.operators.get("{")) {

    def led(self, left):
        return self._outer_instance.object_parser(left)
