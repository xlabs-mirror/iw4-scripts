from pathlib import Path
from sys import path as syspath
from os import getcwd
syspath.append(getcwd())

from parser import *

maplist = Maplist.load("iw4-resources/maps.json")

stringmaps = StringMaps()
stringmaps.parse_files(stringmaps.get_files())

for lang, strings in stringmaps.strings.items():
    print(lang, len(strings))

def load_maps(file):
    with open(file, 'r') as f:
        return f.read().splitlines()

def set_maps_source(file, source, stringmaps = None):
    map_array = load_maps(file)
    for mapname in map_array:
        if mapname not in maplist.maps:
            maplist.maps[mapname] = Map.from_mapname(mapname, source, stringmaps)
        maplist.maps[mapname].source = source

def add_maps(file, source, stringmaps = None):
    map_array = load_maps(file)
    for mapname in map_array:
        maplist.maps[mapname] = Map.from_mapname(mapname, source, stringmaps)


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

maplist.save('iw4-resources/maps.json')
