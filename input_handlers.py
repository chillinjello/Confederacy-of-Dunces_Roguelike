from __future__ import annotations

import os

from typing import Optional, TYPE_CHECKING, Callable, Tuple, Union

import tcod.event
import tcod.los

import actions
from actions import (
    Action,
    DropItem, 
    BumpAction, 
    WaitAction,
    PickupAction,
)
import color
from components.buff import Buff
from components.equipment import Equipment
import exceptions

if TYPE_CHECKING:
    from engine import Engine
    from entity import Item

MOVE_KEYS = {
    # Arrow keys.
    tcod.event.K_UP: (0, -1),
    tcod.event.K_DOWN: (0, 1),
    tcod.event.K_LEFT: (-1, 0),
    tcod.event.K_RIGHT: (1, 0),
    tcod.event.K_HOME: (-1, -1),
    tcod.event.K_END: (-1, 1),
    tcod.event.K_PAGEUP: (1, -1),
    tcod.event.K_PAGEDOWN: (1, 1),
    # Numpad keys.
    tcod.event.K_KP_1: (-1, 1),
    tcod.event.K_KP_2: (0, 1),
    tcod.event.K_KP_3: (1, 1),
    tcod.event.K_KP_4: (-1, 0),
    tcod.event.K_KP_6: (1, 0),
    tcod.event.K_KP_7: (-1, -1),
    tcod.event.K_KP_8: (0, -1),
    tcod.event.K_KP_9: (1, -1),
    # Vi keys.
    tcod.event.K_h: (-1, 0),
    tcod.event.K_j: (0, 1),
    tcod.event.K_k: (0, -1),
    tcod.event.K_l: (1, 0),
    tcod.event.K_y: (-1, -1),
    tcod.event.K_u: (1, -1),
    tcod.event.K_b: (-1, 1),
    tcod.event.K_n: (1, 1),
}

WAIT_KEYS = {
    tcod.event.K_PERIOD,
    tcod.event.K_KP_5,
    tcod.event.K_CLEAR,
}

CONFIRM_KEYS = {
    tcod.event.K_RETURN,
    tcod.event.K_KP_ENTER,
}

ActionOrHandler = Union[Action, "BaseEventHandler"]
"""
An event handler return value which can trigger an action or switch active handlers.

If a handler is returned then it will become the active handler for future events.
If an action is returned it will be attempted and if it's valid then
MainGameEventHandler will become the active handler.
"""

class BaseEventHandler(tcod.event.EventDispatch[ActionOrHandler]):
    def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
        """Handle an event and return the next active event handler."""
        state = self.dispatch(event)
        if isinstance(state, BaseEventHandler):
            return state
        assert not isinstance(state, Action), f"{self!r} can not handle actions."

    def on_render(self, console: tcod.Console) -> None:
        raise NotImplementedError()

    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        raise SystemExit()

class EventHandler(BaseEventHandler):
    def __init__(self, engine: Engine):
        self.engine = engine

    def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
        """Handle events for input handlers with an engine."""
        action_or_state = self.dispatch(event)
        if isinstance(action_or_state, BaseEventHandler):
            return action_or_state
        if self.handle_action(action_or_state):
            # A valid action was performed.
            if not self.engine.player.is_alive:
                # The player was killed sometime during or after the action.
                return GameOverEventHandler(self.engine)
            elif self.engine.player.level.requires_level_up:
                return LevelUpEventHandler(self.engine)
            return MainGameEventHandler(self.engine) # Return to the main handler.
        return self
    

    def handle_action(self, action: Optional[Action]) -> bool:
        """Handle actions returned from event methods.
        
        Returns True if the action will advance a turn.
        """
        if action is None:
            return False

        try: 
            action.perform()
        except exceptions.Impossible as exc:
            self.engine.message_log.add_message(exc.args[0], color.impossible)
            return False # Skip enemy turn on exceptions

        self.engine.handle_enemy_turns()

        # end of the turn actions for all actors
        for entity in set(self.engine.game_map.actors):
            entity.tick()

        # Reset enemy just hits
        for entity in set(self.engine.game_map.actors):
            entity.fighter.reset_just_hit()

        self.engine.update_fov()
        return True

    def ev_mousemotion(self, event: tcod.event.MouseMotion) -> Optional[T]:
        if self.engine.game_map.in_bounds(event.tile.x, event.tile.y):
            self.engine.mouse_location = event.tile.x, event.tile.y

    def on_render(self, console: tcod.Console) -> None:
        self.engine.render(console)


class MainGameEventHandler(EventHandler):
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        action: Optional[Action] = None

        key = event.sym
        modifier = event.mod

        player = self.engine.player

        if key == tcod.event.K_PERIOD and modifier & (
            tcod.event.KMOD_LSHIFT | tcod.event.KMOD_RSHIFT
        ):
            return actions.TakeStairsAction(player)

        if key in MOVE_KEYS:
            dx, dy = MOVE_KEYS[key]
            action = BumpAction(player, dx, dy)
        elif key in WAIT_KEYS:
            action = WaitAction(player)
        elif key == tcod.event.K_ESCAPE:
            raise SystemExit()
        elif key == tcod.event.K_v:
            return HistoryViewer(self.engine)
        elif key == tcod.event.K_g:
            action = PickupAction(player)
        elif key == tcod.event.K_i:
            return InventoryActivateHandler(self.engine)
        elif key == tcod.event.K_d:
            return InventoryDropHandler(self.engine)
        elif key == tcod.event.K_c:
            return CharacterScreenEventHandler(self.engine)
        elif key == tcod.event.K_SLASH:
            return LookHandler(self.engine)

        return action


class GameOverEventHandler(EventHandler):
    def on_quit(self) -> None:
        """Handle exiting out of a finished game."""
        if os.path.exists("savegame.sav"):
            os.remove("savegame.sav") # Deletes the active save file.
        raise exceptions.QuitWithoutSaving() # Avoid saving a finished game.

    def ev_quit(self, event: tcod.event.Quit) -> None:
        self.on_quit()

    def ev_keydown(self,event: tcod.event.KeyDown) -> Optional[Action]:
        if event.sym == tcod.event.K_ESCAPE:
            self.on_quit()

CURSOR_Y_KEYS = {
    tcod.event.K_UP: -1,
    tcod.event.K_DOWN: 1,
    tcod.event.K_PAGEUP: -10,
    tcod.event.K_PAGEDOWN: 10,
}

class HistoryViewer(EventHandler):
    """Print the history on a larger window which can be navigated."""

    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.log_length = len(engine.message_log.messages)
        self.cursor = self.log_length - 1

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)  # Draw the main state as the background.

        log_console = tcod.Console(console.width - 6, console.height - 6)

        # Draw a frame with a custom banner title.
        log_console.draw_frame(0, 0, log_console.width, log_console.height)
        log_console.print_box(
            0, 0, log_console.width, 1, "┤Message history├", alignment=tcod.CENTER
        )

        # Render the message log using the cursor parameter.
        self.engine.message_log.render_messages(
            log_console,
            1,
            1,
            log_console.width - 2,
            log_console.height - 2,
            self.engine.message_log.messages[: self.cursor + 1],
        )
        log_console.blit(console, 3, 3)

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[MainGameEventHandler]:
        # Fancy conditional movement to make it feel right.
        if event.sym in CURSOR_Y_KEYS:
            adjust = CURSOR_Y_KEYS[event.sym]
            if adjust < 0 and self.cursor == 0:
                # Only move from the top to the bottom when you're on the edge.
                self.cursor = self.log_length - 1
            elif adjust > 0 and self.cursor == self.log_length - 1:
                # Same with bottom to top movement.
                self.cursor = 0
            else:
                # Otherwise move while staying clamped to the bounds of the history log.
                self.cursor = max(0, min(self.cursor + adjust, self.log_length - 1))
        elif event.sym == tcod.event.K_HOME:
            self.cursor = 0  # Move directly to the top message.
        elif event.sym == tcod.event.K_END:
            self.cursor = self.log_length - 1  # Move directly to the last message.
        else:  # Any other key moves back to the main game state.
            return MainGameEventHandler(self.engine)
        return None

class AskUserEventHandler(EventHandler):
    """Handles user input for actions which require special input."""

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        """By default any key exits this input handler."""
        if event.sym in { # Ignore modifier keys.
            tcod.event.K_LSHIFT,
            tcod.event.K_RSHIFT,
            tcod.event.K_LCTRL,
            tcod.event.K_RCTRL,
            tcod.event.K_LALT,
            tcod.event.K_RALT, 
        }:
            return None
        return self.on_exit()

    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[ActionOrHandler]:
        """By default any mouse click exits this input handler."""
        return self.on_exit()

    def on_exit(self) -> Optional[ActionOrHandler]:
        """Called when the user is trying to exit or cancel an action.
        
        By default this returns to the main event handler.
        """
        self.engine.event_handler = MainGameEventHandler(self.engine)
        return MainGameEventHandler(self.engine)

class InventoryEventHandler(AskUserEventHandler):
    """This handler lets the user select an item.
    
    What happens then depends on the subclass.
    """

    TITLE = "<missing title>"

    def on_render(self, console: tcod.Console) -> None:
        """Render an inventory menu, which displays the items in the inventory, and the letter to select them.
        Will move to a different position based on where the position is located, so the player can always see where
        they are.
        """
        super().on_render(console)
        number_of_items_in_inventory = len(self.engine.player.inventory.items)

        height = number_of_items_in_inventory + 2

        if height <= 3:
            height = 3

        if self.engine.player.x <= 30:
            x = 40
        else: 
            x = 0

        y = 0

        width = len(self.TITLE) + 4

        console.draw_frame(
            x=x,
            y=y,
            width=width,
            height=height,
            title=self.TITLE,
            clear=True,
            fg=(255, 255, 255),
            bg=(0,0,0),
        )

        if number_of_items_in_inventory > 0:
            for i, item in enumerate(self.engine.player.inventory.items):
                item_key = chr(ord("a") + i)

                is_equipped = self.engine.player.equipment.item_is_equipped(item)

                item_string = f"({item_key}) {item.name}"

                if is_equipped:
                    item_string = f"{item_string} (E)"

                console.print(x + 1, y + i + 1, item_string)
        else: 
            console.print(x + 1, y + 1, "(Empty)")

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        player =self.engine.player
        key = event.sym
        index = key - tcod.event.K_a

        if 0 <= index <= 26:
            try: 
                selected_item = player.inventory.items[index]
            except IndexError:
                self.engine.message_log.add_message("Invalid entry.", color.invalid)
                return None
            return self.on_item_selected(selected_item)
        return super().ev_keydown(event)
    
    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        """Called when the user selects a valid item."""
        raise NotImplementedError()

class InventoryActivateHandler(InventoryEventHandler):
    """Handle using an inventory item."""

    TITLE = "Select an item to use"

    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        if item.consumable:
            # Return the action for the selected item.
            return item.consumable.get_action(self.engine.player)
        elif item.equippable:
            return actions.EquipAction(self.engine.player, item)
        else:
            return None

class InventoryDropHandler(InventoryEventHandler):
    """Handle dropping an inventory item."""

    TITLE = "Select an item to drop"

    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        """Drop this item."""
        return actions.DropItem(self.engine.player, item)

class SelectIndexHandler(AskUserEventHandler):
    """Handles asking the user for an index on the map."""

    def __init__(self, engine: Engine):
        """Sets the cursor to the player when this handler is constructed."""
        super().__init__(engine)
        player = self.engine.player
        engine.mouse_location = player.x, player.y

    def on_render(self, console: tcod.Console) -> None:
        """Highlight the tile under the cursor."""
        super().on_render(console)
        x, y = self.engine.mouse_location
        console.tiles_rgb["bg"][x, y] = color.white
        console.tiles_rgb["fg"][x, y] = color.black

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        """Check for key movement or confirmation keys."""
        key = event.sym
        if key in MOVE_KEYS:
            modifier = 1  # Holding modifier keys will speed up key movement.
            if event.mod & (tcod.event.KMOD_LSHIFT | tcod.event.KMOD_RSHIFT):
                modifier *= 5
            if event.mod & (tcod.event.KMOD_LCTRL | tcod.event.KMOD_RCTRL):
                modifier *= 10
            if event.mod & (tcod.event.KMOD_LALT | tcod.event.KMOD_RALT):
                modifier *= 20

            x, y = self.engine.mouse_location
            dx, dy = MOVE_KEYS[key]
            x += dx * modifier
            y += dy * modifier
            # Clamp the cursor index to the map size.
            x = max(0, min(x, self.engine.game_map.width - 1))
            y = max(0, min(y, self.engine.game_map.height - 1))
            self.engine.mouse_location = x, y
            return None
        elif key in CONFIRM_KEYS:
            return self.on_index_selected(*self.engine.mouse_location)
        return super().ev_keydown(event)

    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[ActionOrHandler]:
        """Left click confirms a selection."""
        if self.engine.game_map.in_bounds(*event.tile):
            if event.button == 1:
                return self.on_index_selected(*event.tile)
        return super().ev_mousebuttondown(event)

    def on_index_selected(self, x: int, y: int) -> Optional[ActionOrHandler]:
        """Called when an index is selected."""
        raise NotImplementedError()


class LookHandler(SelectIndexHandler):
    """Lets the player look around using the keyboard."""

    def on_index_selected(self, x: int, y: int) -> MainGameEventHandler:
        """Return to main handler."""
        return MainGameEventHandler(self.engine)

class SingleRangedAttackHandler(SelectIndexHandler):
    """Handles targeting a single enemy. Only the enemy selected will be affected."""

    def __init__(
        self, engine: Engine, callback: Callable[[Tuple[int, int]], Optional[Action]]
    ):
        super().__init__(engine)

        self.callback = callback

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        return self.callback((x,y))

class PathAttackHandler(SelectIndexHandler):
    """Handles targeting which applies to a path."""

    def __init__(
        self,
        engine: Engine,
        callback: Callable[[Tuple[int, int]], Optional[Action]],
        *,
        range: int = -1,
        starting_xy: Tuple[int, int],
        stop_at_unwalkable: False,
    ):
        super().__init__(engine)

        self.range = range
        self.callback = callback
        self.starting_xy = starting_xy
        self.stop_at_unwalkable = stop_at_unwalkable

    def on_render(self, console: tcod.Console) -> None:
        """Highlight the tile under teh cursor."""
        super().on_render(console)
        end_x, end_y = self.engine.mouse_location
        targeted_coords = tcod.los.bresenham(self.starting_xy, (end_x, end_y)).tolist()
        targeted_coords.pop(0)
        line_length = 1 # starts at 1 b/c ignoring player
        for x, y in targeted_coords:
            if self.stop_at_unwalkable:
                if not self.engine.game_map.is_walkable(x,y):
                    break

            if line_length > self.range:
                break
            
            console.tiles_rgb["bg"][x, y] = color.white
            console.tiles_rgb["fg"][x, y] = color.black

            line_length += 1

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        return self.callback((x, y))


class AreaRangedAttackHandler(SelectIndexHandler):
    """Handles targeting an area within a given radius. Any entity within the area will be affected."""

    def __init__(
        self,
        engine: Engine,
        callback: Callable[[Tuple[int, int]], Optional[Action]],
        *,
        radius: int = -1,
        diameter: int = -1,
        range: int = -1,
    ):
        super().__init__(engine)

        self.radius = radius
        self.callback = callback
        self.diameter = diameter

    def on_render(self, console: tcod.Console) -> None:
        """Highlight the tile under teh cursor."""
        super().on_render(console)

        x, y = self.engine.mouse_location

        # Draw a rectangle around the targeted area, so the player can see the affected tiles.
        if (self.radius > -1):
            console.draw_frame(
                x=x - self.radius - 1,
                y=y - self.radius - 1,
                width=self.radius ** 2,
                height=self.radius ** 2,
                fg=color.red,
                clear=False,
            )
        elif (self.diameter > -1):
            console.draw_frame(
                x=x - (self.diameter//2),
                y=y - (self.diameter//2),
                width=self.diameter,
                height=self.diameter,
                fg=color.red,
                clear=False,
            )

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        return self.callback((x, y))

class PopupMessage(BaseEventHandler):
    """Display a popup text window."""

    def __init__(self, parent_handler: BaseEventHandler, text: str):
        self.parent = parent_handler
        self.text = text
    
    def on_render(self, console: tcod.Console) -> None:
        """Render the parent and dim teh result, then print the message on top."""
        self.parent.on_render(console)
        console.tiles_rgb["fg"] //= 8
        console.tiles_rgb["bg"] //= 8

        console.print(
            console.width // 2,
            console.height // 2,
            self.text,
            fg=color.white,
            bg=color.black,
            alignment=tcod.CENTER,
        )

    def ev_keydown(self, event: tcod.event.KeyDOwn) -> Optional[BaseEventHandler]:
        """Any key returns to the parent handler."""
        return self.parent


class LevelUpEventHandler(AskUserEventHandler):
    TITLE = "Level Up"

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)

        if self.engine.player.x <= 30:
            x = 40
        else: 
            x = 0

        console.draw_frame(
            x=x,
            y=0,
            width=35,
            height=8,
            title=self.TITLE,
            clear=True,
            fg=(255, 255, 255),
            bg=(0, 0, 0),
        )

        console.print(x=x + 1, y=1, string="Congratulations! You level up!")
        console.print(x=x + 1, y=2, string="Select an attribute to increase.")

        console.print(
            x=x + 1,
            y=4,
            string=f"a) Constitution (+20 HP, from {self.engine.player.fighter.max_hp})",
        )
        console.print(
            x=x + 1,
            y=5,
            string=f"b) Strength (+1 attack, from {self.engine.player.fighter.power})",
        )
        console.print(
            x=x + 1,
            y=6,
            string=f"c) Agility (+1 defense, from {self.engine.player.fighter.defense})",
        )

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        player = self.engine.player
        key = event.sym
        index = key - tcod.event.K_a

        if 0 <= index <= 2:
            if index == 0:
                player.level.increase_base_max_hp()
            elif index == 1:
                player.level.increase_power()
            else:
                player.level.increase_defense()
        else:
            self.engine.message_log.add_message("Invalid entry.", color.invalid)

            return None

        return super().ev_keydown(event)

    def ev_mousebuttondown(
        self, event: tcod.event.MouseButtonDown
    ) -> Optional[ActionOrHandler]:
        """Don't allow the player to click to exit the menu, like normal."""
        return None

class CharacterScreenEventHandler(AskUserEventHandler):
    TITLE = "Character Information"

    def display_equipment(self, console: tcod.Console, equipment: Equipment, current_line: int, x: int, name: str) -> int:
        if (equipment):
            console.print(
                x=x + 1, y=current_line, string=f"{name}: {equipment.parent.name}"
            )
            current_line += 1
            attack_p = f"Attack (+): {equipment.power_addition}" if equipment.power_addition != 0 else ""
            if attack_p != "":
                console.print(
                    x=x + 3, y=current_line, string=attack_p
                )
                current_line += 1
            attack_mult = f"Attack (%): {equipment.power_multiplier * 100}" if equipment.power_multiplier != 1 else ""
            if attack_mult != "":
                console.print(
                    x=x + 3, y=current_line, string=attack_mult
                )
                current_line += 1
            defense_p = f"Defense (+): {equipment.defense_addition}" if equipment.defense_addition != 0 else ""
            if defense_p != "":
                console.print(
                    x=x + 3, y=current_line, string=defense_p
                )
                current_line += 1
            defense_mult = f"Defense (%): {equipment.defense_multiplier * 100}" if equipment.defense_multiplier != 1 else ""
            if defense_mult != "":
                console.print(
                    x=x + 3, y=current_line, string=defense_mult
                )
                current_line += 1
            miss_chance_p = f"Miss Chance (+): {equipment.miss_chance_addition}" if equipment.miss_chance_addition != 0 else ""
            if miss_chance_p != "":
                console.print(
                    x=x + 3, y=current_line, string=miss_chance_p
                )
                current_line += 1
            miss_chance_mult = f"Miss Chance (%): {equipment.miss_chance_multiplier * 100}" if equipment.miss_chance_multiplier != 1 else ""
            if miss_chance_mult != "":
                console.print(
                    x=x + 3, y=current_line, string=miss_chance_mult
                )
                current_line += 1
            valve_resistance_p = f"Valve Resistance (+): {equipment.valve_resistance_addition}" if equipment.valve_resistance_addition != 0 else ""
            if valve_resistance_p != "":
                console.print(
                    x=x + 3, y=current_line, string=valve_resistance_p
                )
                current_line += 1
            valve_resistance_mult = f"Valve Resistance (%): {equipment.valve_resistance_multiplier * 100}" if equipment.valve_resistance_multiplier != 1 else ""
            if valve_resistance_mult != "":
                console.print(
                    x=x + 3, y=current_line, string=valve_resistance_mult
                )
                current_line += 1
            max_health_p = f"Max Health (+): {equipment.max_health_addition}" if equipment.max_health_addition != 0 else ""
            if max_health_p != "":
                console.print(
                    x=x + 3, y=current_line, string=max_health_p
                )
                current_line += 1
        else:
            console.print(
                x=x + 1, y=current_line, string=f"{name}: None"
            )
        return current_line

    def display_buff(self, console: tcod.Console, buff: Buff, current_line: int, x: int) -> int:
        console.print(
            x=x + 1, y=current_line, string=f"{buff.parent.name}"
        )
        current_line += 1
        attack_p = f"Attack (+): {buff.power_addition}" if buff.power_addition != 0 else ""
        if attack_p != "":
            console.print(
                x=x + 3, y=current_line, string=attack_p
            )
            current_line += 1
        attack_mult = f"Attack (%): {buff.power_multiplier * 100}" if buff.power_multiplier != 1 else ""
        if attack_mult != "":
            console.print(
                x=x + 3, y=current_line, string=attack_mult
            )
            current_line += 1
        defense_p = f"Defense (+): {buff.defense_addition}" if buff.defense_addition != 0 else ""
        if defense_p != "":
            console.print(
                x=x + 3, y=current_line, string=defense_p
            )
            current_line += 1
        defense_mult = f"Defense (%): {buff.defense_multiplier * 100}" if buff.defense_multiplier != 1 else ""
        if defense_mult != "":
            console.print(
                x=x + 3, y=current_line, string=defense_mult
            )
            current_line += 1
        miss_chance_p = f"Miss Chance (+): {buff.miss_chance_addition}" if buff.miss_chance_addition != 0 else ""
        if miss_chance_p != "":
            console.print(
                x=x + 3, y=current_line, string=miss_chance_p
            )
            current_line += 1
        miss_chance_mult = f"Miss Chance (%): {buff.miss_chance_multiplier * 100}" if buff.miss_chance_multiplier != 1 else ""
        if miss_chance_mult != "":
            console.print(
                x=x + 3, y=current_line, string=miss_chance_mult
            )
            current_line += 1
        valve_resistance_p = f"Valve Resistance (+): {buff.valve_resistance_addition}" if buff.valve_resistance_addition != 0 else ""
        if valve_resistance_p != "":
            console.print(
                x=x + 3, y=current_line, string=valve_resistance_p
            )
            current_line += 1
        valve_resistance_mult = f"Valve Resistance (%): {buff.valve_resistance_multiplier * 100}" if buff.valve_resistance_multiplier != 1 else ""
        if valve_resistance_mult != "":
            console.print(
                x=x + 3, y=current_line, string=valve_resistance_mult
            )
            current_line += 1
        max_health_p = f"Max Health (+): {buff.max_health_addition}" if buff.max_health_addition != 0 else ""
        if max_health_p != "":
            console.print(
                x=x + 3, y=current_line, string=max_health_p
            )
            current_line += 1
        return current_line

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)

        if self.engine.player.x <= 30:
            x = 40
        else:
            x = 0

        y = 0

        width = len(self.TITLE) + 15

        console.draw_frame(
            x=x,
            y=y,
            width=width,
            height=9,
            title=self.TITLE,
            clear=True,
            fg=(255, 255, 255),
            bg=(0, 0, 0),
        )

        console.print(
            x=x + 1, y=y + 1, string=f"Level: {self.engine.player.level.current_level}"
        )
        console.print(
            x=x + 1, y=y + 2, string=f"XP: {self.engine.player.level.current_xp}"
        )
        console.print(
            x=x + 1, 
            y=y + 3, 
            string=f"XP for next Level: {self.engine.player.level.experience_to_next_level}"
        )
        console.print(
            x=x + 1, y=y + 4, string=f"Attack: {self.engine.player.fighter.power}"
        )
        console.print(
            x=x + 1, y=y + 5, string=f"Defense: {self.engine.player.fighter.defense}"
        )
        console.print(
            x=x + 1, y=y + 6, string=f"Miss Chance: {self.engine.player.fighter.miss_chance}%"
        )
        console.print(
            x=x + 1, y=y + 7, string=f"Valve Resistance: {self.engine.player.fighter.valve_resistance}"
        )

        # Print current items
        console.print(
            x=x + 1, y=y + 9, string=f"---Inventory---"
        )

        current_line = y + 10
        # Head
        current_line = self.display_equipment(console, self.engine.player.equipment.head_armor.equippable, current_line, x, "Head")

        # Body
        current_line = self.display_equipment(console, self.engine.player.equipment.body_armor.equippable, current_line, x, "Body")

        # Misc
        current_line = self.display_equipment(console, self.engine.player.equipment.misc_equipment.equippable, current_line, x, "Misc")

        # Print Buffs
        current_line += 1
        console.print(
            x=x + 1, y=current_line, string=f"---Buffs---"
        )
        current_line += 1
        if len(self.engine.player.buff_container.buff_list) > 0:
            console.print(
                x=x + 1, y=current_line, string="None"
            )
            current_line += 1
        else:
            for buff in self.engine.player.buff_container.buff_list:
                current_line = self.display_buff(console, buff, current_line, x)
