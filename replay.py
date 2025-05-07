import replayparser
from replayparser.core import parse_replay

r = parse_replay("assets/replay1.gzr")
print(r.header, r.stage)
for p in r.players:
    print(p.name, p.clan)
print("Commands:", len(r.commands))