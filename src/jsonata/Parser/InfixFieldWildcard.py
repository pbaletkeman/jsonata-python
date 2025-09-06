from src.jsonata.Parser.Infix import Infix
from src.jsonata.Parser.Parser import Parser


class InfixFieldWildcard(Infix):
    _outer_instance: "Parser"

    def __init__(self, outer_instance):
        super().__init__(outer_instance, "*")
        self._outer_instance = outer_instance

        # field wildcard (single level)
        def nud(self):
            """
            Handles the null denotation for the field wildcard operator.
            Sets the type to 'wildcard' and returns self.
            Returns:
                InfixFieldWildcard: The updated instance.
            """
            self.type = "wildcard"
            return self
