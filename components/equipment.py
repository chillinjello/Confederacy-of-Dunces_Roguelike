from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from components.base_component import BaseComponent
from equipment_types import EquipmentType


if TYPE_CHECKING:
    from entity import Actor, Item

class Equipment(BaseComponent):
    parent: Actor

    def __init__(self, weapon: Optional[Item] = None, head_armor: Optional[Item] = None, body_armor: Optional[Item] = None, misc_equipment: Optional[Item] = None):
        self.weapon = weapon
        self.head_armor = head_armor
        self.body_armor = body_armor
        self.misc_equipment = misc_equipment

    @property
    def defense_multiplier(self):
        bonus = 1

        if self.weapon is not None and self.weapon.equippable is not None:
            bonus *= self.weapon.equippable.defense_multiplier

        if self.head_armor is not None and self.head_armor.equippable is not None:
            bonus *= self.head_armor.equippable.defense_multiplier

        if self.body_armor is not None and self.body_armor.equippable is not None:
            bonus *= self.body_armor.equippable.defense_multiplier

        if self.misc_equipment is not None and self.misc_equipment.equippable is not None:
            bonus *= self.misc_equipment.equippable.defense_multiplier
        
        return bonus

    @property
    def defense_addition(self) -> int:
        bonus = 0

        if self.weapon is not None and self.weapon.equippable is not None:
            bonus += self.weapon.equippable.defense_addition

        if self.head_armor is not None and self.head_armor.equippable is not None:
            bonus += self.head_armor.equippable.defense_addition
 
        if self.body_armor is not None and self.body_armor.equippable is not None:
            bonus += self.body_armor.equippable.defense_addition

        if self.misc_equipment is not None and self.misc_equipment.equippable is not None:
            bonus += self.misc_equipment.equippable.defense_addition

        return bonus

    @property
    def power_multiplier(self):
        bonus = 1

        if self.weapon is not None and self.weapon.equippable is not None:
            bonus *= self.weapon.equippable.power_multiplier

        if self.head_armor is not None and self.head_armor.equippable is not None:
            bonus *= self.head_armor.equippable.power_multiplier
        
        if self.body_armor is not None and self.body_armor.equippable is not None:
            bonus *= self.body_armor.equippable.power_multiplier

        if self.misc_equipment is not None and self.misc_equipment.equippable is not None:
            bonus *= self.misc_equipment.equippable.power_multiplier

        return bonus
    
    @property
    def power_addition(self):
        bonus = 0

        if self.weapon is not None and self.weapon.equippable is not None:
            bonus += self.weapon.equippable.power_addition

        if self.head_armor is not None and self.head_armor.equippable is not None:
            bonus += self.head_armor.equippable.power_addition
 
        if self.body_armor is not None and self.body_armor.equippable is not None:
            bonus += self.body_armor.equippable.power_addition       

        if self.misc_equipment is not None and self.misc_equipment.equippable is not None:
            bonus += self.misc_equipment.equippable.power_addition

        return bonus

    @property
    def max_health_addition(self):
        bonus = 0

        if self.weapon is not None and self.weapon.equippable is not None:
            bonus += self.weapon.equippable.max_health_addition

        if self.head_armor is not None and self.head_armor.equippable is not None:
            bonus += self.head_armor.equippable.max_health_addition
 
        if self.body_armor is not None and self.body_armor.equippable is not None:
            bonus += self.body_armor.equippable.max_health_addition

        if self.misc_equipment is not None and self.misc_equipment.equippable is not None:
            bonus += self.misc_equipment.equippable.max_health_addition

        return bonus

    @property
    def miss_chance_addition(self):
        bonus = 0

        if self.weapon is not None and self.weapon.equippable is not None:
            bonus += self.weapon.equippable.miss_chance_addition

        if self.head_armor is not None and self.head_armor.equippable is not None:
            bonus += self.head_armor.equippable.miss_chance_addition
 
        if self.body_armor is not None and self.body_armor.equippable is not None:
            bonus += self.body_armor.equippable.miss_chance_addition

        if self.misc_equipment is not None and self.misc_equipment.equippable is not None:
            bonus += self.misc_equipment.equippable.miss_chance_addition

        return bonus

    @property
    def miss_chance_multiplier(self):
        bonus = 1

        if self.weapon is not None and self.weapon.equippable is not None:
            bonus *= self.weapon.equippable.miss_chance_multiplier

        if self.head_armor is not None and self.head_armor.equippable is not None:
            bonus *= self.head_armor.equippable.miss_chance_multiplier
        
        if self.body_armor is not None and self.body_armor.equippable is not None:
            bonus *= self.body_armor.equippable.miss_chance_multiplier

        if self.misc_equipment is not None and self.misc_equipment.equippable is not None:
            bonus *= self.misc_equipment.equippable.miss_chance_multiplier

        return bonus

    def item_is_equipped(self, item: Item) -> bool:
        return self.weapon == item or self.head_armor == item or self.body_armor == item or self.misc_equipment == item

    def unequip_message(self, item_name: str) -> None:
        self.parent.game_map.engine.message_log.add_message(
            f"You remove the {item_name}."
        )

    def equip_message(self, item_name: str) -> None: 
        self.parent.game_map.engine.message_log.add_message(
            f"You equip the {item_name}."
        )

    def equip_to_slot(self, slot: str, item: Item, add_message: bool) -> None:
        current_item: Item = getattr(self, slot)

        if current_item is not None:
            self.unequip_from_slot(slot, add_message)

        setattr(self, slot, item)

        if add_message:
            self.equip_message(item.name)

    def unequip_from_slot(self, slot: str, add_message: bool) -> None:
        current_item: Item = getattr(self, slot)

        if add_message:
            self.unequip_message(current_item.name)

        setattr(self, slot, None)

    def toggle_equip(self, equippable_item: Item, add_message: bool = True) -> None:
        if (equippable_item.equippable):
            if (equippable_item.equippable.equipment_type == EquipmentType.WEAPON):
                slot = "weapon"
            elif (equippable_item.equippable.equipment_type == EquipmentType.BODY_ARMOR):
                slot = "body_armor"
            elif (equippable_item.equippable.equipment_type == EquipmentType.HEAD_ARMOR):
                slot = "head_armor"
            else:
                slot = "misc_equipment"

        if getattr(self, slot) == equippable_item:
            self.unequip_from_slot(slot, add_message)
        else:
            self.equip_to_slot(slot, equippable_item, add_message)

    def attack(self, attacker, target) -> None:
        if (self.weapon is not None):
            self.weapon.equippable.attack(attacker, target)
        if (self.body_armor is not None):
            self.body_armor.equippable.attack(attacker, target)
        if (self.head_armor is not None):
            self.head_armor.equippable.attack(attacker, target)
        if (self.misc_equipment is not None):
            self.misc_equipment.equippable.attack(attacker, target)

    def take_hit(self, attacker, target) -> None:
        if (self.weapon is not None):
            self.weapon.equippable.take_hit(attacker, target)
        if (self.body_armor is not None):
            self.body_armor.equippable.take_hit(attacker, target)
        if (self.head_armor is not None):
            self.head_armor.equippable.take_hit(attacker, target)
        if (self.misc_equipment is not None):
            self.misc_equipment.equippable.take_hit(attacker, target)