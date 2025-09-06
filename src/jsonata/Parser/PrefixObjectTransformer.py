from Parser.Parser import Parser
from Parser.Prefix import Prefix


class PrefixObjectTransformer(Prefix):
    _outer_instance: "Parser"

    def __init__(self, outer_instance):
        super().__init__(outer_instance, "|")
        self._outer_instance = outer_instance

    def nud(self):
        self.type = "transform"
        self.pattern = self._outer_instance.expression(0)
        self._outer_instance.advance("|")
        self.update = self._outer_instance.expression(0)
        if self._outer_instance.node.id == ",":
            self._outer_instance.advance(",")
            self.delete = self._outer_instance.expression(0)
        self._outer_instance.advance("|")
        return self
