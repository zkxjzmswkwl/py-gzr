import zlib, struct
from io import BytesIO
from typing import Type, Dict

from replayparser.util.dump import hex_dump
from .models import Replay, Command, Message
from collections import Counter

_HEADER_REGISTRY: Dict[int, Type] = {}
_STAGE_REGISTRY:  Dict[int, Type] = {}
_PLAYER_REGISTRY: Dict[int, Type] = {}

def register_header(version: int, cls: Type):
    _HEADER_REGISTRY[version] = cls

def register_stage(version: int, cls: Type):
    _STAGE_REGISTRY[version] = cls

def register_player(version: int, cls: Type):
    _PLAYER_REGISTRY[version] = cls


class BinaryReader:
    def __init__(self, data: bytes):
        self.buf = BytesIO(data)
    def read(self, fmt: str):
        size = struct.calcsize(fmt)
        data = self.buf.read(size)
        if len(data) != size:
            raise EOFError()
        return struct.unpack(fmt, data)
    def read_bytes(self, n: int) -> bytes:
        data = self.buf.read(n)
        if len(data) != n:
            raise EOFError(f"While trying to read: {n} bytes")
        return data
    def read_uint64(self): return self.read('<Q')[0]
    def read_int64(self): return self.read('<Q')[0]
    def read_uint32(self): return self.read('<I')[0]
    def read_int32(self):  return self.read('<i')[0]
    def read_float(self):  return self.read('<f')[0]
    def read_bool(self):   return self.read('<b')[0]
    def read_uint16(self) -> int:   return self.read('<H')[0]
    def read_int16(self)  -> int:   return self.read('<h')[0]
    def read_uint8(self)  -> int:   return self.read('<B')[0]
    def read_int8(self)   -> int:   return self.read('<b')[0]
    def read_string(self, n: int) -> str:
        raw = self.read_bytes(n)
        return raw.split(b'\x00',1)[0].decode('latin1', errors='ignore')
    def read_string_until(self, terminator: bytes) -> str:
        data = b''
        while True:
            byte = self.buf.read(1)
            if byte == terminator or len(byte) == 0:
                break
            data += byte
        return data.decode('latin1', errors='ignore')
    def skip(self, n: int): self.buf.seek(n,1)

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
    print(magic)
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
    for idx, p in enumerate(range(cnt)): 
        players.append(PlayerCls.from_reader(reader, full, idx == cnt))


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
            sz_again = tmp_reader.read_int16()
            opcode = tmp_reader.read_uint16()
            packets.append({'opcode': opcode, 'buffer': data, 'sender': sender})
        except EOFError:
            break

    messages = []
    for pck in packets:
        if pck['opcode'] == 1520:
            r = BinaryReader(pck['buffer'])
            r.skip(0x15)
            sz = r.read_uint16()
            msg = r.read_string(sz)
            messages.append(Message(sender=pck['sender'], message=msg))


    return Replay(header=header, stage=stage, players=players, commands=commands, messages=messages)
