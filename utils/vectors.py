from enum import Enum
from math import atan2


class Vector2D(object):
    """A 2-dimensional vector."""

    # Vector2D Initialisation
    def __init__(self, x: int | float, y: int | float) -> None:
        """Initialises an instance of a Vector2D. The x- and y-coordinates can be either integers or floats."""
        self.x = x
        self.y = y

    # Vector2D Properties
    @property
    def length(self) -> int | float:
        """The length, or magnitude, the vector."""
        return (self.x ** 2 + self.y ** 2) ** 0.5

    @property
    def length_squared(self) -> int | float:
        """The length, or magnitude, of the vector, squared. Using this is faster than the normal length, as this avoids having to calculate the square root of the result."""
        return self.x ** 2 + self.y ** 2

    @property
    def unit_vector(self) -> Vector2D:
        """The unit vector (a vector of length one) of the vector."""
        length: float = self.length

        # If the length is 0, trying to divide by the length would result in a ZeroDivisionError.
        # This if-statement is in place to prevent this.
        if length == 0:
            return Vector2D(0, 0)
        return Vector2D(self.x / length, self.y / length)

    @property
    def angle(self) -> float:
        """The angle (in this case, the arc tangent) of the vector, measured in radians."""
        return atan2(self.y, self.x)

    # Vector2D String Representation
    def __str__(self) -> str:
        return f"Vector2D({self.x}, {self.y})"

    def __repr__(self) -> str:
        return f"Vector2D({self.x}, {self.y})"

    # Vector2D Iteration
    def __iter__(self):
        """Used specifically for when conversion to tuples are necessary."""
        yield self.x
        yield self.y

    # Vector2D Arithmetic
    def __add__(self, other: Vector2D) -> Vector2D:
        """The x- and the y-coordinates of the two vectors are each added together to create a new vector."""
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vector2D) -> Vector2D:
        """The x- and y-coordinates of the second vector is subtracted from the second vector to create a new vector."""
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: int | float) -> Vector2D:
        """The x- and y-coordinates of the vector are multiplied by a scalar quantity (a number that can either be an integer or float) to create a new vector."""
        return Vector2D(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar: int | float) -> Vector2D:
        """The x- and y-coordinates of the vector are divided by a scalar quantity (a number that can either be an integer or float) to create a new vector."""
        return Vector2D(self.x / scalar, self.y / scalar)

    # Vector2D In-place Arithmetic
    def __iadd__(self, other: Vector2D) -> Vector2D:
        """The x- and the y-coordinates of the two vectors are each added together to create a new vector."""
        self.x += other.x
        self.y += other.y
        return self

    def __isub__(self, other: Vector2D) -> Vector2D:
        """The x- and y-coordinates of the second vector is subtracted from the second vector to create a new vector."""
        self.x -= other.x
        self.y -= other.y
        return self

    def __imul__(self, scalar: int | float) -> Vector2D:
        """The x- and y-coordinates of the vector are multiplied by a scalar quantity (a number that can either be an integer or float) to create a new vector."""
        self.x *= scalar
        self.y *= scalar
        return self

    def __itruediv__(self, scalar: int | float) -> Vector2D:
        """The x- and y-coordinates of the vector are divided by a scalar quantity (a number that can either be an integer or float) to create a new vector."""
        self.x /= scalar
        self.y /= scalar
        return self

    # Vector2D Comparison
    def __eq__(self, other: Vector2D) -> bool:
        """Checks to see if the x- and y-coordinates of each vector are the same."""
        return self.x == other.x and self.y == other.y

    def __ne__(self, other: Vector2D) -> bool:
        """Checks to see if the x- and y-coordinates of each vector are not the same."""
        return not self.__eq__(other)


class FloorPosition(Vector2D):
    """A subclass of Vector2D used for positions on a floor's grid. Essentially, they're a vector that can only have integers as x- and y-coordinates."""

    def __init__(self, x: int, y: int) -> None:
        """Initialises an instance of a Vector2D. The x- and y-coordinates can only be an integer."""
        super().__init__(x, y)

    # FloorPosition Methods
    def get_adjacent_positions(self) -> list[FloorPosition]:
        return [self + direction.value for direction in CardinalDirections]

    def get_direction_to(self, other: FloorPosition) -> str:
        delta: FloorPosition = other - self

        try:
            return CardinalDirections(delta.unit_vector).name
        except ValueError:
            print(self, other)
            print(delta, delta.unit_vector)
            raise Exception("Direction not one of the four cardinal directions.")

    # FloorPosition String Representation Overrides
    def __str__(self) -> str:
        return f"FloorPosition({self.x}, {self.y})"

    def __repr__(self) -> str:
        return f"FloorPosition({self.x}, {self.y})"

    # FloorPosition Arithmetic Overrides
    def __add__(self, other: FloorPosition) -> FloorPosition:
        return FloorPosition(self.x + other.x, self.y + other.y)

    def __sub__(self, other: FloorPosition) -> FloorPosition:
        return FloorPosition(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: int) -> FloorPosition:
        return FloorPosition(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar: int) -> FloorPosition:
        return FloorPosition(self.x // scalar, self.y // scalar)

    # FloorPosition In-place Arithmetic Overrides
    def __iadd__(self, other: FloorPosition) -> FloorPosition:
        self.x += other.x
        self.y += other.y
        return self

    def __isub__(self, other: FloorPosition) -> FloorPosition:
        self.x -= other.x
        self.y -= other.y
        return self

    def __imul__(self, scalar: int) -> FloorPosition:
        self.x *= scalar
        self.y *= scalar
        return self

    def __itruediv__(self, scalar: int) -> FloorPosition:
        self.x //= scalar
        self.y //= scalar
        return self


class CardinalDirections(Enum):
    """Represents the cardinal directions in Floor Position vectors."""
    NORTH = FloorPosition(0, -1)
    EAST = FloorPosition(1, 0)
    SOUTH = FloorPosition(0, 1)
    WEST = FloorPosition(-1, 0)


# Vector2D Testing
"""
A = Vector2D(0, 1)
B = Vector2D(1, 0)

print(A + B)
print(A - B)
print(A * 2)
print(A / 2)
print(A.length)
print(A.length_squared)
print(A.angle)
"""

# FloorPosition Testing
"""
C = FloorPosition(2, 3)
D = FloorPosition(2, 4)
print(C)
print(C + FloorPosition(1, 1))
print(C - FloorPosition(1, 1))
print(C * 2)
print(C / 2)
print(C.get_direction_to(D))
"""
