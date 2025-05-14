# GZR parsing library

### Port
When I wake up I'll be porting this project to Go and continuing it there.
There's a chance I handle the parsing in C and use exported functions, then retool this project to do the same.


### Currently supported replay versions
- International GunZ (4)
  - Command parsing broke at some point. Low priority atm.
- [iGunZ](https://igunz.net)
  - Almost all packets handled.
  - Suitable for statistical analysis.

### Working on now
- ijji
- Aeria
- Freestyle (v7, v8, v9)
- Dark GunZ

### Won't do
- UGG
  - Malware
- GG GunZ
  - Will but shutdown soon, who cares
- FXP
  - Owner has admitted to shipping download-and-execute functionality in the past.
  - Replay files are filled with garbage data.
  - Also it's bad.

### Util
- `dump.decompress_to_disk(input_gzr: str, output_gzr: str)`
  - Runs zlib decompression and writes decompressed data back to disk.
  - Necessary when working on adding new versions.

### Dependencies
- rich (`pip install rich`)

### Minimal example
```py
import replayparser as gzr
from replayparser.models import AntileadShotgun, Message

replay = gzr.parse_replay("assets/shagers/castle0900.gzr")
replay.header.display_table()
replay.stage.display_table()

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
```

#### Output
```
PS E:\py-gzr> python test.py
   Header Information    
┏━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Field    ┃ Value      ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━┩
│ version  │ 6          │
│ time     │ 1745545838 │
│ major    │ 1          │
│ minor    │ 4          │
│ patch    │ 4          │
│ revision │ 0          │
└──────────┴────────────┘
                    Stage Information                     
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Field                ┃ Value                           ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ map_name             │ Castle                          │
│ map_idx              │ 2                               │
│ stage_name           │                                 │
│ gametype             │ MMATCH_GAMETYPE_DEATHMATCH_TEAM │
│ round_max            │ 99                              │
│ limit_time           │ 2                               │
│ limit_level          │ 0                               │
│ max_players          │ 8                               │
│ team_kill_enabled    │ 0                               │
│ team_win_the_point   │ 1                               │
│ forced_entry_enabled │ 0                               │
│ auto_team_balancing  │ 0                               │
│ netcode              │ 0                               │
│ force_hp_ap          │ 0                               │
│ hp                   │ 100                             │
│ ap                   │ 50                              │
│ no_flip              │ 0                               │
│ swords_only          │ 0                               │
│ refined_mode         │ 1                               │
│ team_rotate          │ 0                               │
└──────────────────────┴─────────────────────────────────┘
iShagers MUID(2068)
XanXus MUID(2368)
Fancy MUID(2538)
Rabid MUID(2094)
Spore MUID(1162)
1234 MUID(2705)
Pinwheel MUID(2251)
imbecile MUID(2833)
13.160774230957031: iShagers hit 1234 for 16
15.193021774291992: imbecile hit Fancy for 8
15.967081069946289: Rabid hit XanXus for 32
16.11139678955078: Spore hit Fancy for 16
16.126506805419922: imbecile hit Fancy for 40
```