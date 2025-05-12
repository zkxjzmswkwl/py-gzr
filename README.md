# GZR parsing library

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

### Util
- `dump.decompress_to_disk(input_gzr: str, output_gzr: str)`
  - Runs zlib decompression and writes decompressed data back to disk.
  - Necessary when working on adding new versions.