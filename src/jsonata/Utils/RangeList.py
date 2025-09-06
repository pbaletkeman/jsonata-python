from ..Utils.Utils import Utils


class RangeList(list):
    a: int
    b: int
    size: int

    def __init__(self, left, right):
        super().__init__()
        self.a = left
        self.b = right
        self.size = self.b - self.a + 1

    def __len__(self):
        return self.size

    def __getitem__(self, index):
        if index < self.size:
            return Utils.convert_number(self.a + index)
        raise IndexError(index)

    def __iter__(self):
        return iter(range(self.a, self.b))
