__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""
import os
import ssl
import sys
import re
from datetime import timedelta
from urllib.parse import urlparse

import html2text
import requests.adapters

from exchangelib import Credentials, Account, DELEGATE, Configuration, EWSDateTime, EWSTimeZone
from exchangelib.protocol import BaseProtocol

from parse_email.crypt.crypt import decrypt_credentials
from parse_email.utils.ner_helper import ner_image_entity_recognistaion, ner_extract_from_text
from parse_email.utils.servicenow_helper import get_records, insert_new_record
from parse_email.utils.config_helper import get_config
from parse_email.utils.log_helper import log_setup, get_logger
from parse_email.utils.mongdb_helper import get_records_from_db

log = get_logger(__name__)

log_setup("parse_email")

cert_file_path = '' #Enter the certificate path

foldername = cert_file_path.split('/')[0]
log.info(f"foldername {foldername}")
if not os.path.exists(foldername):
    os.makedirs(foldername, exist_ok=True)

config_mongodb = get_config('mongodb')
config = get_records_from_db(config_mongodb,'TblConfigurationValues',{"_id":'email'},{})[0]
log.info(config)

def connect_mailbox():
    log.info("Connecting Mailbox")
    try:

        dict_user_credentials = decrypt_credentials('./config/email_config.json')
        user = dict_user_credentials['username']
        pass1 = dict_user_credentials['password']

        mail_type = bool(config['mail_type'])

        if mail_type:
            server = config['server']
            
            user_name, domain = user.split('@')
            log.info(user_name)
            log.info(domain)
            if 'ad.' in domain:
                company = (domain.split('ad.'))[1]
            else:
                company = domain
            primary_user = user_name + '@' + company

        else:
            server = 'outlook.office365.com'
            user_name = user
            primary_user = user
        log.info(f"Server: {config['server']}")
        credentials = Credentials(username=user_name, password=pass1)
        
        server_config = Configuration(server=server, credentials=credentials)
        account = Account(primary_smtp_address=primary_user, credentials=credentials, autodiscover=False,
                          config=server_config,
                          access_type=DELEGATE)
        log.info("Successfully connected to Mailbox")

        return account
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        log.error(e)
        log.error(f"{exc_type}  {fname}  {exc_tb.tb_lineno}")


def process_email():
    try:

        context = ssl.create_default_context()
        der_certs = context.get_ca_certs(binary_form=True)
        pem_certs = [ssl.DER_cert_to_PEM_cert(der) for der in der_certs]

        with open(cert_file_path, 'w') as outfile:
            for pem in pem_certs:
                outfile.write(pem + '\n')

        log.debug(config)
        server = config['server']
        
        requests.get(f'https://{server}', verify=cert_file_path)

        class RootCAAdapter(requests.adapters.HTTPAdapter):

            def cert_verify(self, conn, url, verify, cert):

                server = config['server']
                
                cert_file = {
                    f"{server}": cert_file_path,
                    'mail.internal': '/path/to/mail.internal.crt'
                }[urlparse(url).hostname]
                super(RootCAAdapter, self).cert_verify(conn=conn, url=url, verify=cert_file, cert=cert)

        # Tell exchangelib to use this adapter class instead of the default
        BaseProtocol.HTTP_ADAPTER_CLS = RootCAAdapter

        account = connect_mailbox()

        h = html2text.HTML2Text()
        h.ignore_links = True

        if config['input_folder'] == '' or config['input_folder'] is None:
            input_folder = account.inbox
        else:
            input_folder = account.inbox / config['input_folder']

        processed_folder = account.inbox / config['processed_folder']

        tz = EWSTimeZone.localzone()
        now = tz.localize(EWSDateTime.now())
        received_dt = now - timedelta(days=int(config['days_to_filter']))

        unread_mail_list = input_folder.all() \
            .filter(datetime_received__gt=received_dt) \
            .order_by('-datetime_received')

        unread_mail_list = list(unread_mail_list)

        curr_mail_list = []
        for mail in unread_mail_list:
            curr_mail_list.append(mail)

        print(len(curr_mail_list))
        log.info(f"len mail list: {len(curr_mail_list)}")
        count = 1
        for mail in reversed(curr_mail_list):
            print(f"Processing Email...{count}/{len(curr_mail_list)}")
            log.info(f"Processing Email...{count}/{len(curr_mail_list)}")
            count = count + 1
            short_description = mail.subject
            log.info(f"short_description: {short_description}")
            try:
                sender_email = mail.sender.email_address
            except Exception as e:
                sender_email = config['caller_emailid']
                log.error(e)
            description = h.handle(mail.body)
            log.debug(f"mail description {description}")
            config_files = get_config('files')
            log.info(f"config_files: {config_files}")
            list_user_details = get_records(api_path='user_api_path', search_records=[('email', '=', sender_email)])

            if not list_user_details:
                sys_id = \
                    get_records(api_path='user_api_path', search_records=[('email', '=', config['caller_emailid'])])[0][
                        'sys_id']
            else:
                sys_id = list_user_details[0]['sys_id']

            attachments = []
            if mail.attachments:
                for attachment in mail.attachments:
                    try:
                        abspath = os.path.abspath('./attachment/')

                        if not os.path.exists(abspath):
                            os.mkdir(abspath)

                        local_path = os.path.join(abspath, attachment.name)

                        with open(local_path, 'wb') as f:
                            f.write(attachment.content)

                        attachments.append(local_path)

                        log.info(f"attachment name: {attachment.name}")
                        log.info(f"attachment format: {attachment.name.split('.')[-1]}")
                        log.info(f"len description : {len(description)}")

                        description = description.strip()

                        if len(description) <= int(config['description_len']):

                            if attachment.name.split(".")[-1] in config_files['image.formats']:

                                image_text = None
                                if config['image_text_extract'].__str__().lower() == 'true':
                                    image_text = ner_image_entity_recognistaion(local_path)
                                    description = description.strip() + ' ' + image_text
                                    log.info(f"image_text : {image_text}")

                                if config['ner_extract'].__str__().lower() == 'true':
                                    if image_text is None:
                                        image_text = ner_image_entity_recognistaion(local_path)

                                    list_NER = ner_extract_from_text(image_text)

                                    for ner in list_NER:
                                        log.info(f"ner: {ner}")
                                        description = description.strip() + ' , '.join(
                                            [f'{key}:{value}' for key, value in ner.items()])

                            if attachment.name.split(".")[-1] in config_files['text.formats']:
                                with open(local_path, "r") as f:
                                    data = f.read()
                                log.info(f"text file data: {data}")
                                description = description + data


                            log.info(f"image description {description}")
                    except Exception as e:
                        log.error(e)

            print("str short_description " + str(short_description).strip())
            if str(short_description).strip() == ""\
                    or short_description is None:

                short_description = description[0:50]

            ## Removing CID's which are part of description when image is attached embedded

            patterns = get_config('email')['cid_patterns']
            log.info(f"patterns: {patterns}")
            patterns = str(patterns).split('~~||~~')
            log.info(f"patterns: {patterns}")
            for pattern in patterns:
                log.info(f"pattern: {pattern}")
                cids = re.findall(str(pattern).strip(), description)
                log.info(f"cids: {cids}")
                if len(cids) > 0:
                    for cid in cids:
                        log.info(f"cid: {cid}")
                        description = description.replace(cid, '')



            dict_new_records = {
                                "short_description": short_description,
                                "description": description.strip(),
                                "caller_id": sys_id,
                                }

            dict_new_records.update(config['ITSM_default_fields'])


            log.info(f"insert new records : {dict_new_records}")

            result = insert_new_record(dict_new_record=dict_new_records, attachments=attachments)

            if result:
                
                mail.move(processed_folder)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        log.error(e)
        log.error(f"{exc_type}  {fname}  {exc_tb.tb_lineno}")
