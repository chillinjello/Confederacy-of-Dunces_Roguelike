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
    fighter=Fighter(hp=30, base_defense=2, base_power=5, base_valve=100, is_player=True),
    inventory=Inventory(capacity=26),
    buff_container=BuffContainer(),
    level=Level(level_up_base=200),
    hostile=Actor.FRIENDLY_ACTOR,
)

orc = Actor(
    char="o", 
    color=(63, 127, 63), 
    name="Orc", 
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=10, base_defense=0, base_power=5),
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
    fighter=Fighter(hp=16, base_defense=1, base_power=6),
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


leather_armor = Item(
    char="[", color=(139, 69, 19), name="Leather Armor", equippable=equippable.LeatherArmor()
)

chain_mail = Item(
    char="[", color=(139, 69, 19), name="Chain Mail", equippable=equippable.ChainMail()
)