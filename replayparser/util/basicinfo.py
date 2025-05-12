import struct, math
from collections import namedtuple
from enum import IntFlag, IntEnum

# constants
SIZEOF_U8 = 1
SIZEOF_SHORT = 2
SIZEOF_FLOAT = 4
SIZEOF_V3 = 3 * SIZEOF_FLOAT
SIZEOF_MSHORTVECTOR = 3 * SIZEOF_SHORT
SIZEOF_PACKEDDIRECTION = 2

class BasicInfoFlags(IntFlag):
    LongPos    = 1
    CameraDir  = 2
    Animations = 4
    SelItem    = 8

class V3:
    def __init__(self, x=0, y=0, z=0):
        self.x, self.y, self.z = float(x), float(y), float(z)
    def __repr__(self): return f"V3({self.x:.3f}, {self.y:.3f}, {self.z:.3f})"

class PackedDirectionData:
    def __init__(self, data): self.data = data
    def __repr__(self): return f"<Packed 0x{self.data.hex()}>"

class BasicInfo:
    def __init__(self):
        self.position = V3()
        self.velocity = V3()
        self.direction = V3()
        self.cameradir = V3()
        self.upperstate = -1
        self.lowerstate = -1
        self.SelectedSlot = -1

class BasicInfoItem(BasicInfo):
    def __init__(self):
        super().__init__()
        self.SentTime = 0
        self.RecvTime = 0
        self.LowerFrameTime = 0
        self.UpperFrameTime = 0

class NewBasicInfo:
    def __init__(self):
        self.Flags = 0
        self.Time = 0
        self.bi = BasicInfoItem()

    def __str__(self):
        return f"NewBasicInfo(Flags={self.Flags}, Time={self.Time}, bi={self.bi})"

    def display_rich_table(self):
        from rich.console import Console
        from rich.table import Table

        console = Console()
        table = Table(title="BasicInfo")

        table.add_column("Field", style="bold cyan")
        table.add_column("Value", style="white")

        for key, value in self.bi.__dict__.items():
            table.add_row(key, str(value))

        console.print(table)

def unpack_direction(packed):
    if len(packed.data) != 2:
        return V3(0, 0, 1)
    yaw, pitch = struct.unpack('<BB', packed.data)
    yaw = yaw / 255 * 2 * math.pi
    pitch = (pitch / 255 - 0.5) * math.pi
    x = math.cos(yaw) * math.cos(pitch)
    y = math.sin(yaw) * math.cos(pitch)
    z = math.sin(pitch)
    return V3(x, y, z)

def mshort_to_v3(x, y, z):
    return V3(x / 100.0, y / 100.0, z / 100.0)

def unpack_new_basic_info(data: bytes, size: int):
    if not data or len(data) < 1:
        return None, "too short"

    cur = 0
    try:
        nbi = NewBasicInfo()
        nbi.Flags = data[cur]
        cur += 1

        def read(fmt, n):
            nonlocal cur
            out = struct.unpack('<' + fmt, data[cur:cur+n])[0]
            cur += n
            return out

        def raw(n):
            nonlocal cur
            out = data[cur:cur+n]
            cur += n
            return out

        nbi.Time = read('f', 4)
        bi = nbi.bi

        if nbi.Flags & BasicInfoFlags.LongPos:
            bi.position = V3(read('f',4), read('f',4), read('f',4))
        else:
            bi.position = mshort_to_v3(read('h',2), read('h',2), read('h',2))

        bi.direction = unpack_direction(PackedDirectionData(raw(2)))
        bi.velocity = mshort_to_v3(read('h',2), read('h',2), read('h',2))

        if nbi.Flags & BasicInfoFlags.CameraDir:
            bi.cameradir = unpack_direction(PackedDirectionData(raw(2)))
        else:
            bi.cameradir = V3(bi.direction.x, bi.direction.y, bi.direction.z)

        if nbi.Flags & BasicInfoFlags.Animations:
            bi.lowerstate = read('B',1)
            bi.upperstate = read('B',1)

        if nbi.Flags & BasicInfoFlags.SelItem:
            bi.SelectedSlot = read('B',1)

        return nbi, "ok"

    except Exception as e:
        return None, f"err: {e}"

def unpack_basicinfo(packet, size):
    unpacked_nbi, status_msg = unpack_new_basic_info(packet, size)
    if status_msg == "ok":
        return unpacked_nbi
    return None
