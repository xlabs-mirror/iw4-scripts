
from json import dumps
from typing import Any
from dataclasses import dataclass

@dataclass
class Player:
    name: str
    ping: int
    score: int
    test_client: int

    def toJSON(self):
        return dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

    @staticmethod
    def from_dict(obj: Any) -> 'Player':
        _name = str(obj.get("name"))
        _ping = int(obj.get("ping")) if obj.get("ping") else 0
        _score = int(obj.get("score")) if obj.get("score") else 0
        _test_client = int(obj.get("test_client")) if obj.get("test_client") else 0
        return Player(_name, _ping, _score, _test_client)