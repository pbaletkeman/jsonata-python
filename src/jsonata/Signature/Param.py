from typing import Optional


class Param:

    type: Optional[str]
    regex: Optional[str]
    context: bool
    array: bool
    subtype: Optional[str]
    context_regex: Optional[str]

    def __init__(self):
        self.type = None
        self.regex = None
        self.context = False
        self.array = False
        self.subtype = None
        self.context_regex = None

    def __repr__(self):
        return (
            "Param "
            + self.type
            + " regex="
            + self.regex
            + " ctx="
            + str(self.context)
            + " array="
            + str(self.array)
        )
