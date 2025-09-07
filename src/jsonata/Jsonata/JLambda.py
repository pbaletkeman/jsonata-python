from collections.abc import Sequence
from typing import Any, Callable, Optional

from src.jsonata.Jsonata.JFunctionCallable import JFunctionCallable
from src.jsonata.Jsonata.JFunctionSignatureValidation import (
    JFunctionSignatureValidation,
)


class JLambda(JFunctionCallable, JFunctionSignatureValidation):
    """
    Represents a JSONata lambda function with signature validation and callable interface.
    """

    function: Callable

    def __init__(self, function):
        """
        Initialize a JLambda object.
        Args:
            function: The callable function implementation.
        """
        self.function = function

    def call(self, input_: Optional[Any], args: Optional[Sequence]) -> Optional[Any]:
        """
        Call the lambda function with the given input and arguments.
        Args:
            input_item: The input item for the function (unused).
            args: Arguments to the function.
        Returns:
            The result of the function call.
        """
        if isinstance(args, list):
            return self.function(*args)
        else:
            return self.function()

    def validate(self, args: Optional[Any], context: Optional[Any]) -> Optional[Any]:
        """
        Validate the arguments for the lambda function.
        Args:
            args: Arguments to validate.
            context: Context for validation.
        Returns:
            The validated arguments.
        """
        # Implement validation logic if needed
        return args
