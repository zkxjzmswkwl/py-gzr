import zlib

def decompress_to_disk(gzr_input: str, decompressed_output: str):
    """
    Decompress a GZR file to a specified output file.
    
    Args:
        gzr_input (str): Path to the input GZR file.
        decompressed_output (str): Path to the output decompressed file.
    """
    with open(gzr_input, 'rb') as f:
        raw = f.read()
    
    try:
        data = zlib.decompress(raw)
    except zlib.error as e:
        print(f"Error decompressing {gzr_input}: {e}")
        return
    
    with open(decompressed_output, 'wb') as f:
        f.write(data)