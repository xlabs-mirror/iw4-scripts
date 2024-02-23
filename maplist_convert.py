from pathlib import Path
from sys import path as syspath
from os import getcwd
syspath.append(getcwd())

from pprint import pprint
from json import dumps as json_dumps, load as json_load
from logging import getLogger, basicConfig, DEBUG
from maplist import Maplist
from maplist.map import MapListMap, Preview, Loadscreen, Minimap, Waypoints
from maplist.campaign import CampaignList, CampaignMission, Location, Mission
from maplist.source import Source, SourceID
from maplist.specops import SpecOpsList, SpecOpsMission

logger = getLogger(__name__)
basicConfig(level=DEBUG)

dir = Path("P:\Python\iw4\iw4-resources")

maplist = Maplist.load(dir / "maps.json")
logger.info(f"Loaded {len(maplist.maps)} maps")

campaignlist = CampaignList.load(dir / "campaign.json")
campaign_mission_count = sum(len(act.missions) for act in campaignlist.Acts)
logger.info(f"Loaded {campaign_mission_count} missions from {len(campaignlist.Acts)} campaign acts")

specopslist = SpecOpsList.load(dir / "specops.json")
specops_mission_count = sum(len(act.missions) for act in specopslist.Acts)
logger.info(f"Loaded {specops_mission_count} missions from {len(specopslist.Acts)} specops acts")

# stringmaps = StringMaps()
# stringmaps.parse_files(stringmaps.get_files())

# for lang, strings in stringmaps.strings.items():
#     print(lang, len(strings))

def load_maps(file, as_json = False):
    with open(file, 'r') as f:
        return f.read().splitlines() if not as_json else json_load(f)
    
txtlist = load_maps(dir / "maps.txt")
logger.info(f"Loaded {len(txtlist)} txt maps")
alternatives_list = load_maps(dir / "alternatives.json", True)
logger.info(f"Loaded {len(alternatives_list)} alternatives")

def set_maps_source(file, source, stringmaps = None):
    map_array = load_maps(file)
    for mapname in map_array:
        if mapname not in maplist.maps:
            maplist.maps[mapname] = MapListMap.from_mapname(mapname, source, stringmaps)
        maplist.maps[mapname].source = source

def add_maps(file, source, stringmaps = None):
    map_array = load_maps(file)
    for mapname in map_array:
        maplist.maps[mapname] = MapListMap.from_mapname(mapname, source, stringmaps)


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

# for txtmap in txtlist:
#     if txtmap not in mapnames:
#         print(f"Missing {txtmap}")

# for mapname, map in maplist.maps.items():
    # if source url is list turn from [ "https", "tinyurl.com", "/iw4xmaps", "", "", "" ] to normal url
    # $map["source"]["url"] = $source_url[0] . "://" . $source_url[1] . $source_url[2];
    # for campaign_name, campaign in campaignlist.Acts.items():
    #     for mission in campaign:
    #         if mission.mapname == mapname:
    #             logger.debug(f"Found mission {mission.name} for map {mapname}")
    #             map.mission = mission
    #             map.mission.mapname = None
    #             break

# for campaign_name, campaign in campaignlist.Acts.items():
#     for i, mission in enumerate(campaign):
#         if mission.mapname:
#             if mission.mapname not in maplist.maps.keys():
#                 logger.warning(f"Missing map {mission.mapname} for mission {mission.name}")


maplist.save('P:\Python\iw4\iw4-resources\maps_out.json')
