from json import JSONEncoder, dump, load
from typing import Any
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from pathlib import Path
from logging import getLogger, DEBUG

logger = getLogger(__name__)
logger.setLevel(DEBUG)

class DvarType(Enum):
    BOOL = "bool"
    FLOAT = "float"
    INT = "int"
    STRING = "string"

@dataclass
class Dvar:
    hash: str
    type: DvarType
    name: Optional[str]
    description: Optional[str]
    default: Optional[int]
    min: Optional[int]
    max: Optional[int]

    def __init__(self, hash: str, type: DvarType, name: Optional[str], description: Optional[str], default: Optional[int], min: Optional[int], max: Optional[int]) -> None:
        self.hash = hash
        self.type = type
        self.name = name
        self.description = description
        self.default = default
        self.min = min
        self.max = max

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v is not None and v != "None"}

    @staticmethod
    def from_dict(obj: Any) -> 'Dvar':
        _Hash = obj.get("Hash")
        _Type = obj.get("Type")
        _Name = obj.get("Name")
        _Description = obj.get("Description")
        _Default = obj.get("Default")
        _Min = obj.get("Min")
        _Max = obj.get("Max")
        return Dvar(_Hash, _Type, _Name, _Description, _Default, _Min, _Max)
    

class DvarDatabase:
    file: Path 
    dvars: list[Dvar]

    def __init__(self, dvars: list[Dvar] = [], file: Path = None) -> None:
        logger.debug(f"Creating new DvarDatabase with {len(dvars)} dvars")
        self.file = file
        self.dvars = dvars

    def save(self, file: Path = None, backup: bool = True, force: bool = False, indent: bool = True) -> None:
        file = file or self.file
        logger.debug(f"Saving dvars to {file}")
        if backup: self.backup(force)
        with open(file, "w") as f:
            dump(self.dvars, f, cls=MyEncoder, indent=4 if indent else None)

    def backup(self, file: Path = None, force: bool = False) -> None:
        file = file or self.file
        bak_file = file.with_suffix('.bak.json')
        exists = Path(bak_file).exists()
        logger.debug(f"Backing up {file} to {bak_file} (exists:{exists})...")
        if exists and not force:
            logger.warning(f"File {bak_file} already exists, not forcing backup!")
            return
        self.save(bak_file, False)

    @staticmethod
    def from_file(file: Path) -> 'DvarDatabase':
        logger.debug(f"Loading dvars from {file}")
        ret = DvarDatabase(file=file)
        with open(file, "r") as f:
            for dvar in load(f):
                ret.dvars.append(Dvar.from_dict(dvar))
        return ret
    
class MyEncoder(JSONEncoder):
        def default(self, o: Dvar): return o.to_dict()

if __name__ == "__main__": raise Exception("This file is not meant to be run directly!")