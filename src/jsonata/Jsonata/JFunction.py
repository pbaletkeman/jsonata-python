from __future__ import annotations
from typing import Any, Optional, Sequence


from src.jsonata.Jsonata.JFunctionCallable import JFunctionCallable
from src.jsonata.Jsonata.JFunctionSignatureValidation import (
    JFunctionSignatureValidation,
)


class JFunction(JFunctionCallable, JFunctionSignatureValidation):
    """
    Represents a JSONata function with signature validation and callable interface.
    """

    function: "JFunctionCallable"
    signature: Optional["Signature"]
    function_name: Optional[str]

    def __init__(self, function, signature):
        """
        Initialize a JFunction object.
        Args:
            function: The callable function implementation.
            signature: The signature string or object.
        """
        from src.jsonata.Signature.Signature import Signature

        self.function = function
        if signature is not None:
            self.signature = Signature(signature, str(type(function)))
        else:
            self.signature = None

        self.function_name = None

    def call(
        self, input_item: Optional[Any], args: Optional[Sequence]
    ) -> Optional[Any]:
        """
        Call the function with the given input and arguments.
        Args:
            input_item: The input item for the function.
            args: Arguments to the function.
        Returns:
            The result of the function call.
        """
        return self.function.call(input_item, args)

    def validate(self, args: Optional[Any], context: Optional[Any]) -> Optional[Any]:
        """
        Validate the arguments against the function signature.
        Args:
            args: Arguments to validate.
            context: Context for validation.
        Returns:
            Validated arguments or original args if no signature.
        """

        if self.signature is not None:
            return self.signature.validate(args, context)

        return args

    def get_number_of_args(self) -> int:
        """
        Get the number of arguments for the function.
        Returns:
            The number of arguments (default 0).
        """

        return 0
