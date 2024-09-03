from dataclasses import asdict, dataclass, field
from typing import Union, Dict, List
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from config_loader import load_config
from datetime import datetime
from interactions import Embed, SlashContext, SlashContext, Snowflake
from localization.loc import Localization
import random

# Define the Database Schema for The World Machine:
@dataclass
class Collection:
    _id: Union[str, Snowflake]
        
    async def update(self, **kwargs):
        '''
        Update the current collection with the given kwargs.
        '''
        
        updated_data = await update_in_database(self, **kwargs)
        
        for k, v in asdict(updated_data).items():
            setattr(self, k, v)
        
    async def fetch(self):
        '''
        Fetch the current collection using id.
        '''
        
        self._id = str(self._id) # Make sure _id is string.
        
        return await fetch_from_database(self)
        
@dataclass
class UserData(Collection):
    wool: int = 5000
    suns: int = 0
    equipped_bg: str = 'Default'
    profile_description: str = 'Hello World!'
    badge_notifications: bool = True
    owned_treasures: Dict[str, int] = field(default_factory=lambda: {'journal': 5})
    owned_backgrounds: List[str] = field(default_factory=lambda: ['Default', 'Blue', 'Red', 'Yellow', 'Green', 'Pink'])
    owned_badges: List[str] = field(default_factory=list)
    ask_limit: int = 14
    last_asked: datetime = field(default_factory=lambda: datetime(2000, 1, 1, 0, 0, 0))
    daily_wool_timestamp: datetime = field(default_factory=lambda: datetime(2000, 1, 1, 0, 0, 0))
    daily_sun_timestamp: datetime = field(default_factory=lambda: datetime(2000, 1, 1, 0, 0, 0))
    times_asked: int = 0
    times_transmitted: int = 0
    times_shattered: int = 0
    translation_language: str = 'english'
    
    async def increment_value(self, key: str, amount: int = 1):
        'Increment a value within the UserData object.'
        value = asdict(self)[key]
        
        if type(value) != int:
            raise TypeError(f'Value for key "{key}" is not an integer.')
        
        return await self.update(**{key: value + amount})
    
    async def manage_wool(self, amount: int):
        if self.wool + amount <= 0:
            amount = 0
            
        return await self.increment_value('wool', amount)
@dataclass
class ServerData(Collection):
    transmit_channel: str = None
    transmittable_servers: Dict[str, str] = field(default_factory=dict)
    blocked_servers: List[str] = field(default_factory=list)
    anonymous: bool = False
    transmit_images: bool = True
    language: str = 'english'
    allow_ask: bool = True
    welcome_message: str = ''

@dataclass
class NikogotchiData(Collection):
    last_interacted: datetime = field(default_factory=lambda: datetime(2000, 1, 1, 0, 0, 0))
    hatched: datetime = field(default_factory=lambda: datetime(2000, 1, 1, 0, 0, 0))
    data: Dict[str, int] = field(default_factory=dict)
    nikogotchi_available: bool = False
    rarity: int = 0
    pancakes: int = 5
    golden_pancakes: int = 1
    glitched_pancakes: int = 0

@dataclass
class Nikogotchi(Collection):
    available: bool = False
    last_interacted: datetime = field(default_factory=lambda: datetime(2000, 1, 1, 0, 0, 0))
    hatched: datetime = field(default_factory=lambda: datetime(2000, 1, 1, 0, 0, 0))
    status: int = -1
    
    rarity: int = 0
    pancakes: int = 5
    golden_pancakes: int = 1
    glitched_pancakes: int = 0
    
    level: int = 0
    health: int = 50
    energy: int = 5
    hunger: int = 50
    cleanliness: int = 50
    happiness: int = 50
    
    attack: int = 5
    defense: int = 2
    
    max_health: int = 50
    max_hunger: int = 50
    max_cleanliness: int = 50
    max_happiness: int = 50
    
    nid: str = '?'
    name: str = 'NONAME'

    async def level_up(self, amount: int):
        
        level = self.level + amount
        
        data = []
        
        algorithm = int(amount * 5 * random.uniform(0.8, 1.4))
        data.append({'old': int(self.max_health), 'new': int(self.max_health) + int(algorithm), 'icon': '❤️'})
        self.max_health += algorithm
        
        algorithm = int(amount * 5 * random.uniform(0.8, 1.4))
        data.append({'old': int(self.max_hunger), 'new': int(self.max_hunger) + int(algorithm), 'icon': '🍴'})
        self.max_hunger += algorithm
        
        algorithm = int(amount * 5 * random.uniform(0.8, 1.4))
        data.append({'old': int(self.max_happiness), 'new': int(self.max_happiness) + int(algorithm), 'icon': '🫂'})
        self.max_happiness += algorithm
        
        algorithm = int(amount * 5 * random.uniform(0.8, 1.4))
        data.append({'old': int(self.max_cleanliness), 'new': int(self.max_cleanliness) + int(algorithm), 'icon': '🧽'})
        self.max_cleanliness += algorithm
        
        algorithm = int(amount * 2 * random.uniform(0.8, 1.4))
        data.append({'old': int(self.attack), 'new': int(self.attack) + int(algorithm), 'icon': '🗡️'})
        self.attack += algorithm
        
        algorithm = int(amount * 2 * random.uniform(0.8, 1.4))
        data.append({'old': int(self.defense), 'new': int(self.defense) + int(algorithm), 'icon': '🛡️'})
        self.defense += algorithm

        self.level = level
        
        self.health = self.max_health
        self.hunger = self.max_hunger
        self.happiness = self.max_happiness
        self.cleanliness = self.max_cleanliness
        
        await self.update(**asdict(self))
        
        return data
    
# ----------------------------------------------------

connection_uri = load_config('database')

connection = None

def create_connection():
    
    global connection
    
    if connection is not None:
        return
    
    connection = AsyncIOMotorClient(connection_uri, server_api=ServerApi('1'))

def get_database():
    
    if connection is None:
        create_connection()
        
    return connection.get_database('TheWorldMachine')

async def fetch_from_database(collection: Collection) -> Collection:
        
    db = get_database()
    
    result = await db.get_collection(collection.__class__.__name__).find_one({'_id': collection._id})
    
    if result is None:
        await new_entry(collection)
        return await fetch_from_database(collection)
    
    return collection.__class__(**result)

async def new_entry(collection: Collection):
    
    db = get_database()
    
    await db.get_collection(collection.__class__.__name__).update_one({'_id': collection._id}, {'$set': asdict(collection)}, upsert=True)

async def update_in_database(collection: Collection, **kwargs):
    db = get_database()
    
    # Fetch the existing document from the database
    existing_data = asdict(collection)

    # Update only the specified fields in the existing document
    updated_data = {**existing_data, **kwargs}
    
    # Update the document in the database
    await db.get_collection(collection.__class__.__name__).update_one(
        {'_id': collection._id}, 
        {'$set': updated_data}, 
        upsert=True
    )
    
    # Create and return an updated instance of the collection
    updated_instance = collection.__class__(**updated_data)
    return updated_instance

async def fetch_items():
    db = get_database()
    
    data = await db.get_collection('ItemData').find_one({"access": 'ItemData'})
    
    return data