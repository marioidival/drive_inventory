from dataclasses import asdict, dataclass
from typing import Optional, List, Set


@dataclass
class File:
    external_id: str
    filename: str
    file_extension: Optional[str]
    mimetype: str
    owned_by_me: bool
    checksum: str
    visibility: str
    owner_file: Optional[str]
    updated_at: str


@dataclass
class Log:
    file_id: str
    changes: dict
    timestamp: str
