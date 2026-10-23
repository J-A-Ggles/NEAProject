from enum import Enum
from os import listdir
from random import choice

import pygame
from pygame import Surface
from pytmx import TiledTileLayer, TiledMap
from pytmx.util_pygame import load_pygame

from temple.room import Room


class RoomTypes(Enum):
    NRM = "./temple/rooms/normal/"
    ITM = "./temple/rooms/item/"
    BSS = "./temple/rooms/boss/"


pygame.display.set_mode()


def load_map(category: str, index: str) -> TiledMap:
    """Loads a Tiled Map.

    :arg category: The category of room to load from.
    :arg index: The index of the room in that category."""

    return load_pygame(f"{RoomTypes[category].value}{index}.tmx")


TILED_MAPS = {
    RoomType.name: {tiled_map[:3]: load_pygame(RoomType.value + tiled_map) for tiled_map in listdir(RoomType.value)} for
    RoomType in RoomTypes
}


def get_maps(category: str) -> list[tuple[str, TiledMap]]:
    """Gets every map of a specific category.

    :arg category: The category of room to load from.
    :return: A list of tuples of room indexes and TMX data."""

    return list(TILED_MAPS[category].items())


def find_maps(room: Room, category: str) -> list[tuple[str, TiledMap]]:
    """Gets a list of potential maps for a room.

    :arg room: The room to find maps for.
    :arg category: The category of room to gets maps of."""

    tiled_maps: list[tuple[str, TiledMap]] = get_maps(category)

    # Each map has a minimum and maximum number of doors. The room should
    # have a number of doors in that range. Additionally, the doors that
    # the room has should be a subset of every door the room could have.
    return [tiled_map for tiled_map in tiled_maps if
            tiled_map[1].layernames["Doors"].properties["min"] <= room.door_count <=
            tiled_map[1].layernames["Doors"].properties["max"] and set(door.direction for door in room.doors).issubset(
                door.name for door in tiled_map[1].layernames["Doors"])]


def assign_room(room: Room, category: str, index: str = "") -> None:
    """Assigns a room TMX (Tiled Map) data.

    :param room: The room to assign to.
    :param category: The category of room to search through.
    :param index: (optional) The index of the room in that category.
    """

    # If no index is specified, a map will be chosen at random.
    if not index:
        possible_maps: list[tuple[str, TiledMap]] = find_maps(room, category)

        if possible_maps:
            # A random map is chosen from all possible maps, then
            # the room is assigned its category, the map's index
            # in the category, and TMX data.
            chosen_map: tuple[str, TiledMap] = choice(possible_maps)
            room.category = category
            room.index = chosen_map[0]
            room.tmx_data = chosen_map[1]
        else:
            raise Exception("No possible room found.")

    # If an index is specified, that map will be loaded.
    else:
        chosen_map: TiledMap = load_map(category, index)
        if chosen_map:
            room.category = category
            room.index = index
            room.tmx_data = chosen_map
        else:
            raise Exception("No room with that ID found.")


class Renderer(object):
    """A Renderer to render maps for the game.

    Currently, only renders tile layers."""

    def render_map(self, tiled_map: TiledMap, surface: Surface) -> None:
        for tile_layer in tiled_map.visible_tile_layers:
            self.render_tile_layer(surface, tiled_map.layers[tile_layer])

    def render_tile_layer(self, surface: Surface, tile_layer: TiledTileLayer):
        surface_blit = surface.blit
        for x, y, image in tile_layer.tiles():
            surface_blit(image, (20 * x, 20 * y))


"""print(TILED_MAPS)
map: TiledMap = TILED_MAPS["NRM"]["000"]
for obj in map.layers[-1]:
    ob: TiledObject = obj
    print(ob)"""
