__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

from bson import json_util
from iia.persistence.mongodbpersistence import MongoDBPersistence
from iia.restservice import RestService
from iia.utils.log_helper import get_logger, log_setup
logging = get_logger(__name__)
app = RestService.getApp()

@app.route("/api/getAlgoDefaultParams/<int:customer_id>/<int:dataset_id>/<parameter_type>", methods=['GET'])
def getAlgoDefaultParams( customer_id,dataset_id,parameter_type):
    return AlgorithmMasterData.getAlgoDefaultParams(customer_id, dataset_id, parameter_type)

@app.route("/api/getDropdownParams/<algorithm_name>", methods=['GET'])
def getDropdownParams(algorithm_name):
    return AlgorithmMasterData.getDropdownParams(algorithm_name)
    
@app.route("/api/changeAlgorithm/<int:customer_id>/<int:algorithm_id>", methods=["PUT"])
def changeAlgorithm( customer_id, algorithm_id):
    return AlgorithmMasterData.changeAlgorithm(customer_id, algorithm_id)
    
@app.route("/api/algorithms/<int:customer_id>/<int:dataset_id>/<status>",methods=["GET"])
def getAlgorithms( customer_id,dataset_id,status):
    return AlgorithmMasterData.getAlgorithms(customer_id, dataset_id, status)
    
@app.route("/api/chosenAlgorithms/<int:customer_id>/<int:dataset_id>/<status>",methods=["GET"])
def getChosenAlgorithms( customer_id,dataset_id,status):
    return AlgorithmMasterData.getChosenAlgorithms(customer_id, dataset_id, status)  

class AlgorithmMasterData(object):
    '''
    classdocs
    '''

    def __init__(self, params):
        '''
        Constructor
        '''
        
    @staticmethod
    def getAlgoDefaultParams( customer_id,dataset_id,parameter_type):
        user_param_choices = {}

        approved_algoparam = MongoDBPersistence.training_hist_tbl.find_one({"CustomerID" : customer_id,"DatasetID" : dataset_id,"TrainingStatus" : "Approved"},{"_id":0,"AlgorithmParameters":1})
        inprogress_algoparam = MongoDBPersistence.training_hist_tbl.find_one({"CustomerID" : customer_id,"DatasetID" : dataset_id,"TrainingStatus" : "InProgress"},{"_id":0,"AlgorithmParameters":1})
        if(approved_algoparam and parameter_type == "Single"):
            user_param_choices['Algorithms'] = approved_algoparam['AlgorithmParameters']
            logging.info("picking up last Approved parameters as default parameters.")
        elif(inprogress_algoparam and parameter_type == "Single"):
            user_param_choices['Algorithms'] = inprogress_algoparam['AlgorithmParameters']
            logging.info("picking up last InProgress parameters as default parameters.")
        return json_util.dumps(user_param_choices)  
    
    @staticmethod
    def changeAlgorithm( customer_id, algorithm_id):
        #customer_tbl is a pymongo object to TblCustomer
        MongoDBPersistence.customer_tbl.update_one({"CustomerID": customer_id},\
                                            {"$set": {"AlgorithmID":algorithm_id}})
        logging.info("Algorithm ID updated successfully!")
        return ('Algorithm ID updated successfully!')
    
    @staticmethod
    def getAlgorithms(customer_id,dataset_id,status):
        #training_hist_tbl is a pymongo object to TblTraining
        predicted_fields_data = MongoDBPersistence.training_hist_tbl.find_one({"CustomerID": customer_id,\
                "DatasetID":dataset_id, "TrainingStatus": status},{"PredictedFields":1,"_id":0})
                
        if(predicted_fields_data):
            logging.info(f"predicted_fields_data: {predicted_fields_data}")
            logging.info('%s: Retrieving PredictedFields.'%RestService.timestamp())
            resp = json_util.dumps(predicted_fields_data)
        else:
            logging.info('%s: PredictedFields not found, returning empty response.'%RestService.timestamp())
            resp = ''
        return resp
    
    @staticmethod
    def getChosenAlgorithms( customer_id,dataset_id,status):
        result = {}

        o_fieldselection_list =  MongoDBPersistence.datasets_tbl.find_one({'CustomerID': customer_id, "DatasetID":dataset_id},{'FieldSelections':1, '_id':0})
        if(o_fieldselection_list):
            o_fieldselection_list = o_fieldselection_list['FieldSelections']
            n_fieldselection_list = o_fieldselection_list
            for fieldselection_dict in o_fieldselection_list:
                if(fieldselection_dict['FieldsStatus']==status):
                    result['PredictedFields'] = fieldselection_dict['PredictedFields']
        else:
            logging.info('%s: FieldSelections not found for a customer (CustomerID: %d).'%(RestService.timestamp(),customer_id))
        if(result):
            resp = json_util.dumps(result)
        else:
            logging.info('%s: PredictedFields not found, returning empty response.'%RestService.timestamp())
            resp = ""
        return resp

    @staticmethod
    def getDropdownParams(algorithm_name):
        dropdownValues = {}
        dropdownValues = MongoDBPersistence.algo_tbl.find_one({"AlgorithmName" : algorithm_name},{"_id":0, "DropdownParams":1})
        if(dropdownValues):
            result = dropdownValues['DropdownParams']
        else:
            logging.info("There are no dropdown values")
            result = 'There are no dropdown values'
        return json_util.dumps(result) 