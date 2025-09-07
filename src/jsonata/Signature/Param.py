# pylint: disable=locally-disabled, multiple-statements, fixme, line-too-long

"""
This module defines the Param class for representing parameters in function signatures for the JSONata parser.
It provides attributes and methods for parameter type, regex, context, array status, and subtype, supporting signature validation.
"""


from typing import Optional


class Param:
    """
    Represents a parameter in a function signature.
    Attributes:
        type: The type of the parameter.
        regex: The regex pattern for the parameter type.
        context: Whether the parameter is a context parameter.
        array: Whether the parameter is an array type.
        subtype: The subtype for parameterized types.
        context_regex: Regex for context parameter.
    """

    type: Optional[str]
    regex: Optional[str]
    context: bool
    array: bool
    subtype: Optional[str]
    context_regex: Optional[str]

    def __init__(self):
        """
        Initialize a Param object with default values.
        """
        self.type = None
        self.regex = None
        self.context = False
        self.array = False
        self.subtype = None
        self.context_regex = None

    def __repr__(self):
        """
        Return a string representation of the Param object.
        Returns:
            A string describing the parameter.
        """
        return (
            "Param "
            + str(self.type)
            + " regex="
            + str(self.regex)
            + " ctx="
            + str(self.context)
            + " array="
            + str(self.array)
        )
