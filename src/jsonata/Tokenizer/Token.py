from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Token:
    """
    Represents a token in the JSONata tokenizer.
    Attributes:
        type: The type of the token (e.g., operator, regex, etc.).
        value: The value of the token.
        position: The position of the token in the input string.
        id: Optional identifier for the token.
    """

    type: Optional[str]
    value: Optional[Any]
    position: int
    id: Optional[Any] = None
