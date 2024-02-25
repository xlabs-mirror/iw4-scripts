from copy import copy
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from os import linesep
from .Waypoint import Waypoint, WaypointType, zeroVector, WaypointRow
from tabulate import tabulate
from typing import TYPE_CHECKING
if TYPE_CHECKING: from .WaypointFile import WaypointFile
from sys import setrecursionlimit
setrecursionlimit(5000)

from logging import getLogger
logger = getLogger(__name__)

class SortingMethod(Enum):
    NONE = auto()
    DISTANCE_TO_ZERO = auto()
    DISTANCE_TO_FIRST = auto()
    DISTANCE_TO_LAST = auto()

# @dataclass
# class WaypointList:
#     waypoints: list[Waypoint]
#     def __init__(self, waypoints: list[Waypoint]):
#         self.waypoints = waypoints


@dataclass  
class WaypointFile:
    path: Path
    _rows: list[str] = field(default_factory=list)
    waypoints: list[Waypoint] = field(default_factory=list)
    _count: int = None

    def __init__(self, path: Path, ask_for_user_input:bool=False, is_cut_file:bool=False):
        if (not path is type(Path)): path = Path(path)
        self.path = path
        self.load(ask_for_user_input=ask_for_user_input, is_cut_file=is_cut_file)

    def purge_unlinked(self):
        removed = 0
        for waypoint in self.waypoints:
            if len(waypoint.connections) < 1:
                self.waypoints.remove(waypoint)
                removed += 1
        logger.info(f"Purged {removed} unlinked waypoints!") #  from {self.path.name}

    def check_count(self, fix=False, ask_for_user_input=False) -> int:
        errors = 0
        wp_count = len(self.waypoints)
        if self._count != wp_count:
            errors += 1
            logger.error(f"Waypoint count {wp_count} does not match declared count {self._count}")
            if fix: self._count = wp_count
        wp_row_count = len(self._rows)
        if self._count != wp_row_count:
            errors += 1
            logger.error(f"Waypoint row count {wp_row_count} does not match declared count {self._count}")
            if fix: self._count = wp_count
        if wp_row_count != wp_count:
            errors += 1
            logger.error(f"Waypoint row count {wp_row_count} does not match waypoint count {wp_count}")
            if fix: self._count = wp_count
        if ask_for_user_input:
            input(f"Found {errors} errors. Press enter to continue...")
        return errors

    def check(self, fix=False, ask_for_user_input=False, keep_connections=-1) -> int:
        errors = self.check_count(fix=fix, ask_for_user_input=ask_for_user_input)
        new_waypoints = []
        for waypoint in self.waypoints:
            # logger.debug(f"Checking {waypoint.shortstr()} ({waypoint})")
            new_waypoint = copy(waypoint)
            # errors += waypoint.check(fix=fix, ask_for_user_input=ask_for_user_input)
            for i, connection in enumerate(waypoint.connections):
                con_index = connection._index
                if con_index > len(self.waypoints):
                    errors += 1; logger.error(f"{waypoint.shortstr()} connection {connection} is over {len(self.waypoints)}")
                    if fix: new_waypoint.connections.remove(connection)
                elif con_index < 0:
                    errors += 1; logger.error(f"{waypoint.shortstr()} connection {connection} is under zero")
                    if fix: new_waypoint.connections.remove(connection)
                if connection == waypoint:
                    errors += 1; logger.error(f"{waypoint.shortstr()} connection {connection} is itself")
                    if fix: new_waypoint.connections.remove(connection)
            if waypoint.position == zeroVector:
                errors += 1; logger.error(f"{waypoint.shortstr()} position is zero")
                if fix: continue
            if waypoint.type is None:
                errors += 1; logger.error(f"{waypoint.shortstr()} has no type")
                if fix: continue
            if waypoint.type in [WaypointType.JUMP, WaypointType.MANTLE]:
                logger.warn(f"{waypoint.shortstr()} has weird type {waypoint.type.name}")
                # if fix: continue
            if not isinstance(waypoint.type, WaypointType) or waypoint.type not in WaypointType.__members__.values():
                logger.warn(f"{waypoint.shortstr()} has non-existant type {waypoint.type.name}")
                # if fix: continue
            if len(waypoint.connections) < 1:
                errors += 1; logger.error(f"{waypoint.shortstr()} has no connections")
                if fix: continue
            elif keep_connections > -1:
                new_waypoint.connections = waypoint.connections[:keep_connections]
            if new_waypoint: new_waypoints.append(new_waypoint)
        logger.debug("1")
        self.waypoints = new_waypoints
        logger.debug("2")
        if ask_for_user_input:
            input(f"{'Fixed'if fix else 'Found'} {errors} errors. Press enter to continue...")
        logger.debug("3")
        return errors

    def merge_from(self, other:'WaypointFile'):
        for waypoint in other.waypoints:
            if waypoint not in self.waypoints:
                self.waypoints.append(waypoint)

    def load(self, ask_for_user_input:bool=False, is_cut_file=False) -> 'WaypointFile':
        self._rows = []
        self.waypoints = []
        with self.path.open(newline='') as csvfile:
            rows = csvfile.readlines() # reader(csvfile, skipinitialspace=True, delimiter=' ', quotechar='|')
            headers: list[str] = []
            for i, row in enumerate(rows):
                row = row.strip()
                if not "," in row:
                    headers.append(row)
                    continue
                if row.startswith('#'):
                    logger.info("Skipping comment:", row)
                    continue
                parts = row.split(',')
                if len(parts) > 6 or len(parts) < 6:
                    logger.info(row)
                    raise Exception(f"[{i}] Invalid row length: {len(parts)}")
                row = [r.strip() for r in parts]
                self._rows.append(row)
                # logger.debug(f"Loaded row {i}: {row}")
                self.waypoints.append(Waypoint.from_row(i, row, self))
            if (len(headers) > 0 and headers[0].isdigit()):
                self._count = int(headers[0])
        offset = 0
        if is_cut_file:
            offset = -abs(self._count - len(self.waypoints))
            logger.info("Cut file detected, setting offset to ", offset)
        skip_all = False

        for waypoint in self.waypoints:
            if ask_for_user_input: logger.info(waypoint)
            connections = copy(waypoint.connections)
            waypoint.connections = []
            skip_all_for_wp = False
            for connection in connections:
                connection += offset + 1 # +1 because of zero index
                # if connection == 0: connection = 1
                if connection > len(self.waypoints):
                    logger.error(f"{waypoint.shortstr()} Connection {connection} is over {len(self.waypoints)}!")
                    if ask_for_user_input and not skip_all and not skip_all_for_wp:
                        a = input("Skip? (a)ll/(w)aypoint/(c)onnection: ").lower()
                        if a == 'a': skip_all = True
                        elif a == 'w': skip_all_for_wp = True
                    continue
                if connection < 0:
                    logger.error(f"Waypoint {waypoint.shortstr()} Connection {connection} is under zero!")
                    if ask_for_user_input and not skip_all and not skip_all_for_wp:
                        a = input("Skip? (a)ll/(w)aypoint/(c)onnection: ").lower()
                        if a == 'a': skip_all = True
                        elif a == 'w': skip_all_for_wp = True
                        continue
                target = self.waypoints[connection-1]
                if target == waypoint:
                    logger.error(f"Waypoint {waypoint.shortstr()} Connection {connection} target is itself!")
                    if ask_for_user_input and not skip_all and not skip_all_for_wp:
                        a = input("Skip? (a)ll/(w)aypoint/(c)onnection: ").lower()
                        if a == 'a': skip_all = True
                        elif a == 'w': skip_all_for_wp = True
                        continue
                waypoint.connections.append(target)
            # logger.info(f"Converted {len(connections)} connections for {waypoint.uuid}")
            skip_all_for_wp = False
        logger.debug(f"Loaded {len(self.waypoints)} ({self._count}) waypoints from {self.path}")
        return self

    def to_waypointrows(self) -> list['WaypointRow']:
        ret = []
        if not isinstance(self.waypoints, list): raise Exception("self.waypoints is not a list")
        logger.debug(f"to_waypointrows: {len(self.waypoints)}")
        for i, waypoint in enumerate(self.waypoints):
            if not isinstance(waypoint, Waypoint): raise Exception(f"Waypoint {waypoint} is not a Waypoint")
            logger.debug(f"test wp={waypoint._index}")
            new_connections = []
            if not isinstance(waypoint.connections, list): raise Exception(f"Waypoint {waypoint.shortstr()} connections is not a list")
            for connection in waypoint.connections:
                if not isinstance(connection, Waypoint): raise Exception(f"Connection {connection} is not a Waypoint")
                logger.debug(f"test conn={connection._index}")
                (con_wp_index, con_wp) = self.get_index(connection.hashstr(connections=False))
                logger.debug(f"found matching connwp3")
                if con_wp:
                    logger.debug(f"found conn index={con_wp_index}")
                    new_connections.append(con_wp_index)
                else:
                    logger.warn(f"Waypoint {waypoint.shortstr()} connection {connection} is not in this file")
            ret.append(WaypointRow(waypoint, new_connections))
        return ret

    def to_strlist(self) -> list[list[str]]:
        return [wp.to_str() for wp in self.to_waypointrows()]

    def to_rows(self) -> list[str]:
        logger.debug("to_rows")
        ret = []
        for wp in self.to_waypointrows():
            ret.append(wp.to_row(connections=True))
        return ret

    def get_index(self, hash: str) -> tuple[int, 'Waypoint']:
        ret: dict[int, 'Waypoint'] = {}
        for i, waypoint in enumerate(self.waypoints):
            hashstr = waypoint.hashstr(connections=False)
            # logger.debug(f"Comparing {hashstr} to {hash}")
            if hashstr == hash: ret[i] = waypoint
        _cnt = len(ret)
        if _cnt < 1 or _cnt > 1:
            _msg = f"Waypoint with hash {hash} has {_cnt} indexes in self.waypoints!"
            logger.error(_msg)
            # raise Exception(_msg)
            for waypoint in self.waypoints:
                logger.debug(';'.join([str(waypoint._index),waypoint.to_row(True)]))
        return next(iter((ret.items())))

    def save(self, path:Path=None, sort:SortingMethod=SortingMethod.NONE, tabs:bool=False):
        if path is None: path = self.path
        if (not path is type(Path)): path = Path(path)
        waypoints = self.waypoints
        if sort is not SortingMethod.NONE:
            logger.info("Sorting",len(waypoints),"waypoints by",sort.name)
            match sort:
                case SortingMethod.DISTANCE_TO_ZERO:
                    waypoints.sort(key=lambda x: x.distance_to_zero())
                case SortingMethod.DISTANCE_TO_FIRST:
                    waypoints.sort(key=lambda x: x.distance_to(waypoints[0]))
                case SortingMethod.DISTANCE_TO_LAST:
                    waypoints.sort(key=lambda x: x.distance_to(waypoints[-1]))
        if tabs: txt = tabulate(self.to_strlist(), "", "plain").replace("\r","").strip()
        else: txt = "\n".join(self.to_rows())
        with path.open('w', newline='') as csvfile:
            csvfile.writelines([str(len(waypoints)), txt, ""])
        logger.info(f"Wrote {len(waypoints)} waypoints to {path}")