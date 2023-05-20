from typing import TypedDict
from enum import Enum


class ArcadiaDataType(Enum):
    NOTE = 'NOTE'
    URL = 'URL'


class ArcadiaDbRecord(TypedDict):
    ID: str
    time_stamp: str
    data: str
    tags: list[str]
    data_type: str


class ItemPackage(TypedDict):
    data_type: ArcadiaDataType
    content: str
    tags: list[str]
