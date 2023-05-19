import ast
import logging.config
import sqlite3
from typing import Any, Union

from .arcadia_types import DataViewType, VineRoot
from .collectors.scraper import Scraper
from .db.db_types import AddDbItemResponse, ItemPackage, ArcadiaDataType, UpdateDbItemResponse
from .vine import Vine
from .db.arcadia_db import ArcadiaDb
from willow_core.library.db_types import DeleteDbItemResponse


class Arcadia:
    def __init__(self, logging_object: Any, sql_lite_db_path: str, data_view_type: DataViewType):
        self._logging_object = logging_object
        self._logger: logging.Logger = logging_object.getLogger(type(self).__name__)
        self._logger.setLevel(logging.INFO)
        self._data_view_type: DataViewType = data_view_type
        self._arcadia_db: ArcadiaDb = ArcadiaDb(logging_object, sql_lite_db_path)

    def _get_subjects_list(self) -> list[str]:
        subjects: Union[str, list] = self.get_subjects()
        if isinstance(subjects, list):
            subjects_list = subjects
        else:
            subjects_list: list[str] = subjects.split(',')
        return subjects_list

    @staticmethod
    def _tags_invalid(tags: list[str]) -> bool:
        return '' in tags

    def get_url_item_count(self) -> int:
        return int(self._arcadia_db.get_url_record_count()[0])

    def get_random_url_item(self) -> dict:
        item: dict = dict(self._arcadia_db.get_random_url_record())
        item['tags'] = ast.literal_eval(item['tags'])
        return item

    def get_item_count(self) -> int:
        return int(self._arcadia_db.get_record_count()[0])

    def add_item(self, item_package: ItemPackage) -> AddDbItemResponse:
        response: AddDbItemResponse = {
            'added_item': False,
            'reason': 'error',
            'data': []
        }
        if Arcadia._tags_invalid(item_package['tags']):
            response['reason'] = 'empty_string_tag'
            response['data'] = item_package['tags']
            self._logger.error('Unaccepted empty string tag')
            return response
        else:
            try:
                response = self._arcadia_db.insert_record(item_package)
                if item_package['data_type'] == ArcadiaDataType.URL:
                    self.update_item_meta(item_package['content'])
            except TypeError as type_error:
                self._logger.error(f'Received error trying to add record: {str(type_error)}')
                response['data'] = ['Received error trying to add record']
            except Exception as error:
                self._logger.error(f'Received error trying to add record: {str(error)}')
                response['data'] = ['Received error trying to add record']
            finally:
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
            subjects: list = [db_tag[0] for db_tag in db_tags]
            subjects.sort(key=lambda subject: subject.lower())
            return subjects if self._data_view_type == DataViewType.RAW else Vine.tag_string(subjects)
        except TypeError as type_error:
            self._logger.error(f'Received error getting arcadia subjects: {str(type_error)}')

    def get_subject_count(self) -> int:
        return int(self._arcadia_db.get_tag_count()[0])

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
                        if subjects_list[subject_index] and subjects_list[subject_index][0]:
                            subject_first_letter: str = subjects_list[subject_index][0].capitalize()
                            if subject_first_letter == key_letter:
                                alphabetical_tags[key_letter].append(subjects_list[subject_index])
                ascii_loop_counter += 1
            return alphabetical_tags
        except TypeError as type_error:
            self._logger.error(f'Received error getting subjects dict: {str(type_error)}')
        except Exception as error:
            self._logger.error(f'Received error trying to get subjects dict: {str(error)}')

    def get_similar_subjects(self, main_tag: str) -> list[str]:
        try:
            similar_subjects: list[str] = []
            subjects_list = self._get_subjects_list()

            for subject in subjects_list:
                if main_tag != subject and main_tag in subject:
                    similar_subjects.append(subject)
            return similar_subjects
        except TypeError as type_error:
            self._logger.error(f'Received error getting similar subjects: {str(type_error)}')

    def update_item_meta(self, db_url: str) -> None:
        try:
            self._logger.info(f'Attempting to get: {db_url}')
            payload = Scraper.get_url_meta(db_url)

            if payload:
                title = payload['title']['content'] if payload['title'] else 'None'
                description = payload['description']['content'] if payload['description'] else 'None'
                image = payload['image']['href'] if payload['image'] else 'None'
                self._arcadia_db.update_record_meta(
                    db_url,
                    title.strip(),
                    description.strip(),
                    image.strip()
                )
            else:
                self._logger.error(f'Unsuccessful getting meta for: {db_url}')
        except Exception as e:
            self._logger.error(f'Exception was thrown: {str(e)}')

    def update_item(self, data_key: str, new_data_key: str, title: str, tags: list[str], description: str,
                    image_location: str) -> UpdateDbItemResponse:
        response: UpdateDbItemResponse = {
            'updated_item': False,
            'reason': 'error',
            'data': []
        }
        if Arcadia._tags_invalid(tags):
            response['reason'] = 'empty_string_tag'
            response['data'] = tags
            self._logger.error('Unaccepted empty string tag')
            return response
        else:
            try:
                response = self._arcadia_db.update_record(data_key, new_data_key, title, tags, description,
                                                          image_location)
            except Exception as e:
                self._logger.error(f'Exception was thrown: {str(e)}')
            finally:
                return response

    def delete_item(self, data_key: str) -> DeleteDbItemResponse:
        response: DeleteDbItemResponse = {
            'deleted_item': False,
            'reason': 'error',
            'data': []
        }
        try:
            response = self._arcadia_db.delete_arc_record(data_key)
        except Exception as exception:
            self._logger.error(f'Exception was thrown: {str(exception)}')
        finally:
            return response
