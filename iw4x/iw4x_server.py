from typing import List
from typing import Any
from dataclasses import dataclass
import json

@dataclass
class Server:
    identifier: str
    ip: str
    port: int
    hostname: str
    protocol: int
    date: int

    def __init__(self, identifier: str, ip: str, port: int, hostname: str, protocol: int, date: int) -> None:
        self.identifier = identifier
        self.ip = ip
        self.port = port
        self.hostname = hostname
        self.protocol = protocol
        self.date = date

    def __str__(self) -> str:
        return f"[{self.protocol}] {self.hostname} ({self.ip}:{self.port})"

    @staticmethod
    def from_dict(obj: Any) -> 'Server':
        _identifier = obj.get("identifier")
        _ip = obj.get("ip")
        _port = int(obj.get("port"))
        _hostname = obj.get("hostname")
        _protocol = int(obj.get("protocol"))
        _date = int(obj.get("date"))
        return Server(_identifier, _ip, _port, _hostname, _protocol, _date)

@dataclass
class ServerList:
    servers: List[Server]

    def __init__(self, servers: List[Server]) -> None:
        self.servers = servers

    @staticmethod
    def from_dict(obj: Any) -> 'ServerList':
        _servers = [Server.from_dict(y) for y in obj.get("servers")]
        return ServerList(_servers)

# Example Usage
# jsonstring = json.loads(myjsonstring)
# root = Root.from_dict(jsonstring)
