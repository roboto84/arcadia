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
            subjects = arcadia.get_subjects_dictionary()

            # TODO: Look at supplying stats through CLI
            # print(f'Total Tag Count: {arcadia.get_subject_count()}')
            # print(f'Total Item Count: {arcadia.get_item_count()}')
            # print(f'Total Url Count: {arcadia.get_url_item_count()}')

            print(f'\nSimilar Tags: {arcadia.get_similar_subjects(search_term)}\n')
            print(arcadia.get_summary(search_term))

            # TODO: Support getting/deleting/updating items through CLI
            print(arcadia.get_counts_of_subjects())
            # print(arcadia.get_random_url_item())
            # arcadia.delete_item('https://www.youtube.com/@MrCastIron/videos')
            # print(arcadia.update_item(
            #     'https://www.google.com',
            #     'https://google.com',
            #     'Something Else',
            #     ['hey', 'there', 'you'],
            #     'New Description',
            #     'new/image/location'
            # ))
            # print(arcadia.get_item('https://www.openfietsmap.nl/downloads/europe'))

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
