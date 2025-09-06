import decimal
import json

from src.jsonata.Utils.Utils import Utils
from src.jsonata.Parser import Parser
from src.jsonata.Jsonata.JFunction import JFunction


class Encoder(json.JSONEncoder):
    def encode(self, o):
        if not isinstance(o, bool) and isinstance(o, (int, float)):
            d = decimal.Decimal(o)
            from src.jsonata.Functions.Functions import Functions

            res = Functions.remove_exponent(d, decimal.Context(prec=15))
            return str(res).lower()

        return super().encode(o)

    def default(self, o):

        if o is Utils.NULL_VALUE:
            return None

        if isinstance(o, (JFunction, Parser.Symbol)):
            return ""

        return super().default(o)
