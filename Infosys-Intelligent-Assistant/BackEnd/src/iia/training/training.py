__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

import os
import csv
import re
import importlib
import pandas as pd
import numpy as np
import datetime 
from iia.incident.incidenttraining import IncidentTraining
from iia.masterdata.datasets import DatasetMasterData
from iia.masterdata.customers import CustomerMasterData
import requests
from iia.persistence.mongodbpersistence import MongoDBPersistence
from iia.persistence.mappingpersistence import MappingPersistence
from iia.persistence.csvpersistence import CSVPersistence
from iia.recommendation.recommendationmodel import Recommendation
from iia.restservice import RestService
from iia.utils.utils import Utils

from hyperopt import hp, fmin, rand, tpe, space_eval
from sklearn.model_selection import  GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression  
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from xgboost import XGBClassifier
from sklearn.pipeline import make_pipeline
import joblib
from datetime import date,datetime
from bson import json_util
from flask import request, jsonify
import pandas as pd
from textblob import TextBlob
from collections import defaultdict
from collections import Counter
import json
import csv
from flask import make_response
from itertools import islice
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from iia.utils.log_helper import get_logger, log_setup
logging = get_logger(__name__)

app = RestService.getApp()

@app.route("/api/algoConfiguration/<int:customer_id>/<int:dataset_id>/<status>", methods=['GET'])
def algoConfiguration(customer_id, dataset_id, status):
    return Training.algoConfiguration(customer_id, dataset_id, status)
    
@app.route("/api/train/<int:customer_id>/<int:dataset_id>", methods=['POST'])
def train(customer_id,dataset_id):
    return Training.train(customer_id, dataset_id)
    
@app.route("/api/moveToTrainingData/<int:customer_id>/<int:dataset_id>",methods=["POST"])
def moveToTrainingData(customer_id, dataset_id):
    return Training.moveToTrainingData(customer_id, dataset_id)

@app.route("/api/updateTrainingStatus/<int:customer_id>/<status>",methods=["PUT"])   #Try Once soma is able to pass TrainingID from Angular
def update_status(customer_id,status):
    return Training.update_status(customer_id, status)

# wrapper methods for stopwords module
@app.route('/api/displayGraph/<int:customer_id>/<int:dataset_id>/<predicted_field>', methods=["GET"])
def displayGraph(customer_id,dataset_id,predicted_field):
    return Training.displayGraph(customer_id,dataset_id,predicted_field)

#Code for word cloud - Adding new stop words
@app.route('/api/saveStopWords/<int:customer_id>/<int:dataset_id>',methods = ['PUT'])
def saveStopWords(customer_id, dataset_id):
    return Training.saveStopWords(customer_id, dataset_id)

# code for getting json for Wordcloud
#returns a unigram json
@app.route('/api/displayWordCloud/<int:customer_id>/<int:dataset_id>/<predictedfield>/<path:sub_field>/<int:number_of_words>/<cloud_type>', methods = ['GET'])
def displayWordCloud(customer_id, dataset_id, predictedfield,sub_field,number_of_words,cloud_type):
    return Training.displayWordCloud(customer_id, dataset_id, predictedfield,sub_field,number_of_words,cloud_type)

#returns a list of stopwords to be displayed
@app.route('/api/displayStopWords/<int:customer_id>/<int:dataset_id>',methods=['GET'])
def displayStopWords(customer_id,dataset_id):
    return Training.displayStopWords(customer_id,dataset_id)

# remove a clicked stopword
@app.route('/api/removeStopWords/<int:customer_id>/<int:dataset_id>/<word>', methods=['GET'])
def removeStopWords(customer_id,dataset_id,word):
    return Training.removeStopWords(customer_id,dataset_id,word)

# get classification reoport
@app.route('/api/getClassificationReport/<int:customer_id>/<int:dataset_id>/<predicted_field>/<algorithm>/<training_status>',methods=['GET'])
def getClassificationReport(customer_id, dataset_id, predicted_field, algorithm, training_status):
    return Training.getClassificationReport(customer_id, dataset_id, predicted_field, algorithm, training_status)

#Get status of all daemon training processes for the customer
@app.route('/api/getTrainingState/<int:customer_id>', methods=['GET'])
def getTrainingState(customer_id):
    return Training.getTrainingState(customer_id)

@app.route('/api/updateWhiteListWords/<int:customer_id>/<int:dataset_id>/<predicted_field>', methods=['PUT','POST'])
def updateWhiteListWords(customer_id, dataset_id, predicted_field):
    return Training.updateWhiteListWords(customer_id, dataset_id, predicted_field)

@app.route('/api/getWhiteListWords/<int:customer_id>/<int:dataset_id>/<predicted_field>',methods=['GET'])
def getWhiteListWords(customer_id,dataset_id,predicted_field):
    return Training.getWhiteListWords(customer_id,dataset_id,predicted_field)

@app.route('/api/deleteWhiteListWords/<int:customer_id>/<int:dataset_id>/<predicted_field>/<path:field_name>/<word>', methods = ['DELETE'])
def deleteWhiteListWords(customer_id, dataset_id, predicted_field, field_name, word):
    return Training.deleteWhiteListWords(customer_id, dataset_id, predicted_field, field_name, word)

@app.route('/api/getWordCloudList/<int:customer_id>/<int:dataset_id>/<predicted_field>/<number_of_words>/<cloud_type>',methods =['GET'])
def getWordCloudList(customer_id,dataset_id,predicted_field,number_of_words,cloud_type):
    return Training.getWordCloudList(customer_id,dataset_id,predicted_field,number_of_words,cloud_type)

@app.route('/api/categoryname/<int:customer_id>/<int:dataset_id>',methods=['GET'])
def getAllCategories(customer_id,dataset_id):
    return Training.getAllCategories(customer_id,dataset_id)

@app.route('/api/barcategoryname/<int:customer_id>/<int:dataset_id>',methods=['GET'])
def getBarCategoryList(customer_id,dataset_id):
    return Training.getBarCategoryList(customer_id,dataset_id)

@app.route('/api/piecategoryname/<int:customer_id>/<int:dataset_id>',methods=['GET'])
def getPieCategoryList(customer_id,dataset_id):
    return Training.getPieCategoryList(customer_id,dataset_id)

@app.route('/api/PMAdisplayGraph/<int:customer_id>/<int:dataset_id>/<selected_field>/<string:year>/<string:month>',methods=['GET'])
def displayGraph_PMA(customer_id,dataset_id,selected_field,year,month):
    return Training.displayGraph_PMA(customer_id,dataset_id,selected_field,year,month)

@app.route('/api/donutPMAdisplayGraph/<int:customer_id>/<int:dataset_id>/<selected_field>/<ag>/<string:unassigned_value>',methods=['GET'])
def displayGraph_donutPMA(customer_id,dataset_id,selected_field,ag,unassigned_value):
    return Training.displayGraph_donutPMA(customer_id,dataset_id,selected_field,ag,unassigned_value)

@app.route('/api/displayLineGraphPMA/<int:customer_id>/<int:dataset_id>/<from_year>/<to_year>',methods=['GET'])  #need to send months from and upto by getting from font end 
def displaylineGraph_PMA(customer_id,dataset_id,from_year,to_year):
    return Training.displaylineGraph_PMA(customer_id,dataset_id,from_year,to_year)

@app.route('/api/PMAdisplayWordCloud/<int:customer_id>/<int:dataset_id>/<selectedfield>/<string:field_value>/<string:unassigned_value>/<int:number_of_words>/<cloud_type>',methods=['GET'])
def displayWordCloud_PMA(customer_id, dataset_id, selectedfield,field_value,unassigned_value,number_of_words,cloud_type):
    return Training.displayWordCloud_PMA(customer_id, dataset_id, selectedfield,field_value,unassigned_value,number_of_words,cloud_type)
   
@app.route('/api/getSourceTargetColumns',methods=['GET'])
def getSourceTargetColumns():
    return Training.getSourceTargetColumns()

@app.route('/api/updatePMATargetColumns',methods=['POST'])
def updatePMATargetColumns():
    return Training.updatePMATargetColumns()

class Training(object):
    '''
    classdocs
    '''

    def __init__(self, params):
        '''
        Constructor
        '''
    @staticmethod
    def getTrainingState(customer_id):
        ()
        training_status_list = list(MongoDBPersistence.datasets_tbl.find( {'CustomerID': customer_id, "$or": [ { "TrainingStatus.TrainingCompletedFlag" : "InProgress" }, { "TrainingStatus.TrainingCompletedFlag" : "Completed" } ] }, {'DatasetID':1,'TrainingStatus':1, '_id':0}))
        if(training_status_list):
            return json_util.dumps(training_status_list)
        else:
            logging.info("No past daemon training process to show..")
            return json_util.dumps('empty')

    @staticmethod
    def clean_TblTraining(customer_id,dataset_id,status):
        """
            A function to clean training history with the given status(InProgress/Approved/Retraining)
            It also cleans up corresponding machine learning models (.pkl files)

            Parameters
            ----------
            :param customer_id: Customer ID 
            :param dataset_id: Dataset ID 
            :param status: Status record which will get cleaned from TblTraining

            Returns
            -------
            :return: response message (success/failure)

            Created by
            ----------
                        
            Last changed by
            ---------------
        """
        try:       
            customer_name = MongoDBPersistence.customer_tbl.find_one({'CustomerID':customer_id},{'CustomerName':1, '_id':0})['CustomerName']
            dataset_name = MongoDBPersistence.datasets_tbl.find_one({'CustomerID':customer_id,"DatasetID" : dataset_id},{'DatasetName':1, '_id':0})['DatasetName']
            MongoDBPersistence.training_hist_tbl.delete_many({'CustomerID':customer_id,"TrainingStatus" : status,"DatasetID":dataset_id})
            for filename in os.listdir("models"):
                file_list = filename.split('__')
                if(customer_name in file_list):
                    if(dataset_name in file_list):
                        if(status in filename.split('__')):
                            os.remove("models/"+filename)
            for filename in os.listdir("data"):
                file_list = filename.split('__')
                if(customer_name in file_list):
                    if(dataset_name in file_list):
                        if(status in filename.split('__')):
                            os.remove("data/"+filename)
            resp = 'success'
        except:
            resp = 'failure'
        return resp


    @staticmethod
    def algoConfiguration(customer_id, dataset_id, status):  #Status will be eigher Tuning/Default
        ()
        #If Tuning: Make Tuned accuracies as InProgress & Delete default one... Also make same changes to pkl files
        #If Default: Let Default accuracies untouched as InProgress & Delete Tuned one... Also make same changes to pkl files
        #While making thease changes, dont touch Approved ones
        dataset_name =  MongoDBPersistence.datasets_tbl.find_one({'CustomerID':customer_id,"DatasetID":dataset_id},{'DatasetName':1,'_id':0})
        customer_name = MongoDBPersistence.customer_tbl.find_one({'CustomerID':customer_id},{'CustomerName':1, '_id':0})
        #()
        #Unset state management parameters #abort-2
        DatasetMasterData.updateDaemonTraining(customer_id,dataset_id, "Ignore", 0, '')
        if(dataset_name):
            customer_name = customer_name["CustomerName"]
            dataset_name = dataset_name["DatasetName"]
            if(status=="Tuning"):
                #Update Training status
                #Recieving last training ID to update TblTraining
                #Update both the statuses in TblCustomer & TblTraining

                stopwords_list = MongoDBPersistence.datasets_tbl.find_one({"CustomerID": customer_id,"DatasetID": dataset_id},{"Stopwords":1,"_id":0})
                if stopwords_list:
                    inprogress_stopwords = stopwords_list['Stopwords'][0]['stopword']
                    approved_stopwords = stopwords_list['Stopwords'][1]['stopword']
                    for word in inprogress_stopwords:
                        if word not in approved_stopwords:
                            approved_stopwords.append(word)
                    try:
                        MongoDBPersistence.datasets_tbl.update_one({"$and":[{"DatasetID": dataset_id},{"CustomerID": customer_id}]},
                                                {"$set": {"Stopwords": [{"stopword": [],"Status": 'InProgress'},
                                                {"stopword": approved_stopwords, "Status": 'Approved'}]}}, upsert=False)
                    except Exception as e:
                        logging.info('%s: Error occured in updating the database'%(RestService.timestamp()))
                else:
                    logging.info('%s: There were no previous stopwords....'%(RestService.timestamp()))

                try:
                    #Make all InProgress to Archieved
                    MongoDBPersistence.training_hist_tbl.update_one({'CustomerID':customer_id,"DatasetID" : dataset_id,"TrainingStatus" : "InProgress"}, {"$set": {"TrainingStatus":"Archived"}}, upsert=False)

                    #Make Tuning as inProgress
                    MongoDBPersistence.training_hist_tbl.update_one({'CustomerID':customer_id,"DatasetID" : dataset_id,"TrainingStatus" : "Tuning"}, {"$set": {"TrainingStatus":"InProgress"}}, upsert=False)
                    logging.info('%s: Updated: TblTraining'%RestService.timestamp())
                    resp = 'success'
                except Exception as e:
                    logging.error('%s: Error occurred: %s '%(RestService.timestamp(),str(e)))
                    resp = 'failure'
                #move previous "InProgress" to "Archived" pkls
                for filename in os.listdir("models"):
                    file_list = filename.split('__')
                    if(customer_name in file_list):
                        if(dataset_name in file_list):
                            if('InProgress' in filename.split('__')):
                                os.remove("models/"+filename)
                
                for filename in os.listdir("data"):
                    file_list = filename.split('__')
                    if(customer_name in file_list):
                        if(dataset_name in file_list):
                            if('InProgress' in filename.split('__')):
                                #remove previous accepted
                                os.remove("data/"+filename)
                
                #Make tuned one "InProgress"
                for filename in os.listdir("models"):
                    file_list = filename.split('__')
                    if(customer_name in file_list):
                        if(dataset_name in file_list):
                            if('Tuning' in filename.split('__')):
                                n_filename = filename.replace("Tuning","InProgress")
                                os.rename("models/"+filename,"models/"+n_filename)
                for filename in os.listdir("data"):
                    file_list = filename.split('__')
                    if(customer_name in file_list):
                        if(dataset_name in file_list):
                            if('Tuning' in filename.split('__')):
                                n_filename = filename.replace("Tuning","InProgress")
                                os.rename("data/"+filename,"data/"+n_filename)
                logging.info('%s: moved previous "InProgress" to "Archived" pkls & mking current Tuning as Approved.'%RestService.timestamp())
                
            elif(status=="Default"):
                #Update Training status
                MongoDBPersistence.training_hist_tbl.update_many({'CustomerID':customer_id,"DatasetID" : dataset_id,"TrainingStatus" : "Tuning"}, {"$set": {"TrainingStatus":"Archived"}}, upsert=False)

                #As training status remains Tuning, it will get deleted next time...no need of this step.. previous Tuning & InProgress pickle files get removed before train
                #remove pkl files with Tuning status
                for filename in os.listdir("models"):
                    file_list = filename.split('__')
                    if(customer_name in file_list):
                        if(dataset_name in file_list):
                            if("Tuning" in file_list):
                                os.remove("models/"+filename)
                for filename in os.listdir("data"):
                    file_list = filename.split('__')
                    if(customer_name in file_list):
                        if(dataset_name in file_list):
                            if("Tuning" in file_list):
                                os.remove("data/"+filename)
                logging.info('%s: Pickle files for algo Tuning deleted successfully.'%RestService.timestamp())
                resp = 'success'

                stopwords_list = MongoDBPersistence.datasets_tbl.find_one({"CustomerID": customer_id,"DatasetID": dataset_id},{"Stopwords":1,"_id":0})
                if stopwords_list:
                    approved_stopwords = stopwords_list['Stopwords'][1]['stopword']
                    MongoDBPersistence.datasets_tbl.update_one({"$and":[{"DatasetID": dataset_id},{"CustomerID": customer_id}]},
                                            {"$set": {"Stopwords": [{"stopword": [],"Status": 'InProgress'},
                                            {"stopword": approved_stopwords, "Status": 'Approved'}]}}, upsert=False)
                    print("deleting Inprogress stopwords")
                else:
                    logging.info('%s: No previous stopwords were found.'%(RestService.timestamp()))

            else:
                resp = 'failure'

        else:
            logging.info('%s: No dataset found..'%RestService.timestamp())
            resp = 'failure'

        return json_util.dumps(resp)


    #Time complexity= O(n^2)  -- Need to be reduced later
    @staticmethod
    def train(customer_id, dataset_id):
        # Get User parameters JSON
        ()
        user_param_choices = {}
        field_to_insert={}
        user_param_choices = request.get_json()
        custom_train_flag, custom_url = CustomerMasterData.check_custom("customTraining")
        if (custom_train_flag=='failure'):
            logging.info("%s: Not able to read values from Configure File"%RestService.timestamp())
            return "failure"

        elif (custom_train_flag=="True"):

            logging.info("%s Custom training is present invoking Custom Training"%RestService.timestamp())
            api = custom_url + "api/custom_train/"+str(customer_id) + "/"+str(dataset_id)  # customer id hardcoded
            print("-----------",api)
            proxies = {"http": None,"https": None}
            req_head = { "Content-Type": "application/json"}
            post_data = {'Status' : user_param_choices['Status']}
            print("--------post data",post_data)
            req_res = requests.post(api,headers = req_head,data=json.dumps(post_data), proxies=proxies)
            print("---Custom files executed succesfully", req_res)
            return json_util.dumps(req_res)

        else:

            if (user_param_choices['Status'] == "Train"):
                training_status = "InProgress"
                
                approved_algoparam = MongoDBPersistence.training_hist_tbl.find_one(
                    {"CustomerID": customer_id, "DatasetID": dataset_id, "TrainingStatus": "Approved"},
                    {"_id": 0, "AlgorithmParameters": 1})
                if (approved_algoparam):
                    user_param_choices['Algorithms'] = approved_algoparam['AlgorithmParameters']
                    logging.info("picking up last Approved parameters as default parameters.")
                else:
                    default_algo_params = list(
                        MongoDBPersistence.algo_tbl.find({}, {'AlgorithmName': 1, 'DefaultParametersSingle': 1, "_id": 0}))
                    if (not default_algo_params):
                        logging.info("Algorithms not found...Please add the algorithms.")
                        return 'failure'
                    user_param_choices = {}
                    user_param_choices['Status'] = "Train"
                    alorithms = []
                    for algo in default_algo_params:
                        tmp = {}
                        tmp['Parameters'] = algo['DefaultParametersSingle']
                        tmp['AlgorithmName'] = algo['AlgorithmName']
                        tmp['ParameterType'] = "Single"
                        alorithms.append(tmp)
                    user_param_choices['Algorithms'] = alorithms
            elif (user_param_choices['Status'] == "Tune"):
                training_status = "Tuning"
                if (not user_param_choices['Algorithms']):
                    logging.info("Please submit all algorithm parameters.")
                    return 'failure'
            else:
                logging.info("Training status not found.. Tune/Train")

            # Check if training data available for the customer (Does not make any sense to check this, as user cant see train button before uploading dataset.)

            # Getting last training id for the customer : Possible exception (NoneType is returned from DB.. if record missing for customer_id)
            last_training_dict = MongoDBPersistence.training_hist_tbl.find_one(
                {"CustomerID": customer_id, "DatasetID": dataset_id, "TrainingID": {"$exists": True}},
                {'_id': 0, "TrainingID": 1}, sort=[("TrainingID", -1)])
            if (last_training_dict):
                last_training_id = last_training_dict['TrainingID']
            else:
                last_training_id = 0
                # It should be non-Registered Customer
                logging.info(
                    '%s: First time user access detected to train module, Please register us if not registerd.' % RestService.timestamp())

            # New training id for the customer
            training_id = last_training_id + 1

            # Preparing a Row data to be inserted into Tbltraining :tbl_training_row
            tbl_training_row = {}
            tbl_training_row['TrainingID'] = training_id
            tbl_training_row["TrainingStatus"] = training_status
            tbl_training_row["CustomerID"] = customer_id
            tbl_training_row["DatasetID"] = dataset_id
            tbl_training_row["LastTrainingBy"] = os.getlogin()
            today = str(datetime.now())
            tbl_training_row["LastTrainingDate"] = today[:19]

            cust_name_dict = MongoDBPersistence.customer_tbl.find_one({'CustomerID': customer_id}, {'CustomerName': 1, '_id': 0})
            if (cust_name_dict):
                cust_name = cust_name_dict['CustomerName']
            else:
                logging.info('%s: Customer not found in the record.' % RestService.timestamp())
            # Getting dataset details
            dataset_info_dict = MongoDBPersistence.datasets_tbl.find_one({'CustomerID': customer_id, "DatasetID": dataset_id},
                                                    {'DatasetName': 1, 'FieldSelections': 1, '_id': 0})
            if (dataset_info_dict):
                dataset_name = dataset_info_dict['DatasetName']
            else:
                logging.info('%s: Dataset not found in the record.' % RestService.timestamp())
            # Fetch list of all algos that are supported : algo_list
            algo_listOfDicts = list(MongoDBPersistence.algo_tbl.find({}, {'_id': 0, 'AlgorithmName': 1}))
            algo_list = []
            if (algo_listOfDicts):
                for algo in algo_listOfDicts:
                    algo_list.append(algo['AlgorithmName'])
            else:
                logging.info(
                    '%s: Algorithms not found.. Please add any of RandomForestClassifier/LogisticRegression/MultinomialNB/SVC to TblAlgorithm.' % RestService.timestamp())
            # get predicted fields from TblCustomer
            fieldselection_list = dataset_info_dict['FieldSelections']
            logging.info(f"fieldselection_list:{fieldselection_list}")
            # train will pickup i/o choices from TblCustomer which status is InProgress
            pred_list = []
            for pred_fields in fieldselection_list:
                if (pred_fields['FieldsStatus'] == 'InProgress' or pred_fields['FieldsStatus']=='Approved'): 
                    pred_list = pred_fields['PredictedFields']
            logging.info(f"pred_list:{pred_list}")
            if (len(pred_list) == 0):
                logging.info("%s: Failure: Customer didn't choose any fields." % RestService.timestamp())
                return 'failure'
            pred_field_list = []
            for pre_field in pred_list:
                pred_field_list.append(pre_field['PredictedFieldName'])
            predicted_fields_data = []
            additional_fields = pred_list[0]['Additionalfields']
            # Clean previous InProgress/Tuning records
            Training.clean_TblTraining(customer_id, dataset_id, training_status)
            today = str(datetime.now())
            completed_status = 0
            DatasetMasterData.updateDaemonTraining(customer_id,dataset_id , "InProgress", completed_status, today[:19])        
            if(training_status == "Tuning"):
                completed_factor = 100.0/(5 * len(pred_field_list))
            else:
                completed_factor = 100.0/(4 * len(pred_field_list))
            final_score_list = []
            for pred_field in pred_field_list:
                pred_field_dict = {}
                pred_field_dict["Name"] = pred_field
                # Based on each prediction field, get all corelated fields appended in a single field(Say in_field)
                # Use feature selection algorithms to select best fields from training dataset
                input_field_list = []
                for input_field in pred_list:
                    if (input_field['PredictedFieldName'] == pred_field):
                        input_field_list = input_field['InputFields']
                if (len(input_field_list) == 0):
                    logging.info('%s: No input fields choosen for %s.' % (RestService.timestamp(), pred_field))
                    continue
                # Concatinating input fields together into in_field
                select_doc={'_id': 0, input_field_list[0]: 1}
                logging.info(f"select_doc:{select_doc}")
                additional_doc = {'_id': 0}
                Column_names = MongoDBPersistence.datasets_tbl.find_one({'CustomerID': customer_id, "DatasetID": dataset_id},
                                                    {'ColumnNames': 1, '_id': 0})
                all_fields =  Column_names['ColumnNames']                        
                print("all_fields:" ,all_fields)
                if additional_fields:
                    for each_field in additional_fields:
                        additional_doc.update({each_field:1})
                else:
                    for each_field in all_fields:
                        additional_doc.update({each_field:0})
                logging.info(f"additional_doc:{additional_doc}")

                input_df = pd.DataFrame()
                input_df = pd.DataFrame(list(MongoDBPersistence.training_tickets_tbl.find({'CustomerID': customer_id, "DatasetID": dataset_id},
                                                                    select_doc)))  #,pred_field:{"$exists":True,"$ne": ""}
                
                additional_df = pd.DataFrame()
                additional_df = pd.DataFrame(list(MongoDBPersistence.training_tickets_tbl.find({'CustomerID': customer_id, "DatasetID": dataset_id},
                                                                    additional_doc)))  #,pred_field:{"$exists":True,"$ne": ""}

                list_addtional_fields = list(additional_df.columns)
                logging.info(f"additional_df: {additional_df.head()}")
                logging.info(f"input_df: {input_df.head()}")
                for input_field_ in input_field_list[1:]:
                    input_df[input_field_] = pd.DataFrame(list(
                        MongoDBPersistence.training_tickets_tbl.find({'CustomerID': customer_id, "DatasetID": dataset_id},
                                                {'_id': 0, input_field_: 1})))

                input_df['in_field'] = ''
                for field in input_field_list:
                    if(input_df[field] is None):
                        input_df[field] = ""
                    input_df['in_field'] += input_df[field] + ' --~||~-- '
                input_df1 = pd.DataFrame()
                input_df1['in_field'] = input_df['in_field']

                in_field = 'in_field'
                training_tkt_df = pd.DataFrame(list(
                    MongoDBPersistence.training_tickets_tbl.find({'CustomerID': customer_id, "DatasetID": dataset_id},
                                            {'_id': 0, pred_field: 1})))

                training_tkt_df[in_field] = input_df1
                for each in list_addtional_fields:
                    training_tkt_df[each] = additional_df[each]
                logging.info(f"training_tkt_df: {training_tkt_df.columns}")

                # Skips those tickets where there is no description field
                logging.info('%s: Number of columns before cleaning: %d.' % (RestService.timestamp(), training_tkt_df.shape[0]))
                training_tkt_df = training_tkt_df[(training_tkt_df[in_field]!="")]
                training_tkt_df = training_tkt_df[(training_tkt_df[pred_field]!="")]
                training_tkt_df = training_tkt_df.dropna(how='any', axis=0)  # IMP step
                logging.info('%s: Number of columns after cleaning: %d.' % (RestService.timestamp(), training_tkt_df.shape[0]))

            
                #######calling an api request for custom preprocessing file ################
                custom_processing_flag, custom_url = CustomerMasterData.check_custom("customPreprocessing")
                if (custom_processing_flag=='failure'):
                    logging.info("%s: Not able to read values from Configure File"%RestService.timestamp())
                    return "failure"

                elif (custom_processing_flag=="True"):
                    try:
                        logging.info("%s Custom processing is present invoking Custom preprocessing "%RestService.timestamp())
                        req_head = { "Content-Type": "application/json"}
                        post_data = {"CustomerID": customer_id,"data":training_tkt_df}
                        proxies = {"http": None,"https": None}
                        api = custom_url + "api/custom_preprocessing"
                        req_response = requests.post(api,data=json_util.dumps(post_data),headers = req_head,proxies=proxies)
                        training_tkt_df = pd.DataFrame.from_dict(req_response.json(),orient="columns")
                    except Exception as e:
                        training_tkt_df = IncidentTraining.cleaningInputFields(training_tkt_df,in_field)
                else:
                    training_tkt_df = IncidentTraining.cleaningInputFields(training_tkt_df,in_field)

                training_tkt_df['category_id'] = training_tkt_df[pred_field].factorize()[0]
                # Mapping labels with integers
                category_id_df = training_tkt_df[[pred_field, 'category_id']].drop_duplicates().sort_values('category_id')
                
                id_to_category = dict(category_id_df[['category_id', pred_field]].values)
                id_to_category = {str(key):str(value) for key, value in id_to_category.items()}            
                field_to_insert[pred_field]=id_to_category

                ##needs to be modified later , find query which appends in existed column
                MongoDBPersistence.datasets_tbl.update_one({'CustomerID':customer_id, "DatasetID": dataset_id}, {"$set": {"IdToLabels":field_to_insert}}, upsert=True)

                model = Utils(training_tkt_df, customer_id, dataset_id, pred_field, in_field, training_status,list_addtional_fields)
                tpe_algo = tpe.suggest

                # Training the models using all available algorithms
                algorithms_data = []
                algorithms_params = []
            
                print(user_param_choices)
                if (len(set(training_tkt_df['category_id'])) > 1):
                    for algo in user_param_choices['Algorithms']:
                        algo_dict = {}
                        score_dict = {}
                        algo_param_dict = {}
                        algo_name = algo['AlgorithmName']
                        algo_param_dict['AlgorithmName'] = algo_name
                        algo_param_dict['ParameterType'] = "Single"
                        if (user_param_choices['Status']=='Tune' and algo_name == 'XGBClassifier'):
                            if (algo['ParameterType'] == "Multiple"):
                                # Use Grid Search CV
                                parameters = algo['Parameters']
                                param_grid = {}
                                objective = 0
                                n_estimators = 0
                                possible_objective = ["binary:logistic", "multi:softprob"]
                                for parameter in parameters:
                                    if (parameter["ParameterName"] == 'n_estimators'):
                                        n_estimators = parameter['Value']
                                    elif (parameter["ParameterName"] == 'objective'):
                                        objective = parameter['Value']
                                if(objective):
                                    if(objective == 'auto'):
                                        param_grid['objective'] = possible_objective
                                    else:
                                        param_grid['objective'] = [objective]
                                else:
                                    logging.info('%s: objective range parameter value missing/cannot be null. taking default values'%(RestService.timestamp()))
                                    param_grid['objective'] = ['binary:logistic']

                                if(n_estimators):
                                    try:
                                        tree_start = int(n_estimators[0])
                                        tree_end = int(n_estimators[1])
                                        tree_evals  = int(n_estimators[2])
                                    except Exception as e:
                                        logging.error('%s: Error occurred: %s '%(RestService.timestamp(),str(e)))
                                        logging.info('%s: Exception catched. taking default as n_estimators'%(RestService.timestamp()))
                                        tree_start = int(n_estimators[0])
                                        tree_end = int(n_estimators[1])
                                        tree_evals  = int(n_estimators[2])
                                    
                                else:
                                    logging.info('%s: n_estimators range parameter value missing/cannot be zero. taking default'%(RestService.timestamp()))
                                    tree_start = int(n_estimators[0])
                                    tree_end = int(n_estimators[1])
                                    tree_evals  = int(n_estimators[2])
                                
                                xgb_space = [hp.quniform('n_estimators', tree_start, tree_end,1), hp.choice('objective', param_grid['objective'])]
                                xgb_tpe_best = fmin(model.XGBClassifierObjective, xgb_space, algo=tpe_algo,max_evals=tree_evals)

                                logging.info('%s: Started training with %s algorithm.' % (RestService.timestamp(), algo_name))
                                score_dict = model.classify(model=XGBClassifier(n_estimators=int(xgb_tpe_best['n_estimators']),objective=possible_objective[xgb_tpe_best['objective']]))

                                logging.info('%s: Model has been trained successfully using %s algorithm.' % (RestService.timestamp(), algo_name))
                                
                                xgb_tpe_best['objective'] = possible_objective[xgb_tpe_best['objective']]
                                params = []
                                for key, value in xgb_tpe_best.items(): 
                                    tmp_dict = {}
                                    tmp_dict['ParameterName'] = key
                                    tmp_dict['Value'] = value
                                    params.append(tmp_dict)
                                algo_param_dict['Parameters'] = params
                            elif (algo['ParameterType'] == "Single"):
                                parameters = algo['Parameters']
                                algo_param_dict['Parameters'] = parameters
                                param_grid = {}
                                for parameter in parameters:
                                    if (parameter["ParameterName"] == 'n_estimators'):
                                        param_grid['n_estimators'] = int(parameter['Value'])
                                    elif (parameter["ParameterName"] == 'objective'):
                                        param_grid['objective'] = parameter['Value']
                                    # Check whether we got n_estimators, objective
                                logging.info('%s: Started training with %s algorithm.' % (RestService.timestamp(), algo_name))
                                score_dict = model.classify(model=XGBClassifier(n_estimators=param_grid['n_estimators'],objective=param_grid['objective']))
                                
                                logging.info('%s: Model has been trained successfully using %s algorithm.' % (RestService.timestamp(), algo_name))

                            else:
                                logging.info('%s: Specify parameter type. Single/Multiple' % (RestService.timestamp(), algo_name))
                                
                                parameters = algo['Parameters']

                        elif (algo_name == 'RandomForestClassifier'):
                            if (algo['ParameterType'] == "Multiple"):
                                parameters = algo['Parameters']
                                
                                param_grid = {}
                                n_estimators = 0
                                max_depth = None
                                criterion = ''
                                possible_criterion = ["gini","entropy"]
                                for parameter in parameters:
                                    if (parameter["ParameterName"] == 'n_estimators'):
                                        n_estimators = parameter['Value']
                                    elif (parameter["ParameterName"] == 'max_depth' and (not parameter["Value"] == "None")):
                                        max_depth = parameter['Value']
                                    elif (parameter["ParameterName"] == 'max_depth' and (parameter["Value"] == "None")):
                                        max_depth = None
                                    elif (parameter["ParameterName"] == 'criterion'):
                                        criterion = parameter['Value']
                                if(criterion):
                                    if(criterion == 'auto'):
                                        param_grid['criterion'] = possible_criterion
                                    else:
                                        param_grid['criterion'] = [criterion]
                                else:
                                    logging.info('%s: criterion range parameter value missing/cannot be null. taking default values as criterion = gini'%(RestService.timestamp()))
                                    param_grid['criterion'] = ['gini']

                                if(n_estimators):
                                    try:
                                        tree_start = int(n_estimators[0])
                                        tree_end = int(n_estimators[1])
                                        tree_evals  = int(n_estimators[2])
                                    except Exception as e:
                                        logging.error('%s: Error occurred: %s '%(RestService.timestamp(),str(e)))
                                        logging.info('%s: Exception catched. taking default as n_estimators'%(RestService.timestamp()))
                                        tree_start = 10
                                        tree_end = 200
                                        tree_evals  = 5
                                    
                                else:
                                    logging.info('%s: n_estimators range parameter value missing/cannot be zero. taking default as n_estimators '%(RestService.timestamp()))
                                    tree_start = 10
                                    tree_end = 200
                                    tree_evals  = 5
                                if(max_depth):
                                    param_grid['max_depth'] = [int(max_depth)]
                                else:
                                    param_grid['max_depth'] = [None]
                                rf_space = [hp.quniform('n_estimators', tree_start, tree_end, 1), hp.choice('max_depth', param_grid['max_depth']),hp.choice('criterion', param_grid['criterion'])]
                                rf_tpe_best = fmin(model.RFClassifierObjective, rf_space, algo=tpe_algo,max_evals=tree_evals)
                                print(rf_tpe_best)
                                logging.info('%s: Started training with %s algorithm.' % (RestService.timestamp(), algo_name))
                                score_dict = model.classify(
                                    model=RandomForestClassifier(n_estimators=int(rf_tpe_best['n_estimators']),
                                                                    criterion=possible_criterion[rf_tpe_best['criterion']],
                                                                    max_depth=param_grid['max_depth'][0]))
                                logging.info('%s: Model has been trained successfully using %s algorithm.' % (RestService.timestamp(), algo_name))
                                # Store best parameters to use it as default next time
                                rf_tpe_best['criterion'] = possible_criterion[rf_tpe_best['criterion']]
                                rf_tpe_best['max_depth'] = int(param_grid['max_depth'][0])
                                params = []
                                for key, value in rf_tpe_best.items(): 
                                    tmp_dict = {}
                                    tmp_dict['ParameterName'] = key
                                    tmp_dict['Value'] = value
                                    params.append(tmp_dict)
                                algo_param_dict['Parameters'] = params
                            elif (algo['ParameterType'] == "Single"):
                                parameters = algo['Parameters']
                                algo_param_dict['Parameters'] = parameters
                                param_grid = {}
                                for parameter in parameters:
                                    if (parameter["ParameterName"] == 'n_estimators'):
                                        param_grid['n_estimators'] = int(parameter['Value'])
                                    elif (parameter["ParameterName"] == 'criterion'):
                                        param_grid['criterion'] = parameter['Value']
                                    elif (parameter["ParameterName"] == 'max_depth' and (not parameter["Value"] == "None")):
                                        param_grid['max_depth'] = int(parameter['Value'])
                                    elif (parameter["ParameterName"] == 'max_depth' and (parameter["Value"] == "None")):
                                        param_grid['max_depth'] = None
                                logging.info('%s: Started training with %s algorithm.' % (RestService.timestamp(), algo_name))
                                # Check whether we got n_estimators, criterion, max_depth values
                                score_dict = model.classify(
                                    model=RandomForestClassifier(n_estimators=param_grid['n_estimators'],
                                                                    criterion=param_grid['criterion'],
                                                                    max_depth=param_grid['max_depth'],random_state=42))
                                logging.info('%s: Model has been trained successfully using %s algorithm.' % (RestService.timestamp(), algo_name))
                            else:
                                logging.info('%s: Specify parameter type. Single/Multiple' % (RestService.timestamp(), algo_name))
                        elif (algo_name == 'SVC'):
                            if (algo['ParameterType'] == "Multiple"):
                                # Use GridSearchCV
                                parameters = algo['Parameters']
                                param_grid = {}
                                kernel = ''
                                possible_kernel = ['linear', 'poly', 'rbf', 'sigmoid']
                                C_val = 0
                                for parameter in parameters:
                                    if (parameter["ParameterName"] == 'C'):
                                        C_val = parameter['Value']
                                    elif (parameter["ParameterName"] == 'kernel'):
                                        kernel = parameter['Value']
                                if(kernel):
                                    if (kernel == 'auto'):
                                        param_grid['kernel'] = possible_kernel
                                    else:
                                        param_grid['kernel'] = [kernel]
                                else:
                                    logging.info('%s: kernel parameter value missing/cannot be null. taking default values as kernel = rbf'%(RestService.timestamp()))
                                    param_grid['kernel'] = ['rbf']
                                if(C_val):
                                    try:
                                        c_start = C_val[0]
                                        c_end = C_val[1]
                                        c_evals  = C_val[2]
                                    except Exception as e:
                                        logging.error('%s: Error occurred: %s '%(RestService.timestamp(),str(e)))
                                        logging.info('%s: Exception catched. taking default C_val as C_val = [3.0].'%(RestService.timestamp()))
                                        c_start = 1
                                        c_end = 10
                                        c_evals  = 5
                                else:
                                    logging.info('%s: C_val range parameter value missing/cannot be zero. taking default C_val as C_val = [3.0]'%(RestService.timestamp()))
                                    c_start = 1
                                    c_end = 10
                                    c_evals  = 5
                                svc_space = [hp.uniform('C', c_start, c_end), hp.choice('kernel', param_grid['kernel'])]
                                svc_tpe_best = fmin(model.SVClassifierObjective, svc_space, algo=tpe_algo,max_evals=c_evals)
                                logging.info('%s: Started training with %s algorithm.' % (RestService.timestamp(), algo_name))
                                score_dict = model.classify(model=SVC(C=svc_tpe_best['C'], kernel=possible_kernel[svc_tpe_best['kernel']], probability=True))
                                logging.info('%s: Model has been trained successfully using %s algorithm.' % (RestService.timestamp(), algo_name))
                                # Store best parameters to use it as default next time
                                svc_tpe_best['kernel'] = possible_kernel[svc_tpe_best['kernel']]
                                params = []
                                for key, value in svc_tpe_best.items():
                                    tmp_dict = {}
                                    tmp_dict['ParameterName'] = key
                                    tmp_dict['Value'] = value
                                    params.append(tmp_dict)
                                algo_param_dict['Parameters'] = params
                            elif (algo['ParameterType'] == "Single"):
                                parameters = algo['Parameters']
                                algo_param_dict['Parameters'] = parameters
                                param_grid = {}
                                for parameter in parameters:
                                    if (parameter["ParameterName"] == 'C'):
                                        param_grid['C'] = parameter['Value']
                                    elif (parameter["ParameterName"] == 'kernel'):
                                        param_grid['kernel'] = parameter['Value']
                                logging.info('%s: Started training with %s algorithm.' % (RestService.timestamp(), algo_name))
                                score_dict = model.classify(
                                    model=SVC(C=param_grid['C'], kernel=param_grid['kernel'], probability=True))
                                logging.info('%s: Model has been trained successfully using %s algorithm.' % (
                                    RestService.timestamp(), algo_name))
                            else:
                                logging.info('%s: Specify parameter type. Single/Multiple' % (RestService.timestamp(), algo_name))
                        elif (algo_name == 'MultinomialNB'):
                            if (algo['ParameterType'] == "Multiple"):
                                # Use GridSearchCV
                                parameters = algo['Parameters']
                                param_grid = {}
                                alpha = 0
                                for parameter in parameters:
                                    if (parameter["ParameterName"] == 'alpha'):
                                        alpha = parameter['Value']
                                if(alpha):
                                    try:
                                        alpha_start = alpha[0]
                                        alpha_end = alpha[1]
                                        alpha_evals  = alpha[2]
                                    except Exception as e:
                                        logging.error('%s: Error occurred: %s '%(RestService.timestamp(),str(e)))
                                        logging.info('%s: Exception catched. taking default alpha as alpha .'%(RestService.timestamp()))
                                        alpha_start = alpha[0]
                                        alpha_end = alpha[1]
                                        alpha_evals  = alpha[2]
                                else:
                                    logging.info('%s: alpha parameter value missing/cannot be zero. taking default'%(RestService.timestamp()))
                                    alpha_start = alpha[0]
                                    alpha_end = alpha[1]
                                    alpha_evals  = alpha[2]
                                mnb_space = [hp.uniform('alpha', alpha_start, alpha_end)]
                                mnb_tpe_best = fmin(model.MultinomialNBClassifierObjective, mnb_space, algo=tpe_algo,max_evals=alpha_evals)
                                logging.info('%s: Started training with %s algorithm.' % (RestService.timestamp(), algo_name))
                                score_dict = model.classify(model=MultinomialNB(alpha=mnb_tpe_best['alpha']))
                                logging.info('%s: Model has been trained successfully using %s algorithm.' % (RestService.timestamp(), algo_name))
                                # Store best parameters to use it as default next time
                                params = []
                                for key, value in mnb_tpe_best.items():
                                    tmp_dict = {}
                                    tmp_dict['ParameterName'] = key
                                    tmp_dict['Value'] = value
                                    params.append(tmp_dict)
                                algo_param_dict['Parameters'] = params
                            elif (algo['ParameterType'] == "Single"):
                                parameters = algo['Parameters']
                                algo_param_dict['Parameters'] = parameters
                                param_grid = {}
                                for parameter in parameters:
                                    if (parameter["ParameterName"] == 'alpha'):
                                        param_grid['alpha'] = parameter['Value']
                                logging.info('%s: Started training with %s algorithm.' % (RestService.timestamp(), algo_name))
                                score_dict = model.classify(model=MultinomialNB(alpha=param_grid['alpha']))
                                logging.info('%s: Model has been trained successfully using %s algorithm.' % (
                                    RestService.timestamp(), algo_name))
                            else:
                                logging.info('%s: Specify parameter type. Single/Multiple' % (RestService.timestamp(), algo_name))
                        elif (algo_name == 'LogisticRegression'):
                            if (algo['ParameterType'] == "Multiple"):
                                # Use GridSearchCV
                                parameters = algo['Parameters']
                                param_grid = {}
                                C_val = 0
                                for parameter in parameters:
                                    if (parameter["ParameterName"] == 'C'):
                                        C_val = parameter['Value']
                                if(C_val):
                                    try:
                                        lr_c_start = C_val[0]
                                        lr_c_end = C_val[1]
                                        lr_c_evals  = C_val[2]
                                    except Exception as e:
                                        logging.error('%s: Error occurred: %s '%(RestService.timestamp(),str(e)))
                                        logging.info('%s: Exception catched. taking default C_val.'%(RestService.timestamp()))
                                        lr_c_start = C_val[0]
                                        lr_c_end = C_val[1]
                                        lr_c_evals  = C_val[2]
                                else:
                                    logging.info('%s: C_val range parameter value missing/cannot be zero. taking default'%(RestService.timestamp()))
                                    lr_c_start = C_val[0]
                                    lr_c_end = C_val[1]
                                    lr_c_evals  = C_val[2]
                                
                                lr_space = [hp.uniform('C', lr_c_start, lr_c_end)]
                                lr_tpe_best = fmin(model.LogisticRegressionObjective, lr_space, algo=tpe_algo,max_evals=lr_c_evals)
                                logging.info('%s: Started training with %s algorithm.' % (RestService.timestamp(), algo_name))
                                score_dict = model.classify(model=LogisticRegression(C=lr_tpe_best['C'], random_state=42))
                                logging.info('%s: Model has been trained successfully using %s algorithm.' % (RestService.timestamp(), algo_name))
                                # Store best parameters to use it as default next time
                                params = []
                                for key, value in lr_tpe_best.items():
                                    tmp_dict = {}
                                    tmp_dict['ParameterName'] = key
                                    tmp_dict['Value'] = value
                                    params.append(tmp_dict)
                                algo_param_dict['Parameters'] = params
                            elif (algo['ParameterType'] == "Single"):
                                parameters = algo['Parameters']
                                algo_param_dict['Parameters'] = parameters
                                param_grid = {}
                                for parameter in parameters:
                                    if (parameter["ParameterName"] == 'C'):
                                        param_grid['C'] = parameter['Value']
                                logging.info('%s: Started training with %s algorithm.' % (RestService.timestamp(), algo_name))
                                print("params....",param_grid)
                                score_dict = model.classify(
                                    model=LogisticRegression(C=param_grid['C'], random_state=42))
                                logging.info('%s: Model has been trained successfully using %s algorithm.' % (
                                    RestService.timestamp(), algo_name))
                            else:
                                logging.info('%s: Specify parameter type. Single/Multiple' % (RestService.timestamp(), algo_name))
                        elif(user_param_choices['Status']=='Train' and algo_name == 'XGBClassifier'):
                            algo_param_dict['Parameters'] = algo['Parameters']
                            algorithms_params.append(algo_param_dict)
                            continue
                        else:
                            logging.info(
                                '%s: There is no model defined for %s algorithm. Use RandomForestClassifier/LogisticRegression/MultinomialNB/SVC' % (
                                    RestService.timestamp(), algo))
                            continue

                        f_accuracy = float("{0:.4f}".format(score_dict['Accuracy']))
                        F1_score_ = float("{0:.4f}".format(score_dict['F1_score']))
                        precision_score_ = float("{0:.4f}".format(score_dict['Precision']))
                        recall_score_ = float("{0:.4f}".format(score_dict['Recall']))
                        

                        pkl_file = cust_name + '__' + dataset_name + '__' + algo_name + '__' + pred_field + '__' + training_status + '__' + 'Model.pkl'
                        algo_dict['AlgorithmName'] = algo_name
                        algo_dict['PredictionPklFile'] = pkl_file

                        algo_dict['Accuracy'] = f_accuracy
                        algo_dict['F1_score'] = F1_score_
                        algo_dict['Precision'] = precision_score_
                        algo_dict['Recall'] = recall_score_
                        final_score_list.append(score_dict['CategoryMetrics'])
                        algorithms_data.append(algo_dict)
                        algorithms_params.append(algo_param_dict)
                        completed_status = completed_status + completed_factor
                        logging.info('%s: Training completed = %f' % (RestService.timestamp(), completed_status))
                        DatasetMasterData.updateDaemonTraining(customer_id,dataset_id, "InProgress", completed_status, today)
                else:
                    logging.info(
                        '%s: Training data for a field- %s is not sufficient enough to train algos. Please submit sufficient data to make algo learn from it.' % (
                            RestService.timestamp(), pred_field))
                    continue
                    # Insert collected data into TblTraining
                # Naming conventions for: ML model pickes- CustomerName__Algorithm__PredictField__InProgress/Approved__Model.pkl
                # Naming conventions for: Vocabulary pickes- CustomerName__inField__PredictField__InProgress/Approved__Vectorization.pkl
                vectorization_pkl = cust_name + '__' + dataset_name + '__' + in_field + '__' + pred_field + '__' + training_status + '__' + 'Vectorization.pkl'
                pred_field_dict["VectorizationPklFile"] = vectorization_pkl
                pred_field_dict["Algorithms"] = algorithms_data
                pred_field_dict["CategoryMetrics"] = final_score_list
                predicted_fields_data.append(pred_field_dict)
            tbl_training_row["PredictedFields"] = predicted_fields_data #CategoryMetrics
            tbl_training_row["AlgorithmParameters"] = algorithms_params
            try:
                logging.info('%s: Trying to insert calculated accuracies into TblTraining.' % RestService.timestamp())
                MongoDBPersistence.training_hist_tbl.insert_one(tbl_training_row)
                logging.info('%s: Accuracies recorded successfully into TblTraining. TrainingID: %d' % (RestService.timestamp(), training_id))
                DatasetMasterData.updateDaemonTraining(customer_id,dataset_id, "Completed", completed_status, today, str(datetime.now())[:19])
                MongoDBPersistence.training_tickets_tbl.update_many({'CustomerID': customer_id, "DatasetID": dataset_id},{"$set": {"TrainingFlag": 1}})

                #Recommendation.generate_TF(customer_id, dataset_id)
                #--Code to insert records to TblWhitelistedWordDetails according to predicted fields
                if(training_status != "Tuning"):
                    whitelisted_record={}
                    logging.info('%s: Trying to insert/update records to whitelisted_word_tbl according to predicted fields'%RestService.timestamp)
                    for pred_field in pred_field_list:
                        whitelisted_record["CustomerID"]=customer_id
                        whitelisted_record["DatasetID"]=dataset_id
                        whitelisted_record["PredictedField"]=pred_field
                        whitelisted_record["WhiteListed_Words"]=[]
                        MongoDBPersistence.whitelisted_word_tbl.update_one({
                                        'CustomerID':customer_id,'DatasetID':dataset_id,'PredictedField':pred_field
                                },{
                                        '$set':whitelisted_record
                                },upsert=True)
                    logging.info('%s: successfully inserted/updated documents to whitelisted_word_tbl'%RestService.timestamp)
                
            except Exception as e:
                logging.error('%s: Error occurred: %s ' % (RestService.timestamp(), str(e)))
                logging.error('%s: Check whether data following the database constarints.' % (RestService.timestamp()))
                return json_util.dumps('failure')
            
            return json_util.dumps(training_id)

    #The below code handles json creation for generating graphs.
    @staticmethod
    def displayGraph(customer_id,dataset_id,predicted_field):
        predict_field = list(MongoDBPersistence.training_tickets_tbl.find({"CustomerID": customer_id, "DatasetID":dataset_id},{predicted_field:1,"_id":0}))
        ()
        temp_list=[]
        for i in range(0,len(predict_field)-1):
            temp_list.append(predict_field[i][predicted_field])
            from collections import Counter
            predict_field_dict = dict(Counter(temp_list))

        if(predict_field):
            resp = json_util.dumps(predict_field_dict)
        else:
            resp = ''
        return resp

    #Code for word cloud - Adding new stop words
    @staticmethod
    def saveStopWords(customer_id, dataset_id):
        new_stopwords = request.get_json()
        stopwords = new_stopwords['stopwords']
        stopwords_list = MongoDBPersistence.datasets_tbl.find_one({"$and": [{"DatasetID": dataset_id},{"CustomerID": customer_id}]},{"Stopwords": 1, "_id": 0})
        # storing stopwords in lowercase
        for i in range(0,len(stopwords)):
            stopwords[i] = stopwords[i].lower()
        if stopwords_list:
            old_stopwords = stopwords_list['Stopwords'][0]['stopword']
            approved_stopwords = stopwords_list['Stopwords'][1]['stopword']
            for word in stopwords:
                if word not in old_stopwords:
                    old_stopwords.append(word)
            MongoDBPersistence.datasets_tbl.update_one({"$and":[{"DatasetID": dataset_id},{"CustomerID": customer_id}]},
            {"$set": {"Stopwords": [{"stopword": old_stopwords,"Status": 'InProgress'},
            {"stopword": approved_stopwords, "Status": 'Approved'}]}}, upsert=False)

        else:
            MongoDBPersistence.datasets_tbl.update_one({"$and":[{"DatasetID": dataset_id},{"CustomerID": customer_id}]},
            {"$set": {"Stopwords": [{"stopword": stopwords,"Status": 'InProgress'},
            {"stopword": [], "Status": 'Approved'}]}}, upsert=False)
            
        return json_util.dumps(stopwords)  

    # code for getting json for Wordcloud
    #returns a unigram json
    @staticmethod
    def displayWordCloud(customer_id, dataset_id, predictedfield,sub_field,number_of_words,cloud_type):
        with open('data/stopwords.csv', 'r') as readFile:
            reader = csv.reader(readFile)
            list1 = list(reader)  
            ENGLISH_STOP_WORDS = list1[0]
            readFile.close()
        ()
        dataset_info_dict =  MongoDBPersistence.datasets_tbl.find_one({'CustomerID':customer_id, "DatasetID":dataset_id},{'FieldSelections':1, '_id':0})
        if(dataset_info_dict):   
            fieldselection_list = dataset_info_dict['FieldSelections']
        else:
            logging.info('%s: Dataset not found in the record.'%RestService.timestamp())
            return 'failure'
        pred_list = []

        for pred_fields in fieldselection_list:
            if(pred_fields['FieldsStatus']=='InProgress' or pred_fields['FieldsStatus']=='Approved'):
                pred_list = pred_fields['PredictedFields']
        if(len(pred_list)==0):
            logging.info("%s: Failure: Customer didn't choose any fields."%RestService.timestamp())
            return 'failure'
        input_field_list = []
        for field in pred_list:
            if field['PredictedFieldName'] == predictedfield:
                input_field_list = field['InputFields']
        input_df = pd.DataFrame()
        input_df = pd.DataFrame(list(MongoDBPersistence.training_tickets_tbl.find({'CustomerID': customer_id, "DatasetID": dataset_id, predictedfield: sub_field},{'_id':0,input_field_list[0]:1})))
        for input_field_ in input_field_list[1:]:
            input_df[input_field_] = pd.DataFrame(list(MongoDBPersistence.training_tickets_tbl.find({'CustomerID': customer_id, "DatasetID": dataset_id, predictedfield: sub_field},{'_id':0,input_field_:1})))
        input_df['in_field'] = ''
        for field in input_field_list:
            input_df['in_field']+=input_df[field] + ' '
        input_df1 = pd.DataFrame()
        input_df1['in_field'] = input_df['in_field'].astype(str)

        #cleaning corpus

        input_df1 = IncidentTraining.cleaningInputFields(input_df1,'in_field')
        pd.options.display.max_colwidth = 500
        sentences = list(input_df1['in_field'])

        stopwords_list = MongoDBPersistence.datasets_tbl.find_one({"$and": [{"DatasetID": dataset_id},{"CustomerID": customer_id}]},{"Stopwords": 1, "_id": 0})
        if stopwords_list:
            in_progress_stopwords = stopwords_list['Stopwords'][0]['stopword']
            stopwords_list = stopwords_list['Stopwords'][1]['stopword']
        else:
            stopwords_list = []
            in_progress_stopwords = []
        final_stopwords = ENGLISH_STOP_WORDS + stopwords_list + in_progress_stopwords
        clean_sentences = []
        for sentence in sentences:
            clean_sentence = sentence.split()
            clean_sentence = [word for word in clean_sentence if not word in set(final_stopwords)]
            clean_sentence = " ".join(clean_sentence)
            clean_sentences.append(clean_sentence)    
        
        if cloud_type == 'Unigram':
            clean_words_list = []
            for sentence in clean_sentences:
                for word in sentence.split():
                    clean_words_list.append(word)
            clean_words_dict = dict(Counter(clean_words_list))
            if number_of_words > len(clean_words_dict):
                number_of_words = len(clean_words_dict)  #also send a default value of number of words from front end
            
            sorted_dict = sorted(clean_words_dict.items(), key=lambda x: x[1])
            words_dict = {}
            for i in range(len(sorted_dict) - 1,len(sorted_dict) - number_of_words -1,-1):
                words_dict.update({sorted_dict[i][0]:sorted_dict[i][1]})
            
            if words_dict:
                resp = json_util.dumps(words_dict)
            else:
                resp = ''
            
        elif cloud_type == 'Bigram':
            clean_words_list_bigram = []
            for i in range (0,len(clean_sentences) -1):
                bigram_list = TextBlob(clean_sentences[i]).ngrams(2)
                for j in range(0,len(bigram_list) - 1):
                    biagram = bigram_list[j][0] + " " + bigram_list[j][1]
                    clean_words_list_bigram.append(biagram)
            clean_word_dict_bigram = dict(Counter(clean_words_list_bigram))
            if number_of_words > len(clean_word_dict_bigram):
                number_of_words = len(clean_word_dict_bigram)  #also send a default value of number of words from front end
            sorted_dict_bigram = sorted(clean_word_dict_bigram.items(), key=lambda x: x[1])
            words_dict_bigram = {}
            for i in range(len(sorted_dict_bigram) - 1,len(sorted_dict_bigram) - number_of_words -1,-1):
                words_dict_bigram.update({sorted_dict_bigram[i][0]:sorted_dict_bigram[i][1]} )
            if words_dict_bigram:
                resp = json_util.dumps(words_dict_bigram)
            else:
                resp = ''
        return resp



    #returns a list of stopwords to be displayed
    @staticmethod
    def displayStopWords(customer_id,dataset_id):
        stopwords_list = MongoDBPersistence.datasets_tbl.find_one({"CustomerID": customer_id,"DatasetID": dataset_id},{"Stopwords":1,"_id":0})
        ()
        if stopwords_list:
            stopwords_list = stopwords_list['Stopwords'][1]['stopword']
            
        else:
            stopwords_list = []
            
        return json_util.dumps(stopwords_list)


    # remove a clicked stopword
    @staticmethod
    def removeStopWords(customer_id,dataset_id,word):
        stopwords_list = MongoDBPersistence.datasets_tbl.find_one({"CustomerID": customer_id,"DatasetID": dataset_id},{"Stopwords":1,"_id":0})
        ()
        if stopwords_list:
            approved_stopwords = stopwords_list['Stopwords'][1]['stopword']
            in_progress_stopwords = stopwords_list['Stopwords'][0]['stopword']
            if word in approved_stopwords:
                approved_stopwords.remove(word)
            else:
                print('error')
            MongoDBPersistence.datasets_tbl.update_one({"$and":[{"DatasetID": dataset_id},{"CustomerID": customer_id}]},
            {"$set": {"Stopwords": [{"stopword": in_progress_stopwords,"Status": 'InProgress'}, 
            {"stopword": approved_stopwords, "Status": 'Approved'}]}}, upsert=False)
        else:
            print("hello")
        return json_util.dumps(approved_stopwords)  #returning a list

    @staticmethod
    def moveToTrainingData(customer_id, dataset_id):
        #delete the document from TblPredictedData, TblIncidentRT & Put it into TblIncidentTraining
        #data holds corrected ticket data.. dictionary/json format.. simple key value
        field_mapping = MappingPersistence.get_mapping_details(customer_id)
        group_field_name = field_mapping['Group_Field_Name']
        ticket_id_field_name = field_mapping['Ticket_ID_Field_Name']
        status_field_name = field_mapping['Status_Field_Name']
        description_field_name = field_mapping['Description_Field_Name']
        data = request.get_json()
        ()
        for ticket in data:
            n_ticket = MongoDBPersistence.rt_tickets_tbl.find({'CustomerID':customer_id, "DatasetID":dataset_id, ticket_id_field_name:ticket[ticket_id_field_name]})
            p_ticket = MongoDBPersistence.predicted_tickets_tbl.find_one({'CustomerID':customer_id, ticket_id_field_name:ticket[ticket_id_field_name]},{"_id":0,ticket_id_field_name:0,"CustomerID":0,"DatasetID":0})
            for field in p_ticket:
                n_ticket[field] = p_ticket[field]
            n_ticket["TrainingFlag"] = 0
            n_ticket["CustomerID"] = customer_id
            n_ticket["DatasetID"] = dataset_id
            try:
                logging.info('%s: Removing updated ticket from TblPredictedData & TblIncidentRT.'%RestService.timestamp())
                MongoDBPersistence.predicted_tickets_tbl.delete_many({'CustomerID':customer_id, "DatasetID":dataset_id, ticket_id_field_name:ticket[ticket_id_field_name]})
                MongoDBPersistence.rt_tickets_tbl.delete_many({'CustomerID':customer_id, "DatasetID":dataset_id, ticket_id_field_name:ticket[ticket_id_field_name]})
                logging.info('%s: Ticket data removed successfully.'%RestService.timestamp())
                #Insert ticket into TblIncidentTraining
                logging.info('%s: Inserting ticket into TblIncidentTraining, for retraining purpose.'%RestService.timestamp())
                MongoDBPersistence.training_tickets_tbl.insert_one(n_ticket)
                logging.info('%s: Ticket data inserted into TblIncidentTraining successfully.'%RestService.timestamp())
                resp = 'success'
            except Exception as e:
                logging.error('%s: Error occurred: %s '%(RestService.timestamp(),str(e)))
                resp = 'failure'
        return resp 
    
    
    @staticmethod
    def update_status(customer_id,status):
        #Fetching last InProgress TrainingID for a given customer
        last_training_dict = MongoDBPersistence.training_hist_tbl.find_one({"CustomerID" : customer_id,"TrainingStatus" : "InProgress", "TrainingID": {"$exists": True}},{'_id':0,"TrainingID":1}, sort=[("TrainingID", -1)])
        ()
        if(last_training_dict):
            last_training_id = last_training_dict['TrainingID']
        else:
            #It should be non-Registered Customer
            logging.info("Last InProgress training info not found for the customer.")
            return json_util.dumps("failure")
        try:
            MongoDBPersistence.customer_tbl.update_one({'CustomerID':customer_id}, {"$set": {"FieldsStatus":status}}, upsert=False)
            MongoDBPersistence.training_hist_tbl.update_one({'CustomerID':customer_id,"TrainingID":last_training_id}, {"$set": {"TrainingStatus":status}}, upsert=False)
            resp = 'success'
        except Exception as e:
            resp = 'failure'
        return json_util.dumps(resp)



    
    @staticmethod
    def getClassificationReport(customer_id, dataset_id, predicted_field, algorithm, training_status):
        output_lst = []
        
        try:
            ()
            classification_lst=MongoDBPersistence.training_hist_tbl.find({'CustomerID': customer_id, 'DatasetID':dataset_id, 'TrainingStatus':training_status},{'PredictedFields.CategoryMetrics':1}).distinct('PredictedFields.CategoryMetrics')
            if(classification_lst):
                for doc in classification_lst:
        
                    if('AlgorithmName' in doc and doc['AlgorithmName'] == algorithm and doc['PredictedField'] == predicted_field):
                        output_lst = doc['ClassificationReport']
                        break
            else:
                raise Exception('Classification report is empty!')
            
            if(not output_lst):
                raise Exception('No document found for',predicted_field,', ',algorithm)
                
        except Exception as e:
            output_lst={'failure':str(e)}
        
        return json_util.dumps(output_lst)
    
    @staticmethod
    def updateWhiteListWords(customer_id, dataset_id, predicted_field):
        white_words_lst = None
        #checking if the predicted field entry is present or not in the Table
        white_words_lst_db = MongoDBPersistence.whitelisted_word_tbl.find_one({
                        'CustomerID':customer_id,'DatasetID':dataset_id,'PredictedField':predicted_field
                },{
                        '_id':0,'WhiteListed_Words':1
                })
        ()
        if white_words_lst_db is not None:
                white_words_lst = white_words_lst_db['WhiteListed_Words']
        
        white_words_data = request.get_json()

        print(white_words_data)
        print(type(white_words_data))
        white_words_dict = defaultdict(list)
        resp = 'success'
            #fetching all the words for all the fields
        for data in white_words_data['words']:
            print(data)
            if (data['keyword'] != ''):
                word_weight_dict = {'word': data['keyword'], 'weightage': data['weighatge']}
                white_words_dict[data['field_name']].append(word_weight_dict)
        print(white_words_dict)

        for field, words in white_words_dict.items():
            if (white_words_lst):
                logging.info('%s Checking for the existence of field_name'%(RestService.timestamp))
                old_white_words = MongoDBPersistence.whitelisted_word_tbl.find_one({
                                    'CustomerID':customer_id,
                                    'DatasetID':dataset_id,
                                    'PredictedField':predicted_field,
                                    'WhiteListed_Words.Field_Name':field
                                },{'_id': 0, "WhiteListed_Words": 1})
                
                if (old_white_words):
                    try:
                        #field entry is already present append new words to that field
                        for data in old_white_words['WhiteListed_Words']:
                            if (data['Field_Name'] == field):
                                old_white_words_list = data['Value']
                        # new_white_words = old_white_words_list + words
                        MongoDBPersistence.whitelisted_word_tbl.update_one({
                            "CustomerID": customer_id,
                            "DatasetID": dataset_id,
                            "PredictedField": predicted_field,
                            "WhiteListed_Words.Field_Name": field},
                            {
                                "$set": {
                                                'WhiteListed_Words.$.Value':words

                                }
                            }
                        )
                    except:
                        logging.info("%s Error occured in updating already present field value"% RestService.timestamp())
                        resp = 'failure'
                else:
                    #field entry is not present add this field entry
                    try:
                        MongoDBPersistence.whitelisted_word_tbl.update_one({
                            "CustomerID": customer_id,
                            "DatasetID": dataset_id,
                            "PredictedField": predicted_field},
                            {
                                "$push": {"WhiteListed_Words": {"Field_Name": field, "Value": words}}
                            }
                        )
                    except:
                        logging.info("%s Error in updating table when field value %s is not present "%(RestService.timestamp(), str(field)))
                        resp = 'failure'
            else:
                logging.info(' %s inserting white words for the first time' % RestService.timestamp())
                try:
                    table_exists = MongoDBPersistence.whitelisted_word_tbl.find_one(
                        {"CustomerID": customer_id, "DatasetID": dataset_id},
                        {"_id":1}
                    )
                    if (table_exists):
                        MongoDBPersistence.whitelisted_word_tbl.update_one({
                            "CustomerID": customer_id,
                            "DatasetID": dataset_id,},
                            {
                                "$set": {
                                    "PredictedField": predicted_field,
                                    "WhiteListed_Words":[
                                        {
                                            "Field_Name": field,
                                            "Value": words
                                        }
                                    ]
                                }
                            }
                        )
                    else:
                        logging.info(' %s inserting document for the first time' % RestService.timestamp())
                        MongoDBPersistence.whitelisted_word_tbl.insert(
                            {"CustomerID": customer_id, "DatasetID": dataset_id,
                            "PredictedField": predicted_field,
                            "WhiteListed_Words":[
                                {
                                    "Field_Name": field,
                                    "Value": words
                                }
                            ]
                            }
                        )
                    white_words_lst = MongoDBPersistence.whitelisted_word_tbl.find({
                    'CustomerID':customer_id,'DatasetID':dataset_id,'PredictedField':predicted_field
                    },{
                            '_id':0,'WhiteListed_Words.Value':1
                    }).distinct('WhiteListed_Words.Value')
                except:
                    logging.info("%s Error occured when there is no predicted field present" % RestService.timestamp())
                    resp = 'failure'
        if (resp == 'failure'):
            return 'failure'
        else:
            return 'success'
        
    @staticmethod
    def getWhiteListWords(customer_id,dataset_id,predicted_field):
        try:
            ()
            logging.info('%s: fetching details from whitelisted_word_tbl'%RestService.timestamp())
            white_words_lst=list(MongoDBPersistence.whitelisted_word_tbl.find({
                                    'CustomerID':customer_id,'DatasetID':dataset_id,'PredictedField':predicted_field
                            },{
                                    '_id':0,'WhiteListed_Words':1        
                            }))
            print("white list words",white_words_lst)
            if(white_words_lst):
                return json_util.dumps(white_words_lst)
        except Exception as e:
            logging.error('%s: some exception in getWhiteListWords: %s'%(RestService.timestamp(),str(e)))
        return 'failure'

    @staticmethod
    def deleteWhiteListWords(customer_id, dataset_id, predicted_field, field_name, word):
        flag = 1
        old_white_words =  MongoDBPersistence.whitelisted_word_tbl.find_one(
            {"CustomerID": customer_id, "DatasetID": dataset_id, "PredictedField":predicted_field, "WhiteListed_Words.Field_Name": field_name},
            {"_id":0, "WhiteListed_Words":1}
        )
        
        ()
        if (old_white_words):
            try:
                
                #field entry is already present append new words to that field
                for data in old_white_words['WhiteListed_Words']:
                    if (data['Field_Name'] == field_name):
                        old_white_words_list = data['Value']
                        print('list before removal of word: ',old_white_words_list)
                        for i in range(len(old_white_words_list)):
                            if old_white_words_list[i]['word'] == word:
                                removed_dict = old_white_words_list.pop(i)
                                break
                        print('list after removal: ',old_white_words_list)
                        MongoDBPersistence.whitelisted_word_tbl.update_one({
                            "CustomerID": customer_id,
                            "DatasetID": dataset_id,
                            "PredictedField": predicted_field,
                            "WhiteListed_Words.Field_Name": field_name},
                            {
                                "$set": {
                                                'WhiteListed_Words.$.Value': old_white_words_list
                                }
                            }
                        )
            except Exception as e:
                print("Exception :",e)
                logging.info("%s some error in deleting WhiteWords" %RestService.timestamp)
        else:
            logging.info('%s: No old_white_words'%old_white_words)
            flag = 0

        if (flag == 1):
            return "success"
        else:
            return "failure"
    

    @staticmethod
    def getWordCloudList(customer_id,dataset_id,predicted_field,number_of_words,cloud_type):
        ()
        logging.info("Inside getWordCloudList method")
        pred_cat = MongoDBPersistence.datasets_tbl.find_one({"CustomerID":customer_id,"DatasetID":dataset_id},{"IdToLabels":1,"_id":0})
        
        sub_category_labels=[]
        idToLabel = pred_cat["IdToLabels"]
        
        for key,value in idToLabel.items():
            
            if(str(key) == str(predicted_field)):

                sub_categories_dict =idToLabel[predicted_field]
                sub_category_labels = [label for key,label in sub_categories_dict.items()]
            
        
        word_cloud_list =[]
        word_count_dict={}
        for sub_cat in sub_category_labels:
            #function provides the json dump 
            json_dump = Training.displayWordCloud(customer_id, dataset_id, predicted_field,\
                                                sub_cat,int(number_of_words),cloud_type)
            
            word_count_dict[sub_cat] = json_dump
        output = Training.exportToCSVFormat(word_count_dict,predicted_field)

        return output
    @staticmethod
    def exportToCSVFormat(word_count_dict,predicted_field):
        ()
        logging.info("Inside exportToCSVFormat")

        data_list = []
        data_list.append([predicted_field,'Words','Count'])
        for key,val in word_count_dict.items():
            strToJson = json.loads(val)
            for i,j in strToJson.items():
                tmp_list=[]
                tmp_list.append(key)
                tmp_list.append(i)
                tmp_list.append(j)
                data_list.append(tmp_list)
        
        si = StringIO()
        cw = csv.writer(si)
        cw.writerows(data_list)
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=export.csv"
        output.headers["Content-type"] = "text/csv"
        logging.info('%s: Predicted tickets have been exported successfully into a csv.'%RestService.timestamp)
        return output

    @staticmethod
    def getAllCategories(customer_id,dataset_id):
        category_list=list(MongoDBPersistence.datasets_tbl.find({"CustomerID":customer_id,"DatasetID":dataset_id},{"ColumnNames":1,"_id":0}))

        dropdownvalues=category_list[0]['ColumnNames']
        print("column names from backemd",dropdownvalues)
        return json_util.dumps(dropdownvalues)




    @staticmethod
    def getBarCategoryList(customer_id,dataset_id):
        category_list=list(MongoDBPersistence.PMAcategory_tbl.find({"CustomerID": customer_id, "DatasetID":dataset_id},{"Bar_Filter_Columns":1,"_id":0}))
        print(category_list)
        dropdownvalues=category_list[0]['Bar_Filter_Columns']
        print("printing dropdown values from DB ",dropdownvalues)
        return json_util.dumps(dropdownvalues)
        
        
    @staticmethod
    def getPieCategoryList(customer_id,dataset_id):
        category_list=list(MongoDBPersistence.PMAcategory_tbl.find({"CustomerID": customer_id, "DatasetID":dataset_id},{"PieChart_Filter_Columns":1,"_id":0}))
        print(category_list)
        dropdownvalues=category_list[0]['PieChart_Filter_Columns']
        print("printing dropdown values from DB ",dropdownvalues)
        return json_util.dumps(dropdownvalues)

    
    @staticmethod
    def take(n, iterable):
        #"Return first n items of the iterable as a list"
          return dict(islice(iterable, n)) 

    @staticmethod
    def displayGraph_PMA(customer_id,dataset_id,selected_field,year,month):
        
        select_field = list(MongoDBPersistence.training_tickets_tbl.find({"CustomerID": 1, "DatasetID":1}))
        mydata = pd.DataFrame(select_field)
        mydata['created'] = pd.to_datetime(mydata.loc[:, 'created'], errors='coerce')
        mydata2 = mydata.filter(["created", selected_field])
        if month in ['January','February','March','April','May','June','July','August','September','October','November','December']:
            year = int(year)
            _month = month
            datetime_object = datetime.datetime.strptime(_month, "%B")
            month_number = datetime_object.month
            month = month_number
            filter_year = ((mydata2['created'] >= str(year)) & (mydata2['created'] < str(year + 1)))
            year_data = mydata2[filter_year]
            filter_month = (year_data['created'].dt.month >= month) & (year_data['created'].dt.month < (month + 1))
            month_data = year_data[filter_month]
            z = pd.DataFrame({'count' : month_data.groupby(selected_field).size()})
            
        elif month == 'undefined' or month=='null':
            year = int(year)
            filter_year = (mydata2['created'] >= str(year)) & (mydata2['created'] < str(year + 1))
            data_for_input_year = mydata2[filter_year]
            z = pd.DataFrame({'count' : data_for_input_year.groupby(selected_field).size()})
            
        z1=z.to_dict()
        z2 = list(z1.values())[0]
        new_select_field_dict=dict(sorted(z2.items(), key=lambda kv: kv[1], reverse=True))
        if(len(new_select_field_dict)>15):
            new_select_field_dict=Training.take(15, new_select_field_dict.items())
        print(new_select_field_dict)

        if(select_field):
            resp = json_util.dumps(new_select_field_dict)
        else:
            resp = ''
        print("data while displaying Graph",resp)
        return resp
    #to display donut graph for priority 
    @staticmethod
    def displayGraph_donutPMA(customer_id,dataset_id,selected_field,ag,unassigned_value):
        if(unassigned_value=="true"):
            select_field = list(MongoDBPersistence.training_tickets_tbl.find({"CustomerID": customer_id, "DatasetID":dataset_id,selected_field:""},{"priority":1,"_id":0}))
            temp_list=[]
            for i in range(0,len(select_field)):
                temp_list.append(select_field[i]["priority"])
                from collections import Counter
                select_field_dict = dict(Counter(temp_list))

            if(select_field):
                resp = json_util.dumps(select_field_dict)
            else:
                resp = ''
            print("data while displaying donut Graph",resp)


        else:    
            select_field = list(MongoDBPersistence.training_tickets_tbl.find({"CustomerID": customer_id, "DatasetID":dataset_id,selected_field:ag},{"priority":1,"_id":0}))

            temp_list=[]
            for i in range(0,len(select_field)):
                temp_list.append(select_field[i]["priority"])
                from collections import Counter
                select_field_dict = dict(Counter(temp_list))

            if(select_field):
                resp = json_util.dumps(select_field_dict)
            else:
                resp = ''
            print("data while displaying donut Graph",resp)
        return resp

    @staticmethod
    def displaylineGraph_PMA(customer_id,dataset_id,from_year,to_year):
        cre_list=[] 
        cre_list=list(MongoDBPersistence.training_tickets_tbl.find({"CustomerID": customer_id, "DatasetID":dataset_id},{"created":1,"_id":0}))
        filtered_data=list(filter(None,cre_list))#to remove null values
        df=pd.DataFrame()
        date_list=[]
        for i in range(len(filtered_data)):
            my_string=filtered_data[i]['created'].split(" ")[0]
            date_list.append(my_string)
        print(len(date_list))
        print("date list is ",date_list)
        df=pd.DataFrame(date_list,columns =['date'])
        df['Count'] = 1
        df['date'] = pd.to_datetime(df['date'])
        df_new=df.groupby(df['date'].dt.strftime('%Y:%B'))['Count'].sum().sort_values()
        data_dict=df_new.to_dict()
        print("printing data in dictionary format ",data_dict)
        #filtering based on from and to years selected 
        print("type of from year and to year is ",type(from_year))
        filtered_dict={k: v for k, v in data_dict.items() if k.startswith((from_year,to_year))}
        resp=json_util.dumps(filtered_dict) 
        return resp


    @staticmethod
    def displayWordCloud_PMA(customer_id, dataset_id, selectedfield,field_value,unassigned_value,number_of_words,cloud_type):
        
        if(unassigned_value=="true"):    
            with open('data/stopwords.csv', 'r') as readFile:
                reader = csv.reader(readFile)
                list1 = list(reader)  
                ENGLISH_STOP_WORDS = list1[0]
                readFile.close()
            
            input_df = pd.DataFrame()
            input_df = pd.DataFrame(list(MongoDBPersistence.training_tickets_tbl.find({'CustomerID': 1, "DatasetID": 1,selectedfield:"" },{'_id':0,"description":1})))

            #cleaning corpus
            input_df = IncidentTraining.cleaningInputFields(input_df,'description')
            pd.options.display.max_colwidth = 500
            sentences = list(input_df['description'])
            final_stopwords = ENGLISH_STOP_WORDS #we can add still more stop words
            clean_sentences = []
            for sentence in sentences:
                clean_sentence = sentence.split()
                clean_sentence = [word for word in clean_sentence if not word in set(final_stopwords)]
                clean_sentence = " ".join(clean_sentence)
                clean_sentences.append(clean_sentence)
            if cloud_type == 'Unigram':
                clean_words_list = []
                for sentence in clean_sentences:
                    for word in sentence.split():
                        clean_words_list.append(word)
                clean_words_dict = dict(Counter(clean_words_list))
                if number_of_words > len(clean_words_dict):
                    number_of_words = len(clean_words_dict)  #also send a default value of number of words from front end
                
                sorted_dict = sorted(clean_words_dict.items(), key=lambda x: x[1])
                words_dict = {}
                for i in range(len(sorted_dict) - 1,len(sorted_dict) - number_of_words -1,-1):
                    words_dict.update({sorted_dict[i][0]:sorted_dict[i][1]})
                
                if words_dict:
                    resp = json_util.dumps(words_dict)
                else:
                    resp = ''

            elif cloud_type == 'Bigram':
                clean_words_list_bigram = []
                for i in range (0,len(clean_sentences) -1):
                    bigram_list = TextBlob(clean_sentences[i]).ngrams(2)
                    for j in range(0,len(bigram_list) - 1):
                        biagram = bigram_list[j][0] + " " + bigram_list[j][1]
                        clean_words_list_bigram.append(biagram)
                clean_word_dict_bigram = dict(Counter(clean_words_list_bigram))
                if number_of_words > len(clean_word_dict_bigram):
                    number_of_words = len(clean_word_dict_bigram)  #also send a default value of number of words from front end
                sorted_dict_bigram = sorted(clean_word_dict_bigram.items(), key=lambda x: x[1])
                words_dict_bigram = {}
                for i in range(len(sorted_dict_bigram) - 1,len(sorted_dict_bigram) - number_of_words -1,-1):
                    words_dict_bigram.update({sorted_dict_bigram[i][0]:sorted_dict_bigram[i][1]} )
                if words_dict_bigram:
                    resp = json_util.dumps(words_dict_bigram)
                else:
                    resp = ''
            return resp
        else:
            with open('data/stopwords.csv', 'r') as readFile:
                reader = csv.reader(readFile)
                list1 = list(reader)  
                ENGLISH_STOP_WORDS = list1[0]
                readFile.close()
            
            input_df = pd.DataFrame()
            input_df = pd.DataFrame(list(MongoDBPersistence.training_tickets_tbl.find({'CustomerID': 1, "DatasetID": 1,selectedfield:field_value },{'_id':0,"description":1})))

            #cleaning corpus
            input_df = IncidentTraining.cleaningInputFields(input_df,'description')
            pd.options.display.max_colwidth = 500
            sentences = list(input_df['description'])
            final_stopwords = ENGLISH_STOP_WORDS #we can add still more stop words
            clean_sentences = []
            for sentence in sentences:
                clean_sentence = sentence.split()
                clean_sentence = [word for word in clean_sentence if not word in set(final_stopwords)]
                clean_sentence = " ".join(clean_sentence)
                clean_sentences.append(clean_sentence)
            if cloud_type == 'Unigram':
                clean_words_list = []
                for sentence in clean_sentences:
                    for word in sentence.split():
                        clean_words_list.append(word)
                clean_words_dict = dict(Counter(clean_words_list))
                if number_of_words > len(clean_words_dict):
                    number_of_words = len(clean_words_dict)  #also send a default value of number of words from front end
                
                sorted_dict = sorted(clean_words_dict.items(), key=lambda x: x[1])
                words_dict = {}
                for i in range(len(sorted_dict) - 1,len(sorted_dict) - number_of_words -1,-1):
                    words_dict.update({sorted_dict[i][0]:sorted_dict[i][1]})
                
                if words_dict:
                    resp = json_util.dumps(words_dict)
                else:
                    resp = ''

            elif cloud_type == 'Bigram':
                clean_words_list_bigram = []
                for i in range (0,len(clean_sentences) -1):
                    bigram_list = TextBlob(clean_sentences[i]).ngrams(2)
                    for j in range(0,len(bigram_list) - 1):
                        biagram = bigram_list[j][0] + " " + bigram_list[j][1]
                        clean_words_list_bigram.append(biagram)
                clean_word_dict_bigram = dict(Counter(clean_words_list_bigram))
                if number_of_words > len(clean_word_dict_bigram):
                    number_of_words = len(clean_word_dict_bigram)  #also send a default value of number of words from front end
                sorted_dict_bigram = sorted(clean_word_dict_bigram.items(), key=lambda x: x[1])
                words_dict_bigram = {}
                for i in range(len(sorted_dict_bigram) - 1,len(sorted_dict_bigram) - number_of_words -1,-1):
                    words_dict_bigram.update({sorted_dict_bigram[i][0]:sorted_dict_bigram[i][1]} )
                if words_dict_bigram:
                    resp = json_util.dumps(words_dict_bigram)
                else:
                    resp = ''
            return resp

    @staticmethod
    def getSourceTargetColumns():
        resp = {}
        source_columns = []
        target_columns = []
        target_list = []
        source_list = []
        try:
            source_columns=dict(MongoDBPersistence.cluster_table.find_one({},{'_id':0}))
            source_list=list(source_columns.keys())
            print("source columns...",source_columns)
            target_columns=list(MongoDBPersistence.pma_fields_tbl.find({},{'_id':0}))
            print("target columns...")
            if len(target_columns) > 0:
                if 'ColumnNames' in target_columns[0].keys():
                    target_list = target_columns[0]['ColumnNames']

            source_list=[column for column in source_list if column not in target_list]

            resp['sourceColumns'] = source_list
            resp['targetColumns'] = target_list

            print("Source column names are:",source_list)
            print("target column names are:",target_list)

            return json_util.dumps(resp)
        except Exception as e:
            print(str(e))
        return 'failure'

    @staticmethod
    def updatePMATargetColumns():
        ColumnNames = request.get_json()
        print('-------',ColumnNames)

        MongoDBPersistence.pma_fields_tbl.update_one({},{'$set': {'ColumnNames':ColumnNames}}, upsert=True)
        MongoDBPersistence.pma_fields_tbl.update_one({},{'$set': {'PieChart_Filter_Columns':ColumnNames}}, upsert=True)
        MongoDBPersistence.pma_fields_tbl.update_one({},{'$set': {'Bar_Filter_Columns':ColumnNames}}, upsert=True)

        return 'success'

