from dataclasses import dataclass
from enum import Enum, IntEnum, auto
from typing import List, Any

class MMatchWeaponType(Enum):
    MWT_NONE = 0

    # melee
    MWT_DAGGER = auto()
    MWT_DUAL_DAGGER = auto()
    MWT_KATANA = auto()
    MWT_GREAT_SWORD = auto()
    MWT_DOUBLE_KATANA = auto()

    # range
    MWT_PISTOL = auto()
    MWT_PISTOLx2 = auto()
    MWT_REVOLVER = auto()
    MWT_REVOLVERx2 = auto()
    MWT_SMG = auto()
    MWT_SMGx2 = auto()
    MWT_SHOTGUN = auto()
    MWT_SAWED_SHOTGUN = auto()
    MWT_RIFLE = auto()
    MWT_MACHINEGUN = auto()
    MWT_ROCKET = auto()
    MWT_SNIFER = auto()

    # custom
    MWT_MED_KIT = auto()
    MWT_REPAIR_KIT = auto()
    MWT_BULLET_KIT = auto()
    MWT_FLASH_BANG = auto()
    MWT_FRAGMENTATION = auto()
    MWT_SMOKE_GRENADE = auto()
    MWT_FOOD = auto()
    MWT_SKILL = auto()

    # custom - enchant
    MWT_ENCHANT_FIRE = auto()
    MWT_ENCHANT_COLD = auto()
    MWT_ENCHANT_LIGHTNING = auto()
    MWT_ENCHANT_POISON = auto()
    MWT_ENCHANT_STAR = auto()
    MWT_ENCHANT_END = auto()

    # custom - effect ring
    MWT_EFFECTRING_SWORDCOLOR = auto()
    MWT_EFFECTRING_SWORDENCHANT = auto()
    MWT_EFFECTRING_AURABERSERKER = auto()
    MWT_EFFECTRING_SHOTEFFECT = auto()
    MWT_EFFECTRING_DASHEFFECT = auto()

    MWT_END = auto()

class MMatchRoundResult(IntEnum):
    DRAW     = 0
    RED_WIN  = 1
    BLUE_WIN = 2
    END      = 3

class MMatchRoundState(IntEnum):
	MMATCH_ROUNDSTATE_PREPARE = 0
	MMATCH_ROUNDSTATE_COUNTDOWN = 1
	MMATCH_ROUNDSTATE_PLAY = 2
	MMATCH_ROUNDSTATE_FINISH = 3
	MMATCH_ROUNDSTATE_EXIT = 4,
	MMATCH_ROUNDSTATE_FREE = 5
	MMATCH_ROUNDSTATE_FAILED = 6
	MMATCH_ROUNDSTATE_END = 7

@dataclass
class Message:
    sender: int
    stage_uid: int
    message: str
    team: int

@dataclass
class Replay:
    header: Any
    stage:  Any
    players: List[Any]
    commands: List[Any]
    packets: List[Any]

@dataclass
class Command:
    time:   float
    sender: int
    size:   int
    data:   bytes

@dataclass
class Round:
    round: int
    state: MMatchRoundState
    arg:   MMatchRoundResult

@dataclass
class AntileadShotgun:
    target: int
    damage: int
    piercing_ratio: float
    damage_type: int

@dataclass
class HPAPInfo:
    hp: float
    ap: float

@dataclass
class ChangeWeapon:
    weapon_id: int

@dataclass
class Dash:
    pos_x: int 
    pos_y: int
    pos_z: int
    dir_x: int
    dir_y: int
    dir_z: int
    sel_type: int

@dataclass
class Slash:
    pos_x: float
    pos_y: float
    pos_z: float
    dir_x: float
    dir_y: float
    dir_z: float
    slash_type: int
    shot_time: float

@dataclass
class Reload:
    pass

@dataclass
class PeerShotSP:
    time:     float
    pos_x:    float
    pos_y:    float
    pos_z:    float
    dir_x:    float
    dir_y:    float
    dir_z:    float
    type_:    int
    sel_type: int

@dataclass
class PeerSPMotion:
    """????"""
    sel_type: int

@dataclass
class Spawn:
    muid:  int
    pos_x: float
    pos_y: float
    pos_z: float
    dir_x: float
    dir_y: float
    dir_z: float

@dataclass
class Death:
    muid: int

@dataclass
class Announcement:
    type_: int
    message: str

@dataclass
class Massive:
    time:  float
    pos_x: float
    pos_y: float
    pos_z: float
    dir_x: float
    dir_y: float
    dir_z: float

@dataclass
class Skill:
    time: float
    skill_id: int
    sel_type: int

@dataclass
class WorldItemPickup:
    muid: int
    item_id: int

@dataclass
class GameDead:
    attacker: int
    attacker_arg: int
    weapon_type: MMatchWeaponType
    victim: int
    victim_arg: int