def splitList(list_a, chunk_size):
  for i in range(0, len(list_a), chunk_size):
    yield list_a[i:i + chunk_size]
from itertools import islice, chain
def splitDict(data, SIZE=15):
  it = iter(data)
  for _ in range(0, len(data), SIZE):
    yield {k:data[k] for k in islice(it, SIZE)}
def pprint(msg): print(f"\t{msg}")

from parser.maplist import Maplist, Map, Source
maplist = Maplist.load()

maps = maplist.maps
maps_per_page = 30


sources = maplist.get_maps_by_source() # list(splitDict(maps, maps_per_page))
sources_cnt = len(sources)
pi = 1
maps: dict[str, Map]
allpages = len(list(chain.from_iterable([list(splitDict(maps, maps_per_page)) for maps in sources.values()])))
for source, maps in sources.items():
  # CHOICE_BUTTON_FOCUS(0, "dlc_list_1", "@MP_ORIGINAL_MAPS", setdvar "iw4x_maps_dlc" 0;, LOCAL_MAP_FOCUS( "MP_ORIGINAL_MAPS", "NULL_EMPTY", "loadscreen_mp_bonusmaps" ), ;)
  print(f"#pragma region SOURCE {source} WITH {len(maps)} MAPS")
  pages = list(splitDict(maps, maps_per_page))
  pages_cnt = len(pages)
  for page in pages:
      pprint(f"// PAGE {pi} OF {pages_cnt} WITH {len(page)} MAPS")
      # pprint(f'MENU_MAP_BUTTON({pi}, {0}, "{source}", "", "")')
      i = 1
      map: Map
      for mapname, map in page.items():
          # print("// MAP", mapname)
          even = (i % 2) == 0
          name = f'{"^9" if even else ""}{map.name.get("english")}'
          # pprint(f'MENU_MAP_BUTTON({pi}, {i}, "{name}", "{map.description.get("english")}", exec "rcon map {mapname}")')
          # LOCAL_MAP_SELECTION(0, 	"mp_afghan", 			"MPUI_AFGHAN", 			"MPUI_DESC_MAP_AFGHAN", 		"preview_mp_afghan",			dvarint("iw4x_maps_dlc") == 0)
          pprint(f'LOCAL_MAP_SELECTION({i-1},\t"{mapname}", \t\t\t"{name}",\t\t\t\t\t"{map.description.get("english")}",\t\t\t\t\t\t"{map.preview.name}",\t\t\t\tdvarint("iw4x_maps_dlc") == 6)')
          # print(f'MENU_CHOICE_BUTTON_VIS({i}, "button_{i+1}", "{name}", exec "rcon map {map}"; close self;, ;, 1)')
          # print(f'MENU_CHOICE_NEWICON_RAW({i}, "preview_{map}", 1)')
          # print(f'MENU_CHOICE_BUTTON_VIS({i}, ;, "{map}",setdvar ui_mapname {map};exec "rcon map {map}";close self;, 1, preview_{map}, {map}, {map})')
          i+=1
      # print("pi", pi, "allpages", allpages)
      if pi < allpages:pprint(f'MENU_CHOICE_BUTTON_VIS({maps_per_page + 1}, ;, "Next", setLocalVarInt ui_page {pi+1};, ;, when( localVarInt( ui_page ) == {pi}))')
      if pi > 1:pprint(f'MENU_CHOICE_BUTTON_VIS({maps_per_page + 2}, ;, "Previous", setLocalVarInt ui_page {pi-1};, ;, when( localVarInt( ui_page ) == {pi}))')
      # pprint(f"#pragma endregion")
      pi+=1
  print(f"#pragma endregion")

print("")
pprint(f'MENU_CHOICE_BUTTON({maps_per_page + 3}, ;, "Back", close "self";, ;)')