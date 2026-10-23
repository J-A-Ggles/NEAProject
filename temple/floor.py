import random
from copy import deepcopy

from temple.room import *
from temple.tiled_maps import assign_room
from utils.vectors import CardinalDirections


class Floor(object):
    """Represents a floor of the temple."""

    # Floor Initialisation
    def __init__(self, width: int, height: int, min_rooms: int,
                 max_rooms: int) -> None:
        """Initialises a new instance of the Floor class.

        :param width: The width of the floor, in rooms.
        :param height: The height of the floor, in rooms.
        :param min_rooms: The minimum number of rooms the floor should contain. If the floor contains less than this many rooms during generation, it will reset.
        :param max_rooms: The maximum number of rooms the floor should contain. If the floor contains more than this many rooms during generation, it will reset."""

        # Floor Generation Parameters
        self.width = width
        """The width of the floor, in rooms."""
        self.height = height
        """The height of the floor, in rooms."""

        self.min_rooms = min_rooms
        """The minimum number of rooms the floor should contain."""
        self.max_rooms = max_rooms
        """The maximum number of rooms the floor should contain."""

        # Floor Layout
        self.initial_layout: list[list[Room]] = [[Room(FloorPosition(x, y)) for x in range(self.width)] for y in
                                                 range(self.height)]
        """The initial layout of the floor, comprised solely of
        RSR_000 rooms to act as placeholders."""

        self.layout: list[list[Room]] = list(list())
        """What is actually used to access the layout of the floor.
        These variables are separate so that, if generation is to fail
        and restart, the initial layout does not need to be remade."""

        self.centre: FloorPosition = FloorPosition(self.width // 2, self.height // 2)
        """The centre of the floor."""
        self.boss_room: Room | None = None
        """The floor's boss room. Is None until a boss room is generated."""
        self.item_room: Room | None = None
        """The floor's item room. Is None until an item room is generated."""

        # Miscellaneous
        self.iterations: int = 0
        """How many iterations it took to generate the floor."""

        while len(self) < self.min_rooms:
            self.iterations += 1
            self.layout = deepcopy(self.initial_layout)
            self.generate_layout()

    # Floor Properties
    @property
    def rooms(self) -> list[Room]:
        """Every valid room (rooms that aren't RSR_000) on the floor."""
        return [room for row in self.layout for room in row if room.id != "RSR_000"]

    @property
    def starting_room(self) -> Room:
        """The room the player starts in on the floor. This is always the centre room of the floor."""
        return self[self.centre]

    @property
    def important_rooms(self) -> list[Room | None]:
        """Any room that is important to the floor. This includes:

        * The starting room
        * The boss room
        * The item room."""
        return [self.starting_room, self.boss_room, self.item_room]

    @property
    def normal_rooms(self) -> list[Room]:
        """Any room not included in the list of important rooms."""
        return [room for room in self.rooms if room not in self.important_rooms]

    # Floor String Representation
    def __str__(self) -> str:
        """Displays the layout of the floor in the console in three different ways:

        * IDs: Displays the layout in a grid, using each room's ID.
        * Letter: Displays the layout in a grid, using a letter corresponding to the room's category.
        * Connections: Displays each room in order and which rooms they connect to."""
        id_layout = "\n".join(["\t".join([room.id for room in row]) for row in self.layout])
        letter_layout = "\n".join([" ".join(
            [
                "R" if room.id == "RSR_001" else "N" if room.category == "NRM" else "B" if room.category == "BSS" else "I" if room.category == "ITM" else "X"
                for room in row]) for row in self.layout])
        connections = "\n".join([f"{room} connected to {", ".join([str(door.to) for door in room.doors])}" for room in
                                 self.sorted_rooms(lambda room: (room.position.y, room.position.x))])

        return f"ID Layout:\n{id_layout}\n\nLetter Layout:\n{letter_layout}\n\nRoom Connections:\n{connections}"

    # Because the floor is meant to be a grid of rooms, accessors
    # and iterator have been made to access the layout itself.

    # Floor Iterators
    def __iter__(self) -> Floor:
        self.current_index: int = 0
        return self

    def __next__(self) -> Room:
        if self.current_index < len(self):
            room: Room = self.rooms[self.current_index]
            self.current_index += 1
            return room
        else:
            raise StopIteration

    def __len__(self) -> int:
        """The number of rooms on the floor."""
        return len(self.rooms)

    # Floor Getters and Setters
    def __getitem__(self, position: FloorPosition) -> Room:
        """Gets the specified room from the layout.

        :arg position: The position of the room within the grid.
        :return: The room at the specified position.
        :raises IndexError: If the position is out-of-bounds."""
        if self.is_in_bounds(position):
            return self.layout[position.y][position.x]
        else:
            raise IndexError

    def __setitem__(self, position: FloorPosition, room: Room) -> None:
        """Sets the specified room from the layout.

        :arg position: The position of the room within the grid.
        :raises IndexError: If the position is out-of-bounds."""
        if self.is_in_bounds(position):
            self.layout[position.y][position.x] = room
        else:
            raise IndexError

    # Floor Methods
    def is_in_bounds(self, position: FloorPosition) -> bool:
        """Checks if the position is in the bounds of the floor.

        :returns: True if the position is in the bounds of the floor; returns false otherwise."""
        return (0 <= position.x < self.width) and (0 <= position.y < self.height)

    def is_dead_end(self, room: Room) -> bool:
        """Checks is the room is a dead-end.

        :returns: True if the room is a dead end; returns false otherwise."""
        return all([bool(room.door_count != 1) for room in self.get_adjacent_rooms(room)])

    def get_adjacent_rooms(self, room: Room) -> list[Room]:
        """Gets a list of the rooms (that aren't RSR_000) adjacent to the given one.

        :arg room: The room to get adjacent rooms from.
        :returns: A list of the rooms adjacent to the given one."""
        rooms: list[Room] = []
        adjacent_positions: list[FloorPosition] = room.position.get_adjacent_positions()

        for adjacent_position in adjacent_positions:
            if self.is_in_bounds(adjacent_position) and self[adjacent_position].id != "RSR_000":
                rooms.append(self[adjacent_position])
        return rooms

    def num_adjacent_rooms(self, room: Room) -> int:
        """The number of rooms (that aren't RSR_000) adjacent to the given one.

        :arg room: The room to get adjacent rooms from.
        :returns: The number of rooms adjacent to the given one."""
        return len(self.get_adjacent_rooms(room))

    def get_adjacent_unoccupied(self, room: Room) -> list[Room]:
        """Gets a list of unoccupied rooms (rooms that are RSR_000) adjacent to the given one.

        :arg room: The room to get adjacent unoccupied rooms from.
        :returns: A list of the unoccupied rooms adjacent to the given one."""
        rooms: list[Room] = []
        adjacent_positions: list[FloorPosition] = room.position.get_adjacent_positions()

        for adjacent_position in adjacent_positions:
            if self.is_in_bounds(adjacent_position) and self[adjacent_position].id == "RSR_000":
                rooms.append(self[adjacent_position])
        return rooms

    def get_adjacent_unoccupied_count(self, room: Room) -> int:
        """The number of unoccupied rooms (rooms that are RSR_000) adjacent to the given one.

        :arg room: The room to get adjacent unoccupied rooms from.
        :returns: The number of unoccupied rooms adjacent to the given one."""
        return len(self.get_adjacent_unoccupied(room))

    def get_distance(self, room: Room, other: Room | None = None, squared: bool = True) -> int | float:
        """Gets the distance between the specified position and the centre of the floor.

        :arg room: The room to get distance from.
        :arg other: (optional) The other room to get distance from. Will default to the starting room if none is specified.
        :arg squared: (optional) If True, returns the squared distance between the specified position and the centre of the floor; returns the normal distance otherwise.
        :returns: The distance between the specified position and the centre of the floor."""
        if not other:
            other = self.starting_room

        if squared:
            return (room.position - other.position).length_squared
        else:
            return (room.position - other.position).length

    def sorted_rooms(self, key):
        """Takes a key and returns a list of all the rooms in the floor sorted based on that key.

        :param key: The key to sort the rooms by.
        :return: A sorted list of rooms.
        """
        return sorted(self.rooms, key=key)

    def generate_boss_room(self) -> bool:
        """Finds a location for the boss room, then assigns that room TMX data.

        :returns: A boolean indicating whether a potential boss room was found or not."""

        # A boss room can only have one room connected to it, and must have at least
        # one unoccupied room adjacent to it.
        potential_boss_rooms: list[Room] = [room for room in self.normal_rooms if
                                            room.door_count == 1 and self.get_adjacent_unoccupied_count(
                                                room) >= 1]

        """
        I originally had plans to make it so that, if a room such as the boss room
        was not found, then it would attempt to add a new room. However, I realised
        that this would be far more over-complicated and most likely waste time over
        simply regenerating a new floor, especially since testing showed that the
        number of times a floor would have to be regenerated after a failed generation
        was low.
        
        if potential_boss_rooms:
            furthest_distance: float = max(self.get_distance(room.position) for room in potential_boss_rooms)
            furthest_rooms: list[Room] = [room for room in potential_boss_rooms if self.get_distance(room.position) == furthest_distance]
            self._boss_room = random.choice(furthest_rooms).position
        else:
            considered_rooms: list[Room] = [room for room in self.normal_rooms if room not in self.get_adjacent_rooms(self.centre)]
            rooms_by_dist: list[Room] = sorted(considered_rooms, key = lambda room : -self.get_distance(room.position))
            new_room: FloorPosition | None = None

            for room in rooms_by_dist:
                unoccupied_rooms: list[Room] = self.get_adjacent_rooms(room.position)
                random.shuffle(unoccupied_rooms)
                for unoccupied_room in unoccupied_rooms:
                    if self.get_adjacent_room_count(unoccupied_room.position) == 1:
                        new_room = unoccupied_room.position

            return False
        """

        if not potential_boss_rooms:
            return False

        # A boss room must also be the furthest room away from the centre.

        # Despite type checkers' issue with self.get_distance having the return type of int | float,
        # this will always return an integer, so the problem here does not exist.
        furthest_distance: int = max(self.get_distance(room) for room in potential_boss_rooms)
        furthest_rooms: list[Room] = [room for room in potential_boss_rooms if
                                      self.get_distance(room) == furthest_distance]

        self.boss_room = random.choice(furthest_rooms)
        self.boss_room.category = "BSS"
        return True

    def generate_item_room(self) -> bool:
        """Finds a location for the item room, then assigns that room TMX data.

        :returns: A boolean indicating whether a potential item room was found or not."""

        # An item room can only have, at most, two rooms connected to it; cannot be
        # as far or further away from the boss room is to the centre; and must be
        # a dead-end to a series of rooms.
        potential_item_rooms: list[Room] = [room for room in self.normal_rooms if
                                            room.door_count in {1, 2} and self.get_distance(
                                                room) <= self.get_distance(
                                                self.boss_room) and self.is_dead_end(room)]
        if not potential_item_rooms:
            return False

        self.item_room = random.choice(potential_item_rooms)
        self.item_room.category = "ITM"
        self.item_room.lock()
        return True

    def room_growth(self) -> bool:
        """A room growth algorithm, based on a breadth-first search.
        It starts from the centre of the grid, then continuously generates
        more rooms until either the queue is empty, or the current number
        of rooms would begin to exceed the maximum number of rooms that
        there should be for the floor.

        :return: A boolean indicating whether room growth was successful or not (i.e., if the number of rooms is greater than the minimum number of room that there should be for the floor)."""

        queue: list[FloorPosition] = list()

        queue.append(self.centre)
        self[self.centre] = Room(self.centre, "RSR", "001")

        while queue and len(self) < self.max_rooms:
            current_position: FloorPosition = queue.pop(0)
            adjacent_positions: list[FloorPosition] = current_position.get_adjacent_positions()

            for adjacent_position in adjacent_positions:
                if self.is_in_bounds(adjacent_position) and len(self) < self.max_rooms:
                    # If a space in the grid is not currently occupied by a room,
                    # then a room will potentially generate in the location.
                    if self[adjacent_position].id == "RSR_000":
                        # Room generation is always guaranteed for rooms adjacent to the centre room.
                        # This is so that the player will always be able to pick one of four directions
                        # to go to.
                        room_generation_chance: float = 1.1
                        if current_position not in self.centre.get_adjacent_positions():
                            # If not adjacent to the centre room, then the initial chance of generation
                            # is dependent on the room's distance from the centre.
                            room_generation_chance = 1 / (adjacent_position - self.centre).length

                            # Next, the chance of a room generating will decrease exponentially
                            # if it is part of a straight line of rooms. If it is a bend, then
                            # chance of generation will increase instead.

                            # This is to prevent floors consisting of several long corridors
                            # of rooms and increase the chances of more interesting floor layouts.
                            direction_back = adjacent_position.get_direction_to(current_position)
                            pos = deepcopy(adjacent_position)
                            line = 0
                            while self.is_in_bounds(pos) and (self[
                                                                  pos].id != "RSR_000" or pos == adjacent_position) and pos != self.centre and direction_back is not None:
                                pos += CardinalDirections[direction_back].value
                                line += 1
                            room_generation_chance *= 1.75 / (1.75 ** (line - 2))

                            # Finally, the chance of a room generating will decrease exponentially
                            # if there are already rooms adjacent to it. This is to prevent floors
                            # being "blobby", with several rooms being bunched up next to each other.
                            room_generation_chance *= 1.5 / (
                                    1.5 ** (self.num_adjacent_rooms(self[adjacent_position]) ** 2))

                        if random.random() < room_generation_chance:
                            # If generation is successful, the room will also being connected to
                            # the room that it is adjacent to.
                            queue.append(adjacent_position)
                            self[adjacent_position] = Room(adjacent_position, "RSR", "001")
                            if not self[adjacent_position].is_connected(self[current_position]):
                                self[adjacent_position].connect_rooms(self[current_position])

                    # If the space is occupied, then that room may be connected
                    # to the current position on the grid.
                    else:
                        # The chance of the two rooms being connected is based on the
                        # number of doors the room already has, decreasing the higher
                        # the number of doors already is.

                        # Before this, however, a check is in place to see if the
                        # rooms are already connected. This is to prevent there
                        # being duplicate doors, as this especially causes issues
                        # when assigning TMX data to the room later on.
                        if not self[adjacent_position].is_connected(self[current_position]) and random.random() >= self[
                            adjacent_position].door_count / 4:
                            self[adjacent_position].connect_rooms(self[current_position])

        return len(self) >= self.min_rooms

    def generate_layout(self) -> None:
        """Generates the layout of the floor. If any issues occur during generation, generation will restart."""

        # First, the floor is grown from the centre room. If this fails, generation restarts.
        room_growth_successful = self.room_growth()
        if not room_growth_successful:
            return

        # Next, a boss room is found. If this fails, generation restarts.
        is_boss_room: bool = self.generate_boss_room()
        if not is_boss_room:
            return

        # Next, an item room is found. If this fails, generation restarts.
        is_item_room: bool = self.generate_item_room()
        if not is_item_room:
            return

        # The starting room will always be this room.
        assign_room(self.starting_room, "NRM", "000")

        # For the remaining rooms, a random Normal room is assigned to them.
        # Which room is assigned is random, but is based on the doors and
        # number of them the room has.
        for room in self.normal_rooms:
            print([door for door in room.doors])
            assign_room(room, "NRM")


# Floor Generation Testing
"""
Number of times generated: 1000
Average number of iterations per floor generation: 1.108
Average time per floor generation: 0.0025327125998446717

iterations_each_gen: list[int] = []
time_per_iteration: list[float | int] = []
for x in range(0, 1_000):
    start: int | float = perf_counter()
    _: Floor = Floor( 5,  5, 8, 12)
    end: int | float = perf_counter()
    iterations_each_gen.append(_.iterations)
    time_per_iteration.append(end - start)
print(f"Number of times generated: {len(iterations_each_gen)}")
print(f"Average number of iterations per floor generation: {sum(iterations_each_gen) / len(iterations_each_gen)}")
print(f"Average time per floor generation: {sum(time_per_iteration) / len(time_per_iteration)}")"""
