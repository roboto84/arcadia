
import ast
import sqlite3
import logging.config
from .node_type import NodeType
from typing import Any, Optional


class Vine:
    def __init__(self, logging_object: Any, main_tag: str, records: list[sqlite3.Row]):
        self._logger: logging.Logger = logging_object.getLogger(type(self).__name__)
        self._logger.setLevel(logging.INFO)
        self._vine: dict = {
            'subject': main_tag,
            'main_node': {},
            'sub_node': []
        }
        self._records: list[dict] = []
        self._vine_sub_categories: list[str] = []
        if len(records) > 0:
            self._copy_records(records)
            self._vine_sub_categories = list(set(self._vine_sub_categories))
            self._vine_sub_categories.sort()
            self._structure_vine(self._records)

    def __str__(self):
        try:
            title: str = f'🌿  {self._vine["subject"].capitalize()}\n'
            main_category_summary: str = ''
            sub_category_summaries: str = ''
            if len(self._records) == 0:
                return f'{title} No results found\n'
            else:
                if self._vine['main_node']:
                    main_category_summary += self._main_category_summary(self._vine['main_node'], NodeType.main)
                for node in self._vine['sub_node']:
                    sub_category_summaries += self._sub_category_summary(node, NodeType.sub)
                return f'{title}' \
                       f'{main_category_summary}\n' \
                       f'{sub_category_summaries}'
        except TypeError as type_error:
            self._logger.error(f'Received type error outputting string representation: {str(type_error)}')
        except NameError as name_error:
            self._logger.error(f'Received name error outputting string representation: {str(name_error)}')

    def _copy_records(self, records):
        try:
            for record in records:
                record_copy = dict(record).copy()
                record_copy['tags'] = ast.literal_eval(record_copy['tags'])
                if len(record_copy['tags']) != 1 and self._vine['subject'] in record_copy['tags']:
                    record_copy['tags'].remove(self._vine['subject'])
                self._vine_sub_categories = self._vine_sub_categories + record_copy['tags']
                self._records.append(record_copy)
        except TypeError as type_error:
            self._logger.error(f'Received error copying records: {str(type_error)}')

    def _structure_vine(self, records):
        try:
            for sub_category in self._vine_sub_categories:
                for record in records:
                    if sub_category in record['tags']:
                        node_type = NodeType.sub
                        if sub_category == self._vine['subject']:
                            node_type = NodeType.main
                        record['tags'].remove(sub_category)
                        new_node: dict = self._get_vine_node(sub_category, node_type)
                        if record['data_type'] == 'note':
                            new_node['notes'].append(record)
                        elif record['data_type'] == 'hyperlink':
                            new_node['hyperlinks'].append(record)

        except TypeError as type_error:
            self._logger.error(f'Received error structuring vine: {str(type_error)}')
        except KeyError as key_error:
            self._logger.error(f'Received error structuring vine: {str(key_error)}')

    def _get_vine_node(self, node_subject, node_type: Optional[NodeType] = NodeType.sub):
        if node_type == NodeType.main:
            if self._vine['main_node']:
                return self._vine['main_node']
        elif node_type == NodeType.sub:
            for node in self._vine['sub_node']:
                if node_subject == node['subject']:
                    return node

        new_node: dict = {
            'subject': node_subject,
            'notes': [],
            'hyperlinks': []
        }
        if node_type == NodeType.main:
            self._vine['main_node'] = new_node
        elif node_type == NodeType.sub:
            self._vine['sub_node'].append(new_node)
        return new_node

    def _main_category_summary(self, node, node_type: NodeType):
        return f'  {self._category_summary(node, node_type)}'

    def _sub_category_summary(self, node, node_type: NodeType):
        return f'  {node["subject"]}: \n' \
               f'  {self._category_summary(node, node_type)}'

    def _category_summary(self, node, node_type: NodeType):
        try:
            return f'{self._sub_category_details(node["notes"], node_type)}' \
                   f'{self._sub_category_details(node["hyperlinks"], node_type)}'
        except TypeError as type_error:
            self._logger.error(f'Received type error creating sub category sub string: {str(type_error)}')

    def _sub_category_details(self, node_array: list[dict], node_type: NodeType):
        try:
            if len(node_array):
                spacer: str = '' if node_type == NodeType.main else '   '
                return '  '.join(
                    f'{spacer}◦ {item["time_stamp"]}{self.tag_string(item["tags"])}: {str(item["data"])}\n'
                    for item in node_array
                )
            else:
                return ''
        except TypeError as type_error:
            self._logger.error(f'Received type error creating category sub string: {str(type_error)}')

    @staticmethod
    def tag_string(tags):
        if tags:
            tag_string = ''.join(f'{tag}, ' for tag in tags).rstrip(', ')
            return f' ({tag_string})'
        else:
            return ''
