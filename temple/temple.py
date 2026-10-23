from temple.floor import Floor


class Temple(object):
    """Represents the temple itself."""

    # Temple Initialisation
    def __init__(self) -> None:
        """Initialises the temple."""

        self.floor_number: int = 0
        """How many floors deep the player is currently."""
        self.floors: list[Floor] = list()
        """All the floors of the temple."""

    # Floor Properties
    @property
    def current_floor(self) -> Floor:
        """The current floor the player is on."""
        return self.floors[self.floor_number - 1]

    # Temple Methods
    def generate_floor(self) -> None:
        """Generates a floor of the temple."""
        width: int = 5 + (self.floor_number // 2) * 2
        height: int = 5 + (self.floor_number // 2) * 2
        min_rooms: int = (6 + (self.floor_number ** 1.5) - (self.floor_number - 1)) ** 1.25
        max_rooms: int = (8 + (self.floor_number ** 1.5) + (self.floor_number - 1)) ** 1.25

        self.floors.append(Floor(width, height, min_rooms, max_rooms))
        self.floor_number += 1
