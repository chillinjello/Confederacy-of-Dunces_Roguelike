from __future__ import annotations
from ast import walk
import pdb

from typing import TYPE_CHECKING
from xmlrpc.client import boolean
import random
import numpy as np

import color
from components.ai import HostileEnemy
from components.buff import Buff
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
        is_player: bool = False,

        base_miss_chance: int = 0,
        base_dodge_chance: float = 0,

        valve_enabled: bool = False,
        starting_valve: int = 50,
        valve_increase_on_kill: int = 2,
        base_valve_resistance: float = 1.0,
    ):
        self.base_max_hp = hp
        self._hp = hp
        
        self.base_defense = base_defense
        self.base_power = base_power
        self.base_miss_chance = base_miss_chance
        self.base_dodge_chance = base_dodge_chance

        self._valve = starting_valve
        self.max_valve = base_valve
        self.base_valve_resistance = base_valve_resistance
        self.valve_increase_on_kill = valve_increase_on_kill

        self.is_player = is_player
        # We want to track that enemies just hit by player don't attack 
        self.just_hit = False
        self.valve_enabled = valve_enabled

    def initialize_after_parent(self) -> None:
        pass

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

        base_miss_chance = self.base_miss_chance
        if self.valve_enabled:
            base_miss_chance += self.valve_miss_chance
        base = (base_miss_chance + addition) * multiplication
        return max(0, min(base, 1))

    @property
    def dodge_chance(self) -> float:
        addition, multiplication = 0, 1

        if self.parent.buff_container:
            multiplication *= self.parent.buff_container.dodge_chance_multiplier
            addition += self.parent.buff_container.dodge_chance_addition

        base = (self.base_dodge_chance + addition) * multiplication
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
            self.parent.inventory.drop_all()

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

    def take_damage(self, amount: int, counts_as_hit: bool = True, attacker: Actor = None) -> None:
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
                teleport_message = "George pulled a fast one at teleported somewhere!"
                self.engine.message_log.add_message(
                    teleport_message, 
                    color.enemy_atk     
                )
        else:
            self.hp -= amount

        self.just_hit = True

class DorianGreenFighter(Fighter):
    def __init__(self, hp: int, base_defense: int, base_power: int, fov: int = 10, spawn_count: int = 1):
        self.spawn_fov = fov
        self.spawn_count = spawn_count
        super().__init__(hp, base_defense, base_power)

    def take_damage(self, amount: int, counts_as_hit: bool = True) -> None:
        if (amount < self.hp):
            valid_coords = self.game_map.walkable_coords_in_range(self.parent.x, self.parent.y, self.spawn_fov)
            np.random.shuffle(valid_coords)
            search_range = 1
            for (x,y) in valid_coords[0:self.spawn_count + search_range]:
                if (self.game_map.get_blocking_entity_at_location(x,y)) != None:
                    search_range += 1
                    continue
                new_fop = entity_factories.fop.spawn(self.game_map, x, y)
                new_fop.fighter.just_hit = True
                summon_message = "Dorian Green summons degenerates from the gullies of the Frech Quarter!"
                self.engine.message_log.add_message(
                    summon_message, 
                    color.enemy_atk     
                )

        return super().take_damage(amount, counts_as_hit)

class NeighborAnnie(Fighter):
    def __init__(self, hp: int, base_defense: int, base_power: int, base_valve: int = 100, *, starting_valve: int = 50, valve_increase_on_kill: int = 2, is_player: bool = False, base_valve_resistance: float = 1):
        super().__init__(hp, base_defense, base_power, base_valve, starting_valve=starting_valve)

    def take_damage(self, amount: int, counts_as_hit: bool = True, attacker: Actor = None) -> None:
        if (attacker == None):
            super().take_damage(amount, counts_as_hit, attacker)
            return
        
        # Get actor coordinates
        a_x, a_y = attacker.x, attacker.y
        x, y = self.parent.x, self.parent.y 

        # Get behind coordinate for 1 pushes
        b_x_1 = x + 1 * max(min(1, x - a_x), -1)
        b_y_1 = y + 1 * max(min(1, y - a_y), -1)

        # Check if the coordinate is walkable
        is_clear_1 = self.game_map.is_coord_clear_and_walkable(b_x_1, b_y_1)
        if (not is_clear_1):
            super().take_damage(amount, counts_as_hit, attacker)
        else:
            # Get behind coordinate for 2 pushes
            b_x_2 = x + 2 * max(min(1, x - a_x), -1)
            b_y_2 = y + 2 * max(min(1, y - a_y), -1)

            # Check if the coordinate is walkable
            is_clear_2 = self.game_map.is_coord_clear_and_walkable(b_x_2, b_y_2)
            if (not is_clear_2):
                # if 2 pushes is not clear, only push once
                self.parent.place(b_x_1, b_y_1)
                self.just_hit = True
            else:
                # if 2 pushes is clear, push both times
                self.parent.place(b_x_2, b_y_2)
                self.just_hit = True

class GonzolozFighter(Fighter):
    def __init__(self, hp: int, base_defense: int, base_power: int, base_valve: int = 100, *, push_back_distance: int = 5, enemies_summoned: int = 2, spawn_fov: int = 10, starting_valve: int = 50):
        super().__init__(hp, base_defense, base_power, base_valve, starting_valve=starting_valve)
        self.enemies_summoned = enemies_summoned
        self.push_back_distance = push_back_distance
        self.spawn_fov = spawn_fov

    def push_back_player(self, player):
        x_diff = player.x - self.parent.x
        y_diff = player.y - self.parent.y

        mult = 1
        new_x_pos, new_y_pos = player.x, player.y
        while mult <= self.push_back_distance:
            prev_x_pos = new_x_pos
            prev_y_pos = new_y_pos
            new_x_pos = player.x + (mult * x_diff)
            new_y_pos = player.y + (mult * y_diff)
            is_clear = self.game_map.is_coord_clear_and_walkable(new_x_pos, new_y_pos)
            if not is_clear:
                if (prev_x_pos == player.x and prev_y_pos == player.y):
                    # player is not pushed
                    break
                else:
                    player.place(prev_x_pos, prev_y_pos)
                    break
            elif mult == self.push_back_distance:
                player.place(prev_x_pos, prev_y_pos)
                break
            mult += 1

    def summon_office_workers(self):
        valid_coords = self.game_map.walkable_coords_in_range(self.parent.x, self.parent.y, self.spawn_fov)
        np.random.shuffle(valid_coords)
        search_range = 0
        for (x,y) in valid_coords[0:self.enemies_summoned + search_range]:
            if (self.game_map.get_blocking_entity_at_location(x,y)) != None:
                search_range += 1
                continue
            new_office_worker = entity_factories.office_worker.spawn(self.game_map, x, y)
            new_office_worker.fighter.just_hit = True


    def take_damage(self, amount: int, counts_as_hit: bool = True, attacker: Actor = None) -> None:
        player = self.game_map.engine.player
        if (attacker is player):
            self.push_back_player(player)
            push_message = "You've left Gonzoloz no choice but to fire you! He forces you away!"
            self.engine.message_log.add_message(
                push_message, 
                color.enemy_atk     
            )
        if amount < self.hp:
            self.summon_office_workers()
        return super().take_damage(amount, counts_as_hit, attacker)

class MrsLevyFighter(Fighter):
    def __init__(self, hp: int, base_defense: int, base_power: int, base_valve: int = 100, *, starting_valve: int = 50, massage_board_health: int = 20):
        super().__init__(hp, base_defense, base_power, base_valve, starting_valve=starting_valve)
        self.massage_board_health = massage_board_health

        self.massage_board = None

        self.has_been_hit_once = False

    def take_damage(self, amount: int, counts_as_hit: bool = True, attacker: Actor = None) -> None:
        if not self.has_been_hit_once:
            self.has_been_hit_once = True
            (x, y) = self.game_map.find_closest_empty_space(self.parent.x, self.parent.y)
            self.massage_board = entity_factories.massage_board_entity.spawn(self.game_map, x, y)
            summon_message = "Mrs. Levy took defense behind her massage board! You must remove it before going after her!"
            self.engine.message_log.add_message(
                summon_message,
                color.enemy_atk     
            )
            return super().take_damage(amount, counts_as_hit, attacker)
        elif self.massage_board != None and self.massage_board.is_alive:
            # Do nothing if the massage_board is still alive
            defense_message = "You can't damage Mrs. Levy until her massage board is gotten rid of!"
            self.engine.message_log.add_message(
                defense_message,
                color.enemy_atk     
            )
            self.just_hit = True
        else:
            return super().take_damage(amount, counts_as_hit, attacker)

        return None

class LanaLeeFighter(Fighter):
    def take_damage(self, amount: int, counts_as_hit: bool = True, attacker: Actor = None) -> None:
        super().take_damage(amount, counts_as_hit, attacker)
        # Isn't stunned!
        self.just_hit = False

class CockatooFighter(Fighter):
    def __init__(self, hp: int, base_defense: int, base_power: int, base_valve: int = 100, *, starting_valve: int = 50, dodge_chance_addition: float = 0.1):
        super().__init__(hp, base_defense, base_power, base_valve, starting_valve=starting_valve, base_miss_chance=1, base_dodge_chance=dodge_chance_addition)
        self.taken_damage = False

    def take_damage(self, amount: int, counts_as_hit: bool = True, attacker: Actor = None) -> None:
        if not self.taken_damage:
            self.parent.ai = HostileEnemy(self.parent)
            self.taken_damage = True
            self.base_miss_chance = 0
        return super().take_damage(amount, counts_as_hit, attacker)

class BusFighter(Fighter):
    def take_damage(self, amount: int, counts_as_hit: bool = True, attacker: Actor = None) -> None:
        super().take_damage(amount, counts_as_hit, attacker)
        # Isn't stunned!
        self.just_hit = False