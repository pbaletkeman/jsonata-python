# pylint: disable=locally-disabled, multiple-statements, fixme, line-too-long

"""
JFunctionCallable module for Jsonata Python implementation.
Defines the JFunctionCallable interface for callable JSONata functions.
"""


from typing import Any, Optional, Sequence


class JFunctionCallable:
    """
    Interface for callable JSONata functions.
    """

    def call(self, input_: Optional[Any], args: Optional[Sequence]) -> Optional[Any]:
        """
        Call the function with the given input and arguments.
        Args:
            input_: The input item for the function.
            args: Arguments to the function.
        Returns:
            The result of the function call.
        """
        # Should be implemented by subclasses.
        raise NotImplementedError("Subclasses must implement call method.")
