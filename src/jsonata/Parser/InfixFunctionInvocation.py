from src.jsonata.Parser.Infix import Infix
from src.jsonata.Parser.Parser import Parser
from src.jsonata.JException.JException import JException
from src.jsonata.Signature import Signature


class InfixFunctionInvocation(Infix):
    _outer_instance: "Parser"

    def __init__(self, outer_instance, get):
        super().__init__(outer_instance, "(", get)
        self._outer_instance = outer_instance

    def led(self, left):
        """
        Handles the left denotation for the function invocation operator (().
        Sets up procedure, arguments, and handles lambda function definitions and signatures.
        Args:
            left: The left operand (function to invoke).
        Returns:
            InfixFunctionInvocation: The updated instance.
        """
        self.procedure = left
        self.type = "function"
        self.arguments = []
        if self._outer_instance.node.id != ")":
            while True:
                if (
                    "operator" == self._outer_instance.node.type
                    and self._outer_instance.node.id == "?"
                ):
                    # partial function application
                    self.type = "partial"
                    self.arguments.append(self._outer_instance.node)
                    self._outer_instance.advance("?")
                else:
                    self.arguments.append(self._outer_instance.expression(0))
                if self._outer_instance.node.id != ",":
                    break
                self._outer_instance.advance(",")
        self._outer_instance.advance(")", True)
        # if the name of the function is 'function' or λ, then this is function definition (lambda function)
        if left.type == "name" and (left.value == "function" or left.value == "\u03bb"):
            # all of the args must be VARIABLE tokens
            for arg in self.arguments:
                if arg.type != "variable":
                    return self._outer_instance.handle_error(
                        JException("S0208", arg.position, arg.value)
                    )
            self.type = "lambda"
            # is the next token a '<' - if so, parse the function signature
            if self._outer_instance.node.id == "<":
                depth = 1
                sig = "<"
                while (
                    depth > 0
                    and self._outer_instance.node.id != "{"
                    and self._outer_instance.node.id != "(end)"
                ):
                    tok = self._outer_instance.advance()
                    if tok.id == ">":
                        depth -= 1
                    elif tok.id == "<":
                        depth += 1
                    sig += tok.value
                self._outer_instance.advance(">")
                self.signature = Signature(sig, "lambda")
            # parse the function body
            self._outer_instance.advance("{")
            self.body = self._outer_instance.expression(0)
            self._outer_instance.advance("}")
        return self

    # })

    # parenthesis - block expression
    # Note: in Java both nud and led are in same class!
    # register(new Prefix("(") {

    def nud(self):
        """
        Handles the null denotation for the parenthesis operator (block expression).
        Collects expressions separated by semicolons and sets type to 'block'.
        Returns:
            InfixFunctionInvocation: The updated instance.
        """
        if self._outer_instance.dbg:
            print("Prefix (")
        expressions = []
        while self._outer_instance.node.id != ")":
            expressions.append(self._outer_instance.expression(0))
            if self._outer_instance.node.id != ";":
                break
            self._outer_instance.advance(";")
        self._outer_instance.advance(")", True)
        self.type = "block"
        self.expressions = expressions
        return self
