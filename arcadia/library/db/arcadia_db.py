
import logging.config
import os
from willow_core.library.sqlite_db import SqlLiteDb
from sqlite3 import Connection, Cursor, Error, Row
from typing import Any
from .db_types import AddDbItemResponse, ItemPackage, UpdateDbItemResponse, DeleteDbItemResponse


class ArcadiaDb(SqlLiteDb):
    def __init__(self, logging_object: Any, db_location: str):
        self._logger: logging.Logger = logging_object.getLogger(type(self).__name__)
        self._logger.setLevel(logging.INFO)
        super().__init__(logging_object, db_location)
        self._check_db_schema()

    @staticmethod
    def add_file_path(relative_file_path: str) -> str:
        return f'{os.path.dirname(__file__)}{relative_file_path}'

    def _check_db_schema(self) -> None:
        if self._check_db_state(['items']):
            self._logger.info(f'DB schema looks good')
        else:
            self._logger.info(f'Tables not found')
            self._create_db_schema()

    def _create_db_schema(self) -> None:
        try:
            conn: Connection = self._db_connect()
            with open(self.add_file_path('/sql/schema.sql')) as f:
                conn.executescript(f.read())
            self._logger.info(f'Initializing Arcadia_DB schema')
            self._db_close(conn)
            self._logger.info(f'Database has been initialized')
        except Error as error:
            self._logger.error(f'Error occurred initializing Arcadia_DB: {str(error)}')

    def _query_for_db_rows(self, sqlite_query: str) -> list[Row]:
        try:
            conn: Connection = self._db_connect()
            self.set_row_factory(conn)
            db_cursor: Cursor = conn.cursor()
            db_records_result: list[Row] = db_cursor.execute(sqlite_query).fetchall()
            self._logger.info(f'Retrieved tags from Arcadia_DB successfully')
            self._db_close(conn)
            return db_records_result
        except Error as error:
            self._logger.error(f'Error occurred getting tags from Arcadia_DB: {str(error)}')

    def _get_column(self, column: str) -> list[Row]:
        return self._query_for_db_rows(f'select {column} from ITEMS')

    def get_records(self, search_term: str) -> list[Row]:
        searchable_length: int = 3
        data_search: str = f'data LIKE "%{search_term}%" or ' if len(search_term) > searchable_length else ''
        return self._query_for_db_rows(
            f'select * from ITEMS where '
            f'{data_search}'
            f'tags LIKE "%\'{search_term}\'%" or '
            f'tags LIKE "%\_{search_term}\'%" or '
            f'tags LIKE "%\'{search_term}\_%" or '
            f'title LIKE "% {search_term} %" or '
            f'description LIKE "% {search_term} %" '
            f'escape "\\" '
            f'order by id desc'
        )

    def get_tags(self) -> list[Row]:
        return self._get_column('tags')

    def get_meta_data(self) -> list[Row]:
        return self._get_column('data, title, description, image')

    def insert_record(self, item_package: ItemPackage) -> AddDbItemResponse:
        response: AddDbItemResponse = {
            'added_item': False,
            'reason': 'item_duplicate',
            'data': []
        }
        item_data: str = item_package['content']
        sql_path: str = self.add_file_path('/sql/insert_record.sql')
        conn: Connection = self._db_connect()
        db_cursor: Cursor = conn.cursor()
        table_list: list = db_cursor.execute(
            """SELECT data, tags FROM ITEMS WHERE data is ?;""",
            [item_data]
        ).fetchall()

        if not table_list:
            try:
                self._logger.info(f'Inserting "{item_data}" into Arcadia_DB')
                with open(sql_path, 'r') as file:
                    db_cursor.execute(
                        file.read(),
                        (self._get_time(), item_data, item_package['data_type'].value, str(item_package['tags'])))
                response: AddDbItemResponse = {
                    'added_item': True,
                    'reason': 'item_added',
                    'data': []
                }
            except Error as error:
                self._logger.error(f'Error occurred inserting record into Arcadia_DB: {str(error)}')
            except IOError as io_error:
                self._logger.error(f'IOError was thrown inserting record: {str(io_error)}')
                raise
            except Exception as exception:
                self._logger.error(f'Exception was thrown inserting record: {str(exception)}')
                raise
        else:
            self._logger.info(f'"{item_data}" is already in the DB, not reinserting')
            response['data'] = table_list
        self._db_close(conn)
        return response

    def update_record_meta(self, data_key: str, title: str, description: str, image_location: str) -> None:
        try:
            conn: Connection = self._db_connect()
            db_cursor: Cursor = conn.cursor()
            db_cursor.execute(
                """UPDATE items SET title = ?, description = ?, image = ? WHERE data = ?;""",
                [title, description, image_location, data_key]
            )
            self._db_close(conn)
            self._logger.info(f'Updated meta data successfully for: {data_key}')
        except Error as error:
            self._logger.error(f'Error occurred updating meta on Arcadia_DB at {data_key}: {str(error)}')
        except Exception as exception:
            self._logger.error(f'Exception was thrown updating meta: {str(exception)}')
            raise

    def update_record(self, data_key: str, new_data_key: str, title: str, tags: list[str], description: str,
                      image_location: str) -> UpdateDbItemResponse:
        response: UpdateDbItemResponse = {
            'updated_item': False,
            'reason': 'error',
            'data': []
        }
        try:
            conn: Connection = self._db_connect()
            db_cursor: Cursor = conn.cursor()
            db_cursor.execute(
                """UPDATE items SET data=?, tags=?, title = ?, description = ?, image = ? WHERE data = ?;""",
                [new_data_key, str(tags), title, description, image_location, data_key]
            )
            self._db_close(conn)
            self._logger.info(f'Updated record data successfully for: {data_key}')
            response['updated_item'] = True
            response['reason'] = 'item_updated'
        except Error as error:
            self._logger.error(f'Error occurred updating record on Arcadia_DB at {data_key}: {str(error)}')
        except Exception as exception:
            self._logger.error(f'Exception was thrown updating record: {str(exception)}')
            raise
        finally:
            return response

    def delete_record(self, data_key: str) -> DeleteDbItemResponse:
        response: DeleteDbItemResponse = {
            'deleted_item': False,
            'reason': 'error',
            'data': []
        }
        try:
            conn: Connection = self._db_connect()
            db_cursor: Cursor = conn.cursor()
            db_cursor.execute("""DELETE FROM items WHERE data = ?;""", [data_key])
            self._db_close(conn)
            self._logger.info(f'Deleted record successfully for: {data_key}')
            response['deleted_item'] = True
            response['reason'] = 'item_deleted'
        except Error as error:
            self._logger.error(f'Error occurred deleting record on Arcadia_DB at {data_key}: {str(error)}')
        except Exception as exception:
            self._logger.error(f'Exception was thrown deleting record: {str(exception)}')
            raise
        finally:
            return response
