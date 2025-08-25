# cython: language_level=3
# Auto-generated Cython-optimized rewrite (conservative)
# NOTE: This preserves Python semantics while introducing cdef/cpdef and typed attributes where safe.

#
# Copyright Robert Yokota
#
# Licensed under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Derived from the following code:
#
#   Project name: jsonata-java
#   Copyright Dashjoin GmbH. https://dashjoin.com
#   Licensed under the Apache License, Version 2.0 (the "License")
#
#   Project name: JSONata
# © Copyright IBM Corp. 2016, 2018 All Rights Reserved
#   This project is licensed under the MIT License, see LICENSE
#

cimport cython
import copy
from typing import Any, MutableSequence, Optional, Sequence

from jsonata import jexception, tokenizer, signature, utils


# var parseSignature = require('./signature')
cdef class Symbol:

    cdef object _outer_instance
    cdef object _else
    cdef object id
    cdef object type
    cdef object value
    cdef int bp
    cdef int lbp
    cdef int position
    cdef bint keep_array
    cdef bint descending
    cdef object expression
    cdef object seeking_parent
    cdef object errors
    cdef object steps
    cdef object slot
    cdef object next_function
    cdef object keep_singleton_array
    cdef object consarray
    cdef object level
    cdef object focus
    cdef object token
    cdef object thunk
    cdef object procedure
    cdef object arguments
    cdef object body
    cdef object predicate
    cdef object stages
    cdef object input
    cdef object tuple
    cdef object expr
    cdef object group
    cdef object name
    cdef object lhs
    cdef object rhs
    cdef object lhs_object
    cdef object rhs_object
    cdef object rhs_terms
    cdef object terms
    cdef object condition
    cdef object then
    cdef object expressions
    cdef object error
    cdef object signature
    cdef object pattern
    cdef object update
    cdef object delete
    cdef object label
    cdef object index
    cdef object _jsonata_lambda
    cdef object ancestor
    cdef object prefix
    # Symbol s
    # Procedure:

    # Infix attributes
    # where rhs = list of Symbol pairs
    # where rhs = list of Symbols
    # Ternary operator:
    # processAST error handling
    # Prefix attributes
    # Ancestor attributes

    cpdef nud(self):
        # error - symbol has been invoked as a unary operator
        err = jexception.JException("S0211", self.position, self.value)

        if self._outer_instance.recover:
            #                
            #                err.remaining = remainingTokens()
            #                err.type = "error"
            #                errors.add(err)
            #                return err
            #                
            return Symbol("(error)")
        else:
            raise err

    cpdef led(self, left):
        raise NotImplementedError("led not implemented")

    _outer_instance: 'Parser'
    id: Optional[str]
    type: Optional[str]
    value: Optional[Any]
    bp: int
    lbp: int
    position: int
    keep_array: bool
    descending: bool
    expression: 'Optional[Symbol]'
    seeking_parent: 'Optional[MutableSequence[Symbol]]'
    errors: Optional[Sequence[Exception]]
    steps: 'Optional[MutableSequence[Symbol]]'
    slot: 'Optional[Symbol]'
    next_function: 'Optional[Symbol]'
    keep_singleton_array: bool
    consarray: bool
    level: int
    focus: Optional[Any]
    token: Optional[Any]
    thunk: bool

    # Procedure:
    procedure: 'Optional[Symbol]'
    arguments: 'Optional[MutableSequence[Symbol]]'
    body: 'Optional[Symbol]'
    predicate: 'Optional[MutableSequence[Symbol]]'
    stages: 'Optional[MutableSequence[Symbol]]'
    input: Optional[Any]
    # environment: jsonata.Jsonata.Frame | None # creates circular ref
    tuple: Optional[Any]
    expr: Optional[Any]
    group: 'Optional[Symbol]'
    name: 'Optional[Symbol]'

    # Infix attributes
    lhs: 'Optional[Symbol]'
    rhs: 'Optional[Symbol]'

    # where rhs = list of Symbol pairs
    lhs_object: 'Optional[Sequence[Sequence[Symbol]]]'
    rhs_object: 'Optional[Sequence[Sequence[Symbol]]]'

    # where rhs = list of Symbols
    rhs_terms: 'Optional[Sequence[Symbol]]'
    terms: 'Optional[Sequence[Symbol]]'

    # Ternary operator:
    condition: 'Optional[Symbol]'
    then: 'Optional[Symbol]'
    _else: 'Optional[Symbol]'

    expressions: 'Optional[MutableSequence[Symbol]]'

    # processAST error handling
    error: 'Optional[jexception.JException]'
    signature: 'Optional[Any]'

    # Prefix attributes
    pattern: 'Optional[Symbol]'
    update: 'Optional[Symbol]'
    delete: 'Optional[Symbol]'

    # Ancestor attributes
    label: Optional[str]
    index: Optional[Any]
    _jsonata_lambda: bool
    ancestor: 'Optional[Symbol]'

    def __init__(self, outer_instance, id=None, bp=0):
        self._outer_instance = outer_instance

        self.id = id
        self.value = id
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

    cpdef clone(self):
        return copy.copy(self)

    def __repr__(self):
        return str(type(self)) + " " + self.id + " value=" + self.value



cdef class InfixRBindVariable(InfixR):
    _outer_instance: 'Parser'

    def __init__(self, outer_instance, get):
        super().__init__(outer_instance, ":=", get)
        self._outer_instance = outer_instance

    cpdef led(self, left):
        if left.type != "variable":
            return self._outer_instance.handle_error(jexception.JException("S0212", left.position, left.value))
        self.lhs = left
        self.rhs = self._outer_instance.expression(
            tokenizer.Tokenizer.operators[":="] - 1)  # subtract 1 from bindingPower for right associative operators
        self.type = "binary"
        return self

cdef class InfixFocusVariableBind(Infix):
    _outer_instance: 'Parser'

    def __init__(self, outer_instance, get):
        super().__init__(outer_instance, "@", get)
        self._outer_instance = outer_instance

    cpdef led(self, left):
        self.lhs = left
        self.rhs = self._outer_instance.expression(tokenizer.Tokenizer.operators["@"])
        if self.rhs.type != "variable":
            return self._outer_instance.handle_error(jexception.JException("S0214", self.rhs.position, "@"))
        self.type = "binary"
        return self

cdef class InfixIndexVariableBind(Infix):
    _outer_instance: 'Parser'

    def __init__(self, outer_instance, get):
        super().__init__(outer_instance, "#", get)
        self._outer_instance = outer_instance

    cpdef led(self, left):
        self.lhs = left
        self.rhs = self._outer_instance.expression(tokenizer.Tokenizer.operators["#"])
        if self.rhs.type != "variable":
            return self._outer_instance.handle_error(jexception.JException("S0214", self.rhs.position, "#"))
        self.type = "binary"
        return self

cdef class InfixTernaryOperator(Infix):
    _outer_instance: 'Parser'

    def __init__(self, outer_instance, get):
        super().__init__(outer_instance, "?", get)
        self._outer_instance = outer_instance

    cpdef led(self, left):
        self.type = "condition"
        self.condition = left
        self.then = self._outer_instance.expression(0)
        if self._outer_instance.node.id == ":":
            # else condition
            self._outer_instance.advance(":")
            self._else = self._outer_instance.expression(0)
        return self

cdef class InfixCoalesce(Infix):
    _outer_instance: 'Parser'

    def __init__(self, outer_instance, get):
        super().__init__(outer_instance, "??", get)
        self._outer_instance = outer_instance

    cpdef led(self, left):
        self.type = "condition"
        # condition becomes function exists(left)
        cond = Symbol(self._outer_instance)
        cond.type = "function"
        cond.value = "("
        proc = Symbol(self._outer_instance)
        proc.type = "variable"
        proc.value = "exists"
        cond.procedure = proc
        cond.arguments = [left]
        self.condition = cond
        self.then = left
        self._else = self._outer_instance.expression(0)
        return self

cdef class InfixDefault(Infix):
    _outer_instance: 'Parser'

    def __init__(self, outer_instance, get):
        super().__init__(outer_instance, "?:", get)
        self._outer_instance = outer_instance

    cpdef led(self, left):
        self.type = "condition"
        self.condition = left
        self.then = left
        self._else = self._outer_instance.expression(0)
        return self

cdef class PrefixObjectTransformer(Prefix):
    _outer_instance: 'Parser'

    def __init__(self, outer_instance):
        super().__init__(outer_instance, "|")
        self._outer_instance = outer_instance

    cpdef nud(self):
        self.type = "transform"
        self.pattern = self._outer_instance.expression(0)
        self._outer_instance.advance("|")
        self.update = self._outer_instance.expression(0)
        if self._outer_instance.node.id == ",":
            self._outer_instance.advance(",")
            self.delete = self._outer_instance.expression(0)
        self._outer_instance.advance("|")
        return self

cdef class Terminal(Symbol):
    _outer_instance: 'Parser'

    def __init__(self, outer_instance, id):
        super().__init__(outer_instance, id, 0)
        self._outer_instance = outer_instance

    cpdef nud(self):
        return self

cdef class Infix(Symbol):
    _outer_instance: 'Parser'

    def __init__(self, outer_instance, id, bp=0):
        super().__init__(outer_instance, id, bp if bp != 0 else (tokenizer.Tokenizer.operators[id] if id is not None else 0))
        self._outer_instance = outer_instance

    cpdef led(self, left):
        self.lhs = left
        self.rhs = self._outer_instance.expression(self.bp)
        self.type = "binary"
        return self

cdef class InfixAndPrefix(Infix):
    _outer_instance: 'Parser'
    prefix: 'Prefix'

    def __init__(self, outer_instance, id, bp=0):
        super().__init__(outer_instance, id, bp)
        self._outer_instance = outer_instance

        self.prefix = Prefix(outer_instance, id)

    cpdef nud(self):
        return self.prefix.nud()
        # expression(70)
        # type="unary"
        # return this

    cpdef clone(self):
        c = super().clone()
        # IMPORTANT: make sure to allocate a new Prefix!!!
        c.prefix = Prefix(self._outer_instance, c.id)
        return c

cdef class InfixR(Symbol):
    _outer_instance: 'Parser'

    def __init__(self, outer_instance, id, bp):
        super().__init__(outer_instance, id, bp)
        self._outer_instance = outer_instance

    # abstract Object led()

cdef class Prefix(Symbol):

    # public List<Symbol[]> lhs

    def __init__(self, outer_instance, id):
        super().__init__(outer_instance, id)
        self._outer_instance = outer_instance
        # type = "unary"

    # Symbol _expression

    cpdef nud(self):
        self.expression = self._outer_instance.expression(70)
        self.type = "unary"
        return self

cdef class InfixFieldWildcard(Infix):
    _outer_instance: 'Parser'

    def __init__(self, outer_instance):
        super().__init__(outer_instance, "*")
        self._outer_instance = outer_instance

    # field wildcard (single level)
    cpdef nud(self):
        self.type = "wildcard"
        return self

cdef class InfixParentOperator(Infix):
    _outer_instance: 'Parser'

    def __init__(self, outer_instance):
        super().__init__(outer_instance, "%")
        self._outer_instance = outer_instance

    # parent operator
    cpdef nud(self):
        self.type = "parent"
        return self

cdef class InfixAnd(Infix):
    _outer_instance: 'Parser'

    def __init__(self, outer_instance):
        super().__init__(outer_instance, "and")
        self._outer_instance = outer_instance

    # allow as terminal
    cpdef nud(self):
        return self

cdef class InfixOr(Infix):
    _outer_instance: 'Parser'

    def __init__(self, outer_instance):
        super().__init__(outer_instance, "or")
        self._outer_instance = outer_instance

    # allow as terminal
    cpdef nud(self):
        return self

cdef class InfixIn(Infix):
    _outer_instance: 'Parser'

    def __init__(self, outer_instance):
        super().__init__(outer_instance, "in")
        self._outer_instance = outer_instance

    # allow as terminal
    cpdef nud(self):
        return self

cdef class InfixRError(Infix):
    _outer_instance: 'Parser'

    def __init__(self, outer_instance):
        super().__init__(outer_instance, "(error)", 10)
        self._outer_instance = outer_instance

    cpdef led(self, left):
        raise NotImplementedError("TODO", None)

cdef class PrefixDescendantWildcard(Prefix):
    _outer_instance: 'Parser'

    def __init__(self, outer_instance):
        super().__init__(outer_instance, "**")
        self._outer_instance = outer_instance

    cpdef nud(self):
        self.type = "descendant"
        return self

cdef class InfixFunctionInvocation(Infix):
    _outer_instance: 'Parser'

    def __init__(self, outer_instance, get):
        super().__init__(outer_instance, "(", get)
        self._outer_instance = outer_instance

    cpdef led(self, left):
        # left is is what we are trying to invoke
        self.procedure = left
        self.type = "function"
        self.arguments = []
        if self._outer_instance.node.id != ")":
            while True:
                if "operator" == self._outer_instance.node.type and self._outer_instance.node.id == "?":
                    # partial function application
                    self.type = "partial"
                    self.arguments.append(self._outer_instance.node)
                    self._outer_instance.advance("?")
                else:
                    self.arguments.append(self._outer_instance.expression(0))
                if self._outer_instance.node.id != ",":
                    break
                self._outer_instance.advance(",")
        self._outer_instance.advance(")", True)
        # if the name of the function is 'function' or λ, then this is function definition (lambda function)
        if left.type == "name" and (left.value == "function" or left.value == "\u03BB"):
            # all of the args must be VARIABLE tokens
            # int index = 0
            for arg in self.arguments:
                # this.arguments.forEach(function (arg, index) {
                if arg.type != "variable":
                    return self._outer_instance.handle_error(
                        jexception.JException("S0208", arg.position, arg.value))
                # index++
            self.type = "lambda"
            # is the next token a '<' - if so, parse the function signature
            if self._outer_instance.node.id == "<":
                depth = 1
                sig = "<"
                while depth > 0 and self._outer_instance.node.id != "{" and self._outer_instance.node.id != "(end)":
                    tok = self._outer_instance.advance()
                    if tok.id == ">":
                        depth -= 1
                    elif tok.id == "<":
                        depth += 1
                    sig += tok.value
                self._outer_instance.advance(">")
                self.signature = signature.Signature(sig, "lambda")
            # parse the function body
            self._outer_instance.advance("{")
            self.body = self._outer_instance.expression(0)
            self._outer_instance.advance("}")
        return self

    # })

    # parenthesis - block expression
    # Note: in Java both nud and led are in same class!
    # register(new Prefix("(") {

    cpdef nud(self):
        if self._outer_instance.dbg:
            print("Prefix (")
        expressions = []
        while self._outer_instance.node.id != ")":
            expressions.append(self._outer_instance.expression(0))
            if self._outer_instance.node.id != ";":
                break
            self._outer_instance.advance(";")
        self._outer_instance.advance(")", True)
        self.type = "block"
        self.expressions = expressions
        return self

cdef class InfixArrayConstructor(Infix):
    _outer_instance: 'Parser'

    def __init__(self, outer_instance, get):
        super().__init__(outer_instance, "[", get)
        self._outer_instance = outer_instance

    cpdef nud(self):
        a = []
        if self._outer_instance.node.id != "]":
            while True:
                item = self._outer_instance.expression(0)
                if self._outer_instance.node.id == "..":
                    # range operator
                    range = Symbol(self._outer_instance)
                    range.type = "binary"
                    range.value = ".."
                    range.position = self._outer_instance.node.position
                    range.lhs = item
                    self._outer_instance.advance("..")
                    range.rhs = self._outer_instance.expression(0)
                    item = range
                a.append(item)
                if self._outer_instance.node.id != ",":
                    break
                self._outer_instance.advance(",")
        self._outer_instance.advance("]", True)
        self.expressions = a
        self.type = "unary"
        return self

    # })

    # filter - predicate or array index
    # register(new Infix("[", tokenizer.Tokenizer.operators.get("[")) {

    cpdef led(self, left):
        if self._outer_instance.node.id == "]":
            # empty predicate means maintain singleton arrays in the output
            step = left
            while step is not None and step.type == "binary" and step.value == "[":
                step = step.lhs
            step.keep_array = True
            self._outer_instance.advance("]")
            return left
        else:
            self.lhs = left
            self.rhs = self._outer_instance.expression(tokenizer.Tokenizer.operators["]"])
            self.type = "binary"
            self._outer_instance.advance("]", True)
            return self

cdef class InfixOrderBy(Infix):
    _outer_instance: 'Parser'

    def __init__(self, outer_instance, get):
        super().__init__(outer_instance, "^", get)
        self._outer_instance = outer_instance

    cpdef led(self, left):
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

cdef class InfixObjectConstructor(Infix):
    _outer_instance: 'Parser'

    def __init__(self, outer_instance, get):
        super().__init__(outer_instance, "{", get)
        self._outer_instance = outer_instance

    # merged register(new Prefix("{") {

    cpdef nud(self):
        return self._outer_instance.object_parser(None)

    # })

    # register(new Infix("{", tokenizer.Tokenizer.operators.get("{")) {

    cpdef led(self, left):
        return self._outer_instance.object_parser(left)

cdef class Parser:

    cdef public bint dbg
    cdef object source
    cdef public bint recover
    cdef public Symbol node
    cdef object lexer
# This parser implements the 'Top down operator precedence' algorithm developed by Vaughan R Pratt; http://dl.acm.org/citation.cfm?id=512931.
    # and builds on the Javascript framework described by Douglas Crockford at http://javascript.crockford.com/tdop/tdop.html
    # and in 'Beautiful Code', edited by Andy Oram and Greg Wilson, Copyright 2007 O'Reilly Media, Inc. 798-0-596-51004-6

    # var parser = function (source, recover) {

    cpdef list[tokenizer.Tokenizer.Token] remaining_tokens(self):
        remaining = []
        if self.node.id != "(end)":
            t = tokenizer.Tokenizer.Token(self.node.type, self.node.value, self.node.position)
            remaining.append(t)
        nxt = self.lexer.next(False)
        while nxt is not None:
            remaining.append(nxt)
            nxt = self.lexer.next(False)
        return remaining

    def register(self, t: Symbol) -> None:

        # if (t instanceof Infix || t instanceof InfixR) return

        s = self.symbol_table.get(t.id)
        if s is not None:
            if self.dbg:
                print("Symbol in table " + t.id + " " + str(type(s)) + " -> " + str(type(t)))
            # symbolTable.put(t.id, t)
            if t.bp >= s.lbp:
                if self.dbg:
                    print("Symbol in table " + t.id + " lbp=" + str(s.lbp) + " -> " + str(t.bp))
                s.lbp = t.bp
        else:
            s = t.create()
            s.value = s.id = t.id
            s.lbp = t.bp
            self.symbol_table[t.id] = s

    cpdef Symbol handle_error(self, err: jexception.JException):
        if self.recover:
            err.remaining = self.remaining_tokens()
            self.errors.append(err)
            # Symbol symbol = symbolTable.get("(error)")
            node = Symbol(self)
            # FIXME node.error = err
            # node.type = "(error)"
            return node
        else:
            raise err

    # }

    cpdef Symbol advance(self, id: Optional[str] = None, infix: bool = False):
        if id is not None and self.node.id != id:
            code = None
            if self.node.id == "(end)":
                # unexpected end of buffer
                code = "S0203"
            else:
                code = "S0202"
            err = jexception.JException(code, self.node.position, id, self.node.value)
            return self.handle_error(err)
        next_token = self.lexer.next(infix)
        if self.dbg:
            print("nextToken " + (next_token.type if next_token is not None else None))
        if next_token is None:
            self.node = self.symbol_table["(end)"]
            self.node.position = len(self.source)
            return self.node
        value = next_token.value
        type = next_token.type
        symbol = None
        if type == "name" or type == "variable":
            symbol = self.symbol_table["(name)"]
        elif type == "operator":
            symbol = self.symbol_table[str(value)]
            if symbol is None:
                return self.handle_error(jexception.JException("S0204", next_token.position, value))
        elif type == "string" or type == "number" or type == "value":
            symbol = self.symbol_table["(literal)"]
        elif type == "regex":
            type = "regex"
            symbol = self.symbol_table["(regex)"]
            # istanbul ignore next
        else:
            return self.handle_error(jexception.JException("S0205", next_token.position, value))

        self.node = symbol.create()
        # Token node = new Token(); //Object.create(symbol)
        self.node.value = value
        self.node.type = type
        self.node.position = next_token.position
        if self.dbg:
            print("advance " + str(self.node))
        return self.node

    # Pratt's algorithm
    cpdef Symbol expression(self, rbp: int):
        left = None
        t = self.node
        self.advance(None, True)
        left = t.nud()
        while rbp < self.node.lbp:
            t = self.node
            self.advance(None, False)
            if self.dbg:
                print("t=" + str(t) + ", left=" + left.type)
            left = t.led(left)
        return left

    #        
    #            var terminal = function (id) {
    #            var s = Symbol(id, 0)
    #            s.nud = function () {
    #                return this
    #            }
    #        }
    #        

    # match infix operators
    # <expression> <operator> <expression>
    # left associative
    # match infix operators
    # <expression> <operator> <expression>
    # right associative
    # match prefix operators
    # <operator> <expression>
    dbg: bool
    source: Optional[str]
    recover: bool
    node: Optional[Symbol]
    lexer: Optional[tokenizer.Tokenizer]
    symbol_table: dict[str, Symbol]
    errors: MutableSequence[Exception]
    ancestor_label: int
    ancestor_index: int
    ancestry: MutableSequence[Symbol]

    def __init__(self):
        self.dbg = False
        self.source = None
        self.recover = False
        self.node = None
        self.lexer = None
        self.symbol_table = {}
        self.errors = []
        self.ancestor_label = 0
        self.ancestor_index = 0
        self.ancestry = []

        self.register(Terminal(self, "(end)"))
        self.register(Terminal(self, "(name)"))
        self.register(Terminal(self, "(literal)"))
        self.register(Terminal(self, "(regex)"))
        self.register(Symbol(self, ":"))
        self.register(Symbol(self, ";"))
        self.register(Symbol(self, ","))
        self.register(Symbol(self, ")"))
        self.register(Symbol(self, "]"))
        self.register(Symbol(self, "}"))
        self.register(Symbol(self, ".."))  # range operator
        self.register(Infix(self, "."))  # map operator
        self.register(Infix(self, "+"))  # numeric addition
        self.register(InfixAndPrefix(self, "-"))  # numeric subtraction
        # unary numeric negation

        self.register(InfixFieldWildcard(self))
        # numeric multiplication
        self.register(Infix(self, "/"))  # numeric division
        self.register(InfixParentOperator(self))
        # numeric modulus
        self.register(Infix(self, "="))  # equality
        self.register(Infix(self, "<"))  # less than
        self.register(Infix(self, ">"))  # greater than
        self.register(Infix(self, "!="))  # not equal to
        self.register(Infix(self, "<="))  # less than or equal
        self.register(Infix(self, ">="))  # greater than or equal
        self.register(Infix(self, "&"))  # string concatenation

        self.register(InfixAnd(self))
        # Boolean AND
        self.register(InfixOr(self))
        # Boolean OR
        self.register(InfixIn(self))
        # is member of array
        # merged Infix: register(new Terminal("and")); // the 'keywords' can also be used as terminals (field names)
        # merged Infix: register(new Terminal("or")); //
        # merged Infix: register(new Terminal("in")); //
        # merged Infix: register(new Prefix("-")); // unary numeric negation
        self.register(Infix(self, "~>"))  # function application

        self.register(InfixRError(self))

        # field wildcard (single level)
        # merged with Infix *
        # register(new Prefix("*") {
        #     @Override Symbol nud() {
        #         type = "wildcard"
        #         return this
        #     }
        # })

        # descendant wildcard (multi-level)

        self.register(PrefixDescendantWildcard(self))

        # parent operator
        # merged with Infix %
        # register(new Prefix("%") {
        #     @Override Symbol nud() {
        #         type = "parent"
        #         return this
        #     }
        # })

        # function invocation
        self.register(InfixFunctionInvocation(self, tokenizer.Tokenizer.operators["("]))

        # array constructor

        # merged: register(new Prefix("[") {        
        self.register(InfixArrayConstructor(self, tokenizer.Tokenizer.operators["["]))

        # order-by
        self.register(InfixOrderBy(self, tokenizer.Tokenizer.operators["^"]))

        self.register(InfixObjectConstructor(self, tokenizer.Tokenizer.operators["{"]))

        # bind variable
        self.register(InfixRBindVariable(self, tokenizer.Tokenizer.operators[":="]))

        # focus variable bind
        self.register(InfixFocusVariableBind(self, tokenizer.Tokenizer.operators["@"]))

        # index (position) variable bind
        self.register(InfixIndexVariableBind(self, tokenizer.Tokenizer.operators["#"]))

        # if/then/else ternary operator ?:
        self.register(InfixTernaryOperator(self, tokenizer.Tokenizer.operators["?"]))

        # coalescing operator ??
        self.register(InfixCoalesce(self, tokenizer.Tokenizer.operators["??"]))

        # elvis/default operator ?:
        self.register(InfixDefault(self, tokenizer.Tokenizer.operators["?:"]))

        # object transformer
        self.register(PrefixObjectTransformer(self))

    # tail call optimization
    # this is invoked by the post parser to analyse lambda functions to see
    # if they make a tail call.  If so, it is replaced by a thunk which will
    # be invoked by the trampoline loop during function application.
    # This enables tail-recursive functions to be written without growing the stack
    def tail_call_optimize(self, expr: Symbol) -> Symbol:
        result = None
        if expr.type == "function" and expr.predicate is None:
            thunk = Symbol(self)
            thunk.type = "lambda"
            thunk.thunk = True
            thunk.arguments = []
            thunk.position = expr.position
            thunk.body = expr
            result = thunk
        elif expr.type == "condition":
            # analyse both branches
            expr.then = self.tail_call_optimize(expr.then)
            if expr._else is not None:
                expr._else = self.tail_call_optimize(expr._else)
            result = expr
        elif expr.type == "block":
            # only the last expression in the block
            length = len(expr.expressions)
            if length > 0:
                if not (isinstance(expr.expressions, list)):
                    expr.expressions = [expr.expressions]
                expr.expressions[length - 1] = self.tail_call_optimize(expr.expressions[length - 1])
            result = expr
        else:
            result = expr
        return result

    def seek_parent(self, node: Symbol, slot: Symbol) -> Symbol:
        if node.type == "name" or node.type == "wildcard":
            slot.level -= 1
            if slot.level == 0:
                if node.ancestor is None:
                    node.ancestor = slot
                else:
                    # reuse the existing label
                    self.ancestry[int(slot.index)].slot.label = node.ancestor.label
                    node.ancestor = slot
                node.tuple = True
        elif node.type == "parent":
            slot.level += 1
        elif node.type == "block":
            # look in last expression in the block
            if node.expressions:
                node.tuple = True
                slot = self.seek_parent(node.expressions[-1], slot)
        elif node.type == "path":
            # last step in path
            node.tuple = True
            index = len(node.steps) - 1
            slot = self.seek_parent(node.steps[index], slot)
            index -= 1
            while slot.level > 0 and index >= 0:
                # check previous steps
                slot = self.seek_parent(node.steps[index], slot)
                index -= 1
        else:
            # error - can't derive ancestor
            raise jexception.JException("S0217", node.position, node.type)
        return slot

    def push_ancestry(self, result: Symbol, value: Optional[Symbol]) -> None:
        if value is None:
            return  # Added NPE check
        if value.seeking_parent is not None or value.type == "parent":
            slots = value.seeking_parent if (value.seeking_parent is not None) else []
            if value.type == "parent":
                slots.append(value.slot)
            if result.seeking_parent is None:
                result.seeking_parent = slots
            else:
                result.seeking_parent.extend(slots)

    def resolve_ancestry(self, path: Symbol) -> None:
        index = len(path.steps) - 1
        laststep = path.steps[index]
        slots = laststep.seeking_parent if (laststep.seeking_parent is not None) else []
        if laststep.type == "parent":
            slots.append(laststep.slot)
        for slot in slots:
            index = len(path.steps) - 2
            while slot.level > 0:
                if index < 0:
                    if path.seeking_parent is None:
                        path.seeking_parent = [slot]
                    else:
                        path.seeking_parent.append(slot)
                    break
                # try previous step
                step = path.steps[index]
                index -= 1
                # multiple contiguous steps that bind the focus should be skipped
                while index >= 0 and step.focus is not None and path.steps[index].focus is not None:
                    step = path.steps[index]
                    index -= 1
                slot = self.seek_parent(step, slot)

    # post-parse stage
    # the purpose of this is to add as much semantic value to the parse tree as possible
    # in order to simplify the work of the evaluator.
    # This includes flattening the parts of the AST representing location paths,
    # converting them to arrays of steps which in turn may contain arrays of predicates.
    # following this, nodes containing '.' and '[' should be eliminated from the AST.
    def process_ast(self, expr: Optional[Symbol]) -> Optional[Symbol]:
        result = expr
        if expr is None:
            return None
        if self.dbg:
            print(" > processAST type=" + expr.type + " value='" + expr.value + "'")
        type = expr.type if expr.type is not None else "(null)"
        if type == "binary":
            value = str(expr.value)
            if value == ".":
                lstep = self.process_ast(expr.lhs)

                if lstep.type == "path":
                    result = lstep
                else:
                    result = Infix(self, None)
                    result.type = "path"
                    result.steps = [lstep]
                    # result = {type: 'path', steps: [lstep]}
                if lstep.type == "parent":
                    result.seeking_parent = [lstep.slot]
                rest = self.process_ast(expr.rhs)
                if (rest.type == "function" and rest.procedure.type == "path" and len(
                        rest.procedure.steps) == 1 and rest.procedure.steps[0].type == "name" and
                        result.steps[-1].type == "function"):
                    # next function in chain of functions - will override a thenable
                    result.steps[-1].next_function = rest.procedure.steps[0].value
                if rest.type == "path":
                    result.steps.extend(rest.steps)
                else:
                    if rest.predicate is not None:
                        rest.stages = rest.predicate
                        rest.predicate = None
                        # delete rest.predicate
                    result.steps.append(rest)
                # any steps within a path that are string literals, should be changed to 'name'
                for step in result.steps:
                    if step.type == "number" or step.type == "value":
                        # don't allow steps to be numbers or the values true/false/null
                        raise jexception.JException("S0213", step.position, step.value)
                    # System.out.println("step "+step+" type="+step.type)
                    if step.type == "string":
                        step.type = "name"
                    # for (var lit : step.steps) {
                    #     System.out.println("step2 "+lit+" type="+lit.type)
                    #     lit.type = "name"
                    # }

                # any step that signals keeping a singleton array, should be flagged on the path
                if [step for step in result.steps if step.keep_array]:
                    result.keep_singleton_array = True
                # if first step is a path constructor, flag it for special handling
                firststep = result.steps[0]
                if firststep.type == "unary" and str(firststep.value) == "[":
                    firststep.consarray = True
                # if the last step is an array constructor, flag it so it doesn't flatten
                laststep = result.steps[-1]
                if laststep.type == "unary" and str(laststep.value) == "[":
                    laststep.consarray = True
                self.resolve_ancestry(result)
            elif value == "[":
                if self.dbg:
                    print("binary [")
                # predicated step
                # LHS is a step or a predicated step
                # RHS is the predicate expr
                result = self.process_ast(expr.lhs)
                step = result
                type = "predicate"
                if result.type == "path":
                    step = result.steps[-1]
                    type = "stages"
                if step.group is not None:
                    raise jexception.JException("S0209", expr.position)
                # if (typeof step[type] === 'undefined') {
                #     step[type] = []
                # }
                if type == "stages":
                    if step.stages is None:
                        step.stages = []
                else:
                    if step.predicate is None:
                        step.predicate = []

                predicate = self.process_ast(expr.rhs)
                if predicate.seeking_parent is not None:
                    for slot in predicate.seeking_parent:
                        if slot.level == 1:
                            self.seek_parent(step, slot)
                        else:
                            slot.level -= 1
                    self.push_ancestry(step, predicate)
                s = Symbol(self)
                s.type = "filter"
                s.expr = predicate
                s.position = expr.position

                # FIXED:
                # this logic is required in Java to fix
                # for example test: flattening case 045
                # otherwise we lose the keepArray flag
                if expr.keep_array:
                    step.keep_array = True

                if type == "stages":
                    step.stages.append(s)
                else:
                    step.predicate.append(s)
                # step[type].push({type: 'filter', expr: predicate, position: expr.position})
            elif value == "{":
                # group-by
                # LHS is a step or a predicated step
                # RHS is the object constructor expr
                result = self.process_ast(expr.lhs)
                if result.group is not None:
                    raise jexception.JException("S0210", expr.position)
                # object constructor - process each pair
                result.group = Symbol(self)
                result.group.lhs_object = [[self.process_ast(pair[0]), self.process_ast(pair[1])]
                                           for pair in expr.rhs_object]
                result.group.position = expr.position

            elif value == "^":
                # order-by
                # LHS is the array to be ordered
                # RHS defines the terms
                result = self.process_ast(expr.lhs)
                if result.type != "path":
                    _res = Symbol(self)
                    _res.type = "path"
                    _res.steps = [result]
                    result = _res
                sort_step = Symbol(self)
                sort_step.type = "sort"
                sort_step.position = expr.position

                def lambda1(terms):
                    expression = self.process_ast(terms.expression)
                    self.push_ancestry(sort_step, expression)
                    res = Symbol(self)
                    res.descending = terms.descending
                    res.expression = expression
                    return res

                sort_step.terms = [lambda1(x) for x in expr.rhs_terms]
                result.steps.append(sort_step)
                self.resolve_ancestry(result)
            elif value == ":=":
                result = Symbol(self)
                result.type = "bind"
                result.value = expr.value
                result.position = expr.position
                result.lhs = self.process_ast(expr.lhs)
                result.rhs = self.process_ast(expr.rhs)
                self.push_ancestry(result, result.rhs)
            elif value == "@":
                result = self.process_ast(expr.lhs)
                step = result
                if result.type == "path":
                    step = result.steps[-1]
                # throw error if there are any predicates defined at this point
                # at this point the only type of stages can be predicates
                if step.stages is not None or step.predicate is not None:
                    raise jexception.JException("S0215", expr.position)
                # also throw if this is applied after an 'order-by' clause
                if step.type == "sort":
                    raise jexception.JException("S0216", expr.position)
                if expr.keep_array:
                    step.keep_array = True
                step.focus = expr.rhs.value
                step.tuple = True
            elif value == "#":
                result = self.process_ast(expr.lhs)
                step = result
                if result.type == "path":
                    step = result.steps[-1]
                else:
                    _res = Symbol(self)
                    _res.type = "path"
                    _res.steps = [result]
                    result = _res
                    if step.predicate is not None:
                        step.stages = step.predicate
                        step.predicate = None
                if step.stages is None:
                    step.index = expr.rhs.value  # name of index variable = String
                else:
                    _res = Symbol(self)
                    _res.type = "index"
                    _res.value = expr.rhs.value
                    _res.position = expr.position
                    step.stages.append(_res)
                step.tuple = True
            elif value == "~>":
                result = Symbol(self)
                result.type = "apply"
                result.value = expr.value
                result.position = expr.position
                result.lhs = self.process_ast(expr.lhs)
                result.rhs = self.process_ast(expr.rhs)
                result.keep_array = result.lhs.keep_array or result.rhs.keep_array
            else:
                result = Infix(self, None)
                result.type = expr.type
                result.value = expr.value
                result.position = expr.position
                result.lhs = self.process_ast(expr.lhs)
                result.rhs = self.process_ast(expr.rhs)
                self.push_ancestry(result, result.lhs)
                self.push_ancestry(result, result.rhs)

        elif type == "unary":
            result = Symbol(self)
            result.type = expr.type
            result.value = expr.value
            result.position = expr.position
            # expr.value might be Character!
            expr_value = str(expr.value)
            if expr_value == "[":
                if self.dbg:
                    print("unary [ " + str(result))

                # array constructor - process each item
                def lambda2(item):
                    value = self.process_ast(item)
                    self.push_ancestry(result, value)
                    return value

                result.expressions = [lambda2(x) for x in expr.expressions]
            elif expr_value == "{":
                # object constructor - process each pair
                # throw new Error("processAST {} unimpl")
                def lambda3(pair):
                    key = self.process_ast(pair[0])
                    self.push_ancestry(result, key)
                    value = self.process_ast(pair[1])
                    self.push_ancestry(result, value)
                    return [key, value]

                result.lhs_object = [lambda3(x) for x in expr.lhs_object]
            else:
                # all other unary expressions - just process the expression
                result.expression = self.process_ast(expr.expression)
                # if unary minus on a number, then pre-process
                if expr_value == "-" and result.expression.type == "number":
                    result = result.expression
                    result.value = utils.Utils.convert_number(-float(result.value))
                    if self.dbg:
                        print("unary - value=" + str(result.value))
                else:
                    self.push_ancestry(result, result.expression)

        elif type == "function" or type == "partial":
            result = Symbol(self)
            result.type = expr.type
            result.name = expr.name
            result.value = expr.value
            result.position = expr.position

            def lambda4(arg):
                arg_ast = self.process_ast(arg)
                self.push_ancestry(result, arg_ast)
                return arg_ast

            result.arguments = [lambda4(x) for x in expr.arguments]
            result.procedure = self.process_ast(expr.procedure)
        elif type == "lambda":
            result = Symbol(self)
            result.type = expr.type
            result.arguments = expr.arguments
            result.signature = expr.signature
            result.position = expr.position
            body = self.process_ast(expr.body)
            result.body = self.tail_call_optimize(body)
        elif type == "condition":
            result = Symbol(self)
            result.type = expr.type
            result.position = expr.position
            result.condition = self.process_ast(expr.condition)
            self.push_ancestry(result, result.condition)
            result.then = self.process_ast(expr.then)
            self.push_ancestry(result, result.then)
            if expr._else is not None:
                result._else = self.process_ast(expr._else)
                self.push_ancestry(result, result._else)
        elif type == "transform":
            result = Symbol(self)
            result.type = expr.type
            result.position = expr.position
            result.pattern = self.process_ast(expr.pattern)
            result.update = self.process_ast(expr.update)
            if expr.delete is not None:
                result.delete = self.process_ast(expr.delete)
        elif type == "block":
            result = Symbol(self)
            result.type = expr.type
            result.position = expr.position

            # array of expressions - process each one
            def lambda5(item):
                part = self.process_ast(item)
                self.push_ancestry(result, part)
                if part.consarray or (part.type == "path" and part.steps[0].consarray):
                    result.consarray = True
                return part

            result.expressions = [lambda5(x) for x in expr.expressions]
            # TODO scan the array of expressions to see if any of them assign variables
            # if so, need to mark the block as one that needs to create a new frame
        elif type == "name":
            result = Symbol(self)
            result.type = "path"
            result.steps = [expr]
            if expr.keep_array:
                result.keep_singleton_array = True
        elif type == "parent":
            result = Symbol(self)
            result.type = "parent"
            result.slot = Symbol(self)
            result.slot.label = "!" + str(self.ancestor_label)
            self.ancestor_label += 1
            result.slot.level = 1
            result.slot.index = self.ancestor_index
            self.ancestor_index += 1
            # slot: { label: '!' + ancestorLabel++, level: 1, index: ancestorIndex++ } }
            self.ancestry.append(result)
        elif (type == "string" or type == "number" or type == "value" or type == "wildcard" or type == "descendant" or
              type == "variable" or type == "regex"):
            result = expr
        elif type == "operator":
            # the tokens 'and' and 'or' might have been used as a name rather than an operator
            if expr.value == "and" or expr.value == "or" or expr.value == "in":
                expr.type = "name"
                result = self.process_ast(expr)
            elif str(expr.value) == "?":
                # partial application
                result = expr
            else:
                raise jexception.JException("S0201", expr.position, expr.value)
        elif type == "error":
            result = expr
            if expr.lhs is not None:
                result = self.process_ast(expr.lhs)
        else:
            code = "S0206"
            # istanbul ignore else
            if expr.id == "(end)":
                code = "S0207"
            err = jexception.JException(code, expr.position, expr.value)
            if self.recover:
                self.errors.append(err)
                ret = Symbol(self)
                ret.type = "error"
                ret.error = err
                return ret
            else:
                # err.stack = (new Error()).stack
                raise err
        if expr.keep_array:
            result.keep_array = True
        return result

    def object_parser(self, left: Optional[Symbol]) -> Symbol:

        res = Infix(self, "{") if left is not None else Prefix(self, "{")

        a = []
        if self.node.id != "}":
            while True:
                n = self.expression(0)
                self.advance(":")
                v = self.expression(0)
                pair = [n, v]
                a.append(pair)  # holds an array of name/value expression pairs
                if self.node.id != ",":
                    break
                self.advance(",")
        self.advance("}", True)
        if left is None:
            # NUD - unary prefix form
            res.lhs_object = a
            res.type = "unary"
        else:
            # LED - binary infix form
            res.lhs = left
            res.rhs_object = a
            res.type = "binary"
        return res

    def parse(self, jsonata: Optional[str]) -> Symbol:
        self.source = jsonata

        # now invoke the tokenizer and the parser and return the syntax tree
        self.lexer = tokenizer.Tokenizer(self.source)
        self.advance()
        # parse the tokens
        expr = self.expression(0)
        if self.node.id != "(end)":
            err = jexception.JException("S0201", self.node.position, self.node.value)
            self.handle_error(err)

        expr = self.process_ast(expr)

        if expr.type == "parent" or expr.seeking_parent is not None:
            # error - trying to derive ancestor at top level
            raise jexception.JException("S0217", expr.position, expr.type)

        if self.errors:
            expr.errors = self.errors

        return expr
