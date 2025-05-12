import zlib
from typing import Type, Dict

from replayparser.binaryreader import BinaryReader
from replayparser.versions.v6handlers import handle_announce, handle_antilead_shotgun, handle_basicinfo, handle_change_weapon, handle_chat, handle_dash, handle_die, handle_game_dead, handle_hpap_info, handle_massive, handle_peer_shot_sp, handle_peer_sp_motion, handle_player_join_battle, handle_reload, handle_round_state_change, handle_skill, handle_slash, handle_spawn, handle_worlditem_pickup

from .models import Replay, Command

_HEADER_REGISTRY: Dict[int, Type] = {}
_STAGE_REGISTRY:  Dict[int, Type] = {}
_PLAYER_REGISTRY: Dict[int, Type] = {}

def register_header(version: int, cls: Type):
    _HEADER_REGISTRY[version] = cls

def register_stage(version: int, cls: Type):
    _STAGE_REGISTRY[version] = cls

def register_player(version: int, cls: Type):
    _PLAYER_REGISTRY[version] = cls


def parse_replay(path: str) -> Replay:
    raw = open(path,'rb').read()
    try:
        data = zlib.decompress(raw)
    except:
        print("Failed to decompress, trying raw data")
        data = raw

    reader = BinaryReader(data)
    full = data

    magic, version = reader.read('<II')
    print(hex(magic))
    if magic != 0x95b1308a and magic != 0xdefbad:
        raise ValueError("Not a GunZ replay")
    HeaderCls = _HEADER_REGISTRY.get(version)
    if not HeaderCls:
        raise ValueError(f"No header registered for version {version}")
    header = HeaderCls.from_reader(reader)

    StageCls = _STAGE_REGISTRY.get(version)
    if not StageCls:
        raise ValueError(f"No stage registered for version {version}")
    stage = StageCls.from_reader(reader)

    cnt = reader.read_int32()
    PlayerCls = _PLAYER_REGISTRY[version]
    if not PlayerCls:
        raise ValueError(f"No player registered for version {version}")

    print("Player count: ", cnt)
    players = []
    for _ in range(cnt): 
        players.append(PlayerCls.from_reader(reader, full))

    reader.skip(0x4)
    commands = []
    packets = []
    while True:
        try:
            t = reader.read_float()
            reader.skip(4) # msvc padding because ?????
            # no other compiler adds padding here.
            # (yes, I checked.)
            sender = reader.read_uint32()
            sz     = reader.read_int32()
            data   = reader.read_bytes(sz)
            commands.append(Command(time=t, sender=sender, size=sz, data=data))
            tmp_reader = BinaryReader(data)
            _ = tmp_reader.read_int16()
            opcode = tmp_reader.read_uint16()
            # hack. for some reason chat packets aren't properly
            # attributed to sender.
            # Note: Not sure if still needed. Check.
            if opcode == 1520:
                tmp_reader.skip(5)
                sender = tmp_reader.read_uint16()

            packets.append({'opcode': opcode, 'buffer': data, 'sender': sender})
        except EOFError as e:
            print(e)
            break

    r = Replay(header=header, stage=stage, players=players, commands=commands, packets=packets)

    for c in r.packets:
        if c['opcode'] == 1402:
            r.players.append(handle_player_join_battle(c))

    unpacked = []
    sorted_basic_info = {}

    for c in r.packets:
        if c['opcode'] == 8016:
            bi = handle_basicinfo(c)
            unpacked.append((c['sender'], bi))
        elif c['opcode'] == 8022:
            ash = handle_antilead_shotgun(c)
            unpacked.append((c['sender'], ash))
        elif c['opcode'] == 1501:
            rsc = handle_round_state_change(c)
            unpacked.append((c['sender'], rsc))
        elif c['opcode'] == 10014:
            hpap = handle_hpap_info(c)
            unpacked.append((c['sender'], hpap))
        elif c['opcode'] == 10022:
            change_weapon = handle_change_weapon(c)
            unpacked.append((c['sender'], change_weapon))
        elif c['opcode'] == 10045:
            dash = handle_dash(c)
            unpacked.append((c['sender'], dash))
        elif c['opcode'] == 8000:
            slash = handle_slash(c)
            unpacked.append((c['sender'], slash))
        elif c['opcode'] == 10033:
            reload = handle_reload(c)
            unpacked.append((c['sender'], reload))
        elif c['opcode'] == 10035:
            peer_shot_sp = handle_peer_shot_sp(c)
            unpacked.append((c['sender'], peer_shot_sp))
        elif c['opcode'] == 10046:
            peer_sp_motion = handle_peer_sp_motion(c)
            unpacked.append((c['sender'], peer_sp_motion))
        elif c['opcode'] == 1516:
            spawn = handle_spawn(c)
            unpacked.append((c['sender'], spawn))
        elif c['opcode'] == 10041:
            death = handle_die(c)
            unpacked.append((c['sender'], death))
        elif c['opcode'] == 402:
            announcement = handle_announce(c)
            unpacked.append((c['sender'], announcement))
        elif c['opcode'] == 8801:
            massive = handle_massive(c)
            unpacked.append((c['sender'], massive))
        elif c['opcode'] == 10036:
            skill = handle_skill(c)
            unpacked.append((c['sender'], skill))
        elif c['opcode'] == 1520:
            chat = handle_chat(c)
            unpacked.append((c['sender'], chat))
        elif c['opcode'] == 1542:
            pickup = handle_worlditem_pickup(c)
            unpacked.append((c['sender'], pickup))
        elif c['opcode'] == 1512:
            game_dead = handle_game_dead(c)
            unpacked.append((c['sender'], game_dead))
    r.packets = unpacked
    return r
