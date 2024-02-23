from base64 import urlsafe_b64encode
from typing import Any, Optional
from dataclasses import dataclass
from requests import get
from hashlib import md5
from maplist.campaign import Mission
from parser.stringmap import StringMaps
from maplist.source import Source
from maplist.image import Preview, Loadscreen, Minimap
from maplist.campaign import CampaignList
from maplist.specops import SpecOpsList
from maplist.file import FileBase
from utils import get_safe, get_fallback

from logging import getLogger
logger = getLogger(__name__)

@dataclass
class Title:
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
    def from_name(title: str, strmap:StringMaps = None, source = None) -> dict[str, str]:
        english = f"{title} is a map for Call of Duty: Modern Warfare 2."
        if source:
            if source == "Custom Maps": english = f"{title} is a custom map."
            else: english = f"{title} is a map from {source}."
        ret = {
            "_key": f"MPUI_DESC_MAP_{title.upper().replace(' ', '_')}",
            "english": english,
        }
        if strmap:
            for lang, strings in strmap.strings.items():
                print("Getting",lang,"value for", ret["_key"])
                if ret["_key"] in strings.keys():
                    ret[lang] = strings.get(ret["_key"])
        return ret

@dataclass
class Waypoints(FileBase):
    count: Optional[int] = None
    def update(self, base64 = False, map: 'MapListMap' = None) -> 'Waypoints':
        filename = self.filename or self.get_filename(map.mapname) if map else None
        if not filename: raise Exception("No filename for waypoints file!")
        urls = [
            f"https://raw.githubusercontent.com/xlabs-mirror/iw4-resources/main/waypoints/{filename}",
            f"https://raw.githubusercontent.com/ineedbots/iw4_bot_warfare/master/scriptdata/waypoints/{filename}",
            f"https://raw.githubusercontent.com/xlabs-mirror/iw4x-bot-waypoints/master/{filename}"
        ]
        logger.debug(f"Updating waypoints for {filename} from {len(urls)} urls")
        response = super().update(urls, filename, base64)
        if response:
            self_declared_count = response.text.split('\n', 1)[0]
            real_count = len(response.text.splitlines()) - 1
            if self_declared_count != real_count:
                msg = f"[{filename}] Declared waypoints count {self_declared_count} does not match real waypoints count {real_count}"
                logger.warning(msg); raise Exception(msg)
            self.count = real_count
        else: self.count = None
        return self
    
    def get_mapname(self) -> str: return Waypoints.get_mapname(self.filename)
    @staticmethod
    def get_filename(mapname: str) -> str:
        return f"{mapname}_wp.csv"
    @staticmethod
    def get_mapname(filename: str) -> str:
        return filename.removesuffix('_wp.csv')

    @staticmethod
    def from_mapname(mapname: str) -> 'Waypoints':
        ret = Waypoints(Waypoints.get_filename(mapname))
        ret.update()
        return ret

    @staticmethod
    def from_dict(obj: Any) -> 'Waypoints':
        if obj is None: return None
        _filename = get_safe(obj, "filename")
        _url = get_safe(obj, "url")
        _md5 = get_safe(obj, "md5")
        _count = get_safe(obj, "count")
        if _count: _count = int(_count) # todo: remove
        if _count and not isinstance(_count, int): _msg = f"Waypoints count is an {type(_count)} (excpected: int): \"{_count}\""; logger.warning(_msg); raise Exception(_msg)
        _base64 = get_safe(obj, "base64")
        return Waypoints(filename=_filename, url=_url, md5=_md5, count=_count, base64=_base64) # todo: remove

@dataclass
class MapListMap:
    index: Optional[int] = None
    mapname: Optional[str] = None
    source: Optional[Source] = None
    title: Optional[dict[str,str]] = None
    description: Optional[dict[str,str]] = None
    preview: Optional[Preview] = None
    loadscreen: Optional[Loadscreen] = None
    minimap: Optional[Minimap] = None
    waypoints: Optional[Waypoints] = None
    alternatives: Optional[dict[str,str]] = None

    @staticmethod
    def from_mapname(mapname: str, source: Source = None, strmap:StringMaps = None) -> 'MapListMap':
        title = Title.from_mapname(mapname, strmap)
        return MapListMap(
            index=None,
            mapname=mapname,
            source=source,
            title=title,
            description=Description.from_name(displayname=title['english'], strmap=strmap, source=source),
            preview=Preview.from_mapname(mapname),
            loadscreen=Loadscreen.from_mapname(mapname),
            minimap=Minimap.from_mapname(mapname),
            waypoints=Waypoints.from_mapname(mapname)
        )

    @staticmethod
    def from_dict(obj: Any) -> 'MapListMap':
        if obj is None: return None
        _index = get_safe(obj, "index")
        _mapname = get_safe(obj, "mapname")
        _title = get_safe(obj, "title")
        _description = get_safe(obj, "description")
        _source = Source.from_dict(get_safe(obj, "source"))
        # except: _source = Source(SourceID.from_dict(get_safe(obj, "source")))
        _preview = get_safe(obj, "preview") # Preview.from_dict(get_safe(obj, "preview"))
        _loadscreen = get_safe(obj, "loadscreen") # Loadscreen.from_dict(get_safe(obj, "loadscreen"))
        _minimap = get_safe(obj, "minimap") # Minimap.from_dict(get_safe(obj, "minimap"))
        _waypoints = Waypoints.from_dict(get_safe(obj, "waypoints"))
        _alternatives = get_safe(obj, "alternatives")
        return MapListMap(index=_index, mapname=_mapname, title=_title, source=_source, description=_description, preview=_preview, loadscreen=_loadscreen, minimap=_minimap, waypoints=_waypoints, alternatives=_alternatives)

    def update(self) -> 'MapListMap':
        logger.debug(f"Updating {self.mapname}")
        if self.preview: self.preview.update(map=self)
        else: self.preview = Preview.from_mapname(self.mapname)
        if self.loadscreen: self.loadscreen.update(map=self)
        else: self.loadscreen = Loadscreen.from_mapname(self.mapname)
        if self.minimap: self.minimap.update(map=self)
        else: self.minimap = Minimap.from_mapname(self.mapname)
        if self.waypoints: self.waypoints.update(map=self)
        else: self.waypoints = Waypoints.from_mapname(self.mapname)
        return self
    
    def get_campaign_mission(self, campaign: CampaignList) -> Mission:
        for act in campaign.Acts:
            for mission in act.missions:
                if mission.mapname == self.mapname:
                    return mission
        return None
    def get_specops_mission(self, specops: SpecOpsList) -> Mission:
        for act in specops.Acts:
            for mission in act.missions:
                if mission.mapname == self.mapname:
                    return mission
        return None