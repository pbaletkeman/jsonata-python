from src.jsonata.Utils.Utils import Utils


class RangeList(list):
    """
    Represents a list-like range from a to b (inclusive) for use in Jsonata expressions.
    Supports indexing and length operations.
    """

    a: int
    b: int
    size: int

    def __init__(self, left, right):
        """
        Initialize a RangeList from left to right (inclusive).
        Args:
            left: Start of the range.
            right: End of the range (inclusive).
        """
        super().__init__()
        self.a = left
        self.b = right
        self.size = self.b - self.a + 1

    def __len__(self):
        """
        Return the size of the RangeList.
        Returns:
            The number of elements in the range.
        """
        return self.size

    def __getitem__(self, index):
        """
        Get the item at the given index in the RangeList.
        Args:
            index: Index of the item.
        Returns:
            The value at the given index.
        """
        if index < self.size:
            return Utils.convert_number(self.a + index)
        raise IndexError(index)

    def __iter__(self):
        """
        Iterate over the RangeList.
        Returns:
            An iterator over the range.
        """
        return iter(range(self.a, self.b))
