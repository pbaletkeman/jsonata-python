from .Parser import Parser
from .Symbol import Symbol


class Terminal(Symbol):
    _outer_instance: "Parser"

    def __init__(self, outer_instance, id):
        super().__init__(outer_instance, id, 0)
        self._outer_instance = outer_instance

    def nud(self):
        return self
