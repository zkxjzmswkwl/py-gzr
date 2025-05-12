import zlib
from typing import Type, Dict

from replayparser.binaryreader import BinaryReader
from replayparser.util.dump import hex_dump
from replayparser.versions.v6handlers import handle_announce, handle_antilead_shotgun, handle_basicinfo, handle_change_weapon, handle_chat, handle_dash, handle_die, handle_game_dead, handle_hpap_info, handle_massive, handle_peer_shot, handle_peer_shot_sp, handle_peer_sp_motion, handle_player_join_battle, handle_reload, handle_round_state_change, handle_skill, handle_slash, handle_spawn, handle_worlditem_pickup

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
    if magic != 0x95b1308a and magic != 0xdefbad:
        raise ValueError("Not a GunZ replay")
    HeaderCls = _HEADER_REGISTRY.get(version)
    if not HeaderCls:
        raise ValueError(f"No header registered for version {version}")
    header = HeaderCls.from_reader(reader)
    print(header)

    StageCls = _STAGE_REGISTRY.get(version)
    if not StageCls:
        raise ValueError(f"No stage registered for version {version}")
    stage = StageCls.from_reader(reader)
    print(stage)

    cnt = reader.read_int32()
    PlayerCls = _PLAYER_REGISTRY[version]
    if not PlayerCls:
        raise ValueError(f"No player registered for version {version}")

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

            packets.append({'time': t, 'opcode': opcode, 'buffer': data, 'sender': sender})
        except EOFError as e:
            break

    r = Replay(header=header, stage=stage, players=players, commands=commands, packets=packets)

    for c in r.packets:
        if c['opcode'] == 1402:
            r.players.append(handle_player_join_battle(c))

    unpacked = []
    for c in r.packets:
        opcode = c['opcode']
        time = c['time']
        if opcode == 8016:
            bi = handle_basicinfo(c)
            unpacked.append((time, c['sender'], opcode, bi))
        elif opcode == 8022:
            ash = handle_antilead_shotgun(c)
            unpacked.append((time, c['sender'], opcode, ash))
        elif opcode == 1501:
            rsc = handle_round_state_change(c)
            unpacked.append((time, c['sender'], opcode, rsc))
        elif opcode == 10014:
            hpap = handle_hpap_info(c)
            unpacked.append((time, c['sender'], opcode, hpap))
        elif opcode == 10022:
            change_weapon = handle_change_weapon(c)
            unpacked.append((time, c['sender'], opcode, change_weapon))
        elif opcode == 10045:
            dash = handle_dash(c)
            unpacked.append((time, c['sender'], opcode, dash))
        elif opcode == 8000:
            slash = handle_slash(c)
            unpacked.append((time, c['sender'], opcode, slash))
        elif opcode == 10033:
            reload = handle_reload(c)
            unpacked.append((time, c['sender'], opcode, reload))
        elif opcode == 10035:
            peer_shot_sp = handle_peer_shot_sp(c)
            unpacked.append((time, c['sender'], opcode, peer_shot_sp))
        elif opcode == 10046:
            peer_sp_motion = handle_peer_sp_motion(c)
            unpacked.append((time, c['sender'], opcode, peer_sp_motion))
        elif opcode == 1516:
            spawn = handle_spawn(c)
            unpacked.append((time, c['sender'], opcode, spawn))
        elif opcode == 10041:
            death = handle_die(c)
            unpacked.append((time, c['sender'], opcode, death))
        elif opcode == 402:
            announcement = handle_announce(c)
            unpacked.append((time, c['sender'], opcode, announcement))
        elif opcode == 8801:
            massive = handle_massive(c)
            unpacked.append((time, c['sender'], opcode, massive))
        elif opcode == 10036:
            skill = handle_skill(c)
            unpacked.append((time, c['sender'], opcode, skill))
        elif opcode == 1520:
            chat = handle_chat(c)
            unpacked.append((time, c['sender'], opcode, chat))
        elif opcode == 1542:
            pickup = handle_worlditem_pickup(c)
            unpacked.append((time, c['sender'], opcode, pickup))
        elif opcode == 1512:
            game_dead = handle_game_dead(c)
            unpacked.append((time, c['sender'], opcode, game_dead))
        elif opcode == 10034:
            hex_dump(c['buffer'])
            peer_shot = handle_peer_shot(c)
            unpacked.append((time, c['sender'], opcode, peer_shot))
            print(peer_shot)


    r.packets = unpacked
    return r
