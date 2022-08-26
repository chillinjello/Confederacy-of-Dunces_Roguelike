from __future__ import annotations

import sys
import random
from typing import List, Tuple, TYPE_CHECKING, Optional, Iterable

from tcod.map import compute_fov

import numpy as np # type: ignore
import tcod

import pdb

from actions import Action, MeleeAction, MovementAction, WaitAction, BumpAction
from components.buff import Buff
from entity import Actor

class BaseAI(Action):
    def __init__(self, entity: Actor, *, view_radius: int = 8):
        super().__init__(entity)
        self.view_radius = view_radius
        self.current_target: Actor = None

    def perform(self) -> None:
        raise NotImplementedError()

    def set_current_target(self, new_target: Actor) -> None:
        self.current_target = new_target

    def get_path_to(self, dest_x: int, dest_y: int) -> List[Tuple[int, int]]:
        """Compute and return a path to the target position.
        If there is no valid path then returns an empty list."""
        # Copy the walkable array.
        cost = np.array(self.entity.parent.tiles["walkable"], dtype=np.int8)

        for entity in self.entity.parent.entities:
            # Check that an entity block movement and the cost isn't zero (blocking)
            if entity.blocks_movement and cost[entity.x, entity.y]:
                # Add to the cost of a blocked position.
                # A lower number means more enemies will crowd behind each other in hallways.
                # A higher number means enemies will take longer paths in order to surround player.
                cost[entity.x, entity.y] += 10

        # Create a graph from the cost array and pass that graph to a new pathfinder.
        graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
        pathfinder = tcod.path.Pathfinder(graph)

        pathfinder.add_root((self.entity.x, self.entity.y)) # Start position.

        # Compute the path to the destination and remove the starting point.
        path: List[List[int]] = pathfinder.path_to((dest_x, dest_y))[1:].tolist()

        # Convert from List[List[int]] to List[Tuple[int, int]].
        return [(index[0], index[1]) for index in path]

    def find_target_within_distance(self, potential_targets: Iterable[Actor], radius: int = 8) -> Actor:
        closest_actor = None
        closest_distance = sys.maxsize
        for target in potential_targets:
            if (not self.fov[target.x, target.y]):
                continue

            dx = target.x - self.entity.x
            dy = target.y - self.entity.y
            distance = max(abs(dx), abs(dy)) # Chebyshev distance.
            if (distance < closest_distance):
                closest_distance = distance
                closest_actor = target

        return closest_actor

    def update_fov(self, radius: int = 8) -> None:
        self.fov = compute_fov(
            self.engine.game_map.tiles["transparent"],
            (self.entity.x, self.entity.y),
            radius=radius,
        )


class HostileEnemy(BaseAI):
    def __init__(self, entity: Actor):
        super().__init__(entity)
        self.path: List[Tuple[int, int]] = []

    def perform(self) -> None:
        # Check to make sure the entity isn't already dead
        if not self.entity.is_alive:
            self.entity.ai = None
            return

        self.update_fov()

        if self.current_target == None or not self.current_target.is_alive:
            self.current_target = self.find_target_within_distance(potential_targets=self.entity.game_map.friendly_actors)

        if self.current_target == None:
            return WaitAction(self.entity).perform()
        
        target = self.current_target
        dx = target.x - self.entity.x
        dy = target.y - self.entity.y
        distance = max(abs(dx), abs(dy)) # Chebyshev distance.

        # If your target is not the player, perform the action freely
        # If your target IS the player, make sure you're in the fov, so you don't hit player off screen
        if (self.current_target != self.engine.player
            or self.engine.game_map.visible[self.engine.player.x, self.engine.player.y]
        ):
            if distance <= 1:
                return MeleeAction(self.entity, dx, dy).perform()

            self.path = self.get_path_to(target.x, target.y)

        if self.path:
            dest_x, dest_y = self.path.pop(0)
            return MovementAction(
                self.entity, dest_x - self.entity.x, dest_y - self.entity.y,
            ).perform()
        
        return WaitAction(self.entity).perform()

class AllyEnemy(BaseAI):
    def __init__(self, entity: Actor, search_distance: int = 40):
        super().__init__(entity)
        self.path: List[Tuple[int, int]] = []
        self.search_distance = search_distance
        entity.hostile = Actor.FRIENDLY_ACTOR

        self.entity.name = "Friendly " + self.entity.name

    def perform(self) -> None:
        # Check to make sure the entity isn't already dead
        if not self.entity.is_alive:
            self.entity.ai = None
            return

        self.update_fov()

        if self.current_target == None or not self.current_target.is_alive:
            self.current_target = self.find_target_within_distance(potential_targets=self.entity.game_map.hostile_actors)

        if self.current_target == None:
            return WaitAction(self.entity).perform()
        
        target = self.current_target
        dx = target.x - self.entity.x
        dy = target.y - self.entity.y
        distance = max(abs(dx), abs(dy)) # Chebyshev distance.

        # If your target is not the player, perform the action freely
        # If your target IS the player, make sure you're in the fov, so you don't hit player off screen
        if (self.current_target != self.engine.player
            or self.engine.game_map.visible[self.engine.player.x, self.engine.player.y]
        ):
            if distance <= 1:
                return MeleeAction(self.entity, dx, dy).perform()

            self.path = self.get_path_to(target.x, target.y)

        if self.path:
            dest_x, dest_y = self.path.pop(0)
            return MovementAction(
                self.entity, dest_x - self.entity.x, dest_y - self.entity.y,
            ).perform()
        
        return WaitAction(self.entity).perform()

class InanimateObject(BaseAI):
    def perform(self) -> None:
        # Do Nothing
        pass

class FrozenEnemy(BaseAI):
    """
    A frozen enemy will not take any actions for a given number of turns, then revert back to its previous AI.
    """
    def __init__(
        self,
        entity: Actor,
        previous_ai: Optional[BaseAI],
        turns_remaining: int = -1,
    ):
        super().__init__(entity)

        self.previous_ai = previous_ai
        self.turns_remaining = turns_remaining

    def perform(self) -> None:
        # Check to make sure the entity isn't already dead
        if not self.entity.is_alive:
            self.entity.ai = None
            return
        # Revert the AI back to the original state if the effect has run its course.
        if self.turns_remaining == 0:
            self.engine.message_log.add_message(
                f"The {self.entity.name} is no longer frozen."
            )
            self.entity.ai = self.previous_ai
        else:
            # do nothing
            self.turns_remaining -= 1
            pass

class ConfusedEnemy(BaseAI):
    """
    A confused enemy will stumble around aimlessly for a given number of turns, then revert back to its previous AI.
    If an actor occupies a tile it is randomly moving into, it will attack.
    """

    def __init__(
        self, entity: Actor, previous_ai: Optional[BaseAI], turns_remaining: int
    ):
        super().__init__(entity)

        self.previous_ai = previous_ai
        self.turns_remaining = turns_remaining

    def perform(self) -> None:
        # Check to make sure the entity isn't already dead
        if not self.entity.is_alive:
            self.entity.ai = None
            return
        # Revert the AI back to the original state if the effect has run its course.
        if self.turns_remaining <= 0:
            self.engine.message_log.add_message(
                f"The {self.entity.name} is no longer confused."
            )
            self.entity.ai = self.previous_ai
        else:
            # Pick a random direction
            direction_x, direction_y = random.choice(
                [
                    (-1, -1), # Northwest
                    (0, -1), # North
                    (1, -1), # Northeast
                    (-1, 0), # West
                    (1, 0), # East
                    (-1, 1), # Southwest
                    (0, 1), # South
                    (1, 1), # Southeast
                ]
            )

            self.turns_remaining -= 1

            # The actor will either try to move or attack in the chosen random direction.
            # Its possible the actor will just bump into the wall, wasting a turn.
            return BumpAction(self.entity, direction_x, direction_y,).perform()

class ClaudeRobichauxAI(HostileEnemy):
    def __init__(self, entity: Actor, time_till_shout: int = 6, debuff_amount: int = 1, defense_debuff_time: int = 20):
        super().__init__(entity)
        self.debuff_amount = debuff_amount
        self.base_time_till_shout = time_till_shout
        self.defense_debuff_time = defense_debuff_time

        self.current_time_till_shout = self.base_time_till_shout


    def perform(self) -> None:
        action = super().perform()

        player = self.entity.game_map.engine.player
        if self.current_target != None and self.current_target == player:
            self.current_time_till_shout -= 1
        if self.current_time_till_shout == 1:
            self.engine.message_log.add_message(
                f"Claude Robichaux is about to pop!"
            )
        elif self.current_time_till_shout == 0:
            debuff = Buff(defense_addition=-1)
            player.buff_container.add_buff(debuff)

            self.current_time_till_shout = self.base_time_till_shout
            self.engine.message_log.add_message(
                f"Claude Robichaux yells at the Player, lowering their defense by {self.base_time_till_shout}."
            )

        return action

class SlowHostileEnemy(HostileEnemy):

    def __init__(self, entity: Actor):
        super().__init__(entity)
        self.move_turn = True

    def perform(self) -> None:
        action = super().perform()
        if self.current_target != None:
            if action is MovementAction and self.move_turn:
               self.move_turn = not self.move_turn 
               return action
            else:
                pass
        else:
            self.move_turn = True
            return action