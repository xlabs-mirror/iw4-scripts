from enum import Enum
from typing import Any
from dataclasses import dataclass
from urlparse import ParseResult, urlparse

class SourceID(Enum):
    UNKNWOWN = "Unknown"
    BASE_GAME = "Call of Duty: Modern Warfare 2"
    BASE_GAME_OR_DLC = "Base Game or DLC"
    DLC_STIMULUS = "Stimulus DLC"
    DLC_RESURGENCE = "Resurgence DLC"
    SINGLEPLAYER = "Singleplayer"
    DLC_COD_ONLINE = "Call of Duty: Online DLC"
    DLC_MW1 = "Call of Duty 4: Modern Warfare DLC"
    DLC_MW3 = "Call of Duty: Modern Warfare 3 DLC"
    USERMAPS = "User Maps"
    OTHERS = "Others"

@dataclass
class Mirror:
    name: str
    url: ParseResult
    icon: str = None

    @staticmethod
    def from_dict(obj: Any) -> 'Mirror':
        _name = str(obj.get("name"))
        _url = urlparse(obj.get("url"))
        _icon = str(obj.get("icon"))
        return Mirror(_name, _url, _icon)

@dataclass
class Source:
    name: SourceID = SourceID.UNKNWOWN
    url: ParseResult = None
    md5: str = None
    mirrors: list[Mirror] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Source':
        _id = str(obj.get("id"))
        _name = str(obj.get("name"))
        _url = urlparse(obj.get("url"))
        _md5 = str(obj.get("md5"))
        _mirrors = Mirror.from_dict(obj.get("mirrors"))
        return Source(_id, _name, _url, _md5, _mirrors)
