from entity import Actor

# from components.buff import Buff
from components.base_component import BaseComponent

class BuffContainer(BaseComponent):
    parent: Actor

    def __init__(self):
        self.buff_list = []

    def add_buff(self, buff: BaseComponent):
        buff.parent = self
        self.buff_list.append(buff)

    def remove_buff(self, buff: BaseComponent):
        self.buff_list.remove(buff)

    def tick(self):
        for buff in list(self.buff_list):
            buff.tick_buff_timer()

    @property
    def power_multiplier(self):
        total_power_mult = 1
        for buff in self.buff_list:
            total_power_mult *= buff.power_multiplier
        return total_power_mult

    @property
    def power_addition(self):
        total_power_addition = 0
        for buff in self.buff_list:
            total_power_addition += buff.power_addition
        return total_power_addition

    @property
    def defense_multiplier(self):
        total_defense_mult = 1
        for buff in self.buff_list:
            total_defense_mult *= buff.defense_multiplier
        return total_defense_mult

    @property
    def defense_addition(self):
        total_defense_addition = 0
        for buff in self.buff_list:
            total_defense_addition += buff.defense_addition
        return total_defense_addition

    @property
    def max_health_addition(self):
        total_max_health_addition = 0
        for buff in self.buff_list:
            total_max_health_addition += buff.max_health_addition
        return total_max_health_addition