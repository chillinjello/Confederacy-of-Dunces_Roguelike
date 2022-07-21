import sys

sys.path.append("../../")

from typing import Dict, List, Tuple, TYPE_CHECKING
import entity_factories

from entity import Entity

colors = {}
item_chances: Dict[int, List[Tuple[Entity, int]]] = {
    0: [(entity_factories.the_consolation_of_philosophy, 100)]
}
enemy_chances: Dict[int, List[Tuple[Entity, int]]] = {
    0: [(entity_factories.orc, 80)],
    3: [(entity_factories.troll, 15)],
    5: [(entity_factories.troll, 30)],
    7: [(entity_factories.troll, 60)],
}

floor_settings = {
    "floor_name": "university",
    "colors": colors,
    "item_chances": item_chances,
    "enemy_chances": enemy_chances,
}