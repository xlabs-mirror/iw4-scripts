from base64 import urlsafe_b64encode
from typing import Any, Optional
from dataclasses import dataclass
from requests import get
from hashlib import md5
from utils import get_safe

@dataclass
class Image:
    # types: ["preview", "compass", "loadscreen"]
    name: Optional[str] = None
    url: Optional[str] = None
    md5: Optional[str] = None
    base64: Optional[str] = None

    def init(self, name: str):
        self.name = name
        self.update()
    
    def __init__(self, name: str = None, url: str = None, md5: str = None, base64: str = None):
        self.name = name
        self.url = url
        self.md5 = md5
        self.base64 = base64

    @staticmethod
    def from_mapname(mapname: str, type: str = "preview") -> 'Image':
        _name = f"{type}_{mapname}"
        return Image(_name).update()

    @staticmethod
    def from_dict(obj: Any) -> 'Image':
        if not obj: return None
        _name = get_safe(obj, "name")
        _url = get_safe(obj, "url")
        _md5 = get_safe(obj, "md5")
        _base64 = get_safe(obj, "base64")
        return Image(_name, _url, _md5, _base64)
    
    def update(self, base64: bool = False, type: str = "preview"):
        mapname = self.name.replace(f'{type}_','')
        response = get(f"https://raw.githubusercontent.com/xlabs-mirror/iw4-resources/main/{type}/{mapname}.png")
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
            self.md5 = md5(response.content).hexdigest()
            if base64: self.base64 = urlsafe_b64encode(response.content).decode("utf-8")
            with open(f"P:/Python/iw4/iw4-resources/{type}/{mapname}.png", "wb") as f:
                f.write(response.content)
        else:
            print("Could not get {type} img from",response.url)
            self.url = None;self.md5 = None;self.base64 = None
        return self
@dataclass
class Preview(Image):
    @staticmethod
    def from_mapname(mapname: str) -> 'Image':
        return Image.from_mapname(mapname, "preview")
    
    def update(self, base64: bool = False):
        return super().update(base64, "preview")
@dataclass
class Loadscreen(Image):
    @staticmethod
    def from_mapname(mapname: str) -> 'Loadscreen':
        return Image.from_mapname(mapname, "loadscreen")
    
    def update(self, base64: bool = False) -> 'Loadscreen':
        return super().update(base64, "loadscreen")
@dataclass
class Minimap(Image):
    
    @staticmethod
    def from_name(mapname: str) -> 'Minimap':
        _name = f"compass_map_{mapname.lower()}"
        return Minimap(name=_name, url=None, base64=None).update()

    def update(self) -> 'Minimap':
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