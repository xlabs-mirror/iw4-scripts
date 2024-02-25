from dataclasses import dataclass
from enum import Enum
from pygame import Vector3
from hashlib import md5
from json import dumps
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .Waypoint import Waypoint
    from .WaypointFile import WaypointFile

from logging import getLogger
logger = getLogger(__name__)

zeroVector = Vector3(0, 0, 0)

def vectorStr(v: Vector3):
    if v is None: return ""
    return f"{v.x} {v.y} {v.z}"

class WaypointType(Enum):
    CROUCH = "crouch" # bw default
    STAND = "stand"
    PRONE = "prone"
    CLIMB = "climb"
    CLAYMORE = "claymore"
    GRENADE = "grenade"
    JAVELIN = "javelin"
    JUMP = "jump" # todo: check if exists
    MANTLE = "mantle" # todo: check if exists
DefaultWaypointType = WaypointType.STAND # my default because duh

@dataclass
class Waypoint:
    _index: int
    file: 'WaypointFile'
    position: Vector3
    type: WaypointType
    angle: Vector3
    target: Vector3
    connections: list['Waypoint']
    def __init__(self, _index:int, position:Vector3, connections:list['Waypoint'], type:WaypointType, angle:Vector3, target:Vector3, file:'WaypointFile'):
        self._index = _index
        self.position = position
        self.connections = connections
        self.connections.sort()
        self.type = type
        self.angle = angle
        self.target = target
        self.file = file

    def __lt__(self, other:'Waypoint'):
        return self.distance_to_first() < other.distance_to_first()
    def __gt__(self, other:'Waypoint'):
        return self.distance_to_first() > other.distance_to_first()
    def __compare__(self, other:'Waypoint') -> bool:
        return self.to_row(connections=False) == other.to_row(connections=False)
    def __hash__(self) -> int:
        return hash(self.hashstr())
    # def shorthash(self) -> str: return self.hashstr()[:8]
    def hashstr(self, connections: bool = False) -> str: return self.to_row(connections=connections) # md5(self.to_row(connections).encode('utf-8')).hexdigest()
    def __str__(self) -> str:
        return f"WP|{self.position}|{self.connections_str()}|{self.type.name}|{self.angle}|{self.target}"
    def shortstr(self) -> str:
        return f"[{self.file.path.name}|{self._index}/{len(self.file.waypoints)}]"
    def connections_str(self) -> str:
        if self.connections is None: raise Exception(f"self.connections is None: {self.connections}")
        if not isinstance(self.connections, list): raise Exception(f"self.connections is not a list: {self.connections}")
        if len(self.connections) and isinstance(self.connections[0], Waypoint):
            return ' '.join([str(c._index) for c in self.connections]) # todo: dont use index pls
        return ' '.join([str(c) for c in self.connections])
    def to_list(self, connections: bool = False):
        return [vectorStr(self.position), self.connections_str() if connections else "", self.type.value, vectorStr(self.angle), vectorStr(self.target), ""]
    def to_row(self, connections = False) -> str:
        return (",".join(self.to_list(connections=connections))).strip()
    def to_str(self) -> str:
        return [f+"," for f in self.to_list()[:-1]]
    
    def distance_to_zero(self) -> float: return self.position.distance_to(zeroVector)
    def distance_to_first(self) -> float: return self.distance_to(self.file.waypoints[0])
    def distance_to_last(self) -> float: return self.distance_to(self.file.waypoints[-1])
    def distance_to(self, other:'Waypoint') -> float: return self.position.distance_to(other.position)

    def check(self, fix: bool = False, ask_for_user_input: bool = False) -> int:
        if fix: raise Exception("Fix not implemented")
        errors = 0
        # if self.index() != self._index:
        #     errors += 1
        #     logger.info(f"Waypoint index {self.index()} does not match declared index {self._index}")
        if self.position == zeroVector:
            errors += 1
            logger.info(f"Waypoint {self.shortstr()} position {self.position} is zero")
        if len(self.connections) < 1:
            errors += 1
            logger.info(f"Waypoint {self.shortstr()} has no connections")
        if not isinstance(self.type, WaypointType) or self.type not in WaypointType.__members__.values():
            errors += 1
            logger.info(f"Waypoint {self.shortstr()} has potentially non-existant type {self.type}")
        if self.type is None:
            errors += 1
            logger.info(f"Waypoint {self.shortstr()} has no type")
        return errors

    @staticmethod
    def from_row(row_index:int, row:list[str], file:'WaypointFile'):
        wp_index = row_index - 1
        pos = Vector3([float(p) for p in row[0].split(' ')]) if row[0] else None
        angle = Vector3([float(p) for p in row[3].split(' ')]) if row[3] else None
        connections = []
        try: connections = [int(c) for c in row[1].split(' ')] # if row[1] else []
        except Exception as ex:
            msg = f"Invalid waypoint connections: {row[1]} in row {row_index} (wp: {wp_index}) of {file.path.name}"
            logger.error(msg)
            for i, c in enumerate(row[1].split(' ')):
                try: connections.append(int(c))
                except Exception as ex:
                    msg = f"Invalid waypoint connection #{i}: {c} in row {row_index} (wp: {wp_index}) of {file.path.name}"
                    logger.error(msg)
        for connection in connections:
            if connection == wp_index:
                msg = f"Connection {connection} is connected to itself in row {row_index} (wp: {wp_index}) of {file.path.name}"
                logger.error(msg)
                # connections.remove(connection)
        target = Vector3([float(p) for p in row[4].split(' ')]) if row[4] else None
        wp_type = row[2]
        try: wp_type = WaypointType(wp_type)
        except Exception as ex:
            msg = f"Invalid waypoint type: {wp_type} in row {row_index} (wp: {wp_index}) of {file.path.name} [Replacing with default {DefaultWaypointType.name}]"
            logger.error(msg)
            wp_type = DefaultWaypointType
        return Waypoint(_index=wp_index, position=pos, connections=connections, type=wp_type, angle=angle, target=target, file=file)

@dataclass
class WaypointRow(Waypoint):
    connections: list[int]
    def __init__(self, waypoint: 'Waypoint', connections: list[int]):
        super().__init__(waypoint._index, waypoint.position, waypoint.connections, waypoint.type, waypoint.angle, waypoint.target, waypoint.file)
        self.connections = connections

    def to_list(self, connections: bool = False):
        return [vectorStr(self.position), self.connections_str() if connections else "" , self.type.value, vectorStr(self.angle), vectorStr(self.target), ""]