from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Token:
    type: Optional[str]
    value: Optional[Any]
    position: int
    id: Optional[Any] = None
