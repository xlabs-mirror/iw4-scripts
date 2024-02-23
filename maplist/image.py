from base64 import urlsafe_b64encode
from typing import Any, Optional
from dataclasses import dataclass
from requests import get
from hashlib import md5
from utils import get_safe, get_fallback
try: from maplist.map import MapListMap
except: pass

from logging import getLogger
logger = getLogger(__name__)

@dataclass
class Image:
    # types: ["preview", "compass", "loadscreen"]
    filename: Optional[str] = None
    name: Optional[str] = None
    url: Optional[str] = None
    md5: Optional[str] = None
    base64: Optional[str] = None

    def init(self, filename: str):
        self.filename = filename
        self.update()
    
    def __init__(self, filename: str = None, url: str = None, md5: str = None, base64: str = None):
        self.filename = filename
        self.url = url
        self.md5 = md5
        self.base64 = base64
    
    def get_mapname(self) -> str: return Image.get_mapname(self.filename)

    @staticmethod
    def get_filename(mapname: str) -> str:
        return f"{mapname}.iwi"
    @staticmethod
    def get_mapname(filename: str) -> str:
        return filename.removesuffix('.iwi')
    @staticmethod
    def from_mapname(mapname: str) -> 'Image':
        return Image(Image.get_filename(mapname)).update()
    @staticmethod
    def from_dict(obj: Any) -> 'Image':
        if not obj: return None
        _filename = get_safe(obj, "filename") or get_safe(obj, "name")
        _url = get_safe(obj, "url")
        _md5 = get_safe(obj, "md5")
        _base64 = get_safe(obj, "base64")
        return Image(_filename, _url, _md5, _base64)
    
    def update(self, base64: bool = False, type: str = "preview", map: 'MapListMap' = None):
        mapname = map.mapname or self.get_mapname()
        logger.debug(f"Updating {type} image for {mapname}")
        mapname = mapname.lower()
        noprefix = mapname.removeprefix('mp_')
        response = get_fallback([
            f"https://raw.githubusercontent.com/xlabs-mirror/iw4-resources/main/{type}/{mapname}.png",
            f"https://callofdutymaps.com/wp-content/uploads/{noprefix}1-1500x500.jpg",
            f"http://www.themodernwarfare2.com/images/mw2/maps/{noprefix}-prev.jpg",
            f"https://image.gametracker.com/images/maps/160x120/cod4/{mapname}.jpg"
        ])
        if response:
            self.url = response.url
            self.md5 = md5(response.content).hexdigest()
            if base64: self.base64 = urlsafe_b64encode(response.content).decode("utf-8")
            with open(f"P:/Python/iw4/iw4-resources/{type}/{mapname}.png", "wb") as f:
                f.write(response.content)
        else:
            logger.warn(f"Could not get {type} img from {response.url}")
            self.url = None;self.md5 = None;self.base64 = None
        return self
prefix_preview = "preview_"
@dataclass
class Preview(Image):
    def get_mapname(self) -> str: return Preview.get_mapname(self.filename)
    @staticmethod
    def get_filename(mapname: str) -> str:
        return f"{prefix_preview}{Image.get_filename(mapname)}"
    @staticmethod
    def get_mapname(filename: str) -> str:
        return Image.get_mapname(filename).removeprefix(prefix_preview)
    @staticmethod
    def from_mapname(mapname: str) -> 'Image':
        return Image.from_mapname(mapname, "preview")
    def update(self, base64: bool = False):
        return super().update(base64=base64, type="preview")
prefix_loadscreen = "loadscreen_map_"
@dataclass
class Loadscreen(Image):
    def get_mapname(self) -> str: return Loadscreen.get_mapname(self.filename)
    @staticmethod
    def get_filename(mapname: str) -> str:
        return f"{prefix_loadscreen}{Image.get_filename(mapname)}"
    @staticmethod
    def get_mapname(filename: str) -> str:
        return Image.get_mapname(filename).removeprefix(prefix_loadscreen)
    @staticmethod
    def from_mapname(mapname: str) -> 'Loadscreen':
        return Image.from_mapname(mapname, "loadscreen")
    def update(self, base64: bool = False):
        return super().update(base64=base64, type="loadscreen")
prefix_minimap = "compass_"
@dataclass
class Minimap(Image):
    def get_mapname(self) -> str: return Minimap.get_mapname(self.filename)
    @staticmethod
    def get_filename(mapname: str) -> str:
        return f"{prefix_minimap}{Image.get_filename(mapname)}"
    @staticmethod
    def get_mapname(filename: str) -> str:
        return Image.get_mapname(filename).removeprefix(prefix_minimap)
    @staticmethod
    def from_mapname(mapname: str) -> 'Minimap':
        return Image.from_mapname(mapname, "compass")
    def update(self, base64: bool = False, map: 'MapListMap' = None) -> 'Minimap':
        mapname = (map.mapname or self.get_mapname()).lower()
        noprefix = mapname.lower().removeprefix('mp_')
        response = get_fallback([
            f"https://raw.githubusercontent.com/xlabs-mirror/iw4-resources/main/compass/{mapname}.png",
            f"https://callofdutymaps.com/wp-content/uploads/{noprefix}compass.png",
            f"http://www.themodernwarfare2.com/images/mw2/maps/{noprefix}-layout.jpg"
        ])
        if response:
            self.url = response.url
            self.md5 = md5(response.content).hexdigest()
            if base64: self.base64 = urlsafe_b64encode(response.content).decode("utf-8")
            with open(f"P:/Python/iw4/iw4-resources/compass/{mapname}.png", "wb") as f:
                f.write(response.content)
        else:
            logger.warn(f"Could not get minimap img from {response.url}")
            self.url = None;self.base64 = None;self.md5 = None
        return self