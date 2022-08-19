"""Handle the loading and initialization of game sessions."""
from __future__ import annotations

from typing import Dict

import lzma
import pickle
import traceback
import copy
from typing import Optional
import numpy as np

import tcod

import color
from engine import Engine
import entity_factories
import input_handlers
from game_map import GameWorld
from procgen import generate_dungeon
from floors.floor_settings import floor_settings, floor_name_constants

# Load the background image and remove the alpha channel.
background_image = tcod.image.load("menu_background.png")[:, :, :3]

def get_new_floor_order():
    floor_order = floor_name_constants.copy()
    np.random.shuffle(floor_order)
    return floor_order

def get_floor_settings():
    ordered_floor_settings = []
    floor_order = get_new_floor_order()
    for floor in floor_order:
        ordered_floor_settings.append(floor_settings.get(floor))
    return ordered_floor_settings


def new_game() -> Engine:
    """Return a brand new game session as an Engine instance."""
    map_width = 80
    map_height = 43

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    player = copy.deepcopy(entity_factories.player)

    engine = Engine(player=player)

    engine.game_world = GameWorld(
        engine=engine,
        max_rooms=max_rooms,
        room_min_size=room_min_size,
        room_max_size=room_max_size,
        map_width=map_width,
        map_height=map_height,
        ordered_settings=get_floor_settings(),
    )

    engine.game_world.generate_floor()
    engine.update_fov()

    engine.message_log.add_message(
        "Hello and welcome, adventurer, to yet another dungeon!", color.welcome_text
    )

    # test weapons
    test_weapons = []
    test_weapons.append(copy.deepcopy(entity_factories.plastic_scimitar))
    test_weapons.append(copy.deepcopy(entity_factories.big_chief_tablet))
    test_weapons.append(copy.deepcopy(entity_factories.lute))
    test_weapons.append(copy.deepcopy(entity_factories.chains))
    test_weapons.append(copy.deepcopy(entity_factories.brick))
    test_weapons.append(copy.deepcopy(entity_factories.broom))
    for weapon in test_weapons:
        weapon.parent = player.inventory
        player.inventory.items.append(weapon)

    # test body armor
    test_heads = []
    test_heads.append(copy.deepcopy(entity_factories.earing))
    test_heads.append(copy.deepcopy(entity_factories.hunting_cap))
    test_heads.append(copy.deepcopy(entity_factories.black_sunglasses))
    test_heads.append(copy.deepcopy(entity_factories.massage_board))
    for head in test_heads:
        head.parent = player.inventory
        player.inventory.items.append(head)

    # test body armor
    test_body = []
    test_body.append(copy.deepcopy(entity_factories.santa_outfit))
    test_body.append(copy.deepcopy(entity_factories.trench_coat_and_scarf))
    test_body.append(copy.deepcopy(entity_factories.police_uniform))
    test_body.append(copy.deepcopy(entity_factories.trixies_pajamas))
    for body in test_body:
        body.parent = player.inventory
        player.inventory.items.append(body)

    # test misc armor
    test_misc = []
    test_misc.append(copy.deepcopy(entity_factories.hot_dog_cart))
    test_misc.append(copy.deepcopy(entity_factories.picture_of_santas_mom))
    test_misc.append(copy.deepcopy(entity_factories.box_of_porno))
    test_misc.append(copy.deepcopy(entity_factories.letter_from_the_minx))
    test_misc.append(copy.deepcopy(entity_factories.yellow_cockatoo))
    test_misc.append(copy.deepcopy(entity_factories.a_picture_of_rex))
    test_misc.append(copy.deepcopy(entity_factories.a_picture_of_rex))
    for misc in test_misc:
        misc.parent = player.inventory
        player.inventory.items.append(misc)

    return engine

def load_game(filename: str) -> Engine:
    """Load an Engine instance from a file."""
    with open(filename, "rb") as f:
        engine = pickle.loads(lzma.decompress(f.read()))
    assert isinstance(engine, Engine)
    return engine


class MainMenu(input_handlers.BaseEventHandler):
    """Handle the main menu rendering and input."""

    def on_render(self, console: tcod.Console) -> None:
        """Render the main menu on a background image."""
        console.draw_semigraphics(background_image, 0, 0)

        console.print(
            console.width // 2,
            console.height // 2 - 4,
            "A CONFEDERACY OF DUNCES",
            fg=color.menu_title,
            alignment=tcod.CENTER,
        )
        console.print(
            console.width // 2,
            console.height - 2,
            "By Joel Davidson",
            fg=color.menu_title,
            alignment=tcod.CENTER,
        )

        menu_width = 24
        for i, text in enumerate(
            ["[N]ew game", "[C]ontinue last game", "[Q]uit"]
        ):
            console.print(
                console.width // 2,
                console.height // 2 - 2 + i,
                text.ljust(menu_width),
                fg=color.menu_text,
                bg=color.black,
                alignment=tcod.CENTER,
                bg_blend=tcod.BKGND_ALPHA(64),
            )

    def ev_keydown(
        self, event: tcod.event.KeyDown
    ) -> Optional[input_handlers.BaseEventHandler]:
        if event.sym in (tcod.event.K_q, tcod.event.K_ESCAPE):
            raise SystemExit()
        elif event.sym == tcod.event.K_c:
            try: 
                return input_handlers.MainGameEventHandler(load_game("savegame.sav"))
            except FileNotFoundError:
                return input_handlers.PopupMessage(self, "No saved game to load.")
            except Exception as exc:
                traceback.print_exc() # Print to stderr.
                return input_handlers.PopupMessage(self, f"Failed to load save:\n{exc}")
        elif event.sym == tcod.event.K_n:
            return input_handlers.MainGameEventHandler(new_game())

        return None