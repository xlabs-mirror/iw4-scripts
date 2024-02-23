from pathlib import Path
from sys import path as syspath
from os import getcwd
syspath.append(getcwd())

from pprint import pprint
from json import dumps as json_dumps, load as json_load
from logging import getLogger, basicConfig, DEBUG
from maplist import Maplist
from maplist.map import MapListMap, Preview, Loadscreen, Minimap, Waypoints
from maplist.campaign import CampaignList, CampaignMission, Location, Mission, CampaignAct
from maplist.source import Source, SourceID
from maplist.specops import SpecOpsList, SpecOpsMission, SpecOpsAct

def load_maps(file, as_json = False):
    with open(file, 'r') as f:
        return f.read().splitlines() if not as_json else json_load(f)

logger = getLogger(__name__)
basicConfig(level=DEBUG)

dir = Path("P:\Python\iw4\iw4-resources")

maplist = Maplist.load(dir / "maps_out.json")
logger.info(f"Loaded {maplist}")

campaignlist = CampaignList.load(dir / "campaign.json")
logger.info(f"Loaded {campaignlist}")

specopslist = SpecOpsList.load(dir / "specops.json")
logger.info(f"Loaded {specopslist}")

# stringmaps = StringMaps()
# stringmaps.parse_files(stringmaps.get_files())

# for lang, strings in stringmaps.strings.items():
#     print(lang, len(strings))
    
txtlist = load_maps(dir / "maps.txt")
logger.info(f"Loaded {len(txtlist)} txt maps")
alternatives_dict: dict[str, list[str]] = load_maps(dir / "alternatives.json", True)
logger.info(f"Loaded {len(alternatives_dict)} alternatives")

for act in campaignlist.Acts:
    for i, mission in enumerate(act.missions):
        if mission.mapname:
            if mission.mapname not in maplist.maps.keys():
                logger.warning(f"Missing map {mission.mapname} for campaign mission {mission.title}")

for specopsact in specopslist.Acts:
    for i, mission in enumerate(specopsact.missions):
        if mission.mapname:
            if mission.mapname not in maplist.maps.keys():
                logger.warning(f"Missing map {mission.mapname} for specops mission {mission.title}")

for txtmap in txtlist:
    if txtmap not in maplist.maps.keys():
        print(f"Missing txtmap {txtmap}")

# def set_maps_source(file, source, stringmaps = None):
#     map_array = load_maps(file)
#     for mapname in map_array:
#         if mapname not in maplist.maps:
#             maplist.maps[mapname] = MapListMap.from_mapname(mapname, source, stringmaps)
#         maplist.maps[mapname].source = source

# def add_maps(file, source, stringmaps = None):
#     map_array = load_maps(file)
#     for mapname in map_array:
#         maplist.maps[mapname] = MapListMap.from_mapname(mapname, source, stringmaps)


# add_maps('maps_main.txt', Source("Call of Duty: Modern Warfare 2"), stringmaps)
# add_maps('maps_dlc_stimulus.txt', Source("Stimulus DLC", "https://tinyurl.com/iw4xmaps"), stringmaps)
# add_maps('maps_dlc_resurgence.txt', Source("Resurgence DLC", "https://tinyurl.com/iw4xmaps"), stringmaps)
# add_maps('maps_dlc_codo.txt', Source("IW4x Call of Duty: Online DLC", "https://tinyurl.com/iw4xmaps"), stringmaps)
# add_maps('maps_dlc_cod4.txt', Source("IW4x Call of Duty: Modern Warfare DLC", "https://tinyurl.com/iw4xmaps"), stringmaps)
# add_maps('maps_dlc_mw3.txt', Source("IW4x Call of Duty: Modern Warfare 3 DLC", "https://tinyurl.com/iw4xmaps"), stringmaps)
# add_maps('maps_usermaps.txt', Source("Custom Maps", "https://tinyurl.com/iw4xmaps"), stringmaps)

# maplist.maps['mp_abandon'].source = Map.from_mapname("mp_abandon", Source("Base Game", "https://tinyurl.com/iw4xmaps"), stringmaps)

# for mapname, map in maplist.maps.items():
#     map.preview.update()
#     map.minimap.update()

# i = 0
# for actname, act in campaignlist.Acts.items():
#     source = Source(f"Singleplayer ({actname})", "https://steamcommunity.com/groups/IW4X/discussions/0/1470841715980056455")
#     for mission in act:
#         i += 1
#         mission: Mission
#         if mission.mapname:
#             if mission.mapname not in maplist.maps:
#                 maplist.maps[mission.mapname] = MapListMap(
#                     source=source,
#                     name={"english": mission.name},
#                     description={"english": mission.description}
#                 )
#                 maplist.maps[mission.mapname].preview = Preview(url=mission.preview.url)
#             maplist.maps[mission.mapname].source = source
#             maplist.maps[mission.mapname].name["english"] = f"{i}: " + mission.name.replace("\u00e2\u20ac\u2122","'")
#             maplist.maps[mission.mapname].description["english"] = mission.description.replace("\u00e2\u20ac\u2122","'")

# mission_mapnames = [mission.mapname for act in campaignlist.Acts.values() for mission in act if mission.mapname]

# mapnames = [mapname for mapname in maplist.maps]
        
    # if source url is list turn from [ "https", "tinyurl.com", "/iw4xmaps", "", "", "" ] to normal url
    # $map["source"]["url"] = $source_url[0] . "://" . $source_url[1] . $source_url[2];

# for act in campaignlist.Acts:
#     for i, mission in enumerate(act.missions):
#         mission.name = {"english": mission.name}
#         mission.description = {"english": mission.description}

# campaignlist.save('P:\Python\iw4\iw4-resources\campaigns_out.json')

# for mapname, map in maplist.maps.items():
#     map.mapname = mapname
#     map.title = map.name
#     map.name = None

# for mapname, map in maplist.maps.items():
#     for act in campaignlist.Acts:
#         for mission in act.missions:
#             if mission.mapname == mapname:
#                 logger.debug(f"Found mission {mission.title} for map {mapname}")
#                 map.title['english'] = f"{mission.title['english']} (#{mission.index})"
#                 break

# for mapname, alternatives in alternatives_dict.items():
#     if not mapname in maplist.maps.keys():
#         logger.warning(f"Map {mapname} not found in maplist")
#         raise Exception(f"Map {mapname} not found in maplist")
#     alt_dict = {}
#     for alternative in alternatives:
#         alt_dict[alternative] = ""
#         mission, act = specopslist.get_by_mapname(alternative)
#         if mission:
#             alt_dict[alternative] = f"Spec Ops {act.title['english']}: {mission.title['english']} (#{mission.index})"
#         mission, act = campaignlist.get_by_mapname(alternative)
#         if mission:
#             alt_dict[alternative] = f"Campaign {act.title['english']}: {mission.title['english']} (#{mission.index})"
#     maplist.maps[mapname].alternatives = alt_dict

# maplist.update()

for mapname, map in maplist.maps.items():
    if map.waypoints:
        map.waypoints.file = f"{mapname}_wp.csv"

maplist.save('P:\Python\iw4\iw4-resources\maps_out2.json')
