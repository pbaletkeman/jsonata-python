# pylint: disable=locally-disabled, multiple-statements, fixme, line-too-long

"""
Symbol module for Jsonata Python implementation.
Defines the Symbol class for representing symbols in the JSONata parser, supporting infix, prefix, and other operator types.
"""

import copy

from typing import Any, MutableSequence, Optional, Sequence
from src.jsonata.JException.JException import JException


class Symbol:
    """
    Represents a symbol in the JSONata parser, supporting infix, prefix, and other operator types.
    """

    @property
    def jsonata_lambda(self):
        """
        Property indicating if this symbol is a JSONata lambda.
        Returns:
            True if lambda, False otherwise.
        """
        return self._jsonata_lambda

    def nud(self):
        """
        Null denotation method (unary operator handler).
        Returns:
            Symbol error if recoverable, else raises JException.
        """
        err = JException("S0211", self.position, self.value)
        if self._outer_instance.recover:
            return Symbol("(error)")
        else:
            raise err

    def led(self, left):
        """
        Left denotation method (infix operator handler).
        Args:
            left: The left operand.
        Raises:
            NotImplementedError: Always, as this is a base class.
        """
        raise NotImplementedError("led not implemented")

    _outer_instance: Optional[Any]
    id: Optional[str]
    type: Optional[str]
    value: Optional[Any]
    bp: int
    lbp: int
    position: int
    keep_array: bool
    descending: bool
    expression: "Optional[Symbol]"
    seeking_parent: "Optional[MutableSequence[Symbol]]"
    errors: Optional[Sequence[Exception]]
    steps: "Optional[MutableSequence[Symbol]]"
    slot: "Optional[Symbol]"
    next_function: "Optional[Symbol]"
    keep_singleton_array: bool
    consarray: bool
    level: int
    focus: Optional[Any]
    token: Optional[Any]
    thunk: bool

    # Procedure:
    procedure: "Optional[Symbol]"
    arguments: "Optional[MutableSequence[Symbol]]"
    body: "Optional[Symbol]"
    predicate: "Optional[MutableSequence[Symbol]]"
    stages: "Optional[MutableSequence[Symbol]]"
    input: Optional[Any]
    # environment: jsonata.Jsonata.Frame | None # creates circular ref
    tuple: Optional[Any]
    expr: Optional[Any]
    group: "Optional[Symbol]"
    name: "Optional[Symbol]"

    # Infix attributes
    lhs: "Optional[Symbol]"
    rhs: "Optional[Symbol]"

    # where rhs = list of Symbol pairs
    lhs_object: "Optional[Sequence[Sequence[Symbol]]]"
    rhs_object: "Optional[Sequence[Sequence[Symbol]]]"

    # where rhs = list of Symbols
    rhs_terms: "Optional[Sequence[Symbol]]"
    terms: "Optional[Sequence[Symbol]]"

    # Ternary operator:
    condition: "Optional[Symbol]"
    then: "Optional[Symbol]"
    _else: "Optional[Symbol]"

    expressions: "Optional[MutableSequence[Symbol]]"

    # processAST error handling
    error: "Optional[JException]"
    signature: "Optional[Any]"

    # Prefix attributes
    pattern: "Optional[Symbol]"
    update: "Optional[Symbol]"
    delete: "Optional[Symbol]"

    # Ancestor attributes
    label: Optional[str]
    index: Optional[Any]
    _jsonata_lambda: bool
    ancestor: "Optional[Symbol]"

    def __init__(self, outer_instance, symbol_id=None, bp=0):
        """
        Initialize a Symbol object with all attributes set to defaults.
        Args:
            outer_instance: The parser instance.
            symbol_id: The symbol identifier.
            bp: The binding power.
        """
        self._outer_instance = outer_instance
        self.id = symbol_id
        self.value = symbol_id
        self.bp = bp
        self.type = None
        self.lbp = 0
        self.position = 0
        self.keep_array = False
        self.descending = False
        self.expression = None
        self.seeking_parent = None
        self.errors = None
        self.steps = None
        self.slot = None
        self.next_function = None
        self.keep_singleton_array = False
        self.consarray = False
        self.level = 0
        self.focus = None
        self.token = None
        self.thunk = False
        self.procedure = None
        self.arguments = None
        self.body = None
        self.predicate = None
        self.stages = None
        self.input = None
        self.environment = None
        self.tuple = None
        self.expr = None
        self.group = None
        self.name = None
        self.lhs = None
        self.rhs = None
        self.lhs_object = None
        self.rhs_object = None
        self.rhs_terms = None
        self.terms = None
        self.condition = None
        self.then = None
        self._else = None
        self.expressions = None
        self.error = None
        self.signature = None
        self.pattern = None
        self.update = None
        self.delete = None
        self.label = None
        self.index = None
        self._jsonata_lambda = False
        self.ancestor = None

    def create(self):
        """
        Create a shallow clone of this Symbol.
        Returns:
            A shallow copy of the Symbol instance.
        """
        cl = self.clone()
        return cl

    def clone(self):
        """
        Return a shallow copy of this Symbol.
        Returns:
            A shallow copy of the Symbol instance.
        """
        return copy.copy(self)

    def __repr__(self):
        """
        Return a string representation of the Symbol.
        Returns:
            A string describing the Symbol instance.
        """
        return str(type(self)) + " " + str(self.id) + " value=" + str(self.value)
