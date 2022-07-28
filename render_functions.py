from __future__ import annotations

from typing import TYPE_CHECKING

import color

if TYPE_CHECKING:
    from tcod import Console
    from engine import Engine
    from game_map import GameMap
    
def render_health_bar(
    console: Console, current_value: int, maximum_value: int, total_width: int
) -> None:
    bar_width = 0
    if (maximum_value != 0):
        bar_width = int(float(current_value) / maximum_value * total_width)

    console.draw_rect(x=0, y=45, width=total_width, height=1, ch=1, bg=color.bar_empty)

    if bar_width > 0:
        console.draw_rect(
            x=0, y=45, width=bar_width, height=1, ch=1, bg=color.bar_filled
        )
    
    console.print(
        x=1, y=45, string=f"HP: {current_value}/{maximum_value}", fg=color.bar_text
    )

def render_valve_bar(
    console: Console, 
    valve_level: int, 
    current_valve: int, 
    max_valve: int,
    total_width: int
):
    valve_string = ""
    valve_background_color = color.bar_empty

    if (valve_level == 0):
        valve_string = "Fully Closed"
        valve_background_color = color.valve_bar_0
    elif (valve_level == 1):
        valve_string = "Partially Closed"
        valve_background_color = color.valve_bar_1
    elif (valve_level == 2):
        valve_string = "Halfway Open"
        valve_background_color = color.valve_bar_2
    elif (valve_level == 3):
        valve_string = "Nearly Open"
        valve_background_color = color.valve_bar_3
    else:
        valve_string = "100% Clear"
        valve_background_color = color.valve_bar_4

    bar_width = 0
    if (max_valve != 0):
        bar_width = int(float(current_valve) / max_valve * total_width)

    console.draw_rect(x=0, y=46, width=total_width, height=1, ch=1, bg=color.bar_empty)

    console.draw_rect(x=0, y=46, width=bar_width, height=1, ch=1, bg=valve_background_color)

    console.print(
        x=1, y=46, string=f"Valve: {valve_string}", fg=color.bar_text
    )

def get_names_at_location(x: int, y: int, game_map: GameMap) -> str:
    if not game_map.in_bounds(x, y) or not game_map.visible[x, y]:
        return ""

    names = ", ".join(
        entity.name for entity in game_map.entities if entity.x == x and entity.y == y
    )

    return names.capitalize()

def render_names_at_mouse_location(
    console: Console, x: int, y: int, engine: Engine
) -> None:
    mouse_x, mouse_y = engine.mouse_location

    names_at_mouse_location = get_names_at_location(
        x=mouse_x, y=mouse_y, game_map=engine.game_map
    )

    console.print(x=x, y=y, string=names_at_mouse_location)

def render_dungeon_level(
    console: Console, dungeon_level: int, location: Tuple[int, int]
) -> None:
    """
    Render the level the player is currently on, at the given location.
    """
    x, y = location

    console.print(x=x, y=y, string=f"Dungeon level: {dungeon_level}")