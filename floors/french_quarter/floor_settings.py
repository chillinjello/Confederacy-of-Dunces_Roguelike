import sys

sys.path.append("../../")

from typing import Dict, List, Tuple, TYPE_CHECKING
import entity_factories

from entity import Entity

colors = {}
item_chances: Dict[int, List[Tuple[Entity, int]]] = {
    0: [(entity_factories.health_potion, 35)],
    2: [(entity_factories.confusion_scroll, 10)],
    4: [(entity_factories.lightning_scroll, 25), (entity_factories.sword, 5)],
    6: [(entity_factories.fireball_scroll, 25), (entity_factories.chain_mail, 15)],
}
enemy_chances: Dict[int, List[Tuple[Entity, int]]] = {
    0: [(entity_factories.orc, 80)],
    3: [(entity_factories.troll, 15)],
    5: [(entity_factories.troll, 30)],
    7: [(entity_factories.troll, 60)],
}

floor_settings = {
    "floor_name": "french_quarter",
    "colors": colors,
    "item_chances": item_chances,
    "enemy_chances": enemy_chances,
}