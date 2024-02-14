from typing import Any, Optional
from dataclasses import dataclass
from requests import get
from hashlib import md5
from parser.stringmap import StringMaps
from maplist.source import Source, SourceID
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
class Minimap:
    name: str
    url: str
    base64: str

    def __init__(self, name: str):
        self.name = name
        self.update()
    
    def __init__(self, name: str, url: str, base64: str):
        self.name = name
        self.url = url
        self.base64 = base64

    @staticmethod
    def from_name(mapname: str) -> dict[str, str]:
        _name = f"compass_map_{mapname.lower()}"
        return Minimap(name=_name, url=None, base64=None).update()

    def update(self):
        mapname = self.name.replace('preview_','')
        response = get(f"https://raw.githubusercontent.com/xlabs-mirror/iw4-resources/main/compass/{mapname}.png")
        if response.status_code != 200:
            response = get(f"https://callofdutymaps.com/wp-content/uploads/{mapname.lower().removeprefix('mp_')}compass.png")
        if response.status_code != 200:
            response = get(f"http://www.themodernwarfare2.com/images/mw2/maps/{mapname.lower().removeprefix('mp_')}-layout.jpg")
        if response.status_code == 200:
            self.url = response.url
            self.base64 = None # urlsafe_b64encode(response.content).decode("utf-8")
            with open(f"P:/Python/iw4/iw4-resources/compass/{mapname}.png", "wb") as f:
                f.write(response.content)
        else:
            print("Could not get minimap img from",response.url)
            self.url = None;self.base64 = None
        return self

    @staticmethod
    def from_dict(obj: Any) -> 'Minimap':
        if obj is None: return None
        _name = get_safe(obj, "name")
        _url = get_safe(obj, "url")
        _base64 = get_safe(obj, "base64")
        return Minimap(name=_name, url=_url, base64=_base64)

@dataclass
class Preview:
    name: Optional[str] = None
    url: Optional[str] = None
    base64: Optional[str] = None

    def init(self, name: str):
        self.name = name
        self.update()
    
    def __init__(self, name: str = None, url: str = None, base64: str = None):
        self.name = name
        self.url = url
        self.base64 = base64

    @staticmethod
    def from_mapname(mapname: str) -> 'Preview':
        _name = f"preview_{mapname}"
        return Preview(_name, None, None).update()
    
    def update(self):
        mapname = self.name.replace('preview_','')
        response = get(f"https://raw.githubusercontent.com/xlabs-mirror/iw4-resources/main/preview/{mapname}.png")
        if response.status_code != 200:
            response = get(f"https://callofdutymaps.com/wp-content/uploads/{mapname.lower().removeprefix('mp_')}1-1500x500.jpg")
        if response.status_code != 200:
            response = get(f"http://www.themodernwarfare2.com/images/mw2/maps/{mapname.lower().removeprefix('mp_')}-prev.jpg")
        if response.status_code != 200:
            response = get(f"http://www.themodernwarfare2.com/images/mw2/maps/{mapname.lower().removeprefix('mp_')}-t.jpg")
        if response.status_code != 200:
            response = get(f"https://image.gametracker.com/images/maps/160x120/cod4/{mapname}.jpg")
        if response.status_code == 200:
            self.url = response.url
            # self.base64 = urlsafe_b64encode(response.content).decode("utf-8")
            with open(f"P:/Python/iw4/iw4-resources/preview/{mapname}.png", "wb") as f:
                f.write(response.content)
        else:
            print("Could not get preview img from",response.url)
            self.url = None;self.base64 = None
        return self

    @staticmethod
    def from_dict(obj: Any) -> 'Preview':
        if obj is None: return None
        _name = get_safe(obj, "name")
        _url = get_safe(obj, "url")
        _base64 = get_safe(obj, "base64")
        return Preview(_name, _url, _base64)

@dataclass
class Waypoints:
    file: Optional[str] = None
    url: Optional[str] = None
    md5: Optional[str] = None
    count: Optional[int] = None

    def update(self, url = None):
        response = get(url or self.url)
        self.file = response.text if response.status_code == 200 else None
        self.md5 = md5(self.file.encode("utf-8")).hexdigest() if response.status_code == 200 else None
        self.count = self.file.partition('\n')[0] if response.status_code == 200 else None
        return self

    @staticmethod
    def from_mapname(mapname: str) -> 'Waypoints':
        file = f"{mapname}_wp.csv"
        url = f"https://raw.githubusercontent.com/xlabs-mirror/iw4x-bot-waypoints/master/{file}"
        ret = Waypoints(file, url)
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
    minimap: Optional[Minimap] = None
    waypoints: Optional[Waypoints] = None

    @staticmethod
    def from_mapname(name: str, source: Source = None, strmap:StringMaps = None) -> 'MapListMap':
        displayname = Name.from_mapname(name, strmap)
        return MapListMap(
            source=source,
            name=displayname,
            description=Description.from_name(displayname=displayname['english'], strmap=strmap, source=source),
            preview=Preview.from_mapname(name),
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
        _minimap = Minimap.from_dict(get_safe(obj, "minimap"))
        _waypoints = Waypoints.from_dict(get_safe(obj, "waypoints"))
        return MapListMap(_source, _name, _description, _preview, _minimap, _waypoints)
