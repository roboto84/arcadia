import os
import sys
import logging.config
from dotenv import load_dotenv

from library.arcadia_types import DataViewType
from library.db.db_types import ItemPackage, ArcadiaDataType
from library.arcadia import Arcadia

if __name__ == '__main__':
    logging.config.fileConfig(fname=os.path.abspath('arcadia/bin/logging.conf'), disable_existing_loggers=False)
    logger: logging.Logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    try:
        load_dotenv()
        SQL_LITE_DB: str = os.getenv('SQL_LITE_DB')

        if len(sys.argv) == 2:
            search_term = sys.argv[1]
            arcadia = Arcadia(logging, SQL_LITE_DB, DataViewType.TEXT)
            print(f'Similar Tags: {arcadia.get_similar_subjects(search_term)}')
            print(arcadia.get_summary(search_term))
        elif len(sys.argv) == 3:
            add_data = sys.argv[1]
            data_tags = sys.argv[2].split(',')
            arcadia = Arcadia(logging, SQL_LITE_DB, DataViewType.TEXT)
            add_package: ItemPackage = {
                'data_type': ArcadiaDataType.URL,
                'content': add_data,
                'tags': data_tags
            }
            print(arcadia.add_item(add_package))
        else:
            print('Please give term to search')

    except TypeError as type_error:
        print(f'Received TypeError: Check that the .env project file is configured correctly: {type_error}')
        exit()
