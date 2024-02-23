from base64 import urlsafe_b64encode
from typing import Any, Optional
from dataclasses import dataclass
from hashlib import md5
from utils import get_safe, get_fallback
from requests import Response

from logging import getLogger
logger = getLogger(__name__)

@dataclass
class FileBase:
    filename: Optional[str] = None
    url: Optional[str] = None
    md5: Optional[str] = None
    base64: Optional[str] = None

    def init(self, filename: str) -> None:
        self.filename = filename
        self.update()
    def __init__(self, filename: str = None, url: str = None, md5: str = None, base64: str = None) -> None:
        self.filename = filename
        self.url = url
        self.md5 = md5
        self.base64 = base64
    @staticmethod
    def from_dict(obj: Any) -> 'FileBase':
        if not obj: return None
        _filename = get_safe(obj, "filename") or get_safe(obj, "name")
        _url = get_safe(obj, "url")
        _md5 = get_safe(obj, "md5")
        _base64 = get_safe(obj, "base64")
        return FileBase(filename=_filename, url=_url, md5=_md5, base64=_base64)

    def update(self, urls: list[str] = None, filename: str = None, base64 = False) -> Response:
        urls = urls or ([self.url] if self.url else [])
        filename = filename or self.filename
        logger.debug(f"Updating {filename} from {len(urls)} urls")
        response = get_fallback([url.replace('{filename}', filename) for url in urls if url])
        if response:
            self.filename = filename
            self.url = response.url
            response_encoded = response.text.encode("utf-8")
            self.md5 = md5(response_encoded).hexdigest()
            if base64: self.base64 = urlsafe_b64encode(response_encoded).decode("utf-8") if base64 else None
        else: self.md5 = None;self.base64 = None; self.url = None
        return response