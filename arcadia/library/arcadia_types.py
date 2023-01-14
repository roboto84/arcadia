
from enum import Enum
from typing import TypedDict, Union
from .db.db_types import ArcadiaDbRecord


class DataViewType(Enum):
    TEXT = 'TEXT'
    ENHANCED_TEXT = 'ENHANCED_TEXT'
    RAW = 'RAW'


class NodeType(Enum):
    root = 1
    subNode = 2


class VineNode(TypedDict):
    subject: str
    notes: list[ArcadiaDbRecord]
    urls: list[ArcadiaDbRecord]


class VineRoot(TypedDict):
    subject: str
    main_node: Union[VineNode, None]
    sub_node: list[VineNode]

