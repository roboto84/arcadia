import os
import logging.config
import sqlite3

from dotenv import load_dotenv
from library.arcadia_types import DataViewType
from library.arcadia import Arcadia
from library.db.arcadia_db import ArcadiaDb


if __name__ == '__main__':
    logging.config.fileConfig(fname=os.path.abspath('arcadia/bin/logging.conf'), disable_existing_loggers=False)
    logger: logging.Logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    try:
        load_dotenv()
        SQL_LITE_DB: str = os.getenv('SQL_LITE_DB')
        arcadia_db: ArcadiaDb = ArcadiaDb(logging, SQL_LITE_DB)
        arcadia: Arcadia = Arcadia(logging, SQL_LITE_DB, DataViewType.RAW)
        db_urls: list[sqlite3.Row] = arcadia_db.get_meta_data()
        urls: list[str] = []
        count = 0

        for url in db_urls:
            if url['title'] == 'None' and url['description'] == 'None' and url['image'] == 'None':
                count += 1
                arcadia.update_item_meta(url['data'])
        logger.info(f'Total Updates Attempted: {count}')

    except TypeError as type_error:
        logger.error(f'Received TypeError: {type_error}')
        exit()
    except Exception as exception:
        logger.error(f'Exception was thrown: {str(exception)}')
        raise
