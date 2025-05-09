import replayparser # Seems silly, but needed to trigger import in __init__.py which registers handlers.
from replayparser.core import parse_replay
from replayparser.util import decompress_to_disk

# decompress_to_disk("assets/gayer.gzr", "assets/gayer.bin")
r = parse_replay("assets/igz_ladder.gzr")
print(r.header, r.stage)
for p in r.players:
    print(p.name, p.clan)
print("Commands:", len(r.commands))