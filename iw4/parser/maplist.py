from dataclasses import dataclass
from json import dumps, load

from .map import Map

def remove_none_values(dictionary:dict):
    forbbiden_values = [None, "None", "", [], "null"]
    for key, value in list(dictionary.items()):
        if value in forbbiden_values:
            del dictionary[key]
        elif isinstance(value, dict):
            remove_none_values(value)
    return dictionary

@dataclass
class Maplist:
    game: str
    maps: dict[str,'Map']

    def get_maps_by_source(self):
        maps = {}
        for mapname, map in self.maps.items():
            if map.source not in maps:
                maps[map.source] = {}
            maps[map.source][mapname] = map
        return maps

    @staticmethod
    def from_dict(obj: dict) -> 'Maplist':
        maps = {}
        for game, _maps in obj.items():
            for mapname, map in _maps.items():
                maps[mapname] = Map.from_dict(map)
        sources = {map.source for map in maps.values()}
        print("Loaded", len(maps), "maps from", len(sources), "sources")
        return Maplist(game, maps)
    
    @staticmethod
    def load(file: str = 'maps.json'):
        with open(file, 'r', encoding="utf-8") as f:
            jsonstring = load(f)
            return Maplist.from_dict(jsonstring)
    
    def save(self, file: str = 'maps.json'):
        cleaned_maps = remove_none_values({self.game: cleaned_maps})
        json = dumps(cleaned_maps, default=lambda o: o.__dict__, sort_keys=True, indent=4) # , object_hook=remove_nulls
        if file:
            with open(file, 'w') as f: f.write(json)
        print("Saved ", len(self.maps), "maps to", file)
        return json