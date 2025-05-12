from dataclasses import dataclass, field
from typing import List, Tuple
from ..core import register_header, register_player, register_stage
from ..binaryreader import BinaryReader

# I'm not sure *where* these bytes are written in the client's source,
# but they indicate the end of each character information struct in *some* (most) 
# v4 replays.
CHARINFO_MARKER  = b'\x7A\x44\x00\x00\x7A\x44'
CHARINFO_PAD     = 90
MMCIP_END        = 12
CLAN_NAME_LENGTH = 16
MAPNAME_LENGTH   = 32

@dataclass
class HeaderV7:
    """
    Version 1 header: we only care about the version number here,
    since parse_replay has already consumed the magic and version.
    """
    version: int = 4

    @classmethod
    def from_reader(cls, r: BinaryReader):
        return cls()

@dataclass
class StageV7:
    """
    Version 1 stage record, exactly the 68-byte struct:
    we only expose map_name and map_idx here.
    """
    map_name: str
    map_idx:  int

    @classmethod
    def from_reader(cls, r: BinaryReader):
        start = r.buf.tell()

        r.read('<II')

        raw_name = r.read_bytes(MAPNAME_LENGTH)
        map_name = raw_name.split(b'\x00', 1)[0].decode('latin1', errors='ignore')

        map_idx, = r.read('<b')

        pad = (4 - ((r.buf.tell() - start) % 4)) % 4
        if pad:
            r.skip(pad)

        r.skip(5*4 + 3*1)

        tail = 68 - (r.buf.tell() - start)
        if tail > 0:
            r.skip(tail)

        return cls(map_name=map_name, map_idx=map_idx)


@dataclass
class PlayerV7:
    is_hero:    bool
    name:       str
    clan:       str
    clan_grade: int
    clan_cont:  int
    char_num:   int
    level:      int
    sex:        int
    hair:       int
    face:       int
    xp:         int
    bp:         int
    bonus_rate: float
    prize:      int
    hp:         int
    ap:         int
    max_weight: int
    safe_falls: int
    fr:         int
    cr:         int
    er:         int
    wr:         int
    equipped:   List[int]   = field(default_factory=list)
    user_grade: int         = 0
    clan_clid:  int         = 0
    uid:        int         = 0

    @classmethod
    def from_reader(cls, r: BinaryReader, full: bytes):
        is_hero, = r.read('<?')
        start    = r.buf.tell()

        pos = full.find(CHARINFO_MARKER, start)
        if pos < 0:
            raise ValueError("Couldn't find end-of-char-info marker")
        end    = pos + len(CHARINFO_MARKER) + 1
        length = end - start

        raw_info = r.read_bytes(length)
        info     = BinaryReader(raw_info)

        name     = info.read_string(32)
        clan     = info.read_string(CLAN_NAME_LENGTH)

        clan_grade, = info.read_int32(),
        clan_cont,  = info.read_uint16(),
        char_num,   = info.read_int8(),
        level,      = info.read_uint16(),
        sex,        = info.read_uint8(), 
        hair,       = info.read_uint8(), 
        face,       = info.read_uint8(), 

        xp          = info.read_uint32()
        bp          = info.read_int32()
        bonus_rate  = info.read_float()
        prize, hp, ap, max_wt, safe_fall, fr, cr, er, wr = (
            info.read_uint16() for _ in range(9)
        )

        equipped = [info.read_uint32() for _ in range(MMCIP_END)]

        user_grade = info.read_uint32()
        clan_clid  = info.read_uint32()

        info.skip(4)
        uid_val = info.read_uint32()

        r.skip(CHARINFO_PAD + 83)

        return cls(
            is_hero=is_hero,
            name=name, clan=clan,
            clan_grade=clan_grade,
            clan_cont=clan_cont,
            char_num=char_num,
            level=level,
            sex=sex,
            hair=hair,
            face=face,
            xp=xp,
            bp=bp,
            bonus_rate=bonus_rate,
            prize=prize,
            hp=hp,
            ap=ap,
            max_weight=max_wt,
            safe_falls=safe_fall,
            fr=fr, cr=cr, er=er, wr=wr,
            equipped=equipped,
            user_grade=user_grade,
            clan_clid=clan_clid,
            uid=uid_val
        )

register_header(7, HeaderV7)
register_stage(7, StageV7)
register_player(7, PlayerV7)