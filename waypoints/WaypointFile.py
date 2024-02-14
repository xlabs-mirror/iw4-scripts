from copy import copy
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from os import linesep
from .Waypoint import Waypoint
from tabulate import tabulate
from typing import TYPE_CHECKING
if TYPE_CHECKING: from .WaypointFile import WaypointFile

class SortingMethod(Enum):
    NONE = auto()
    DISTANCE_TO_ZERO = auto()
    DISTANCE_TO_FIRST = auto()
    DISTANCE_TO_LAST = auto()

@dataclass
class WaypointList:
    waypoints: list[Waypoint]
    def __init__(self, waypoints: list[Waypoint]):
        self.waypoints = waypoints


@dataclass  
class WaypointFile:
    path: Path
    rows: list[str]
    waypoints: list[Waypoint]
    _count: int

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
        print(f"Purged {removed} unlinked waypoints!") #  from {self.path.name}

    def check(self, fix=False, ask_for_user_input=False, keep_connections=-1) -> int:
        errors = 0
        for waypoint in self.waypoints:
            for i, connection in enumerate(waypoint.connections):
                con_index = connection.index()
                if con_index > len(self.waypoints):
                    errors += 1; print(f"{waypoint} connection {connection} is over {len(self.waypoints)}")
                    if fix: waypoint.connections.remove(connection)
                elif con_index < 0:
                    errors += 1; print(f"{waypoint} connection {connection} is under zero")
                    if fix: waypoint.connections.remove(connection)
                if connection == waypoint:
                    errors += 1; print(f"{waypoint} connection {connection} is itself")
                    if fix: waypoint.connections.remove(connection)
            if len(waypoint.connections) < 1:
                errors += 1; print(f"{waypoint} has no connections")
            elif keep_connections > -1:
                waypoint.connections = waypoint.connections[:keep_connections]
        if ask_for_user_input:
            input(f"Found {errors} errors. Press enter to continue...")
        return errors

    def merge_from(self, other:'WaypointFile'):
        for waypoint in other.waypoints:
            if waypoint not in self.waypoints:
                self.waypoints.append(waypoint)

    def load(self, ask_for_user_input:bool=False, is_cut_file=False) -> 'WaypointFile':
        self.rows = []
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
                    print("Skipping comment:", row)
                    continue
                parts = row.split(',')
                if len(parts) > 6 or len(parts) < 6:
                    print(row)
                    raise Exception(f"[{i}] Invalid row length: {len(parts)}")
                row = [r.strip() for r in parts]
                self.rows.append(row)
                self.waypoints.append(Waypoint.from_row(i, row, self))
            if (len(headers) > 0 and headers[0].isdigit()):
                self._count = int(headers[0])
        offset = 0
        if is_cut_file:
            offset = -abs(self._count - len(self.waypoints))
            print("Cut file detected, setting offset to ", offset)
        skip_all = False
        for waypoint in self.waypoints:
            if ask_for_user_input: print(waypoint)
            connections = copy(waypoint.connections)
            waypoint.connections = []
            skip_all_for_wp = False
            for connection in connections:
                connection += offset + 1 # +1 because of zero index
                # if connection == 0: connection = 1
                if connection > len(self.waypoints):
                    print(f"WARNING: Waypoint {waypoint.uuid} Connection {connection} is over {len(self.waypoints)}!")
                    if ask_for_user_input and not skip_all and not skip_all_for_wp:
                        a = input("Skip? (a)ll/(w)aypoint/(c)onnection: ").lower()
                        if a == 'a': skip_all = True
                        elif a == 'w': skip_all_for_wp = True
                    continue
                if connection < 0:
                    print(f"WARNING: Waypoint {waypoint.uuid} Connection {connection} is under zero!")
                    if ask_for_user_input and not skip_all and not skip_all_for_wp:
                        a = input("Skip? (a)ll/(w)aypoint/(c)onnection: ").lower()
                        if a == 'a': skip_all = True
                        elif a == 'w': skip_all_for_wp = True
                        continue
                target = self.waypoints[connection-1]
                if target == waypoint:
                    print(f"WARNING: Waypoint {waypoint.uuid} Connection {connection} target is itself!")
                    if ask_for_user_input and not skip_all and not skip_all_for_wp:
                        a = input("Skip? (a)ll/(w)aypoint/(c)onnection: ").lower()
                        if a == 'a': skip_all = True
                        elif a == 'w': skip_all_for_wp = True
                        continue
                waypoint.connections.append(target)
            # print(f"Converted {len(connections)} connections for {waypoint.uuid}")
            skip_all_for_wp = False
        print(f"Loaded {len(self.waypoints)} ({self._count}) waypoints from {self.path}")
        return self

    def to_strlist(self) -> list[list[str]]:
        return [wp.to_str() for wp in self.waypoints]

    def to_rows(self) -> list[str]:
        return [wp.to_row() for wp in self.waypoints]

    def save(self, path:Path=None, sort:SortingMethod=SortingMethod.NONE, tabs:bool=False):
        if path is None: path = self.path
        if (not path is type(Path)): path = Path(path)
        waypoints = self.waypoints
        if sort is not SortingMethod.NONE:
            print("Sorting",len(waypoints),"waypoints by",sort.name)
            match sort:
                case SortingMethod.DISTANCE_TO_ZERO:
                    waypoints.sort(key=lambda x: x.distance_to_zero())
                case SortingMethod.DISTANCE_TO_FIRST:
                    waypoints.sort(key=lambda x: x.distance_to(waypoints[0]))
                case SortingMethod.DISTANCE_TO_LAST:
                    waypoints.sort(key=lambda x: x.distance_to(waypoints[-1]))
        with path.open('w', newline='') as csvfile:
            csvfile.write(f"{len(waypoints)}\n")
            if tabs:
                csvfile.write(tabulate(self.to_strlist(), "", "plain").replace("\r","").strip())
            else: csvfile.write("\n".join(self.to_rows()))
        print(f"Wrote {len(waypoints)} waypoints to {path}")