from dataclasses import dataclass, field
from typing import List, Tuple

from replayparser.versions.playerv6 import PlayerV6
from ..core import register_header, register_player, register_stage
from ..binaryreader import BinaryReader

from rich.console import Console
from rich.table import Table

MMCIP_END        = 14
CLAN_NAME_LENGTH = 16
MAPNAME_LENGTH   = 32
STAGE_NAME_LENGTH   = 64

SIZE_REPLAY_HEADER_RG = 32
SIZE_REPLAY_STAGE_SETTING_NODE = 192
SIZE_REPLAY_PLAYER_INFO = 774

def get_mmatch_gametype_name(value):
    gametype_map = {
        0: "MMATCH_GAMETYPE_DEATHMATCH_SOLO",
        1: "MMATCH_GAMETYPE_DEATHMATCH_TEAM",
        2: "MMATCH_GAMETYPE_GLADIATOR_SOLO",
        3: "MMATCH_GAMETYPE_GLADIATOR_TEAM",
        4: "MMATCH_GAMETYPE_ASSASSINATE",
        5: "MMATCH_GAMETYPE_TRAINING",
        6: "MMATCH_GAMETYPE_SURVIVAL",
        7: "MMATCH_GAMETYPE_QUEST",
        8: "MMATCH_GAMETYPE_BERSERKER",
        9: "MMATCH_GAMETYPE_DEATHMATCH_TEAM2",
        10: "MMATCH_GAMETYPE_DUEL",
        11: "MMATCH_GAMETYPE_SKILLMAP",
        12: "MMATCH_GAMETYPE_GUNGAME",
        100: "MMATCH_GAMETYPE_ALL"
    }
    return gametype_map.get(value, f"UNKNOWN_GAMETYPE_{value}")


def opcode_to_packet(opcode: int) -> str:
    """
    Convert an opcode to a packet name.
    """
    packet_map = {
        1520: "CHAT",
        8016: "BASICINFO",
        10001: "PING",
        10002: "PONG",
        60000: "DMG_COUNTER",
        60001: "NOTIFY_HIT",
        50054: "REQ_HPAP",
        50055: "RESP_HPAP"
    }
    return packet_map.get(opcode, f"UNKNOWN_OPCODE_{opcode}")


@dataclass
class HeaderV6:
    version:  int = 6
    time:     int = 0
    major:    int = 0
    minor:    int = 0
    patch:    int = 0
    revision: int = 0

    def display_table(cls):
        table = Table(title="Header Information")
        table.add_column("Field", style="green", justify="left")
        table.add_column("Value", style="cyan", justify="left")

        for field, value in cls.__dict__.items():
            if not field.startswith("_"):
                table.add_row(field, str(value))

        console = Console()
        console.print(table)

    @classmethod
    def from_reader(cls, r: BinaryReader):
        time = r.read_uint64()

        major = r.read_uint32()
        minor = r.read_uint32()
        patch = r.read_uint32()
        revision = r.read_uint32()

        assert r.buf.tell() == SIZE_REPLAY_HEADER_RG, \
            f"V6 (iGunZ.net): expected {SIZE_REPLAY_HEADER_RG} bytes, got {r.buf.tell()}"

        return cls(time=time, major=major, minor=minor, patch=patch, revision=revision)


@dataclass
class StageV6:
    map_name: str
    map_idx: int
    stage_name: str
    gametype: str
    round_max: int
    limit_time: int
    limit_level: int
    max_players: int
    team_kill_enabled: bool
    team_win_the_point: bool
    forced_entry_enabled: bool
    auto_team_balancing: bool
    netcode: int
    force_hp_ap: bool
    hp: int
    ap: int
    no_flip: bool
    swords_only: bool
    refined_mode: bool
    team_rotate: bool

    def display_table(cls):
        table = Table(title="Stage Information")
        table.add_column("Field", style="green", justify="left")
        table.add_column("Value", style="cyan", justify="left")

        for field, value in cls.__dict__.items():
            if not field.startswith("_"):
                table.add_row(field, str(value))

        console = Console()
        console.print(table)

    @classmethod
    def from_reader(cls, r: BinaryReader):
        # This is Kappa.
        muid = r.read_uint64()

        raw_stage_name = r.read_bytes(STAGE_NAME_LENGTH)
        stage_name = raw_stage_name.split(b'\x00', 1)[0].decode('latin1', errors='ignore')

        raw_map_name = r.read_bytes(MAPNAME_LENGTH)
        map_name = raw_map_name.split(b'\x00', 1)[0].decode('latin1', errors='ignore')

        map_idx = r.read_uint32()
        gametype = get_mmatch_gametype_name(r.read_int32())
        round_max = r.read_int32()
        limit_time = r.read_int32()
        limit_level = r.read_int32()
        max_players = r.read_int32()
        team_kill_enabled = r.read_bool()
        team_win_the_point = r.read_bool()
        forced_entry_enabled = r.read_bool()
        auto_team_balancing = r.read_bool()
        netcode = r.read_uint8() & 0x03
        force_hp_ap = r.read_bool()
        hp = r.read_int32()
        ap = r.read_int32()
        no_flip = r.read_bool()
        swords_only = r.read_bool()
        refined_mode = r.read_bool()
        team_rotate = r.read_bool()
        reserved = r.read_bytes(46)

        return cls(
            map_name=map_name,
            map_idx=map_idx,
            stage_name=stage_name,
            gametype=gametype,
            round_max=round_max,
            limit_time=limit_time,
            limit_level=limit_level,
            max_players=max_players,
            team_kill_enabled=team_kill_enabled,
            team_win_the_point=team_win_the_point,
            forced_entry_enabled=forced_entry_enabled,
            auto_team_balancing=auto_team_balancing,
            netcode=netcode,
            force_hp_ap=force_hp_ap,
            hp=hp,
            ap=ap,
            no_flip=no_flip,
            swords_only=swords_only,
            refined_mode=refined_mode,
            team_rotate=team_rotate
        )

register_header(6, HeaderV6)
register_stage(6, StageV6)
register_player(6, PlayerV6)