__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""
import os
import requests
from matplotlib import pyplot as plt
from pymongo import MongoClient
from pathlib import Path
from iia.persistence.mongodbpersistence import MongoDBPersistence
from iia.persistence.mappingpersistence import MappingPersistence
from iia.utils.config_helper import get_config
import pysnow
import atexit
from datetime import datetime as dt
from iia.utils.log_helper import get_logger, log_setup
from iia.itsm.adapter import SNOW
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.start()
atexit.register(lambda: scheduler.pause())
logging = get_logger(__name__)

class ParseITSMAttachments(object):

    @staticmethod
    def save_attachments(number:str, sys_id:str, customer_id,save_directories:list):
        try:
            logging.debug(f"Fetching attachments for {number},{sys_id}")
            itsm_details = MongoDBPersistence.itsm_details_tbl.find_one({"CustomerID": customer_id}, {"_id": 0})
            logging.debug(f"itsm_details: {itsm_details}")
            acceptable_file_formats = get_config('files')['image.formats']
            acceptable_file_formats = acceptable_file_formats.split(',')
            resource = SNOW.getClient(itsm_details) if SNOW.servicenow_incidents is None else SNOW.servicenow_incidents
            logging.debug(f"Proccesing sys_id: {sys_id}")
            service_now_attachments = resource.attachments.get(sys_id=sys_id)

            logging.debug(f"service_now_attachments: {service_now_attachments}")
            attachment_count = 1
            accepted_attachment_count = 1
            for attachment in service_now_attachments:
                logging.debug(f"processing attachment {attachment_count}/{len(service_now_attachments)}")

                file_name = attachment['file_name']
                logging.debug(f"filename: {file_name}")
                file_format = str(attachment['content_type']).split("/")[-1].lower()
                print(f"file_format: {file_format}")
                if file_format in acceptable_file_formats:
                    download_link = attachment['download_link']
                    logging.debug(f"download_link: {download_link}")
                    modified_file_name = f"{number}_{accepted_attachment_count}.png"
                    logging.debug(f"modified_file_name: {modified_file_name}")
                    accepted_attachment_count = accepted_attachment_count + 1

                    for dir in save_directories:
                        r = requests.get(download_link,
                                         auth=(itsm_details['UserID'], itsm_details['Password']),
                                         stream=True)
                        logging.debug(f"Saving in directory : {dir}")
                        if not os.path.isdir(dir):
                            os.mkdir(dir)
                        dir_incident = dir + number + "\\"
                        logging.debug(f"Saving in directory : {dir_incident}")
                        if not os.path.isdir(dir_incident):
                            os.mkdir(dir_incident)

                        with open(dir_incident + modified_file_name, "wb") as image_file:
                            for chunk in r.iter_content(1024):
                                image_file.write(chunk)

                attachment_count = attachment_count + 1
        except Exception as e:
            logging.error(e,exc_info=True)

    @staticmethod
    def parse_attachment():
        try:
            customer_ids = list(MongoDBPersistence.customer_tbl.find({}, {"CustomerID": 1, "_id": 0}))
            logging.debug(f"customer_ids: {customer_ids}")
            for customer_id in customer_ids:
                customer_id = customer_id['CustomerID']
                logging.debug(f"Proccessing CustomerId: {customer_id}")
                field_mapping = MappingPersistence.get_mapping_details(customer_id)
                ticket_id_field_name_ = field_mapping['Ticket_ID_Field_Name']
                path1 = "static\\assets\\uploads\\"
                path2 = "data\\AttachementAnalysis\\uploads\\"
                # Creating directory for image attachements in static folder
                if not os.path.exists("static\\assets\\uploads\\"):
                    os.makedirs("static\\assets\\uploads\\")
                    logging.debug(f"Folder created Successfully in static folder")

                # Creating directory for image attachements in AttachementAnalysis folder
                if not os.path.exists("data\\AttachementAnalysis\\uploads\\"):
                    os.makedirs("data\\AttachementAnalysis\\uploads\\")
                    logging.debug(f"Folder created Successfully in attachment analysis folder")
                records = MongoDBPersistence.rt_tickets_tbl.find({'attachment_parsed': False}
                                                                 , {ticket_id_field_name_: 1, "sys_id":1 , "_id": 0})
                for record in records:
                    logging.info(f"Parsing Attachment for {record[ticket_id_field_name_]}")
                    try:
                        ParseITSMAttachments.save_attachments(number=record[ticket_id_field_name_],
                                                         sys_id=record['sys_id'],
                                                         customer_id=customer_id,
                                                         save_directories=[path1, path2])
                        logging.debug("Attachment saved successfully")

                        MongoDBPersistence.rt_tickets_tbl.update_one(
                            {ticket_id_field_name_: record[ticket_id_field_name_]},
                            {'$set': {'attachment_parsed': True}}, upsert=True)
                    except Exception as e:
                        logging.error(e,exc_info=True)

        except Exception as e:
            logging.error("error in saving attachements")
            logging.error(e,exc_info=True)


job_id = 'DEFAULT_JOB_ID' #add job_id here
str_time = dt.now()
print("Adding Job")
seconds = 60
try:
    seconds = get_config('service_now')['attachment_schedule_seconds']
except Exception as e:
    logging.error(e, exc_info=True)
scheduler.add_job(ParseITSMAttachments.parse_attachment, trigger="interval", id=job_id,
                  seconds=60, next_run_time=str_time)