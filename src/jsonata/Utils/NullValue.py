"""
NullValue module for Jsonata Python implementation.
Defines the NullValue class, representing a JSONata null value.
"""


class NullValue:
    """
    Represents a JSONata null value for use in expression evaluation.
    Provides a string representation for display and debugging.
    """

    def __repr__(self):
        """
        Return the string representation of NullValue.
        Returns:
            The string "null".
        """
        return "null"
