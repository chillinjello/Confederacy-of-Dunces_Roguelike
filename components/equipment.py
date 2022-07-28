from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from components.base_component import BaseComponent
from equipment_types import EquipmentType


if TYPE_CHECKING:
    from entity import Actor, Item

class Equipment(BaseComponent):
    parent: Actor

    def __init__(self, weapon: Optional[Item] = None, armor: Optional[Item] = None):
        self.weapon = weapon
        self.armor = armor

    @property
    def defense_multiplier(self):
        bonus = 1

        if self.weapon is not None and self.weapon.equippable is not None:
            bonus *= self.weapon.equippable.defense_multiplier

        if self.armor is not None and self.armor.equippable is not None:
            bonus *= self.armor.equippable.defense_multiplier
        
        return bonus

    @property
    def defense_addition(self) -> int:
        bonus = 0

        if self.weapon is not None and self.weapon.equippable is not None:
            bonus += self.weapon.equippable.defense_addition

        if self.armor is not None and self.armor.equippable is not None:
            bonus += self.armor.equippable.defense_addition
        
        return bonus

    @property
    def power_multiplier(self):
        bonus = 1

        if self.weapon is not None and self.weapon.equippable is not None:
            bonus *= self.weapon.equippable.power_multiplier

        if self.armor is not None and self.armor.equippable is not None:
            bonus *= self.armor.equippable.power_multiplier
        
        return bonus
    
    @property
    def power_addition(self):
        bonus = 0

        if self.weapon is not None and self.weapon.equippable is not None:
            bonus += self.weapon.equippable.power_addition

        if self.armor is not None and self.armor.equippable is not None:
            bonus += self.armor.equippable.power_addition
        
        return bonus

    def item_is_equipped(self, item: Item) -> bool:
        return self.weapon == item or self.armor == item

    def unequip_message(self, item_name: str) -> None:
        self.parent.game_map.engine.message_log.add_message(
            f"You remove the {item_name}."
        )

    def equip_message(self, item_name: str) -> None: 
        self.parent.game_map.engine.message_log.add_message(
            f"You equip the {item_name}."
        )

    def equip_to_slot(self, slot: str, item: Item, add_message: bool) -> None:
        current_item = getattr(self, slot)

        if current_item is not None:
            self.unequip_from_slot(slot, add_message)

        setattr(self, slot, item)

        if add_message:
            self.equip_message(item.name)

    def unequip_from_slot(self, slot: str, add_message: bool) -> None:
        current_item = getattr(self, slot)

        if add_message:
            self.unequip_message(current_item.name)

        setattr(self, slot, None)

    def toggle_equip(self, equippable_item: Item, add_message: bool = True) -> None:
        if (
            equippable_item.equippable
            and equippable_item.equippable.equipment_type == EquipmentType.WEAPON
        ):
            slot = "weapon"
        else:
            slot = "armor"

        if getattr(self, slot) == equippable_item:
            self.unequip_from_slot(slot, add_message)
        else:
            self.equip_to_slot(slot, equippable_item, add_message)

    def use_weapon(self, attacker, target) -> None:
        if (self.weapon is not None):
            self.weapon.equippable.use_weapon(attacker, target)

    def take_hit(self, attacker, target) -> None:
        if (self.armor is not None):
            self.weapon.equippable.take_hit(attacker, target)