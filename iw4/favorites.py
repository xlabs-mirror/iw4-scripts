
from sys import path as syspath
from os import getcwd
from pprint import pformat
from asyncio import get_event_loop
from logging import info, error, getLogger, basicConfig, DEBUG, INFO, ERROR
syspath.append(getcwd())

from iw4x.favorites import FavoritesFile

logger = getLogger()
logger.setLevel(DEBUG)
basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%d-%b-%y %H:%M:%S")

logger.debug((__file__,"START"))

async def main():
    # File path for the favourites.json file
    favourites_file = FavoritesFile("S:/Call of Duty/CoD 6 (MW2)/players/favourites.json")
    await favourites_file.update_async(timeout=.2)

    for favorite in favourites_file.favorites:
        if favorite.info:
            info(pformat(favorite.info))

    favourites_file.purge_duplicates()
    favourites_file.purge_unreachable()
    favourites_file.save()

if __name__ ==  '__main__':
    loop = get_event_loop()
    loop.run_until_complete(main())

input("Press enter to exit...")
logger.debug((__file__,"END"))