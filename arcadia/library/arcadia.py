import logging.config
import sqlite3
import ast
from typing import Any, Union

from .arcadia_types import DataViewType, VineRoot
from .db.db_types import AddDbItemResponse, ItemPackage
from .vine import Vine
from .db.arcadia_db import ArcadiaDb


class Arcadia:
    def __init__(self, logging_object: Any, sql_lite_db_path: str, data_view_type: DataViewType):
        self._logging_object = logging_object
        self._logger: logging.Logger = logging_object.getLogger(type(self).__name__)
        self._logger.setLevel(logging.INFO)
        self._data_view_type: DataViewType = data_view_type
        self._arcadia_db: ArcadiaDb = ArcadiaDb(logging_object, sql_lite_db_path)

    def _get_subjects_list(self) -> list:
        subjects: Union[str, list] = self.get_subjects()
        if isinstance(subjects, list):
            subjects_list = subjects
        else:
            subjects_list: list[str] = subjects.split(',')
        return subjects_list

    def add_item(self, item_package: ItemPackage) -> AddDbItemResponse:
        response: AddDbItemResponse = {
            'added_item': False,
            'reason': 'error',
            'data': []
        }
        try:
            attempt_insert: AddDbItemResponse = self._arcadia_db.insert_record(item_package)
            return attempt_insert
        except TypeError as type_error:
            self._logger.error(f'Received error trying to add record: {str(type_error)}')
            response['data'] = ['Received error trying to add record']
            return response
        except Exception as error:
            self._logger.error(f'Received error trying to add record: {str(error)}')
            response['data'] = ['Received error trying to add record']
            return response

    def get_summary(self, main_tag: str) -> Union[VineRoot, str]:
        try:
            records: list[sqlite3.Row] = self._arcadia_db.get_records(main_tag)
            arcadia_vine: Vine = Vine(self._logging_object, main_tag, records, self._data_view_type)
            if self._data_view_type == DataViewType.RAW:
                return arcadia_vine.get_vine_root()
            return arcadia_vine.__str__()
        except TypeError as type_error:
            self._logger.error(f'Received error getting record vine: {str(type_error)}')

    def get_subjects(self) -> Union[str, list]:
        try:
            db_tags: list[sqlite3.Row] = self._arcadia_db.get_tags()
            subjects: list = []

            for tag in db_tags:
                tags: list = ast.literal_eval(tag['tags'])
                for item_tag in tags:
                    if item_tag not in subjects:
                        subjects.append(item_tag)
            subjects.sort(key=lambda subject: subject.lower())
            return subjects if self._data_view_type == DataViewType.RAW else Vine.tag_string(subjects)
        except TypeError as type_error:
            self._logger.error(f'Received error getting arcadia subjects: {str(type_error)}')

    def get_subjects_dictionary(self) -> dict[str:list[str]]:
        try:
            subjects_list = self._get_subjects_list()
            ascii_start: int = 65
            ascii_stop: int = 91
            ascii_loop_counter: int = ascii_start
            ascii_range: int = ascii_stop - ascii_start
            alphabetical_tags: dict[str:list[str]] = {}

            for index in range(ascii_range):
                if ascii_loop_counter < ascii_stop:
                    key_letter: str = chr(ascii_loop_counter)
                    alphabetical_tags[key_letter] = []
                    for subject_index in range(len(subjects_list)):
                        subject_first_letter: str = subjects_list[subject_index][0].capitalize()
                        if subject_first_letter == key_letter:
                            alphabetical_tags[key_letter].append(subjects_list[subject_index])
                ascii_loop_counter += 1
            return alphabetical_tags
        except TypeError as type_error:
            self._logger.error(f'Received error getting subjects dict: {str(type_error)}')
        except Exception as error:
            self._logger.error(f'Received error trying to get subjects dict: {str(error)}')

    def get_similar_subjects(self, main_tag: str) -> list:
        try:
            similar_subjects: list = []
            subjects_list = self._get_subjects_list()

            for subject in subjects_list:
                if main_tag != subject and main_tag in subject:
                    similar_subjects.append(subject)
            return similar_subjects
        except TypeError as type_error:
            self._logger.error(f'Received error getting similar subjects: {str(type_error)}')
