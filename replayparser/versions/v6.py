from dataclasses import dataclass, field
from typing import List, Tuple
from ..core import register_header, register_player, BinaryReader, register_stage

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


@dataclass
class PlayerV6:
    is_hero:        bool
    name:           str
    clan:           str
    clan_grade:     int
    clan_cont:      int
    char_num:       int
    level:          int
    sex:            int
    hair:           int
    face:           int
    xp:             int
    bp:             int
    gems:           int
    bonus_rate:     float
    prize:          int
    hp:             int
    ap:             int
    max_weight:     int
    safe_falls:     int
    fr:             int
    cr:             int
    er:             int
    wr:             int
    round_damage:   int
    ranked_wins:    int
    ranked_loses:   int
    ranked_points:  int
    ranked_rank:    int
    user_grade:     int
    premium_grade:  int
    clan_clid:      int
    discord_id:     str
    discord_avatar_url: str
    discord_avatar_checksum: int
    uid:            int
    muid:           int
    equipped:       List[int] = field(default_factory=list)

    @classmethod
    def parse_player(cls, r: BinaryReader):
        raw_name = r.read_bytes(32)
        name = raw_name.split(b'\x00', 1)[0].decode('latin1', errors='ignore')

        raw_clan_name = r.read_bytes(CLAN_NAME_LENGTH)
        clan = raw_clan_name.split(b'\x00', 1)[0].decode('latin1', errors='ignore')
        clan_grade = r.read_int32()
        clan_cont = r.read_uint16()
        char_num = r.read_int8()
        level = r.read_uint16()
        sex = r.read_uint8()
        hair = r.read_uint8()
        face = r.read_uint8()
        xp = r.read_uint32()
        bp = r.read_int32()
        gems = r.read_int32()
        bonus_rate = r.read_float()
        prize = r.read_uint16()
        hp = r.read_uint16()
        ap = r.read_uint16()
        max_wt = r.read_uint16()
        safe_fall = r.read_uint16()
        fr = r.read_uint16()
        cr = r.read_uint16()
        er = r.read_uint16()
        wr = r.read_uint16()
        round_damage = r.read_uint16()
        ranked_wins = r.read_int32()
        ranked_loses = r.read_int32()
        ranked_points = r.read_int32()
        ranked_rank = r.read_int32()
        equipped = [r.read_uint32() for _ in range(MMCIP_END)]
        ugrade = r.read_uint32()
        pgrade = r.read_uint32()
        clan_clid = r.read_uint32()
        raw_discord_id = r.read_bytes(32)
        discord_id = raw_discord_id.split(b'\x00', 1)[0].decode('latin1', errors='ignore')
        raw_discord_avatar_url = r.read_bytes(256)
        discord_avatar_url = raw_discord_avatar_url.split(b'\x00', 1)[0].decode('latin1', errors='ignore')
        discord_avatar_checksum = r.read_uint32()
        return cls(
            is_hero=False,
            name=name,
            clan=clan,
            clan_grade=clan_grade,
            clan_cont=clan_cont,
            char_num=char_num,
            level=level,
            sex=sex,
            hair=hair,
            face=face,
            xp=xp,
            bp=bp,
            gems=gems,
            bonus_rate=bonus_rate,
            prize=prize,
            hp=hp,
            ap=ap,
            max_weight=max_wt,
            safe_falls=safe_fall,
            fr=fr,
            cr=cr,
            er=er,
            wr=wr,
            round_damage=round_damage,
            ranked_wins=ranked_wins,
            ranked_loses=ranked_loses,
            ranked_points=ranked_points,
            ranked_rank=ranked_rank,
            user_grade=ugrade,
            premium_grade=pgrade,
            clan_clid=clan_clid,
            discord_id=discord_id,
            discord_avatar_url=discord_avatar_url,
            discord_avatar_checksum=discord_avatar_checksum,
            muid=0,
            uid=0
        )

    @classmethod
    def from_reader(cls, r: BinaryReader, full: bytes):
        is_hero, = r.read('<?')
        player = cls.parse_player(r)
        uid_val = r.read_uint32()
        muid = r.read_uint32()
        r.skip(293)

        return cls(
            is_hero=is_hero,
            name=player.name,
            clan=player.clan,
            clan_grade=player.clan_grade,
            clan_cont=player.clan_cont,
            char_num=player.char_num,
            level=player.level,
            sex=player.sex,
            hair=player.hair,
            face=player.face,
            xp=player.xp,
            bp=player.bp,
            gems=player.gems,
            bonus_rate=player.bonus_rate,
            prize=player.prize,
            hp=player.hp,
            ap=player.ap,
            max_weight=player.max_weight,
            safe_falls=player.safe_falls,
            fr=player.fr,
            cr=player.cr,
            er=player.er,
            wr=player.wr,
            round_damage=player.round_damage,
            ranked_wins=player.ranked_wins,
            ranked_loses=player.ranked_loses,
            ranked_points=player.ranked_points,
            ranked_rank=player.ranked_rank,
            user_grade=player.user_grade,
            premium_grade=player.premium_grade,
            clan_clid=player.clan_clid,
            discord_id=player.discord_id,
            discord_avatar_url=player.discord_avatar_url,
            discord_avatar_checksum=player.discord_avatar_checksum,
            uid=uid_val,
            muid=muid,
            equipped=player.equipped
        )

register_header(6, HeaderV6)
register_stage(6, StageV6)
register_player(6, PlayerV6)