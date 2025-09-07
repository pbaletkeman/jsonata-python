# pylint: disable=locally-disabled, multiple-statements, fixme, line-too-long

"""
This module defines the Infix class for handling infix operators in the Jsonata parser.
It provides logic for parsing left-associative binary expressions and integrating with the parser's symbol and tokenizer framework.
"""


# match infix operators
# <expression> <operator> <expression>
# left associative
from src.jsonata.Parser.Symbol import Symbol
from src.jsonata.Tokenizer.Tokenizer import Tokenizer
from src.jsonata.Parser.Parser import Parser


class Infix(Symbol):
    """
    Represents an infix operator in the Jsonata parser (e.g., <expr> <op> <expr>).
    Handles left-associative binary expressions.
    """

    _outer_instance: "Parser"

    def __init__(self, outer_instance, op_id, bp=0):
        """
        Initialize an Infix symbol for parsing binary expressions.
        Args:
            outer_instance (Parser): The parser instance.
            op_id: Operator identifier.
            bp (int): Binding power (precedence).
        """
        super().__init__(
            outer_instance,
            op_id,
            (
                bp
                if bp != 0
                else (Tokenizer.operators[op_id] if op_id is not None else 0)
            ),
        )
        self._outer_instance = outer_instance

    def led(self, left):
        """
        Parse the right-hand side of a binary infix expression.
        Args:
            left: The left-hand side expression.
        Returns:
            Infix: The completed binary expression node.
        """
        self.lhs = left
        self.rhs = self._outer_instance.expression(self.bp)
        self.type = "binary"
        return self
