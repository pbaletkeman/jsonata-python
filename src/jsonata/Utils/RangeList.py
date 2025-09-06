from src.jsonata.Utils.Utils import Utils


class RangeList(list):
    a: int
    b: int
    size: int

    def __init__(self, left, right):
        """
        Initialize a RangeList from left to right (inclusive).
        """
        super().__init__()
        self.a = left
        self.b = right
        self.size = self.b - self.a + 1

    def __len__(self):
        """
        Return the size of the RangeList.
        """
        return self.size

    def __getitem__(self, index):
        """
        Get the item at the given index in the RangeList.
        """
        if index < self.size:
            return Utils.convert_number(self.a + index)
        raise IndexError(index)

    def __iter__(self):
        """
        Iterate over the RangeList.
        """
        return iter(range(self.a, self.b))
