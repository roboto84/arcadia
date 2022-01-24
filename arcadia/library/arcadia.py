
import logging.config
import sqlite3
import ast
from typing import Any
from .vine import Vine
from .db.arcadia_db import ArcadiaDb


class Arcadia:
    def __init__(self, sql_lite_db_path: str, logging_object: Any):
        self._logging_object = logging_object
        self._logger: logging.Logger = logging_object.getLogger(type(self).__name__)
        self._logger.setLevel(logging.INFO)
        self._arcadia_db = ArcadiaDb(logging_object, sql_lite_db_path)

    def get_summary(self, main_tag) -> str:
        try:
            records: list[sqlite3.Row] = self._arcadia_db.get_records(main_tag)
            arcadia_vine = Vine(self._logging_object, main_tag, records)
            return arcadia_vine.__str__()
        except TypeError as type_error:
            self._logger.error(f'Received error getting record vine: {str(type_error)}')

    def get_subjects(self):
        try:
            db_tags: list[sqlite3.Row] = self._arcadia_db.get_tags()
            subjects: list = []

            for tag in db_tags:
                tags: list = ast.literal_eval(tag['tags'])
                for item_tag in tags:
                    if item_tag not in subjects:
                        subjects.append(item_tag)
            subjects.sort()
            return Vine.tag_string(subjects)
        except TypeError as type_error:
            self._logger.error(f'Received error getting arcadia subjects: {str(type_error)}')
