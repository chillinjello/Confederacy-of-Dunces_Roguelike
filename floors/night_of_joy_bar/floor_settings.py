import sys

sys.path.append("../../")

from typing import Dict, List, Tuple, TYPE_CHECKING

import entity_factories
import color
from entity import Entity

colors = color.night_of_joy_bar_colors
item_chances: Dict[int, List[Tuple[Entity, int]]] = {
    0: [
        (entity_factories.jelly_donut, 10),
        (entity_factories.hot_dog, 10),
        (entity_factories.dr_nut, 10),
        (entity_factories.communiss_pamflet, 10),
        (entity_factories.ticket_to_the_movies, 10),
        (entity_factories.jazz_record, 10),
        (entity_factories.stained_sheet, 10),
        (entity_factories.dirty_cat, 10),
        (entity_factories.bowling_ball, 10),
        (entity_factories.oven_wine, 10),
        (entity_factories.the_consolation_of_philosophy, 10),
        (entity_factories.cross_item, 10),
        (entity_factories.nude_postcard, 10),
        (entity_factories.plastic_scimitar, 10),
        (entity_factories.big_chief_tablet, 10),
        (entity_factories.lute, 10),
        (entity_factories.chains, 10),
        (entity_factories.brick, 10),
        (entity_factories.broom, 10),
        (entity_factories.earing, 10),
        (entity_factories.hunting_cap, 10),
        (entity_factories.black_sunglasses, 10),
        (entity_factories.massage_board_item, 10),
        (entity_factories.santa_outfit, 10),
        (entity_factories.trench_coat_and_scarf, 10),
        (entity_factories.police_uniform, 10),
        (entity_factories.trixies_pajamas, 10),
        (entity_factories.hot_dog_cart, 10),
        (entity_factories.picture_of_santas_mom, 10),
        (entity_factories.box_of_porno, 10),
        (entity_factories.letter_from_the_minx, 10),
        (entity_factories.yellow_cockatoo, 10),
        (entity_factories.a_picture_of_rex, 10),
        (entity_factories.letter_to_mr_abelman, 10),
    ]
}
enemy_chances: Dict[int, List[Tuple[Entity, int]]] = {
    0: [
        (entity_factories.vagabond, 50),
        (entity_factories.sailor, 50),
        (entity_factories.bartender, 50)
    ],
}
bosses: Dict[int, List[Tuple[Entity, int]]] = {
    0: [
        (entity_factories.cockatoo, 50),
        (entity_factories.lana_lee, 50)
    ]
}

floor_settings = {
    "floor_name": "night_of_joy_bar",
    "colors": colors,
    "item_chances": item_chances,
    "enemy_chances": enemy_chances,
    "bosses": bosses
}