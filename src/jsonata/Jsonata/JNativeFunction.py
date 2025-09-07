# pylint: disable=locally-disabled, multiple-statements, fixme, line-too-long

"""
JNativeFunction module for Jsonata Python implementation.
Defines the JNativeFunction class for wrapping native Python implementations and signatures in Jsonata.
"""

import inspect
from typing import Any, Optional, Sequence
from src.jsonata.Jsonata.JFunction import JFunction
from src.jsonata.Signature.Signature import Signature


class JNativeFunction(JFunction):
    """
    Represents a native function in Jsonata, wrapping Python implementations and signatures.
    """

    function_name: str
    signature: Optional[Signature]
    clz: Any
    method: Optional[Any]
    nargs: int

    def __init__(self, function_name, signature, clz, impl_method_name):
        """
        Initialize a JNativeFunction object.
        Args:
            function_name: Name of the function.
            signature: Signature string.
            clz: Class containing the function implementation.
            impl_method_name: Name of the implementation method.
        """
        super().__init__(None, None)
        self.function_name = function_name
        self.signature = Signature(signature, function_name)
        if impl_method_name is None:
            impl_method_name = self.function_name
        from src.jsonata.Functions.Functions import Functions

        self.method = Functions.get_function(clz, impl_method_name)
        self.nargs = (
            len(inspect.signature(self.method).parameters)
            if self.method is not None
            else 0
        )

        if self.method is None:
            print(
                "Function not implemented: "
                + function_name
                + " impl="
                + impl_method_name
            )

    def call(
        self, input_item: Optional[Any], args: Optional[Sequence]
    ) -> Optional[Any]:
        """
        Call the native function with the given arguments.
        Args:
            input_: Input item (unused for native functions).
            args: Arguments to the function.
        Returns:
            The result of the function call.
        """
        from src.jsonata.Functions.Functions import Functions

        return Functions.call(self.method, self.nargs, args)

    def get_number_of_args(self) -> int:
        """
        Get the number of arguments for the native function.
        Returns:
            int: Number of arguments.
        """
        return self.nargs
