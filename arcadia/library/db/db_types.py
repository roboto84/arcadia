from typing import TypedDict
from enum import Enum


class ArcadiaDataType(Enum):
    HYPERLINK = 'hyperlink'


class AddDbItemResponse(TypedDict):
    added_item: bool
    reason: str
    data: list


class ItemPackage(TypedDict):
    data_type: ArcadiaDataType
    content: str
    tags: list
