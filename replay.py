import replayparser # Seems silly, but needed to trigger import in __init__.py which registers handlers.
from replayparser.core import parse_replay

r = parse_replay("assets/replay1.gzr")
print(r.header, r.stage)
for p in r.players:
    print(p.name, p.clan)
print("Commands:", len(r.commands))