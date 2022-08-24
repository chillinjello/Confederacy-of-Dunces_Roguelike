from __future__ import annotations
from ast import walk
import pdb

from typing import TYPE_CHECKING
from xmlrpc.client import boolean
import random
import numpy as np

import color
import entity_factories
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
        starting_valve: int = 50,
        valve_increase_on_kill: int = 2,
        is_player: bool = False,
        base_valve_resistance: float = 1.0,
    ):
        self.base_max_hp = hp
        self._hp = hp
        self.base_defense = base_defense
        self.base_power = base_power
        self._valve = starting_valve
        self.max_valve = base_valve
        self.base_valve_resistance = base_valve_resistance
        self.valve_increase_on_kill = valve_increase_on_kill
        self.is_player = is_player
        # We want to track that enemies just hit by player don't attack 
        self.just_hit = False



    def reset_just_hit(self) -> None:
        self.just_hit = False

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, value: int) -> None:
        self._hp = max(0, min(value, self.max_hp))
        if self._hp == 0 and self.parent.ai:
            self.die()

    @property
    def max_hp(self) -> int:
        final_max_health = self.base_max_hp
        if self.parent.buff_container:
            final_max_health += self.parent.buff_container.max_health_addition
        if self.parent.equipment:
            final_max_health += self.parent.equipment.max_health_addition
        return final_max_health

    def increase_base_max_hp(self, value: int) -> None:
        hp_to_add = max(0, value)
        self.base_max_hp += value
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
    def valve_miss_chance(self) -> float:
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
    def valve_resistance(self) -> float:
        addition, multiplication = 0, 1
        if self.parent.equipment:
            multiplication *= self.parent.equipment.valve_resistance_multiplier
            addition += self.parent.equipment.valve_resistance_addition

        if self.parent.buff_container:
            multiplication *= self.parent.buff_container.valve_resistance_multiplier
            addition += self.parent.buff_container.valve_resistance_addition

        return (self.base_valve_resistance + addition) * multiplication

    @property
    def miss_chance(self) -> float:
        addition, multiplication = 0, 1
        if self.parent.equipment:
            multiplication *= self.parent.equipment.miss_chance_multiplier
            addition += self.parent.equipment.miss_chance_addition

        if self.parent.buff_container:
            multiplication *= self.parent.buff_container.miss_chance_multiplication
            addition += self.parent.buff_container.miss_chance_addition

        base = (self.valve_miss_chance + addition) * multiplication
        return max(0, min(base, 1))

    def tick(self) -> None:
        if self._hp > self.max_hp:
            self._hp = self.max_hp

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

    def on_kill(self) -> None:
        if self.engine.player is self.parent:
            self.valve = min(self.max_valve, self.valve + self.valve_increase_on_kill)
    
    def heal(self, amount:int) -> int:
        if self.hp == self.max_hp:
            return 0

        new_hp_value = self.hp + amount

        if new_hp_value > self.max_hp:
            new_hp_value = self.max_hp

        amount_recovered = new_hp_value - self.hp

        self.hp = new_hp_value

        return amount_recovered

    def max_out_health(self) -> None:
        self.hp = self.base_max_hp

    def max_out_valve(self) -> None:
        self.valve = self.max_valve

    def take_damage(self, amount: int, counts_as_hit: bool = True) -> None:
        self.hp -= amount

        if self.is_player:
            self.valve_take_damage(amount)
        else:
            self.just_hit = True
    
    def valve_take_damage(self, amount: int) -> None:
        factor = float(amount) * self.valve_resistance
        assert(factor > 0)
        self.valve = int(self.valve - factor)

class GeorgeFighter(Fighter):
    def __init__(self, hp: int, base_defense: int, base_power: int, base_valve: int = 100, *, starting_valve: int = 50):
        super().__init__(hp, base_defense, base_power, base_valve, starting_valve=starting_valve)
        self.hit_lethal = False

    def take_damage(self, amount: int, counts_as_hit: bool = True) -> None:
        if (self.hp <= amount and not self.hit_lethal):
            self.hp = 1
            self.hit_lethal = True
            walkable_coords = self.game_map.walkable_coords()
            if (len(walkable_coords) > 0):
                r_index = random.randint(0, len(walkable_coords) - 1)
                r_coord = walkable_coords[r_index]
                self.parent.place(*r_coord)
        else:
            self.hp -= amount

        self.just_hit

class DorianGreenFighter(Fighter):
    def __init__(self, hp: int, base_defense: int, base_power: int, fov: int = 10, spawn_count: int = 1):
        self.spawn_fov = fov
        self.spawn_count = spawn_count
        super().__init__(hp, base_defense, base_power)

    def take_damage(self, amount: int, counts_as_hit: bool = True) -> None:
        valid_coords = self.game_map.walkable_coords_in_range(self.parent.x, self.parent.y, self.spawn_fov)
        np.random.shuffle(valid_coords)
        for (x,y) in valid_coords[0:self.spawn_count + 1]:
            new_fop = entity_factories.fop.spawn(self.game_map, x, y)
            new_fop.fighter.just_hit = True

        return super().take_damage(amount, counts_as_hit)