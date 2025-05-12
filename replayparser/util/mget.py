from collections import namedtuple
import struct

from replayparser.models import AntileadShotgun

def mget_blob_array_count(blob: bytes) -> int:
    """
    Read the blob-array count (second int32) from the front of `blob`.
    """
    # offset 4 bytes from start
    (count,) = struct.unpack_from('<i', blob, 4)
    return count

def mget_blob_array_size(blob: bytes) -> int:
    """
    Compute total size = 2×int32 header + count×element_size.
    """
    (element_size,) = struct.unpack_from('<i', blob, 0)
    (count,)        = struct.unpack_from('<i', blob, 4)
    return 2*4 + element_size * count

def mget_blob_array_element(blob: bytes, index: int) -> bytes:
    """
    Return the `index`-th element (as its own bytes slice).
    Raises IndexError if out of bounds.
    """
    (element_size,) = struct.unpack_from('<i', blob, 0)
    (count,)        = struct.unpack_from('<i', blob, 4)

    if not (0 <= index < count):
        raise IndexError(f"Blob index {index} out of range [0, {count})")

    start = 2*4 + element_size * index
    end   = start + element_size
    return blob[start:end]

ShotgunDamageInfo = namedtuple(
    'ShotgunDamageInfo',
    ['Target', 'Damage', 'PiercingRatio', 'DamageType']
)

def mget_blob_array_element_offset(blob: bytes, index: int) -> int:
    """
    Return the byte‐offset of element #index in the blob‐array.
    """
    element_size, count = struct.unpack_from('<ii', blob, 0)
    if not (0 <= index < count):
        raise IndexError(f"Index {index} out of range [0, {count})")
    return 8 + element_size * index  # skip two ints (8 bytes)

def get_shotgun_damage_info(blob: bytes, index: int) -> ShotgunDamageInfo:
    """
    Reads the `index`-th ShotgunDamageInfo from `blob` and returns it.
    """
    base = mget_blob_array_element_offset(blob, index)

    # unpack in one go: I (uint32), i (int32), f (float32), i (int32), i (int32)
    target, dam, piercing, dam_type, = struct.unpack_from(
        '<Iifi', blob, 14
    )

    return AntileadShotgun(
        target=target,
        damage=dam,
        piercing_ratio=piercing,
        damage_type=dam_type,
    )

def get_peer_node_info(blob: bytes, index: int):
    """
    Reads the `index`-th PeerNodeInfo from `blob` and returns it.
    """
    base = mget_blob_array_element_offset(blob, index)

    # unpack in one go: I (uint32), I (unt32), I (uint32)
    uid, dwIp, nPort, = struct.unpack_from(
        '<III', blob, 22
    )
    return uid, dwIp, nPort

class MCommandParameter:
    def __init__(self, p_type, value):
        self.type  = p_type
        self.value = value