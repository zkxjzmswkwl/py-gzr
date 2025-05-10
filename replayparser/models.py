from dataclasses import dataclass
from typing import List, Any

@dataclass
class Message:
    sender: int
    message: str

@dataclass
class Replay:
    header: Any
    stage:  Any
    players: List[Any]
    commands: List[Any]
    messages: List[Message]

@dataclass
class Command:
    time:   float
    sender: int
    size:   int
    data:   bytes