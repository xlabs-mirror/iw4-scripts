from typing import Any
from dataclasses import dataclass
import json
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

    @staticmethod
    def from_dict(obj: Any) -> 'Dvar':
        _Hash = str(obj.get("Hash"))
        _Type = str(obj.get("Type"))
        _Name = str(obj.get("Name"))
        _Description = str(obj.get("Description"))
        _Default = str(obj.get("Default"))
        _Min = str(obj.get("Min"))
        _Max = str(obj.get("Max"))
        return Dvar(_Hash, _Type, _Name, _Description, _Default, _Min, _Max)
    

class DvarDatabase:
    file: Path 
    dvars: list[Dvar]

    def __init__(self, dvars: list[Dvar], file: Path = None) -> None:
        logger.debug(f"Creating new DvarDatabase with {len(dvars)} dvars")
        self.file = file
        self.dvars = dvars

    def load(self, file: Path = None) -> None:
        file = file or self.file
        logger.debug(f"Loading dvars from {file}")
        with open(file, "r") as f:
            self.dvars = json.load(f)

    def save(self, file: Path = None, backup: bool = True, force: bool = False, indent: bool = True) -> None:
        file = file or self.file
        logger.debug(f"Saving dvars to {file}")
        if backup: self.backup(force)
        with open(file, "w") as f:
            json.dump(self.dvars, f, indent=4 if indent else None)

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
        with open(file, "r") as f:
            return DvarDatabase(dvars=json.load(f), file=file)
    

if __name__ == "__main__": raise Exception("This file is not meant to be run directly!")