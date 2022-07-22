from __future__ import annotations

import copy
import math
from typing import Optional, Tuple, TypeVar, Type, TYPE_CHECKING, Union
from xmlrpc.client import Boolean

from render_order import RenderOrder

if TYPE_CHECKING:
    from components.ai import BaseAI
    from components.fighter import Fighter
    from components.consumable import Consumable
    from components.equipment import Equipment
    from components.inventory import Inventory
    from components.level import Level
    from components.equippable import Equippable
    from components.buff_container import BuffContainer
    from game_map import GameMap

T = TypeVar("T", bound="Entity")

class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """

    parent: Union[GameMap, Inventory]

    def __init__(
        self, 
        parent: Optional[GameMap] = None,
        x: int = 0, 
        y: int = 0, 
        char: str = "?", 
        color: Tuple[int, int, int] = (255, 255, 255),
        name: str = "<Unnamed>",
        blocks_movement: bool = False,
        render_order: RenderOrder = RenderOrder.CORPSE,
    ):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement
        self.render_order = render_order
        if parent:
            # If parent isn't provided now then it will be set later.
            self.parent = parent
            parent.entities.add(self)
    
    @property
    def game_map(self) -> game_map:
        return self.parent.game_map

    @property
    def engine(self) -> Engine:
        return self.parent.game_map.engine

    def spawn(self: T, game_map: game_map, x: int, y: int) -> T:
        """Spawn a copy of this instance at the given location."""
        clone = copy.deepcopy(self)
        clone.x = x
        clone.y = y
        clone.parent = game_map
        game_map.entities.add(clone)
        return clone

    def place(self, x: int, y: int, game_map: Optional[game_map] = None) -> None:
        """Place this entity at a new location. Handles moving across game_maps."""
        self.x = x
        self.y = y
        if game_map:
            if hasattr(self, "parent"): # Possibly uninitialized.
                if self.parent is self.game_map:
                    self.game_map.entities.remove(self)
            self.parent = game_map
            game_map.entities.add(self)

    def distance(self, x: int, y: int) -> float:
        """
        Return the distance between the current entity and the given (x, y) coordinate.
        """
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def move(self, dx: int, dy: int) -> None:
        # Move the entity by a given amount
        self.x += dx
        self.y += dy


class Actor(Entity):
    HOSTILE_ACTOR = "HOSTILE_ACTOR"
    FRIENDLY_ACTOR = "FRIENDLY_ACTOR"
    NEUTRAL_ACTOR = "NEUTRAL_ACTOR"
    INANIMATE_ACTOR = "INANIMATE_ACTOR"

    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: Tuple[int, int, int] = (255, 255, 255),
        name: str = "<Unnamed>",
        ai_cls: Type[BaseAI],
        equipment: Equipment,
        fighter: Fighter,
        inventory: Inventory,
        buff_container: BuffContainer,
        level: Level,
        hostile: str = HOSTILE_ACTOR,
    ):
        super().__init__(
            x=x,
            y=y,
            char=char,
            color=color,
            name=name,
            blocks_movement=True,
            render_order=RenderOrder.ACTOR,
        )

        self.ai: Optional[BaseAI] = ai_cls(self)

        self.equipment: Equipment = equipment
        self.equipment.parent = self

        self.fighter = fighter
        self.fighter.parent = self

        self.inventory = inventory
        self.inventory.parent = self

        self.buff_container = buff_container
        self.buff_container.parent = self

        self.level = level
        self.level.parent = self

        self.hostile = hostile

    @property
    def is_alive(self) -> bool:
        """Returns True as long as this actor can perform actions."""
        return bool(self.ai)

class Item(Entity):
    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: Tuple[int, int, int] = (255, 255, 255),
        name: str = "<Unnamed>",
        consumable: Optional[Consumable] = None,
        equippable: Optional[Equippable] = None,
    ):
        super().__init__(
            x=x,
            y=y,
            char=char,
            color=color,
            name=name,
            blocks_movement=False,
            render_order=RenderOrder.ITEM,
        )

        self.consumable = consumable

        if self.consumable:
            self.consumable.parent = self

        self.equippable = equippable

        if self.equippable:
            self.equippable.parent = self