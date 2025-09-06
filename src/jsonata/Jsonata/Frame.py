from collections.abc import Callable
from typing import Any, MutableMapping, Optional
from src.jsonata.Timebox import Timebox
from src.jsonata.Utils.Utils import Utils


class Frame:
    """
    Represents an environment frame for variable bindings and scope management in JSONata.
    """

    bindings: MutableMapping[str, Any]
    parent: Optional["Frame"]
    is_parallel_call: bool

    def __init__(self, parent):
        """
        Initialize a Frame object.
        Args:
            parent: The parent Frame instance.
        """
        self.bindings = {}
        self.parent = parent
        self.is_parallel_call = False

    def bind(self, name: str, val: Optional[Any]) -> None:
        """
        Bind a value to a variable name in the frame.
        Args:
            name: The variable name.
            val: The value to bind.
        """
        self.bindings[name] = val
        if getattr(val, "signature", None) is not None:
            val.signature.set_function_name(name)

    def lookup(self, name: str) -> Optional[Any]:
        """
        Lookup a variable value by name, searching parent frames if necessary.
        Args:
            name: The variable name to look up.
        Returns:
            The value bound to the name, or None if not found.
        """
        val = self.bindings.get(name, Utils.NONE)
        if val is not Utils.NONE:
            return val
        if self.parent is not None:
            return self.parent.lookup(name)
        return None

    def set_runtime_bounds(self, timeout: int, max_recursion_depth: int) -> None:
        """
        Set the runtime bounds for this environment.
        Args:
            timeout: Timeout in milliseconds.
            max_recursion_depth: Maximum recursion depth.
        """
        Timebox(self, timeout, max_recursion_depth)

    def set_evaluate_entry_callback(self, cb: Callable) -> None:
        """
        Set the callback to be called on entry to evaluation.
        Args:
            cb: The callback function.
        """
        self.bind("__evaluate_entry", cb)

    def set_evaluate_exit_callback(self, cb: Callable) -> None:
        """
        Set the callback to be called on exit from evaluation.
        Args:
            cb: The callback function.
        """
        self.bind("__evaluate_exit", cb)
