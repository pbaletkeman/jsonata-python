from src.jsonata.Parser.Symbol import Symbol


class Terminal(Symbol):
    _outer_instance: object

    def __init__(self, outer_instance, symbol_id):
        super().__init__(outer_instance, symbol_id, 0)
        self._outer_instance = outer_instance

    def nud(self):
        return self

    def led(self, left):
        raise NotImplementedError("led not implemented in Terminal")
