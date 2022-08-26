from typing import Dict

from floors.university.floor_settings import floor_settings as university_floor_settings
from floors.french_quarter.floor_settings import floor_settings as french_quarter_floor_settings
from floors.ignatius_house.floor_settings import floor_settings as ignatius_house_floor_settings
from floors.levy_factory.floor_settings import floor_settings as levy_factory_floor_settings
from floors.night_of_joy_bar.floor_settings import floor_settings as night_of_joy_bar_floor_settings

FRENCH_QUARTER = "FRENCH_QUARTER"
IGNATIUS_HOUSE = "IGNATIUS_HOUSE"
LEVY_FACTORY = "LEVY_FACTORY"
NIGHT_OF_JOY_BAR = "NIGHT_OF_JOY_BAR"
UNIVERSITY = "UNIVERSITY"
floor_name_constants = [
    # FRENCH_QUARTER,
    IGNATIUS_HOUSE,
    # LEVY_FACTORY,
    # NIGHT_OF_JOY_BAR,
    # UNIVERSITY,
]

floor_settings: Dict = {
    UNIVERSITY: university_floor_settings, 
    FRENCH_QUARTER: french_quarter_floor_settings,
    IGNATIUS_HOUSE: ignatius_house_floor_settings,
    LEVY_FACTORY: levy_factory_floor_settings,
    NIGHT_OF_JOY_BAR: night_of_joy_bar_floor_settings,
}