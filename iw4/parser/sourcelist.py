from typing import Any
from dataclasses import dataclass
from .source import Source

@dataclass
class SourceList:
    sources: list[Source]

    @staticmethod
    def from_dict(obj: Any) -> 'SourceList':
        _sources = Source.from_dict(obj.get("sources"))
        return SourceList(_sources)