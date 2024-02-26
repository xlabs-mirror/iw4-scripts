from typing import Optional, List, Any
from dataclasses import dataclass
from json import dumps, load
from utils import get_safe
from maplist.campaign import CampaignAct, Mission
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from maplist import Maplist
    from maplist.map import MapListMap

@dataclass
class Preview:
    url: Optional[str]

    def __init__(self, url: str) -> None:
        self.url = url

    @staticmethod
    def from_dict(obj: Any) -> 'Preview':
        if not obj: return None
        _url = get_safe(obj, "url")
        return Preview(_url)

class SpecOpsMission(Mission):
    opposition: Optional[str]
    classification: Optional[str]
    estimated_time: Optional[str]
    iw_best_time: Optional[str]
    required_players: Optional[int]

    def __init__(self, index: int, title: dict[str,str], description: dict[str,str], opposition: str, classification: str, estimated_time: str, iw_best_time: str, mapname: str, required_players: Optional[int], preview: Preview) -> None:
        self.index = index
        self.title = title
        self.description = description
        self.opposition = opposition
        self.classification = classification
        self.estimated_time = estimated_time
        self.iw_best_time = iw_best_time
        self.mapname = mapname
        self.required_players = required_players
        self.preview = preview

    @staticmethod
    def from_dict(obj: Any) -> 'SpecOpsMission':
        if not obj: return None
        _index = get_safe(obj, "index")
        _title = get_safe(obj, "title")
        _description = get_safe(obj, "description")
        _opposition = get_safe(obj, "opposition")
        _classification = get_safe(obj, "classification")
        _estimated_time = get_safe(obj, "estimated_time")
        _iw_best_time = get_safe(obj, "iw_best_time")
        _mapname = get_safe(obj, "mapname")
        _required_players = get_safe(obj, "required_players")
        _preview = Preview.from_dict(get_safe(obj, "preview"))
        return SpecOpsMission(_index, _title, _description, _opposition, _classification, _estimated_time, _iw_best_time, _mapname, _required_players, _preview)
    
    def get_map(self, maplist: 'Maplist') -> 'MapListMap':
        return maplist.maps[self.mapname] if self.mapname in maplist.get_mapnames() else None

class SpecOpsAct(CampaignAct):
    required_stars: Optional[int]
    missions: List[SpecOpsMission]

    def __init__(self, title: dict[str, str], description: dict[str, str], missions: List[SpecOpsMission], required_stars: int) -> None:
        self.title = title
        self.description = description
        self.missions = missions
        self.required_stars = required_stars

    @staticmethod
    def from_dict(obj: Any) -> 'SpecOpsAct':
        if not obj: return None
        _title = get_safe(obj, "title")
        _description = get_safe(obj, "description")
        _missions = [SpecOpsMission.from_dict(y) for y in get_safe(obj, "missions")]
        _required_stars = get_safe(obj, "required_stars")
        return SpecOpsAct(_title, _description, _missions, _required_stars)


@dataclass
class SpecOpsList:
    Acts: List[SpecOpsAct]

    def __init__(self, acts: list[SpecOpsAct]) -> None:
        self.Acts = acts

    @staticmethod
    def from_list(obj: list) -> 'SpecOpsList':
        if not obj: return None
        Acts = [SpecOpsAct.from_dict(y) for y in obj]
        return SpecOpsList(Acts)
    
    @staticmethod
    def load(file: str = 'specops.json'):
        with open(file, 'r', encoding="utf-8") as f:
            jsonstring = load(f)
            return SpecOpsList.from_list(jsonstring)
    
    def save(self, file: str = 'specops.json'):
        json = dumps(
            {self.Acts},
            default=lambda o: dict((key, value) for key, value in o.__dict__.items() if value),
            sort_keys=True,
            indent=4,
            allow_nan=False
        )
        if file:
            with open(file, 'w') as f: f.write(json)
        print("Saved", len(self.Acts), "acts to", file)
        return json
    
    def __str__(self) -> str:
        return f"{sum(len(act.missions) for act in self.Acts)} missions from {len(self.Acts)} specops acts"
    
    def get_by_mapname(self, mapname: str) -> tuple[SpecOpsMission, SpecOpsAct]:
        for act in self.Acts:
            for mission in act.missions:
                if mission.mapname == mapname:
                    return mission, act
        return None, None
    def get_by_title(self, title: str, language: str = "english") -> tuple[SpecOpsMission, SpecOpsAct]:
        for act in self.Acts:
            for mission in act.missions:
                if language in mission.title and mission.title[language] == title:
                    return mission, act
        return None, None
    def get_by_index(self, index: int) -> tuple[SpecOpsMission, SpecOpsAct]:
        for act in self.Acts:
            for mission in act.missions:
                if mission.index == index:
                    return mission, act
        return None, None