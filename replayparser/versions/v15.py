from dataclasses import dataclass, field
from typing import List, Tuple

from replayparser.util.dump import hex_dump
from replayparser.versions.playerv15 import PlayerV15
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
class HeaderV15:
    version:  int = 15

    @classmethod
    def from_reader(cls, r: BinaryReader):
        return cls()

@dataclass
class StageV15:
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
        r.skip(8)
        print(hex(r.buf.tell()))

        raw_map_name = r.read_bytes(MAPNAME_LENGTH)
        hex_dump(raw_map_name)
        map_name = raw_map_name.split(b'\x00', 1)[0].decode('latin1', errors='ignore')

        raw_stage_name = r.read_bytes(STAGE_NAME_LENGTH)
        stage_name = raw_stage_name.split(b'\x00', 1)[0].decode('utf-8', errors='ignore')


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
        )

register_header(15, HeaderV15)
register_stage(15, StageV15)
register_player(15, PlayerV15)