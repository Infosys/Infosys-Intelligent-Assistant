__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""
import os
import ssl
from urllib.parse import urlparse

import requests.adapters
from exchangelib import Credentials, Account, DELEGATE, Configuration, Message, FileAttachment, Mailbox, HTMLBody
from exchangelib.protocol import BaseProtocol

from iia.utils.config_helper import get_config
from iia.utils.log_helper import log_setup, get_logger
from iia.crypt.crypt import decrypt_credentials
from iia.utils.mongdb_helper import get_records_from_db
log = get_logger(__name__)

config_mongodb = get_config('mongodb')
try:
    config = get_records_from_db(config_mongodb,'TblConfigurationValues',{"_id":'email'},{})[0]
    log.debug(config)
except Exception as e:
    log.warning("Email settings are not configured in TblConfigurationValues going with default values")
    config = {  "mail_type" : True,
                "server" : "" #enter the server link/name
             }
    log.debug(config)

cert_file_path = '' #Enter the certificate path

foldername = cert_file_path.split('/')[0]
log.debug(f"foldername {foldername}")
if not os.path.exists(foldername):
    os.makedirs(foldername, exist_ok=True)

class SendEmail(object):
    '''
        classdocs
        '''
    def __init__(self):
        pass

    @staticmethod
    def connect_mailbox():
        """

        :return: account
        """
        log.info("Connecting Mailbox")
        try:
            config_email = get_config('email')
            dict_user_credentials = decrypt_credentials(config_email['config_file_name'])
            user = dict_user_credentials['username']
            pass1 = dict_user_credentials['password']
            mail_type = bool(config['mail_type'])
            log.info(f"Server: {config['server']}")
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
                print(primary_user)

            else:
                server = 'outlook.office365.com'
                user_name = user
                primary_user = user

            credentials = Credentials(username=user_name, password=pass1)
            mail_config = Configuration(server=server, credentials=credentials)
            account = Account(primary_smtp_address=primary_user, credentials=credentials, autodiscover=False,
                              config=mail_config,
                              access_type=DELEGATE)
            log.info("Successfully connected to Mailbox")

            return account
        except Exception as e:
            log.error(e)

    @staticmethod
    def __send_email(account, recipients:list, subject:str, body:str, html_body, cc_recipient:list=[], attachments=None):
        """

        :param account:
        :param recipients:
        :param subject:
        :param body:
        :param html_body:
        :param cc_recipient:
        :param attachments:
        :return:
        """
        try:
            to_recipients = []
            log.info(f'To: {recipients}')
            for recipient in recipients:
                to_recipients.append(Mailbox(email_address=recipient))

            cc_recipients = []

            if not cc_recipient:
                for ccrecipient in cc_recipient:
                    cc_recipients.append(Mailbox(email_address=ccrecipient))

            log.info(f'CC: {cc_recipient}')

            if html_body:
                body = HTMLBody(body)

            nl = '\r\n'

            if not cc_recipients:
                m = Message(account=account,
                            folder=account.sent,
                            subject=subject,
                            body=body,
                            to_recipients=to_recipients,
                            cc_recipients=cc_recipients)
            else:
                m = Message(account=account,
                            folder=account.sent,
                            subject=subject,
                            body=body,
                            to_recipients=to_recipients
                            )

            # attach files
            for attachment_name, attachment_content in attachments or []:
                file = FileAttachment(name=attachment_name, content=attachment_content)
                log.info(f"Attaching {attachment_name}")
                m.attach(file)

            log.info(f'Sending Email')
            m.send_and_save()
            log.info('Sent Email')
            return "Success"
        except Exception as e:
            log.error(e,exc_info=True)
            return "Failure"

    @staticmethod
    def send_email(to: list, cc: list, subject, body, files: list=[], html_body=False):
        """

        :param to:
        :param cc:
        :param subject:
        :param body:
        :param files:
        :param html_body:
        :return:
        """
        try:

            context = ssl.create_default_context()
            der_certs = context.get_ca_certs(binary_form=True)
            pem_certs = [ssl.DER_cert_to_PEM_cert(der) for der in der_certs]

            with open(cert_file_path, 'w') as outfile:
                for pem in pem_certs:
                    outfile.write(pem + '\n')

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

            account = SendEmail.connect_mailbox()
            attachments = []

            for file in files:
                with open(file, 'rb') as f:
                    content = f.read()
                attachments.append((file.split('/')[-1], content))

            result = SendEmail.__send_email(account=account, recipients=to, cc_recipient=cc, subject=subject, body=body, html_body=html_body, attachments=attachments)

            for file in files:
                try:
                    os.remove(file)
                except Exception as e:
                    log.error(e)
            return result

        except Exception as e:
            log.error(e)

