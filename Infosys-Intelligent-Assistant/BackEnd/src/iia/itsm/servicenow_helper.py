__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""
import requests
from bson import json_util
from iia.utils.config_helper import get_config
from iia.utils.log_helper import log_setup, get_logger
log = get_logger(__name__)

def insert_new_record(dict_new_record: dict, attachments: list):
    try:
        config = get_config('service_now')
        url = f"https://{config['hostname']}/api/now/{config['table_api_path']}"
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        log.info("Inserting New Record")
        log.info(dict_new_record)
        request_session = requests.Session()
        proxy = get_proxy_details()
        if proxy:
            request_session.proxies = get_proxy_details()
            request_session.trust_env = False
            request_session.auth = (config['user'], config['password'])

        response = request_session.post(url, headers=headers,
                                        data=json_util.dumps(dict_new_record))

        log.info(response.status_code)

        if response.status_code != 200 and response.status_code != 201:
            log.error(f'Status: {response.status_code} Headers: {response.headers} Error Response: {response.json()}')
            return False
        else:
            try:
                data = response.json()
                sys_id = data['result']['sys_id']

                log.info(f"response data: {data}")
                log.info(f"Attachments Count : {len(attachments)}")
                for attachment in attachments:
                    attachment_url = f"https://{config['hostname']}/api/now/{config['attachment_api_path']}" \
                                     f"?table_name={config['table_api_path'].split('/')[-1]}" \
                                     f"&table_sys_id={sys_id}" \
                                     f"&file_name={attachment['name']}"

                    log.info(f"Inserting attachment: {attachment}")

                    headers = {"Content-Type": f"{attachment['type']}", "Accept": "application/json"}
                    log.debug(f"attachment: {attachment}")
                    log.info(f"attachment_url: {attachment_url}")
                    log.info(f"headers: {headers}")

                    files = {
                        'file': (attachment['name'], attachment['content'], attachment['type'], {'Expires': '0'})}

                    response = request_session.post(attachment_url, auth=(config['user'], config['password']), headers=headers,
                                             files=files)

                    log.info(
                        f'Status: {response.status_code} Headers: {response.headers} Response: {response.json()}')
                return True

            except Exception as e:
                log.error(e)
                return False

    except Exception as e:
        log.error(e)
        return False


def get_records(api_path: str = 'table_api_path', search_and_records: list = [], search_or_records: list = []):
    try:
        config = get_config('service_now')

        url = f"https://{config['hostname']}/api/now/{config[api_path]}?&"

        for item in search_and_records:
            for key in list(item):
                url = url + key + '=' + item[key] + '&AND'

        if list(search_and_records):
            url = url[:-4]
        for item in search_or_records:
            for key in list(item):
                url = url + key + '=' + item[key] + '&OR'
        if search_or_records:
            url = url[:-3]

        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        log.info(f"url: {url}")
        request_session = requests.Session()
        proxy = get_proxy_details()

        if proxy:
            request_session.proxies = get_proxy_details()
            request_session.trust_env = False

        response = request_session.get(url, auth=(config['user'], config['password']), headers=headers)

        if response.status_code != 200:
            log.error(
                f'Status: {response.status_code} Headers: {response.headers} Error Response: {response.json()}')
            return []
        else:
            data = response.json()
            log.info(f"data:{data}")
            return data['result']

    except Exception as e:
        log.error(e)
        return []


def get_proxy_details() -> dict:
    config = get_config('service_now')
    try:
        if str(config['proxy']).lower() == 'true':

            proxy_server = config['proxy_server']
            proxy_port = config['proxy_port']
            proxy_server = str(proxy_server).replace('https', '')
            proxy_server = str(proxy_server).replace('http', '')
            proxy_server = str(proxy_server).replace('ftp', '')

            return {"http": f"http://{proxy_server}:{proxy_port}",
                    "https": f"https://{proxy_server}:{proxy_port}",
                    "ftp": f"ftp://{proxy_server}:{proxy_port}"}
        else:
            return {}
    except Exception as e:
        log.error(e)
        return {}