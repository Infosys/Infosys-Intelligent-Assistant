__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""
from bson.binary import Binary
from pymongo import MongoClient

from parse_email.utils.log_helper import log_setup, get_logger

log = get_logger(__name__)

def insert_one_to_db(config: dict, collection_name: str, record_to_insert: dict) -> str:
    """

    :param config:
    :param collection_name:
    :param record_to_insert:
    :return: inserted id
    """
    try:
        client = MongoClient(config['hostname'], int(config['port']))
        db = client[config['database']]
        collection = db[collection_name]
        insert_response = collection.insert_one(record_to_insert)
        log.info(insert_response)
        log.info(f"insert_response.inserted_id: {insert_response.inserted_id}")
        return insert_response.inserted_id

    except Exception as e:
        log.info(f"Not Inserted: {record_to_insert}")
        log.error(e)
        return ''


def insert_many_to_db(config: dict, collection_name: str, records_to_insert: list) -> dict:
    """

    :param config:
    :param collection_name:
    :param records_to_insert:
    :return: inserted ids
    """
    try:
        client = MongoClient(config['hostname'], int(config['port']))
        db = client[config['database']]
        collection = db[collection_name]
        insert_responses = collection.insert_many(records_to_insert)

    except Exception as e:
        log.info(f"Not Inserted: {records_to_insert[0]}")
        log.error(e)
        return []


def update_records_to_db(config: dict, collection_name: str, key: str, values_to_update: dict, records: dict):
    """

    :param config:
    :param collection_name:
    :param key:
    :param values_to_update:
    :param records:
    :return: None
    """
    try:
        client = MongoClient(config['hostname'], int(config['port']))
        db = client[config['database']]
        collection = db[collection_name]
        log.info("Finding Details")
        log.debug(f"values_to_update: {values_to_update}")
        log.debug(f"key: {key}")
        collection_find = collection.find(
            {'_id': key},
            {"_id": 1, })

        collection_list = list(collection_find)

        if not collection_list:
            insert_response = collection.insert_one(
                {
                    records.update(values_to_update)
                }
            )
            log.info(f"Inserted User Details {insert_response.inserted_id}")
        else:

            update_result = collection.update(
                {'_id': key},
                {"$set": values_to_update})
            log.info(f"Updated User Details {update_result}")
    except Exception as e:
        log.error(e, exc_info=True)


def get_records_from_db(config: dict, collection_name: str, record_to_find: dict, select_fields: dict = {}) -> list:

    try:
        client = MongoClient(config['hostname'], int(config['port']))
        db = client[config['database']]
        collection = db[collection_name]
        log.info("Finding Details")
        select_fields.update({ '_id': 0 })
        log.info(f"record_to_find : {record_to_find}")
        return list(collection.find(record_to_find, select_fields))
    except Exception as e:
        log.error(e)
        return []