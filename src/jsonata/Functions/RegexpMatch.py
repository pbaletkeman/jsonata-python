# pylint: disable=locally-disabled, multiple-statements, fixme, line-too-long

"""
RegexpMatch module for Jsonata Python implementation.
Defines the RegexpMatch dataclass, representing the result of a regular expression match, including the matched substring, index, and captured groups.
"""


from dataclasses import dataclass
from typing import AnyStr, Sequence


@dataclass
class RegexpMatch:
    """
    Represents a regular expression match result.
    Fields:
        match (str): The matched substring.
        index (int): The start index of the match in the input string.
        groups (Sequence[AnyStr]): The captured groups from the match.
    """

    match: str
    index: int
    groups: Sequence[AnyStr]
