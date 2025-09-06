from src.jsonata.Parser.Infix import Infix
from src.jsonata.Parser.Parser import Parser


class InfixIn(Infix):
    _outer_instance: "Parser"

    def __init__(self, outer_instance):
        super().__init__(outer_instance, "in")
        self._outer_instance = outer_instance

    # allow as terminal
    def nud(self):
        return self
