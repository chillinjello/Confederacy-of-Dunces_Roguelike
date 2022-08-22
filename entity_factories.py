from components.ai import HostileEnemy, InanimateObject
from components import consumable, equippable
from components.buff_container import BuffContainer
from components.equipment import Equipment
from components.fighter import Fighter
from components.inventory import Inventory
from components.level import Level
from entity import Actor, Item

player = Actor(
    char="@",
    color=(255, 255, 255), 
    name="Player", 
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=10, base_defense=0, base_power=2, base_valve=100, is_player=True),
    inventory=Inventory(capacity=26),
    buff_container=BuffContainer(),
    level=Level(level_up_base=200),
    hostile=Actor.FRIENDLY_ACTOR,
)

"""
French Quarter
"""

#
# Special Enemies
#

george = Actor(
    char="G", 
    color=(0, 127, 0), 
    name="George", 
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=5, base_defense=1, base_power=3),
    inventory=Inventory(capacity=26),
    buff_container=BuffContainer(),
    level=Level(xp_given=100),
    hostile=Actor.HOSTILE_ACTOR,
)
dorian_green = Actor(
    char="D", 
    color=(0, 127, 0), 
    name="Dorian Green", 
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=5, base_defense=1, base_power=3),
    inventory=Inventory(capacity=26),
    buff_container=BuffContainer(),
    level=Level(xp_given=100),
    hostile=Actor.HOSTILE_ACTOR,
)

#
# Common Enemies
#
sailor = Actor(
    char="s", 
    color=(0, 127, 0), 
    name="Dorian Green", 
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=5, base_defense=1, base_power=3),
    inventory=Inventory(capacity=26),
    buff_container=BuffContainer(),
    level=Level(xp_given=100),
    hostile=Actor.HOSTILE_ACTOR,
)
fop = Actor(
    char="f", 
    color=(0, 127, 0), 
    name="Fop", 
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=5, base_defense=1, base_power=3),
    inventory=Inventory(capacity=26),
    buff_container=BuffContainer(),
    level=Level(xp_given=100),
    hostile=Actor.HOSTILE_ACTOR,
)
lady_painter = Actor(
    char="l", 
    color=(0, 127, 0), 
    name="Lady Painter", 
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=5, base_defense=1, base_power=3),
    inventory=Inventory(capacity=26),
    buff_container=BuffContainer(),
    level=Level(xp_given=100),
    hostile=Actor.HOSTILE_ACTOR,
)

"""
Ignatius' House
"""
#
# Special Enemies
#

#
# Common Enemies
#

"""
Levy Factory
"""
#
# Special Enemies
#

#
# Common Enemies
#

"""
Night of Joy Bar
"""
#
# Special Enemies
#
cockatoo = Actor(
    char="C", 
    color=(0, 127, 0), 
    name="Cockatoo", 
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=5, base_defense=1, base_power=3),
    inventory=Inventory(capacity=26),
    buff_container=BuffContainer(),
    level=Level(xp_given=100),
    hostile=Actor.HOSTILE_ACTOR,
)
lana_lee = Actor(
    char="L", 
    color=(0, 127, 0), 
    name="Lana Lee", 
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=5, base_defense=1, base_power=3),
    inventory=Inventory(capacity=26),
    buff_container=BuffContainer(),
    level=Level(xp_given=100),
    hostile=Actor.HOSTILE_ACTOR,
)

#
# Common Enemies
#
vagabond = Actor(
    char="v", 
    color=(0, 127, 0), 
    name="Vagabond", 
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=5, base_defense=1, base_power=3),
    inventory=Inventory(capacity=26),
    buff_container=BuffContainer(),
    level=Level(xp_given=100),
    hostile=Actor.HOSTILE_ACTOR,
)
bartender = Actor(
    char="b", 
    color=(0, 127, 0), 
    name="Bartender", 
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=5, base_defense=1, base_power=3),
    inventory=Inventory(capacity=26),
    buff_container=BuffContainer(),
    level=Level(xp_given=100),
    hostile=Actor.HOSTILE_ACTOR,
)

"""
University
"""
#
# Special Enemies
#

#
# Common Enemies
#

orc = Actor(
    char="o", 
    color=(63, 127, 63), 
    name="Orc", 
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=3, base_defense=0, base_power=2),
    inventory=Inventory(capacity=26),
    buff_container=BuffContainer(),
    level=Level(xp_given=35),
    hostile=Actor.HOSTILE_ACTOR,
)
troll = Actor(
    char="T", 
    color=(0, 127, 0), 
    name="Troll", 
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=5, base_defense=1, base_power=3),
    inventory=Inventory(capacity=26),
    buff_container=BuffContainer(),
    level=Level(xp_given=100),
    hostile=Actor.HOSTILE_ACTOR,
)
cross_entity = Actor(
    char="t",
    color=(0, 127, 0),
    name="Cross",
    ai_cls=InanimateObject,
    equipment=Equipment(),
    fighter=Fighter(hp=100, base_defense=0, base_power=5),
    inventory=Inventory(capacity=26),
    buff_container=BuffContainer(),
    level=Level(xp_given=0),
    hostile=Actor.INANIMATE_ACTOR,
)

jelly_donut = Item(
    char="!",
    color=(207, 63, 255),
    name="Jelly Donut",
    consumable=consumable.JellyDonut(
        amount=15,
    )
)
hot_dog = Item(
    char="!",
    color=(207, 63, 255),
    name="Hot Dog",
    consumable=consumable.HotDog(
        amount=2,
    ),
)
dr_nut = Item(
    char="!",
    color=(127, 0, 255),
    name="Dr. Nut",
    consumable=consumable.DrNut(
        number_of_turns=20,
    )
)
communiss_pamflet = Item(
    char="!",
    color=(127, 0, 255),
    name="Communiss Pamflet",
    consumable=consumable.CommunissPamflet(
        range=10,
    ),
)
ticket_to_the_movies = Item(
    char="!",
    color=(127, 0, 255),
    name="Ticket to the Movies",
    consumable=consumable.TicketToTheMovies(),
)
jazz_record = Item(
    char="!",
    color=(127,0,255),
    name="Jazz Record",
    consumable=consumable.JazzRecord(
        number_of_turns=10,
    ),
)
stained_sheet = Item(
    char="!",
    color=(127,0,255),
    name="Stained Sheet",
    consumable=consumable.StainedSheet(),
)
dirty_cat = Item(
    char="!",
    color=(127,0,255),
    name="Dirty Cat",
    consumable=consumable.DirtyCat(
        power_modifier=2,
        max_health_modifier=-5,
    ),
)
bowling_ball = Item(
    char="~",
    color=(127,0,255),
    name="Bowling Ball",
    consumable=consumable.BowlingBall(
        base_damage=10,
        additional_damage=5,
        max_range=8
    ),
)
oven_wine = Item(
    char="~",
    color=(127, 0, 255),
    name="Oven Wine",
    consumable=consumable.OvenWine(
        damage=1,
        diameter=3,
        number_of_turns=5,
    ),
)
the_consolation_of_philosophy = Item(
    char="~",
    color=(127, 0, 255),
    name="The Consolation of Philosophy",
    consumable=consumable.TheConsolationOfPhilosophy(
        time_length=-1,
        max_range=15,
    ),
)
cross_item = Item(
    char="~",
    color=(127, 0, 255),
    name="Calvary Cross",
    consumable=consumable.Cross(
        health=50,
        max_range=15,
    ),
)
nude_postcard = Item(
    char="~",
    color=(127, 0, 255),
    name="Nude Postcard",
    consumable=consumable.NudePostcard(
        20,
        15,
    )
)

plastic_scimitar = Item(
    char="/", 
    color=(0, 191, 255), 
    name="Plastic Scimitar", 
    equippable=equippable.PlasticScimitar(
        power_addition=3
    )
)
big_chief_tablet = Item(
    char="/",
    color=(0, 191, 255),
    name="Big Cief Tablet",
    equippable=equippable.BigChiefTablet(
        power_addition=2,
        defense_subtraction=1
    )
)
lute = Item(
    char="/",
    color=(0, 191, 255),
    name="Lute",
    equippable=equippable.Lute(
        power_addition=2,
        splash_damage=2,
        splash_range=1
    )
)
chains = Item(
    char="/",
    color=(0, 191, 255),
    name="Chains",
    equippable=equippable.Chains(
        power_addition=3,
        freeze_length=3,
    )
)
brick = Item(
    char="/",
    color=(0, 191, 255),
    name="Brick",
    equippable=equippable.Brick(
        power_addition=5,
    )
)
broom = Item(
    char="/",
    color=(0, 191, 255),
    name="Broom",
    equippable=equippable.Broom(
        power_addition=3, 
        push_back_distance=2
    ),
)

"""
Head Armor
"""
earing = Item(
    char="{", 
    color=(139, 69, 19), 
    name="Earing", 
    equippable=equippable.Earing()
)
hunting_cap = Item(
    char="{", 
    color=(139, 69, 19), 
    name="Hunting Cap", 
    equippable=equippable.HuntingCap(
        valve_resistance_multiplier=1.5
    )
)
black_sunglasses = Item(
    char="{", 
    color=(139, 69, 19), 
    name="Black Sunglasses", 
    equippable=equippable.BlackSunglasses(
        power_addition=2
    )
)
massage_board = Item(
    char="{", 
    color=(139, 69, 19), 
    name="Massage Board", 
    equippable=equippable.MassageBoard(
        defense_addition=2
    )
)

"""
Body Armor
"""
santa_outfit = Item(
    char="[",
    color=(139, 69, 19),
    name="Santa Outfit",
    equippable=equippable.SantaOutfit(
        defense_addition=3,
    )
)
trench_coat_and_scarf = Item(
    char="[", 
    color=(139, 69, 19), 
    name="Trench Coat and Scarf", 
    equippable=equippable.TrenchCoatAndScarf(
        defense_addition=2,
        valve_resistance_multiplier=1.5
    )
)
police_uniform = Item(
    char="[",
    color=(139, 69, 19), 
    name="Police Uniform",
    equippable=equippable.PoliceUniform(
        defense_addition=2,
        miss_chance_addition=-0.5,
    )
)
trixies_pajamas = Item(
    char="[",
    color=(139, 69, 19),
    name="Trixies' Pajamas",
    equippable=equippable.TrixiesPajamas(
        power_addition=2,
        miss_chance_addition=-0.5,
    )
)

"""
Misc Equipment
"""
hot_dog_cart = Item(
    char="+", 
    color=(139, 69, 19), 
    name="Hot Dog Cart", 
    equippable=equippable.HotDogCart()
)
picture_of_santas_mom = Item(
    char="+",
    color=(139, 69, 19),
    name="Picture Of Santas Mom",
    equippable=equippable.PictureOfSantasMom(
        defense_addition=3,
        power_addition=-2,
    )
)
box_of_porno = Item(
    char="+",
    color=(139, 69, 19),
    name="Box of Porno",
    equippable=equippable.BoxOfPorno(
        defense_addition=2,
        max_health_addition=-5,
    )
)
letter_from_the_minx = Item(
    char="+",
    color=(139, 69, 19),
    name="Letter From the Minx",
    equippable=equippable.LetterFromTheMinx(
        power_addition=3
    )
)
yellow_cockatoo = Item(
    char="+",
    color=(139, 69, 19),
    name="Yellow Cockatoo",
    equippable=equippable.YellowCockatoo(
        damage=1,
        radius=5,
    )
)
a_picture_of_rex = Item(
    char="+",
    color=(139, 69, 19),
    name="A Picture of Rex",
    equippable=equippable.APictureOfRex(
        miss_chance_addition=0.5,
        power_addition=3,
        defense_addition=3,
    )
)
letter_to_mr_abelman = Item(
    char="+",
    color=(139, 69, 19),
    name="Letter To Mr. Abelman",
    equippable=equippable.LetterToMrAbelman(
        miss_chance_multiplier=0.0
    )
)