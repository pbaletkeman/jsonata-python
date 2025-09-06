from src.jsonata.Parser.Infix import Infix
from src.jsonata.Parser.Parser import Parser


class InfixParentOperator(Infix):
    _outer_instance: "Parser"

    def __init__(self, outer_instance):
        super().__init__(outer_instance, "%")
        self._outer_instance = outer_instance

    # parent operator
    def nud(self):
        self.type = "parent"
        return self
