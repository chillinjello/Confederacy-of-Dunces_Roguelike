from __future__ import annotations
import pdb

from typing import Iterable, Iterator, Optional, Tuple, TYPE_CHECKING

import numpy as np 
from tcod.console import Console
from tcod.map import compute_fov

from entity import Actor, Item
import tile_types

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity

class GameMap: 
    def __init__(self, engine: Engine, width: int, height: int, entities: Iterable[Entity] = ()):
        self.engine = engine
        self.width, self.height = width, height
        self.entities = set(entities)
        self.tiles = np.full((width, height), fill_value=tile_types.wall, order="F")

        self.visible = np.full(
            (width, height), fill_value=False, order="F"
        ) # Tiles the player can currently see
        self.explored = np.full(
            (width, height), fill_value=False, order="F"
        ) # Tiles the player has seen before

        self.downstairs_location = (0, 0)

    @property
    def game_map(self) -> GameMap:
        return self

    @property
    def actors(self) -> Iterator[Actor]:
        """Iterate over this maps living actors."""
        yield from (
            entity
            for entity in self.entities
            if isinstance(entity, Actor) and entity.is_alive
        )

    @property
    def hostile_actors(self) -> Iterator[Actor]:
        """Iterate over this maps living actors."""
        yield from (
            entity
            for entity in self.entities
            if isinstance(entity, Actor) and entity.is_alive and entity.hostile == Actor.HOSTILE_ACTOR
        )
    
    @property
    def friendly_actors(self) -> Iterator[Actor]:
        """Iterate over this maps living actors."""
        yield from (
            entity
            for entity in self.entities
            if isinstance(entity, Actor) and entity.is_alive and entity.hostile == Actor.FRIENDLY_ACTOR
        )

    @property
    def inanimate_actors(self) -> Iterator[Actor]:
        """Iterate over this maps living actors."""
        yield from (
            entity
            for entity in self.entities
            if isinstance(entity, Actor) and entity.is_alive and entity.hostile == Actor.INANIMATE_ACTOR
        )

    def actors_within_range(self, x, y, range, actors=None) -> Iterator[Actor]:
        if actors == None:
            actors = self.actors

        actors_in_range = []
        for actor in actors:
            if actor.distance(x, y) <= range:
                actors_in_range.append(actor)
        
        return actors_in_range

    def actors_within_fov(self, x, y, range, actors=None):
        if actors == None:
            actors = self.actors

        fov = compute_fov(
            self.tiles["transparent"],
            (x,y),
            radius = range,
        )

        actors_in_range = []
        for actor in actors:
            if fov[actor.x, actor.y]:
                actors_in_range.append(actor)
        
        return actors_in_range

    @property
    def items(self) -> Iterator[Item]:
        yield from (entity for entity in self.entities if isinstance(entity, Item))

    def get_blocking_entity_at_location(
        self, location_x: int, location_y: int
    ) -> Optional[Entity]:
        for entity in self.entities:
            if (
                entity.blocks_movement 
                and entity.x == location_x 
                and entity.y == location_y
            ):
                return entity

        return None

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if x and y are inside of the bounds of this map"""
        return 0 <= x < self.width and 0 <= y < self.height

    def is_walkable(self, x: int, y: int) -> bool:
        """Return True if x and y are on a walkable tile"""
        return self.tiles["walkable"][x,y]

    def walkable_coords(self) -> Iterable(Tuple[int,int]):
        walkable_coord_array = []
        for x in range(self.width):
            for y in range(self.height):
                if self.tiles["walkable"][x,y]:
                    walkable_coord_array.append((x,y))
        return walkable_coord_array

    def walkable_coords_in_range(self, x, y, range) -> Iterable(Tuple[int, int]):
        fov = compute_fov(
            self.tiles["transparent"],
            (x,y),
            radius = range,
        )
        walkable_coords_in_range = []
        for x, xVal in enumerate(fov):
            for y, yVal in enumerate(fov[x]):
                if yVal and self.is_walkable(x,y) and self.get_blocking_entity_at_location(x,y) == None:
                    walkable_coords_in_range.append((x, y))

        return walkable_coords_in_range

    def render(self, console: Console) -> None:
        """
        Renders the map.

        If a tile is in the "visible" array, then draw it with the "light" colors.
        If it isn't, but it's in the "explored" array, then draw it with the "dark" colors.
        Otherwise, the default is "SHROUD". 
        """
        console.tiles_rgb[0:self.width, 0:self.height] = np.select(
            condlist=[self.visible, self.explored],
            choicelist=[self.tiles["light"], self.tiles["dark"]],
            default=tile_types.SHROUD,
        )

        entities_sorted_for_rendering = sorted(
            self.entities, key=lambda x: x.render_order.value
        )

        for entity in entities_sorted_for_rendering:
            # Only print entities that are in the FOV
            if self.visible[entity.x, entity.y]:
                console.print(entity.x, entity.y, entity.char, fg=entity.color)

    def get_actor_at_location(self, x: int, y: int) -> Optional[Actor]:
        for actor in self.actors:
            if actor.x == x and actor.y == y: 
                return actor

        return None

class GameWorld:
    """
    Holds the settings for the GameMap, and generates new maps when moving down the stairs.
    """

    def __init__(
        self, 
        *, 
        engine: Engine,
        map_width: int,
        map_height: int,
        max_rooms: int,
        room_min_size: int,
        room_max_size: int,
        ordered_settings: Iterator,
        current_floor: int = 0,
    ):
        self.engine = engine

        self.map_width = map_width
        self.map_height = map_height

        self.max_rooms = max_rooms

        self.room_min_size = room_min_size
        self.room_max_size = room_max_size

        self.ordered_settings = ordered_settings

        self.current_floor = current_floor

    def generate_floor(self) -> None:
        from procgen import generate_dungeon

        self.current_floor += 1

        current_settings = self.ordered_settings[(self.current_floor - 1) % len(self.ordered_settings)]
        self.engine.game_map = generate_dungeon(
            floor_settings=current_settings,
            max_rooms=self.max_rooms,
            room_min_size=self.room_min_size,
            room_max_size=self.room_max_size,
            map_width=self.map_width,
            map_height=self.map_height,
            engine=self.engine,
            floor_number=self.current_floor,
        )