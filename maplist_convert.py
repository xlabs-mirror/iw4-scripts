from copy import copy
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
from maplist.image import IWImage, PNGImage

def load_maps(file, as_json = False):
    with open(file, 'r') as f:
        return f.read().splitlines() if not as_json else json_load(f)

logger = getLogger(__name__)
basicConfig(level=DEBUG)
#region loading
dir = Path("P:\Python\iw4\iw4-resources")

# maplist_file = dir / "maps.json"
# exit(0)

maplist = Maplist.load(dir / "maps.json")
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
#endregion loading
#region check_missing
for act in campaignlist.Acts:
    for i, mission in enumerate(act.missions):
        if mission.mapname:
            if mission.mapname not in maplist.maps.keys():
                logger.warning(f"Missing map {mission.mapname} for campaign mission {mission.title}")
for act in specopslist.Acts:
    for i, mission in enumerate(act.missions):
        if mission.mapname:
            if mission.mapname not in maplist.maps.keys():
                logger.warning(f"Missing map {mission.mapname} for specops mission {mission.title}")
mission = act = i = None                
for txtmap in txtlist:
    if txtmap not in maplist.maps.keys():
        print(f"Missing txtmap {txtmap}")
#endregion check_missing
# region map_related_methods
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

def get_map_subtitle(mapname):            
    campaign_mission, campaign_act = campaignlist.get_by_mapname(mapname)
    if campaign_mission: return f"Campaign {campaign_act.title['english']}: {campaign_mission.title['english']} (#{campaign_mission.index})"
    specops_mission, specops_act = specopslist.get_by_mapname(mapname)
    if specops_mission: return f"Spec Ops {specops_act.title['english']}: {specops_mission.title['english']} (#{specops_mission.index})"
    mainmap = maplist.maps[mapname]
    return (f"{mainmap.source.name}: " if mainmap.source.name else "") + f"{mainmap.title['english']}" + (f" (#{mainmap.index})" if mainmap.index else "")
#endregion map_related_methods

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
#                 # map.title['english'] = f"{mission.title['english']} (#{mission.index})"
#                 map.index = mission.index
#                 break
#     for act in specopslist.Acts:
#         for mission in act.missions:
#             if mission.mapname == mapname:
#                 logger.debug(f"Found mission {mission.title} for map {mapname}")
#                 map.index = mission.index


# for mapname, map in maplist.maps.items():
#     if map.alternatives and isinstance(map.alternatives, list):
#         map.alternatives = {alternative: "" for alternative in map.alternatives}

# alt_items = alternatives_dict.items()
# mapnames = maplist.maps.keys()

# for mainmapname, alternatives in alt_items:
#     if mainmapname in mapnames:
#         for alternative in alternatives:
#             mainmap = maplist.maps[mainmapname]
#             alternative_map = copy(mainmap)
#             alternative_map.mapname = alternative
            
#             new_alternatives = {k: v for k, v in mainmap.alternatives.items()}


#             del new_alternatives[alternative]
#             new_alternatives[mainmapname] = mainmap.title['english']
            
#             alternative_map.alternatives = new_alternatives
#             maplist.maps[alternative] = alternative_map
#             logger.debug(f"[{mainmapname}] new alternative: {alternative_map.mapname}")
        

# for mapname, map in maplist.maps.items():
#     if not map.alternatives: continue
#     if mapname in map.alternatives.keys():
#         del map.alternatives[mapname]
#     for alternative, title in map.alternatives.items():
#         map.alternatives[alternative] = get_map_subtitle(alternative)

# for mapname, map in maplist.maps.items():
#     if map.preview:
#         preview = map.preview
#         map.preview = Preview(
#             iwi=IWImage(
#                 filename=preview["filename"]
#             ),
#             png=PNGImage(
#                 filename=mapname + ".png",
#                 md5=preview["md5"] if "md5" in preview else None,
#                 url=preview["url"] if "url" in preview else None
#             )
#         )
#     if map.loadscreen:
#         loadscreen = map.loadscreen
#         map.loadscreen = Loadscreen(
#             iwi=IWImage(
#                 filename=loadscreen["filename"]
#             ),
#             png=PNGImage(
#                 filename=mapname + ".png",
#                 md5=loadscreen["md5"] if "md5" in loadscreen else None,
#                 url=loadscreen["url"] if "url" in loadscreen else None
#             )
#         )
#     if map.minimap:
#         minimap = map.minimap
#         map.minimap = Minimap(
#             iwi=IWImage(
#                 filename=minimap["filename"]
#             ),
#             png=PNGImage(
#                 filename=mapname + ".png",
#                 md5=minimap["md5"] if "md5" in minimap else None,
#                 url=minimap["url"] if "url" in minimap else None
#             )
#         )

for txtmap in txtlist:
    if txtmap not in maplist.maps:
        maplist.maps[txtmap] = MapListMap.from_mapname(txtmap)
        maplist.maps[txtmap].source = Source("Unknown", "https://tinyurl.com/iw4xmaps")

# maplist.update()
        

maplist.save('P:\Python\iw4\iw4-resources\maps_out.json')
