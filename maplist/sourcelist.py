from typing import Any
from dataclasses import dataclass
from .source import Source
from utils import get_safe

@dataclass
class SourceList:
    sources: list[Source]

    @staticmethod
    def from_dict(obj: Any) -> 'SourceList':
        _sources = Source.from_dict(get_safe(obj, "sources"))
        return SourceList(_sources)