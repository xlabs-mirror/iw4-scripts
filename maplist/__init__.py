from dataclasses import dataclass
from pickle import dump as pickle_dump, load as pickle_load
from json import dumps as json_dumps, load as json_load, dump as json_dump
from copy import copy
from pathlib import Path
# from utils import jsencoder

from maplist.map import MapListMap

# def del_none(d):
#     for key, value in list(d.items()):
#         if value is None:
#             del d[key]
#         elif isinstance(value, dict):
#             del_none(value)
#     return d  # For convenience
# def remove_none_values(dictionary:dict):
#     forbbiden_values = [None, "None", "", [], "null"]
#     for key, value in dictionary.items():
#         if value in forbbiden_values:
#             del dictionary[key]
#         elif isinstance(value, dict):
#             remove_none_values(value)
#     return dictionary

@dataclass
class Maplist:
    game: str
    maps: dict[str,'MapListMap']

    @staticmethod
    def from_dict(obj: dict[str,dict[str,'MapListMap']]) -> 'Maplist':
        maps = {}
        for game, _maps in obj.items():
            _maps: dict[str, 'MapListMap']
            for mapname, map in _maps.items():
                maps[mapname] = MapListMap.from_dict(map)
        return Maplist(game, maps)
    
    @staticmethod
    def load(file: Path = 'maps.json'):
        with open(file, 'r', encoding="utf-8") as f:
            jsonstring = json_load(f)
            return Maplist.from_dict(jsonstring)
    
    def save(self, file: Path = 'maps.json'):
        if isinstance(file, str): file = Path(file)
        def filter_object_dict(o):
            # Initialize an empty list to store tuples
            filtered_items = []
            
            if isinstance(o, bytes): o = o.decode('utf-8')
            if isinstance(o, str): return
            # Iterate over all items in the object's __dict__ attribute
            for key, value in o.__dict__.items():
                # Check if the value is truthy
                if value:
                    # Add the key-value pair to the list if the value is truthy
                    filtered_items.append((key, value))
            
            # Convert the list of tuples into a dictionary
            result_dict = dict(filtered_items)
            
            return result_dict

        def recursive_iterate_dict(d: dict):
            for key, value in d.items():
                if isinstance(value, dict):
                    recursive_iterate_dict(value)
                elif isinstance(value, bytes):
                    raise Exception(f"{str(value)} is bytes!")
        if file:
            with open(file.with_suffix(".pickle"), 'wb') as f: pickle_dump(self.maps, f)
        obj = {self.game: {}}
        for mapname, map in self.maps.items():
            obj[self.game][mapname] = dict((key, value) for key, value in map.__dict__.items() if value)
        if file:
            with open(file.with_suffix(".obj.pickle"), 'wb') as f: pickle_dump(obj, f)
        # for game, maps in obj.items():
        #     recursive_iterate_dict(maps)
        #     for mapname, map in maps.items():
        json = json_dumps(
            obj,
            # cls=jsencoder,
            default = filter_object_dict, # lambda o: dict((key, value) for key, value in o.__dict__.items() if value),
            sort_keys=True,
            indent=4,
            allow_nan=False
        )
        if file:
            with open(file, 'w') as f: f.write(json)
        print("Saved", len(self.maps), "maps to", file)
        return json
    
    def __str__(self) -> str:
        return f"{len(self.maps)} maps from {len(self.get_maps_by_source())} sources"

    def get_maps_by_source(self):
        maps = {}
        for mapname, map in self.maps.items():
            if map.source not in maps:
                maps[map.source] = {}
            maps[map.source][mapname] = map
        return maps
    
    def get_maps_by_name(self, mapname: str) -> list['MapListMap']:
        return [map for map in self.maps.values() if map.mapname == mapname]
    
    def get_maps_by_title(self, title: str) -> list['MapListMap']:
        return [map for map in self.maps.values() if map.title == title]
    
    def get_mapnames(self):
        return list(self.maps.keys())
    
    def find_possible_alternatives(self, ignore_splits: list[str] = None) -> list[dict[str,str]]:
        alts: list[dict[str,str]] = []
        for mapname, map in self.maps.items():
            _alts = map.find_possible_alternatives(self, ignore_splits=ignore_splits)
            if _alts:
                _alts[mapname] = map.shortstr()
                alts.append(_alts)
        # sort all dicts by keys
        for alt in alts: alt = {k: alt[k] for k in sorted(alt)}
        alts = list({json_dumps(alt, sort_keys=True): alt for alt in alts}.values())
        return alts
    
    def copy_waypoints(self, wp_dir: Path) -> 'Maplist':
        for map in self.maps.values():
            map.copy_waypoints(wp_dir)
        return self
    
    def update(self) -> None:
        for map in self.maps.values():
            map.update()