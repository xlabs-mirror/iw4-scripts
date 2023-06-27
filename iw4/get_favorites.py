
from sys import path as syspath
from os import getcwd
syspath.append(getcwd())

from pathlib import Path
from json import load, dump
from .iw4x import *
import requests

# File path for the favourites.json file
favourites_file = Path("S:/Call of Duty/CoD 6 (MW2)/players/favourites.json")

game_name = "iw4"
servers_url = "http://minopia.de/iw4/servers/index.php?format=json"
# servers_url = f"http://192.168.2.38/iw4/servers/index.json"
print(f"Requesting server list from {servers_url}")
response = requests.get(servers_url, timeout=1)
print(f"Got response from server: {response.text[:100]}")
server_data = response.json()
servers = []
print(f"Got {len(server_data)} games from {servers_url}")
print(f"Got {len(server_data[game_name])} games in {game_name}")
for server in server_data["iw4"]:
    ip = server["ip"]
    port = server["port"] if "port" in server else "28960"
    if ip and port:
        server_address = f"{ip}:{port}"
        if server_address not in servers:
            servers.append(server_address)
            print(f"Added {server_address} to favorites")
        else:
            print(f"{server_address} already exists in favorites")
with open(favourites_file, "r") as file:
    favourites = load(file)
print(f"Loaded {len(favourites)} favorites from {favourites_file}")
merged_favourites = favourites + servers
merged_favourites = list(set(merged_favourites))
backup_file = favourites_file.with_stem("favorites.bak")
favourites_file.rename(backup_file)
print(f"Created backup at {backup_file}")
with open(favourites_file, "w") as file:
    dump(merged_favourites, file, indent=4)
print(f"Wrote {len(merged_favourites)} favorites to {favourites_file}")
