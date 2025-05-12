import struct
from enum import Enum
from typing import List, Any

from replayparser.core import BinaryReader

class MPT(Enum):
    INT    = 0
    FLOAT  = 1
    STR    = 2
    BLOB   = 3
    SHORT  = 4
    UCHAR  = 5

class MCommandParameter:
    def __init__(self, ptype: MPT, value: Any):
        self.type  = ptype
        self.value = value

class MCommand:
    def __init__(self, command_id: int, sender: int, params: List[MCommandParameter]):
        self.command_id = command_id
        self.sender     = sender
        self.params     = params

    @staticmethod
    def from_bytes(data: bytes, param_types: List[MPT]) -> 'MCommand':
        """
        Parse a GetData()-style buffer:
          [0..1]   u16 total_size
          [2..3]   u16 command_id
          [4]      u8  sender/serial
          [5..end] parameters, in the order given by param_types
        """
        r = BinaryReader(data)

        total_size = r.read_uint16()
        cmd_id     = r.read_uint16()
        serial     = r.read_uint8()
        # print(total_size, serial)

        params = []
        for t in param_types:
            if t is MPT.INT:
                val = r.read_int32()
            elif t is MPT.FLOAT:
                val = r.read_float()
            elif t is MPT.STR:
                # assume next uint16 length prefix
                length = r.read_uint16()
                val    = r.read_string(length)
            elif t is MPT.BLOB:
                # assume next uint16 length prefix too
                length = r.read_uint16()
                val    = r.read_bytes(length)
            elif t is MPT.SHORT:
                val = r.read_uint16()
            elif t is MPT.UCHAR:
                val = r.read_uint8()
            else:
                raise ValueError(f"Unsupported param type: {t}")
            params.append(MCommandParameter(t, val))

        return MCommand(cmd_id, serial, params)

    def get_parameter(self, index: int) -> Any:
        """Helper to retrieve parameter’s raw value."""
        return self.params[index].value
