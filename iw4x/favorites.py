
from concurrent.futures import ThreadPoolExecutor
from time import time
from typing import Any
from pathlib import Path
from dataclasses import dataclass
import logging
from json import dumps, load
from asyncio import sleep as asleep
from asyncio import gather, create_task, run
from socket import gethostbyname, getaddrinfo, AF_INET6, AF_INET
from ipaddress import IPv4Address, IPv6Address

from .server import ServerInfoResponse

try:
    from dns import resolver
    dns = resolver.Resolver()
    dns.nameservers = ['8.8.8.8']
except: pass

cache_dir = Path("cache/servers/")

def to_str(ip: str, port: int): return f"{ip}:{port}"

@dataclass
class Favorite:
    address: str
    port: int
    info: ServerInfoResponse
    ipv4: IPv4Address = None
    ipv6: IPv6Address = None

    def __init__(self, address: str, port: int, info: ServerInfoResponse = None):
        self.address = address
        self.update_ips()
        self.port = port
        self.info = info
        # else: info(f"[{to_str(ip,port)}] Favorite needs updating...")

    def update_ips(self):
        try: self.ipv4 = IPv4Address(self.address)
        except Exception as ex:
            # print(f"[{self.address}] Failed to parse ipv4 address: {ex}")
            try: self.ipv4 = IPv4Address(gethostbyname(self.address))
            except Exception as ex:
                # print(f"[{self.address}] Failed to resolve ipv4 address: {ex}")
                try: self.ipv4 = IPv4Address(getaddrinfo(self.address, None, AF_INET))
                except Exception as ex:
                    # print(f"[{self.address}] Failed to resolve ipv4 address: {ex}")
                    try: self.ipv4 = IPv4Address(dns.query(self.address,'A')[0].address)
                    except Exception as ex: pass # print(f"[{self.address}] Failed to resolve ipv4 address: {ex}")
        try: self.ipv6 = IPv6Address(self.address)
        except Exception as ex:
            # print(f"[{self.address}] Failed to parse ipv6 address: {ex}")
            try: self.ipv6 = IPv6Address(getaddrinfo(self.address, None, AF_INET6))
            except Exception as ex:
                # print(f"[{self.address}] Failed to resolve ipv6 address: {ex}")
                try: self.ipv6 = IPv6Address(dns.query(self.address,'AAAA')[0].address)
                except Exception as ex: pass # print(f"[{self.address}] Failed to resolve ipv6 address: {ex}")

    async def async_update_info(self, timeout: int = 1):
        # Perform long-running or blocking operations here using await
        self.info = await self.async_get_server_info(timeout=timeout)
        return self.info

    async def async_get_server_info(self, timeout: int = 1):
        # await asleep(1)
        return ServerInfoResponse.from_ip(self.ipv4, self.port, timeout=timeout)

    async def update(self, timeout: int = 1):
        cache_file = cache_dir / f"{self.address}_{self.port}.json"
        if cache_file.exists():
            cache_file_time = cache_file.stat().st_mtime
            if cache_file_time > time() - 86400:
                logging.debug(f"[{self.to_str()}] Loading from cache...")
                self.info = ServerInfoResponse.from_file(cache_file)
                if self.info: return self.info
            else: logging.warn(f"[{self.to_str()}] Cache file is older than a day, updating...")
        self.info = await self.async_update_info(timeout=timeout)
        if not self.info: logging.error(f"[{self.to_str()}] Failed to get server info")
        else :
            logging.info(f"[{self.to_str()}] Updated server info")
            self.info.to_file(cache_file)
        return self.info

    async def is_valid(self):
        if self.ipv4 is None and self.ipv6 is None: self.update_ips()
        if self.ipv4 is None and self.ipv6 is None: return False
        if self.info is None: await self.update()
        return self.info is not None

    def to_str(self): return to_str(self.address, self.port)

    def to_json(self):
        return dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

    @staticmethod
    def from_str(input: str):
        ip, port = input.split(":")
        return Favorite(ip, int(port))

@dataclass
class FavoritesFile:
    path: Path = "favourites.json"
    favorites: list[Favorite] = None

    def __init__(self, path: Path):
        if isinstance(path, str): self.path = Path(path)
        self.path = path
        self.favorites = self.load()

    def update(self):
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(favorite.update) for favorite in self.favorites]
            for future in futures:
                future.result()
        logging.info(f"Initiated update for {len(self.favorites)} favorites")
        return self.favorites

    async def update_async(self, timeout= 1):
        tasks = []
        for favorite in self.favorites:
            task = create_task(favorite.update(timeout=timeout))
            tasks.append(task)
        
        await gather(*tasks)
        
        logging.info(f"Initiated update for {len(self.favorites)} favorites")
        return self.favorites

    def get(self, item: str):
        ret = []
        for favorite in self.favorites:
            if favorite.to_str() == item:
                ret.append(favorite)
        return ret

    async def purge_unreachable(self):
        ret = []
        for favorite in self.favorites:
            if not await favorite.is_valid():
                ret.append(favorite)
                self.favorites.remove(favorite)
        logging.info(f"Removed {len(ret)} unreachable favorites")
        return ret

    def purge_duplicates(self, remove: bool = True):
        ret = []
        for favorite in self.favorites:
            instances = self.get(favorite.to_str())
            if len(instances) > 1:
                ret.append(favorite)
                if remove:
                    for instance in instances[1:]: self.favorites.remove(instance)
        logging.info(f'{"Removed" if remove else "Found"} {len(ret)} duplicate favorites')
        return ret

    def load(self, file: Path = None):
        if not file: file = self.path
        with open(file, "r") as f:
            items = []
            try: items = load(f)
            except Exception as ex:
                logging.error(f"Failed to load favorites from {file}: {ex}")
            self.favorites = [Favorite.from_str(item.strip()) for item in items]
            logging.info((f"Loaded {len(self.favorites)} favorites from {file}"))
            return self.favorites
        
    def save(self, file: Path = None, newline: bool = False):
        if not file: file = self.path
        favs = [fav.to_str() for fav in self.favorites]
        with open(file, "w") as f:
            if newline: f.write("\n".join(favs))
            else: f.write(dumps(favs, indent=4))
            logging.info((f"Saved {len(self.favorites)} favorites to {file}"))

    def toJSON(self):
        return dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)