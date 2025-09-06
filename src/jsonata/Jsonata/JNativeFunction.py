import inspect
from typing import Any, Optional, Sequence
from src.jsonata.Jsonata.JFunction import JFunction
from src.jsonata.Signature.Signature import Signature


class JNativeFunction(JFunction):
    function_name: str
    signature: Optional[Signature]
    clz: Any
    method: Optional[Any]
    nargs: int

    def __init__(self, function_name, signature, clz, impl_method_name):
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

    def call(self, input_: Optional[Any], args: Optional[Sequence]) -> Optional[Any]:
        from src.jsonata.Functions.Functions import Functions

        # input_ is unused, but kept for signature compatibility
        return Functions.call(self.method, self.nargs, args)

    def get_number_of_args(self) -> int:
        return self.nargs
