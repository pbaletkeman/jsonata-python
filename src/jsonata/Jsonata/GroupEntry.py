# pylint: disable=locally-disabled, multiple-statements, fixme, line-too-long

"""
GroupEntry module for Jsonata Python implementation.
Defines the GroupEntry dataclass for grouping operations in Jsonata expressions.
"""


from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class GroupEntry:
    """
    Represents a group entry for grouping operations in JSONata.
    Attributes:
        data: The grouped data.
        exprIndex: The index of the expression that generated this group.
    """

    data: Optional[Any]
    exprIndex: int
