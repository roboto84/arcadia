import logging.config
import sqlite3
import ast
from typing import Any
from .vine import Vine
from .db.arcadia_db import ArcadiaDb


class Arcadia:
    def __init__(self, logging_object: Any, sql_lite_db_path: str, enhanced_view: bool):
        self._logging_object = logging_object
        self._logger: logging.Logger = logging_object.getLogger(type(self).__name__)
        self._logger.setLevel(logging.INFO)
        self._enhanced_view = enhanced_view
        self._arcadia_db = ArcadiaDb(logging_object, sql_lite_db_path)

    def add_item(self, item_package) -> bool:
        try:
            self._arcadia_db.insert_record(item_package)
            return True
        except TypeError as type_error:
            self._logger.error(f'Received error trying to add record: {str(type_error)}')
            return False
        except Exception as error:
            self._logger.error(f'Received error trying to add record: {str(error)}')
            return False

    def get_summary(self, main_tag) -> str:
        try:
            records: list[sqlite3.Row] = self._arcadia_db.get_records(main_tag)
            arcadia_vine = Vine(self._logging_object, main_tag, records, self._enhanced_view)
            return arcadia_vine.__str__()
        except TypeError as type_error:
            self._logger.error(f'Received error getting record vine: {str(type_error)}')

    def get_subjects(self) -> str:
        try:
            db_tags: list[sqlite3.Row] = self._arcadia_db.get_tags()
            subjects: list = []

            for tag in db_tags:
                tags: list = ast.literal_eval(tag['tags'])
                for item_tag in tags:
                    if item_tag not in subjects:
                        subjects.append(item_tag)
            subjects.sort(key=lambda subject: subject.lower())
            return Vine.tag_string(subjects)
        except TypeError as type_error:
            self._logger.error(f'Received error getting arcadia subjects: {str(type_error)}')

    def get_subjects_dictionary(self) -> dict[str:list[str]]:
        subjects: str = self.get_subjects()
        subjects_list: list[str] = subjects.split(',')
        ascii_start: int = 65
        ascii_stop: int = 91
        ascii_loop_counter = ascii_start
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
