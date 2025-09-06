import decimal
import json

from Utils.Utils import Utils
from Functions import Functions
from Jsonata import Jsonata
from Parser import Parser
from Jsonata.JFunction import JFunction


class Encoder(json.JSONEncoder):
    def encode(self, arg):
        if not isinstance(arg, bool) and isinstance(arg, (int, float)):
            d = decimal.Decimal(arg)
            res = Functions.remove_exponent(d, decimal.Context(prec=15))
            return str(res).lower()

        return super().encode(arg)

    def default(self, arg):

        if arg is Utils.NULL_VALUE:
            return None

        if isinstance(arg, (JFunction, Parser.Symbol)):
            return ""

        return super().default(arg)
