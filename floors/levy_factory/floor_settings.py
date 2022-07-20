import sys

sys.path.append("../../")

from typing import Dict, List, Tuple, TYPE_CHECKING
import entity_factories

from entity import Entity

colors = {}
item_chances: Dict[int, List[Tuple[Entity, int]]] = {
    0: [(entity_factories.dr_nut, 50), (entity_factories.jelly_donut, 50)]
}
enemy_chances: Dict[int, List[Tuple[Entity, int]]] = {
    0: [(entity_factories.orc, 80)],
    3: [(entity_factories.troll, 15)],
    5: [(entity_factories.troll, 30)],
    7: [(entity_factories.troll, 60)],
}

floor_settings = {
    "floor_name": "levy_factory",
    "colors": colors,
    "item_chances": item_chances,
    "enemy_chances": enemy_chances,
}