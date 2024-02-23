from enum import Enum
from typing import Any, Optional
from dataclasses import dataclass
from urllib.parse import ParseResult, urlparse
from utils import get_safe

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

    @staticmethod
    def from_dict(d: dict) -> 'SourceID':
        return SourceID.from_str(d.get("name"))

    @staticmethod
    def from_str(str) -> 'SourceID':
        match(str.lower()):
            case "unknown": return SourceID.UNKNWOWN
            case "base game": return SourceID.BASE_GAME
            case "base game or dlc": return SourceID.BASE_GAME_OR_DLC
            case "stimulus dlc": return SourceID.DLC_STIMULUS
            case "resurgence dlc": return SourceID.DLC_RESURGENCE
            case "singleplayer": return SourceID.SINGLEPLAYER
            case "call of duty: online dlc": return SourceID.DLC_COD_ONLINE
            case "call of duty 4: modern warfare dlc": return SourceID.DLC_MW1
            case "call of duty: modern warfare 3 dlc": return SourceID.DLC_MW3
            case "user maps": return SourceID.USERMAPS
            case "others": return SourceID.OTHERS
        return SourceID.UNKNWOWN

@dataclass
class Mirror:
    name: str
    url: ParseResult
    icon: str = None

    @staticmethod
    def from_dict(obj: Any) -> 'Mirror':
        if obj is None: return None
        _name = get_safe(obj, "name")
        _url = urlparse(get_safe(obj, "url"))
        _icon = get_safe(obj, "icon")
        return Mirror(_name, _url, _icon)

@dataclass
class Source:
    name: str = None # SourceID = SourceID.UNKNWOWN
    url: str = None
    md5: str = None
    mirrors: Optional[list[Mirror]] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Source':
        if obj is None: return None
        # _id = get_safe(obj, "id")
        _name = get_safe(obj, "name")
        _url = get_safe(obj, "url") # urlparse(
        _md5 = get_safe(obj, "md5")
        _mirrors = Mirror.from_dict(get_safe(obj, "mirrors")) or None
        return Source(_name, _url, _md5, _mirrors)

    def __eq__(self, other):
        return self.url == other.url and self.md5 == other.md5 and self.name == other.name and self.mirrors == other.mirrors
    
    def __hash__(self):
        return hash((self.name, self.url, self.md5, self.mirrors))
    
    def __str__(self):
        return f"{self.name} ({self.url}) [{len(self.mirrors) if self.mirrors else 0} mirrors]"