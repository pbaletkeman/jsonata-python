from collections.abc import Sequence
from typing import Any, Callable, Optional

from .JFunctionCallable import JFunctionCallable
from .JFunctionSignatureValidation import JFunctionSignatureValidation


class JLambda(JFunctionCallable, JFunctionSignatureValidation):
    function: Callable

    def __init__(self, function):
        self.function = function

    def call(self, input: Optional[Any], args: Optional[Sequence]) -> Optional[Any]:
        if isinstance(args, list):
            return self.function(*args)
        else:
            return self.function()

    def validate(self, args: Optional[Any], context: Optional[Any]) -> Optional[Any]:
        return args
