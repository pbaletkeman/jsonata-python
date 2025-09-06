from typing import Any, MutableSequence, Optional, Sequence
from src.jsonata.JException.JException import JException
import copy


class Symbol:
    # Symbol s

    # Procedure:

    # Infix attributes
    # where rhs = list of Symbol pairs
    # where rhs = list of Symbols

    # Ternary operator:

    # processAST error handling

    # Prefix attributes

    # Ancestor attributes

    def nud(self):
        # error - symbol has been invoked as a unary operator
        err = JException("S0211", self.position, self.value)
        if self._outer_instance.recover:
            # err.remaining = remainingTokens()
            # err.type = "error"
            # errors.add(err)
            # return err
            return Symbol("(error)")
        else:
            raise err

    def led(self, left):
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
        self._outer_instance = outer_instance
        self.id = symbol_id
        self.value = symbol_id
        self.bp = bp
        # use register(Symbol) ! Otherwise inheritance doesn't work
        #            Symbol s = symbolTable.get(id)
        #            //bp = bp != 0 ? bp : 0
        #            if (s != null) {
        #                if (bp >= s.lbp) {
        #                    s.lbp = bp
        #                }
        #            } else {
        #                s = new Symbol()
        #                s.value = s.id = id
        #                s.lbp = bp
        #                symbolTable.put(id, s)
        #            }
        #
        #
        # return s

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
        # We want a shallow clone (do not duplicate outer class!)
        cl = self.clone()
        # System.err.println("cloning "+this+" clone="+cl)
        return cl

    def clone(self):
        return copy.copy(self)

    def __repr__(self):
        return str(type(self)) + " " + self.id + " value=" + self.value
