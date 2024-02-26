from base64 import urlsafe_b64encode
from typing import Any, Optional
from dataclasses import dataclass
from requests import get
from hashlib import md5
from pathlib import Path
from utils import get_safe, get_fallback
from maplist.file import FileBase
from typing import TYPE_CHECKING
if TYPE_CHECKING: from maplist.map import MapListMap

from logging import getLogger
logger = getLogger(__name__)

@dataclass
class Image(FileBase):
    # types: ["preview", "compass", "loadscreen"]

    def get_mapname(self) -> str: return Image.get_mapname(self.filename)
    @staticmethod
    def get_mapname(filename: str) -> str:
        return filename.removesuffix('.iwi').removesuffix('.png').removesuffix('.jpg')
    @staticmethod
    def from_dict(obj: Any) -> 'Image':
        if not obj: return None
        _filename = get_safe(obj, "filename") or get_safe(obj, "name")
        _url = get_safe(obj, "url")
        _md5 = get_safe(obj, "md5")
        _base64 = get_safe(obj, "base64")
        return Image(filename=_filename, url=_url, md5=_md5, base64=_base64)
    
    def update(self, imagetype: str, urls: list[str], base64: bool = False, map: 'MapListMap' = None):
        filename = self.filename
        if not filename: raise Exception("No filename for image file!")
        mapname = map.mapname or self.get_mapname(filename)
        logger.debug(f"Updating {imagetype} image for {mapname}: {filename}")
        mapname = mapname.lower()
        # noprefix = mapname.removeprefix('mp_')
        response = super().update(urls, filename, base64)
        if response:
            target_path = Path(f"P:/Python/iw4/iw4-resources/{imagetype}/{mapname}.png")
            if target_path.exists():
                logger.warn(f"File {target_path} already exists")
                return self
            with open(target_path, "wb") as f:
                f.write(response.content)
        else:
            logger.warn(f"Could not get {imagetype} img for {mapname}")
        return self
iwi_extension = ".iwi"
@dataclass
class IWImage(Image):
    @staticmethod
    def from_filename(filename: str) -> Image:
        return Image(filename + iwi_extension)
    @staticmethod
    def get_filename(mapname: str) -> str:
        return mapname + iwi_extension

png_extension = ".png"
@dataclass
class PNGImage(Image):
    @staticmethod
    def from_filename(filename: str) -> Image:
        return Image(filename + png_extension)
    @staticmethod
    def get_filename(mapname: str) -> str:
        return mapname + png_extension

prefix_preview = "preview_"
@dataclass
class Preview():
    iwi: Optional[IWImage] = None
    png: Optional[PNGImage] = None
    @staticmethod
    def from_dict(obj: Any) -> 'Preview':
        if not obj: return None
        return Preview(iwi=get_safe(obj, "iwi"), png=get_safe(obj, "png"))
    @staticmethod
    def from_mapname(mapname: str) -> 'Preview':
        return Preview(
            IWImage.from_filename(filename=prefix_preview+mapname),
            PNGImage.from_filename(filename=prefix_preview+mapname)
        )
    
    def get_mapname(self) -> str|None:
        if self.iwi: return Preview.get_mapname(filename=self.iwi.filename)
        if self.png: return Preview.get_mapname(filename=self.png.filename)
        return None
    @staticmethod
    def get_mapname(filename: str) -> str|None:
        return Image.get_mapname(filename=filename).removeprefix(prefix_preview)
    def update(self, base64: bool = False, mapname: str = None, map: 'MapListMap' = None) -> 'Preview':
        imagetype = "preview"
        mapname = mapname or (map.mapname if map else None)
        if not mapname: raise Exception(f"No mapname for {imagetype}")
        noprefix = mapname.removeprefix('mp_')
        urls = [
            f"https://raw.githubusercontent.com/xlabs-mirror/iw4-resources/main/{imagetype}/{mapname}.png",
            f"https://callofdutymaps.com/wp-content/uploads/{noprefix}1-1500x500.jpg",
            f"http://www.themodernwarfare2.com/images/mw2/maps/{noprefix}-prev.jpg",
            f"https://image.gametracker.com/images/maps/160x120/cod4/{mapname}.jpg"
        ]
        if self.iwi: self.iwi.update(imagetype=imagetype, urls=urls, base64=base64, map=map)
        if self.png: self.png.update(imagetype=imagetype, urls=urls, base64=base64, map=map)
        return self
prefix_loadscreen = "loadscreen_map_"
@dataclass
class Loadscreen():
    iwi: Optional[IWImage] = None
    png: Optional[PNGImage] = None
    @staticmethod
    def from_dict(obj: Any) -> 'Loadscreen':
        if not obj: return None
        return Loadscreen(iwi=get_safe(obj, "iwi"), png=get_safe(obj, "png"))
    @staticmethod
    def from_mapname(mapname: str) -> 'Loadscreen':
        return Loadscreen(
            IWImage.from_filename(prefix_loadscreen+mapname),
            PNGImage.from_filename(prefix_loadscreen+mapname)
        )

    def get_mapname(self) -> str|None:
        if self.iwi: return Loadscreen.get_mapname(self.iwi.filename)
        if self.png: return Loadscreen.get_mapname(self.png.filename)
        return None
    @staticmethod
    def get_mapname(filename: str) -> str|None:
        return Image.get_mapname(filename).removeprefix(prefix_preview)
    def update(self, base64: bool = False, mapname: str = None, map: 'MapListMap' = None) -> 'Loadscreen':
        imagetype = "loadscreen"
        mapname = mapname or (map.mapname if map else None)
        if not mapname: raise Exception(f"No mapname for {imagetype}")
        # noprefix = mapname.removeprefix('mp_')
        urls = [
            f"https://raw.githubusercontent.com/xlabs-mirror/iw4-resources/main/{imagetype}/{mapname}.png",
        ]
        if self.iwi: self.iwi.update(imagetype=imagetype, urls=urls, base64=base64, map=map)
        if self.png: self.png.update(imagetype=imagetype, urls=urls, base64=base64, map=map)
        return self
prefix_minimap = "compass_"
@dataclass
class Minimap():
    iwi: Optional[IWImage] = None
    png: Optional[PNGImage] = None
    @staticmethod
    def from_dict(obj: Any) -> 'Minimap':
        if not obj: return None
        return Minimap(iwi=get_safe(obj, "iwi"), png=get_safe(obj, "png"))
    @staticmethod
    def from_mapname(mapname: str) -> 'Minimap':
        return Minimap(
            IWImage.from_filename(filename=prefix_minimap+mapname),
            PNGImage.from_filename(filename=prefix_minimap+mapname)
        )

    def get_mapname(self) -> str|None:
        if self.iwi: return Minimap.get_mapname(self.iwi.filename)
        if self.png: return Minimap.get_mapname(self.png.filename)
        return None
    @staticmethod
    def get_mapname(filename: str) -> str|None:
        return Image.get_mapname(filename).removeprefix(prefix_preview)
    def update(self, base64: bool = False, mapname: str = None, map: 'MapListMap' = None) -> 'Minimap':
        imagetype = "compass"
        mapname = mapname or (map.mapname if map else None)
        if not mapname: raise Exception(f"No mapname for {imagetype}")
        noprefix = mapname.removeprefix('mp_')
        urls = [
            f"https://raw.githubusercontent.com/xlabs-mirror/iw4-resources/main/{imagetype}/{mapname}.png",
            f"https://callofdutymaps.com/wp-content/uploads/{noprefix}compass.png",
            f"http://www.themodernwarfare2.com/images/mw2/maps/{noprefix}-layout.jpg"
        ]
        if self.iwi: self.iwi.update(imagetype=imagetype, urls=urls, base64=base64, map=map)
        if self.png: self.png.update(imagetype=imagetype, urls=urls, base64=base64, map=map)
        return self