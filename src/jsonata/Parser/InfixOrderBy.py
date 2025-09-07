# pylint: disable=locally-disabled, multiple-statements, fixme, line-too-long

"""
InfixOrderBy module for Jsonata Python implementation.
Defines the InfixOrderBy and InfixParentOperator classes for sorting and parent context operators in the Jsonata parser.
"""


from src.jsonata.Parser.Symbol import Symbol
from src.jsonata.Parser.Infix import Infix
from src.jsonata.Parser.Parser import Parser


class InfixParentOperator(Infix):
    """
    Represents the infix parent operator (%) in the Jsonata parser.
    Used to refer to the parent context in expressions.
    """

    _outer_instance: "Parser"

    def __init__(self, outer_instance):
        """
        Initialize an InfixParentOperator symbol for the parent operator.
        Args:
            outer_instance: The parser instance.
        """
        super().__init__(outer_instance, "%")
        self._outer_instance = outer_instance

    def nud(self):
        """
        Handles the null denotation for the parent operator (%).
        Sets the type to 'parent'.
        Returns:
            InfixParentOperator: The instance itself.
        """
        self.type = "parent"
        return self


class InfixOrderBy(Infix):
    """
    Represents the infix order by operator (^) in the Jsonata parser.
    Used to specify sorting order for expressions.
    """

    _outer_instance: "Parser"

    def __init__(self, outer_instance, get):
        """
        Initialize an InfixOrderBy symbol for the order by operator.
        Args:
            outer_instance: The parser instance.
            get: Binding power or precedence value.
        """
        super().__init__(outer_instance, "^", get)
        self._outer_instance = outer_instance

    def led(self, left):
        """
        Handles the left denotation for the order by operator (^).
        Advances through sorting terms, sets ascending/descending, and collects expressions.
        Args:
            left: The left operand.
        Returns:
            InfixOrderBy: The updated instance.
        """
        self._outer_instance.advance("(")
        terms = []
        while True:
            term = Symbol(self._outer_instance)
            term.descending = False

            if self._outer_instance.node.id == "<":
                # ascending sort
                self._outer_instance.advance("<")
            elif self._outer_instance.node.id == ">":
                # descending sort
                term.descending = True
                self._outer_instance.advance(">")
            else:
                # unspecified - default to ascending
                pass
            term.expression = self._outer_instance.expression(0)
            terms.append(term)
            if self._outer_instance.node.id != ",":
                break
            self._outer_instance.advance(",")
        self._outer_instance.advance(")")
        self.lhs = left
        self.rhs_terms = terms
        self.type = "binary"
        return self
