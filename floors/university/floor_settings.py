import sys

sys.path.append("../../")

from typing import Dict, List, Tuple, TYPE_CHECKING
import entity_factories

from entity import Entity

colors = {}
item_chances: Dict[int, List[Tuple[Entity, int]]] = {
    0: [(entity_factories.bowling_ball, 100)]
}
enemy_chances: Dict[int, List[Tuple[Entity, int]]] = {
    0: [(entity_factories.professor_talc, 80)],
}

floor_settings = {
    "floor_name": "university",
    "colors": colors,
    "item_chances": item_chances,
    "enemy_chances": enemy_chances,
}