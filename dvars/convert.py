if __name__ != "__main__": exit()

from dvar import Dvar, DvarType, DvarDatabase
from logging import getLogger, DEBUG, basicConfig
from pathlib import Path
from fnv1a import FNV1a
import fnvhash
import sys
if sys.version_info[0] == 3: _get_byte = lambda c: c
else: _get_byte = ord


logger = getLogger()
logger.setLevel(DEBUG)
fmt = "%(asctime)s - %(levelname)s - %(message)s"; datefmt = "%d-%b-%y %H:%M:%S"
basicConfig(format=fmt, datefmt=datefmt)
basicConfig(filename=f"{__name__}.log", filemode="w", format=fmt, datefmt=datefmt)

logger.debug((__file__,"START"))

workdir = Path("dvars/")
input_file = workdir/"dvars.json"
output_file = workdir/"dvars_out.json"

hasher = FNV1a()
hasher._prime = 0xB3CB2E29
hasher._seed = 0x319712C3

fnvhash.FNV_32_PRIME = 0xB3CB2E29
fnvhash.FNV1_32_INIT = 0x319712C3

db = DvarDatabase.from_file(input_file)
logger.info(f"Loaded {len(db.dvars)} dvars from {input_file}")

for dvar in db.dvars:
    if dvar.name is None:
        # logger.debug(f"Dvar {dvar.hash} has no name")
        continue
    rehash_fnvhash = fnvhash.fnv1a_32(bytes(dvar.name.encode("utf-8")), 0x319712C3)
    rehash_fnvhash_hex = hex(rehash_fnvhash).upper()
    if (rehash_fnvhash != dvar.hash):
        logger.info(f"Dvar {dvar.name} has a hash mismatch: {dvar.hash} -> {rehash_fnvhash_hex} ({rehash_fnvhash})")

    rehash_fnv1a = hasher.hash(dvar.name)
    # convert from int64 str ('1ab9184778fd37f9') to int32 hex ('0xFC60C821')
    rehash_fnv1a_bytes = int(rehash_fnv1a,  16) & 0xFFFFFFFF
    rehash_fnv1a_hex = hex(rehash_fnv1a_bytes).upper()
    if (rehash_fnv1a != dvar.hash):
        logger.info(f"Dvar {dvar.name} has a hash mismatch: {dvar.hash} -> {rehash_fnv1a_hex} ({rehash_fnv1a_bytes} | {rehash_fnv1a})")

db.save(output_file, True)


# Example Usage
# jsonstring = json.loads(myjsonstring)
# root = Root.from_dict(jsonstring)