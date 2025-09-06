from dataclasses import dataclass
from typing import AnyStr, Sequence


@dataclass
class RegexpMatch:
    match: str
    index: int
    groups: Sequence[AnyStr]
