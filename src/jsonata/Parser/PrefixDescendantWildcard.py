from .Prefix import Prefix
from .Parser import Parser


class PrefixDescendantWildcard(Prefix):
    _outer_instance: "Parser"

    def __init__(self, outer_instance):
        super().__init__(outer_instance, "**")
        self._outer_instance = outer_instance

    def nud(self):
        self.type = "descendant"
        return self
