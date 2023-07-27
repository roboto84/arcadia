import logging.config
import os
from willow_core.library.sqlite_db import SqlLiteDb
from willow_core.library.db_types import DeleteDbItemResponse, AddDbItemResponse, UpdateDbItemResponse
from sqlite3 import Connection, Cursor, Error, Row
from typing import Any
from .db_types import ItemPackage
from .initial_db_data import initial_records


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
        if self._check_db_state(['ITEMS']):
            self._logger.info(f'DB schema looks good')
        else:
            self._logger.info(f'Tables not found')
            self._create_db_schema()
            self._load_init_db_data()

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

    def _load_init_db_data(self) -> None:
        for record in initial_records:
            db_url: str = record[0]['content']
            self.insert_record(record[0])
            self.update_record_meta(db_url, **record[1])

    def _get_column(self, column: str) -> list[Row]:
        return self._query_for_db_rows(f'select {column} from ITEMS')

    def get_record(self, item_key: str) -> Row:
        db_record: list[Row] = self._query_for_db_rows(f'SELECT * FROM items WHERE data=\'{item_key}\'')
        return db_record[0] if len(db_record) == 1 else {}

    def get_random_url_record(self) -> Row:
        db_random_url: list[Row] = self._query_for_db_rows(
            "SELECT * FROM items WHERE data_type='URL' ORDER BY RANDOM() LIMIT 1"
        )
        return db_random_url[0] if len(db_random_url) == 1 else {}

    def get_records(self, search_term: str) -> list[Row]:
        searchable_length: int = 3
        data_search: str = f'data LIKE "%{search_term}%" or ' if len(search_term) > searchable_length else ''
        return self._query_for_db_rows(
            f'select * from ITEMS where '
            f'{data_search}'
            f'tags LIKE "%\'{search_term}\'%" or '
            f'tags LIKE "%\_{search_term}\'%" or '
            f'tags LIKE "%\'{search_term}\_%" or '
            f'title LIKE "%{search_term}%" or '
            f'description LIKE "%{search_term}%" '
            f'escape "\\" '
            f'order by id desc'
        )

    def get_tags(self) -> list[Row]:
        return self._query_for_db_rows(
            "SELECT tag FROM (SELECT value AS tag FROM items, json_each(REPLACE(tags, '''', '\"'))) GROUP BY tag"
        )

    def get_tag_count(self) -> Row:
        return self._query_for_db_rows(
            "SELECT COUNT(*) FROM (SELECT tag FROM (SELECT value AS tag FROM items, json_each(REPLACE(tags, '''', "
            "'\"'))) GROUP BY tag)"
        )[0]

    def get_record_count(self) -> Row:
        return self._query_for_db_rows("SELECT COUNT(*) FROM items")[0]

    def get_url_record_count(self) -> Row:
        return self._query_for_db_rows("SELECT COUNT(*) FROM items WHERE data_type='URL'")[0]

    def get_meta_data(self) -> list[Row]:
        return self._get_column('data, title, description, image')

    def delete_arc_record(self, data_key: str) -> DeleteDbItemResponse:
        return self.delete_record(data_key, 'data', 'items')

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
            'SELECT data, tags FROM ITEMS WHERE data is ?;',
            [item_data]
        ).fetchall()

        if not table_list:
            try:
                self._logger.info(f'Inserting "{item_data}" into Arcadia_DB')
                with open(sql_path, 'r') as file:
                    db_cursor.execute(
                        file.read(),
                        (
                            self._get_time(),
                            item_data,
                            item_package['data_type'].value,
                            str(item_package['tags']).lower()
                        )
                    )
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
                'UPDATE items SET title = ?, description = ?, image = ? WHERE data = ?;',
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
                'UPDATE items SET data=?, tags=?, title = ?, description = ?, image = ? WHERE data = ?;',
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
