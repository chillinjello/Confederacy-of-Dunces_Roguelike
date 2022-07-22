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
    char="o",
    color=(207, 63, 255),
    name="Jelly Donut",
    consumable=consumable.JellyDonut()
)
hot_dog = Item(
    char="~",
    color=(207, 63, 255),
    name="Hot Dog",
    consumable=consumable.HotDog(),
)
dr_nut = Item(
    char="u",
    color=(127, 0, 255),
    name="Dr. Nut",
    consumable=consumable.DrNut()
)
communiss_pamflet = Item(
    char="m",
    color=(127, 0, 255),
    name="Communiss Pamflet",
    consumable=consumable.CommunissPamflet(),
)
ticket_to_the_movies = Item(
    char="*",
    color=(127, 0, 255),
    name="Ticket to the Movies",
    consumable=consumable.TicketToTheMovies(),
)
jazz_record = Item(
    char="=",
    color=(127,0,255),
    name="Jazz Record",
    consumable=consumable.JazzRecord(),
)
stained_sheet = Item(
    char="#",
    color=(127,0,255),
    name="Stained Sheet",
    consumable=consumable.StainedSheet(),
)


the_consolation_of_philosophy = Item(
    char="=",
    color=(127, 0, 255),
    name="The Consolation of Philosophy",
    consumable=consumable.TheConsolationOfPhilosophy(),
)
cross_item = Item(
    char="t",
    color=(127, 0, 255),
    name="Calvary Cross",
    consumable=consumable.Cross(),
)

# confusion_scroll = Item(
#     char="~",
#     color=(207, 63, 255),
#     name="Confusion Scroll",
#     consumable=consumable.ConfusionConsumable(number_of_turns=10),
# )
# health_potion = Item(
#     char="!",
#     color=(127, 0, 255),
#     name="Health Potion",
#     consumable=consumable.HealingConsumable(amount=4,)
# )
# lightning_scroll = Item(
#     char="~",
#     color=(255, 255, 0),
#     name="Lightning Scroll",
#     consumable=consumable.LightningDamageConsumable(damage=20, maximum_range=5),
# )
# fireball_scroll = Item(
#     char="~",
#     color=(255,0,0),
#     name="Fireball Scroll",
#     consumable=consumable.FireballDamageConsumable(damage=12, radius=3),
# )

dagger = Item(
    char="/", color=(0, 191, 255), name="Dagger", equippable=equippable.Dagger()
)

sword = Item(
    char="/", color=(0, 191, 255), name="Sword", equippable=equippable.Sword()
)

leather_armor = Item(
    char="[", color=(139, 69, 19), name="Leather Armor", equippable=equippable.LeatherArmor()
)

chain_mail = Item(
    char="[", color=(139, 69, 19), name="Chain Mail", equippable=equippable.ChainMail()
)