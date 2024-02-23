from typing import Optional, List, Union, Any
from dataclasses import dataclass
from json import dumps, load
from utils import get_safe
from maplist.image import Preview
    

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
    name: Optional[str]
    mapname: Optional[str]
    description: Optional[str]
    preview: Optional[Preview]

    def __init__(self, index: int, name: str, mapname: str, description: str, preview: Preview) -> None:
        self.index = index
        self.name = name
        self.mapname = mapname
        self.description = description
        self.preview = preview

    @staticmethod
    def from_dict(obj: Any) -> 'Mission':
        if not obj: return None
        _index = get_safe(obj, "index")
        _name = get_safe(obj, "name")
        _mapname = get_safe(obj, "mapname")
        _description = get_safe(obj, "description")
        _preview = Preview.from_dict(get_safe(obj, "preview"))
        return Mission(_index, _name, _mapname, _description, _preview)

@dataclass
class CampaignMission(Mission):
    location: Union[Location, str]
    date: Optional[str]

    def __init__(self, index: int, name: str, mapname: str, description: str, location: Union[Location, str], date: str, preview: Preview) -> None:
        self.index = index
        self.name = name
        self.mapname = mapname
        self.description = description
        self.location = location
        self.date = date
        self.preview = preview

    @staticmethod
    def from_dict(obj: Any) -> 'CampaignMission':
        if not obj: return None
        _index = get_safe(obj, "index")
        _name = get_safe(obj, "name")
        _mapname = get_safe(obj, "mapname")
        _description = get_safe(obj, "description")
        _location = get_safe(obj, "location")
        if isinstance(get_safe(obj, "location"), dict):
            _location = Location.from_dict(get_safe(obj, "location"))
        _date = get_safe(obj, "date")
        _preview = Preview.from_dict(get_safe(obj, "preview"))
        return CampaignMission(_index, _name, _mapname, _description, _location, _date, _preview)

class CampaignAct:
    name: Optional[dict[str,str]]
    description: Optional[dict[str,str]]
    missions: List[CampaignMission]

    def __init__(self, name: dict[str,str], description: dict[str,str], missions: list[CampaignMission]) -> None:
        self.name = name
        self.description = description
        self.missions = missions

    @staticmethod
    def from_dict(obj: Any) -> 'CampaignAct':
        if not obj: return None
        _name = get_safe(obj, "name")
        _description = get_safe(obj, "description")
        _missions = [CampaignMission.from_dict(y) for y in get_safe(obj, "missions")]
        return CampaignAct(_name, _description, _missions)

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
        return f"{sum(len(act.missions) for act in self.Acts)} missions from {len(self.Acts)} campaign acts"