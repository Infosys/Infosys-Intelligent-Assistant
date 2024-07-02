__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

import atexit
import uuid

import requests

from src.iia.restservice import RestService
from src.iia.utils.config_helper import get_config
from src.iia.utils.log_helper import get_logger, log_setup
logging = get_logger(__name__)
log_setup()
app = RestService.getApp()
app.secret_key="iia-secret-key"
from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.pause())

seconds = 30
port = 5011
try:
    scheduler_predict_config = get_config('scheduler_predict')
    seconds = int(scheduler_predict_config['seconds'])

    if seconds <=30:
        seconds = 30

    port = int(scheduler_predict_config['port'])
except:
    pass


def run_predict():
    try:
        logging.info("Calling Schedule Predict")

        payload = {"user":"","password":""}  # update username and password
        server_fields = get_config('server')

        server_config = {}
        ssl_fields = get_config('ssl')
        ssl_flag = str(ssl_fields['ssl']).lower()
        http = 'http'
        if ssl_flag == 'true':
            http = 'https'
        url = f'{http}://127.0.0.1:{port}'

        response = requests.post(f'{url}/api/validateUser', data=payload, verify=False)
        print(response.status_code)
        print(response.text)
        print(response.cookies)

        cookies = response.cookies

        response = requests.get(f'{url}/api/invoke_ITSM_adapter/1', cookies=cookies,
                                verify=False)
        print(response.status_code)
        print(response.text)

        response = requests.get(f'{url}/api/predict/1', cookies=cookies,
                                verify=False)

        print(response.status_code)
        print(response.text)


    except Exception as e:
        print(e)


run_predict()

scheduler.add_job(run_predict,
                  trigger="interval",
                  id=uuid.uuid4().hex,
                  seconds=seconds)

app.run(port=port)

