__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""
import os
import requests
import pysnow
from pymongo import MongoClient

from parse_email.utils.config_helper import get_config
from parse_email.utils.log_helper import log_setup, get_logger

log = get_logger(__name__)

log_setup("parse_email")

from urllib import request
log.info(request.getproxies())

def connect():
    config_service_now = get_config('service_now')
    config_mongodb = get_config('mongodb')

    m_client = MongoClient(config_mongodb['hostname'], int(config_mongodb['port']))
    db = m_client[config_mongodb['database']]
    collection = db['TblITSMDetails']

    config_collection = collection.find_one({}, {"UserID": 1, "Password": 1,"ITSMInstance":1,"_id": 0 })

    log.debug(f"config_collection: {config_collection}")

    username = config_collection['UserID']
    password = config_collection['Password']
    servicenow_instance = config_collection['ITSMInstance']
    log.info("Connecting to Service Now")

    log.info(request.getproxies())

    client = pysnow.Client(instance=servicenow_instance,
                               user=username,
                               password=password)
    log.info("Connected")
    return client


def insert_new_record(dict_new_record: dict, attachments: list):
    try:
        config = get_config('service_now')
        client = connect()
        incident = client.resource(api_path=config['table_api_path'])

        log.info("Inserting New Record")

        log.info(dict_new_record)

        result = incident.create(payload=dict_new_record)

        log.debug(result.headers)

        log.info(f"Attachments Count : {len(attachments)}")

        for attachment in attachments:
            try:
                log.info(f"Insering Attachment: {attachment}")

                attach_result = incident.attachments.upload(sys_id=f"{result.headers['Location'].split('/')[-1]}",
                                                            file_path=attachment)

                log.debug(attach_result.headers)
            except Exception as e:
                print(e)

            try:
                os.remove(attachment)
            except Exception as e:
                log.error(e)

        client.close()
        log.info("Completed Insert")
        return True
    except Exception as e:
        log.error(e)
        return False


def get_records(api_path: str = 'table_api_path', search_records: list = []):
    try:
        config = get_config('service_now')
        client = connect()
        incident = client.resource(api_path=config[api_path])

        query = ''

        for fields in search_records:
            for field in fields:
                query = query + field

        log.info(f"qb: {query}")

        iterable_content = incident.get(query=query).all()
        client.close()
        return iterable_content
    except Exception as e:
        log.error(e)
        return []