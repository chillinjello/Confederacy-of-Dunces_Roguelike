from components.base_component import BaseComponent
from components.buff_container import BuffContainer

class Buff(BaseComponent):
    parent: BuffContainer

    def __init__(
        self,
        *,
        defense_multiplier: int = 1,
        defense_addition: int = 0,
        power_multiplier: int = 1,
        power_addition: int = 0,
        buff_time: int = -1,
        time_expired_message: str = "",
    ):
        self.defense_multiplier = defense_multiplier
        self.defense_addition = defense_addition
        
        self.power_multiplier = power_multiplier
        self.power_addition = power_addition

        self.buff_time = buff_time
        self.time_expired_message = time_expired_message

    def end_of_turn_affect(self):
        pass

    def display_expired_message(self):
        if (self.time_expired_message != ""):
            self.engine.message_log.add_message(
                self.time_expired_message
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
        defense_multiplier: int = 1,
        defense_addition: int = 5,
        power_multiplier: int = 1,
        power_addition: int = 0,
        buff_time: int = -1,
        time_expired_message: str = "",
        number_of_charges: int = 5,
    ):
        super.__init__(
            defense_multiplier = defense_multiplier,
            defense_addition = defense_addition,
            power_multiplier = power_multiplier,
            power_addition = power_addition,
            buff_time = buff_time,
            time_expired_message = time_expired_message,
        )
        self.player_previous_hp = self.engine.player.fighter.hp
        self.charges = number_of_charges


    def end_of_turn_affect(self):
        player_current_hp = self.engine.player.fighter.hp
        if (self.player_previous_hp > player_current_hp):
            self.charges -= 1
            if (self.charges == 0):
                self.parent.remove_buff(self)
                self.display_expired_message()
                return

        self.player_previous_hp = player_current_hp

        
