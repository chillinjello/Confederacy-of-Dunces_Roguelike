from components.base_component import BaseComponent
from components.buff_container import BuffContainer
import color

class Buff(BaseComponent):
    parent: BuffContainer

    def __init__(
        self,
        *,
        name: str = "[No Buff Name]",
        defense_multiplier: int = 1,
        defense_addition: int = 0,
        power_multiplier: int = 1,
        power_addition: int = 0,
        max_heath_addition: int = 0,
        buff_time: int = -1,
        time_expired_message: str = "",
    ):
        self.name = name

        self.defense_multiplier = defense_multiplier
        self.defense_addition = defense_addition
        
        self.power_multiplier = power_multiplier
        self.power_addition = power_addition

        self.max_health_addition = max_heath_addition

        self.buff_time = buff_time
        self.time_expired_message = time_expired_message

    def end_of_turn_affect(self):
        pass

    def display_expired_message(self):
        if (self.time_expired_message != ""):
            self.engine.message_log.add_message(
                self.time_expired_message
            )
        else:
            self.engine.message_log.add_message(
                f"The {self.name} buff wore off."
            )

    def tick_buff_timer(self):
        self.end_of_turn_affect()
        
        if (self.buff_time == -1):
            # This buff is permanent
            return
        self.buff_time -= 1
        if (self.buff_time == -1):
            self.parent.remove_buff(self)
            self.display_expired_message()


class SheetBuff(Buff):
    def __init__(
        self,
        *,
        name: str = "[No Buff Name]",
        defense_multiplier: int = 1,
        defense_addition: int = 5,
        power_multiplier: int = 1,
        power_addition: int = 0,
        max_health_addition: int = 0,
        buff_time: int = -1,
        time_expired_message: str = "",
        number_of_charges: int = 5,
    ):
        super().__init__(
            name = name,
            defense_multiplier = defense_multiplier,
            defense_addition = defense_addition,
            power_multiplier = power_multiplier,
            power_addition = power_addition,
            max_heath_addition=max_health_addition,
            buff_time = buff_time,
            time_expired_message = time_expired_message,
        )
        self.actor_previous_hp = self.engine.player.fighter.hp
        self.charges = number_of_charges


    def end_of_turn_affect(self):
        actor_current_hp = self.parent.parent.fighter.hp
        if (self.actor_previous_hp > actor_current_hp):
            self.charges -= 1
            if (self.charges == 0):
                self.parent.remove_buff(self)
                self.display_expired_message()
                return

        self.actor_previous_hp = actor_current_hp

        
class BleedBuff(Buff):
    def __init__(
        self,
        *,
        name: str = "[No Buff Name]",
        defense_multiplier: int = 1,
        defense_addition: int = 0,
        power_multiplier: int = 1,
        power_addition: int = 0,
        max_health_addition: int = 0,
        buff_time: int = -1,
        time_expired_message: str = "",
        damage: int = 1,
    ):
        super().__init__(
            name = name,
            defense_multiplier = defense_multiplier,
            defense_addition = defense_addition,
            power_multiplier = power_multiplier,
            power_addition = power_addition,
            max_heath_addition=max_health_addition,
            buff_time = buff_time,
            time_expired_message = time_expired_message,
        )
        self.damage = damage


    def end_of_turn_affect(self):
        self.parent.parent.fighter.take_damage(self.damage)
        self.engine.message_log.add_message(
            f"The {self.parent.parent.name} takes {self.damage} bleed damage.",
            color.player_atk 
        )

class BleedBuff(Buff):
    def __init__(
        self,
        *,
        name: str = "[No Buff Name]",
        defense_multiplier: int = 1,
        defense_addition: int = 0,
        power_multiplier: int = 1,
        power_addition: int = 0,
        max_health_addition: int = 0,
        buff_time: int = -1,
        time_expired_message: str = "",
        damage: int = 1,
    ):
        super().__init__(
            name = name,
            defense_multiplier = defense_multiplier,
            defense_addition = defense_addition,
            power_multiplier = power_multiplier,
            power_addition = power_addition,
            max_heath_addition=max_health_addition,
            buff_time = buff_time,
            time_expired_message = time_expired_message,
        )
        self.damage = damage


    def end_of_turn_affect(self):
        self.parent.parent.fighter.take_damage(self.damage)
        self.engine.message_log.add_message(
            f"The {self.parent.parent.name} takes {self.damage} bleed damage.",
            color.player_atk 
        )