__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

from flask.app import Flask
from flask_restful import Api
from flask import request, jsonify
from intent.restservice import RestService
from intent.incident.incidentrt import IncidentRT
from intent.incident.incidenttraining import IncidentTraining
from intent.itsm.servicenow import ServiceNow
from intent.masterdata.customers import CustomerMasterData
from intent.masterdata.algorithms import AlgorithmMasterData
from intent.masterdata.applications import ApplicationMasterData
from intent.masterdata.datasets import DatasetMasterData
from intent.masterdata.resourceavailability import ResourceAvailabilityMasterData
from intent.masterdata.resources import ResourceMasterData
from intent.masterdata.teams import TeamMasterData
from intent.predict.predict import Predict
from intent.training.training import Training
from intent.training.tagtraining import TagsTraining
from intent.jobscheduler.retrainjobscheduler import JobScheduler
from intent.training.retraining import Retrain
from intent.recommendation.recommendationmodel import Recommendation
from intent.recommendation.knowledgearticles import KnowledgeArticle
from intent.recommendation.kbscheduler import KnowledgeBaseScheduler
from intent.recommendation.fileserver import FileServerKnowledgeArticles
from intent.usermanagement.usermanagement import UserManagement
from intent.resolution.resolution import Resolution
from intent.resolution.RPA_Resolution import RPA_Resolution
from intent.itsm.itsm import ITSM
from intent.resolution.provideaccesstoIIA import ProvideAccessToIIA
from intent.NER.nerapi import NER
from intent.pma.pma import PMA
from intent.oneshotlearning.OneShotLearning import OneShotLearning
from intent.dashboard.dashboard import Dashboard

from datetime import datetime
from flask_cors.extension import CORS

from intent.related_tickets.RTscheduler import RelatedTicketScheduler
from intent.related_tickets.related_tickets_search import relatedticket
from intent.itsm.parse_itsm_attachments import ParseITSMAttachments
from intent.jobscheduler.run_job_schedulers import SchedulerJobs
import os
from flask.helpers import send_from_directory
from intent.utils.config_helper import get_config, log_setup

from intent.utils.log_helper import get_logger

# import logging
import os

from flask import request, jsonify, redirect, make_response
from flask.helpers import send_from_directory

from intent.restservice import RestService
from intent.utils.config_helper import get_config
from intent.utils.log_helper import get_logger

from asgiref.wsgi import WsgiToAsgi

app = RestService.getApp()

app.secret_key = 'intent-secret-key'

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
    # resp = jsonify(message)
    # return resp
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
