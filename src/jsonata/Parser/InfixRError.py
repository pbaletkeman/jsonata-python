from .Infix import Infix
from .Parser import Parser


class InfixRError(Infix):
    _outer_instance: "Parser"

    def __init__(self, outer_instance):
        super().__init__(outer_instance, "(error)", 10)
        self._outer_instance = outer_instance

    def led(self, left):
        raise NotImplementedError("TODO", None)
