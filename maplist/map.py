from base64 import urlsafe_b64encode
from typing import Any, Optional
from dataclasses import dataclass
from requests import get
from hashlib import md5
from maplist.campaign import Mission
from parser.stringmap import StringMaps
from maplist.source import Source
from maplist.image import Preview, Loadscreen, Minimap
from utils import get_safe

@dataclass
class Name:
    @staticmethod
    def from_mapname(mapname: str, strmap:StringMaps = None) -> dict[str, str]:
        nomp = mapname.replace("mp_", "")
        ret = {
            "_key": f"MPUI_{nomp.upper()}",
            "english": nomp.replace("_"," ").title()
        }
        if strmap:
            for lang, strings in strmap.strings.items():
                print("Getting",lang,"value for", ret["_key"])
                if ret["_key"] in strings.keys():
                    val = strings.get(ret["_key"])
                    if lang != "english" and val == ret["english"]: continue
                    ret[lang] = val
        return ret

class Description:
    @staticmethod
    def from_name(displayname: str, strmap:StringMaps = None, source = None) -> dict[str, str]:
        english = f"{displayname} is a map for Call of Duty: Modern Warfare 2."
        if source:
            if source == "Custom Maps": english = f"{displayname} is a custom map."
            else: english = f"{displayname} is a map from {source}."
        ret = {
            "_key": f"MPUI_DESC_MAP_{displayname.upper().replace(' ', '_')}",
            "english": english,
        }
        if strmap:
            for lang, strings in strmap.strings.items():
                print("Getting",lang,"value for", ret["_key"])
                if ret["_key"] in strings.keys():
                    ret[lang] = strings.get(ret["_key"])
        return ret

@dataclass
class Waypoints:
    file: Optional[str] = None
    url: Optional[str] = None
    md5: Optional[str] = None
    count: Optional[int] = None

    def update(self, url = None):
        url = url or self.url
        if not url: url = f"https://raw.githubusercontent.com/xlabs-mirror/iw4-resources/main/waypoints/{self.file}"
        print("Updating waypoints from",url)
        response = get(url)
        self.file = response.text if response.status_code == 200 else None
        self.md5 = md5(self.file.encode("utf-8")).hexdigest() if response.status_code == 200 else None
        self.count = self.file.partition('\n')[0] if response.status_code == 200 else None
        return self

    @staticmethod
    def from_mapname(mapname: str) -> 'Waypoints':
        file = f"{mapname}_wp.csv"
        ret = Waypoints(file)
        ret.update()
        return ret

    @staticmethod
    def from_dict(obj: Any) -> 'Waypoints':
        if obj is None: return None
        _file = get_safe(obj, "file")
        _url = get_safe(obj, "url")
        _md5 = get_safe(obj, "md5")
        _count = get_safe(obj, "count")
        return Waypoints(_file, _url, _md5, _count)

@dataclass
class MapListMap:
    source: Optional[Source] = None
    name: Optional[dict[str,str]] = None
    description: Optional[dict[str,str]] = None
    preview: Optional[Preview] = None
    loadscreen: Optional[Loadscreen] = None
    minimap: Optional[Minimap] = None
    waypoints: Optional[Waypoints] = None
    mission: Optional[Mission] = None
    alternatives: Optional[list[str]] = None

    @staticmethod
    def from_mapname(name: str, source: Source = None, strmap:StringMaps = None) -> 'MapListMap':
        displayname = Name.from_mapname(name, strmap)
        return MapListMap(
            source=source,
            name=displayname,
            description=Description.from_name(displayname=displayname['english'], strmap=strmap, source=source),
            preview=Preview.from_mapname(name),
            loadscreen=Loadscreen.from_mapname(name),
            minimap=Minimap.from_name(name),
            waypoints=Waypoints.from_mapname(name)
        )

    @staticmethod
    def from_dict(obj: Any) -> 'MapListMap':
        if obj is None: return None
        _source = Source.from_dict(get_safe(obj, "source"))
        # except: _source = Source(SourceID.from_dict(get_safe(obj, "source")))
        _name = get_safe(obj, "name")
        _description = get_safe(obj, "description")
        _preview = Preview.from_dict(get_safe(obj, "preview"))
        _loadscreen = Loadscreen.from_dict(get_safe(obj, "loadscreen"))
        _minimap = Minimap.from_dict(get_safe(obj, "minimap"))
        _waypoints = Waypoints.from_dict(get_safe(obj, "waypoints"))
        _mission = Mission.from_dict(get_safe(obj, "mission"))
        _alternatives = get_safe(obj, "alternatives")
        return MapListMap(_source, _name, _description, _preview, _loadscreen, _minimap, _waypoints, _mission, _alternatives)
