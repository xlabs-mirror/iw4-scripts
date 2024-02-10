
from sys import path as syspath
from os import getcwd
from pprint import pformat
from asyncio import get_event_loop
from logging import info, error, getLogger, basicConfig, DEBUG, INFO, ERROR

from iw4x.server import ServerInfoResponse
syspath.append(getcwd())

from iw4x.favorites import FavoritesFile, Favorite
from iw4x.iw4x_server import Server
from favorites2 import fetch_server_data

logger = getLogger()
logger.setLevel(DEBUG)
basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%d-%b-%y %H:%M:%S")

logger.debug((__file__,"START"))

async def main():
    # File path for the favourites.json file
    favourites_file = FavoritesFile("G:/Steam/steamapps/common/Call of Duty Modern Warfare 2/players/favourites.json") # "S:/Call of Duty/CoD 6 (MW2)/players/favourites.json"
    await favourites_file.update_async(timeout=.2)

    online_servers = fetch_server_data()

    for server in online_servers.servers:
        if server in favourites_file.favorites:
            logger.debug(f"{server} is already in favourites")
            continue
        fav = Favorite(server.ip, server.port)
        logger.debug(f"Adding {server} as {fav}")
        favourites_file.favorites.append(fav) # ServerInfoResponse(True, server.hostname, None, list(), None)

    for favorite in favourites_file.favorites:
        if favorite.info:
            info(pformat(favorite.info))

    favourites_file.purge_duplicates()
    await favourites_file.purge_unreachable()
    favourites_file.save()

if __name__ ==  '__main__':
    loop = get_event_loop()
    loop.run_until_complete(main())

# input("Press enter to exit...")
logger.debug((__file__,"END"))