import os
import sys
import logging.config
from dotenv import load_dotenv
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
            arcadia = Arcadia(logging, SQL_LITE_DB, False)
            print(f'Current Subjects: {arcadia.get_subjects()}')
            print(arcadia.get_summary(search_term))
        else:
            print('Please give term to search')

    except TypeError as type_error:
        print(f'Received TypeError: Check that the .env project file is configured correctly: {type_error}')
        exit()
