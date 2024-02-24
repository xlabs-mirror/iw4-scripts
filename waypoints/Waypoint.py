from dataclasses import dataclass
from enum import Enum
from pygame import Vector3
from hashlib import md5
from json import dumps
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .Waypoint import Waypoint
    from .WaypointFile import WaypointFile

from logging import getLogger, basicConfig, DEBUG, INFO
basicConfig(level=INFO)
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
    uuid: str = None

    def __lt__(self, other:'Waypoint'):
        return self.distance_to_first() < other.distance_to_first()
    def __gt__(self, other:'Waypoint'):
        return self.distance_to_first() > other.distance_to_first()
    def __compare__(self, other:'Waypoint') -> bool:
        return self.uuid == other.uuid
    def __hash__(self) -> int:
        return hash(self.hashstr())
    def hashstr(self) -> str: return dumps([str(self.position), len(self.connections), self.type.name, str(self.angle), str(self.target)])
    def index(self) -> int:
        if hasattr(self, 'file'):
            return self.file.waypoints.index(self) # +1

    def __init__(self, index:int, position:Vector3, connections:list['Waypoint'], type:WaypointType, angle:Vector3, target:Vector3, file:'WaypointFile'):
        self._index = index
        self.position = position
        self.connections = connections
        self.connections.sort()
        self.type = type
        self.angle = angle
        self.target = target
        self.uuid = md5(self.__repr__(True).encode('utf-8')).hexdigest()
        self.file = file

    def __repr__(self, connections=False) -> str:
        return f"Waypoint(uuid={self.uuid}, hash={self.__hash__()}, _i={self._index}, i={self.index()}, pos={self.position}, conns={self.connections_str() if connections else len(self.connections)}, type={self.type.name}, angle={self.angle}, target={self.target})"

    def __str__(self) -> str:
        return f"WP|{self.uuid}|{self.__hash__()}|{self.index()}|{self.position}|{self.connections_str()}|{self.type.name}|{self.angle}|{self.target}"
    
    def shortstr(self) -> str:
        return f"[{self.file.path.name}|{self.index()}/{len(self.file.waypoints)}]"

    def str(self) -> str:
        logger.info(f"self: {self}")
        logger.info(f"__repr__: {self.__repr__(True)}")
        logger.info(f"to_str: {self.to_str()}")
        logger.info(f"to_row: {self.to_row()}")
        logger.info(f"hashstr: {self.hashstr()}")

    def distance_to_zero(self) -> float: return self.position.distance_to(zeroVector)
    def distance_to_first(self) -> float: return self.distance_to(self.file.waypoints[0])
    def distance_to_last(self) -> float: return self.distance_to(self.file.waypoints[-1])
    def distance_to(self, other:'Waypoint') -> float: return self.position.distance_to(other.position)

    def connections_str(self) -> str:
        if len(self.connections) and isinstance(self.connections[0], Waypoint):
            return ' '.join([c.uuid[:8] for c in self.connections])
        return ' '.join([str(c) for c in self.connections])
    
    def to_str(self) -> str:
        return [f+"," for f in self.to_list()[:-1]]

    def to_list(self):
        connections = ' '.join([str(c.index()) for c in self.connections])
        return [vectorStr(self.position), connections, self.type.value, vectorStr(self.angle), vectorStr(self.target), ""]

    def to_row(self) -> str:
        return (",".join(self.to_list())).strip()
    
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
    def from_row(index:int, row:list[str], file:'WaypointFile'):
        pos = Vector3([float(p) for p in row[0].split(' ')]) if row[0] else None
        angle = Vector3([float(p) for p in row[3].split(' ')]) if row[3] else None
        try: connections = [int(c) for c in row[1].split(' ')] if row[1] else []
        except Exception as ex:
            msg = f"Invalid waypoint connections: {row[1]} in row {index} of {file.path.name}"
            logger.error(msg)
            for i, c in enumerate(row[1].split(' ')):
                try: connections.append(int(c))
                except Exception as ex:
                    msg = f"Invalid waypoint connection #{i}: {c} in row {index} of {file.path.name}"
                    logger.error(msg)
        target = Vector3([float(p) for p in row[4].split(' ')]) if row[4] else None
        wp_type = row[2]
        try: wp_type = WaypointType(wp_type)
        except Exception as ex:
            msg = f"Invalid waypoint type: {wp_type} in row {index} of {file.path.name} [Replacing with default {DefaultWaypointType.name}]"
            logger.error(msg)
            wp_type = DefaultWaypointType
        return Waypoint(index=index, position=pos, connections=connections, type=wp_type, angle=angle, target=target, file=file)