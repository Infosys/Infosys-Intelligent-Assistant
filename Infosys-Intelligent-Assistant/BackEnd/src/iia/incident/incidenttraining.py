__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

from iia.persistence.mongodbpersistence import MongoDBPersistence
from iia.persistence.mappingpersistence import MappingPersistence
from iia.restservice import RestService
from iia.masterdata.customers import CustomerMasterData
from flask import request
import requests
import json
from bson import json_util
import re
import pandas as pd
import io
import csv
from iia.environ import *
from iia.utils.log_helper import get_logger, log_setup
import zipfile
from io import StringIO
from io import BytesIO
import joblib
import os
from datetime import datetime
from flask import session
logging = get_logger(__name__)
app = RestService.getApp()

@app.route('/api/uploadTrainingData/<int:customer_id>/<dataset_name>/<team_name>/<trainingMode>', methods=["POST"])
def db_insert_training_tickets( customer_id,dataset_name,team_name,trainingMode):
    return IncidentTraining.db_insert_training_tickets(customer_id, dataset_name, team_name,trainingMode)

@app.route('/api/deleteTrainingRecords/<int:customer_id>/<int:dataset_id>/<string:team_name>', methods=["POST"])
def deleteTrainingRecords( customer_id,dataset_id,team_name):
    return IncidentTraining.deleteTrainingRecords(customer_id, dataset_id, team_name)

class IncidentTraining(object):
    '''
    classdocs
    '''

    def __init__(self, params):
        '''
        Constructor
        '''
    @staticmethod
    def db_insert_training_tickets( customer_id,dataset_name,team_name,trainingMode):
        print(request)
        print("Request files: ", request.files)
        new_dataset_flag = 0
        file = request.files['trainingData']
        print("type:" , type(file))
        custom_incidenttraining_flag, custom_url = CustomerMasterData.check_custom("customIncidentTraining")
        if (custom_incidenttraining_flag=='failure'):
            logging.info("%s: Not able to read values from Configure File"%RestService.timestamp())
            return "failure"

        elif (custom_incidenttraining_flag=="True"):
            logging.info("%s Custom incident training is present invoking Custom changes"%RestService.timestamp())
            api = custom_url + "api/custom_uploadTrainingData/"+str(customer_id) + "/"+dataset_name+"/"+team_name  # customer id hardcoded
            print("-----------",api)
            proxies = {"http": None,"https": None}
            req_head = { "Content-Type": "application/json"}
            if not file:
                return "No file"
            elif(not '.csv' in str(file)):
                return "Upload csv file."
            stream = io.StringIO(file.stream.read().decode("latin-1"), newline=None)
            stream.seek(0)
            result = stream.read()
            #create list of dictionaries keyed by header row
            csv_dicts = [{k.lower(): v for k, v in row.items()} for row in csv.DictReader(result.splitlines(), \
                skipinitialspace=True)]

            csv_df = pd.DataFrame(csv_dicts)
            post_data=csv_df.to_json()
            req_res = requests.post(api,headers = req_head,data=post_data, proxies=proxies)
            response=req_res.text
            return response
        
        else:
            if trainingMode=='EDA':
                if not file:
                    return "No file"
                elif(not '.zip' in str(file)):
                    return "Upload zip file."
                print("FILE: ",file)
                streamm = BytesIO(file.read())
                zf = zipfile.ZipFile(streamm, "r")
                expected_file_names = ['DatasetTable.pkl', 'IIAupdate.pkl', 'LogisticRegression_model.pkl', 'Logisticparameters.pkl', 'MultinomialNB_model.pkl', 'Multinomialparameters.pkl', 'RandomForestClassifier_model.pkl', 'RandomForrestparameters.pkl', 'SVCParameters.pkl', 'SVC_model.pkl', 'TrainingTbl.pkl', 'XgBoostparameters.pkl', 'additionalcolumns.pkl', 'coef_lr.pkl', 'coef_mnb.pkl', 'coef_rf.pkl', 'columnTransformer.pkl', 'id_to_label.pkl', 'preprocessed_train.csv', 'vocabulary.pkl']
                recieved_file_names = []
                for fileinfo in zf.infolist():
                    print(f"file_name: {fileinfo.filename}")
                    file_name = fileinfo.filename.split("/")[-1]
                    print(f"split file_name: {file_name}")
                    if str(file_name).strip() is not None and file_name != '' : 
                        recieved_file_names.append(file_name)
                expected_file_names.sort()
                recieved_file_names.sort()
                print("expected_file_names: ",expected_file_names)
                print("recieved_file_names :",recieved_file_names)
                
                if expected_file_names != recieved_file_names:
                    print("Invalid Files in Zip")
                    return "Invalid Files in Zip"    

                for fileinfo in zf.infolist():
                    print(fileinfo)
                    print(type(fileinfo)) 
                    bytes = zf.read(fileinfo)  
                    file_name = fileinfo.filename.split("/")[-1]
                    print(f"split file_name: {file_name}")
                    if str(file_name).strip() is not None and file_name != '' : 
                        
                        with open(f"./data/{file_name}", "wb") as f:
                            f.write(bytes)

                dataset_ = MongoDBPersistence.teams_tbl.find_one({"CustomerID": customer_id,"TeamName":team_name},{"DatasetID":1,"_id":0})
                if(dataset_):
                    dataset_dict = {}
                    #Dataset exist for the team
                    logging.info('%s: Getting old dataset details.'%RestService.timestamp())
                    dataset_id = dataset_["DatasetID"]
                else:
                    #Newly adding the dataset
                    logging.info('%s: Adding new dataset.'%RestService.timestamp())
                    #getting max dataset id for the customer, so that new dataset id = old + 1
                    dataset_dict = MongoDBPersistence.datasets_tbl.find_one({"CustomerID" : customer_id, "DatasetID": {"$exists": True}},{'_id':0,"DatasetID":1}, sort=[("DatasetID", -1)])
                    if(dataset_dict):
                        last_dataset_id = dataset_dict['DatasetID']
                    else:
                        last_dataset_id = 0
                        logging.info('%s: Adding dataset for very first team.'%RestService.timestamp())
            
                    #New dataset id for the customer
                    dataset_id = last_dataset_id + 1
                    
                    new_dataset_dict = {}
                    new_dataset_dict["DatasetID"] = dataset_id
                    new_dataset_dict["DatasetName"] = dataset_name
                    new_dataset_dict["CustomerID"] =  customer_id
                    new_dataset_flag = 1

                logging.info('%s: Trying to update TblTeams with Dataset details...'%RestService.timestamp())
                MongoDBPersistence.teams_tbl.update_one({'CustomerID':customer_id, "TeamName":team_name}, \
                            {"$set": {"DatasetID":dataset_id}}, upsert=False)

                print("In EDA - Going to add daraset id in assignment enable table for the team ", team_name)
                team_doc = MongoDBPersistence.teams_tbl.find_one({'CustomerID': customer_id, "TeamName": team_name})
                team_id = team_doc["TeamID"]
                MongoDBPersistence.assign_enable_tbl.update_one({"TeamID": team_id},
                                                                {"$set": {"DatasetID": dataset_id}}, upsert=False)
                print("Dataset_id added!")

                #UPDATING ALGORITHM TABLE FOR IIA ZIP TRAINING
                MongoDBPersistence.algo_tbl.drop()
                file_training_lr = 'Logisticparameters.pkl'
                Algorithm_dict_Lr = joblib.load(f"./data/{file_training_lr}")
                Algorithm_dict_Lr['RecordCreatedDate'] = str(datetime.now())[:19]
                MongoDBPersistence.algo_tbl.insert_one(Algorithm_dict_Lr)

                file_training_rf = 'RandomForrestparameters.pkl'
                Algorithm_dict_rf = joblib.load(f"./data/{file_training_rf}")
                Algorithm_dict_rf['RecordCreatedDate'] = str(datetime.now())[:19]
                MongoDBPersistence.algo_tbl.insert_one(Algorithm_dict_rf)

                file_training_svc = 'SVCParameters.pkl'
                Algorithm_dict_svc = joblib.load(f"./data/{file_training_svc}")
                Algorithm_dict_svc['RecordCreatedDate'] = str(datetime.now())[:19]
                MongoDBPersistence.algo_tbl.insert_one(Algorithm_dict_svc)

                file_training_mb = 'Multinomialparameters.pkl'
                Algorithm_dict_mb = joblib.load(f"./data/{file_training_mb}")
                Algorithm_dict_mb['RecordCreatedDate'] = str(datetime.now())[:19]
                MongoDBPersistence.algo_tbl.insert_one(Algorithm_dict_mb)

                file_training_xg = 'XgBoostparameters.pkl'
                Algorithm_dict_xg = joblib.load(f"./data/{file_training_xg}")
                Algorithm_dict_xg['RecordCreatedDate'] = str(datetime.now())[:19]
                MongoDBPersistence.algo_tbl.insert_one(Algorithm_dict_xg)
                
                #UPDATING DATASET TABLE FOR EDA PICKLE TRAINING
                file_dataset = 'DatasetTable.pkl'
                Dataset_dict = joblib.load(f"./data/{file_dataset}")
                datasettbl = {}
                datasettbl["DatasetID"] = dataset_id
                datasettbl["DatasetName"] = dataset_name
                datasettbl["CustomerID"] =  customer_id
                datasettbl.update(Dataset_dict)
                datasettbl['TrainingStatus']['TrainingStartedBy'] = session["user"]
                datasettbl['TrainingStatus']['TrainingStartDate'] = str(datetime.now())[:19]
                datasettbl['TrainingStatus']['TrainingEndDate'] = str(datetime.now())[:19]
                algoname = datasettbl['FieldSelections'][0]['PredictedFields'][0]['AlgorithmName']
                predfield = datasettbl['FieldSelections'][0]['PredictedFields'][0]['PredictedFieldName']
                datasettbl['training_mode'] = "EDA"                
                MongoDBPersistence.datasets_tbl.insert_one(datasettbl)

                #UPDATING INCIDENT TRAINING FOR EDA PICKLE TRAINING
                df = pd.read_csv("./data/preprocessed_train.csv")
                df['DatasetID'] = dataset_id
                df['CustomerID'] = customer_id
                df['TrainingFlag']= 1
                dict_training = df.to_dict(orient='records')
                MongoDBPersistence.training_tickets_tbl.delete_many({'CustomerID':customer_id,"DatasetID":dataset_id})
                MongoDBPersistence.training_tickets_tbl.insert_many(dict_training)

                customer_name = MongoDBPersistence.customer_tbl.find_one({},{"CustomerName":1,"_id":0})
                customername = customer_name['CustomerName']

                dest_model = './models'
                dest_data = './data'
                root = './data'

                for val in recieved_file_names:
                    if val=='LogisticRegression_model.pkl':
                        source_1 = root + '/' + val
                        dest = dest_model + '/' + f"{customername}__{dataset_name}__LogisticRegression__{predfield}__InProgress__Model.pkl"
                        if os.path.exists(dest):
                            os.remove(dest)
                        os.rename(source_1, dest)
                    elif val=='RandomForestClassifier_model.pkl':
                        source_1 = root + '/' + val
                        dest = dest_model + '/' + f"{customername}__{dataset_name}__RandomForestClassifier__{predfield}__InProgress__Model.pkl"
                        if os.path.exists(dest):
                            os.remove(dest)
                        os.rename(source_1, dest)
                    elif val=='SVC_model.pkl':
                        source_1 = root + '/' + val
                        dest = dest_model + '/' + f"{customername}__{dataset_name}__SVC__{predfield}__InProgress__Model.pkl"
                        if os.path.exists(dest):
                            os.remove(dest)
                        os.rename(source_1, dest)
                    if val=='MultinomialNB_model.pkl':
                        source_1 = root + '/' + val
                        dest = dest_model + '/' + f"{customername}__{dataset_name}__MultinomialNB__{predfield}__InProgress__Model.pkl"
                        if os.path.exists(dest):
                            os.remove(dest)
                        os.rename(source_1, dest)
                    
                    elif val == 'vocabulary.pkl':
                        source_2 = root + '/' + val
                        dest = dest_data + '/' + f'{customername}__{dataset_name}__in_field__{predfield}__Vocab.pkl'
                        if os.path.exists(dest):
                            os.remove(dest)
                        os.rename(source_2, dest)
                    elif val == 'columnTransformer.pkl':
                        source_3 = root + '/' + val
                        dest = dest_data + '/' + f'{customername}__{dataset_name}__in_field__{predfield}__InProgress__transformer.pkl'
                        if os.path.exists(dest):
                            os.remove(dest)
                        os.rename(source_3, dest)
                    elif val == 'additionalcolumns.pkl':
                        source_4 = root + '/' + val
                        dest = dest_data + '/' + f'{customername}__{dataset_name}__in_field__{predfield}__additionalcolumns.pkl'
                        if os.path.exists(dest):
                            os.remove(dest)
                        os.rename(source_4, dest)

                    elif val == 'coef_lr.pkl':
                        source_4 = root + '/' + val
                        dest = dest_model + '/' + f"{customername}__{dataset_name}__LogisticRegression__{predfield}__Coef_.pkl"
                        if os.path.exists(dest):
                            os.remove(dest)
                        os.rename(source_4, dest)

                    elif val == 'coef_rf.pkl':
                        source_4 = root + '/' + val
                        dest = dest_model + '/' + f"{customername}__{dataset_name}__RandomForestClassifier__{predfield}__Coef_.pkl"
                        if os.path.exists(dest):
                            os.remove(dest)
                        os.rename(source_4, dest)
                    
                    elif val == 'coef_mnb.pkl':
                        source_4 = root + '/' + val
                        dest = dest_model + '/' + f"{customername}__{dataset_name}__MultinomialNB__{predfield}__Coef_.pkl"
                        if os.path.exists(dest):
                            os.remove(dest)
                        os.rename(source_4, dest)

                #UPDATING TRAINING TABLE FOR EDA PICKLE TRAINING 
                file_training = 'TrainingTbl.pkl'
                Training_dict = joblib.load(f"./data/{file_training}")
                TrainingTbl = {}
                TrainingTbl["DatasetID"] = dataset_id
                TrainingTbl["CustomerID"] =  customer_id
                TrainingTbl.update({"TrainingID" : 1, "TrainingStatus" : "InProgress", "LastTrainingBy" : session["user"], "LastTrainingDate" : str(datetime.now())[:19]})
                TrainingTbl.update(Training_dict)
                TrainingTbl['PredictedFields'][0]['VectorizationPklFile'] = f"{customername}__{dataset_name}__in_field__{predfield}__Approved__transformer.pkl"
                algopickle = TrainingTbl['PredictedFields'][0]["Algorithms"][0]["AlgorithmName"]
                print("algopickle: ",algopickle)
                print("algoname: ",algoname)

                MongoDBPersistence.training_hist_tbl.delete_many({'CustomerID':customer_id,"DatasetID":dataset_id})
                MongoDBPersistence.training_hist_tbl.insert_one(TrainingTbl)

                try:
                    for delfile in recieved_file_names:
                        if os.path.exists("./data/"  + str(delfile)):
                            os.remove("./data/" + str(delfile))
                    logging.error("Files deleted")
                except Exception as e:
                    logging.error("Files not deleted")

                result = MongoDBPersistence.datasets_tbl.find_one({"CustomerID": customer_id, "DatasetID":dataset_id},{"FieldSelections":1, "UniqueFields":1, "DependedPredict":1, "_id":0})
                if(result):
                    keys = result.keys()
                    if('DependedPredict' in keys and 'FieldSelections' in keys and result['DependedPredict'][0]['flag'] == 'true'):
                        for predict_field in result['FieldSelections'][0]['PredictedFields']:
                            if predict_field['usePredFieldFlag'] == 'true':
                                for dependend_field in result['DependedPredict'][0]['values']:
                                    if (predict_field['PredictedFieldName'] == dependend_field['PredictValue']):
                                        for dependend_value in dependend_field['DepPredictValue']:
                                            predict_field['InputFields'][predict_field['InputFields'].index(dependend_value)] = 'predicted_'+dependend_value
                        del result['DependedPredict']
                    resp = json_util.dumps(result)
                    logging.info('%s: Getting fields from dataset table in incidenttraining.py'%RestService.timestamp())
                    print('Response:',resp)
                    print('Result:',result)
                    return "success"
                    

                else:
                    resp = ''
                    logging.info('%s: FieldSelections not found in TblDataset in incidenttraining.py, returning empty string...'%RestService.timestamp())
                
                    return "success"


            elif trainingMode=='IIA':
                if not file:
                    return "No file"
                elif(not '.zip' in str(file) and not '.csv' in str(file)):
                    return "Upload either zip file or csv file."
                
                if '.zip' in str(file):
                    streamm = BytesIO(file.read())
                    zf = zipfile.ZipFile(streamm, "r")
                    expected_file_names = ['DatasetTable.pkl', 'IIAupdate.pkl', 'LogisticRegression_model.pkl', 'Logisticparameters.pkl', 'MultinomialNB_model.pkl', 'Multinomialparameters.pkl', 'RandomForestClassifier_model.pkl', 'RandomForrestparameters.pkl', 'SVCParameters.pkl', 'SVC_model.pkl', 'TrainingTbl.pkl', 'XgBoostparameters.pkl', 'additionalcolumns.pkl', 'coef_lr.pkl', 'coef_mnb.pkl', 'coef_rf.pkl', 'columnTransformer.pkl', 'id_to_label.pkl', 'preprocessed_train.csv', 'vocabulary.pkl']
                    recieved_file_names = []
                    for fileinfo in zf.infolist():
                        print(f"file_name: {fileinfo.filename}")
                        file_name = fileinfo.filename.split("/")[-1]
                        print(f"split file_name: {file_name}")
                        if str(file_name).strip() is not None and file_name != '' : 
                            recieved_file_names.append(file_name)
                    expected_file_names.sort()
                    recieved_file_names.sort()
                    print("expected_file_names: ",expected_file_names)
                    print("recieved_file_names :",recieved_file_names)
                    
                    if expected_file_names != recieved_file_names:
                        print("Invalid Files in Zip")
                        return "Invalid Files in Zip"

                    for fileinfo in zf.infolist():
                        print(fileinfo)
                        print(type(fileinfo)) 
                        bytes = zf.read(fileinfo)  
                        file_name = fileinfo.filename.split("/")[-1]
                        print(f"split file_name: {file_name}")
                        if str(file_name).strip() is not None and file_name != '' : 
                            with open(f"./data/{file_name}", "wb") as f:
                                f.write(bytes)
                    
                    dataset_ = MongoDBPersistence.teams_tbl.find_one({"CustomerID": customer_id,"TeamName":team_name},{"DatasetID":1,"_id":0})
                    if(dataset_):
                        dataset_dict = {}
                        #Dataset exist for the team
                        logging.info('%s: Getting old dataset details.'%RestService.timestamp())
                        dataset_id = dataset_["DatasetID"]
                    else:
                        #Newly adding the dataset
                        logging.info('%s: Adding new dataset.'%RestService.timestamp())
                        #getting max dataset id for the customer, so that new dataset id = old + 1
                        dataset_dict = MongoDBPersistence.datasets_tbl.find_one({"CustomerID" : customer_id, "DatasetID": {"$exists": True}},{'_id':0,"DatasetID":1}, sort=[("DatasetID", -1)])
                        if(dataset_dict):
                            last_dataset_id = dataset_dict['DatasetID']
                        else:
                            last_dataset_id = 0
                            logging.info('%s: Adding dataset for very first team.'%RestService.timestamp())
                
                        #New dataset id for the customer
                        dataset_id = last_dataset_id + 1
                        
                        new_dataset_dict = {}
                        new_dataset_dict["DatasetID"] = dataset_id
                        new_dataset_dict["DatasetName"] = dataset_name
                        new_dataset_dict["CustomerID"] =  customer_id
                        new_dataset_flag = 1

                    logging.info('%s: Trying to update TblTeams with Dataset details...'%RestService.timestamp())
                    MongoDBPersistence.teams_tbl.update_one({'CustomerID':customer_id, "TeamName":team_name}, \
                                {"$set": {"DatasetID":dataset_id}}, upsert=False)

                    print("In IIA - Going to add daraset id in assignment enable table for the team ", team_name)
                    team_doc = MongoDBPersistence.teams_tbl.find_one(
                        {'CustomerID': customer_id, "TeamName": team_name})
                    team_id = team_doc["TeamID"]
                    MongoDBPersistence.assign_enable_tbl.update_one({"TeamID": team_id},
                                                                    {"$set": {"DatasetID": dataset_id}},
                                                                    upsert=False)
                    print("Dataset_id added!")

                    #UPDATING INCIDENT TRAINING FOR IIA ZIP TRAINING
                    df = pd.read_csv("./data/preprocessed_train.csv")
                    df['DatasetID'] = dataset_id
                    df['CustomerID'] = customer_id
                    df['TrainingFlag']= 0
                    dict_training = df.to_dict(orient='records')
                    MongoDBPersistence.training_tickets_tbl.delete_many({'CustomerID':customer_id,"DatasetID":dataset_id})
                    MongoDBPersistence.training_tickets_tbl.insert_many(dict_training)

                    #UPDATING ALGORITHM TABLE FOR IIA ZIP TRAINING
                    MongoDBPersistence.algo_tbl.drop()
                    file_training_lr = 'Logisticparameters.pkl'
                    Algorithm_dict_Lr = joblib.load(f"./data/{file_training_lr}")
                    Algorithm_dict_Lr['RecordCreatedDate'] = str(datetime.now())[:19]
                    MongoDBPersistence.algo_tbl.insert_one(Algorithm_dict_Lr)

                    file_training_rf = 'RandomForrestparameters.pkl'
                    Algorithm_dict_rf = joblib.load(f"./data/{file_training_rf}")
                    Algorithm_dict_rf['RecordCreatedDate'] = str(datetime.now())[:19]
                    MongoDBPersistence.algo_tbl.insert_one(Algorithm_dict_rf)

                    file_training_svc = 'SVCParameters.pkl'
                    Algorithm_dict_svc = joblib.load(f"./data/{file_training_svc}")
                    Algorithm_dict_svc['RecordCreatedDate'] = str(datetime.now())[:19]
                    MongoDBPersistence.algo_tbl.insert_one(Algorithm_dict_svc)

                    file_training_mb = 'Multinomialparameters.pkl'
                    Algorithm_dict_mb = joblib.load(f"./data/{file_training_mb}")
                    Algorithm_dict_mb['RecordCreatedDate'] = str(datetime.now())[:19]
                    MongoDBPersistence.algo_tbl.insert_one(Algorithm_dict_mb)

                    file_training_xg = 'XgBoostparameters.pkl'
                    Algorithm_dict_xg = joblib.load(f"./data/{file_training_xg}")
                    Algorithm_dict_xg['RecordCreatedDate'] = str(datetime.now())[:19]
                    MongoDBPersistence.algo_tbl.insert_one(Algorithm_dict_xg)

                    # UPDATING DATASET TABLE 
                    file_dataset = 'DatasetTable.pkl'
                    Dataset_dict = joblib.load(f"./data/{file_dataset}")
                    datasettbl = {}
                    datasettbl["DatasetID"] = dataset_id
                    datasettbl["DatasetName"] = dataset_name
                    datasettbl["CustomerID"] =  customer_id
                    datasettbl.update(Dataset_dict)
                    del datasettbl['TrainingStatus']
                    del datasettbl['IdToLabels']
                    datasettbl['GridsearchParams'] = {'AlgoParamsLR' : {"AlgorithmName": Algorithm_dict_Lr['AlgorithmName'],"Parameters": Algorithm_dict_Lr['DefaultParametersSingle'][0]},
                                                      'AlgoParamsRF' : {"AlgorithmName":Algorithm_dict_rf['AlgorithmName'],"Parameters":Algorithm_dict_rf['DefaultParametersSingle'][0]},
                                                      'AlgoParamsSVC' : {"AlgorithmName": Algorithm_dict_svc['AlgorithmName'],"Parameters": Algorithm_dict_svc['DefaultParametersSingle'][0]},
                                                      'AlgoParamsMNB' : {"AlgorithmName": Algorithm_dict_mb['AlgorithmName'],"Parameters":Algorithm_dict_mb['DefaultParametersSingle'][0]},
                                                      'AlgoParamsXGB' : {"AlgorithmName": Algorithm_dict_xg['AlgorithmName'],"Parameters": Algorithm_dict_xg['DefaultParametersSingle'][0]}}

                    datasettbl.update({'training_mode' : "IIA"})
                    MongoDBPersistence.datasets_tbl.insert_one(datasettbl)

                    try:
                        for delfile in recieved_file_names:
                            if os.path.exists("./data/"  + str(delfile)):
                                os.remove("./data/" + str(delfile))
                        logging.error("Files deleted")
                    except Exception as e:
                        logging.error("Files not deleted")

                    result = MongoDBPersistence.datasets_tbl.find_one({"CustomerID": customer_id, "DatasetID":dataset_id},{"FieldSelections":1, "UniqueFields":1, "DependedPredict":1, "_id":0})
                    if(result):
                        keys = result.keys()
                        if('DependedPredict' in keys and 'FieldSelections' in keys and result['DependedPredict'][0]['flag'] == 'true'):
                            for predict_field in result['FieldSelections'][0]['PredictedFields']:
                                if predict_field['usePredFieldFlag'] == 'true':
                                    for dependend_field in result['DependedPredict'][0]['values']:
                                        if (predict_field['PredictedFieldName'] == dependend_field['PredictValue']):
                                            for dependend_value in dependend_field['DepPredictValue']:
                                                predict_field['InputFields'][predict_field['InputFields'].index(dependend_value)] = 'predicted_'+dependend_value
                            del result['DependedPredict']
                        resp = json_util.dumps(result)
                        logging.info('%s: Getting fields from dataset table in incidenttraining.py'%RestService.timestamp())
                        print('Response:',resp)
                        print('Result:',result)
                        return "success"

                    else:
                        resp = ''
                        logging.info('%s: FieldSelections not found in TblDataset in incidenttraining.py, returning empty string...'%RestService.timestamp())
                    
                        return "success"
                
                    

                if '.csv' in str(file):
                    dataset_ = MongoDBPersistence.teams_tbl.find_one({"CustomerID": customer_id,"TeamName":team_name},{"DatasetID":1,"_id":0})
                    if(dataset_):
                        dataset_dict = {}
                        #Dataset exist for the team
                        logging.info('%s: Getting old dataset details.'%RestService.timestamp())
                        dataset_id = dataset_["DatasetID"]
                    else:
                        #Newly adding the dataset
                        logging.info('%s: Adding new dataset.'%RestService.timestamp())
                        #getting max dataset id for the customer, so that new dataset id = old + 1
                        dataset_dict = MongoDBPersistence.datasets_tbl.find_one({"CustomerID" : customer_id, "DatasetID": {"$exists": True}},{'_id':0,"DatasetID":1}, sort=[("DatasetID", -1)])
                        if(dataset_dict):
                            last_dataset_id = dataset_dict['DatasetID']
                        else:
                            last_dataset_id = 0
                            logging.info('%s: Adding dataset for very first team.'%RestService.timestamp())
                
                        #New dataset id for the customer
                        dataset_id = last_dataset_id + 1
                        
                        new_dataset_dict = {}
                        new_dataset_dict["DatasetID"] = dataset_id
                        new_dataset_dict["DatasetName"] = dataset_name
                        new_dataset_dict["CustomerID"] =  customer_id
                        new_dataset_dict["training_mode"] =  "IIA"
                        new_dataset_flag = 1

                    stream = io.StringIO(file.stream.read().decode("latin-1"),newline=None)
                    csv_input = csv.reader(stream)
                    df_data =[]
                
                    for row in csv_input:
                        df_data.append(row)
                    headers =  df_data.pop(0)
                    headers = [c.lower()  for c in headers]
                    
                    df = pd.DataFrame(df_data,columns=headers)
                    list_columns = list(df.columns)
                    df['CustomerID']=customer_id
                    df['DatasetID']=dataset_id
                    df['TrainingFlag']=0
            
                    list_columns = ["_".join(re.sub("[^a-zA-Z]"," ",col).strip().split(" ")) for col in list_columns]
            
                    if(ticket_id_field_name not in df.columns):
                        logging.info('%s: Please rename ticket_id/Incident_id column to "number".'%RestService.timestamp())
                        return 'failure'

                    #remove special chars between the name of column
                    df.columns = ["_".join(re.sub("[^a-zA-Z]"," ",col).strip().split(" ")) for col in df.columns]

                    #Remove duplicate columns if there any (Based on Incident number)
                    df.drop_duplicates(subset =ticket_id_field_name, keep = 'first', inplace = True)
                    csv_df_cols = df.columns

                    if(len(set(csv_df_cols))<len(csv_df_cols)):
                        logging.info('%s: Duplicate columns, please rename the duplicate column names..'%RestService.timestamp())
                        return 'failure'

                    try:
                        ColNames = list(MongoDBPersistence.datasets_tbl.find({'CustomerID':customer_id, "DatasetID": dataset_id},{"ColumnNames":1, "_id":0}))
                        print("ColNames:" ,ColNames)
                        if not (ColNames):
                            current_row_count = df.shape[0]
                            prev_ticket_count = MongoDBPersistence.datasets_tbl.find_one({"CustomerID": customer_id,"DatasetID":dataset_id},{"TicketCount":1,"_id":0})
                            if(prev_ticket_count):
                                prev_ticket_count = prev_ticket_count['TicketCount']
                                row_count = current_row_count + prev_ticket_count
                            else:
                                row_count = current_row_count
                            new_dataset_dict["TicketCount"] = row_count
                            new_dataset_dict["ColumnNames"] = list_columns
                            logging.info('%s: Trying to insert records into TblIncidentTraining...'%RestService.timestamp())
                            json_str = df.to_json(orient='records')
                            json_data = json.loads(json_str)
                            
                            MongoDBPersistence.training_tickets_tbl.insert_many(json_data)
                            logging.info('%s: Trying to insert new dataset into TblDataset...'%RestService.timestamp())
                            MongoDBPersistence.datasets_tbl.insert_one(new_dataset_dict)

                            logging.info('%s: Trying to update TblTeams with Dataset details...'%RestService.timestamp())
                            MongoDBPersistence.teams_tbl.update_one({'CustomerID':customer_id, "TeamName":team_name}, \
                            {"$set": {"DatasetID":dataset_id}}, upsert=False)
                            print("In IIA - Going to add daraset id in assignment enable table for the team ",
                                  team_name)
                            team_doc = MongoDBPersistence.teams_tbl.find_one(
                                {'CustomerID': customer_id, "TeamName": team_name})
                            team_id = team_doc["TeamID"]
                            MongoDBPersistence.assign_enable_tbl.update_one({"TeamID": team_id},
                                                                            {"$set": {"DatasetID": dataset_id}},
                                                                            upsert=False)
                            print("Dataset_id added!")
                            resp = 'success'
                        
                        else:
                            oldColNames = ColNames[0]["ColumnNames"]
                            oldColNames.sort()
                            list_columns.sort()
                            print("OldColNames are : ", oldColNames)
                            print("list_columns are : ", list_columns)
                            

                            if(oldColNames==list_columns):
                                resp_col = "Columns are matching, proceeding ahead"
                                print("df:" ,df)
                                Tickets = MongoDBPersistence.training_tickets_tbl.find({'CustomerID':customer_id,'DatasetID':dataset_id},{'_id':0 })
                                new_df = pd.DataFrame.from_dict(Tickets)
                                new_df = new_df.drop(['CustomerID','DatasetID','TrainingFlag'],axis=1)
                                df_without_duplicates = df.loc[df.index.difference(df.merge(new_df, how='inner', on=ticket_id_field_name).index)]
                                df_without_duplicates = df_without_duplicates.reset_index(drop=True)
                                print("df_without_duplicates:" ,df_without_duplicates)
                                current_row_count = df_without_duplicates.shape[0]
                                prev_ticket_count = MongoDBPersistence.datasets_tbl.find_one({"CustomerID": customer_id,"DatasetID":dataset_id},{"TicketCount":1,"_id":0})
                                if(prev_ticket_count):
                                    prev_ticket_count = prev_ticket_count['TicketCount']
                                    row_count = current_row_count + prev_ticket_count
                                else:
                                    row_count = current_row_count
                                dataset_dict["TicketCount"] = row_count
                                dataset_dict["ColumnNames"] = list_columns
                                logging.info('%s: Trying to insert records into TblIncidentTraining...'%RestService.timestamp())
                                json_str = df_without_duplicates.to_json(orient='records')
                                json_data = json.loads(json_str)
                                
                                MongoDBPersistence.training_tickets_tbl.insert_many(json_data)
                                MongoDBPersistence.datasets_tbl.update_one({'CustomerID':customer_id, "DatasetID": dataset_id},\
                                {"$set": {"TicketCount" : dataset_dict["TicketCount"], "ColumnNames" : dataset_dict["ColumnNames"]}}, upsert=False)

                                resp = 'success'

                            else:
                                resp_col = "Upload failed, please upload the right dataset"
                                resp = 'failure'
                            print("resp while comparing two dfs>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.",resp_col)

                    except Exception as e:
                        logging.error('%s: Error occurred: %s '%(RestService.timestamp(),str(e)))
                        logging.error('%s: Possible error: Data format in csv not matching with database constarints.(unique key & not null)'%RestService.timestamp())
                        resp = 'failure'
                    return resp

    @staticmethod
    def cleaningInputFields(df,in_field):
        print("Inside line break method")
        logging.info("inside cleaningInputFields")
        for index, row in df.iterrows():
            row[in_field] = re.sub(r'\n', " ", row[in_field])
            row[in_field] = re.sub("[^A-Za-z0-9]+", " ", row[in_field])
            df[in_field][index] = row[in_field].lower()
        return df

    #Refresh Training Records API
    @staticmethod
    def deleteTrainingRecords(customer_id,dataset_id,team_name):
        try:
            print('inside deleteTrainingRecords')
            out_dict={}
            #checking file is csv
            file = request.files['trainingData']
            if not file:
                out_dict['status']='Error: No File'
                print('No file')
                return json_util.dumps(out_dict)
            elif(not '.csv' in str(file)):
                out_dict['status']="Error: Upload csv file."
                print('Upload csv file.')
                return json_util.dumps(out_dict)
            
            #reading csv
            stream = io.StringIO(file.stream.read().decode("latin-1"),newline=None)
            csv_input = csv.reader(stream)
            df_data =[]

            for row in csv_input:
                df_data.append(row)

            headers =  df_data.pop(0)
            headers = [c.lower()  for c in headers]
            df = pd.DataFrame(df_data,columns=headers)
            list_columns = list(df.columns)

            #check column names from csv with db records
            print(customer_id,dataset_id)
            team_doc=MongoDBPersistence.training_tickets_tbl.find_one({"CustomerID":customer_id,"DatasetID":dataset_id},
                                                            {"_id":0,"CustomerID":0,"DatasetID":0,"TrainingFlag":0})
            print(team_doc)
            list_columns_db = list(dict(team_doc).keys())
            
            if set(list_columns) == set(list_columns_db):

                #Delete existing training records
                MongoDBPersistence.training_tickets_tbl.delete_many({"CustomerID":customer_id,"DatasetID":dataset_id})

                #creating df for new training records
                df['CustomerID']=customer_id
                df['DatasetID']=dataset_id
                df['TrainingFlag']=0

                df.drop_duplicates(subset =ticket_id_field_name, keep = 'first', inplace = True)
                csv_df_cols = df.columns

                if(len(set(csv_df_cols))<len(csv_df_cols)):
                    logging.info('%s: Duplicate columns, please rename the duplicate column names..'%RestService.timestamp())
                    out_dict['status']='Failure: Duplicate columns, please rename the duplicate column names.'
                    return json_util.dumps(out_dict)

                json_str = df.to_json(orient='records')
                json_data = json.loads(json_str)

                try:
                    logging.info('%s: Trying to insert records into TblIncidentTraining...'%RestService.timestamp())
                    MongoDBPersistence.training_tickets_tbl.insert_many(json_data)

                    dataset_dict={}
                    dataset_dict["TicketCount"] = df.shape[0]
                    MongoDBPersistence.datasets_tbl.update_one({'CustomerID':customer_id, "DatasetID": dataset_id},
                                                            {"$set": {"TicketCount" : dataset_dict["TicketCount"]}}, 
                                                            upsert=False)
                    logging.info('%s: Records inserted successfully.'%RestService.timestamp())
                    out_dict['status']='success'

                except Exception as e:
                    logging.error('%s: Error occurred: %s '%(RestService.timestamp(),str(e)))
                    logging.error('%s: Possible error: Data format in csv not matching with database constarints.(unique key & not null)'%RestService.timestamp())
                    out_dict['status']='Failure'
                return json_util.dumps(out_dict)
            else:
                logging.error(f'Different column names in the csv.')
                out_dict['status']='Failure: Different column names in the csv.'
                return json_util.dumps(out_dict)
        except Exception as e:
            out_dict['status']='Failure'
            print(str(e))
            return json_util.dumps(out_dict)

    