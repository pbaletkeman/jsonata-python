"""
Encoder module for JSONata Python implementation.
Provides a custom JSON encoder for handling decimals and special types in JSONata expressions.
"""

import decimal
import json

from src.jsonata.Utils.Utils import Utils
from src.jsonata.Parser import Parser
from src.jsonata.Jsonata.JFunction import JFunction


class Encoder(json.JSONEncoder):
    """
    Custom JSON encoder for Jsonata, handling decimals and special types.
    """

    def encode(self, o):
        """
        Encode an object, handling decimals and numbers specially.
        Args:
            o: Object to encode.
        Returns:
            str: Encoded JSON string.
        """
        if not isinstance(o, bool) and isinstance(o, (int, float)):
            d = decimal.Decimal(o)
            from src.jsonata.Functions.Functions import Functions

            res = Functions.remove_exponent(d, decimal.Context(prec=15))
            return str(res).lower()

        return super().encode(o)

    def default(self, o):
        """
        Provide a default encoding for special Jsonata types.
        Args:
            o: Object to encode.
        Returns:
            Any: Encoded value for JSON.
        """
        if o is Utils.NULL_VALUE:
            return None

        if isinstance(o, (JFunction, Parser.Symbol)):
            return ""

        return super().default(o)
