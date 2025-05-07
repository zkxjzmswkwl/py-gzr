from dataclasses import dataclass
from typing import List, Any

@dataclass
class Replay:
    header: Any
    stage:  Any
    players: List[Any]
    commands: List[Any]

@dataclass
class Command:
    time:   float
    sender: int
    size:   int
    data:   bytes