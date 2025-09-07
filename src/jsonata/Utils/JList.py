"""
JList module for Jsonata Python implementation.
Defines the JList class, a specialized list with flags for Jsonata evaluation semantics.
"""


class JList(list):
    """
    Specialized list for Jsonata evaluation, supporting flags for sequence, tuple streams, singleton handling, and construction semantics.
    Extends Python's built-in list with additional attributes used during expression evaluation.
    """

    sequence: bool
    outer_wrapper: bool
    tuple_stream: bool
    keep_singleton: bool
    cons: bool

    def __init__(self, c=()):
        """
        Initialize JList and set Jsonata specific flags.
        Args:
            c: Iterable to initialize the list.
        """
        super().__init__(c)
        self.sequence = False
        self.outer_wrapper = False
        self.tuple_stream = False
        self.keep_singleton = False
        self.cons = False
