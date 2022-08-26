from __future__ import annotations
import pdb

import random
from typing import Dict, Iterator, List, Tuple, TYPE_CHECKING
from numpy import int8
import numpy as np

import tcod

import entity_factories
from game_map import GameMap
import tile_types

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity

# first tuple value is level, second value is num items
max_items_by_floor = [
    (1, 1),
    (4, 2),
]
# first tuple value is level, second value is num monsters
max_monsters_by_floor = [
    (1, 2),
    (4, 3),
    (6, 5),
]

def get_max_value_for_floor(
    max_value_by_floor: List[Tuple[int, int]], floor: int
) -> int:
    current_value = 0

    for floor_minimum, value in max_value_by_floor:
        if floor_minimum > floor:
            break
        else:
            current_value = value
    
    return current_value

def get_entities_at_random(
    weighted_chances_by_floor: Dict[int, List[Tuple[Entity, int]]],
    number_of_entities: int,
    floor: int,
) -> List[Entity]:
    entity_weighted_chances = {}

    for key, values in weighted_chances_by_floor.items():
        if key > floor:
            break
        else:
            for value in values:
                entity = value[0]
                weighted_chance = value[1]

                entity_weighted_chances[entity] = weighted_chance

    entities = list(entity_weighted_chances.keys())
    entity_weighted_chance_values = list(entity_weighted_chances.values())

    chosen_entities = random.choices(
        entities, weights=entity_weighted_chance_values, k=number_of_entities
    )

    return chosen_entities

class RectangularRoom:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x1 = x
        self.x2 = x + width
        self.y1 = y
        self.y2 = y + height

    @property
    def center(self) -> Tuple[int, int]:
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)

        return center_x, center_y

    @property
    def inner(self) -> Tuple[slice, slice]:
        """Return the inner area of this room as a 2D array index"""
        return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)

    def intersects(self, other: RectangularRoom) -> bool:
        """Return True if this room overlaps with another RectangularRoom"""
        return (
            self.x1 <= other.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y2 >= other.y1
        )

def place_entities(
    room: RectangularRoom, 
    dungeon: GameMap, 
    floor_number: int,
    enemy_chances,
    item_chances,
) -> None:
    number_of_monsters = random.randint(
        0, get_max_value_for_floor(max_monsters_by_floor, floor_number)
    )
    number_of_items = random.randint(
        0, get_max_value_for_floor(max_items_by_floor, floor_number)
    )

    monsters: List[Entity] = get_entities_at_random(
        enemy_chances, number_of_monsters, floor_number
    )
    items: List[Entity] = get_entities_at_random(
        item_chances, number_of_items, floor_number
    )

    for entity in monsters + items:
        x = random.randint(room.x1 + 1, room.x2 - 1)
        y = random.randint(room.y1 + 1, room.y2 - 1)

        if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
            entity.spawn(dungeon, x, y)


def tunnel_between(
    start: Tuple[int, int], end: Tuple[int, int]
) -> Iterator[Tuple[int, int]]:
    """Return an L-shaped tunnel between these two points."""
    x1, y1 = start
    x2, y2 = end
    if random.random() < 0.5: # 50% change
        # Move horizontally, then vertically.
        corner_x, corner_y = x2, y1
    else:
        # Move vertically, then horizontally.
        corner_x, corner_y = x1, y2

    # Generate the coordinates for this tunnel.
    for x, y in tcod.los.bresenham((x1, y1), (corner_x, corner_y)).tolist():
        yield x, y
    for x, y in tcod.los.bresenham((corner_x, corner_y), (x2, y2)).tolist():
        yield x, y 

def generate_dungeon(
    floor_settings: Dict[str, Dict],
    max_rooms: int,
    room_min_size: int,
    room_max_size: int,
    map_width: int,
    map_height: int,
    engine: Engine,
    floor_number: int,
) -> GameMap:
    """Generate a new dungeon map."""
    player = engine.player
    dungeon = GameMap(engine, map_width, map_height, entities=[player])

    def get_floor_color(x=0, y=0) -> Tuple[int8, int8, int8]:
        colors = floor_settings["colors"]
        if colors == None or colors["floor_primary"] == None:
            return (0xFF, 0xFF, 0xFF)
        elif colors["floor_secondary"] == None or len(colors["floor_secondary"]) <= 0:
            return colors["floor_primary"]
        color_index_based_on_pos = (x + y) % (1 + len(colors["floor_secondary"]))
        if color_index_based_on_pos == 0:
            return colors["floor_primary"]
        else:
            return colors["floor_secondary"][color_index_based_on_pos - 1]

    def get_floor_from_slice(slices: Tuple[slice, slice]) -> List[Tuple[int, int, int]]:
        floors = []
        x_slice, y_slice = slices[0], slices[1]
        for i, x in enumerate(range(x_slice.start, x_slice.stop)):
            floors.append([])
            for y in range(y_slice.start, y_slice.stop):
                floors[i].append(tile_types.floor(get_floor_color(x, y)))
        return floors

    engine.message_log.add_message(f"You've entered { floor_settings['floor_name'] }")
    enemy_chances = floor_settings["enemy_chances"]
    item_chances = floor_settings["item_chances"]

    rooms: List[RectangularRoom] = []

    center_of_last_room = (0,0)

    for r in range(max_rooms):
        room_width = random.randint(room_min_size, room_max_size)
        room_height = random.randint(room_min_size, room_max_size)

        x = random.randint(0, dungeon.width - room_width - 1)
        y = random.randint(0, dungeon.height - room_height - 1)

        # "RectangularRoom" class makes rectangles easier to work with
        new_room = RectangularRoom(x, y, room_width, room_height)

        # Run through the other rooms and see if they intersect with this one.
        if any(new_room.intersects(other_room) for other_room in rooms):
            continue # this room intersects, so go to the next attempt.
        # If there are no intersections then the room is valid.

        # Dig out this rooms inner area.
        dungeon.tiles[new_room.inner] = get_floor_from_slice(new_room.inner)
        # for iy, ix in np.ndindex(new_room.inner):
        #     dungeon.tiles[iy, ix] = tile_types.floor(get_floor_color(ix, iy))

        if len(rooms) == 0:
            # The first room, where the player stars.
            player.place(*new_room.center, dungeon)
        else: # All rooms after the first
            # Dig out a tunnel betwewen this room and the previous one.
            for x, y in tunnel_between(rooms[-1].center, new_room.center):
                dungeon.tiles[x,y] = tile_types.floor(floor_settings["colors"]["floor_primary"])

            center_of_last_room = new_room.center

        place_entities(new_room, dungeon, floor_number, enemy_chances, item_chances)

        dungeon.tiles[center_of_last_room] = tile_types.down_stairs((200,200,200))
        dungeon.downstairs_location = center_of_last_room

        # Finally, append the new room to the list.
        rooms.append(new_room)

    return dungeon
