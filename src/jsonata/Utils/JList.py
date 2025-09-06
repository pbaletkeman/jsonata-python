class JList(list):
    sequence: bool
    outer_wrapper: bool
    tuple_stream: bool
    keep_singleton: bool
    cons: bool

    def __init__(self, c=()):
        """
        Initialize JList and set Jsonata specific flags.
        """
        super().__init__(c)
        self.sequence = False
        self.outer_wrapper = False
        self.tuple_stream = False
        self.keep_singleton = False
        self.cons = False
