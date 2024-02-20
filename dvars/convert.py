from dvar import Dvar, DvarType, DvarDatabase
from logging import getLogger, DEBUG, basicConfig
from pathlib import Path

if __name__ != "__main__": exit()

logger = getLogger()
logger.setLevel(DEBUG)
fmt = "%(asctime)s - %(levelname)s - %(message)s"; datefmt = "%d-%b-%y %H:%M:%S"
basicConfig(format=fmt, datefmt=datefmt)
basicConfig(filename=f"{__name__}.log", filemode="w", format=fmt, datefmt=datefmt)

logger.debug((__file__,"START"))

workdir = Path("dvars/")
input_file = workdir/"dvars.json"
output_file = workdir/"dvars_out.json"

db = DvarDatabase.from_file(input_file)
logger.info(f"Loaded {len(db.dvars)} dvars from {input_file}")

db.save(output_file, True)


# Example Usage
# jsonstring = json.loads(myjsonstring)
# root = Root.from_dict(jsonstring)