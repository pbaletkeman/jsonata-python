from __future__ import annotations
from typing import Any, Optional, Sequence

from .JFunctionCallable import JFunctionCallable
from .JFunctionSignatureValidation import JFunctionSignatureValidation


class JFunction(JFunctionCallable, JFunctionSignatureValidation):

    function: "JFunctionCallable"
    signature: Optional["Signature"]
    function_name: Optional[str]

    def __init__(self, function, signature):
        from ..Signature.Signature import Signature

        self.function = function
        if signature is not None:
            # use classname as default, gets overwritten once the function is registered
            self.signature = Signature(signature, str(type(function)))
        else:
            self.signature = None

        self.function_name = None

    def call(
        self, input_item: Optional[Any], args: Optional[Sequence]
    ) -> Optional[Any]:
        return self.function.call(input_item, args)

    def validate(self, args: Optional[Any], context: Optional[Any]) -> Optional[Any]:
        if self.signature is not None:
            return self.signature.validate(args, context)
        else:
            return args

    def get_number_of_args(self) -> int:
        return 0
