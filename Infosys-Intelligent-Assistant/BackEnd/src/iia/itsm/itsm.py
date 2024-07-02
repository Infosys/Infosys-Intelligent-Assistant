__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

from iia.persistence.mongodbpersistence import MongoDBPersistence
from iia.restservice import RestService
from iia.masterdata.datasets import DatasetMasterData
from flask import request
from bson import json_util
from datetime import datetime, timedelta
from iia.itsm.servicenow import ServiceNow
from iia.itsm.adapter import ITSMAdapter
import importlib
from iia.utils.log_helper import get_logger, log_setup
logging = get_logger(__name__)
app = RestService.getApp()


@app.route('/api/invoke_ITSM_adapter/<int:customer_id>', methods=['GET'])
def invoke_ITSM_adapter(customer_id):
    return ITSM.invoke_ITSM_adapter(customer_id)

class ITSM(object):
    '''
    classdocs
    '''
    
    def __init__(self, params):
        '''
        Constructor
        '''

    @staticmethod
    def invoke_ITSM_adapter(customer_id):

        itsm_details = MongoDBPersistence.itsm_details_tbl.find_one({"CustomerID": customer_id}, {"_id":0})
        itsm_adapter = ITSMAdapter(itsm_details,customer_id=customer_id)
        resp = itsm_adapter.invoke_itsm()
        return resp