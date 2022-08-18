from __future__ import annotations
from gc import freeze

from typing import TYPE_CHECKING
import random

import color
from components.base_component import BaseComponent
from components.buff import BleedBuff, Buff
from components.ai import FrozenEnemy, ConfusedEnemy
from components.equipment import Equipment
from equipment_types import EquipmentType
from entity import Actor

if TYPE_CHECKING:
    from entity import Item

class Equippable(BaseComponent):
    parent: Item

    def __init__(
        self,
        equipment_type: EquipmentType,
        power_multiplier: int = 1,
        power_addition: int = 0,
        defense_multiplier: int = 1,
        defense_addition: int = 0,
        max_health_addition: int = 0,
        miss_chance_addition: float = 0,
        miss_chance_multiplier: float = 1,
        valve_resistance_addition: float = 0,
        valve_resistance_multiplier: float = 1,
    ):
        self.equipment_type = equipment_type

        self.power_addition = power_addition
        self.power_multiplier = power_multiplier

        self.defense_addition = defense_addition
        self.defense_multiplier = defense_multiplier

        self.max_health_addition = max_health_addition

        self.miss_chance_addition = miss_chance_addition
        self.miss_chance_multiplier = miss_chance_multiplier

        self.valve_resistance_addition = valve_resistance_addition
        self.valve_resistance_multiplier = valve_resistance_multiplier

    def equipment_message(self, attacker: Actor, message, *, target: Actor = None) -> None:
        if target is not None and not target.is_alive:
            # don't display a message because actor is already dead
            return

        text_color = color.equipment_neutural
        if (attacker == self.engine.player) :
            text_color = color.equipment_positive
        else:
            text_color = color.equipment_negative

        self.engine.message_log.add_message(
            message, text_color
        )

    def attack(self, attacker, target):
        pass

    def take_hit(self, attacker, target):
        pass

class Weapon(Equippable):
    def __init__(
        self, 
        power_multiplier: int = 1, 
        power_addition: int = 0, 
        defense_multiplier: int = 1, 
        defense_addition: int = 0,
        max_health_addition: int = 0,
        miss_chance_addition: float = 0,
        miss_chance_multiplier: float = 1,
    ):
        equipment_type=EquipmentType.WEAPON
        super().__init__(
            equipment_type, 
            power_multiplier, 
            power_addition, 
            defense_multiplier, 
            defense_addition,
            max_health_addition,
            miss_chance_addition,
            miss_chance_multiplier
        )

class Armor(Equippable):
    def __init__(
        self, 
        armor_type,
        power_multiplier: int = 1, 
        power_addition: int = 0, 
        defense_multiplier: int = 1, 
        defense_addition: int = 0,
        max_health_addition: int = 0,
        miss_chance_addition: int = 0,
        miss_chance_multiplier: int = 1,
    ):
        equipment_type=armor_type
        super().__init__(
            equipment_type, 
            power_multiplier, 
            power_addition, 
            defense_multiplier, 
            defense_addition,
            max_health_addition,
            miss_chance_addition,
            miss_chance_multiplier
        )

class HeadArmor(Armor):
    def __init__(
        self, 
        power_multiplier: int = 1, 
        power_addition: int = 0, 
        defense_multiplier: int = 1,
        defense_addition: int = 0,
        max_health_addition: int = 0,
        miss_chance_addition: int = 0,
        miss_chance_multiplier: int = 1,
    ):
        super().__init__(
            EquipmentType.HEAD_ARMOR, 
            power_multiplier, 
            power_addition, 
            defense_multiplier, 
            defense_addition,
            max_health_addition,
            miss_chance_addition,
            miss_chance_multiplier
        )

class BodyArmor(Armor):
    def __init__(
        self, 
        power_multiplier: int = 1, 
        power_addition: int = 0, 
        defense_multiplier: int = 1, 
        defense_addition: int = 0,
        max_health_addition: int = 0,
        miss_chance_addition: int = 0,
        miss_chance_multiplier: int = 1,
    ):
        super().__init__(
            EquipmentType.BODY_ARMOR, 
            power_multiplier, 
            power_addition, 
            defense_multiplier, 
            defense_addition,
            max_health_addition,
            miss_chance_addition,
            miss_chance_multiplier
        )

class MiscEquipment(Armor):
    def __init__(
        self, 
        power_multiplier: int = 1, 
        power_addition: int = 0, 
        defense_multiplier: int = 1, 
        defense_addition: int = 0,
        max_health_addition: int = 0,
        miss_chance_addition: int = 0,
        miss_chance_multiplier: int = 1,
    ):
        super().__init__(
            EquipmentType.MISC, 
            power_multiplier, 
            power_addition, 
            defense_multiplier, 
            defense_addition,
            max_health_addition,
            miss_chance_addition,
            miss_chance_multiplier
        )

"""
Weapons
"""

class PlasticScimitar(Weapon):
    def __init__(self, power_addition=3, bleed_damage=1, bleed_time=10) -> None:
        super().__init__(power_addition=power_addition)
        self.bleed_damage = bleed_damage
        self.bleed_time = bleed_time

    def attack(self, attacker: Actor, target: Actor) -> None:
        # give enemy bleed (de)buff
        debuf = BleedBuff(
            damage=self.bleed_damage,
            buff_time=self.bleed_time,
            time_expired_message=f"A Scimitar inflicted gash has healed on {target.name}'s mangled body."
        )
        target.buff_container.add_buff(debuf)
        self.equipment_message(attacker, f"The scimitar's mortal blow made {target.name} start to bleed", target=target)


class BigChiefTablet(Weapon):
    def __init__(self, power_addition=2, defense_subtraction: int = 1) -> None:
        super().__init__(power_addition=power_addition)
        self.defense_subtraction = defense_subtraction

    def attack(self, attacker: Actor, target: Actor) -> None:
        # give enemy -1 
        debuf = Buff(
            defense_addition=(-1 * self.defense_subtraction),
            time_expired_message="Time shouldn't expire for big chief debuf",
        )
        target.buff_container.add_buff(debuf)
        self.equipment_message(attacker, f"The Big Chief Tablet lowered {target.name}'s defense by {self.defense_subtraction}", target=target)


class Lute(Weapon):
    def __init__(self, power_addition=2, splash_damage: int = 2, splash_range: int = 1):
        super().__init__(power_addition=power_addition)
        self.splash_damage = splash_damage
        self.splash_range = splash_range

    def attack(self, attacker: Actor, target: Actor) -> None:
        x = target.x
        y = target.y
        actors = self.game_map.actors_within_range(x,y,self.splash_range)
        for actor in actors: 
            if actor == attacker or actor == target:
                continue
            actor.fighter.take_damage(self.splash_damage)
            self.equipment_message(attacker, f"{target.name.capitalize()} was hit by {self.splash_damage} splash damage.", target=target)

class Chains(Weapon):
    def __init__(self, power_addition=3, freeze_length=3):
        super().__init__(power_addition=power_addition)
        self.freeze_length = freeze_length

    def attack(self, attacker: Actor, target: Actor) -> None:
        if target.ai != None:
            target.ai = FrozenEnemy(
                entity=target,
                previous_ai=target.ai,
                turns_remaining=self.freeze_length,
            )
            self.equipment_message(attacker, f"{target.name} has been sensually chained to the ground for {self.freeze_length} turns.", target=target)

class Brick(Weapon):
    def __init__(self, power_addition=5):
        super().__init__(power_addition=power_addition)

class Broom(Weapon):
    def __init__(self, power_addition=3, push_back_distance=2):
        super().__init__(power_addition=power_addition)
        self.push_back_distance = push_back_distance

    def attack(self, attacker: Actor, target: Actor) -> None:
        a_x = attacker.x
        a_y = attacker.y
        t_x = target.x
        t_y = target.y

        dx = self.push_back_distance * (t_x - a_x)
        dy = self.push_back_distance * (t_y - a_y)

        while(True):
            new_x = target.x + dx
            new_y = target.y + dy
            print(str(new_x) + " " + str(new_y))
            if (self.game_map.in_bounds(new_x, new_y)
                and self.game_map.is_walkable(new_x, new_y) 
                and self.game_map.get_actor_at_location(new_x, new_y) is None
            ):
                target.place(new_x, new_y)
                self.equipment_message(attacker, f"{target.name} has been lightly swept back.", target=target)
                break 
            else:
                dx = dx // 2
                dy = dy // 2

            if dx == 0 and dy == 0:
                break

"""
Head Armor
"""

class Earing(HeadArmor):
    def __init__(self, confusion_chance: float = 0.1, confusion_time: int = 5, power_multiplier: int = 1, power_addition: int = 0, defense_multiplier: int = 1, defense_addition: int = 0):
        super().__init__(power_multiplier, power_addition, defense_multiplier, defense_addition)
        self.confusion_chance = confusion_chance
        self.confusion_time = confusion_time

    def attack(self, attacker, target):
        rnd = random.uniform(0,1)
        # roll confuse enemy
        if (rnd > self.confusion_chance and target.ai != None):
            target.ai = ConfusedEnemy(
                entity=target, previous_ai=target.ai, turns_remaining=self.confusion_time
            )
            self.equipment_message(attacker, f"The {attacker.name}'s radical earing confused the {target.name} for {self.confusion_time} turn(s).", target=target)

class HuntingCap(HeadArmor):
    def __init__(self, power_multiplier: int = 1, power_addition: int = 0, defense_multiplier: int = 1, defense_addition: int = 0):
        super().__init__(power_multiplier, power_addition, defense_multiplier, defense_addition)

class BlackSunglasses(HeadArmor):
    def __init__(self, power_multiplier: int = 1, power_addition: int = 0, defense_multiplier: int = 1, defense_addition: int = 0):
        super().__init__(power_multiplier, power_addition, defense_multiplier, defense_addition)

class MassageBoard(HeadArmor):
    def __init__(self, power_multiplier: int = 1, power_addition: int = 0, defense_multiplier: int = 1, defense_addition: int = 0):
        super().__init__(power_multiplier, power_addition, defense_multiplier, defense_addition)

"""
Body Armor
"""

class SantaOutfit(BodyArmor):
    def __init__(self, power_multiplier: int = 1, power_addition: int = 0, defense_multiplier: int = 1, defense_addition: int = 0):
        super().__init__(power_multiplier, power_addition, defense_multiplier, defense_addition)

class TrenchCoatAndScarf(BodyArmor):
    def __init__(self, power_multiplier: int = 1, power_addition: int = 0, defense_multiplier: int = 1, defense_addition: int = 0):
        super().__init__(power_multiplier, power_addition, defense_multiplier, defense_addition)

class PoliceUniform(BodyArmor):
    def __init__(self, power_multiplier: int = 1, power_addition: int = 0, defense_multiplier: int = 1, defense_addition: int = 0):
        super().__init__(power_multiplier, power_addition, defense_multiplier, defense_addition)

class TrixiesPajamas(BodyArmor):
    def __init__(self, power_multiplier: int = 1, power_addition: int = 0, defense_multiplier: int = 1, defense_addition: int = 0):
        super().__init__(power_multiplier, power_addition, defense_multiplier, defense_addition)

"""
Misc Equipment
"""

class HotDogCart(MiscEquipment):
    def __init__(self, power_multiplier: int = 1, power_addition: int = 0, defense_multiplier: int = 1, defense_addition: int = 0):
        super().__init__(power_multiplier, power_addition, defense_multiplier, defense_addition)

class PictureOfSantasMom(MiscEquipment):
    def __init__(self, power_multiplier: int = 1, power_addition: int = 0, defense_multiplier: int = 1, defense_addition: int = 0):
        super().__init__(power_multiplier, power_addition, defense_multiplier, defense_addition)

class BoxOfPorno(MiscEquipment):
    def __init__(self, power_multiplier: int = 1, power_addition: int = 0, defense_multiplier: int = 1, defense_addition: int = 0):
        super().__init__(power_multiplier, power_addition, defense_multiplier, defense_addition)

class LetterFromTheMinx(MiscEquipment):
    def __init__(self, power_multiplier: int = 1, power_addition: int = 0, defense_multiplier: int = 1, defense_addition: int = 0):
        super().__init__(power_multiplier, power_addition, defense_multiplier, defense_addition)

class YellowCockatoo(MiscEquipment):
    def __init__(self, power_multiplier: int = 1, power_addition: int = 0, defense_multiplier: int = 1, defense_addition: int = 0):
        super().__init__(power_multiplier, power_addition, defense_multiplier, defense_addition)

class APictureOfRex(MiscEquipment):
    def __init__(self, power_multiplier: int = 1, power_addition: int = 0, defense_multiplier: int = 1, defense_addition: int = 0):
        super().__init__(power_multiplier, power_addition, defense_multiplier, defense_addition)

class LetterToMrAbelman(MiscEquipment):
    def __init__(self, power_multiplier: int = 1, power_addition: int = 0, defense_multiplier: int = 1, defense_addition: int = 0):
        super().__init__(power_multiplier, power_addition, defense_multiplier, defense_addition)

