__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

import os
from datetime import datetime

import pandas as pd
import requests
from bson import json_util
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from xgboost import XGBClassifier

from iia.incident.incidenttraining import IncidentTraining
from iia.masterdata.customers import CustomerMasterData
from iia.persistence.mongodbpersistence import MongoDBPersistence
from iia.restservice import RestService
from iia.training.training import Training
from iia.utils.log_helper import get_logger
from iia.utils.utils import Utils

logging = get_logger(__name__)


class Retrain(object):
    '''
    classdocs
    '''

    def __init__(self, params):
        '''
        Constructor
        '''

    # api for retrain method
    @staticmethod
    def retrain(customer_id, dataset_id):
        # Get User parameters JSON
        user_param_choices = {}

        training_status = "Retraining"
        logging.info("%s: Retraining the dataset(DatasetID:%d)." % (RestService.timestamp(), dataset_id))
        JobSettings = MongoDBPersistence.datasets_tbl.find_one({"CustomerID": customer_id, "DatasetID": dataset_id},
                                                               {"JobSettings": 1,
                                                                "_id": 0})  # Fetch from TblDataset JobSettings
        if (JobSettings):
            max_untrained_setting = JobSettings['JobSettings']['MinUntrained']
        else:
            logging.info(
                "%s: Job setting not found for the dataset(DatasetID:%d)." % (RestService.timestamp(), dataset_id))
        max_untrained = MongoDBPersistence.training_tickets_tbl.find(
            {"CustomerID": customer_id, "DatasetID": dataset_id,
             "TrainingFlag": 0}).count()  # Count in TblIncidentTraining where TrainingFlag = 0
        if (max_untrained < max_untrained_setting):
            logging.info("%s: Insufficient untrained tickets for retraining the dataset(DatasetID:%d)." % (
                RestService.timestamp(), dataset_id))
            return
        logging.info("%s: Retraining in progress..." % (RestService.timestamp()))
        # Fetch default parameters
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

        cust_name_dict = MongoDBPersistence.customer_tbl.find_one({'CustomerID': customer_id},
                                                                  {'CustomerName': 1, '_id': 0})
        if (cust_name_dict):
            cust_name = cust_name_dict['CustomerName']
        else:
            logging.info('%s: Customer not found in the record.' % RestService.timestamp())
        # Getting dataset details
        dataset_info_dict = MongoDBPersistence.datasets_tbl.find_one(
            {'CustomerID': customer_id, "DatasetID": dataset_id},
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
        # retrain will pickup i/o choices from TblCustomer which status is Approved
        pred_list = []
        for pred_fields in fieldselection_list:
            if (pred_fields['FieldsStatus'] == 'Approved'):
                pred_list = pred_fields['PredictedFields']
        if (len(pred_list) == 0):
            logging.info("%s: Failure: Customer didn't choose any fields." % RestService.timestamp())
            return 'failure'
        pred_field_list = []
        for pre_field in pred_list:
            pred_field_list.append(pre_field['PredictedFieldName'])
        predicted_fields_data = []

        additional_fields = pred_list[0]['Additionalfields']

        # Clean previous Retraining records
        Training.clean_TblTraining(customer_id, dataset_id, training_status)
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

            additional_doc = {'_id': 0}
            for each_field in additional_fields:
                additional_doc.update({each_field: 1})
            logging.info(f"additional_doc:{additional_doc}")
            # Concatinating input fields together into in_field
            input_df = pd.DataFrame()
            input_df = pd.DataFrame(
                list(MongoDBPersistence.training_tickets_tbl.find({'CustomerID': customer_id, "DatasetID": dataset_id},
                                                                  {'_id': 0, input_field_list[0]: 1})))

            additional_df = pd.DataFrame()
            additional_df = pd.DataFrame(
                list(MongoDBPersistence.training_tickets_tbl.find({'CustomerID': customer_id, "DatasetID": dataset_id},
                                                                  additional_doc)))  # ,pred_field:{"$exists":True,"$ne": ""}
            list_addtional_fields = list(additional_df.columns)
            for input_field_ in input_field_list[1:]:
                input_df[input_field_] = pd.DataFrame(list(
                    MongoDBPersistence.training_tickets_tbl.find({'CustomerID': customer_id, "DatasetID": dataset_id},
                                                                 {'_id': 0, input_field_: 1})))

            input_df['in_field'] = ''
            for field in input_field_list:
                if (input_df[field] is None):
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
            print("training_tkt_df:", training_tkt_df.columns)

            # Skips those tickets where there is no description field
            logging.info(
                '%s: Number of columns before cleaning: %d.' % (RestService.timestamp(), training_tkt_df.shape[0]))
            training_tkt_df = training_tkt_df[(training_tkt_df[in_field] != "")]
            training_tkt_df = training_tkt_df[(training_tkt_df[pred_field] != "")]
            training_tkt_df = training_tkt_df.dropna(how='any', axis=0)  # IMP step
            logging.info(
                '%s: Number of columns after cleaning: %d.' % (RestService.timestamp(), training_tkt_df.shape[0]))

            #######calling an api request for custom preprocessing file ################
            custom_processing_flag, custom_url = CustomerMasterData.check_custom("customPreprocessing")
            if (custom_processing_flag == 'failure'):
                logging.info("%s: Not able to read values from Configure File" % RestService.timestamp())
                return "failure"

            elif (custom_processing_flag == "True"):
                try:
                    logging.info(
                        "%s Custom processing is present invoking Custom preprocessing " % RestService.timestamp())
                    req_head = {"Content-Type": "application/json"}
                    post_data = {"CustomerID": customer_id, "data": training_tkt_df}
                    proxies = {"http": None, "https": None}
                    api = custom_url + "api/custom_preprocessing"
                    req_response = requests.post(api, data=json_util.dumps(post_data), headers=req_head,
                                                 proxies=proxies)
                    training_tkt_df = pd.DataFrame.from_dict(req_response.json(), orient="columns")
                except Exception as e:
                    training_tkt_df = IncidentTraining.cleaningInputFields(training_tkt_df, in_field)
            else:
                training_tkt_df = IncidentTraining.cleaningInputFields(training_tkt_df, in_field)

            training_tkt_df['category_id'] = training_tkt_df[pred_field].factorize()[0]

            model = Utils(training_tkt_df, customer_id, dataset_id, pred_field, in_field, training_status,
                          additional_fields)
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
                    try:
                        if (algo_name == 'XGBClassifier'):
                            parameters = algo['Parameters']
                            algo_param_dict['Parameters'] = parameters
                            param_grid = {}
                            for parameter in parameters:
                                if (parameter["ParameterName"] == 'n_estimators'):
                                    param_grid['n_estimators'] = int(parameter['Value'])
                                elif (parameter["ParameterName"] == 'objective'):
                                    param_grid['objective'] = parameter['Value']
                                    # Check whether we got n_estimators, objective
                            logging.info(
                                '%s: Started training with %s algorithm.' % (RestService.timestamp(), algo_name))
                            score_dict = model.classify(model=XGBClassifier(n_estimators=param_grid['n_estimators'],
                                                                            objective=param_grid['objective']))
                            logging.info('%s: Model has been trained successfully using %s algorithm.' % (
                            RestService.timestamp(), algo_name))
                            parameters = algo['Parameters']

                        elif (algo_name == 'RandomForestClassifier'):
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
                            logging.info(
                                '%s: Started training with %s algorithm.' % (RestService.timestamp(), algo_name))
                            # Check whether we got n_estimators, criterion, max_depth values
                            score_dict = model.classify(
                                model=RandomForestClassifier(n_estimators=param_grid['n_estimators'],
                                                             criterion=param_grid['criterion'],
                                                             max_depth=param_grid['max_depth']))
                            logging.info('%s: Model has been trained successfully using %s algorithm.' % (
                            RestService.timestamp(), algo_name))
                        elif (algo_name == 'SVC'):
                            parameters = algo['Parameters']
                            algo_param_dict['Parameters'] = parameters
                            param_grid = {}
                            for parameter in parameters:
                                if (parameter["ParameterName"] == 'C'):
                                    param_grid['C'] = parameter['Value']
                                elif (parameter["ParameterName"] == 'kernel'):
                                    param_grid['kernel'] = parameter['Value']
                            logging.info(
                                '%s: Started training with %s algorithm.' % (RestService.timestamp(), algo_name))
                            score_dict = model.classify(
                                model=SVC(C=param_grid['C'], kernel=param_grid['kernel'], probability=True))
                            logging.info('%s: Model has been trained successfully using %s algorithm.' % (
                            RestService.timestamp(), algo_name))

                        elif (algo_name == 'MultinomialNB'):
                            parameters = algo['Parameters']
                            algo_param_dict['Parameters'] = parameters
                            param_grid = {}
                            for parameter in parameters:
                                if (parameter["ParameterName"] == 'alpha'):
                                    param_grid['alpha'] = parameter['Value']
                            logging.info(
                                '%s: Started training with %s algorithm.' % (RestService.timestamp(), algo_name))
                            score_dict = model.classify(model=MultinomialNB(alpha=param_grid['alpha']))
                            logging.info('%s: Model has been trained successfully using %s algorithm.' % (
                            RestService.timestamp(), algo_name))

                        elif (algo_name == 'LogisticRegression'):
                            parameters = algo['Parameters']
                            algo_param_dict['Parameters'] = parameters
                            param_grid = {}
                            for parameter in parameters:
                                if (parameter["ParameterName"] == 'C'):
                                    param_grid['C'] = parameter['Value']
                            logging.info(
                                '%s: Started training with %s algorithm.' % (RestService.timestamp(), algo_name))
                            score_dict = model.classify(model=LogisticRegression(C=param_grid['C'], random_state=42))
                            logging.info('%s: Model has been trained successfully using %s algorithm.' % (
                            RestService.timestamp(), algo_name))

                        else:
                            logging.info(
                                '%s: There is no model defined for %s algorithm. Use RandomForestClassifier/LogisticRegression/MultinomialNB/SVC' % (
                                    RestService.timestamp(), algo))
                            continue

                        f_accuracy = float("{0:.4f}".format(score_dict['Accuracy']))
                        F1_score_ = float("{0:.4f}".format(score_dict['F1_score']))
                        precision_score_ = float("{0:.4f}".format(score_dict['Precision']))
                        recall_score_ = float("{0:.4f}".format(score_dict['Recall']))
                    except Exception as e:
                        logging.error('%s: Error occurred: %s ' % (RestService.timestamp(), str(e)))

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
        tbl_training_row["PredictedFields"] = predicted_fields_data
        tbl_training_row["AlgorithmParameters"] = algorithms_params
        try:
            logging.info('%s: Trying to insert calculated accuracies into TblTraining.' % RestService.timestamp())
            MongoDBPersistence.training_hist_tbl.insert_one(tbl_training_row)
            MongoDBPersistence.training_tickets_tbl.update_many({'CustomerID': customer_id, "DatasetID": dataset_id},
                                                                {"$set": {"TrainingFlag": 1}})
            logging.info(
                '%s: Accuracies recorded successfully into TblTraining. TrainingID: %d' % (
                RestService.timestamp(), training_id))
        except Exception as e:
            logging.error('%s: Error occurred: %s ' % (RestService.timestamp(), str(e)))
            logging.error('%s: Check whether data following the database constarints.' % (RestService.timestamp()))
            return json_util.dumps('failure')
        return json_util.dumps(training_id)
