
import ast
import sqlite3
import logging.config
from typing import Any


class Vine:
    def __init__(self, logging_object: Any, main_tag: str, records: list[sqlite3.Row]):
        self._logger: logging.Logger = logging_object.getLogger(type(self).__name__)
        self._logger.setLevel(logging.INFO)
        self._vine: dict = {
            'subject': main_tag,
            'nodes': []
        }
        self._records: list[dict] = []
        self._vine_sub_categories: list[str] = []
        self._copy_records(records)
        self._vine_sub_categories = list(set(self._vine_sub_categories))
        self._vine_sub_categories.sort()
        self._structure_vine(self._records)

    def __str__(self):
        try:
            categories_summaries: str = ''
            for node in self._vine['nodes']:
                categories_summaries += self._sub_category_summary(node)
            return f'\n🌿  {self._vine["subject"].capitalize()}\n' \
                   f'{categories_summaries}'
        except TypeError as type_error:
            self._logger.error(f'Received type error outputting string representation: {str(type_error)}')
        except NameError as name_error:
            self._logger.error(f'Received name error outputting string representation: {str(name_error)}')

    def _copy_records(self, records):
        try:
            for record in records:
                record_copy = dict(record).copy()
                record_copy['tags'] = ast.literal_eval(record_copy['tags'])
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
                        record['tags'].remove(sub_category)
                        new_node: dict = self._get_vine_node(sub_category)
                        if record['data_type'] == 'note':
                            new_node['notes'].append(record)
                        elif record['data_type'] == 'hyperlink':
                            new_node['hyperlinks'].append(record)

        except TypeError as type_error:
            self._logger.error(f'Received error structuring vine: {str(type_error)}')
        except KeyError as key_error:
            self._logger.error(f'Received error structuring vine: {str(key_error)}')

    def _get_vine_node(self, node_subject):
        for node in self._vine['nodes']:
            if node_subject == node['subject']:
                return node
        new_node: dict = {
            'subject': node_subject,
            'notes': [],
            'hyperlinks': []
        }
        self._vine['nodes'].append(new_node)
        return new_node

    def _sub_category_summary(self, node):
        try:
            return f'{node["subject"]}: \n' \
                   f'{self._sub_category_details(node["notes"])}'\
                   f'{self._sub_category_details(node["hyperlinks"])}'
        except TypeError as type_error:
            self._logger.error(f'Received type error creating category sub string: {str(type_error)}')

    def _sub_category_details(self, node_array: list[dict]):
        try:
            if len(node_array):
                return ''.join(
                    f'  ◦ {item["time_stamp"]}{self.tag_string(item["tags"])}: {str(item["data"])}\n'
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
