from pathlib import Path
from pprint import pprint
from sys import path as syspath
from os import getcwd
syspath.append(getcwd())
from waypoints.WaypointFile import WaypointFile, SortingMethod
from waypoints.Waypoint import zeroVector, WaypointType

from logging import getLogger, StreamHandler, FileHandler, Formatter, DEBUG, INFO
logger = getLogger()
logger.setLevel(DEBUG)
formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = StreamHandler()
ch.setLevel(INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)
fh = FileHandler('waypoints.log')
fh.setLevel(DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)

fix = True
ask_input = False
wp_dir = Path(r"P:\Python\iw4\iw4-resources\waypoints")

errs = 0
files = 0
wps = 0
for file in wp_dir.glob("*.csv"):
    # if not str(file).endswith("so_chopper_invasion_wp.csv"):
    #     continue
    print(file)
    files += 1
    file = WaypointFile(file, ask_for_user_input=ask_input)
    wps += len(file.waypoints)
    # for waypoint in file.waypoints:
    #     if waypoint.type == WaypointType.JAVELIN:
        # if waypoint.target is not None and waypoint.target == zeroVector:
            # print(waypoint)

    err = file.check(fix=fix, ask_for_user_input=ask_input)
    errs += err
    if err > 0:
        logger.debug("err > 0")
        file.save(file.path.with_suffix(".fixed"), sort=SortingMethod.NONE)

print(f"Checked {files} files with {wps} waypoints, {'fixed'if fix else'found'} {errs} errors")
    

# file = WaypointFile(r"G:\Steam\steamapps\common\Call of Duty Modern Warfare 2\userraw\scriptdata\waypoints\mp_plaza2_wp__.csv", ask_for_user_input=ask_input)
# for waypoint in file.waypoints:
#     print(waypoint)
#     waypoint.position.z += 500
# file.save(r"G:\Steam\steamapps\common\Call of Duty Modern Warfare 2\userraw\scriptdata\waypoints\mp_plaza2_wp.csv")
# pass # input("Press enter to exit...")
# err = file.check(fix=True, ask_for_user_input=ask_input)
# file2 = WaypointFile(r"S:\Call of Duty\CoD 6 (MW2)\userraw\scriptdata\waypoints\co_hunted_ext.csv", ask_for_user_input=ask_input, is_cut_file=True)
# err = file2.check(fix=True, ask_for_user_input=ask_input)
# # file2.waypoints = file2.waypoints[1:]
# # err = file2.check(fix=True, ask_for_user_input=ask_input)


# file.save(r"S:\Call of Duty\CoD 6 (MW2)\userraw\scriptdata\waypoints\co_hunted_wp_fixed.csv", sort=SortingMethod.NONE)
# file.merge_from(file2)
# file.check(fix=True, ask_for_user_input=ask_input)
# for waypoint in file.waypoints:
#     print(waypoint)

# file2.save(r"S:\Call of Duty\CoD 6 (MW2)\userraw\scriptdata\waypoints\co_hunted_wp_ext_fixed.csv", sort=SortingMethod.NONE)
# file.save(r"S:\Call of Duty\CoD 6 (MW2)\userraw\scriptdata\waypoints\co_hunted_wp_merged.csv", sort=SortingMethod.NONE)