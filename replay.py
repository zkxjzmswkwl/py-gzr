import os
import replayparser
from collections import Counter
from replayparser.core import parse_replay
from replayparser.util import decompress_to_disk
from replayparser.util.dump import hex_dump
from replayparser.versions.v6handlers import handle_announce, handle_antilead_shotgun, handle_basicinfo, handle_change_weapon, handle_chat, handle_dash, handle_die, handle_game_dead, handle_hpap_info, handle_massive, handle_peer_shot_sp, handle_peer_sp_motion, handle_player_join_battle, handle_reload, handle_round_state_change, handle_skill, handle_slash, handle_spawn, handle_worlditem_pickup

def list_files_in_dir(dir_path):
    try:
        return os.listdir(dir_path)
    except FileNotFoundError:
        print(f"Directory {dir_path} not found.")
        return []

# pending = list_files_in_dir("assets/shagers")
# decompress_to_disk("assets/shagers/shagers4.gzr", "assets/shaggers4.bin")
r = parse_replay(f"assets/shagers/shagers4.gzr")

# need to pass over packets to get all players.
# if the replay started prior to other players joining, they must 
# be fetched from the ENTER_BATTLE packet parameters.
for c in r.packets:
    if c['opcode'] == 1402:
        r.players.append(handle_player_join_battle(c))

unpacked = []
sorted_basic_info = {}
opcode_count = Counter()

for c in r.packets:
    opcode_count[c['opcode']] += 1
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


sorted_opcodes = opcode_count.most_common()
with open("output/opcodes.txt", "w") as f:
    for opcode, count in sorted_opcodes:
        f.write(f"Opcode {opcode}: {count} packets\n")
