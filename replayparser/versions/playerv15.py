
from dataclasses import dataclass, field
from typing import List
from replayparser.binaryreader import BinaryReader


@dataclass
class PlayerV15:
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
    user_grade:     int
    premium_grade:  int
    clan_clid:      int
    uid:            int
    muid:           int
    equipped:       List[int] = field(default_factory=list)

    @classmethod
    def parse_player(cls, r: BinaryReader):
        raw_name = r.read_bytes(32)
        name = raw_name.split(b'\x00', 1)[0].decode('latin1', errors='ignore')

        raw_clan_name = r.read_bytes(16)
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
        equipped = [r.read_uint32() for _ in range(17)]
        ugrade = r.read_uint32()
        pgrade = r.read_uint32()
        clan_clid = r.read_uint32()
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
            user_grade=ugrade,
            premium_grade=pgrade,
            clan_clid=clan_clid,
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
            user_grade=player.user_grade,
            premium_grade=player.premium_grade,
            clan_clid=player.clan_clid,
            uid=uid_val,
            muid=muid,
            equipped=player.equipped
        )