class int2:
    """ Basic coordinate data structure, includes mathematical operations"""
    x: int
    y: int

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __str__(self):
        return f"({self.x},{self.y})"

    def __add__(self, other):
        return int2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return int2(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return int2(self.x * other.x, self.y * other.y)

    def __truediv__(self, other):
        return int2(self.x / other.x, self.y / other.y)

    def __floordiv__(self, other):
        return int2(self.x // other.x, self.y // other.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return self.x != other.x or self.y != other.y
