from __future__ import annotations
import pdb

from typing import TYPE_CHECKING
from xmlrpc.client import boolean

import color
from components.base_component import BaseComponent
from game_map import GameMap
from render_order import RenderOrder

if TYPE_CHECKING:
    from entity import Actor


class Fighter(BaseComponent):
    parent: Actor

    def __init__(self, 
        hp: int, 
        base_defense: int, 
        base_power: int, 
        base_valve: int = 100,
        *,
        is_player: bool = False
    ):
        self.max_hp = hp
        self._hp = hp
        self.base_defense = base_defense
        self.base_power = base_power
        self._valve = base_valve
        self.max_valve = base_valve
        self.is_player = is_player

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, value: int) -> None:
        self._hp = max(0, min(value, self.max_hp))
        if self._hp == 0 and self.parent.ai:
            self.die()

    def increase_max_hp(self, value: int) -> None:
        hp_to_add = max(0, value)
        self.max_hp += value
        self.heal(hp_to_add)
        return hp_to_add

    @property
    def valve(self) -> int:
        return self._valve

    @valve.setter
    def valve(self, value:int) -> None:
        starting_valve_level = self.valve_level
        self._valve = max(0, min(value, self.max_valve))
        end_valve_level = self.valve_level
        if starting_valve_level != end_valve_level:
            self.parent.parent.engine.message_log.add_message(
                f"Your valve feels {self.get_valve_level_string(end_valve_level)}."
            )

    @property
    def valve_level(self) -> int:
        # Returns 0-4 indicating Fully Closed to 100% Clear
        current_ratio = self._valve / self.max_valve
        if (current_ratio > 0.8):
            return 4 # 100% Clear
        elif (current_ratio > 0.6):
            return 3 # Almost Fully Open
        elif (current_ratio > 0.4):
            return 2 # Halfway Open
        elif (current_ratio > 0.2):
            return 1 # Partially Closed
        else:
            return 0 # Fully Closed

    def get_valve_level_string(self, level: int) -> str:
        if (level == 0):
            return "Fully Closed"
        elif (level == 1):
            return "Partially Closed"
        elif (level == 2):
            return "Halfway Open"
        elif (level == 3):
            return "Nearly Open"
        elif (level == 4):
            return "100% Clear"

    @property
    def defense(self) -> int:
        return self.base_defense + self.defense_bonus

    @property
    def power(self) -> int:
        return self.base_power + self.power_bonus

    @property
    def defense_bonus(self) -> int:
        addition = 0
        multiplication = 1
        if self.parent.equipment:
            multiplication *= self.parent.equipment.defense_multiplier
            addition += self.parent.equipment.defense_addition
        if self.parent.buff_container:
            multiplication *= self.parent.buff_container.defense_multiplier
            addition += self.parent.buff_container.defense_addition
            if self.parent.buff_container.defense_addition > 0:
                pdb.set_trace()
        return int(addition * multiplication)

    @property
    def power_bonus(self) -> int:
        addition = 0
        multiplication = 1
        if self.parent.equipment:
            multiplication *= self.parent.equipment.power_multiplier
            addition += self.parent.equipment.power_addition
        if self.parent.buff_container:
            multiplication *= self.parent.buff_container.power_multiplier
            addition += self.parent.buff_container.power_addition
        return int(addition * multiplication)

    @property
    def valve_miss_chance(self) -> int:
        valve_level = self.valve_level
        if valve_level == 0:
            return 0.6
        elif valve_level == 1:
            return 0.3
        elif valve_level == 2:
            return 0.15
        elif valve_level == 3:
            return 0.05
        else:
            return 0

    @property
    def miss_chance(self) -> int:
        return self.valve_miss_chance

    def die(self) -> None:
        if self.engine.player is self.parent:
            death_message = "You died!"
            death_message_color = color.player_die
        else:
            death_message = f"{self.parent.name} is dead!"
            death_message_color = color.enemy_die

        self.parent.char = "%"
        self.parent.color = (191, 0, 0)
        self.parent.blocks_movement = False
        self.parent.ai = None
        self.parent.name = f"remains of {self.parent.name}"
        self.parent.render_order = RenderOrder.CORPSE

        self.engine.message_log.add_message(death_message, death_message_color)

        self.engine.player.level.add_xp(self.parent.level.xp_given)
    
    def heal(self, amount:int) -> int:
        if self.hp == self.max_hp:
            return 0

        new_hp_value = self.hp + amount

        if new_hp_value > self.max_hp:
            new_hp_value = self.max_hp

        amount_recovered = new_hp_value - self.hp

        self.hp = new_hp_value

        return amount_recovered

    def take_damage(self, amount: int) -> None:
        self.hp -= amount

        if self.is_player:
            factor = 1 - 2 * abs(amount)/100
            self.valve = int(self.valve * factor)