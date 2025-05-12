from collections import Counter, defaultdict

from replayparser.binaryreader import BinaryReader
from replayparser.models import Announcement, AntileadShotgun, ChangeWeapon, Dash, Death, GameDead, HPAPInfo, Massive, PeerSPMotion, PeerShotSP, Reload, Round, Skill, Slash, Spawn, Message, WorldItemPickup
from replayparser.util.mget import get_shotgun_damage_info
from replayparser.util.basicinfo import unpack_basicinfo
from replayparser.util.mcommand import MPT, MCommand
from replayparser.versions.playerv6 import PlayerV6

def handle_basicinfo(c):
    """Opcode: 8016"""
    br = BinaryReader(c['buffer'])
    total_size = br.read_uint16()
    opcode = br.read_uint16()
    sender = br.read_uint16()
    br.skip(3)
    payload_len = total_size - 9
    buffer = br.read_bytes(payload_len)

    result = unpack_basicinfo(buffer, payload_len)
    if result is not None:
        return result
    return None


def handle_antilead_shotgun(c):
    """Opcode: 8022"""
    mcmd = MCommand.from_bytes(c['buffer'], [MPT.FLOAT, MPT.SHORT, MPT.BLOB])
    time = mcmd.get_parameter(0)
    sel_type = mcmd.get_parameter(1)
    data = mcmd.get_parameter(2)
    shot = get_shotgun_damage_info(data, 0)
    return shot


def handle_round_state_change(c):
    """Opcode: 1501"""
    nrm = BinaryReader(c['buffer'])
    nrm.skip(6)
    stage_id = nrm.read_uint32()
    nrm.skip(3)
    return Round(nrm.read_uint32(), nrm.read_uint32(), nrm.read_uint32())

def handle_player_join_battle(c):
    """Opcode: 8017"""
    nr = BinaryReader(c['buffer'])
    mcmd = MCommand.from_bytes(c['buffer'], [MPT.UCHAR, MPT.BLOB, MPT.UCHAR])
    br = BinaryReader(c['buffer'][0x22-0xC:])
    muid = br.read_uint32()
    player = PlayerV6.parse_player(BinaryReader(c['buffer'][0x22:]))
    player.muid = muid
    return player

def handle_hpap_info(c):
    """Opcode: 10014"""
    r = BinaryReader(c['buffer'][5:])
    return HPAPInfo(r.read_float(), r.read_float())

def handle_change_weapon(c):
    """Opcode: 10022"""
    r = BinaryReader(c['buffer'][5:])
    return ChangeWeapon(r.read_int32())

def handle_dash(c):
    """Opcode: 10045"""
    r = BinaryReader(c['buffer'][9:])
    posx = r.read_int16()
    posy = r.read_int16()
    posz = r.read_int16()
    dirx = r.read_int16()
    diry = r.read_int16()
    dirz = r.read_int16()
    seltype = r.read_uint8()
    return Dash(posx, posy, posz, dirx, diry, dirz, seltype)

def handle_slash(c):
    """Opcode: 8000"""
    r = BinaryReader(c['buffer'][5:])
    pos_x = r.read_float()
    pos_y = r.read_float()
    pos_z = r.read_float()
    dir_x = r.read_float()
    dir_y = r.read_float()
    dir_z = r.read_float()
    slash_type = r.read_uint32()
    shot_time = r.read_float()
    return Slash(pos_x, pos_y, pos_z, dir_x, dir_y, dir_z, slash_type, shot_time)

def handle_reload(c):
    """Opcode: 10033"""
    return Reload()

def handle_peer_shot_sp(c):
    """Opcode: 10035"""
    r = BinaryReader(c['buffer'][5:])
    time = r.read_float()
    pos_x = r.read_float()
    pos_y = r.read_float()
    pos_z = r.read_float()
    dir_x = r.read_float()
    dir_y = r.read_float()
    dir_z = r.read_float()
    type_ = r.read_uint32()
    sel_type = r.read_uint32()
    return PeerShotSP(time, pos_x, pos_y, pos_z, dir_x, dir_y, dir_z, type_, sel_type)

def handle_peer_sp_motion(c):
    """Opcode: 10046"""
    r = BinaryReader(c['buffer'][5:])
    sel_type = r.read_uint32()
    return PeerSPMotion(sel_type)

def handle_spawn(c):
    """Opcode: 1516"""
    r = BinaryReader(c['buffer'][9:])
    muid = r.read_uint32()
    pos_x = r.read_uint16()
    pos_y = r.read_uint16()
    pos_z = r.read_uint16()
    dir_x = r.read_uint16()
    dir_y = r.read_uint16()
    dir_z = r.read_uint16()
    return Spawn(muid, pos_x, pos_y, pos_z, dir_x, dir_y, dir_z)

def handle_die(c):
    """Opcode: 10041"""
    r = BinaryReader(c['buffer'][9:])
    muid = r.read_uint32()
    return Death(muid)

def handle_announce(c):
    """Opcode: 402"""
    r = BinaryReader(c['buffer'][5:])
    type_ = r.read_uint32()
    size = r.read_uint16()
    msg = r.read_string(size)
    return Announcement(type_, msg)

def handle_massive(c):
    """Opcode: 8801"""
    r = BinaryReader(c['buffer'][5:])
    time = r.read_float()
    pos_x = r.read_float()
    pos_y = r.read_float()
    pos_z = r.read_float()
    dir_x = r.read_float()
    dir_y = r.read_float()
    dir_z = r.read_float()
    return Massive(time, pos_x, pos_y, pos_z, dir_x, dir_y, dir_z)

def handle_skill(c):
    """Opcode: 10036"""
    r = BinaryReader(c['buffer'][5:])
    time = r.read_float()
    skill_id = r.read_int32()
    sel_type = r.read_int32()
    return Skill(time, skill_id, sel_type)

def handle_chat(c):
    """Opcode: 1520"""
    r = BinaryReader(c['buffer'][9:])
    sender = r.read_uint64()
    stage_uid = r.read_uint32()
    size = r.read_uint16()
    msg = r.read_string(size)
    team = r.read_int32()
    return Message(sender, stage_uid, msg, team)

def handle_worlditem_pickup(c):
    """Opcode: 1542"""
    r = BinaryReader(c['buffer'][9:])
    muid = r.read_uint32()
    item_id = r.read_uint32()
    return WorldItemPickup(muid, item_id)

def handle_game_dead(c):
    """Opcode: 1512"""
    r = BinaryReader(c['buffer'][9:])
    attacker = r.read_uint32()
    attacker_arg = r.read_uint32()
    attacker_weapon_type = r.read_uint32()
    r.skip(4) # ??
    victim = r.read_uint32()
    victim_arg = r.read_uint32()
    return GameDead(attacker, attacker_arg, attacker_weapon_type, victim, victim_arg)

