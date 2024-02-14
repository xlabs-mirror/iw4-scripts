from typing import Optional, List, Union, Any
from dataclasses import dataclass
from json import dumps, load
from utils import get_safe

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
    name: Optional[str]
    mapname: Optional[str]
    description: Optional[str]
    location: Union[Location, str]
    date: Optional[str]
    preview: Optional[Preview]

    def __init__(self, name: str, mapname: str, description: str, location: Union[Location, str], date: str, preview: Preview) -> None:
        self.name = name
        self.mapname = mapname
        self.description = description
        self.location = location
        self.date = date
        self.preview = preview

    @staticmethod
    def from_dict(obj: Any) -> 'Mission':
        if not obj: return None
        _name = get_safe(obj, "name")
        _map = get_safe(obj, "map")
        _description = get_safe(obj, "description")
        _location = get_safe(obj, "location")
        if isinstance(get_safe(obj, "location"), dict):
            _location = Location.from_dict(get_safe(obj, "location"))
        _date = get_safe(obj, "date")
        _preview = Preview.from_dict(get_safe(obj, "preview"))
        return Mission(_name, _map, _description, _location, _date, _preview)

@dataclass
class CampaignList:
    Acts: dict[str, list[Mission]]

    def __init__(self, acts: dict[str, list[Mission]]) -> None:
        self.Acts = acts

    @staticmethod
    def from_dict(obj: Any) -> 'CampaignList':
        Acts = {}
        for actname, act in obj.items():
            Acts[actname] = [Mission.from_dict(mission) for mission in act]
        return CampaignList(Acts)
    
    @staticmethod
    def load(file: str = 'campaigns.json'):
        with open(file, 'r', encoding="utf-8") as f:
            jsonstring = load(f)
            return CampaignList.from_dict(jsonstring)
    
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