
import ast
import sqlite3
import logging.config

from .arcadia_types import NodeType, VineNode, VineRoot, DataViewType
from typing import Any, Optional

from .db.db_types import ArcadiaDbRecord, ArcadiaDataType


class Vine:
    def __init__(self, logging_object: Any, main_tag: str, records: list[sqlite3.Row], data_view_type: DataViewType):
        self._logger: logging.Logger = logging_object.getLogger(type(self).__name__)
        self._logger.setLevel(logging.INFO)
        self._data_view_type: DataViewType = data_view_type
        self._vine: VineRoot = {
            'subject': main_tag,
            'main_node': None,
            'sub_node': []
        }
        self._records: list[ArcadiaDbRecord] = []
        self._vine_sub_categories: list[str] = []
        if len(records) > 0:
            self._copy_records(records)
            self._vine_sub_categories = list(set(self._vine_sub_categories))
            self._vine_sub_categories.sort()
            self._structure_vine(self._records)

    def __str__(self):
        try:
            title_raw: str = f'{self._vine["subject"].capitalize()}'
            title: str = f'*{title_raw}*' if self._data_view_type == DataViewType.ENHANCED_TEXT else title_raw
            title_view: str = f'🌿  {title}\n'
            main_category_summary: str = ''
            sub_category_summaries: str = ''
            if len(self._records) == 0:
                return f'{title_view} No results found\n'
            else:
                if self._vine['main_node']:
                    main_category_summary += self._main_category_summary(self._vine['main_node'], NodeType.root)
                for node in self._vine['sub_node']:
                    sub_category_summaries += self._sub_category_summary(node, NodeType.subNode)
                return f'{title_view}' \
                       f'{main_category_summary}\n' \
                       f'{sub_category_summaries}'
        except TypeError as type_error:
            self._logger.error(f'Received type error outputting string representation: {str(type_error)}')
        except NameError as name_error:
            self._logger.error(f'Received name error outputting string representation: {str(name_error)}')

    def _copy_records(self, records: list[sqlite3.Row]) -> None:
        try:
            for record in records:
                record_copy = dict(record).copy()
                record_copy['tags'] = ast.literal_eval(record_copy['tags'])
                self._vine_sub_categories = self._vine_sub_categories + record_copy['tags']
                self._records.append(record_copy)
        except TypeError as type_error:
            self._logger.error(f'Received error copying records: {str(type_error)}')

    def _structure_vine(self, records: list[ArcadiaDbRecord]) -> None:
        try:
            for record in records:
                tags_copy = record['tags'].copy()
                for sub_category in self._vine_sub_categories:
                    if sub_category in record['tags']:
                        node_type = NodeType.subNode
                        if sub_category == self._vine['subject'] and len(record['tags']) == 1:
                            node_type = NodeType.root
                        record['tags'].remove(sub_category)

                        if node_type == NodeType.root or sub_category != self._vine['subject']:
                            new_node: VineNode = self._get_vine_node(sub_category, node_type)
                            if record['data_type'] == ArcadiaDataType.NOTE.value:
                                new_node['notes'].append(record)
                            elif record['data_type'] == ArcadiaDataType.URL.value:
                                new_node['urls'].append(record)
                record['tags'] = tags_copy

        except TypeError as type_error:
            self._logger.error(f'Received error structuring vine: {str(type_error)}')
        except KeyError as key_error:
            self._logger.error(f'Received error structuring vine: {str(key_error)}')

    def _get_vine_node(self, node_subject: str, node_type: Optional[NodeType] = NodeType.subNode) -> VineNode:
        if node_type == NodeType.root:
            if self._vine['main_node']:
                return self._vine['main_node']
        elif node_type == NodeType.subNode:
            for node in self._vine['sub_node']:
                if node_subject == node['subject']:
                    return node

        new_node: VineNode = {
            'subject': node_subject,
            'notes': [],
            'urls': []
        }

        if node_type == NodeType.root:
            self._vine.update({'main_node': new_node})
        elif node_type == NodeType.subNode:
            self._vine['sub_node'].append(new_node)
        return new_node

    def _main_category_summary(self, node, node_type: NodeType) -> str:
        return f'  {self._category_summary(node, node_type)}'

    def _sub_category_summary(self, node, node_type: NodeType) -> str:
        subtitle_raw: str = node["subject"]
        subtitle: str = f'*{subtitle_raw}*' \
            if self._data_view_type == DataViewType.ENHANCED_TEXT else f'{subtitle_raw}:'
        return f'  {subtitle}\n' \
               f'  {self._category_summary(node, node_type)}'

    def _category_summary(self, node, node_type: NodeType) -> str:
        try:
            return f'{self._sub_category_details(node["notes"], node_type)}' \
                   f'{self._sub_category_details(node["urls"], node_type)}'
        except TypeError as type_error:
            self._logger.error(f'Received type error creating sub category sub string: {str(type_error)}')

    def _sub_category_details(self, node_array: list[ArcadiaDbRecord], node_type: NodeType) -> str:
        try:
            if len(node_array):
                spacer: str = '' if node_type == NodeType.root else '   '
                return '  '.join(
                    f'{spacer}◦ {item["time_stamp"]} [{self.tag_string(item["tags"])}]: {str(item["data"])}\n'
                    for item in node_array
                )
            else:
                return ''
        except TypeError as type_error:
            self._logger.error(f'Received type error creating category sub string: {str(type_error)}')

    @staticmethod
    def tag_string(tags) -> str:
        if tags:
            tag_string = ''.join(f'{tag},' for tag in tags).rstrip(', ')
            return f'{tag_string}'
        else:
            return ''

    def get_vine_root(self) -> VineRoot:
        return self._vine
