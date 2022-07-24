from __future__ import annotations

from typing import Optional, TYPE_CHECKING
import pdb
import sys
import random
import tcod.los

import actions
import color
import components.ai
import components.inventory
import entity_factories
from components.base_component import BaseComponent
from components.buff import BleedBuff, Buff
from exceptions import Impossible
from input_handlers import (
    ActionOrHandler,
    AreaRangedAttackHandler,
    PathAttackHandler, 
    SingleRangedAttackHandler
)

if TYPE_CHECKING:
    from entity import Actor, Item

class Consumable(BaseComponent):
    parent: Item

    def get_action(self, consumer: Actor) -> Optional[ActionOrHandler]:
        """Try to return the action for this item."""
        return actions.ItemAction(consumer, self.parent)

    def activate(self, action: actions.ItemAction) -> None:
        """Invoke this items ability.
        
        `action` is the context for this activation.
        """
        raise NotImplementedError()

    def consume(self) -> None:
        """Remove the consumed item from this containing inventory."""
        entity = self.parent
        inventory = entity.parent
        if isinstance(inventory, components.inventory.Inventory):
            inventory.items.remove(entity)

class ConfusionConsumable(Consumable):
    def __init__(self, number_of_turns: int):
        self.number_of_turns = number_of_turns

    def get_action(self, consumer: Actor) -> SingleRangedAttackHandler:
        self.engine.message_log.add_message(
            "Select a target location.", color.needs_target
        )
        return SingleRangedAttackHandler(
            self.engine,
            callback = lambda xy: actions.ItemAction(consumer, self.parent, xy),
        )

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        target = action.target_actor

        if not self.engine.game_map.visible[action.target_xy]:
            raise Impossible("You cannot target an area that you cannot see.")
        if not target:
            raise Impossible("You must select an enemy to target.")
        if target is consumer:
            raise Impossible("You cannot confuse yourself!")
        
        self.engine.message_log.add_message(
            f"The eyes of the {target.name} look vacant, as it starts to stumble around!",
            color.status_effect_applied
        )
        target.ai = components.ai.ConfusedEnemy(
            entity=target, previous_ai=target.ai, turns_remaining=self.number_of_turns
        )
        self.consume()
        

class HealingConsumable(Consumable):
    def __init__(self, amount: int):
        self.amount = amount

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        amount_recovered = consumer.fighter.heal(self.amount)

        if amount_recovered > 0:
            self.engine.message_log.add_message(
                f"You consume the {self.parent.name}, and recover {amount_recovered} HP!",
                color.health_recovered
            )
            self.consume()
        else:
            raise Impossible(f"Your health is already full.")

class LightningDamageConsumable(Consumable):
    def __init__(self, damage: int, maximum_range: int):
        self.damage = damage
        self.maximum_range = maximum_range

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        target = None
        closest_distance = self.maximum_range + 1.0

        for actor in self.engine.game_map.actors:
            if actor is not consumer and self.parent.game_map.visible[actor.x, actor.y]:
                distance = consumer.distance(actor.x, actor.y)

                if distance < closest_distance:
                    target = actor
                    closest_distance = distance

        if target:
            self.engine.message_log.add_message(
                f"A lighting bolt strikes the {target.name} with a loud thunder, for {self.damage} damage!"
            )
            target.fighter.take_damage(self.damage)
            self.consume()
        else:
            raise Impossible("No enemy is close enough to strike.")

class FireballDamageConsumable(Consumable):
    def __init__(self, damage: int, radius: int):
        self.damage = damage
        self.radius = radius

    def get_action(self, consumer: Actor) -> AreaRangedAttackHandler:
        self.engine.message_log.add_message(
            "Select a target location.", color.needs_target
        )
        return AreaRangedAttackHandler(
            self.engine,
            radius=self.radius,
            callback=lambda xy: actions.ItemAction(consumer, self.parent, xy),
        )
    
    def activate(self, action: actions.ItemAction) -> None:
        target_xy = action.target_xy

        if not self.engine.game_map.visible[target_xy]:
            raise Impossible("You cannot target an area that you cannot see.")

        targets_hit = False
        for actor in self.engine.game_map.actors:
            if actor.distance(*target_xy) <= self.radius:
                self.engine.message_log.add_message(
                    f"The {actor.name} is engulfed in a fiery explosion, taking {self.damage} damage!"
                )
                actor.fighter.take_damage(self.damage)
                targets_hit = True
            
        if not targets_hit:
            raise Impossible("There are no targets in the radius.")
        self.consume()


#
# Untargeted Consumables
#

class JellyDonut(Consumable):
    def __init__(self, amount: int = 15):
        self.amount = amount

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        amount_recovered = consumer.fighter.heal(self.amount)

        if amount_recovered > 0:
            self.engine.message_log.add_message(
                f"You consume the {self.parent.name}, and recover {amount_recovered} HP!",
                color.health_recovered
            )
            self.consume()
        else:
            raise Impossible(f"Your health is already full.")

class HotDog(Consumable):
    def __init__(self, amount: int = 2):
        self.amount = amount

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        amount_recovered = consumer.fighter.increase_max_hp(self.amount)

        if amount_recovered > 0:
            self.engine.message_log.add_message(
                f"The Hot Dog does wonders for your figure! Health increased by {self.amount}",
                color.health_recovered
            )
            self.consume()
        else:
            raise Impossible(f"Your health is already maxed out or something, idk.")

class DrNut(Consumable):
    def __init__(self, number_of_turns: int = 20):
        self.number_of_turns = number_of_turns

        self.defense_modifier = -5
        self.power_modifier = 10

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        dr_nut_buff = Buff(
            buff_time=self.number_of_turns,
            defense_addition=self.defense_modifier, 
            power_addition=self.power_modifier,
            time_expired_message="Your delicious Dr. Nut wore off."
        )
        consumer.buff_container.add_buff(dr_nut_buff)

        self.engine.message_log.add_message(
            f"You consume the delicious Dr. Nut! Your defense dropped {self.defense_modifier} and power increased {self.power_modifier}.",
            color.health_recovered
        )

        self.consume()

class CommunissPamflet(Consumable):
    def __init__(self, range: int = 10) -> None:
        self.range = range

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity

        enemies_in_range = self.game_map.actors_within_fov(
            consumer.x,
            consumer.y,
            range=self.range,
            actors=self.game_map.hostile_actors,
        )

        if len(enemies_in_range) == 0:
            raise Impossible(f"There's no one around to be indoctrinated.")

        #find lowest health of enemies
        lowest_health = sys.maxsize
        for enemy in enemies_in_range:
            if enemy.fighter.hp < lowest_health:
                lowest_health = enemy.fighter.hp

        for enemy in enemies_in_range:
            enemy.fighter.hp = lowest_health
            self.engine.message_log.add_message(
                f"The {enemy.name}'s health as been reduced to {lowest_health}.",
                color.health_recovered
            )

        self.engine.message_log.add_message(
            f"Workingmen of all countries unite!",
            color.health_recovered
        )

        self.consume()

class TicketToTheMovies(Consumable):
    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity

        walkable_coords = self.game_map.walkable_coords()
        if len(walkable_coords) == 0:
            raise Impossible("Sadly, the theater's are all closed.")
        
        r_index = random.randint(0, len(walkable_coords) - 1)
        r_coord = walkable_coords[r_index]

        consumer.place(*r_coord)

        self.engine.message_log.add_message(
            f"Who do they expect to buy this waste?",
            color.health_recovered
        )

        self.consume()

class JazzRecord(Consumable):
    def __init__(self, number_of_turns) -> None:
        self.number_of_turns = number_of_turns

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity

        enemies_in_range = self.game_map.actors_within_fov(
            consumer.x,
            consumer.y,
            range=10,
            actors=self.game_map.hostile_actors,
        )

        if len(enemies_in_range) == 0:
            raise Impossible(f"There's no one around to be hear your hip jazz music.")

        for enemy in enemies_in_range:
            enemy.ai = components.ai.ConfusedEnemy(
                entity=enemy, previous_ai=enemy.ai, turns_remaining=self.number_of_turns
            )

        self.engine.message_log.add_message(
            f"Jazz is for the people!",
            color.health_recovered
        )

        self.consume()

class StainedSheet(Consumable):
    def __init__(self, ):
        self.defense_modifier = 5
    
    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        stained_sheet_buff = Buff(
            defense_addition=self.defense_modifier, 
            time_expired_message="Your sheet tears and falls to the ground.",
        )
        consumer.buff_container.add_buff(stained_sheet_buff)

        self.engine.message_log.add_message(
            f"You wrap your favorite sheet tightly around your body, raising your defense by {self.defense_modifier}.",
            color.health_recovered
        )

        self.consume()




#
# Targeted Consumables
#

class Cross(Consumable):
    def __init__(self, health: int = 50, max_range: int = 15):
        self.health = health
        self.max_range = max_range

    def get_action(self, consumer: Actor) -> AreaRangedAttackHandler:
        self.engine.message_log.add_message(
            "Place your cross.", color.needs_target
        )
        return AreaRangedAttackHandler(
            self.engine,
            range=self.max_range,
            callback=lambda xy: actions.ItemAction(consumer, self.parent, xy),
        )

    def activate(self, action: actions.ItemAction) -> None:
        target_xy = action.target_xy
        consumer = action.entity

        if not self.engine.game_map.visible[target_xy]:
            raise Impossible("You cannot place the cross beyond your vision.")

        blocking_entity = self.game_map.get_blocking_entity_at_location(*target_xy)
        in_bounds = self.game_map.in_bounds(*target_xy)
        walkable = self.game_map.is_walkable(*target_xy)

        if blocking_entity or not in_bounds or not walkable:
            raise Impossible(f"Some earthly blemish is blocking you from placing the cross!")

        dx = target_xy[0] - consumer.x
        dy = target_xy[1] - consumer.y
        distance = max(abs(dx), abs(dy))
        if distance > self.max_range:
            raise Impossible("Cross must be placed closer!")

        self.engine.message_log.add_message(
            f"Placing it down, you feel the room's energy gather around the cross.",
            color.status_effect_applied
        )
        cross = entity_factories.cross_entity.spawn(self.game_map, *target_xy)

        enemies = self.game_map.actors_within_fov(
            *target_xy,
            range=10,
            actors=self.game_map.hostile_actors,
        )
        for enemy in enemies:
            enemy.ai.set_current_target(cross)

class TheConsolationOfPhilosophy(Consumable):
    def __init__(self, time_length: int = -1, max_range: int = 15):
        self.time_length = time_length
        self.max_range = max_range

    def get_action(self, consumer: Actor) -> AreaRangedAttackHandler:
        self.engine.message_log.add_message(
            "Select a conversion location.", color.needs_target
        )
        return AreaRangedAttackHandler(
            self.engine,
            range=self.max_range,
            callback=lambda xy: actions.ItemAction(consumer, self.parent, xy),
        )
    
    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        target = action.target_actor

        if not self.engine.game_map.visible[action.target_xy]:
            raise Impossible("You cannot target an area that you cannot see.")
        if not target:
            raise Impossible("You must select an enemy to target.")
        if target is consumer:
            raise Impossible("You're already enlightened!")
        if target.distance(consumer.x, consumer.y) > self.max_range:
            raise Impossible("Enemy out of range!")

        self.engine.message_log.add_message(
            f"The {target.name} has recieved enlightenment!",
            color.status_effect_applied
        )
        target.ai = components.ai.AllyEnemy(
            entity=target,
            search_distance=10,
        )

        self.consume()

class BowlingBall(Consumable):
    def __init__(self, base_damage: int = 10, additional_damage: int = 5, max_range: int = 8) -> None:
        self.starting_pos = None
        self.end_pos = None

        self.base_damage = base_damage
        self.additional_damage = additional_damage

        self.max_range = max_range

    def get_action(self, consumer: Actor) -> AreaRangedAttackHandler:
        self.engine.message_log.add_message(
            "Select ball path.", color.needs_target
        )
        self.starting_pos = (consumer.x, consumer.y)
        return PathAttackHandler(
            self.engine,
            range=self.max_range,
            callback=lambda xy: actions.ItemAction(consumer, self.parent, xy),
            starting_xy=self.starting_pos,
            stop_at_unwalkable=True,
        )
    
    def activate(self, action: actions.ItemAction) -> None:
        full_coords = tcod.los.bresenham(self.starting_pos, action.target_xy).tolist()
        full_coords.pop(0)
        coords = []
        line_length = 1
        for coord in full_coords:
            if not self.engine.game_map.is_walkable(*coord):
                break
            if line_length > self.max_range:
                break

            coords.append(coord)

            line_length += 1
            
            
        if (len(coords) <= 1):
            raise Impossible("You cannot target yourself.")

        # get rid of the first entry
        coords.pop()
        targets_in_line = []
        for coord in coords:
            coord_target = self.engine.game_map.get_actor_at_location(*coord)
            if coord_target != None:
                targets_in_line.append(coord_target)

        if (len(targets_in_line) == 0):
            raise Impossible("There are no enemies in your path to get bowled.")

        total_damage = self.base_damage + (len(targets_in_line) - 1) * self.additional_damage
        for target in targets_in_line:
            target.fighter.take_damage(total_damage)
            self.engine.message_log.add_message(
                f"The {target.name} has been hit by the bowling ball. Strike!",
                color.status_effect_applied
            )

        self.consume()

class OvenWine(Consumable):
    def __init__(self, damage: int = 5, diameter: int = 1, number_of_turns: int = 5):
        self.damage = damage
        self.diameter = diameter
        self.number_of_turns = number_of_turns

    def get_action(self, consumer: Actor) -> AreaRangedAttackHandler:
        self.engine.message_log.add_message(
            "Select a wine location.", color.needs_target
        )
        return AreaRangedAttackHandler(
            self.engine,
            diameter=self.diameter,
            callback=lambda xy: actions.ItemAction(consumer, self.parent, xy),
        )
    
    def activate(self, action: actions.ItemAction) -> None:
        target_xy = action.target_xy

        if not self.engine.game_map.visible[target_xy]:
            raise Impossible("You cannot wine an area that you cannot see.")

        targets_hit = False
        for actor in self.engine.game_map.actors:
            if actor.distance(*target_xy) <= self.diameter/2:
                self.engine.message_log.add_message(
                    f"The {actor.name} begins to bleed in the wake of splashes of glass and cheap wine, taking {self.damage} damage!"
                )
                actor.fighter.take_damage(self.damage)
                actor.ai = components.ai.ConfusedEnemy(
                    entity=actor, previous_ai=actor.ai, turns_remaining=self.number_of_turns
                )
                new_bleed_buff = BleedBuff(
                    buff_time=self.number_of_turns,
                    damage=self.damage,
                    time_expired_message=f"The {actor.name}'s wine bottle inflicted wounds are healed.",
                )
                actor.buff_container.add_buff(new_bleed_buff)
                targets_hit = True
            
        if not targets_hit:
            raise Impossible("There are no targets in the radius.")
        self.consume()