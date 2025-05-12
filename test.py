import replayparser as gzr
from replayparser.models import AntileadShotgun, Message
from replayparser.util import decompress_to_disk

replay = gzr.parse_replay("assets/igz_ladder.gzr")
# replay.header.display_table()
# replay.stage.display_table()

def log_event(time, msg):
    print(f"{time}: {msg}")

for player in replay.players:
    print(f"{player.name} MUID({player.muid})")

# (packet sender's muid, opcode, serialized packet object)
count = 0
for time, sender, opcode, packet in replay.packets:
    pt = type(packet)
    if pt == AntileadShotgun:
        str_attacker = replay.muid_to_name(sender)
        if packet.hit:
            str_target = replay.muid_to_name(packet.target)
            damage = packet.damage
            log_event(time, f"{str_attacker} hit {str_target} for {damage}")
        else:
            log_event(time, f"{str_attacker} missed")
        count += 1
        if count > 4:
            break
