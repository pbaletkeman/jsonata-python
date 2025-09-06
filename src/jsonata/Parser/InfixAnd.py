from .Infix import Infix
from .Parser import Parser


class InfixAnd(Infix):
    _outer_instance: "Parser"

    def __init__(self, outer_instance):
        super().__init__(outer_instance, "and")
        self._outer_instance = outer_instance

    # allow as terminal
    def nud(self):
        return self
