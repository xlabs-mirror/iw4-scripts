from pprint import pprint
from typing import List
from typing import Any
from dataclasses import dataclass
from requests import get
from logging import info, error
from json import dump, dumps

from .player import Player

@dataclass
class Host:
    admin: str = ""
    email: str = ""
    location: str = ""
    website: str = ""

    def toJSON(self):
        return dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

    @staticmethod
    def from_dict(obj: Any) -> 'Host':
        if obj is None: return Host()
        _admin = obj.get("admin", None)
        _email = obj.get("email", None)
        _location = obj.get("location", None)
        _website = obj.get("website", None)
        return Host(_admin, _email, _location, _website)

@dataclass
class MapRotation:
    gametypes: list[str] = None
    maps: list[str] = None

    def toJSON(self):
        return dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

    @staticmethod
    def from_dict(obj: Any) -> 'MapRotation':
        if obj is None: return MapRotation([], [])
        _gametypes = obj.get("gametypes", [])
        _maps = obj.get("maps", [])
        return MapRotation(_gametypes, _maps)

@dataclass
class Status:
    sv_hostname: str
    matchtype: int
    g_gametype: str
    mapname: str
    aimAssist: bool
    g_hardcore: bool
    isPrivate: bool
    scr_game_allowkillcam: bool
    scr_team_fftype: int
    sv_allowAnonymous: bool
    sv_allowClientConsole: bool
    sv_floodProtect: bool
    sv_minPing: int
    sv_maxPing: int
    sv_maxRate: int
    sv_maxclients: int
    sv_privateClients: int
    sv_privateClientsForClients: int
    sv_pure: bool
    sv_securityLevel: int
    voiceChat: bool
    protocol: int
    shortversion: str
    version: str
    gamename: str
    checksum: str

    def toJSON(self):
        return dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

    @staticmethod
    def from_dict(obj: Any) -> 'Status':
        _sv_hostname = obj.get("sv_hostname")
        _matchtype = int(obj.get("matchtype")) if obj.get("matchtype") else None
        _g_gametype = obj.get("g_gametype")
        _mapname = obj.get("mapname")
        _aimAssist = bool(obj.get("aimAssist"))
        _g_hardcore = bool(obj.get("g_hardcore"))
        _isPrivate = bool(obj.get("isPrivate"))
        _scr_game_allowkillcam = bool(obj.get("scr_game_allowkillcam"))
        _scr_team_fftype = int(obj.get("scr_team_fftype")) if obj.get("scr_team_fftype") else None
        _sv_allowAnonymous = bool(obj.get("sv_allowAnonymous"))
        _sv_allowClientConsole = bool(obj.get("sv_allowClientConsole"))
        _sv_floodProtect = bool(obj.get("sv_floodProtect"))
        _sv_minPing = int(obj.get("sv_minPing")) if obj.get("sv_minPing") else None
        _sv_maxPing = int(obj.get("sv_maxPing")) if obj.get("sv_maxPing") else None
        _sv_maxRate = int(obj.get("sv_maxRate")) if obj.get("sv_maxRate") else None
        _sv_maxclients = int(obj.get("sv_maxclients")) if obj.get("sv_maxclients") else None
        _sv_privateClients = int(obj.get("sv_privateClients")) if obj.get("sv_privateClients") else None
        _sv_privateClientsForClients = int(obj.get("sv_privateClientsForClients")) if obj.get("sv_privateClientsForClients") else None
        _sv_pure = bool(obj.get("sv_pure"))
        _sv_securityLevel = int(obj.get("sv_securityLevel")) if obj.get("sv_securityLevel") else None
        _voiceChat = bool(obj.get("voiceChat"))
        _protocol = int(obj.get("protocol")) if obj.get("protocol") else None
        _shortversion = obj.get("shortversion")
        _version = obj.get("version")
        _gamename = obj.get("gamename")
        _checksum = obj.get("checksum")
        return Status(_sv_hostname, _matchtype, _g_gametype, _mapname, _aimAssist, _g_hardcore, _isPrivate, _scr_game_allowkillcam, _scr_team_fftype, _sv_allowAnonymous, _sv_allowClientConsole, _sv_floodProtect, _sv_minPing, _sv_maxPing, _sv_maxRate, _sv_maxclients, _sv_privateClients, _sv_privateClientsForClients, _sv_pure, _sv_securityLevel, _voiceChat, _protocol, _shortversion, _version, _gamename, _checksum)

@dataclass
class ServerInfoResponse:
    dedicated: bool
    host: Host
    map_rotation: MapRotation
    players: List[Player]
    status: Status

    def to_json(self):
        return dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
        
    def to_file(self, path: str) -> None:
        try: 
            with open(path, "w") as f:
                f.write(self.to_json())
        except Exception as ex: error(f"Failed to write to file: {ex}")

    @staticmethod
    def from_dict(obj: Any) -> 'ServerInfoResponse':
        if not isinstance(obj, dict): return None
        _dedicated = bool(obj.get("dedicated"))
        _host = Host.from_dict(obj.get("host"))
        _map_rotation = MapRotation.from_dict(obj.get("map_rotation"))
        _players = [Player.from_dict(y) for y in obj.get("players")]
        _status = Status.from_dict(obj.get("status"))
        return ServerInfoResponse(_dedicated, _host, _map_rotation, _players, _status)
    
    @staticmethod
    def from_url(url: str, timeout = 1) -> 'ServerInfoResponse':
        info(f"[{url}] Fetching server info ...")
        try: response = get(url, timeout=timeout)
        except Exception as ex:
            error(f"[{url}] Failed to get response : {ex}")
            return None
        info(f"Response: {response.status_code}")
        try: parsed_response = response.json()
        except Exception as ex:
            error(f"[{url}] Failed to parse response as json: {ex}")
            return None
        return ServerInfoResponse.from_dict(parsed_response)
    
    @staticmethod
    def from_file(path: str) -> 'ServerInfoResponse':
        with open(path, "r") as f:
            return ServerInfoResponse.from_dict(f.read())
    
    @staticmethod
    def from_ip(address: str, port: int = 28960, timeout = 1) -> 'ServerInfoResponse':
        return ServerInfoResponse.from_url(f"http://{address}:{port}/info", timeout=timeout)