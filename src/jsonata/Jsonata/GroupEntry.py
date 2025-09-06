from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class GroupEntry:
    data: Optional[Any]
    exprIndex: int
