from collections.abc import Callable
from typing import Any, MutableMapping, Optional
from src.jsonata.Timebox import Timebox
from src.jsonata.Utils.Utils import Utils


class Frame:
    bindings: MutableMapping[str, Any]
    parent: Optional["Frame"]
    is_parallel_call: bool

    def __init__(self, parent):
        self.bindings = {}
        self.parent = parent
        self.is_parallel_call = False

    def bind(self, name: str, val: Optional[Any]) -> None:
        self.bindings[name] = val
        if getattr(val, "signature", None) is not None:
            val.signature.set_function_name(name)

    def lookup(self, name: str) -> Optional[Any]:
        # Important: if we have a null value,
        # return it
        val = self.bindings.get(name, Utils.NONE)
        if val is not Utils.NONE:
            return val
        if self.parent is not None:
            return self.parent.lookup(name)
        return None

    #
    # Sets the runtime bounds for this environment
    #
    # @param timeout Timeout in millis
    # @param maxRecursionDepth Max recursion depth
    #
    def set_runtime_bounds(self, timeout: int, max_recursion_depth: int) -> None:
        Timebox(self, timeout, max_recursion_depth)

    def set_evaluate_entry_callback(self, cb: Callable) -> None:
        self.bind("__evaluate_entry", cb)

    def set_evaluate_exit_callback(self, cb: Callable) -> None:
        self.bind("__evaluate_exit", cb)
