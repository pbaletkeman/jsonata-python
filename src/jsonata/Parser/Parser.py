#
"""
Parser module for JSONata Python implementation.
Handles parsing of JSONata expressions, including infix, prefix, and function operators.
Adapted from jsonata-java and IBM JSONata projects, supporting advanced query and transformation syntax.
"""
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

import copy
from src.jsonata.Parser.Prefix import Prefix
from src.jsonata.Parser.InfixAndPrefix import InfixAndPrefix
from src.jsonata.Parser.InfixAnd import InfixAnd
from src.jsonata.Parser.InfixOr import InfixOr
from src.jsonata.Parser.InfixIn import InfixIn
from src.jsonata.Parser.InfixParentOperator import InfixParentOperator
from src.jsonata.Parser.InfixFieldWildcard import InfixFieldWildcard
from src.jsonata.Parser.InfixRError import InfixRError
from src.jsonata.Parser.PrefixDescendantWildcard import PrefixDescendantWildcard
from src.jsonata.Parser.InfixFunctionInvocation import InfixFunctionInvocation
from src.jsonata.Parser.InfixArrayConstructor import InfixArrayConstructor
from src.jsonata.Parser.InfixOrderBy import InfixOrderBy
from src.jsonata.Parser.InfixObjectConstructor import InfixObjectConstructor
from src.jsonata.Parser.InfixRBindVariable import InfixRBindVariable
from src.jsonata.Parser.InfixFocusVariableBind import InfixFocusVariableBind
from src.jsonata.Parser.InfixIndexVariableBind import InfixIndexVariableBind
from src.jsonata.Parser.InfixTernaryOperator import InfixTernaryOperator
from src.jsonata.Parser.InfixCoalesce import InfixCoalesce
from src.jsonata.Parser.InfixDefault import InfixDefault
from src.jsonata.Parser.PrefixObjectTransformer import PrefixObjectTransformer

from src.jsonata.Parser.Infix import Infix
from src.jsonata.Parser.Terminal import Terminal
from src.jsonata.Tokenizer.Token import Token
from typing import Any, MutableSequence, Optional, Sequence

from src.jsonata.JException.JException import JException
from src.jsonata.Tokenizer.Tokenizer import Tokenizer
from src.jsonata.Utils.Utils import Utils
from src.jsonata.Parser.Symbol import Symbol
from src.jsonata.Signature.Signature import Signature


# var parseSignature = require('./signature')
class Parser:
    """
    Implements the top-down operator precedence parser for Jsonata expressions.
    Based on Pratt's algorithm and inspired by JavaScript and Java implementations.
    Handles tokenization, symbol registration, parsing, error recovery, AST processing, and tail call optimization.
    """

    # This parser implements the 'Top down operator precedence' algorithm developed by Vaughan R Pratt; http://dl.acm.org/citation.cfm?id=512931.
    # and builds on the Javascript framework described by Douglas Crockford at http://javascript.crockford.com/tdop/tdop.html
    # and in 'Beautiful Code', edited by Andy Oram and Greg Wilson, Copyright 2007 O'Reilly Media, Inc. 798-0-596-51004-6

    # var parser = function (source, recover) {

    def remaining_tokens(self) -> list[Token]:
        """
        Get the list of remaining tokens from the lexer.
        Returns:
            List of Token objects.
        """
        remaining = []
        if self.node.id != "(end)":
            t = Token(self.node.type, self.node.value, self.node.position)
            remaining.append(t)
        nxt = self.lexer.next(False)
        while nxt is not None:
            remaining.append(nxt)
            nxt = self.lexer.next(False)
        return remaining

    def register(self, t: Symbol) -> None:
        """
        Register a symbol in the parser's symbol table.
        Args:
            t: The Symbol to register.
        """
        s = self.symbol_table.get(t.id)
        if s is not None:
            if self.dbg:
                print(
                    "Symbol in table "
                    + t.id
                    + " "
                    + str(type(s))
                    + " -> "
                    + str(type(t))
                )
            if t.bp >= s.lbp:
                if self.dbg:
                    print(
                        "Symbol in table "
                        + t.id
                        + " lbp="
                        + str(s.lbp)
                        + " -> "
                        + str(t.bp)
                    )
                s.lbp = t.bp
        else:
            s = t.create()
            s.value = s.id = t.id
            s.lbp = t.bp
            self.symbol_table[t.id] = s

    def handle_error(self, err: JException) -> Symbol:
        """
        Handle a parsing error, optionally recovering.
        Args:
            err: The JException to handle.
        Returns:
            A Symbol error node if recoverable, else raises the exception.
        """
        if self.recover:
            err.remaining = self.remaining_tokens()
            self.errors.append(err)
            node = Parser.Symbol(self)
            return node
        else:
            raise err

    # }

    def advance(self, id: Optional[str] = None, infix: bool = False) -> Symbol:
        """
        Advance the parser to the next token, optionally checking for a specific id.
        Args:
            id: The expected token id.
            infix: Whether to treat as infix.
        Returns:
            The next Symbol node.
        """
        if id is not None and self.node.id != id:
            code = None
            if self.node.id == "(end)":
                code = "S0203"
            else:
                code = "S0202"
            err = JException(code, self.node.position, id, self.node.value)
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
                return self.handle_error(
                    JException("S0204", next_token.position, value)
                )
        elif type == "string" or type == "number" or type == "value":
            symbol = self.symbol_table["(literal)"]
        elif type == "regex":
            type = "regex"
            symbol = self.symbol_table["(regex)"]
        else:
            return self.handle_error(JException("S0205", next_token.position, value))

        self.node = symbol.create()
        self.node.value = value
        self.node.type = type
        self.node.position = next_token.position
        if self.dbg:
            print("advance " + str(self.node))
        return self.node

    # Pratt's algorithm
    def expression(self, rbp: int) -> Symbol:
        """
        Parse an expression using Pratt's algorithm.
        Args:
            rbp: The right binding power.
        Returns:
            The parsed Symbol node.
        """
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
    #            var s = Parser.Symbol(id, 0)
    #            s.nud = function () {
    #                return this
    #            }
    #        }
    #

    dbg: bool
    source: Optional[str]
    recover: bool
    node: Optional[Symbol]
    lexer: Optional[Tokenizer]
    symbol_table: dict[str, Symbol]
    errors: MutableSequence[Exception]
    ancestor_label: int
    ancestor_index: int
    ancestry: MutableSequence[Symbol]

    def __init__(self):
        """
        Initialize a Parser object and register terminal symbols.
        """
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
        self.register(InfixFunctionInvocation(self, Tokenizer.operators["("]))

        # array constructor

        # merged: register(new Prefix("[") {
        self.register(InfixArrayConstructor(self, Tokenizer.operators["["]))

        # order-by
        self.register(InfixOrderBy(self, Tokenizer.operators["^"]))

        self.register(InfixObjectConstructor(self, Tokenizer.operators["{"]))

        # bind variable
        self.register(InfixRBindVariable(self, Tokenizer.operators[":="]))

        # focus variable bind
        self.register(InfixFocusVariableBind(self, Tokenizer.operators["@"]))

        # index (position) variable bind
        self.register(InfixIndexVariableBind(self, Tokenizer.operators["#"]))

        # if/then/else ternary operator ?:
        self.register(InfixTernaryOperator(self, Tokenizer.operators["?"]))

        # coalescing operator ??
        self.register(InfixCoalesce(self, Tokenizer.operators["??"]))

        # elvis/default operator ?:
        self.register(InfixDefault(self, Tokenizer.operators["?:"]))

        # object transformer
        self.register(PrefixObjectTransformer(self))

    # tail call optimization
    # this is invoked by the post parser to analyse lambda functions to see
    # if they make a tail call.  If so, it is replaced by a thunk which will
    # be invoked by the trampoline loop during function application.
    # This enables tail-recursive functions to be written without growing the stack
    def tail_call_optimize(self, expr: Symbol) -> Symbol:
        """
        Optimize tail-recursive lambda functions in the AST to prevent stack overflow.
        Replaces tail calls with thunks for trampoline execution.
        Args:
            expr: The Symbol node representing the expression.
        Returns:
            Symbol: The optimized Symbol node.
        """
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
                if not isinstance(expr.expressions, list):
                    expr.expressions = [expr.expressions]
                expr.expressions[length - 1] = self.tail_call_optimize(
                    expr.expressions[length - 1]
                )
            result = expr
        else:
            result = expr
        return result

    def seek_parent(self, node: Symbol, slot: Symbol) -> Symbol:
        """
        Seek and assign the parent slot for a given node in the AST.
        Used for resolving ancestry in path and block expressions.
        Args:
            node: The Symbol node to resolve parent for.
            slot: The Symbol slot representing the parent.
        Returns:
            Symbol: The updated slot after seeking parent.
        """
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
            raise JException("S0217", node.position, node.type)
        return slot

    def push_ancestry(self, result: Symbol, value: Optional[Symbol]) -> None:
        """
        Push ancestry slots from a value node to a result node in the AST.
        Used for tracking parent relationships in complex expressions.
        Args:
            result: The Symbol node to update ancestry for.
            value: The Symbol node providing ancestry slots.
        """
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
        """
        Resolve ancestry slots for a path expression in the AST.
        Ensures correct parent relationships for all steps in the path.
        Args:
            path: The Symbol node representing the path expression.
        """
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
                while (
                    index >= 0
                    and step.focus is not None
                    and path.steps[index].focus is not None
                ):
                    step = path.steps[index]
                    index -= 1
                slot = self.seek_parent(step, slot)

    def process_ast(self, expr: Optional[Symbol]) -> Optional[Symbol]:
        """
        Post-process the parsed Abstract Syntax Tree (AST) to enrich it with semantic information for evaluation.
        This method flattens location path nodes, converts them to arrays of steps and predicates, and eliminates unnecessary nodes.
        It also flags singleton arrays, resolves ancestry relationships, and transforms various expression types for easier evaluation.
        Args:
            expr: The root Symbol node of the parsed AST.
        Returns:
            The processed Symbol node with enhanced semantic structure, or None if input is None.
        Raises:
            JException: For invalid or unsupported AST structures.
        """
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
                    result = Parser.Infix(self, None)
                    result.type = "path"
                    result.steps = [lstep]
                    # result = {type: 'path', steps: [lstep]}
                if lstep.type == "parent":
                    result.seeking_parent = [lstep.slot]
                rest = self.process_ast(expr.rhs)
                if (
                    rest.type == "function"
                    and rest.procedure.type == "path"
                    and len(rest.procedure.steps) == 1
                    and rest.procedure.steps[0].type == "name"
                    and result.steps[-1].type == "function"
                ):
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
                        raise JException("S0213", step.position, step.value)
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
                    raise JException("S0209", expr.position)
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
                s = Parser.Symbol(self)
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
                    raise JException("S0210", expr.position)
                # object constructor - process each pair
                result.group = Parser.Symbol(self)
                result.group.lhs_object = [
                    [self.process_ast(pair[0]), self.process_ast(pair[1])]
                    for pair in expr.rhs_object
                ]
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
                sort_step = Parser.Symbol(self)
                sort_step.type = "sort"
                sort_step.position = expr.position

                def lambda1(terms):
                    # Processes a sort term for order-by expressions
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
                    raise JException("S0215", expr.position)
                # also throw if this is applied after an 'order-by' clause
                if step.type == "sort":
                    raise JException("S0216", expr.position)
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
                    _res = Parser.Symbol(self)
                    _res.type = "path"
                    _res.steps = [result]
                    result = _res
                    if step.predicate is not None:
                        step.stages = step.predicate
                        step.predicate = None
                if step.stages is None:
                    step.index = expr.rhs.value  # name of index variable = String
                else:
                    _res = Parser.Symbol(self)
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
                    # Processes an item for array constructor expressions
                    value = self.process_ast(item)
                    self.push_ancestry(result, value)
                    return value

                result.expressions = [lambda2(x) for x in expr.expressions]
            elif expr_value == "{":
                # object constructor - process each pair
                # throw new Error("processAST {} unimpl")
                def lambda3(pair):
                    # Processes a key-value pair for object constructor expressions
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
                    result.value = Utils.convert_number(-float(result.value))
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
                # Processes an argument for function and partial expressions
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
                # Processes an item for block expressions, tracking consarray flag
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
        elif (
            type == "string"
            or type == "number"
            or type == "value"
            or type == "wildcard"
            or type == "descendant"
            or type == "variable"
            or type == "regex"
        ):
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
                raise JException("S0201", expr.position, expr.value)
        elif type == "error":
            result = expr
            if expr.lhs is not None:
                result = self.process_ast(expr.lhs)
        else:
            code = "S0206"
            # istanbul ignore else
            if expr.id == "(end)":
                code = "S0207"
            err = JException(code, expr.position, expr.value)
            if self.recover:
                self.errors.append(err)
                ret = Parser.Symbol(self)
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
        """
        Parse an object constructor expression, handling both prefix (unary) and infix (binary) forms.
        This method builds an array of name/value pairs for the object, advancing through tokens and handling commas and colons.
        Args:
            left: The left Symbol node if parsing in infix (binary) form, or None for prefix (unary) form.
        Returns:
            Symbol: The constructed object Symbol node, with appropriate type and child objects.
        """
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
        """
        Parse a JSONata expression string and return the processed Abstract Syntax Tree (AST).
        This method tokenizes the input, advances through tokens, builds the syntax tree, and post-processes the AST for semantic enrichment.
        It also handles errors and validates top-level ancestry constraints.
        Args:
            jsonata: The JSONata expression string to parse.
        Returns:
            Symbol: The root node of the processed AST.
        Raises:
            JException: For syntax errors or invalid top-level ancestry.
        """
        self.source = jsonata

        # now invoke the tokenizer and the parser and return the syntax tree
        self.lexer = Tokenizer(self.source)
        self.advance()
        # parse the tokens
        expr = self.expression(0)
        if self.node.id != "(end)":
            err = JException("S0201", self.node.position, self.node.value)
            self.handle_error(err)

        expr = self.process_ast(expr)

        if expr.type == "parent" or expr.seeking_parent is not None:
            # error - trying to derive ancestor at top level
            raise JException("S0217", expr.position, expr.type)

        if self.errors:
            expr.errors = self.errors

        return expr
