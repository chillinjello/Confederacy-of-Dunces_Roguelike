from __future__ import annotations

from typing import TYPE_CHECKING

from components.base_component import BaseComponent
from equipment_types import EquipmentType

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
    ):
        self.equipment_type = equipment_type

        self.power_addition = power_addition
        self.power_multiplier = power_multiplier

        self.defense_addition = defense_addition
        self.defense_multiplier = defense_multiplier

class Dagger(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.WEAPON, power_bonus=2)

class Sword(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.WEAPON, power_bonus=4)

class LeatherArmor(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.ARMOR, defense_bonus=1)

class ChainMail(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.ARMOR, defense_bonus=3)