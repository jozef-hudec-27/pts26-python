from enum import Enum
from dataclasses import dataclass, field

class Resource(Enum):
    COAL = 1
    OIL = 2
    GARBAGE = 3
    URANIUM = 4

class PlayerColor(Enum):
    RED = 1
    YELLOW = 2
    BLUE = 3
    GREEN = 4
    PURPLE = 5
    BLACK = 6

class PhaseStatus(Enum):
    PHASE_CONTINUES = 1
    PHASE_ENDS = 2
    GAME_ENDS = 3

class GamePhase(Enum):
    AUCTION_POWER_PLANTS = 1
    BUY_RESOURCES = 2
    BUY_HOUSES = 3
    BUREAUCRACY = 4
    GAME_END = 5

@dataclass
class PowerPlantNumber:
    number: int

@dataclass
class RequestError:
    description: str

@dataclass
class SerializedGameState:
    state: str

@dataclass
class PowerPlant:
    number: PowerPlantNumber
    resource_amount: int
    number_of_cities: int
    accepted_resources: list[Resource] = field(default_factory=list)
