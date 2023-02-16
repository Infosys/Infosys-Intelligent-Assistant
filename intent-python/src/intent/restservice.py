__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

from flask import Flask, request, make_response, redirect, url_for, jsonify    #Currently 'make_response' Not Using
from flask_cors import CORS, cross_origin    #Currently 'cross_origin' Not Using
from flask_restful import Resource, Api  
from datetime import datetime
#import logging
import time
from intent.persistence.mongodbpersistence import MongoDBPersistence
from intent.utils.log_helper import get_logger, log_setup
logging = get_logger(__name__)
# log_setup()
class RestService(object):
    '''
    classdocs
    '''
    app = None
    api = None
    #@staticmethod
    #def timestamp():
        #return str(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))

    @staticmethod
    def timestamp():
        return str(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))

    @staticmethod
    def getApp():        #Creating Flask app      
        now = datetime.now() 

        #logging.basicConfig(filename='intent.log', level=logging.INFO) 
        MongoDBPersistence.datasets_tbl.update_many({"job_id":{"$exists":True},"JobSettings":{"$exists":True}},{"$unset":{"job_id":1,"JobSettings":1}})
        logging.info("Warning : Restarting flask services , Hence Deleting all the Jobs.Create New !!!")
        if(RestService.app is None): 

            # time_in_sec = time.time()
            # RestService.timestamp = str(datetime.fromtimestamp(time_in_sec).strftime('%Y-%m-%d %H:%M:%S'))
            print("Creating new instance -- "+ str(now))
            RestService.app = Flask(__name__)

            RestService.api = Api(RestService.app)
            
            CORS(RestService.app)
        else:
            print("Returning existing instance "+ str(now))        
        return RestService.app
    def __init__(self, params):
        '''
        Constructor
        '''
        