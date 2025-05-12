from io import BytesIO
import struct

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
    def back(self, n: int): self.buf.seek(-n,1)

