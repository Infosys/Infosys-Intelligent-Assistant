__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

import os

from asgiref.wsgi import WsgiToAsgi
from flask import request, make_response
from flask.helpers import send_from_directory

from iia.restservice import RestService
from iia.utils.config_helper import get_config
from iia.utils.config_helper import log_setup
from iia.utils.log_helper import get_logger


from iia.incident.incidentrt import IncidentRT
from iia.incident.incidenttraining import IncidentTraining
from iia.itsm.servicenow import ServiceNow
from iia.masterdata.customers import CustomerMasterData
from iia.masterdata.algorithms import AlgorithmMasterData
from iia.masterdata.applications import ApplicationMasterData
from iia.masterdata.datasets import DatasetMasterData
from iia.masterdata.resourceavailability import ResourceAvailabilityMasterData
from iia.masterdata.resources import ResourceMasterData
from iia.masterdata.teams import TeamMasterData
from iia.predict.predict import Predict
from iia.training.training import Training
from iia.training.tagtraining import TagsTraining
from iia.jobscheduler.retrainjobscheduler import JobScheduler
from iia.training.retraining import Retrain
from iia.recommendation.recommendationmodel import Recommendation
from iia.recommendation.knowledgearticles import KnowledgeArticle
from iia.recommendation.kbscheduler import KnowledgeBaseScheduler
from iia.recommendation.fileserver import FileServerKnowledgeArticles
from iia.usermanagement.usermanagement import UserManagement
from iia.resolution.resolution import Resolution
from iia.resolution.RPA_Resolution import RPA_Resolution
from iia.itsm.itsm import ITSM
from iia.resolution.provideaccesstoIIA import ProvideAccessToIIA
from iia.ner.nerapi import NER
from iia.pma.pma import PMA
from iia.oneshotlearning.OneShotLearning import OneShotLearning
from iia.dashboard.dashboard import Dashboard
from iia.relatedtickets.RTscheduler import RelatedTicketScheduler
from iia.relatedtickets.related_tickets_search import relatedticket
from iia.itsm.parse_itsm_attachments import ParseITSMAttachments
from iia.jobscheduler.run_job_schedulers import SchedulerJobs

app = RestService.getApp()

app.secret_key = 'iia-secret-key'

log_setup()

logging = get_logger(__name__)

logging.info(str(app))


@app.route('/')
def root():
    print("requested for root. Serving index.html")
    return send_js('index.html')


@app.route('/<path:path>')
def send_js(path):
    if ('imageUploadScreen' in path):
        path = 'index.html'
    print("requested for " + path + ". Serving from static folder")
    cwd = os.getcwd()
    print("Current Directory = " + cwd)
    return send_from_directory(cwd + '/static', path)


ssl = get_config('ssl')

try:
    headers = ssl['headers']
except:
    headers = 'False'

if ssl['headers'] == 'True':

    @app.before_request
    def before_request():
        dict_headers = request.headers
        logging.debug(f"request_headers: {dict_headers}")
        try:

            content_length = dict_headers['Content-Length']
            if int(content_length) > 0:
                transfer_encoding = dict_headers['Transfer-Encoding']
                logging.debug(f"transfer_encoding: {transfer_encoding}")
                response = make_response("", 501)
                return response
            else:
                request_headers = str(dict_headers).lower()
                content_length = request_headers.__contains__('content-length')
                transfer_encoding = request_headers.__contains__('transfer-encoding')
                if content_length and transfer_encoding:
                    response = make_response("", 501)
                    return response

        except Exception as e:
            request_headers = str(dict_headers).lower()
            content_length = request_headers.__contains__('content-length')
            transfer_encoding = request_headers.__contains__('transfer-encoding')
            logging.debug(f"content_length: {content_length}")
            logging.debug(f"transfer_encoding: {transfer_encoding}")
            if content_length and transfer_encoding:
                response = make_response("", 501)
                return response


    @app.after_request
    def after_request(response):

        if response.status == "200 OK":
            logging.debug(f"request_headers: {response.headers}")
            response_dict = get_config('response_headers')
            for item in response_dict:
                if item in response.headers:
                    response.headers[item] = response_dict[item]
                else:
                    response.headers.add(item, response_dict[item])

        logging.debug(f"response_headers: {response.headers}")
        return response


@app.errorhandler(400)
def bad_request(error=None):
    message = {
        'status': 400,
        'message': 'Bad Request: ' + request.url + '--> Please check your data payload...',
    }
    response = make_response("", 400)
    return response


ssl_flag = get_config('ssl')['ssl']

if ssl_flag.lower() == 'true':
    app.config.update(SESSION_COOKIE_SECURE=True)
    app.config.update(SESSION_COOKIE_SAMESITE='strict')

try:
    environment = os.environ['build_environment']
    if str(environment).lower() == 'dev':
        server_fields = get_config('server')
        app.run(host=server_fields['hostname'], port=server_fields['port'], debug=os.environ['debug'])
    else:
        app = WsgiToAsgi(app)
except Exception as e:
    logging.error(e, exc_info=True)
    app = WsgiToAsgi(app)
