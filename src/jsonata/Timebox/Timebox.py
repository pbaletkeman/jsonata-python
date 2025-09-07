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

# pylint: disable=locally-disabled, multiple-statements, fixme, line-too-long

"""
Timebox module for JSONata Python implementation.
Provides runtime protection for expression evaluation, enforcing timeouts and maximum recursion depth to prevent runaway execution.
Adapted from jsonata-java project.
"""

import time

from src.jsonata.JException.JException import JException


#
# Configure max runtime / max recursion depth.
# See Frame.setRuntimeBounds - usually not used directly
#
class Timebox:
    """
    Protects expression evaluation from runaway execution by enforcing timeouts and maximum recursion depth.
    Used to prevent infinite loops and excessive stack growth in Jsonata expressions.
    """

    #
    # Protect the process/browser from a runnaway expression
    # i.e. Infinite loop (tail recursion), or excessive stack growth
    #
    # @param {Object} expr - expression to protect
    # @param {Number} timeout - max time in ms
    # @param {Number} max_depth - max stack depth
    #

    timeout: int
    max_depth: int
    time: int
    depth: int

    def __init__(self, expr, timeout=10000, max_depth=100):
        """
        Initialize a Timebox to protect against runaway expressions.
        Args:
            expr: The expression to protect.
            timeout: Maximum time in milliseconds.
            max_depth: Maximum stack depth.
        """
        self.timeout = timeout
        self.max_depth = max_depth
        self.time = Timebox.current_milli_time()
        self.depth = 0

        # register callbacks
        def entry_callback(exp, input, env):
            if env.is_parallel_call:
                return
            self.depth += 1
            self.check_runaway()

        expr.set_evaluate_entry_callback(entry_callback)

        def exit_callback(exp, input, env, res):
            if env.is_parallel_call:
                return
            self.depth -= 1
            self.check_runaway()

        expr.set_evaluate_exit_callback(exit_callback)

    def check_runaway(self) -> None:
        """
        Check for runaway execution (stack overflow or timeout).
        Raises:
            JException: If stack depth or timeout exceeded.
        """
        if self.depth > self.max_depth:
            # stack too deep
            raise JException(
                "Stack overflow error: Check for non-terminating recursive function.  Consider rewriting as tail-recursive. Depth="
                + str(self.depth)
                + " max="
                + str(self.max_depth),
                -1,
            )
        if Timebox.current_milli_time() - self.time > self.timeout:
            # expression has run for too long
            raise JException(
                "Expression evaluation timeout: "
                + str(self.timeout)
                + "ms. Check for infinite loop",
                -1,
            )

    @staticmethod
    def current_milli_time() -> int:
        """
        Get the current time in milliseconds.
        Returns:
            Current time in milliseconds.
        """
        return round(time.time() * 1000)
