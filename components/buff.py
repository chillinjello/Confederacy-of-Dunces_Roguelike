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
    ):
        self.defense_multiplier = defense_multiplier
        self.defense_addition = defense_addition
        
        self.power_multiplier = power_multiplier
        self.power_addition = power_addition

        self.buff_time = buff_time

    def tick_buff_timer(self):
        if (self.buff_time == -1):
            # This buff is permanent
            return
        self.buff_time -= 1
        if (self.buff_time == -1):
            self.parent.remove_buff(self)


    
