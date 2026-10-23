from pytmx import TiledMap

from utils.vectors import FloorPosition


class Room(object):
    """Represents a room on a floor."""

    # Room Initialisation
    def __init__(self, position: FloorPosition, category: str = "RSR", index: str = "000") -> None:
        """Initialises an instance of a room on a floor.

        :param position: The position of the room on the floor.
        :param category: (optional) The category of the room. Will default to RSR if none is provided.
        :param index: (optional) The index of the room. Will default to 000 if none is provided."""

        self.position = position
        """The position of the room on the floor."""
        self.doors: list[Door] = []
        """The doors of the room."""

        self.category = category
        """The category of the room."""
        self.index = index
        """The index of the room."""

        self.locked: bool = False
        """Whether or not the room is locked."""

        self.tmx_data: TiledMap | None = None
        """The TMX data assigned to the room. Defaults to None, as the default ID
        (RSR_000) is not a real room."""

    # Room Properties
    @property
    def id(self) -> str:
        """The ID of the room."""
        return f"{self.category}_{self.index}"

    @property
    def reserved(self) -> bool:
        """Whether or not the room is reserved. RSR_000 means that this is currently
         not a real room, while RSR_001 means that the room will become a real room
         once generation is finished."""
        return self.id in {"RSR_000", "RSR_001"}

    @property
    def door_count(self) -> int:
        """The number of doors in the room."""
        return len(self.doors)

    @property
    def connections(self) -> list[Room]:
        """Every room this room is connected with."""
        return [door.to for door in self.doors]

    # Room String Representation
    def __str__(self) -> str:
        return f"Room({self.position}, {self.id})"

    def __repr__(self) -> str:
        return f"Room({self.position}, {self.id})"

    # Room Equality
    def __eq__(self, other: Room) -> bool:
        return isinstance(other, Room) and self.position == other.position

    def __ne__(self, other: Room) -> bool:
        return not self.__eq__(other)

    # Room Methods
    def connect_rooms(self, other: Room) -> None:
        """Connects a room to another room.

        :param other: The room to connect to this one."""

        self.doors.append(Door(self, other))
        other.doors.append(Door(other, self))
        self.doors[-1].connected_to = other.doors[-1]
        other.doors[-1].connected_to = self.doors[-1]

    def is_connected(self, other: Room) -> bool:
        """Checks if a room is connected to this one."""
        return other in self.connections

    def lock(self) -> None:
        """Locks the room and its doors."""
        self.locked = True
        for door in self.doors:
            door.locked = True
            door.connected_to.locked = True


class Door(object):
    """Represents a door on a floor."""

    # Door Initialisation
    def __init__(self, fr: Room, to: Room) -> None:
        self.fr = fr
        """The room that this door is from."""
        self.to = to
        """The room that this door goes to."""
        self.connected_to: Door
        """The door this door is connected to."""

        self.locked: bool = False
        """Whether or not the door is locked."""

    # Door Properties
    @property
    def direction(self) -> str:
        """The direction of the door."""
        return self.fr.position.get_direction_to(self.to.position)

    # Door String Representation
    def __str__(self) -> str:
        return f"Door({self.fr}, {self.to})"

    def __repr__(self) -> str:
        return f"Door({self.fr}, {self.to})"
