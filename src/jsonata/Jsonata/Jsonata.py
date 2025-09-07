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
# © Copyright IBM Corp. 2016, 2017 All Rights Reserved
#   This project is licensed under the MIT License, see LICENSE
#

import copy
import inspect
import math
import re
import threading
import sys

from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    MutableSequence,
    Optional,
    Sequence,
    Mapping,
)
from src.jsonata.Jsonata.GroupEntry import GroupEntry
from src.jsonata.Jsonata.Transformer import Transformer
from src.jsonata.Jsonata.JNativeFunction import JNativeFunction
from src.jsonata.Parser.Symbol import Symbol
from src.jsonata.JException.JException import JException
from src.jsonata.Timebox.Timebox import Timebox
from src.jsonata.Utils.Utils import Utils, JList
from src.jsonata.Utils.RangeList import RangeList
from src.jsonata.Functions.Functions import Functions
from src.jsonata.Jsonata.Frame import Frame
from src.jsonata.Jsonata.JFunction import JFunction
from src.jsonata.Parser.Parser import Parser
from src.jsonata.Signature.Signature import Signature as sig


#
# @module JSONata
# @description JSON query and transformation language
#
class Jsonata:
    """
    Main class for the Jsonata Python implementation. Provides methods for evaluating
    and transforming JSONata expressions against input data, supporting query, transformation,
    and advanced features like grouping, sorting, and filtering.
    """

    static_frame = None  # = createFrame(null);

    def __init__(self, parser=None):
        # Ensure parser is always available
        from src.jsonata.Parser.Parser import Parser

        self.parser = parser if parser is not None else Parser()

    #
    # JFunction callable Lambda interface
    #

    #
    # JFunction definition class
    #
    def eval(
        self,
        expr: Optional[Symbol],
        input_item: Optional[Any],
        environment: Optional[Frame],
    ) -> Optional[Any]:
        """
        Evaluate expression against input_item data
        @param expr: JSONata expression
        @param input_item: input_item data to evaluate against
        @param environment: Environment
        @returns: Evaluated input_item data
        """
        # Thread safety:
        # Make sure each evaluate is executed on an instance per thread
        return self.get_per_thread_instance()._eval(expr, input_item, environment)

    def _eval(
        self,
        expr: Optional[Symbol],
        input_item: Optional[Any],
        environment: Optional[Frame],
    ) -> Optional[Any]:
        """
        Internal evaluation of a JSONata expression against input data and environment.
        Args:
            expr: JSONata expression symbol.
            input_item: Input data to evaluate against.
            environment: Environment frame.
        Returns:
            The result of the evaluation.
        """
        result = None

        # Store the current input_item
        # This is required by Functions.functionEval for current $eval() input_item context
        self.input_item = input_item

        if self.parser.dbg:
            print(
                "eval expr=" + str(expr) + " type=" + expr.type
            )  # +" input_item="+input_item);

        entry_callback = environment.lookup("__evaluate_entry")
        if entry_callback is not None:
            entry_callback(expr, input_item, environment)

        if getattr(expr, "type", None) is not None:
            if expr.type == "path":
                result = self.evaluate_path(expr, input_item, environment)
            elif expr.type == "binary":
                result = self.evaluate_binary(expr, input_item, environment)
            elif expr.type == "unary":
                result = self.evaluate_unary(expr, input_item, environment)
            elif expr.type == "name":
                result = self.evaluate_name(expr, input_item, environment)
                if self.parser.dbg:
                    print("evalName " + result)
            elif expr.type == "string" or expr.type == "number" or expr.type == "value":
                result = self.evaluate_literal(expr)  # , input_item, environment);
            elif expr.type == "wildcard":
                result = self.evaluate_wildcard(expr, input_item)  # , environment);
            elif expr.type == "descendant":
                result = self.evaluate_descendants(expr, input_item)  # , environment);
            elif expr.type == "parent":
                result = environment.lookup(expr.slot.label)
            elif expr.type == "condition":
                result = self.evaluate_condition(expr, input_item, environment)
            elif expr.type == "block":
                result = self.evaluate_block(expr, input_item, environment)
            elif expr.type == "bind":
                result = self.evaluate_bind_expression(expr, input_item, environment)
            elif expr.type == "regex":
                result = self.evaluate_regex(expr)  # , input_item, environment);
            elif expr.type == "function":
                result = self.evaluate_function(
                    expr, input_item, environment, Utils.NONE
                )
            elif expr.type == "variable":
                result = self.evaluate_variable(expr, input_item, environment)
            elif expr.type == "lambda":
                result = self.evaluate_lambda(expr, input_item, environment)
            elif expr.type == "partial":
                result = self.evaluate_partial_application(
                    expr, input_item, environment
                )
            elif expr.type == "apply":
                result = self.evaluate_apply_expression(expr, input_item, environment)
            elif expr.type == "transform":
                result = self.evaluate_transform_expression(
                    expr, input_item, environment
                )

        if getattr(expr, "predicate", None) is not None:
            for item in expr.predicate:
                result = self.evaluate_filter(item.expr, result, environment)

        if (
            getattr(expr, "type", None) is not None
            and expr.type != "path"
            and getattr(expr, "group", None) is not None
        ):
            result = self.evaluate_group_expression(expr.group, result, environment)

        exit_callback = environment.lookup("__evaluate_exit")
        if exit_callback is not None:
            exit_callback(expr, input_item, environment, result)

        # mangle result (list of 1 element -> 1 element, empty list -> null)
        if result is not None and Utils.is_sequence(result) and not result.tuple_stream:
            if expr.keep_array:
                result.keep_singleton = True
            if not result:
                result = None
            elif len(result) == 1:
                result = result if result.keep_singleton else result[0]

        return result

    #
    def evaluate_path(
        self,
        expr: Optional[Symbol],
        input_item: Optional[Any],
        environment: Optional[Frame],
    ) -> Optional[Any]:
        """
        Evaluate path expression against input_item data
        @param expr: JSONata expression
        @param input_item: input_item data to evaluate against
        @param environment: Environment
        @returns: Evaluated input_item data
        """
        input_sequence = None
        # expr is an array of steps
        # if the first step is a variable reference ($...), including root reference ($$),
        #   then the path is absolute rather than relative
        if isinstance(input_item, list) and expr.steps[0].type != "variable":
            input_sequence = input_item
        else:
            # if input_item is not an array, make it so
            input_sequence = Utils.create_sequence(input_item)

        result_sequence = None
        is_tuple_stream = False
        tuple_bindings = None

        # evaluate each step in turn
        for ii, step in enumerate(expr.steps):

            if step.tuple is not None:
                is_tuple_stream = True

            # if the first step is an explicit array constructor, then just evaluate that (i.e. don"t iterate over a context array)
            if ii == 0 and step.consarray:
                result_sequence = self.eval(step, input_sequence, environment)
            else:
                if is_tuple_stream:
                    tuple_bindings = self.evaluate_tuple_step(
                        step, input_sequence, tuple_bindings, environment
                    )
                else:
                    result_sequence = self.evaluate_step(
                        step, input_sequence, environment, ii == len(expr.steps) - 1
                    )

            if not is_tuple_stream and (result_sequence is None or not result_sequence):
                break

            if step.focus is None:
                input_sequence = result_sequence

        if is_tuple_stream:
            if expr.tuple is not None:
                # tuple stream is carrying ancestry information - keep this
                result_sequence = tuple_bindings
            else:
                result_sequence = Utils.create_sequence_from_iter(
                    b["@"] for b in tuple_bindings
                )

        if expr.keep_singleton_array:

            # If we only got an ArrayList, convert it so we can set the keepSingleton flag
            if not (isinstance(result_sequence, JList)):
                result_sequence = JList(result_sequence)

            # if the array is explicitly constructed in the expression and marked to promote singleton sequences to array
            if (
                (isinstance(result_sequence, JList))
                and result_sequence.cons
                and not result_sequence.sequence
            ):
                result_sequence = Utils.create_sequence(result_sequence)
            result_sequence.keep_singleton = True

        if expr.group is not None:
            result_sequence = self.evaluate_group_expression(
                expr.group,
                tuple_bindings if is_tuple_stream else result_sequence,
                environment,
            )

        return result_sequence

    def create_frame_from_tuple(
        self, environment: Optional[Frame], tuple_data: Optional[Mapping[str, Any]]
    ) -> Frame:
        """
        Create a new frame and bind tuple data to it.
        Args:
            environment: The enclosing environment frame.
            tuple_data: Dictionary of properties to bind.
        Returns:
            Frame: The new frame with bindings.
        """
        frame = self.create_frame(environment)
        if tuple_data is not None:
            for prop, val in tuple_data.items():
                frame.bind(prop, val)
        return frame

    def evaluate_step(
        self,
        expr: Symbol,
        input_item: Optional[Any],
        environment: Optional[Frame],
        last_step: bool,
    ) -> Optional[Any]:
        """
        Evaluate a step within a path
        @param expr: JSONata expression
        @param input_item: Input data to evaluate against
        @param environment: Environment
        @param last_step: flag the last step in a path
        @returns: Evaluated input data
        """
        if expr.type == "sort":
            result = self.evaluate_sort_expression(expr, input_item, environment)
            if expr.stages is not None:
                result = self.evaluate_stages(expr.stages, result, environment)
            return result

        result = Utils.create_sequence()

        for inp in input_item:
            res = self.eval(expr, inp, environment)
            if expr.stages is not None:
                for stage in expr.stages:
                    res = self.evaluate_filter(stage.expr, res, environment)
            if res is not None:
                result.append(res)

        result_sequence = Utils.create_sequence()
        if (
            last_step
            and len(result) == 1
            and (isinstance(result[0], list))
            and not Utils.is_sequence(result[0])
        ):
            result_sequence = result[0]
        else:
            # flatten the sequence
            for res in result:
                if not (isinstance(res, list)) or (isinstance(res, JList) and res.cons):
                    # it's not an array - just push into the result sequence
                    result_sequence.append(res)
                else:
                    # res is a sequence - flatten it into the parent sequence
                    result_sequence.extend(res)

        return result_sequence

    # async
    def evaluate_stages(
        self,
        stages: Optional[Sequence[Symbol]],
        input: Any,
        environment: Optional[Frame],
    ) -> Any:
        result = input
        for stage in stages:
            if stage.type == "filter":
                result = self.evaluate_filter(stage.expr, result, environment)
            elif stage.type == "index":
                for ee, tuple in enumerate(result):
                    tuple[str(stage.value)] = ee
        return result

    def evaluate_tuple_step(
        self,
        expr: Symbol,
        input_item: Optional[Sequence],
        tuple_bindings: Optional[Sequence[Mapping[str, Any]]],
        environment: Optional[Frame],
    ) -> Optional[Any]:
        """
        Evaluate a step within a path (tuple stream)
        @param expr: JSONata expression
        @param input_item: Input data to evaluate against
        @param tuple_bindings: The tuple stream
        @param environment: Environment
        @returns: Evaluated input data
        """
        result = None
        if expr.type == "sort":
            if tuple_bindings is not None:
                result = self.evaluate_sort_expression(
                    expr, tuple_bindings, environment
                )
            else:
                sorted = self.evaluate_sort_expression(expr, input_item, environment)
                result = Utils.create_sequence_from_iter(
                    {"@": item, expr.index: ss} for ss, item in enumerate(sorted)
                )
                result.tuple_stream = True
            if expr.stages is not None:
                result = self.evaluate_stages(expr.stages, result, environment)
            return result

        result = Utils.create_sequence()
        result.tuple_stream = True
        step_env = environment
        if tuple_bindings is None:
            tuple_bindings = [{"@": item} for item in input_item if item is not None]

        for tuple_binding in tuple_bindings:
            step_env = self.create_frame_from_tuple(environment, tuple_binding)
            res = self.eval(expr, tuple_binding["@"], step_env)
            # res is the binding sequence for the output tuple stream
            if res is not None:
                if not (isinstance(res, list)):
                    res = [res]
                for bb, item in enumerate(res):
                    tuple = dict(tuple_binding)
                    # Object.assign(tuple, tupleBindings[ee])
                    if (isinstance(res, JList)) and res.tuple_stream:
                        tuple.update(item)
                    else:
                        if expr.focus is not None:
                            tuple[expr.focus] = item
                            tuple["@"] = tuple_binding["@"]
                        else:
                            tuple["@"] = item
                        if expr.index is not None:
                            tuple[expr.index] = bb
                        if expr.ancestor is not None:
                            tuple[expr.ancestor.label] = tuple_binding["@"]
                    result.append(tuple)

        if expr.stages is not None:
            result = self.evaluate_stages(expr.stages, result, environment)

        return result

    def evaluate_filter(
        self,
        predicate: Optional[Any],
        input_item: Optional[Any],
        environment: Optional[Frame],
    ) -> Any:
        """
        Apply filter predicate to input data
        @param predicate: filter expression
        @param input_item: Input data to apply predicates against
        @param environment: Environment
        @returns: Result after applying predicates
        """
        results = Utils.create_sequence()
        if isinstance(input_item, JList) and input_item.tuple_stream:
            results.tuple_stream = True
        if not (isinstance(input_item, list)):
            input_item = Utils.create_sequence(input_item)
        if predicate.type == "number":
            index = int(predicate.value)  # round it down - was Math.floor
            if index < 0:
                # count in from end of array
                index = len(input_item) + index
            item = input_item[index] if index < len(input_item) else None
            if item is not None:
                if isinstance(item, list):
                    results = item
                else:
                    results.append(item)
        else:
            for index, item in enumerate(input_item):
                context = item
                env = environment
                if isinstance(input_item, JList) and input_item.tuple_stream:
                    context = item["@"]
                    env = self.create_frame_from_tuple(environment, item)
                res = self.eval(predicate, context, env)
                if Utils.is_numeric(res):
                    res = Utils.create_sequence(res)
                if Utils.is_array_of_numbers(res):
                    for ires in res:
                        # round it down
                        ii = int(ires)  # Math.floor(ires);
                        if ii < 0:
                            # count in from end of array
                            ii = len(input_item) + ii
                        if ii == index:
                            results.append(item)
                elif Jsonata.boolize(res):
                    results.append(item)
        return results

    #
    # Evaluate binary expression against input data
    # @param {Object} expr - JSONata expression
    # @param {Object} input - Input data to evaluate against
    # @param {Object} environment - Environment
    # @returns {*} Evaluated input data
    #
    # async
    def evaluate_binary(
        self,
        expr: Optional[Symbol],
        input_item: Optional[Any],
        environment: Optional[Frame],
    ) -> Optional[Any]:
        """
        Evaluate a binary expression (arithmetic, logical, comparison, or inclusion) against input data.
        Args:
            expr: JSONata binary expression symbol.
            input_item: Input data to evaluate against.
            environment: Environment frame.
        Returns:
            The result of the binary operation, or raises JException for errors.
        """
        lhs = self.eval(expr.lhs, input_item, environment)
        op = str(expr.value)

        if op == "and" or op == "or":

            # defer evaluation of RHS to allow short-circuiting
            evalrhs = lambda: self.eval(expr.rhs, input_item, environment)
            try:
                return self.evaluate_boolean_expression(lhs, evalrhs, op)
            except Exception as err:
                if not (isinstance(err, JException)):
                    raise JException("Unexpected", expr.position)
                # err.position = expr.position
                # err.token = op
                raise err

        rhs = self.eval(expr.rhs, input_item, environment)  # evalrhs();
        try:
            if op == "+" or op == "-" or op == "*" or op == "/" or op == "%":
                result = self.evaluate_numeric_expression(lhs, rhs, op)
            elif op == "=" or op == "!=":
                result = self.evaluate_equality_expression(lhs, rhs, op)
            elif op == "<" or op == "<=" or op == ">" or op == ">=":
                result = self.evaluate_comparison_expression(lhs, rhs, op)
            elif op == "&":
                result = self.evaluate_string_concat(lhs, rhs)
            elif op == "..":
                result = self.evaluate_range_expression(lhs, rhs)
            elif op == "in":
                result = self.evaluate_includes_expression(lhs, rhs)
            else:
                raise JException("Unexpected operator " + op, expr.position)
        except Exception as err:
            # err.position = expr.position
            # err.token = op
            raise err
        return result

    #
    # Evaluate unary expression against input data
    # @param {Object} expr - JSONata expression
    # @param {Object} input - Input data to evaluate against
    # @param {Object} environment - Environment
    # @returns {*} Evaluated input data
    #
    # async
    def evaluate_unary(
        self,
        expr: Optional[Symbol],
        input_item: Optional[Any],
        environment: Optional[Frame],
    ) -> Optional[Any]:
        result = None

        value = str(expr.value)

        def evaluate_unary(
            self,
            expr: Optional[Symbol],
            input_item: Optional[Any],
            environment: Optional[Frame],
        ) -> Optional[Any]:
            """
            Evaluate a unary expression (negation, array constructor, or object constructor) against input data.
            Args:
                expr: JSONata unary expression symbol.
                input_item: Input data to evaluate against.
                environment: Environment frame.
            Returns:
                The result of the unary operation, such as negated value, constructed array, or grouped object.
            Raises:
                JException: If the operation is invalid or input is not numeric for negation.
            """
            result = None

            value = str(expr.value)
            if value == "-":
                result = self.eval(expr.expression, input_item, environment)
                if result is None:
                    result = None
                elif Utils.is_numeric(result):
                    result = Utils.convert_number(-float(result))
                else:
                    raise JException("D1002", expr.position, expr.value, result)
            elif value == "[":
                # array constructor - evaluate each item
                result = Utils.JList()  # [];
                idx = 0
                for item in expr.expressions:
                    environment.is_parallel_call = idx > 0
                    value = self.eval(item, input_item, environment)
                    if value is not None:
                        if str(item.value) == "[":
                            result.append(value)
                        else:
                            result = Functions.append(result, value)
                    idx += 1
                if expr.consarray:
                    if not (isinstance(result, Utils.JList)):
                        result = Utils.JList(result)
                    # System.out.println("const "+result)
                    result.cons = True
            elif value == "{":
                # object constructor - apply grouping
                result = self.evaluate_group_expression(expr, input_item, environment)

            return result

    def evaluate_name(
        self,
        expr: Optional[Symbol],
        input_item: Optional[Any],
        environment: Optional[Frame],
    ) -> Optional[Any]:
        """
        Evaluate a name expression by looking up the named item in the input_item.
        Args:
            expr: JSONata expression representing the name.
            input_item: Input data to evaluate against.
            environment: Environment frame.
        Returns:
            The value associated with the name in input_item.
        """
        return Functions.lookup(input_item, str(expr.value))

    #
    # Evaluate literal against input data
    # @param {Object} expr - JSONata expression
    # @returns {*} Evaluated input data
    #
    def evaluate_literal(self, expr: Optional[Symbol]) -> Optional[Any]:
        return expr.value if expr.value is not None else Utils.NULL_VALUE

    #
    # Evaluate wildcard against input_item data
    # @param {Object} expr - JSONata expression
    # @param {Object} input - Input data to evaluate against
    # @returns {*} Evaluated input data
    #
    def evaluate_wildcard(
        self, expr: Optional[Symbol], input_item: Optional[Any]
    ) -> Optional[Any]:
        """
        Evaluate wildcard expression against input_item data.
        Args:
            expr: JSONata expression representing the wildcard.
            input_item: Input data to evaluate against.
        Returns:
            Sequence of values matching the wildcard expression.
        """
        results = Utils.create_sequence()
        if (isinstance(input_item, JList)) and input_item.outer_wrapper and input_item:
            input_item = input_item[0]
        if input_item is not None and isinstance(input_item, dict):
            for value in input_item.values():
                if isinstance(value, list):
                    value = self.flatten(value, None)
                    results = Functions.append(results, value)
                else:
                    results.append(value)
        elif isinstance(input_item, list):
            # Java: need to handle List separately
            for value in input_item:
                if isinstance(value, list):
                    value = self.flatten(value, None)
                    results = Functions.append(results, value)
                elif isinstance(value, dict):
                    # Call recursively do decompose the map
                    results.extend(self.evaluate_wildcard(expr, value))
                else:
                    results.append(value)

        # result = normalizeSequence(results)
        return results

    #
    # Returns a flattened array
    # @param {Array} arg - the array to be flatten
    # @param {Array} flattened - carries the flattened array - if not defined, will initialize to []
    # @returns {Array} - the flattened array
    #
    def flatten(self, arg: Any, flattened: Optional[MutableSequence]) -> Any:
        """
        Flatten a nested list into a single list.
        Args:
            arg: The array or value to flatten.
            flattened: The list to accumulate results (optional).
        Returns:
            The flattened list.
        """
        if flattened is None:
            flattened = []
        if isinstance(arg, list):
            for item in arg:
                self.flatten(item, flattened)
        else:
            flattened.append(arg)
        return flattened

    #
    # Evaluate descendants against input_item data
    # @param {Object} expr - JSONata expression
    # @param {Object} input_item - input_item data to evaluate against
    # @returns {*} Evaluated input_item data
    #
    def evaluate_descendants(
        self, expr: Optional[Symbol], input_item: Optional[Any]
    ) -> Optional[Any]:
        """
        Evaluate all descendants of the input_item for a JSONata expression.
        Args:
            expr: JSONata expression representing the descendant operation.
            input_item: Input data to evaluate against.
        Returns:
            The descendants as a sequence or single value.
        """
        result = None
        result_sequence = Utils.create_sequence()
        if input_item is not None:
            # traverse all descendants of this object/array
            self.recurse_descendants(input_item, result_sequence)
            if len(result_sequence) == 1:
                result = result_sequence[0]
            else:
                result = result_sequence
        return result

    #
    # Recurse through descendants
    # @param {Object} input_item - input_item data
    # @param {Object} results - Results
    #
    def recurse_descendants(
        self, input_item: Optional[Any], results: MutableSequence
    ) -> None:
        """
        Recursively collect all descendants of an input item.
        Args:
            input_item: The input data (list or dict).
            results: List to accumulate descendants.
        """
        # this is the equivalent of //* in XPath
        if not (isinstance(input_item, list)):
            results.append(input_item)
        if isinstance(input_item, list):
            for member in input_item:
                self.recurse_descendants(member, results)
        elif input_item is not None and isinstance(input_item, dict):
            for value in input_item.values():
                self.recurse_descendants(value, results)

    #
    # Evaluate numeric expression against input_item data
    # @param {Object} lhs - LHS value
    # @param {Object} rhs - RHS value
    # @param {Object} op - opcode
    # @returns {*} Result
    #

    def evaluate_numeric_expression(
        self, lhs: Optional[Any], rhs: Optional[Any], op: Optional[str]
    ) -> Optional[Any]:
        """
        Evaluate a numeric expression using the provided operator.
        Args:
            lhs: Left-hand side value (number).
            rhs: Right-hand side value (number).
            op: Operator as a string ('+', '-', '*', '/', '%').
        Returns:
            The result of the numeric operation, or None if either side is undefined.
        Raises:
            JException: If lhs or rhs is not numeric.
        """
        result = 0

        if lhs is not None and not Utils.is_numeric(lhs):
            raise JException("T2001", -1, op, lhs)
        if rhs is not None and not Utils.is_numeric(rhs):
            raise JException("T2002", -1, op, rhs)

        if lhs is None or rhs is None:
            # if either side is undefined, the result is undefined
            return None

        # System.out.println("op22 "+op+" "+_lhs+" "+_rhs)
        lhs = float(lhs)
        rhs = float(rhs)

        if op == "+":
            result = lhs + rhs
        elif op == "-":
            result = lhs - rhs
        elif op == "*":
            result = lhs * rhs
        elif op == "/":
            result = lhs / rhs
        elif op == "%":
            result = int(math.fmod(lhs, rhs))
        return Utils.convert_number(result)

    #
    # Evaluate equality expression against input_item data
    # @param {Object} lhs - LHS value
    # @param {Object} rhs - RHS value
    # @param {Object} op - opcode
    # @returns {*} Result
    #
    def evaluate_equality_expression(
        self, lhs: Optional[Any], rhs: Optional[Any], op: Optional[str]
    ) -> Optional[Any]:
        """
        Evaluate equality expression between two values.
        Args:
            lhs: Left-hand side value.
            rhs: Right-hand side value.
            op: Operator as a string ('=', '!=').
        Returns:
            True or False depending on equality, or False if either side is undefined.
        """
        if lhs is None or rhs is None:
            # if either side is undefined, the result is false
            return False

        # JSON might come with integers,
        # convert all to double...
        # FIXME: semantically OK?
        if not isinstance(lhs, bool) and isinstance(lhs, (int, float)):
            lhs = float(lhs)
        if not isinstance(rhs, bool) and isinstance(rhs, (int, float)):
            rhs = float(rhs)

        result = None
        if op == "=":
            result = lhs == rhs  # isDeepEqual(lhs, rhs);
        elif op == "!=":
            result = lhs != rhs  # !isDeepEqual(lhs, rhs);
        return result

    #
    # Evaluate comparison expression against input_item data
    # @param {Object} lhs - LHS value
    # @param {Object} rhs - RHS value
    # @param {Object} op - opcode
    # @returns {*} Result
    #
    def evaluate_comparison_expression(
        self, lhs: Optional[Any], rhs: Optional[Any], op: Optional[str]
    ) -> Optional[Any]:
        """
        Evaluate comparison expression between two values.
        Args:
            lhs: Left-hand side value.
            rhs: Right-hand side value.
            op: Operator as a string ('<', '<=', '>', '>=').
        Returns:
            The result of the comparison, or None if either side is undefined.
        Raises:
            JException: If values are not comparable or types mismatch.
        """
        result = None

        # type checks
        lcomparable = (
            lhs is None
            or isinstance(lhs, str)
            or (not isinstance(lhs, bool) and isinstance(lhs, (int, float)))
        )
        rcomparable = (
            rhs is None
            or isinstance(rhs, str)
            or (not isinstance(rhs, bool) and isinstance(rhs, (int, float)))
        )

        # if either aa or bb are not comparable (string or numeric) values, then throw an error
        if not lcomparable or not rcomparable:
            raise JException("T2010", 0, op, lhs if lhs is not None else rhs)

        # if either side is undefined, the result is undefined
        if lhs is None or rhs is None:
            return None

        # if aa and bb are not of the same type
        if type(lhs) is not type(rhs):

            if (
                not isinstance(lhs, bool)
                and isinstance(lhs, (int, float))
                and not isinstance(rhs, bool)
                and isinstance(rhs, (int, float))
            ):
                # Java : handle Double / Integer / Long comparisons
                # convert all to double -> loss of precision (64-bit long to double) be a problem here?
                lhs = float(lhs)
                rhs = float(rhs)

            else:

                raise JException("T2009", 0, lhs, rhs)

        if op == "<":
            result = lhs < rhs
        elif op == "<=":
            result = lhs <= rhs
        elif op == ">":
            result = lhs > rhs
        elif op == ">=":
            result = lhs >= rhs
        return result

    #
    # Inclusion operator - in
    #
    # @param {Object} lhs - LHS value
    # @param {Object} rhs - RHS value
    # @returns {boolean} - true if lhs is a member of rhs
    #
    def evaluate_includes_expression(
        self, lhs: Optional[Any], rhs: Optional[Any]
    ) -> Any:
        """
        Evaluate inclusion operator to check if lhs is a member of rhs.
        Args:
            lhs: Value to check for inclusion.
            rhs: List or value to check against.
        Returns:
            True if lhs in rhs, False otherwise.
        """
        result = False

        if lhs is None or rhs is None:
            # if either side is undefined, the result is false
            return False

        if not (isinstance(rhs, list)):
            rhs = [rhs]

        for item in rhs:
            if item == lhs:
                result = True
                break

        return result

    #
    # Evaluate boolean expression against input_item data
    # @param {Object} lhs - LHS value
    # @param {functions.Function} evalrhs - Object to evaluate RHS value
    # @param {Object} op - opcode
    # @returns {*} Result
    #
    # async
    def evaluate_boolean_expression(
        self,
        lhs: Optional[Any],
        evalrhs: Callable[[], Optional[Any]],
        op: Optional[str],
    ) -> Optional[Any]:
        """
        Evaluate a boolean expression ('and', 'or') between lhs and rhs.
        Args:
            lhs: Left-hand side value.
            evalrhs: Callable to evaluate right-hand side value.
            op: Operator as a string ('and', 'or').
        Returns:
            The result of the boolean operation.
        """
        result = None

        l_bool = Jsonata.boolize(lhs)

        if op == "and":
            result = l_bool and Jsonata.boolize(evalrhs())
        elif op == "or":
            result = l_bool or Jsonata.boolize(evalrhs())
        return result

    @staticmethod
    def boolize(value: Optional[Any]) -> bool:
        """
        Convert a value to its boolean representation using Functions.to_boolean.
        Args:
            value: The value to convert.
        Returns:
            False if the conversion result is None, otherwise the boolean value.
        """
        booled_value = Functions.to_boolean(value)
        return False if booled_value is None else booled_value

    #
    # Evaluate string concatenation against input_item data
    # @param {Object} lhs - LHS value
    # @param {Object} rhs - RHS value
    # @returns {string|*} Concatenated string
    #
    def evaluate_string_concat(self, lhs: Optional[Any], rhs: Optional[Any]) -> str:
        """
        Concatenate two values as strings.
        Args:
            lhs: Left-hand side value.
            rhs: Right-hand side value.
        Returns:
            Concatenated string result.
        """
        lstr = ""
        rstr = ""
        if lhs is not None:
            lstr = Functions.string(lhs, None)
        if rhs is not None:
            rstr = Functions.string(rhs, None)

        result = lstr + rstr
        return result

    #
    # Evaluate group expression against input_item data
    # @param {Object} expr - JSONata expression
    # @param {Object} input_item - input_item data to evaluate against
    # @param {Object} environment - Environment
    # @returns {{}} Evaluated input_item data
    #
    # async
    def evaluate_group_expression(
        self,
        expr: Optional[Symbol],
        input_item: Optional[Any],
        environment: Optional[Frame],
    ) -> Any:
        """
        Evaluate a group expression, grouping input items by key and evaluating values.
        Args:
            expr: JSONata group expression.
            input_item: Input data to group.
            environment: Environment frame.
        Returns:
            Dictionary of grouped results.
        """
        result = {}
        groups = {}
        reduce = (
            True
            if (isinstance(input_item, JList)) and input_item.tuple_stream
            else False
        )
        # group the input_item sequence by "key" expression
        if not (isinstance(input_item, list)):
            input_item = Utils.create_sequence(input_item)

        # if the array is empty, add an undefined entry to enable literal JSON object to be generated
        if not input_item:
            input_item.append(None)

        for itemIndex, item in enumerate(input_item):
            env = (
                self.create_frame_from_tuple(environment, item)
                if reduce
                else environment
            )
            for pairIndex, pair in enumerate(expr.lhs_object):
                key = self.eval(pair[0], item["@"] if reduce else item, env)
                # key has to be a string
                if key is not None and not (isinstance(key, str)):
                    raise JException("T1003", expr.position, key)

                if key is not None:
                    entry = GroupEntry(item, pairIndex)
                    if groups.get(key) is not None:
                        # a value already exists in this slot
                        if groups[key].exprIndex != pairIndex:
                            # this key has been generated by another expression in the group
                            # when multiple key expressions evaluate to the same key, then error D1009 must be thrown
                            raise JException("D1009", expr.position, key)

                        # append it as an array
                        groups[key].data = Functions.append(groups[key].data, item)
                    else:
                        groups[key] = entry

        # iterate over the groups to evaluate the "value" expression
        # let generators = /* await */ Promise.all(Object.keys(groups).map(/* async */ (key, idx) => {
        idx = 0
        for k, v in groups.items():
            entry = v
            context = entry.data
            env = environment
            if reduce:
                tuple = self.reduce_tuple_stream(entry.data)
                context = tuple["@"]
                tuple.pop("@", None)
                env = self.create_frame_from_tuple(environment, tuple)
            env.is_parallel_call = idx > 0
            # return [key, /* await */ eval(expr.lhs[entry.exprIndex][1], context, env)]
            res = self.eval(expr.lhs_object[entry.exprIndex][1], context, env)
            if res is not None:
                result[k] = res

            idx += 1

        #  for (let generator of generators) {
        #      var [key, value] = /* await */ generator
        #      if(typeof value !== "undefined") {
        #          result[key] = value
        #      }
        #  }

        return result

    def reduce_tuple_stream(self, tuple_stream: Optional[Any]) -> Optional[Any]:
        """
        Reduce a tuple stream to a single dictionary by merging items.
        Args:
            tuple_stream: List of dictionaries to merge.
        Returns:
            Merged dictionary or original value if not a list.
        """
        if not (isinstance(tuple_stream, list)):
            return tuple_stream

        result = dict(tuple_stream[0])

        for ii in range(1, len(tuple_stream)):
            el = tuple_stream[ii]
            for k, v in el.items():
                result[k] = Functions.append(result[k], v)
        return result

    #
    # Evaluate range expression against input_item data
    # @param {Object} lhs - LHS value
    # @param {Object} rhs - RHS value
    # @returns {Array} Resultant array
    #
    def evaluate_range_expression(
        self, lhs: Optional[Any], rhs: Optional[Any]
    ) -> Optional[Any]:
        """
        Evaluate a range expression to produce a list of integers from lhs to rhs.
        Args:
            lhs: Left-hand side integer value.
            rhs: Right-hand side integer value.
        Returns:
            List of integers in the range, or None if invalid.
        Raises:
            JException: If lhs or rhs is not a valid integer or out of bounds.
        """
        result = None

        if lhs is not None and (isinstance(lhs, bool) or not (isinstance(lhs, int))):
            raise JException("T2003", -1, lhs)
        if rhs is not None and (isinstance(rhs, bool) or not (isinstance(rhs, int))):
            raise JException("T2004", -1, rhs)

        if rhs is None or lhs is None:
            # if either side is undefined, the result is undefined
            return result

        lhs = int(lhs)
        rhs = int(rhs)

        if lhs > rhs:
            # if the lhs is greater than the rhs, return undefined
            return result

        # limit the size of the array to ten million entries (1e7)
        # this is an implementation defined limit to protect against
        # memory and performance issues.  This value may increase in the future.
        size = rhs - lhs + 1
        if size > 1e7:
            raise JException("D2014", -1, size)

        return RangeList(lhs, rhs + 1)

    #
    # Evaluate bind expression against input_item data
    # @param {Object} expr - JSONata expression
    # @param {Object} input_item - input_item data to evaluate against
    # @param {Object} environment - Environment
    # @returns {*} Evaluated input_item data
    #
    # async
    def evaluate_bind_expression(
        self,
        expr: Optional[Symbol],
        input_item: Optional[Any],
        environment: Optional[Frame],
    ) -> Optional[Any]:
        """
        Evaluate a bind expression, assigning the result of RHS to the LHS variable in the environment.
        Args:
            expr: JSONata bind expression.
            input_item: Input data to evaluate against.
            environment: Environment frame.
        Returns:
            The value assigned to the variable.
        """
        # The RHS is the expression to evaluate
        # The LHS is the name of the variable to bind to - should be a VARIABLE token (enforced by parser)
        value = self.eval(expr.rhs, input_item, environment)
        environment.bind(str(expr.lhs.value), value)
        return value

    #
    # Evaluate condition against input_item data
    # @param {Object} expr - JSONata expression
    # @param {Object} input_item - input_item data to evaluate against
    # @param {Object} environment - Environment
    # @returns {*} Evaluated input_item data
    #
    # async
    def evaluate_condition(
        self,
        expr: Optional[Symbol],
        input_item: Optional[Any],
        environment: Optional[Frame],
    ) -> Optional[Any]:
        """
        Evaluate a conditional (if-then-else) expression.
        Args:
            expr: JSONata condition expression.
            input_item: Input data to evaluate against.
            environment: Environment frame.
        Returns:
            The result of the then or else branch, or None.
        """
        result = None
        condition = self.eval(expr.condition, input_item, environment)
        if Jsonata.boolize(condition):
            result = self.eval(expr.then, input_item, environment)
        elif expr._else is not None:
            result = self.eval(expr._else, input_item, environment)
        return result

    #
    # Evaluate block against input_item data
    # @param {Object} expr - JSONata expression
    # @param {Object} input_item - input_item data to evaluate against
    # @param {Object} environment - Environment
    # @returns {*} Evaluated input_item data
    #
    # async
    def evaluate_block(
        self,
        expr: Optional[Symbol],
        input_item: Optional[Any],
        environment: Optional[Frame],
    ) -> Optional[Any]:
        """
        Evaluate a block expression, executing each sub-expression in a new frame.
        Args:
            expr: JSONata block expression.
            input_item: Input data to evaluate against.
            environment: Environment frame.
        Returns:
            The result of the last sub-expression in the block.
        """
        result = None
        # create a new frame to limit the scope of variable assignments
        # TODO, only do this if the post-parse stage has flagged this as required
        frame = self.create_frame(environment)
        # invoke each expression in turn
        # only return the result of the last one
        for ex in expr.expressions:
            result = self.eval(ex, input_item, frame)

        return result

    #
    # Prepare a regex
    # @param {Object} expr - expression containing regex
    # @returns {functions.Function} Higher order Object representing prepared regex
    #
    def evaluate_regex(self, expr: Optional[Symbol]) -> Optional[Any]:
        """
        Prepare and return a regex object from the given expression.
        Args:
            expr: Expression containing regex.
        Returns:
            Compiled regex or value.
        """
        # Note: in Java we just use the compiled regex Pattern
        # The apply functions need to take care to evaluate
        return expr.value

    #
    # Evaluate variable against input_item data
    # @param {Object} expr - JSONata expression
    # @param {Object} input_item - input_item data to evaluate against
    # @param {Object} environment - Environment
    # @returns {*} Evaluated input_item data
    #
    def evaluate_variable(
        self,
        expr: Optional[Symbol],
        input_item: Optional[Any],
        environment: Optional[Frame],
    ) -> Optional[Any]:
        """
        Evaluate a variable expression, looking up its value in the environment.
        Args:
            expr: JSONata variable expression.
            input_item: Input data to evaluate against.
            environment: Environment frame.
        Returns:
            The value of the variable, or context value if empty string.
        """
        # lookup the variable value in the environment
        result = None
        # if the variable name is empty string, then it refers to context value
        if expr.value == "":
            # Empty string == "$" !
            result = (
                input_item[0]
                if isinstance(input_item, JList) and input_item.outer_wrapper
                else input_item
            )
        else:
            result = environment.lookup(str(expr.value))
            if self.parser.dbg:
                print("variable name=" + expr.value + " val=" + result)
        return result

    #
    # sort / order-by operator
    # @param {Object} expr - AST for operator
    # @param {Object} input_item - input_item data to evaluate against
    # @param {Object} environment - Environment
    # @returns {*} Ordered sequence
    #
    # async
    def evaluate_sort_expression(
        self,
        expr: Optional[Symbol],
        input_item: Optional[Any],
        environment: Optional[Frame],
    ) -> Optional[Any]:
        """
        Evaluate a sort expression, ordering input items by the given criteria.
        Args:
            expr: JSONata sort expression.
            input_item: Input data to sort.
            environment: Environment frame.
        Returns:
            Ordered sequence of input items.
        """
        result = None

        # evaluate the lhs, then sort the results in order according to rhs expression
        lhs = input_item
        is_tuple_sort = (
            True
            if (isinstance(input_item, JList) and input_item.tuple_stream)
            else False
        )

        # sort the lhs array
        # use comparator function

        from src.jsonata.Jsonata.ComparatorWrapper import ComparatorWrapper

        comparator = ComparatorWrapper(self, expr, environment, is_tuple_sort).compare

        #  var focus = {
        #      environment: environment,
        #      input_item: input_item
        #  }
        #  // the `focus` is passed in as the `this` for the invoked function
        #  result = /* await */ fn.sort.apply(focus, [lhs, comparator])

        result = Functions.sort(lhs, comparator)
        return result

    #
    # create a transformer function
    # @param {Object} expr - AST for operator
    # @param {Object} input_item - input_item data to evaluate against
    # @param {Object} environment - Environment
    # @returns {*} tranformer function
    #
    def evaluate_transform_expression(
        self,
        expr: Optional[Symbol],
        input_item: Optional[Any],
        environment: Optional[Frame],
    ) -> Optional[Any]:
        """
        Create a transformer function from the given expression.
        Args:
            expr: AST for operator.
            input_item: Input data to evaluate against.
            environment: Environment frame.
        Returns:
            Transformer function as JFunction.
        """
        transformer = Transformer(self, expr, environment)
        return JFunction(transformer, "<(oa):o>")

    _chain_ast = (
        None  # = new Parser().parse("function($f, $g) { function($x){ $g($f($x)) } }");
    )

    @staticmethod
    def chain_ast() -> Optional[Symbol]:
        """
        Return the parsed AST for function composition (chaining).
        Returns:
            Symbol: The parsed AST representing function composition.
        """
        if Jsonata._chain_ast is None:
            # only create on demand
            Jsonata._chain_ast = (Parser()).parse(
                "function($f, $g) { function($x){ $g($f($x)) } }"
            )
        return Jsonata._chain_ast

    #
    # Apply the Object on the RHS using the sequence on the LHS as the first argument
    # @param {Object} expr - JSONata expression
    # @param {Object} input_item - input_item data to evaluate against
    # @param {Object} environment - Environment
    # @returns {*} Evaluated input_item data
    #
    # async
    def evaluate_apply_expression(
        self,
        expr: Optional[Symbol],
        input_item: Optional[Any],
        environment: Optional[Frame],
    ) -> Optional[Any]:
        """
        Apply the object on the RHS using the sequence on the LHS as the first argument.
        Args:
            expr: JSONata expression.
            input_item: Input data to evaluate against.
            environment: Environment frame.
        Returns:
            Evaluated input_item data.
        """
        result = None

        lhs = self.eval(expr.lhs, input_item, environment)

        if expr.rhs.type == "function":
            # Symbol applyTo = new Symbol(); applyTo.context = lhs
            # this is a Object _invocation_; invoke it with lhs expression as the first argument
            result = self.evaluate_function(expr.rhs, input_item, environment, lhs)
        else:
            func = self.eval(expr.rhs, input_item, environment)

            if not self.is_function_like(func) and not self.is_function_like(lhs):
                raise JException("T2006", expr.position, func)

            if self.is_function_like(lhs):
                # this is Object chaining (func1 ~> func2)
                # λ($f, $g) { λ($x){ $g($f($x)) } }
                chain = self.eval(Jsonata.chain_ast(), None, environment)
                args = [lhs, func]
                result = self.apply(chain, args, None, environment)
            else:
                args = [lhs]
                result = self.apply(func, args, None, environment)

        return result

    def is_function_like(self, o: Optional[Any]) -> bool:
        """
        Check if the object is function-like (native, lambda, or regex).
        Args:
            o: Object to check.
        Returns:
            bool: True if function-like, False otherwise.
        """
        return (
            Utils.is_function(o)
            or Functions.is_lambda(o)
            or (isinstance(o, re.Pattern))
        )

    CURRENT = threading.local()
    MUTEX = threading.Lock()

    #
    # Returns a per thread instance of this parsed expression.
    #
    # @return
    #
    def get_per_thread_instance(self):
        """
        Get a per-thread instance of Jsonata for thread safety.
        Returns:
            Jsonata: The thread-local instance.
        """
        if hasattr(Jsonata.CURRENT, "jsonata"):
            return Jsonata.CURRENT.jsonata

        with Jsonata.MUTEX:
            if hasattr(Jsonata.CURRENT, "jsonata"):
                return Jsonata.CURRENT.jsonata
            thread_inst = copy.copy(self)
            Jsonata.CURRENT.jsonata = thread_inst
            return thread_inst

    #
    # Evaluate Object against input_item data
    # @param {Object} expr - JSONata expression
    # @param {Object} input_item - input_item data to evaluate against
    # @param {Object} environment - Environment
    # @returns {*} Evaluated input_item data
    #
    # async
    def evaluate_function(
        self,
        expr: Optional[Symbol],
        input_item: Optional[Any],
        environment: Optional[Frame],
        applyto_context: Optional[Any],
    ) -> Optional[Any]:
        """
        Evaluate a function expression against input_item data.
        Args:
            expr: JSONata expression.
            input_item: Input data to evaluate against.
            environment: Environment frame.
            applyto_context: Context to apply to function.
        Returns:
            Evaluated input_item data.
        """
        # this.current is set by getPerThreadInstance() at this point

        # create the procedure
        # can"t assume that expr.procedure is a lambda type directly
        # could be an expression that evaluates to a Object (e.g. variable reference, parens expr etc.
        # evaluate it generically first, then check that it is a function.  Throw error if not.
        proc = self.eval(expr.procedure, input_item, environment)

        if (
            proc is None
            and getattr(expr.procedure, "type", None) is not None
            and expr.procedure.type == "path"
            and environment.lookup(str(expr.procedure.steps[0].value)) is not None
        ):
            # help the user out here if they simply forgot the leading $
            raise JException("T1005", expr.position, expr.procedure.steps[0].value)

        evaluated_args = []

        if applyto_context is not Utils.NONE:
            evaluated_args.append(applyto_context)
        # eager evaluation - evaluate the arguments
        args = expr.arguments if expr.arguments is not None else []
        for val in args:
            arg = self.eval(val, input_item, environment)
            if Utils.is_function(arg) or Functions.is_lambda(arg):
                # wrap this in a closure
                # Java: not required, already a JFunction
                #  const closure = /* async */ Object (...params) {
                #      // invoke func
                #      return /* await */ apply(arg, params, null, environment)
                #  }
                #  closure.arity = getFunctionArity(arg)

                # JFunctionCallable fc = (ctx,params) ->
                #     apply(arg, params, null, environment)

                # JFunction cl = new JFunction(fc, "<o:o>")

                # Object cl = apply(arg, params, null, environment)
                evaluated_args.append(arg)
            else:
                evaluated_args.append(arg)
        # apply the procedure
        proc_val = expr.procedure.value if expr.procedure is not None else None
        proc_name = (
            expr.procedure.steps[0].value
            if getattr(expr.procedure, "type", None) is not None
            and expr.procedure.type == "path"
            else proc_val
        )

        # Error if proc is null
        if proc is None:
            raise JException("T1006", expr.position, proc_name)

        try:
            if isinstance(proc, Symbol):
                proc.token = proc_name
                proc.position = expr.position
            result = self.apply(proc, evaluated_args, input_item, environment)
        except JException as jex:
            if jex.location < 0:
                # add the position field to the error
                jex.location = expr.position
            if jex.current is None:
                # and the Object identifier
                jex.current = expr.token
            raise jex
        except Exception as err:
            raise err
        return result

    #
    # Apply procedure or function
    # @param {Object} proc - Procedure
    # @param {Array} args - Arguments
    # @param {Object} input_item - input_item
    # @param {Object} environment - environment
    # @returns {*} Result of procedure
    #
    # async
    def apply(
        self,
        proc: Optional[Any],
        args: Optional[Any],
        input_item: Optional[Any],
        environment: Optional[Frame],
    ) -> Optional[Any]:
        """
        Apply a procedure or function to arguments and input data, handling tail-call optimization.
        Args:
            proc: Procedure or function to apply.
            args: Arguments to pass to the procedure.
            input_item: Input data.
            environment: Environment frame.
        Returns:
            Result of procedure or function application.
        """
        result = self.apply_inner(proc, args, input_item, environment)
        while Functions.is_lambda(result) and result.thunk:
            # trampoline loop - this gets invoked as a result of tail-call optimization
            # the Object returned a tail-call thunk
            # unpack it, evaluate its arguments, and apply the tail call
            next = self.eval(
                result.body.procedure, result.input_item, result.environment
            )
            if result.body.procedure.type == "variable":
                if isinstance(next, Symbol):  # Java: not if JFunction
                    next.token = result.body.procedure.value
            if isinstance(next, Symbol):  # Java: not if JFunction
                next.position = result.body.procedure.position
            evaluated_args = []
            for arg in result.body.arguments:
                evaluated_args.append(
                    self.eval(arg, result.input_item, result.environment)
                )

            result = self.apply_inner(next, evaluated_args, input_item, environment)
        return result

    #
    # Apply procedure or function
    # @param {Object} proc - Procedure
    # @param {Array} args - Arguments
    # @param {Object} input_item - input_item
    # @param {Object} environment - environment
    # @returns {*} Result of procedure
    #
    # async
    def apply_inner(
        self,
        proc: Optional[Any],
        args: Optional[Any],
        input_item: Optional[Any],
        environment: Optional[Frame],
    ) -> Optional[Any]:
        """
        Apply a procedure or function to arguments and input data (internal implementation).
        Args:
            proc: Procedure or function to apply.
            args: Arguments to pass to the procedure.
            input_item: Input data.
            environment: Environment frame.
        Returns:
            Result of procedure or function application.
        """
        try:
            validated_args = args
            if proc is not None:
                validated_args = self.validate_arguments(proc, args, input_item)

            if Functions.is_lambda(proc):
                result = self.apply_procedure(proc, validated_args)
            elif isinstance(proc, JFunction):
                # typically these are functions that are returned by the invocation of plugin functions
                # the `input_item` is being passed in as the `this` for the invoked function
                # this is so that functions that return objects containing functions can chain
                # e.g. /* await */ (/* await */ $func())

                # handling special case of Javascript:
                # when calling a function with fn.apply(ctx, args) and args = [undefined]
                # Javascript will convert to undefined (without array)
                if (
                    isinstance(validated_args, list)
                    and len(validated_args) == 1
                    and validated_args[0] is None
                ):
                    # validated_args = null
                    pass

                result = proc.call(input_item, validated_args)
                #  if (isPromise(result)) {
                #      result = /* await */ result
                #  }
            from src.jsonata.Jsonata.JLambda import JLambda

            if isinstance(proc, JLambda):
                result = proc.call(input_item, validated_args)
            elif isinstance(proc, re.Pattern):
                result = [s for s in validated_args if proc.search(s) is not None]
            else:
                print("Proc not found " + str(proc))
                raise JException("T1006", 0)
        except JException as err:
            #  if(proc) {
            #      if (typeof err.token == "undefined" && typeof proc.token !== "undefined") {
            #          err.token = proc.token
            #      }
            #      err.position = proc.position
            #  }
            raise err
        return result

    #
    # Evaluate lambda against input_item data
    # @param {Object} expr - JSONata expression
    # @param {Object} input_item - input_item data to evaluate against
    # @param {Object} environment - Environment
    # @returns {{lambda: boolean, input_item: *, environment: *, arguments: *, body: *}} Evaluated input_item data
    #
    def evaluate_lambda(
        self,
        expr: Optional[Symbol],
        input_item: Optional[Any],
        environment: Optional[Frame],
    ) -> Optional[Any]:
        """
        Evaluate a lambda expression and return a closure object.
        Args:
            expr: JSONata lambda expression.
            input_item: Input data to evaluate against.
            environment: Environment frame.
        Returns:
            Closure object representing the lambda.
        """
        # make a Object (closure)
        procedure = Symbol(self.parser)

        procedure._jsonata_lambda = True
        procedure.input_item = input_item
        procedure.environment = environment
        procedure.arguments = expr.arguments
        procedure.signature = expr.signature
        procedure.body = expr.body

        if expr.thunk:
            procedure.thunk = True

        # procedure.apply = /* async */ function(self, args) {
        #     return /* await */ apply(procedure, args, input_item_item, !!self ? self.environment : environment)
        # }
        return procedure

    #
    # Evaluate partial application
    # @param {Object} expr - JSONata expression
    # @param {Object} input_item_item - input_item_item data to evaluate against
    # @param {Object} environment - Environment
    # @returns {*} Evaluated input_item data
    #
    # async
    def evaluate_partial_application(
        self,
        expr: Optional[Symbol],
        input_item: Optional[Any],
        environment: Optional[Frame],
    ) -> Optional[Any]:
        """
        Evaluate a partial application, returning a partially applied function or lambda.
        Args:
            expr: JSONata partial application expression.
            input_item: Input data to evaluate against.
            environment: Environment frame.
        Returns:
            Partially applied function or lambda.
        """
        # partially apply a function
        result = None
        # evaluate the arguments
        evaluated_args = []
        for arg in expr.arguments:
            if arg.type == "operator" and (arg.value == "?"):
                evaluated_args.append(arg)
            else:
                evaluated_args.append(self.eval(arg, input_item, environment))
        # lookup the procedure
        proc = self.eval(expr.procedure, input_item, environment)
        if (
            proc is not None
            and expr.procedure.type == "path"
            and environment.lookup(str(expr.procedure.steps[0].value)) is not None
        ):
            # help the user out here if they simply forgot the leading $
            raise JException("T1007", expr.position, expr.procedure.steps[0].value)
        if Functions.is_lambda(proc):
            result = self.partial_apply_procedure(proc, evaluated_args)
        elif Utils.is_function(proc):
            result = self.partial_apply_native_function(proc, evaluated_args)
            #  } else if (typeof proc === "function") {
            #      result = partialApplyNativeFunction(proc, evaluated_args)
        else:
            raise JException(
                "T1008",
                expr.position,
                (
                    expr.procedure.steps[0].value
                    if expr.procedure.type == "path"
                    else expr.procedure.value
                ),
            )
        return result

    #
    # Validate the arguments against the signature validator (if it exists)
    # @param {Function} signature - validator function
    # @param {Array} args - Object arguments
    # @param {*} context - context value
    # @returns {Array} - validated arguments
    #
    def validate_arguments(
        self, signature: Any, args: Optional[Any], context: Optional[Any]
    ) -> Optional[Any]:
        """
        Validate the arguments against the signature validator (if it exists).
        Args:
            signature: Validator function or lambda.
            args: Arguments to validate.
            context: Context value.
        Returns:
            Validated arguments.
        """
        validated_args = args
        if Utils.is_function(signature):
            validated_args = signature.validate(args, context)
        elif Functions.is_lambda(signature):
            sig = signature.signature
            if sig is not None:
                validated_args = sig.validate(args, context)
        return validated_args

    #
    # Apply procedure
    # @param {Object} proc - Procedure
    # @param {Array} args - Arguments
    # @returns {*} Result of procedure
    #
    # async
    def apply_procedure(
        self, proc: Optional[Any], args: Optional[Any]
    ) -> Optional[Any]:
        """
        Apply a procedure to arguments and return the result.
        Args:
            proc: Procedure to apply.
            args: Arguments to pass to the procedure.
        Returns:
            Result of procedure execution.
        """
        result = None
        env = self.create_frame(proc.environment)
        for i, arg in enumerate(proc.arguments):
            if i >= len(args):
                break
            env.bind(str(arg.value), args[i])
        if isinstance(proc.body, Symbol):
            result = self.eval(proc.body, proc.input, env)
        else:
            raise RuntimeError("Cannot execute procedure: " + proc + " " + proc.body)
        #  if (typeof proc.body === "function") {
        #      // this is a lambda that wraps a native Object - generated by partially evaluating a native
        #      result = /* await */ applyNativeFunction(proc.body, env)
        return result

    #
    # Partially apply procedure
    # @param {Object} proc - Procedure
    # @param {Array} args - Arguments
    # @returns {{lambda: boolean, input: *, environment: {bind, lookup}, arguments: Array, body: *}} Result of partially applied procedure
    #
    def partial_apply_procedure(self, proc: Optional[Symbol], args: Sequence) -> Symbol:
        """
        Partially apply a procedure, binding supplied parameters and returning a closure for remaining parameters.
        Args:
            proc: Procedure to partially apply.
            args: Arguments to bind.
        Returns:
            Closure object representing the partially applied procedure.
        """
        # create a closure, bind the supplied parameters and return a Object that takes the remaining (?) parameters
        # Note Uli: if no env, bind to default env so the native functions can be found
        env = self.create_frame(
            proc.environment if proc.environment is not None else self.environment
        )
        unbound_args = []
        index = 0
        for param in proc.arguments:
            #         proc.arguments.forEach(Object (param, index) {
            arg = args[index] if index < len(args) else None
            if (arg is None) or (
                isinstance(arg, Symbol)
                and ("operator" == arg.type and "?" == arg.value)
            ):
                unbound_args.append(param)
            else:
                env.bind(str(param.value), arg)
            index += 1
        procedure = Symbol(self.parser)
        procedure._jsonata_lambda = True
        procedure.input = proc.input
        procedure.environment = env
        procedure.arguments = unbound_args
        procedure.body = proc.body

        return procedure

    #
    # Partially apply native function
    # @param {Function} native - Native function
    # @param {Array} args - Arguments
    # @returns {{lambda: boolean, input: *, environment: {bind, lookup}, arguments: Array, body: *}} Result of partially applying native function
    #
    def partial_apply_native_function(
        self, native: Optional[JFunction], args: Sequence
    ) -> Symbol:
        """
        Partially apply a native function, binding supplied arguments and returning a closure for remaining parameters.
        Args:
            native: Native function to partially apply.
            args: Arguments to bind.
        Returns:
            Closure object representing the partially applied native function.
        """
        # create a lambda Object that wraps and invokes the native function
        # get the list of declared arguments from the native function
        # this has to be picked out from the toString() value

        # var body = "function($a,$c) { $substring($a,0,$c) }"

        sig_args = []
        part_args = []
        i = 0
        while i < native.get_number_of_args():
            arg_name = "$" + chr(ord("a") + i)
            sig_args.append(arg_name)
            if i >= len(args) or args[i] is None:
                part_args.append(arg_name)
            else:
                part_args.append(args[i])
            i += 1

        body = "function(" + ", ".join(sig_args) + "){"
        body += "$" + native.function_name + "(" + ", ".join(sig_args) + ") }"

        if self.parser.dbg:
            print("partial trampoline = " + body)

        #  var sig_args = getNativeFunctionArguments(_native)
        #  sig_args = sig_args.stream().map(sigArg -> {
        #      return "$" + sigArg
        #  }).toList()
        #  var body = "function(" + String.join(", ", sig_args) + "){ _ }"

        body_ast = self.parser.parse(body)
        # body_ast.body = _native

        partial = self.partial_apply_procedure(body_ast, args)
        return partial

    #
    # Apply native function
    # @param {Object} proc - Procedure
    # @param {Object} env - Environment
    # @returns {*} Result of applying native function
    #
    # async
    def apply_native_function(
        self, proc: Optional[JFunction], env: Optional[Frame]
    ) -> Optional[Any]:
        """
        Apply a native function within the given environment.
        Args:
            proc: Native function to apply.
            env: Environment in which to apply the function.
        Returns:
            Result of applying the native function, or None if not implemented.
        """
        # Not called in Java - JFunction call directly calls native function
        return None

    def get_native_function_arguments(
        self, func: Optional[JFunction]
    ) -> Optional[list]:
        """
        Retrieve the arguments for a native function.
        Args:
            func: Native function whose arguments are to be retrieved.
        Returns:
            List of arguments for the native function, or None if not implemented.
        """
        # Not called in Java
        return None

    @staticmethod
    def define_function(
        func: str, signature: Optional[str], func_impl_method: Optional[str] = None
    ) -> JFunction:
        """
        Define a new function and bind it to the static frame.
        Args:
            func: Function name as a string.
            signature: JSONata function signature definition.
            func_impl_method: Optional implementation method name.
        Returns:
            JFunction object representing the defined function.
        """
        fn = JNativeFunction(func, signature, Functions, func_impl_method)
        Jsonata.static_frame.bind(func, fn)
        return fn

    @staticmethod
    def function(
        name: str, signature: Optional[str], clazz: Optional[Any], method_name: str
    ) -> JFunction:
        """
        Create and return a JNativeFunction instance for the given function definition.
        Args:
            name: Name of the function.
            signature: JSONata function signature definition.
            clazz: Class or module containing the function implementation.
            method_name: Name of the implementation method.
        Returns:
            JFunction object representing the defined native function.
        """
        return JNativeFunction(name, signature, clazz, method_name)

    #
    # parses and evaluates the supplied expression
    # @param {string} expr - expression to evaluate
    # @returns {*} - result of evaluating the expression
    #
    # async
    # Object functionEval(String expr, Object focus) {
    # moved to functions.Functions !
    # }

    #
    # Clones an object
    # @param {Object} arg - object to clone (deep copy)
    # @returns {*} - the cloned object
    #
    # Object functionClone(Object arg) {
    # moved to functions.Functions !
    # }

    #
    # Create frame
    # @param {Object} enclosingEnvironment - Enclosing environment
    # @returns {{bind: bind, lookup: lookup}} Created frame
    #
    def create_frame(self, enclosing_environment: Optional[Frame] = None) -> Frame:
        """Create frame
        @param {Object} enclosingEnvironment - Enclosing environment
        @returns {{bind: bind, lookup: lookup}} Created frame
        """
        return Frame(enclosing_environment)

        # The following logic is in class Frame:
        #  var bindings = {}
        #  return {
        #      bind: Object (name, value) {
        #          bindings[name] = value
        #      },
        #      lookup: Object (name) {
        #          var value
        #          if(bindings.hasOwnProperty(name)) {
        #              value = bindings[name]
        #          } else if (enclosingEnvironment) {
        #              value = enclosingEnvironment.lookup(name)
        #          }
        #          return value
        #      },
        #      timestamp: enclosingEnvironment ? enclosingEnvironment.timestamp : null,
        #      async: enclosingEnvironment ? enclosingEnvironment./* async */ : false,
        #      isParallelCall: enclosingEnvironment ? enclosingEnvironment.isParallelCall : false,
        #      global: enclosingEnvironment ? enclosingEnvironment.global : {
        #          ancestry: [ null ]
        #      }
        #  }

    # Function registration
    @staticmethod
    def register_functions() -> None:
        """
        Register all built-in JSONata functions in the static frame.
        This method defines and binds standard functions such as sum, count, string manipulation,
        math operations, date/time utilities, and other core JSONata features.
        """
        Jsonata.define_function("sum", "<a<n>:n>")
        Jsonata.define_function("count", "<a:n>")
        Jsonata.define_function("max", "<a<n>:n>")
        Jsonata.define_function("min", "<a<n>:n>")
        Jsonata.define_function("average", "<a<n>:n>")
        Jsonata.define_function("string", "<x-b?:s>")
        Jsonata.define_function("substring", "<s-nn?:s>")
        Jsonata.define_function("substringBefore", "<s-s:s>", "substring_before")
        Jsonata.define_function("substringAfter", "<s-s:s>", "substring_after")
        Jsonata.define_function("lowercase", "<s-:s>")
        Jsonata.define_function("uppercase", "<s-:s>")
        Jsonata.define_function("length", "<s-:n>")
        Jsonata.define_function("trim", "<s-:s>")
        Jsonata.define_function("pad", "<s-ns?:s>")
        Jsonata.define_function("match", "<s-f<s:o>n?:a<o>>", "match_")
        Jsonata.define_function("contains", "<s-(sf):b>")  # TODO <s-(sf<s:o>):b>
        Jsonata.define_function(
            "replace", "<s-(sf)(sf)n?:s>"
        )  # TODO <s-(sf<s:o>)(sf<o:s>)n?:s>
        Jsonata.define_function("split", "<s-(sf)n?:a<s>>")  # TODO <s-(sf<s:o>)n?:a<s>>
        Jsonata.define_function("join", "<a<s>s?:s>")
        Jsonata.define_function("formatNumber", "<n-so?:s>", "format_number")
        Jsonata.define_function("formatBase", "<n-n?:s>", "format_base")
        Jsonata.define_function("formatInteger", "<n-s:s>", "format_integer")
        Jsonata.define_function("parseInteger", "<s-s:n>", "parse_integer")
        Jsonata.define_function("number", "<(nsb)-:n>")
        Jsonata.define_function("floor", "<n-:n>")
        Jsonata.define_function("ceil", "<n-:n>")
        Jsonata.define_function("round", "<n-n?:n>")
        Jsonata.define_function("abs", "<n-:n>")
        Jsonata.define_function("sqrt", "<n-:n>")
        Jsonata.define_function("power", "<n-n:n>")
        Jsonata.define_function("random", "<:n>")
        Jsonata.define_function("boolean", "<x-:b>", "to_boolean")
        Jsonata.define_function("not", "<x-:b>", "not_")
        Jsonata.define_function("map", "<af>")
        Jsonata.define_function("zip", "<a+>")
        Jsonata.define_function("filter", "<af>")
        Jsonata.define_function("single", "<af?>")
        Jsonata.define_function(
            "reduce", "<afj?:j>", "fold_left"
        )  # TODO <f<jj:j>a<j>j?:j>
        Jsonata.define_function("sift", "<o-f?:o>")
        Jsonata.define_function("keys", "<x-:a<s>>")
        Jsonata.define_function("lookup", "<x-s:x>")
        Jsonata.define_function("append", "<xx:a>")
        Jsonata.define_function("exists", "<x:b>")
        Jsonata.define_function("spread", "<x-:a<o>>")
        Jsonata.define_function("merge", "<a<o>:o>")
        Jsonata.define_function("reverse", "<a:a>")
        Jsonata.define_function("each", "<o-f:a>")
        Jsonata.define_function("error", "<s?:x>")
        Jsonata.define_function("assert", "<bs?:x>", "assert_fn")
        Jsonata.define_function("type", "<x:s>")
        Jsonata.define_function("sort", "<af?:a>")
        Jsonata.define_function("shuffle", "<a:a>")
        Jsonata.define_function("distinct", "<x:x>")
        Jsonata.define_function("base64encode", "<s-:s>")
        Jsonata.define_function("base64decode", "<s-:s>")
        Jsonata.define_function("encodeUrlComponent", "<s-:s>", "encode_url_component")
        Jsonata.define_function("encodeUrl", "<s-:s>", "encode_url")
        Jsonata.define_function("decodeUrlComponent", "<s-:s>", "decode_url_component")
        Jsonata.define_function("decodeUrl", "<s-:s>", "decode_url")
        Jsonata.define_function("eval", "<sx?:x>", "function_eval")
        Jsonata.define_function("toMillis", "<s-s?:n>", "datetime_to_millis")
        Jsonata.define_function("fromMillis", "<n-s?s?:s>", "datetime_from_millis")
        Jsonata.define_function("clone", "<(oa)-:o>", "function_clone")

        Jsonata.define_function("now", "<s?s?:s>")
        Jsonata.define_function("millis", "<:n>")

        #  environment.bind("now", defineFunction(function(picture, timezone) {
        #      return datetime.fromMillis(timestamp.getTime(), picture, timezone)
        #  }, "<s?s?:s>"))
        #  environment.bind("millis", defineFunction(function() {
        #      return timestamp.getTime()
        #  }, "<:n>"))
