from typing import Optional, List, Union, Any
from dataclasses import dataclass
from json import dumps, load
from utils import get_safe
from maplist.image import Preview
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from maplist import Maplist
    from maplist.map import MapListMap
    

@dataclass
class Location:
    country: Optional[str]
    city: Optional[str]
    state: Optional[str]

    def __init__(self, country: Optional[str], city: Optional[str], state: Optional[str]) -> None:
        self.country = country
        self.city = city
        self.state = state

    @staticmethod
    def from_dict(obj: Any) -> 'Location':
        if not obj: return None
        _country = get_safe(obj, "country")
        _state = get_safe(obj, "state")
        _city = get_safe(obj, "city")
        return Location(_country, _state, _city)

@dataclass
class Mission:
    index: Optional[int]
    title: Optional[dict[str,str]]
    mapname: Optional[str]
    description: Optional[dict[str,str]]
    preview: Optional[Preview]

    def __init__(self, index: int, title: dict[str,str], mapname: str, description: dict[str,str], preview: Preview) -> None:
        self.index = index
        self.title = title
        self.mapname = mapname
        self.description = description
        self.preview = preview

    @staticmethod
    def from_dict(obj: Any) -> 'Mission':
        if not obj: return None
        _index = get_safe(obj, "index")
        _title = get_safe(obj, "title")
        _mapname = get_safe(obj, "mapname")
        _description = get_safe(obj, "description")
        _preview = Preview.from_dict(get_safe(obj, "preview"))
        return Mission(_index, _title, _mapname, _description, _preview)
    
    def shortstr(self, key: str = "english") -> str:
        return f"{self.title[key] if key in self.title else self.title} ({self.mapname})"
    def fullstr(self) -> str:
        return f"CampaignMission({','.join([f'{key}={value}' for key, value in self.__dict__.items() if value])})"

@dataclass
class CampaignMission(Mission):
    location: Union[Location, str]
    date: Optional[str]

    def __init__(self, index: int, title: str, mapname: str, description: str, location: Union[Location, str], date: str, preview: Preview) -> None:
        self.index = index
        self.title = title
        self.mapname = mapname
        self.description = description
        self.location = location
        self.date = date
        self.preview = preview

    @staticmethod
    def from_dict(obj: Any) -> 'CampaignMission':
        if not obj: return None
        _index = get_safe(obj, "index")
        _title = get_safe(obj, "title")
        _mapname = get_safe(obj, "mapname")
        _description = get_safe(obj, "description")
        _location = get_safe(obj, "location")
        if isinstance(get_safe(obj, "location"), dict):
            _location = Location.from_dict(get_safe(obj, "location"))
        _date = get_safe(obj, "date")
        _preview = Preview.from_dict(get_safe(obj, "preview"))
        return CampaignMission(index=_index, title=_title, mapname=_mapname, description=_description, location=_location, date=_date, preview=_preview)
    
    def get_map(self, maplist: 'Maplist') -> 'MapListMap':
        return maplist.maps[self.mapname] if self.mapname in maplist.get_mapnames() else None

class CampaignAct:
    title: Optional[dict[str,str]]
    description: Optional[dict[str,str]]
    missions: List[CampaignMission]

    def __init__(self, title: dict[str,str], description: dict[str,str], missions: list[CampaignMission]) -> None:
        self.title = title
        self.description = description
        self.missions = missions

    @staticmethod
    def from_dict(obj: Any) -> 'CampaignAct':
        if not obj: return None
        _title = get_safe(obj, "title")
        if _title and not isinstance(_title, dict): raise ValueError(f"Invalid type {type(_title)} for title {_title}")
        _description = get_safe(obj, "description")
        if _description and not isinstance(_description, dict): raise ValueError(f"Invalid type {type(_description)} for description {_description}")
        _missions = [CampaignMission.from_dict(y) for y in get_safe(obj, "missions")]
        if _missions and len(_missions) > 0 and not isinstance(_missions[0], CampaignMission): raise ValueError(f"Invalid type {type(_missions[0])} for missions[0] {_missions[0]}")
        return CampaignAct(title=_title, description=_description, missions=_missions)

@dataclass
class CampaignList:
    Acts: List[CampaignAct]

    def __init__(self, acts: list[CampaignAct]) -> None:
        self.Acts = acts

    @staticmethod
    def from_list(obj: list) -> 'CampaignList':
        if not obj: return None
        Acts = [CampaignAct.from_dict(y) for y in obj]
        return CampaignList(Acts)
    
    @staticmethod
    def load(file: str = 'campaigns.json'):
        with open(file, 'r', encoding="utf-8") as f:
            jsonstring = load(f)
            return CampaignList.from_list(jsonstring)
    
    def save(self, file: str = 'campaigns.json'):
        json = dumps(
            self.Acts,
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
        return f"{sum(len(act.missions) for act in self.Acts)} missions from {len(self.Acts)} campaign acts"
    
    def get_by_mapname(self, mapname: str) -> tuple[CampaignMission, CampaignAct]:
        for act in self.Acts:
            for mission in act.missions:
                if mission.mapname == mapname:
                    return mission, act
        return None, None
    def get_by_title(self, title: str, language: str = "english") -> tuple[CampaignMission, CampaignAct]:
        for act in self.Acts:
            for mission in act.missions:
                if language in mission.title and mission.title[language] == title:
                    return mission, act
        return None, None
    def get_by_index(self, index: int) -> tuple[CampaignMission, CampaignAct]:
        for act in self.Acts:
            for mission in act.missions:
                if mission.index == index:
                    return mission, act
        return None, None