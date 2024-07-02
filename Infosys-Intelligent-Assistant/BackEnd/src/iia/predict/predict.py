__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

from iia.itsm.adapter import ITSMAdapter
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from iia.persistence.mongodbpersistence import MongoDBPersistence
from iia.persistence.mappingpersistence import MappingPersistence
from iia.masterdata.customers import CustomerMasterData
from iia.restservice import RestService
from nltk.cluster.util import cosine_distance
from iia.masterdata.resources import ResourceMasterData
from iia.itsm.servicenow import ServiceNow
from pathlib import Path
import joblib
from bson import json_util
from flask import request
import json
import pandas as pd
import re
import csv
import importlib
import configparser
import subprocess
from iia.incident.incidenttraining import IncidentTraining
import os
import requests
from flask import session
from iia.masterdata.assignment import Assignment
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
from iia.masterdata.datasets import DatasetMasterData
import spacy
import operator
from iia.utils.log_helper import get_logger, log_setup

logging = get_logger(__name__)
log_setup()
app = RestService.getApp()
from datetime import datetime
import time
from twilio.rest import Client
import pymsteams
from iia.resolution.RPA_Resolution import RPA_Resolution
from iia.resolution.resolution import Resolution
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial
from itertools import repeat


app.secret_key = "iia-secret-key"

core_web_model = spacy.load('en_core_web_md')

@app.route('/api/predict/<int:customer_id>', methods=['GET'])
def predict(customer_id):

    return Predict.predict(customer_id)


@app.route('/api/predictAPI/<int:customer_id>/<int:dataset_id>/<description>/<pred_field>', methods=['GET'])
def predictAPI(customer_id, dataset_id, description, pred_field):
    return Predict.predictAPI(customer_id, dataset_id, description, pred_field)


@app.route("/api/predictedTickets/<int:customer_id>/<int:dataset_id>", methods=["GET"])
def getPredictedTickets(customer_id, dataset_id):
    return Predict.getPredictedTickets(customer_id, dataset_id)


@app.route("/api/predicted/<int:customer_id>/<int:dataset_id>/<ticket_id>", methods=["GET"])
def getPredictedData(customer_id, dataset_id, ticket_id):
    return Predict.getPredictedData(customer_id, dataset_id, ticket_id)

@app.route("/api/predictedfields/<int:customer_id>/<chosen_team>")
def getPredictedFields(customer_id, chosen_team):
    return Predict.getPredictedFields(customer_id, chosen_team)


@app.route("/api/updatePredictedDetails/<int:customer_id>/<int:dataset_id>", methods=["PUT"])
def updatePredictedDetails(customer_id, dataset_id):
    return Predict.updatePredictedDetails(customer_id, dataset_id)


@app.route("/api/getfirstPredDataSetID", methods=["GET"])
def getfirstPredDataSetID():
    logging.info("Calling getfirstPredDataSetID")
    return Predict.getfirstPredDataSetID()

@app.route("/api/getPredictedTicktesForPage/<int:customer_id>/<int:dataset_id>/<int:page_size>/<int:page_num>/<prev_pred_state>/<show_app_ticket>")
def getPredictedTicketsForPage(customer_id, dataset_id, page_size, page_num, prev_pred_state, show_app_ticket):
    return Predict.getPredictedTicketsForPage(customer_id, dataset_id, page_size, page_num, prev_pred_state, show_app_ticket)

@app.route("/api/predictedTicketsCount/<int:customer_id>/<int:dataset_id>/<prev_pred_state>", methods=["GET"])
def getPredictedTicketsCount(customer_id, dataset_id, prev_pred_state):
    return Predict.getPredictedTicketsCount(customer_id, dataset_id, prev_pred_state)

@app.route("/api/assignmentEnableStatus/<field>/<current_status>/<int:customer_id>/<chosen_team>", methods=["PUT"])
def assignmentEnableStatus(field, current_status, customer_id, chosen_team):
    return Predict.assignmentEnableStatus(field, current_status, customer_id, chosen_team)

@app.route("/api/getSwitchStatus/<int:customer_id>/<chosen_team>", methods=["GET"])
def getSwitchStatus(customer_id,chosen_team):
    return Predict.getSwitchStatus(customer_id,chosen_team)

@app.route("/api/hinglishEnableStatus/<field>/<current_status>/<int:customer_id>/<chosen_team>", methods=["PUT"])
def hinglishEnableStatus(field, current_status, customer_id, chosen_team):
    return Predict.hinglishEnableStatus(field, current_status, customer_id, chosen_team)

@app.route("/api/insertTValue/<int:customer_id>/<chosen_team>", methods=["POST"])
def insertTValue(customer_id, chosen_team):
    return Predict.insertTValue(customer_id, chosen_team)

@app.route("/api/insertIopsStatus/<status>/<int:customer_id>/<chosen_team>", methods=["POST"])
def insertIopsStatus(status,customer_id, chosen_team):
    return Predict.insertIopsStatus(status,customer_id, chosen_team)

@app.route("/api/insertIopsPath", methods=["POST"])
def insertIopsPath():
    return Predict.insertIopsPath()

@app.route("/api/insertAccuracyPercent/<percent>/<int:customer_id>", methods=["POST"])
def insertAccuracyPercent(percent, customer_id):
    return Predict.insertAccuracyPercent(percent, customer_id)

@app.route("/api/insertITSMSourceDetails", methods=["POST"])
def insertITSMSourceDetails():
    return Predict.insertITSMSourceDetails()

@app.route("/api/insertFileSourceDetails", methods=["POST"])
def insertFileSourceDetails():
    return Predict.insertFileSourceDetails()

@app.route("/api/insertSharepointSourceDetails", methods=["POST"])
def insertSharepointSourceDetails():
    return Predict.insertSharepointSourceDetails()

@app.route("/api/getMatchPercentage", methods=["GET"])
def getMatchPercentage():
    return Predict.getMatchPercentage()

@app.route("/api/getiOpsValues/<int:customer_id>/<chosen_team>", methods=["GET"])
def getiOpsValues(customer_id, chosen_team):
    return Predict.getiOpsValues(customer_id, chosen_team)

@app.route("/api/saveDefaultKBSource/<source>", methods=["POST"])
def saveDefaultKBSource(source):
    return Predict.saveDefaultKBSource(source)

@app.route("/api/getDefaultKBSource", methods=["GET"])
def getDefaultKBSource():
    return Predict.getDefaultKBSource()

@app.route("/api/getdefaultSourceDetails", methods=["GET"])
def getDefaultSourceDetails():
    return Predict.getDefaultSourceDetails()

@app.route("/api/predictionEnableStatus/<field>/<current_status>/<int:customer_id>/<chosen_team>", methods=["PUT"])
def predictionEnableStatus(field, current_status, customer_id, chosen_team):
    return Predict.predictionEnableStatus(field, current_status, customer_id, chosen_team)

@app.route("/api/importantFeaturesReport/<int:customer_id>/<int:dataset_id>/<number>", methods=["GET"])
def importantFeaturesReport(customer_id, dataset_id, number):
    return Predict.importantFeaturesReport(customer_id, dataset_id, number)

@app.route(
    "/api/sortAndFilter/<int:customer_id>/<int:dataset_id>/<filter_field>/<filter_value>/<sort_field>/<sort_value>/<int:page_size>/<int:page_num>/<prev_pred_state>/<show_app_ticket>",
    methods=["GET"])
def sortAndFilter(customer_id, dataset_id, filter_field, filter_value, sort_field, sort_value, page_size, page_num,
                  prev_pred_state, show_app_ticket):
    return Predict.sortAndFilter(customer_id, dataset_id, filter_field, filter_value, sort_field, sort_value, page_size,
                                 page_num, prev_pred_state, show_app_ticket)

@app.route("/api/itsmUsers/<int:customer_id>/<method>", methods=["POST"])
def itsm_user_mapping(customer_id, method):
    return Predict.itsm_users(customer_id, method)

@app.route("/api/ticketsAssignedToUser/<int:customer_id>/<int:dataset_id>/<int:page_size>/<int:page_num>/<show_app_ticket>",
           methods=["GET"])
def assigned_to_user(customer_id, dataset_id, page_size, page_num,show_app_ticket):
    return Predict.tickets_assigned_to_user(customer_id, dataset_id, page_size, page_num, show_app_ticket)

@app.route("/api/roundRobinEnableStatus/<field>/<current_status>", methods=["PUT"])
def roundrobinEnableStatus(field, current_status):
    return Predict.roundrobinEnableStatus(field, current_status)

@app.route("/api/updateuserstatus/<int:customer_id>/<int:dataset_id>/<threshold_value>", methods=["GET"])
def update_user_status(customer_id, dataset_id, threshold_value):
    return Predict.update_user_status(customer_id, dataset_id, threshold_value)

class Predict(object):
    '''
    classdocs
    '''

    def __init__(self, params):
        '''
        Constructor
        '''

    ## depricated API 
    @staticmethod
    def predictAPI(customer_id, dataset_id, description, pred_field):
        final_predictions = {}

        cust_name = \
        MongoDBPersistence.customer_tbl.find_one({'CustomerID': customer_id}, {'CustomerName': 1, '_id': 0})[
            'CustomerName']
        dataset_info_dict = MongoDBPersistence.datasets_tbl.find_one(
            {'CustomerID': customer_id, "DatasetID": dataset_id}, {'DatasetName': 1, 'FieldSelections': 1, '_id': 0})
        if (dataset_info_dict):
            dataset_name = dataset_info_dict['DatasetName']
        else:
            logging.info('%s: Customer name not found in the record.' % RestService.timestamp())
            return "failure"
        fieldselection_list = dataset_info_dict['FieldSelections']

        # Pick up Approved customer choices
        for pred_fields in fieldselection_list:
            if (pred_fields['FieldsStatus'] == 'Approved'):
                pred_fields_choices_list = pred_fields['PredictedFields']

        pred_field_list = []
        for pre_field in pred_fields_choices_list:
            pred_field_list.append(pre_field['PredictedFieldName'])

        for input_field in pred_fields_choices_list:
            if (input_field['PredictedFieldName'] == pred_field):
                algoName = input_field['AlgorithmName']

        description_ = re.sub("[^_a-zA-Z]", " ", description)
        description = description_.lower()

        pred_output_result = []

        vocab_path = 'data/' + cust_name + "__" + dataset_name + '__' + "in_field" + "__" + pred_field + "__" + "Approved" + "__" + "transformer.pkl"
        model_path = 'models/' + cust_name + "__" + dataset_name + '__' + algoName + "__" + pred_field + "__" + "Approved" + "__" + "Model.pkl"
        vocab_file = Path(vocab_path)
        model_file = Path(model_path)
        if (vocab_file.is_file()):
            transformer = joblib.load(vocab_path)
        else:
            logging.info(
                '%s: Vocabulary file not found for %s field.. please train algo, save the choices & try again.' % (
                RestService.timestamp(), pred_field))
            return "failure"

        if (model_file.is_file()):
            fittedModel = joblib.load(model_file)
        else:
            logging.info(
                '%s: ML Model file not found for %s field.. please train algo, save the choices & try again.' % (
                RestService.timestamp(), pred_field))
            return 'failure'
        pred_output_result = fittedModel.predict(transformer.transform([description]))
        id_to_labels = MongoDBPersistence.datasets_tbl.find_one({'CustomerID': customer_id, "DatasetID": dataset_id},
                                                                {"_id": 0, "IdToLabels": 1})
        if (id_to_labels):
            id_to_labels_dict = id_to_labels["IdToLabels"]
        else:
            logging.info('%s: De-map data not found for %s field.' % (RestService.timestamp(), pred_field))

        predicted_label = id_to_labels_dict[str(pred_output_result[0])]
        final_predictions['Output'] = predicted_label

        ######################################## Updated ########################################
        confidence_score = float("{0:.2f}".format(max(fittedModel.predict_proba(tfidf.transform([description]))[0])))

        final_predictions['ConfidenceScore'] = confidence_score
        final_predictions['CustomerID'] = customer_id
        final_predictions['DatasetID'] = dataset_id
        return "sucess"

    @staticmethod
    def listflatten(lst):
        for elem in lst:
            if type(elem) in (tuple, list):
                for i in Predict.listflatten(elem):
                    yield i
            else:
                yield elem

    @staticmethod
    def tick_to_approved(ticket, regex_dictionary):
        customer_id = 1
        before_predict = datetime.now()
        final_predictions_lst = []
        tickets_to_be_approved1 = []
        pred_assignment_grp_lst = []
        garbage_tickets = []
        field_mapping = MappingPersistence.get_mapping_details(customer_id)
        group_field_name = field_mapping['Group_Field_Name']
        ticket_id_field_name = field_mapping['Ticket_ID_Field_Name']
        status_field_name = field_mapping['Status_Field_Name']
        description_field_name = field_mapping['Description_Field_Name']
        assignment_logic_dependancy_field = group_field_name
        config = configparser.ConfigParser()
        try:
            logging.info("%s Going for Entity trainig " % RestService.timestamp())
            nerModelURL = config["NERModel"]["url"]
            print("url ", nerModelURL)
            api = nerModelURL + "ner/api/training_entity_ticket"
            proxies = {"http": None, "https": None}
            data = {}
            data['ticket_data'] = rt_tickets
            post_data = json.dumps(data)
            req_head = {"Content-Type": "application/json"}
            req_response = requests.post(api, proxies=proxies, data=post_data, headers=req_head)
            tickets_to_be_approved = "True"

        except  Exception as e:
            print(e, "EXCEPTION IN NER")
            logging.error("Error Handled !!! %s" % str(e))
            tickets_to_be_approved = "False"

        dataset_id = ticket['DatasetID']
        # Predict dependent on earlier predicted value
        dep_pre = MongoDBPersistence.datasets_tbl.find_one({'CustomerID': customer_id, 'DatasetID': dataset_id},
                                                            {'_id': 0, 'DependedPredict': 1})['DependedPredict'][
            0]
        
        white_lst_collection = list(
                    MongoDBPersistence.whitelisted_word_tbl.find({'CustomerID': customer_id, 'DatasetID': dataset_id}))
                
        t_value_doc = MongoDBPersistence.assign_enable_tbl.find_one({})
        t_value_keys = list(t_value_doc.keys())
        t_value = 0
        t_value_enabled = False
        if (t_value_doc and "t_value_enabled" in t_value_keys):
            if (t_value_doc['t_value_enabled'] == 'true' and 'threshold_value' in t_value_keys):
                logging.info('assigning value for "t_value" and for "t_value_enabled" from database!')
                predfld_tvalue_doclst = t_value_doc["threshold_value"]
                
                t_value_enabled = True
            else:
                logging.info(
                    '%s: Either "t_value_enabled" is false or no "threshold_value" field in database' % RestService.timestamp())
        else:
            logging.info(
                '%s: Either "t_value_doc" not exist or no field "t_value_enabled" in database' % RestService.timestamp())

        
        if (t_value_doc and 'assignment_enabled' in list(t_value_doc.keys())):
            assignment_enabled = True if t_value_doc['assignment_enabled'] == 'true' else False
        else:
            logging.info(
                '%s: Either "t_value_doc" not exist or no field "assignment_enabled" in database' % RestService.timestamp())
            logging.info('assigning default value "True" for "assignment_enabled"')
            assignment_enabled = True
        
        # List of predict items depends on predicted values (Y values list)
        dep_prelist_y = []
       
        dep_prelist_x = []
        if dep_pre['flag'] == 'true':
            for item in dep_pre['values']:
                dep_prelist_y.append(item['PredictValue'])
                dep_prelist_x.extend(item['DepPredictValue'])

            print(dep_prelist_y)
            print(dep_prelist_x)
        
        
        description_for_ner = ticket[description_field_name]
       
        all_ok_flag = 0
        try:
            dataset_id = ticket['DatasetID']
            
        except Exception as e:
            logging.error('%s: Error: %s' % (RestService.timestamp(), str(e)))
            garbage_tickets.append(ticket[ticket_id_field_name])
            logging.info('%s: Dataset id not found for the ticket Number: %s' % (
            RestService.timestamp(), ticket[ticket_id_field_name]))
        
        final_predictions = {}
        final_predictions[ticket_id_field_name] = ticket[ticket_id_field_name]
        
        # Fetch Customer choices
        cust_name = MongoDBPersistence.customer_tbl.find_one({'CustomerID': customer_id},
                                                            {'CustomerName': 1, '_id': 0})['CustomerName']
        dataset_info_dict = MongoDBPersistence.datasets_tbl.find_one(
            {'CustomerID': customer_id, "DatasetID": dataset_id},
            {'DatasetName': 1, 'FieldSelections': 1, 'DependedPredict': 1, '_id': 0})
        if (dataset_info_dict):
            dataset_name = dataset_info_dict['DatasetName']
        else:
            logging.info('%s: Customer name not found in the record.' % RestService.timestamp())
            return "failure"
        
        fieldselection_list = dataset_info_dict['FieldSelections']
        
        pred_fields_choices_list = []
        # Pick up Approved customer choices
        for pred_fields in fieldselection_list:
            if (pred_fields['FieldsStatus'] == 'Approved'):
                pred_fields_choices_list = pred_fields['PredictedFields']
                # -- Sorting --
                if dep_pre['flag'] == 'true':
                    pred_fields_choices_list.sort(key=lambda x: x['usePredFieldFlag'] == 'true')
                    depended_predict_lst = dataset_info_dict['DependedPredict'][0]['values']

                    index = [pred_fields_choices_list.index(item) for item in pred_fields_choices_list if
                            item['usePredFieldFlag'] == 'true'][0]
                    pred_fields_choices_sub_list = pred_fields_choices_list[index:]
                    pred_fields_choices_list = pred_fields_choices_list[:index]

                    field_lst = [item['PredictedFieldName'] for item in pred_fields_choices_sub_list]

                    sort_lst = field_lst[:]
                    order_flag = True
                    while (order_flag):
                        order_flag = False
                        for field in field_lst:
                            for depended_doc in depended_predict_lst:
                                if (field == depended_doc['PredictValue']):
                                    for dep_field in depended_doc['DepPredictValue']:
                                        if (dep_field in sort_lst and sort_lst.index(
                                                dep_field) > sort_lst.index(field)):
                                            index = sort_lst.index(field)
                                            sort_lst.remove(dep_field)
                                            sort_lst.insert(index, dep_field)
                                            order_Flag = True

                    temp_pred_fields_choices_list = pred_fields_choices_sub_list
                    pred_fields_choices_sub_list = []
                    pred_fields_choices_sub_list = [pred_field_doc for field in sort_lst for pred_field_doc
                                                    in temp_pred_fields_choices_list if
                                                    field == pred_field_doc['PredictedFieldName']]

                    pred_fields_choices_list += pred_fields_choices_sub_list
                    
        pred_field_list = []
        for pre_field in pred_fields_choices_list:
            pred_field_list.append(pre_field['PredictedFieldName'])
            
        conf_score = []
        # --Automatic approval of incident tickets based on threshold value--
        t_value_confidence_flag = 0
        total_fields_to_be_perdicted = len(pred_field_list)

        temp_predict_dict = {}
        
        for pred_field in pred_field_list:
            pred_field_confidance = {}
            #                      ----setting threshould value for each field----
            if (t_value_enabled):
                for predfld_tvalue_doc in predfld_tvalue_doclst:
                    if (predfld_tvalue_doc['predictedField'] == pred_field):
                        t_value = predfld_tvalue_doc['tValue']
                #                        ------------------------------------------------
                # Based on each prediction field, get all corelated fields appended in a single field(Say in_field)
                # Use feature selection algorithms to select best fields from training dataset
            input_field_list = []
            for input_field in pred_fields_choices_list:
                if (input_field['PredictedFieldName'] == pred_field):
                    input_field_list = input_field['InputFields']
                    additional_field_list = input_field['Additionalfields']
                    
                    algoName = input_field['AlgorithmName']
            if (len(input_field_list) == 0):
                logging.info('%s: No input fields choosen for %s.' % (RestService.timestamp(), pred_field))
                continue
            
            input_df = pd.DataFrame()
            if dep_pre['flag'] == 'true' and pred_field in dep_prelist_y:
                list_of_dependencies = next((ser['DepPredictValue'] for ser in dep_pre['values'] if
                                            ser["PredictValue"] == pred_field), [])
                
                if input_field_list[0] in list_of_dependencies:
                    
                    print("Used dependencies predicted field: ",
                        temp_predict_dict[ticket[ticket_id_field_name] + input_field_list[0]])
                    input_df = pd.DataFrame([{input_field_list[0]: temp_predict_dict[
                        ticket[ticket_id_field_name] + input_field_list[0]]}])
                else:
                    
                    print("Used RT ticket: ", input_field_list[0], ticket[input_field_list[0]])
                    input_df = pd.DataFrame([{input_field_list[0]: ticket[input_field_list[0]]}])
                    
                final_predictions[input_field_list[0]] = ticket[input_field_list[0]]
                for input_field_ in input_field_list[1:]:
                    final_predictions[input_field_] = ticket[input_field_]
                    if input_field_ in list_of_dependencies:
                        
                        print("Used dependencies predict filed: ",
                            temp_predict_dict[ticket[ticket_id_field_name] + input_field_])
                        input_df[input_field_] = pd.DataFrame([{input_field_: temp_predict_dict[
                            ticket[ticket_id_field_name] + input_field_]}])
                    else:
                        print("Used RT ticket: ", input_field_, ticket[input_field_list[0]])
                       
                        input_df[input_field_] = pd.DataFrame([{input_field_: ticket[input_field_]}])
            else:
                print("Normal Predict flow, Not using any dependency predict field...")
                for field in additional_field_list:
                    input_df[field] = ticket[field]
                input_df = pd.DataFrame([{input_field_list[0]: ticket[input_field_list[0]]}])
                final_predictions[input_field_list[0]] = ticket[input_field_list[0]]
                for input_field_ in input_field_list[1:]:
                    final_predictions[input_field_] = ticket[input_field_]
                    input_df[input_field_] = pd.DataFrame([{input_field_: ticket[input_field_]}])

            
            input_df['in_field'] = ''
            for field in input_field_list:
                if (input_df[field] is None):
                    input_df[field] = ""
                input_df['in_field'] += input_df[field] + ' --~||~-- '
            input_df1 = pd.DataFrame()
            input_df1['in_field'] = input_df['in_field']

            
            in_field = 'in_field'
            
            input_df1 = input_df1[pd.notnull(input_df1[in_field])]

            ## No custom preprocessing file present , so going for some basic cleaning
            training_tkt_df = IncidentTraining.cleaningInputFields(input_df1, in_field)
            for field in additional_field_list:
                training_tkt_df[field] = ticket[field]

            input_df_list = input_df1['in_field'].tolist()
            descr_df = [str(x) for x in input_df_list]
            columns_path = 'data/' + cust_name + "__" + dataset_name + '__' + in_field + "__" + pred_field + "__" + "additionalcolumns.pkl"
            columns_file = Path(columns_path)
            if (columns_file.is_file()):
                column_list = joblib.load(columns_path)
            else:
                logging.info(
                    '%s: column file not found for %s field.. please train algo, save the choices & try again.' % (
                    RestService.timestamp(), pred_field))
                continue

            df_encoded = pd.get_dummies(training_tkt_df, columns=additional_field_list)
            for i in column_list:
                if i not in df_encoded.columns:
                    df_encoded[i] = 0

            #   ----White Listed Word Logic---
            found_white_lst_wrd = False
            input_descr = descr_df[0]

            # Whitelisting by giving word weighatge for prediction - START
            try:
                weightage_summation = {}

                for white_lst_doc in white_lst_collection:
                    if (white_lst_doc['PredictedField'] == pred_field and white_lst_doc[
                        'WhiteListed_Words'] != []):
                        
                        for item in white_lst_doc['WhiteListed_Words']:
                            for i in range(len(item['Value'])):
                                if (item['Value'][i]['word']).lower() in input_descr:
                                    
                                    if not item['Field_Name'] in weightage_summation:
                                        weightage_summation[item['Field_Name']] = float(
                                            item['Value'][i]['weightage'])
                                    else:
                                        weightage_value = float(weightage_summation[item['Field_Name']])
                                        weightage_summation[item['Field_Name']] = float(
                                            item['Value'][i]['weightage']) + weightage_value

                logging.info(f"len(weightage_summation): {len(weightage_summation)}")

                if (len(weightage_summation) > 0):
                    logging.info(
                        '%s: found a match from white listed words collection' % RestService.timestamp())
                    predicted_label = max(weightage_summation.items(), key=operator.itemgetter(1))[0]
                    logging.info(f"predicted_label: {predicted_label}")
                    pred_field_confidance[pred_field] = predicted_label
                    pred_field_confidance['ConfidenceScore'] = 1
                    pred_field_confidance['prediction_by'] = 'white list word'
                    conf_score.append(pred_field_confidance)
                    found_white_lst_wrd = True

                    if (pred_field == assignment_logic_dependancy_field):  # --condition 3--
                        pred_assignment_grp_lst.append({ticket[ticket_id_field_name]: predicted_label})
                        obj = Assignment(possible_assignee=predicted_label)
                        final_predictions['possible_assignees'] = obj.assignmentRouting()


                # --loop 1--
            except Exception as e:
                logging.error(e, exc_info=True)
            if (found_white_lst_wrd):
                all_ok_flag = 1
                logging.info(f'match found!, continueing the loop with next predicted field')
                continue
            #   ------------------------------
            # Whitelisting by giving word weighatge for prediction - END

            pred_output_result = []

            vocab_path = 'data/' + cust_name + "__" + dataset_name + '__' + "in_field" + "__" + pred_field + "__" + "Approved" + "__" + "transformer.pkl"
            model_path = 'models/' + cust_name + "__" + dataset_name + '__' + algoName + "__" + pred_field + "__" + "Approved" + "__" + "Model.pkl"
            vocab_file = Path(vocab_path)
            model_file = Path(model_path)
            if (vocab_file.is_file()):
                transformer = joblib.load(vocab_path)
            else:
                logging.info(
                    f'Vocabulary file not found for %s field.. please train algo, save the choices & try again. pred_field: {pred_field}')
                continue

            if (model_file.is_file()):
                fittedModel = joblib.load(model_file)
            else:
                logging.info(
                    '%s: ML Model file not found for %s field.. please train algo, save the choices & try again.' % (
                    RestService.timestamp(), pred_field))
                continue

            pred_output_result = fittedModel.predict(transformer.transform(df_encoded))
            id_to_labels = MongoDBPersistence.datasets_tbl.find_one(
                {'CustomerID': customer_id, "DatasetID": dataset_id}, {"_id": 0, "IdToLabels": 1})
            if (id_to_labels):
                id_to_labels_dict = id_to_labels["IdToLabels"]
                inside_id_to_label = id_to_labels_dict[str(pred_field)]
            else:
                logging.info(
                    '%s: De-map data not found for %s field.' % (RestService.timestamp(), pred_field))

            predicted_label = inside_id_to_label[str(pred_output_result[0])]
            print("predicted_label:", predicted_label)
            print("pred_field:::", pred_field)

            # Predict dependent on earlier predicted value
            if pred_field in dep_prelist_x:
                temp_predict_dict[ticket[ticket_id_field_name] + pred_field] = predicted_label

            pred_field_confidance[pred_field] = predicted_label

            confidence_score = float(
                "{0:.2f}".format(max(fittedModel.predict_proba(transformer.transform(df_encoded))[0])))
            pred_field_confidance['ConfidenceScore'] = confidence_score
            pred_field_confidance['prediction_by'] = 'algorithm'
            conf_score.append(pred_field_confidance)
            # --Automatic approval of incident tickets based on threshold value--
            logging.info(f"t_value_enabled: {t_value_enabled}")
            logging.info(f"t_value: {t_value}")
            logging.info(f"confidence_score: {confidence_score}")
            if (t_value_enabled and float(t_value) <= confidence_score):
                t_value_confidence_flag = t_value_confidence_flag + 1

            if pred_field == assignment_logic_dependancy_field and assignment_enabled:
                pred_assignment_grp_lst.append({ticket[ticket_id_field_name]: predicted_label})
                obj = Assignment(possible_assignee=predicted_label)
                final_predictions['possible_assignees'] = obj.assignmentRouting()



            all_ok_flag = 1
        
        if (all_ok_flag):
            entity_dct = {}
            try:
                doc_flag = MongoDBPersistence.assign_enable_tbl.find_one({})
            except Exception as e:
                logging.error('assign_enable_tbl : %s' % str(e))
            regex_flag = True if doc_flag['regex_enabled'] == 'true' else False
            db_regex_flag = True if doc_flag['db_enabled'] == 'true' else False
            spacy_regex_flag = True if doc_flag['spacy_enabled'] == 'true' else False

            if regex_flag:
                for entity_name, regex_list in regex_dictionary.items():

                    for regex in regex_list:
                        match_list = re.findall(regex, description_for_ner, re.I)
                        if (match_list):
                            if (entity_name in entity_dct.keys()):
                                entity_dct[entity_name].append(match_list)
                            else:
                                entity_dct[entity_name] = match_list
            logging.info(f"entity_dct : {entity_dct}")
            if db_regex_flag:
                nmd_entity_lst = list(MongoDBPersistence.annotation_mapping_tbl.find({},
                                                                                    {'_id': 0, 'entity': 1,
                                                                                    'description': 1}))
                
                description_lower = description_for_ner.lower()
                for nmd_entity_item in nmd_entity_lst:
                    
                    for item in nmd_entity_item['description']:
                        
                        if item.lower() in description_lower:
                           
                            if (nmd_entity_item['entity'] in entity_dct.keys()):
                                entity_dct[nmd_entity_item['entity']].append(item)
                            else:
                                entity_dct[nmd_entity_item['entity']] = [item]

            if spacy_regex_flag:
                spacy_corpus_dir = 'models/spacy_corpus'
                spacy_corpus_path = Path(spacy_corpus_dir)
                if (spacy_corpus_path.is_dir()):
                    
                    doc = nlp(description_for_ner)
                    for ent in doc.ents:
                        if (ent.label_ in entity_dct.keys()):
                            entity_dct[ent.label_].append(ent.text)
                        else:
                            entity_dct[ent.label_] = [ent.text]
                
                else:
                    logging.info(
                        '%s: spacy_corpus_path not found for %s field.. please train algo, save the choices & try again.' % (
                        RestService.timestamp(), pred_field))

            # related to Knowledge Information code

            mapping = MongoDBPersistence.knowledge_entity_tbl.find_one({"Mapping": True},
                                                                    {"AccountToIiaColumnMapping": 1,
                                                                        '_id': 0})

            if mapping:
                if bool(entity_dct):
                    acct2iia = mapping['AccountToIiaColumnMapping']
                    kg_list = list(acct2iia.keys())
                    final_kg_list = {}
                    for entity, value in entity_dct.items():
                        
                        if entity in kg_list:
                            for item in value:
                               
                                info_name = entity
                                info_details = list(MongoDBPersistence.knowledge_entity_tbl.find(
                                    {info_name: {"$regex": item, "$options": "i"}}, {'_id': 0}))
                                if bool(info_details):
                                    final_kg_list[item] = info_details
                                print(item, ":::::::", info_details)
                    if bool(final_kg_list):
                        final_predictions['KgInfo'] = [final_kg_list]
                    else:
                        final_predictions['KgInfo'] = []


            final_predictions["user_status"] = "Not Approved"
            final_predictions["state"] = ticket["state"]
            final_predictions['predicted_fields'] = conf_score
            final_predictions['CustomerID'] = customer_id
            final_predictions['DatasetID'] = dataset_id
            final_predictions['timestamp'] = datetime.fromtimestamp(time.time()).strftime(
                "%Y-%m-%d %H:%M:%S")
            if (entity_dct):
                print("Entities Captured", entity_dct)
                final_entities = []

                for entity, value in entity_dct.items():
                    entities = {}
                    entities["Entity"] = entity
                    entities["Value"] = value
                    final_entities.append(entities)
                final_predictions['NamedEntities'] = final_entities
            final_predictions_lst.append(final_predictions)
        
        # --Automatic approval of incident tickets based on threshold value--
        if (t_value_enabled and total_fields_to_be_perdicted == t_value_confidence_flag):
            temp_doc = {}
            temp_doc[ticket_id_field_name] = ticket[ticket_id_field_name]
            temp_doc['DatasetID'] = ticket['DatasetID']
            for doc in conf_score:
                key = list(doc.keys())[0]
                predicted_value = doc[key]
                temp_doc[key] = predicted_value

            tickets_to_be_approved1.append(temp_doc)

        after_predict = datetime.now()
        logging.debug(f"after_predict: {after_predict}")
        logging.debug(f"time_taken: {after_predict-before_predict}")
        seconds_elapsed = after_predict-before_predict
        print(f"time_taken: %s " % (seconds_elapsed))

        return pred_assignment_grp_lst, final_predictions_lst, garbage_tickets, tickets_to_be_approved1

    @staticmethod
    def predict(customer_id):

        before_predict = datetime.now()
        logging.debug(f"before_predict: {before_predict}")

        print("INSIDE PREDICT", "*****************************************888888")
        field_mapping = MappingPersistence.get_mapping_details(customer_id)
       
        description_field_name = field_mapping['Description_Field_Name']
        custom_predict_flag, custom_url = CustomerMasterData.check_custom("customPrediction")
        if (custom_predict_flag == 'failure'):
            logging.info("%s: Not able to read values from Configure File" % RestService.timestamp())
            return "failure"

        elif (custom_predict_flag == "True"):
            logging.info("%s Custom predict is present invoking Custom Predict" % RestService.timestamp())
            api = custom_url + "api/custom_predict/" + str(customer_id)
            proxies = {"http": None, "https": None}
           
            payload = {}
            if (session.get('user')):
                logging.info("%s Catching User Session" % RestService.timestamp())
                payload['user'] = session['user']
                logging.info("%s Session catched user as  %s" % (RestService.timestamp(), payload['user']))
            else:
                logging.info("%s You are not logged in please login" % RestService.timestamp())
                return "No Login Found"
           
            req_response = requests.get(api, proxies=proxies, params=payload)
            
            return json_util.dumps(req_response.json())
        else:
            field_mapping = MappingPersistence.get_mapping_details(customer_id)
            group_field_name = field_mapping['Group_Field_Name']
            ticket_id_field_name = field_mapping['Ticket_ID_Field_Name']
            status_field_name = field_mapping['Status_Field_Name']
            
            print("assignment_logic_dependancy_field is empty")
            assignment_logic_dependancy_field = group_field_name

            result = {}
            if (session.get('user')):
                logging.info("%s Catching User Session" % RestService.timestamp())
                user = session['user']
                logging.info("%s Session catched user as  %s" % (RestService.timestamp(), user))
            else:
                logging.info("%s You are not logged in please login" % RestService.timestamp())
                return "No Login Found"

            login_user = MongoDBPersistence.users_tbl.find_one({"UserID": user}, {"_id": 0})
            if (login_user):
                regex_dictionary = {}
                try:
                    config = configparser.ConfigParser()
                    config["DEFAULT"]['path'] = "config/"
                    config.read(config["DEFAULT"]["path"] + "iia.ini")
                    entities_list = config["NamedEntitiesRegex"]["Entities"]
                    entities_list = entities_list.split(',')
                    for entity_type in entities_list:
                        entity_regex = config["NamedEntitiesRegex"][entity_type]
                        entity_regex = entity_regex.split(',')
                        regex_dictionary[entity_type] = entity_regex
                    print("Final Regex", regex_dictionary)
                except Exception as e:
                    logging.error("Error occured: Hint: 'Entities' is not defined in 'config/iia.ini' file.")
                    entities_list = ["EMAIL,", "SERVER", "ISSUE", "NUMBER", "APPLICATION", "PLATFORM",
                                     "TRANSACTION_CODE", "TABLE"]
                    regex_dictionary = {"EMAIL": ["[\w\.-]+@[\w\.-]+"],
                                        "SERVER": ["CMT\w+", "CTM\w+", "SIT:?", "CD1\-?"], "ISSUE": ["run[a-z\s]+ce"],
                                        "NUMBER": [
                                            "(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})"],
                                        "APPLICATION": ["Shar\w+nt"], "PLATFORM": ["Az\w+e"],
                                        "TRANSACTION_CODE": ["T[0-9]{3}"], "TABLE": ["CISF"]}
                    logging.info(
                        "%s Taking default as 'entitites_list as [EMAIL, SERVER, ISSUE, NUMBER, APPLICATION, PLATFORM, TRANSACTION_CODE, TABLE]'.." % RestService.timestamp())

                # loading Default spacy model for PERSON and GPE recognition
                try:
                    flag = MongoDBPersistence.assign_enable_tbl.find_one({}, {'_id': 0, "spacy_enabled": 1})
                    spacy_flag = True if flag['spacy_enabled'] == 'true' else False
                    
                except Exception as e:
                    
                    logging.error('assign_enable_tbl : %s' % str(e))

                if spacy_flag:
                    spacy_corpus_dir = 'models/spacy_corpus'
                    spacy_corpus_path = Path(spacy_corpus_dir)
                    if (spacy_corpus_path.is_dir()):
                        nlp = spacy.load(spacy_corpus_dir)
                    else:
                        logging.info(
                            '%s: spacy corpus path not found.. please train Spacy, save the choices & try again.' % RestService.timestamp())
                else:
                    nlp = core_web_model
                
                accessible_datasets = DatasetMasterData.guess_dataset_access(user)

                logging.info(f"##################accessible_datasets######################,{accessible_datasets} ")

                garbage_tickets = []
                rt_tickets = list(MongoDBPersistence.rt_tickets_tbl.find(
                    {'CustomerID': customer_id, "DatasetID": {"$in": accessible_datasets}, status_field_name: 'New',
                     'user_status': 'Not Approved'}, {'_id': 0}))
                already_predicted_tickets = list(
                    MongoDBPersistence.predicted_tickets_tbl.find({}, {"_id": 1, ticket_id_field_name: 1}))
                before_removal = rt_tickets.copy()
                #### Removing Same Tickets from Prediction####
                dataset_id = -1
                if len(rt_tickets) > 0:
                    dataset_id = rt_tickets[0]['DatasetID']
                    for predicted_tickets in already_predicted_tickets:
                        logging.info(f"Removing {predicted_tickets[ticket_id_field_name]} from RT")
                        rt_tickets = [i for i in rt_tickets if
                                      not (i[ticket_id_field_name] == predicted_tickets[ticket_id_field_name])]

                if (not rt_tickets):
                    if dataset_id > 0:
                        result = {}
                        result['DatasetID'] = dataset_id
                        return result
                    logging.info(
                        '%s: There is nothing uploaded for prediction. Upload tickets data first & then try again.' % RestService.timestamp())
                    return "failure"
                
                pred_assignment_grp_lst = []
                final_predictions_lst = []
                predfld_tvalue_doclst = []
                dataset_id = rt_tickets[0]['DatasetID']

                FieldSelections = list(MongoDBPersistence.datasets_tbl.find({'CustomerID':customer_id,'DatasetID':dataset_id},{'_id':0, 'FieldSelections' :1 }))
                input_field_name = FieldSelections[0]['FieldSelections'][0]['PredictedFields'][0]['InputFields'][0]
                
                if input_field_name=='description':
                    description_field_name = field_mapping['Description_Field_Name']
                elif input_field_name=='short_description':
                    description_field_name = field_mapping['Short_Description_Field_Name']

                white_lst_collection = list(
                    MongoDBPersistence.whitelisted_word_tbl.find({'CustomerID': customer_id, 'DatasetID': dataset_id}))
                # --Automatic approval of incident tickets based on threshold value--
                tickets_to_be_approved = []
                logging.info('%s: fetching details from "assign_enable_tbl"' % RestService.timestamp())
                t_value_doc = MongoDBPersistence.assign_enable_tbl.find_one({})
                t_value_keys = list(t_value_doc.keys())
                logging.info(
                    '%s: assigning default value 0 for "t_value" and "False" for "t_value_enabled"' % RestService.timestamp())
                t_value = 0
                t_value_enabled = False
                if (t_value_doc and "t_value_enabled" in t_value_keys):
                    if (t_value_doc['t_value_enabled'] == 'true' and 'threshold_value' in t_value_keys):
                        logging.info('assigning value for "t_value" and for "t_value_enabled" from database!')
                        predfld_tvalue_doclst = t_value_doc["threshold_value"]
                        #                        t_value=t_value_doc["threshold_value"]
                        t_value_enabled = True
                    else:
                        logging.info(
                            '%s: Either "t_value_enabled" is false or no "threshold_value" field in database' % RestService.timestamp())
                else:
                    logging.info(
                        '%s: Either "t_value_doc" not exist or no field "t_value_enabled" in database' % RestService.timestamp())

                if (t_value_doc and 'assignment_enabled' in list(t_value_doc.keys())):
                    assignment_enabled = True if t_value_doc['assignment_enabled'] == 'true' else False
                else:
                    logging.info(
                        '%s: Either "t_value_doc" not exist or no field "assignment_enabled" in database' % RestService.timestamp())
                    logging.info('assigning default value "True" for "assignment_enabled"')
                    assignment_enabled = True

                # Predict dependent on earlier predicted value
                dep_pre = MongoDBPersistence.datasets_tbl.find_one({'CustomerID': customer_id, 'DatasetID': dataset_id},
                                                                   {'_id': 0, 'DependedPredict': 1})['DependedPredict'][
                    0]
                # List of predict items depends on predicted values (Y values list)
                dep_prelist_y = []
                # X value list 
                dep_prelist_x = []
                if dep_pre['flag'] == 'true':
                    for item in dep_pre['values']:
                        dep_prelist_y.append(item['PredictValue'])
                        dep_prelist_x.extend(item['DepPredictValue'])

                    print(dep_prelist_y)
                    print(dep_prelist_x)                
                
                try:
                    config = configparser.ConfigParser()
                    config["DEFAULT"]['path'] = "config/"
                    config.read(config["DEFAULT"]["path"] + "iia.ini")
                    Multithreading = config["ModuleConfig"]["Multithreading"]
                    print("Multithreading -------------", Multithreading)
                except Exception as e:
                    logging.error("Error occured: Hint: 'Multithreading' is not defined in 'config/iia.ini' file.")
                    Multithreading = False
                    logging.info("%s Taking default as 'Multithreading as False'..")

                if Multithreading == "True":
                    logging.info("%s Multithreading Status: True..")
                    start = time.time()

                    with ThreadPoolExecutor() as executor:
                        result_list = list(executor.map(
                            partial(
                                Predict.tick_to_approved,
                            ),
                            rt_tickets, repeat(regex_dictionary)
                        ))
                    
                    pred_assignment_grp_lst = [i[0] for i in result_list]
                    final_predictions_lst = [i[1] for i in result_list]
                    garbage_tickets= [i[2] for i in result_list]
                    tickets_to_be_approved = [i[3] for i in result_list]

                    final_predictions_lst = list(Predict.listflatten(final_predictions_lst))
                    garbage_tickets = list(Predict.listflatten(garbage_tickets))
                    tickets_to_be_approved = list(Predict.listflatten(tickets_to_be_approved))
                    pred_assignment_grp_lst = list(Predict.listflatten(pred_assignment_grp_lst))
                else:
                    logging.info("%s Multithreading Status: False..")
                    ################### NER integration ##################
                    for ticket in rt_tickets:

                        try:
                            logging.info("%s Going for Entity trainig " % RestService.timestamp())
                            nerModelURL = config["NERModel"]["url"]
                            print("url ", nerModelURL)
                            api = nerModelURL + "ner/api/training_entity_ticket"
                            proxies = {"http": None, "https": None}
                            data = {}
                            data['ticket_data'] = ticket
                            post_data = json.dumps(data)
                            req_head = {"Content-Type": "application/json"}
                            req_response = requests.post(api, proxies=proxies, data=post_data, headers=req_head)

                        except  Exception as e:
                            print(e, "EXCEPTION IN NER")
                            logging.error("Error Handled !!! %s" % str(e))

                        description_for_ner = ticket[description_field_name]

                        all_ok_flag = 0
                        try:
                            dataset_id = ticket['DatasetID']
                            
                        except Exception as e:
                            logging.error('%s: Error: %s' % (RestService.timestamp(), str(e)))
                            garbage_tickets.append(ticket[ticket_id_field_name])
                            logging.info('%s: Dataset id not found for the ticket Number: %s' % (
                            RestService.timestamp(), ticket[ticket_id_field_name]))
                            continue
                        final_predictions = {}
                        final_predictions[ticket_id_field_name] = ticket[ticket_id_field_name]

                        # Fetch Customer choices
                        cust_name = MongoDBPersistence.customer_tbl.find_one({'CustomerID': customer_id},
                                                                            {'CustomerName': 1, '_id': 0})['CustomerName']
                        dataset_info_dict = MongoDBPersistence.datasets_tbl.find_one(
                            {'CustomerID': customer_id, "DatasetID": dataset_id},
                            {'DatasetName': 1, 'FieldSelections': 1, 'DependedPredict': 1, '_id': 0})
                        if (dataset_info_dict):
                            dataset_name = dataset_info_dict['DatasetName']
                        else:
                            logging.info('%s: Customer name not found in the record.' % RestService.timestamp())
                            return "failure"
                        fieldselection_list = dataset_info_dict['FieldSelections']
                        
                        pred_fields_choices_list = []
                        # Pick up Approved customer choices
                        for pred_fields in fieldselection_list:
                            if (pred_fields['FieldsStatus'] == 'Approved'):
                                pred_fields_choices_list = pred_fields['PredictedFields']
                                # -- Sorting --
                                if dep_pre['flag'] == 'true':
                                    pred_fields_choices_list.sort(key=lambda x: x['usePredFieldFlag'] == 'true')
                                    depended_predict_lst = dataset_info_dict['DependedPredict'][0]['values']

                                    index = [pred_fields_choices_list.index(item) for item in pred_fields_choices_list if
                                            item['usePredFieldFlag'] == 'true'][0]
                                    pred_fields_choices_sub_list = pred_fields_choices_list[index:]
                                    pred_fields_choices_list = pred_fields_choices_list[:index]

                                    field_lst = [item['PredictedFieldName'] for item in pred_fields_choices_sub_list]

                                    sort_lst = field_lst[:]
                                    order_flag = True
                                    while (order_flag):
                                        order_flag = False
                                        for field in field_lst:
                                            for depended_doc in depended_predict_lst:
                                                if (field == depended_doc['PredictValue']):
                                                    for dep_field in depended_doc['DepPredictValue']:
                                                        if (dep_field in sort_lst and sort_lst.index(
                                                                dep_field) > sort_lst.index(field)):
                                                            index = sort_lst.index(field)
                                                            sort_lst.remove(dep_field)
                                                            sort_lst.insert(index, dep_field)
                                                            order_Flag = True

                                    temp_pred_fields_choices_list = pred_fields_choices_sub_list
                                    pred_fields_choices_sub_list = []
                                    pred_fields_choices_sub_list = [pred_field_doc for field in sort_lst for pred_field_doc
                                                                    in temp_pred_fields_choices_list if
                                                                    field == pred_field_doc['PredictedFieldName']]

                                    pred_fields_choices_list += pred_fields_choices_sub_list

                        pred_field_list = []
                        for pre_field in pred_fields_choices_list:
                            pred_field_list.append(pre_field['PredictedFieldName'])

                        conf_score = []
                        # --Automatic approval of incident tickets based on threshold value--
                        t_value_confidence_flag = 0
                        total_fields_to_be_perdicted = len(pred_field_list)

                        temp_predict_dict = {}

                        for pred_field in pred_field_list:
                            pred_field_confidance = {}
                            #                      ----setting threshould value for each field----
                            if (t_value_enabled):
                                for predfld_tvalue_doc in predfld_tvalue_doclst:
                                    if (predfld_tvalue_doc['predictedField'] == pred_field):
                                        t_value = predfld_tvalue_doc['tValue']
                                #                        ------------------------------------------------
                                # Based on each prediction field, get all corelated fields appended in a single field(Say in_field)
                                # Use feature selection algorithms to select best fields from training dataset
                            input_field_list = []
                            for input_field in pred_fields_choices_list:
                                if (input_field['PredictedFieldName'] == pred_field):
                                    input_field_list = input_field['InputFields']
                                    additional_field_list = input_field['Additionalfields']
                                    # print('input field list is ' + str(input_field_list))
                                    algoName = input_field['AlgorithmName']
                            if (len(input_field_list) == 0):
                                logging.info('%s: No input fields choosen for %s.' % (RestService.timestamp(), pred_field))
                                continue
                           
                            input_df = pd.DataFrame()
                            if dep_pre['flag'] == 'true' and pred_field in dep_prelist_y:
                                list_of_dependencies = next((ser['DepPredictValue'] for ser in dep_pre['values'] if
                                                            ser["PredictValue"] == pred_field), [])
                                
                                if input_field_list[0] in list_of_dependencies:
                                    
                                    print("Used dependencies predicted field: ",
                                        temp_predict_dict[ticket[ticket_id_field_name] + input_field_list[0]])
                                    input_df = pd.DataFrame([{input_field_list[0]: temp_predict_dict[
                                        ticket[ticket_id_field_name] + input_field_list[0]]}])
                                else:
                                    
                                    print("Used RT ticket: ", input_field_list[0], ticket[input_field_list[0]])
                                    input_df = pd.DataFrame([{input_field_list[0]: ticket[input_field_list[0]]}])
                                    
                                final_predictions[input_field_list[0]] = ticket[input_field_list[0]]
                                for input_field_ in input_field_list[1:]:
                                    final_predictions[input_field_] = ticket[input_field_]
                                    if input_field_ in list_of_dependencies:
                                        
                                        print("Used dependencies predict filed: ",
                                            temp_predict_dict[ticket[ticket_id_field_name] + input_field_])
                                        input_df[input_field_] = pd.DataFrame([{input_field_: temp_predict_dict[
                                            ticket[ticket_id_field_name] + input_field_]}])
                                    else:
                                        print("Used RT ticket: ", input_field_, ticket[input_field_list[0]])
                                        
                                        input_df[input_field_] = pd.DataFrame([{input_field_: ticket[input_field_]}])
                            else:
                                print("Normal Predict flow, Not using any dependency predict field...")
                                for field in additional_field_list:
                                    input_df[field] = ticket[field]
                                input_df = pd.DataFrame([{input_field_list[0]: ticket[input_field_list[0]]}])
                                final_predictions[input_field_list[0]] = ticket[input_field_list[0]]
                                for input_field_ in input_field_list[1:]:
                                    final_predictions[input_field_] = ticket[input_field_]
                                    input_df[input_field_] = pd.DataFrame([{input_field_: ticket[input_field_]}])

                            input_df['in_field'] = ''
                            for field in input_field_list:
                                if (input_df[field] is None):
                                    input_df[field] = ""
                                input_df['in_field'] += input_df[field] + ' --~||~-- '
                            input_df1 = pd.DataFrame()
                            input_df1['in_field'] = input_df['in_field']

                            
                            in_field = 'in_field'
                            # Skips those tickets where there is no description field
                            input_df1 = input_df1[pd.notnull(input_df1[in_field])]

                        
                            ## No custom preprocessing file present , so going for some basic cleaning
                            training_tkt_df = IncidentTraining.cleaningInputFields(input_df1, in_field)
                            for field in additional_field_list:
                                training_tkt_df[field] = ticket[field]

                            input_df_list = input_df1['in_field'].tolist()
                            descr_df = [str(x) for x in input_df_list]
                            columns_path = 'data/' + cust_name + "__" + dataset_name + '__' + in_field + "__" + pred_field + "__" + "additionalcolumns.pkl"
                            columns_file = Path(columns_path)
                            if (columns_file.is_file()):
                                column_list = joblib.load(columns_path)
                            else:
                                logging.info(
                                    '%s: column file not found for %s field.. please train algo, save the choices & try again.' % (
                                    RestService.timestamp(), pred_field))
                                continue

                            df_encoded = pd.get_dummies(training_tkt_df, columns=additional_field_list)
                            for i in column_list:
                                if i not in df_encoded.columns:
                                    df_encoded[i] = 0

                            #   ----White Listed Word Logic---
                            found_white_lst_wrd = False
                            input_descr = descr_df[0]

                            # Whitelisting by giving word weighatge for prediction - START
                            try:
                                weightage_summation = {}

                                for white_lst_doc in white_lst_collection:
                                    if (white_lst_doc['PredictedField'] == pred_field and white_lst_doc[
                                        'WhiteListed_Words'] != []):
                                        
                                        for item in white_lst_doc['WhiteListed_Words']:
                                            for i in range(len(item['Value'])):
                                                if (item['Value'][i]['word']).lower() in input_descr:
                                                    
                                                    if not item['Field_Name'] in weightage_summation:
                                                        weightage_summation[item['Field_Name']] = float(
                                                            item['Value'][i]['weightage'])
                                                    else:
                                                        weightage_value = float(weightage_summation[item['Field_Name']])
                                                        weightage_summation[item['Field_Name']] = float(
                                                            item['Value'][i]['weightage']) + weightage_value

                                logging.info(f"len(weightage_summation): {len(weightage_summation)}")

                                if (len(weightage_summation) > 0):
                                    logging.info(
                                        '%s: found a match from white listed words collection' % RestService.timestamp())
                                    predicted_label = max(weightage_summation.items(), key=operator.itemgetter(1))[0]
                                    logging.info(f"predicted_label: {predicted_label}")
                                    pred_field_confidance[pred_field] = predicted_label
                                    pred_field_confidance['ConfidenceScore'] = 1
                                    pred_field_confidance['prediction_by'] = 'white list word'
                                    conf_score.append(pred_field_confidance)
                                    found_white_lst_wrd = True

                                    if (pred_field == assignment_logic_dependancy_field):  # --condition 3--
                                        pred_assignment_grp_lst.append({ticket[ticket_id_field_name]: predicted_label})
                                        obj = Assignment(possible_assignee=predicted_label)
                                        final_predictions['possible_assignees'] = obj.assignmentRouting()


                                # --loop 1--
                            except Exception as e:
                                logging.error(e, exc_info=True)
                            if (found_white_lst_wrd):
                                all_ok_flag = 1
                                logging.info(f'match found!, continueing the loop with next predicted field')
                                continue
                            #   ------------------------------
                            # Whitelisting by giving word weighatge for prediction - END

                            pred_output_result = []

                            vocab_path = 'data/' + cust_name + "__" + dataset_name + '__' + in_field + "__" + pred_field + "__" + "Approved" + "__" + "transformer.pkl"
                            model_path = 'models/' + cust_name + "__" + dataset_name + '__' + algoName + "__" + pred_field + "__" + "Approved" + "__" + "Model.pkl"
                            vocab_file = Path(vocab_path)
                            model_file = Path(model_path)
                            if (vocab_file.is_file()):
                                transformer = joblib.load(vocab_path)
                            else:
                                logging.info(
                                    f'Vocabulary file not found for %s field.. please train algo, save the choices & try again. pred_field: {pred_field}')
                                continue

                            if (model_file.is_file()):
                                fittedModel = joblib.load(model_file)
                            else:
                                logging.info(
                                    '%s: ML Model file not found for %s field.. please train algo, save the choices & try again.' % (
                                    RestService.timestamp(), pred_field))
                                continue

                            pred_output_result = fittedModel.predict(transformer.transform(df_encoded))
                            id_to_labels = MongoDBPersistence.datasets_tbl.find_one(
                                {'CustomerID': customer_id, "DatasetID": dataset_id}, {"_id": 0, "IdToLabels": 1})
                            if (id_to_labels):
                                id_to_labels_dict = id_to_labels["IdToLabels"]
                                inside_id_to_label = id_to_labels_dict[str(pred_field)]
                            else:
                                logging.info(
                                    '%s: De-map data not found for %s field.' % (RestService.timestamp(), pred_field))

                            predicted_label = inside_id_to_label[str(pred_output_result[0])]
                            print("predicted_label:", predicted_label)
                            print("pred_field:::", pred_field)

                            # Predict dependent on earlier predicted value
                            if pred_field in dep_prelist_x:
                                temp_predict_dict[ticket[ticket_id_field_name] + pred_field] = predicted_label
                           
                            pred_field_confidance[pred_field] = predicted_label

                            confidence_score = float(
                                "{0:.2f}".format(max(fittedModel.predict_proba(transformer.transform(df_encoded))[0])))
                            pred_field_confidance['ConfidenceScore'] = confidence_score
                            pred_field_confidance['prediction_by'] = 'algorithm'
                            conf_score.append(pred_field_confidance)
                            # --Automatic approval of incident tickets based on threshold value--
                            logging.info(f"t_value_enabled: {t_value_enabled}")
                            logging.info(f"t_value: {t_value}")
                            logging.info(f"confidence_score: {confidence_score}")
                            if (t_value_enabled and float(t_value) <= confidence_score):
                                t_value_confidence_flag = t_value_confidence_flag + 1

                            if pred_field == assignment_logic_dependancy_field and assignment_enabled:
                                pred_assignment_grp_lst.append({ticket[ticket_id_field_name]: predicted_label})
                                obj = Assignment(possible_assignee=predicted_label)
                                final_predictions['possible_assignees'] = obj.assignmentRouting()

                            all_ok_flag = 1

                        if (all_ok_flag):
                            entity_dct = {}
                            try:
                                doc_flag = MongoDBPersistence.assign_enable_tbl.find_one({})
                            except Exception as e:
                                logging.error('assign_enable_tbl : %s' % str(e))
                            regex_flag = True if doc_flag['regex_enabled'] == 'true' else False
                            db_regex_flag = True if doc_flag['db_enabled'] == 'true' else False
                            spacy_regex_flag = True if doc_flag['spacy_enabled'] == 'true' else False

                            if regex_flag:
                                for entity_name, regex_list in regex_dictionary.items():

                                    for regex in regex_list:
                                        match_list = re.findall(regex, description_for_ner, re.I)
                                        if (match_list):
                                            if (entity_name in entity_dct.keys()):
                                                entity_dct[entity_name].append(match_list)
                                            else:
                                                entity_dct[entity_name] = match_list
                            logging.info(f"entity_dct : {entity_dct}")
                            if db_regex_flag:
                                nmd_entity_lst = list(MongoDBPersistence.annotation_mapping_tbl.find({},
                                                                                                    {'_id': 0, 'entity': 1,
                                                                                                    'description': 1}))
                                description_lower = description_for_ner.lower()
                                for nmd_entity_item in nmd_entity_lst:
                                    
                                    for item in nmd_entity_item['description']:
                                       
                                        if item.lower() in description_lower:
                                            
                                            if (nmd_entity_item['entity'] in entity_dct.keys()):
                                                entity_dct[nmd_entity_item['entity']].append(item)
                                            else:
                                                entity_dct[nmd_entity_item['entity']] = [item]

                            if spacy_regex_flag:
                                spacy_corpus_dir = 'models/spacy_corpus'
                                spacy_corpus_path = Path(spacy_corpus_dir)
                                if (spacy_corpus_path.is_dir()):
                                    
                                    doc = nlp(description_for_ner)
                                    for ent in doc.ents:
                                        if (ent.label_ in entity_dct.keys()):
                                            entity_dct[ent.label_].append(ent.text)
                                        else:
                                            entity_dct[ent.label_] = [ent.text]
                                    
                                else:
                                    logging.info(
                                        '%s: spacy_corpus_path not found for %s field.. please train algo, save the choices & try again.' % (
                                        RestService.timestamp(), pred_field))


                            mapping = MongoDBPersistence.knowledge_entity_tbl.find_one({"Mapping": True},
                                                                                    {"AccountToIiaColumnMapping": 1,
                                                                                        '_id': 0})

                            if mapping:
                                if bool(entity_dct):
                                    acct2iia = mapping['AccountToIiaColumnMapping']
                                    kg_list = list(acct2iia.keys())
                                    final_kg_list = {}
                                    for entity, value in entity_dct.items():
                                        
                                        if entity in kg_list:
                                            for item in value:
                                               
                                                info_name = entity
                                                info_details = list(MongoDBPersistence.knowledge_entity_tbl.find(
                                                    {info_name: {"$regex": item, "$options": "i"}}, {'_id': 0}))
                                                if bool(info_details):
                                                    final_kg_list[item] = info_details
                                                print(item, ":::::::", info_details)
                                    if bool(final_kg_list):
                                        final_predictions['KgInfo'] = [final_kg_list]
                                    else:
                                        final_predictions['KgInfo'] = []


                            final_predictions["user_status"] = "Not Approved"
                            final_predictions["state"] = ticket["state"]
                            final_predictions['predicted_fields'] = conf_score
                            final_predictions['CustomerID'] = customer_id
                            final_predictions['DatasetID'] = dataset_id
                            final_predictions['timestamp'] = datetime.fromtimestamp(time.time()).strftime(
                                "%Y-%m-%d %H:%M:%S")
                            if (entity_dct):
                                print("Entities Captured", entity_dct)
                                final_entities = []

                                for entity, value in entity_dct.items():
                                    entities = {}
                                    entities["Entity"] = entity
                                    entities["Value"] = value
                                    final_entities.append(entities)
                                final_predictions['NamedEntities'] = final_entities
                            final_predictions_lst.append(final_predictions)
                        # --Automatic approval of incident tickets based on threshold value--
                        if (t_value_enabled and total_fields_to_be_perdicted == t_value_confidence_flag):
                            temp_doc = {}
                            temp_doc[ticket_id_field_name] = ticket[ticket_id_field_name]
                            temp_doc['DatasetID'] = ticket['DatasetID']
                            for doc in conf_score:
                                key = list(doc.keys())[0]
                                predicted_value = doc[key]
                                temp_doc[key] = predicted_value

                            tickets_to_be_approved.append(temp_doc)

                # --calling assignment logic from new location--
                if (pred_assignment_grp_lst):
                    print("--------------1-------------", pred_assignment_grp_lst)

                    obj = Assignment(possible_assignee_for_assignment=pred_assignment_grp_lst)
                    assignees = obj.assignmentRouting()
                    logging.info(f"assignees: {assignees}")
                    logging.info('%s: values in pred assignment grp lst and %s: values in tickets to be approved' % (
                    str(len(pred_assignment_grp_lst)), str(len(tickets_to_be_approved))))
                    sub_index = 0
                    total_approve_tickets = len(tickets_to_be_approved)
                    ### #####code to not approve tickets with empty assignee-Start0
                    tick_with_empty_assingee = []
                    for fin in final_predictions_lst:
                        if (fin['possible_assignees'] == []):
                            tick_with_empty_assingee.append(fin[ticket_id_field_name])
                    print("tick_with_empty_assingee", tick_with_empty_assingee)
                    ### #####code to not approve tickets with empty assignee-END
                    
                    logging.debug(f"total_approve_tickets: {total_approve_tickets}")
                    logging.debug(f"pred_assignment_grp_lst: {len(pred_assignment_grp_lst)}")
                    logging.debug(f"final_predictions_lst: {len(final_predictions_lst)}")
                    logging.debug(f"pred_assignment_grp_lst: {pred_assignment_grp_lst}")
                    logging.debug(f"final_predictions_lst: {final_predictions_lst}")

                    if (len(pred_assignment_grp_lst) == len(final_predictions_lst)):

                        logging.info(f"len(assignees) : {len(assignees)}")
                        logging.info(f"len(pred_assignment_grp_lst) : {len(pred_assignment_grp_lst)}")
                        logging.info(f"assignees : {assignees}")
                        logging.info(f"pred_assignment_grp_lst : {pred_assignment_grp_lst}")
                        if (len(assignees) == len(pred_assignment_grp_lst)):
                            for index in range(0, len(pred_assignment_grp_lst)):
                                try:
                                    
                                    assignee = assignees[index]
                                    
                                    final_predictions_lst[index]['predicted_assigned_to'] = assignee
                                    
                                    if total_approve_tickets > 0:
                                        if (sub_index < total_approve_tickets and t_value_enabled and
                                                tickets_to_be_approved[sub_index][ticket_id_field_name] ==
                                                final_predictions_lst[index][ticket_id_field_name]):
                                            

                                            tickets_to_be_approved[sub_index]['predicted_assigned_to'] = assignee
                                            sub_index = sub_index + 1
                                    else:
                                        logging.debug("Total Approved Tickets is 0")
                                except Exception as e:
                                    logging.error(e, exc_info=True)
                            #####code to not approve tickets with empty assignee-Start1
                            tick_number_approved = []
                            for tick in tickets_to_be_approved:
                                tick_number_approved.append(tick[ticket_id_field_name])

                            for tick_empty in tick_with_empty_assingee:
                                if (tick_empty in tick_number_approved):
                                    index = 0
                                    for ti in tickets_to_be_approved:
                                        if (ti[ticket_id_field_name] == tick_empty):
                                            del tickets_to_be_approved[index]
                                            break
                                        else:
                                            index += 1
                            #####code to not approve tickets with empty assignee -END1

                        else:
                            logging.warn(
                                'Assignment of assignees not possible as not enough assignee details able to get from Assignment module!, Please varify proper assignee details are uploaded')
                    else:
                        logging.info(
                            '%s: no. of assignment groups predicted and no. of tickets predicted are different! cannot assign resource' % RestService.timestamp())
                else:
                    logging.info("In application settings assignment_module is not enabled ...")
                
                all_ok_flag = 1
                if (all_ok_flag):
                    try:

                        logging.info(
                            '%s: Trying to insert newly predicted record into TblPredictedData.' % RestService.timestamp())                        
                        MongoDBPersistence.predicted_tickets_tbl.insert_many(final_predictions_lst)
                        to_approved = []
                        auto_dict = {}
                        auto_dict["user_status"] = "Approved"
                        for ticket in tickets_to_be_approved:
                            to_approved.append(ticket[ticket_id_field_name])

                        for ticket in final_predictions_lst:
                            if (ticket[ticket_id_field_name] in to_approved):
                                MongoDBPersistence.predicted_tickets_tbl.update_one(
                                    {'CustomerID': customer_id, ticket_id_field_name: ticket[ticket_id_field_name],
                                     'DatasetID': ticket['DatasetID']}, {"$set": auto_dict}, upsert=False)

                        logging.info('%s: Record inserted successfully.' % RestService.timestamp())
                    except Exception as e:
                        logging.error('%s: Error occurred: %s ' % (RestService.timestamp(), str(e)))

                # --Automatic approval of incident tickets based on threshold value-
                if (t_value_enabled and tickets_to_be_approved):
                    Predict.automaticTicketApproval(customer_id, dataset_id, tickets_to_be_approved)

                if (len(garbage_tickets) > 0):
                    result['DatasetID'] = -1
    
                    logging.info("%d tickets cannot be predicted.. dataset info missing" % len(garbage_tickets))
                else:
                    result['DatasetID'] = dataset_id
                    
                after_predict = datetime.now()
                logging.debug(f"after_predict: {after_predict}")
                logging.debug(f"time_taken: {after_predict-before_predict}")
                seconds_elapsed = after_predict-before_predict
                print(f"time_taken: %s " % (seconds_elapsed))
                return json_util.dumps(result)
            else:
                logging.info("%s User is not authenticated" % RestService.timestamp())
                return "failure"
    
    @staticmethod
    def update_user_status(customer_id, dataset_id, t_value):
        result = {}
        if (session.get('user')):
            logging.info("%s Catching User Session" % RestService.timestamp())
            user = session['user']
            logging.info("%s Session catched user as  %s" % (RestService.timestamp(), user))
        else:
            logging.info("%s You are not logged in please login" % RestService.timestamp())
            return "No Login Found"
        login_user = MongoDBPersistence.users_tbl.find_one({"UserID": user}, {"_id": 0})
        if (login_user):
            field_mapping = MappingPersistence.get_mapping_details(customer_id)
            ticket_id_field_name = field_mapping['Ticket_ID_Field_Name']
            predicted_tkts = list(MongoDBPersistence.predicted_tickets_tbl.find({'CustomerID': customer_id, "DatasetID": dataset_id, "user_status":"Not Approved"}))
            if(predicted_tkts):
                try:    
                    auto_dict = {}
                    auto_dict["user_status"] = "Approved"
                    tickets_to_be_approved = []
                    for ticket in predicted_tkts:
                        for field in ticket['predicted_fields']:
                            if(float(field['ConfidenceScore']) >= float(t_value)):
                                temp_doc = {}
                                temp_doc[ticket_id_field_name] = ticket[ticket_id_field_name]
                                temp_doc['DatasetID'] = ticket['DatasetID']
                                key = list(field.keys())[0]
                                predicted_value = field[key]
                                temp_doc[key] = predicted_value
                                MongoDBPersistence.predicted_tickets_tbl.update_one(
                                                        {'CustomerID': customer_id, ticket_id_field_name: ticket[ticket_id_field_name],
                                                        'DatasetID': ticket['DatasetID']}, {"$set": auto_dict}, upsert=False)
                                tickets_to_be_approved.append(temp_doc)
                                
                    logging.info('%s: Records updated successfully.' % RestService.timestamp())
                except Exception as e:
                    logging.error('%s: Error occurred: %s ' % (RestService.timestamp(), str(e)))
            else:
                logging.info('%s: No Record in predictdata table.' % RestService.timestamp())
                return "failure"

            t_value_doc = MongoDBPersistence.assign_enable_tbl.find_one({})
            t_value_enabled = t_value_doc['t_value_enabled']

            if (t_value_enabled and tickets_to_be_approved):
                Predict.automaticTicketApproval(customer_id, dataset_id, tickets_to_be_approved)
            return "success"
        else:
            logging.info("%s User is not authenticated" % RestService.timestamp())
            return "failure"
    
    @staticmethod
    def getPredictedTickets(customer_id, dataset_id):

        # rt_tickets_tbl is a pymongo object to TblIncidentRT
        predicted_tkts = MongoDBPersistence.predicted_tickets_tbl.find(
            {'CustomerID': customer_id, "DatasetID": dataset_id})
        if (predicted_tkts):
            logging.info('%s: Getting real time tickets.' % RestService.timestamp())
            resp = json_util.dumps(predicted_tkts)
        else:
            logging.info('%s: Failed to get real time tickets.' % RestService.timestamp())
            resp = 'failure'
        return resp

    @staticmethod
    def getPredictedTicketsCount(customer_id, dataset_id, prev_pred_state):
        try:

            # --fetching tikets specific for team--
            if (session.get('user')):
                logging.info("%s Catching User Session" % RestService.timestamp())
                user = session['user']
                role = session['role']
                logging.info("%s Session catched user as  %s" % (RestService.timestamp(), user))
                if (role == 'Admin'):
                    match_doc = {'CustomerID': customer_id, 'DatasetID': dataset_id}
                else:
                    user_doc = MongoDBPersistence.users_tbl.find_one({'UserID': user})
                    if (user_doc):
                        team_id = int(user_doc['TeamID'])
                        team_doc = MongoDBPersistence.teams_tbl.find_one({'TeamID': team_id})
                        if (team_doc):
                            dataset_id = team_doc['DatasetID']
                            match_doc = {'CustomerID': customer_id, "DatasetID": dataset_id}
                        else:
                            logging.warn('There is no document in Tbl_Teams with team id %s' % str(team_id))
                    else:
                        logging.warn('There is no document in Tbl_Users with user_id %s' % user)
            else:
                logging.info("%s You are not logged in please login" % RestService.timestamp())
                return "No Login Found"
            
            if (prev_pred_state == 'false'):
                match_doc['user'] = {'$exists': False}
            predicted_tkts_count = MongoDBPersistence.predicted_tickets_tbl.count(match_doc)
        except Exception as e:
            logging.error('%s: %s' % (RestService.timestamp(), str(e)))
        if (predicted_tkts_count):
            logging.info('%s: Getting real time tickets.' % RestService.timestamp())
            resp = json_util.dumps({'count': predicted_tkts_count})
        else:
            logging.info('%s: Failed to get real time tickets.' % RestService.timestamp())
            resp = 'failure'
        return resp

    @staticmethod
    def getPredictedData(customer_id, dataset_id, ticket_id):

        field_mapping = MappingPersistence.get_mapping_details(customer_id)
        group_field_name = field_mapping['Group_Field_Name']
        ticket_id_field_name = field_mapping['Ticket_ID_Field_Name']
        status_field_name = field_mapping['Status_Field_Name']
        description_field_name = field_mapping['Description_Field_Name']
        # predicted_tickets_tbl is a pymongo object to TblPredictedData
        result = MongoDBPersistence.predicted_tickets_tbl.find(
            {'CustomerID': customer_id, "DatasetID": dataset_id, ticket_id_field_name: ticket_id})
        if (result):
            logging.info('%s: Getting predicted ticket.' % RestService.timestamp())
            resp = json_util.dumps(result)
        else:
            logging.info('%s: Failed to get predicted tickets.' % RestService.timestamp())
            resp = 'failure'
        return resp

    @staticmethod
    def getPredictedFields(customer_id, chosen_team):
        print("Inside getPredictedFields function in Predict class in src predict.py ")
        # these two values should come from front end
        dataset_id_all = MongoDBPersistence.teams_tbl.find_one({"CustomerID": customer_id, "TeamName": chosen_team},
                                                               {"DatasetID": 1, "_id": 0})
        print('dataset_id_all : ', dataset_id_all)
        print('dataset id :', dataset_id_all['DatasetID'])
        dataset_id = dataset_id_all['DatasetID']
        # customer_tbl is a pymongo object to TblCustomer
        TrainingMode = MongoDBPersistence.datasets_tbl.find_one({"CustomerID": customer_id, "DatasetID": dataset_id},
                                                                {"training_mode": 1, "_id": 0})
        print("TrainingMode:", TrainingMode)
        if TrainingMode['training_mode'] == "EDA":
            print("THIS IS EDA")
            result = MongoDBPersistence.datasets_tbl.find_one({"CustomerID": customer_id, "DatasetID": dataset_id},
                                                              {"FieldSelections": 1, "UniqueFields": 1,
                                                               "DependedPredict": 1, "BestAlgoParams": 1, "_id": 0})
            if (result):
                keys = result.keys()
                if ('DependedPredict' in keys and 'FieldSelections' in keys and result['DependedPredict'][0][
                    'flag'] == 'true'):
                    for predict_field in result['FieldSelections'][0]['PredictedFields']:
                        if predict_field['usePredFieldFlag'] == 'true':
                            for dependend_field in result['DependedPredict'][0]['values']:
                                if (predict_field['PredictedFieldName'] == dependend_field['PredictValue']):
                                    for dependend_value in dependend_field['DepPredictValue']:
                                        predict_field['InputFields'][predict_field['InputFields'].index(
                                            dependend_value)] = 'predicted_' + dependend_value
                    del result['DependedPredict']
                resp = json_util.dumps(result)
                logging.info('%s: Getting FieldSelections of the customer...' % RestService.timestamp())

            else:
                resp = ''
                logging.info(
                    '%s: FieldSelections not found in TblDataset, returning empty string...' % RestService.timestamp())
            return resp

        elif TrainingMode['training_mode'] == "IIA":
            print("THIS IS IIA")
            result = MongoDBPersistence.datasets_tbl.find_one({"CustomerID": customer_id, "DatasetID": dataset_id},
                                                              {"FieldSelections": 1, "UniqueFields": 1,
                                                               "DependedPredict": 1, "GridsearchParams": 1, "_id": 0})
            if (result):
                keys = result.keys()
                if ('DependedPredict' in keys and 'FieldSelections' in keys and result['DependedPredict'][0][
                    'flag'] == 'true'):
                    for predict_field in result['FieldSelections'][0]['PredictedFields']:
                        if predict_field['usePredFieldFlag'] == 'true':
                            for dependend_field in result['DependedPredict'][0]['values']:
                                if (predict_field['PredictedFieldName'] == dependend_field['PredictValue']):
                                    for dependend_value in dependend_field['DepPredictValue']:
                                        predict_field['InputFields'][predict_field['InputFields'].index(
                                            dependend_value)] = 'predicted_' + dependend_value
                    del result['DependedPredict']
                resp = json_util.dumps(result)
                logging.info('%s: Getting FieldSelections of the customer...' % RestService.timestamp())



            else:
                resp = ''
                logging.info(
                    '%s: FieldSelections not found in TblDataset, returning empty string...' % RestService.timestamp())
            return resp

    @staticmethod
    def updatePredictedDetails(customer_id, dataset_id):
        try:

            data = request.get_json()
            itsm_details = MongoDBPersistence.itsm_details_tbl.find_one({"CustomerID": customer_id}, {"_id": 0})
            obj = ITSMAdapter(itsm_details=itsm_details, customer_id=customer_id, dataset_id=dataset_id, data=data)
            logging.info("Inside updatePredictedDetails")
            return obj.updateITSMFields()
        except Exception as e:
            print("Error in Update predicted", e)
            return "failure"

    @staticmethod
    def automaticTicketApproval(customer_id, dataset_id, data=[]):
        logging.info("Auto Ticket Approval")

        field_mapping = MappingPersistence.get_mapping_details(customer_id)
        ticket_id_field_name = field_mapping['Ticket_ID_Field_Name']

        try:
            
            incidentNumber = ''
            incident_lst = []
            servicenow_exists = MongoDBPersistence.customer_tbl.find_one({"CustomerID": customer_id},
                                                                         {"_id": 0, "SNOWInstance": 1})
            if (servicenow_exists):
                servicenow_flag = 1
            else:
                servicenow_flag = 0
            if (data):
                
                resolution_tickets = data.copy()
                for incidentToUpdate in data:
                    incidentNumber = incidentToUpdate[ticket_id_field_name]
                    incident_lst.append(incidentNumber)
                    assigned_to = ''
                    try:
                        assigned_to = incidentToUpdate['predicted_assigned_to']
                        incidentToUpdate[
                            'work_notes'] = f"Ticket Auto Approved and Assigned to {assigned_to} by Infosys Intelligent Assistant"
                    except Exception as e:
                        logging.error(e, exc_info=True)

                    logging.info(f"Updating RT Table for ticket {incidentNumber}")
                    update_result = MongoDBPersistence.rt_tickets_tbl.update_one(
                        {'CustomerID': customer_id, ticket_id_field_name: incidentNumber, 'DatasetID': dataset_id},
                        {"$set": {'user_status': 'Approved'}}, upsert=False)

                    # the following code is for inserting approved tickets into Training table for Retraining
                    incidentToUpdate['CustomerID'] = customer_id
                    
                    incidentToUpdate["DatasetID"] = incidentToUpdate["DatasetID"]
                   
                    incidentToinsert = MongoDBPersistence.rt_tickets_tbl.find_one(
                        {ticket_id_field_name: incidentNumber})
                    incidentToinsert['TrainingFlag'] = 0
                    
                    try:
                        MongoDBPersistence.training_tickets_tbl.update_one(
                            {ticket_id_field_name: incidentToinsert[ticket_id_field_name]}, {"$set": incidentToinsert},
                            upsert=True)
                    except Exception as e:
                        print(str(e))
                    logging.info(f"incidentToUpdate: {incidentToUpdate}")
                    try:
                        MongoDBPersistence.approved_tickets_tbl.insert_one({
                            'CustomerID': customer_id,
                            'DatasetID': incidentToUpdate["DatasetID"],
                            'ticket_number': incidentNumber,
                            'assigned_to': assigned_to,
                            'auto_approve': True
                        })
                        MongoDBPersistence.rt_tickets_tbl.update_one(
                            {ticket_id_field_name: incidentToinsert[ticket_id_field_name]}
                            , {"$set": {'assigned_to': assigned_to}})
                    except Exception as e:
                        logging.error(e, exc_info=True)

                    MongoDBPersistence.predicted_tickets_tbl.update_one(
                        {'CustomerID': customer_id, ticket_id_field_name: incidentNumber,
                         'DatasetID': incidentToUpdate["DatasetID"]}, {"$set": incidentToUpdate}, upsert=False)
                    MongoDBPersistence.rt_tickets_tbl.update_one(
                        {'CustomerID': customer_id, ticket_id_field_name: incidentNumber,
                         'DatasetID': incidentToUpdate["DatasetID"]}, {"$set": incidentToUpdate}, upsert=False)

                    logging.info(f"servicenow_flag: {servicenow_flag}")
                    servicenow_exists = ServiceNow.getClient()

                    logging.info(f"ServiceNow.servicenow_incidents: {servicenow_exists}")
                    if (servicenow_flag and servicenow_exists != None):
                        service_now_update_dict = {}
                        ticket_id = incidentToUpdate[ticket_id_field_name]
                        for key, value in incidentToUpdate.items():
                            key = key.lower()
                            if (key == 'predicted_assigned_to'):
                                key = 'assigned_to'
                            service_now_update_dict[key]=value
                        try:
                            servicenow_exists.update(query={ticket_id_field_name: ticket_id},
                                                     payload=service_now_update_dict)
                        except Exception as e:
                            logging.error(e)
                            pass
                    logging.info(
                        '%s: Predicted Details has been successfully updated into a collection TblPredictedData.' % RestService.timestamp())
                    try:

                        ITSMAdapter.notifications(incidentToUpdate, ticket_id_field_name)

                    except Exception as e:
                        logging.error(e, exc_info=True)

                    resp = 'success'
                # --Workload calculation--
                ticket_number_list = []
                for incidentToUpdate in data:
                    ticket_number_list.append(incidentToUpdate[ticket_id_field_name])
                    ResourceMasterData.incident_workload_update(customer_id, incidentToUpdate['DatasetID'],
                                                                ticket_number_list)

                # =============Auto Resolution================#
                try:
                    for resolution_ticket in resolution_tickets:
                        logging.info(f"Running Auto Resolution for {resolution_ticket[ticket_id_field_name]}")
                        mongodb_result = MongoDBPersistence.rt_tickets_tbl.find_one(
                            {'number': resolution_ticket[ticket_id_field_name]},
                            {"description": 1, "_id": 0})
                        description = str(mongodb_result[description_field_name])

                        possible_resolutions = json_util.loads(
                            Resolution.getPossibleResolutions(number=resolution_ticket[ticket_id_field_name], desc=description,
                                                              tags=[]))
                        logging.info(f"possible_resolutions: {possible_resolutions}")
                        for resolution in possible_resolutions:
                            try:
                                logging.info(f"running resolution: {resolution}")
                                if resolution['type'] == 'script':
                                    auto_resolution_result = Resolution.invokeIopsScripts(script_name=resolution['name'],
                                                                                          env='local',
                                                                                          script_type= 'main',
                                                                                          args={'ticket_number': resolution_ticket[ticket_id_field_name]}
                                                                                          )
                                    logging.info(f"auto_resolution_result: {auto_resolution_result}")

                                    if 'error' not in auto_resolution_result.lower():
                                        MongoDBPersistence.rt_tickets_tbl.update_one(
                                            {'CustomerID': customer_id, ticket_id_field_name: incidentNumber,
                                             'DatasetID': incidentToUpdate["DatasetID"]}, {"$set": {'auto_resolution': True}},
                                            upsert=False)

                            except Exception as e:
                                logging.error(e, exc_info=True)
                                pass

                except Exception as e:
                    logging.error(e, exc_info=True)

                resp = 'success'
                # ------------------------
            else:
                logging.info(
                    '%s: Getting empty JSON from Angular component, returning string empty...' % RestService.timestamp())
                resp = 'empty'
        except Exception as e:
            logging.error('%s: Error occurred: %s ' % (RestService.timestamp(), str(e)))
            resp = 'failure'

        return resp

    @staticmethod
    def getfirstPredDataSetID():
        try:
            logging.info("Running getfirstPredDataSetID")
            if (session.get('user')):
                logging.info("%s Catching User Session" % RestService.timestamp())
                user = session['user']
                role = session['role']
                logging.info("%s Session catched user as  %s" % (RestService.timestamp(), user))
                if (role == 'Admin'):
                    match_doc = {}
                else:
                    user_doc = MongoDBPersistence.users_tbl.find_one({'UserID': user})
                    if (user_doc):
                        team_id = int(user_doc['TeamID'])
                        team_doc = MongoDBPersistence.teams_tbl.find_one({'TeamID': team_id})
                       
                        if (team_doc):
                            dataset_id = team_doc['DatasetID']
                            match_doc = {"DatasetID": dataset_id}
                        else:
                            logging.warn('There is no document in Tbl_Teams with team id %s' % str(team_id))
                    else:
                        logging.warn('There is no document in Tbl_Users with user_id %s' % user)
            else:
                logging.info("%s You are not logged in please login" % RestService.timestamp())
                return "No Login Found"

            datasetID = MongoDBPersistence.predicted_tickets_tbl.find_one(match_doc, {"DatasetID": 1, "_id": 0})
            
        except Exception as e:
            logging.error('%s: Error occurred: %s ' % (RestService.timestamp(), str(e)))
            logging.error(e, exc_info=True)
            datasetID = "Failure"

        return json_util.dumps(datasetID)

    @staticmethod
    def getPredictedTicketsForPage(customer_id, dataset_id, page_size, page_num, prev_pred_state, show_app_ticket):
        resp = 'failure'
        try:

            # --fetching tikets specific for team--
            if (session.get('user')):
                logging.info("%s Catching User Session" % RestService.timestamp())
                user = session['user']
                role = session['role']
                logging.info("%s Session catched user as  %s" % (RestService.timestamp(), user))
                if (role == 'Admin'):
                    match_doc = {'CustomerID': customer_id, 'DatasetID': dataset_id}
                else:
                    user_doc = MongoDBPersistence.users_tbl.find_one({'UserID': user})
                    if (user_doc):
                        team_id = int(user_doc['TeamID'])
                        team_doc = MongoDBPersistence.teams_tbl.find_one({'TeamID': team_id})
                        if (team_doc):
                            if dataset_id == -1:
                                dataset_id = team_doc['DatasetID']
                            match_doc = {'CustomerID': customer_id, "DatasetID": dataset_id}
                        else:
                            logging.warn('There is no document in Tbl_Teams with team id %s' % str(team_id))
                    else:
                        logging.warn('There is no document in Tbl_Users with user_id %s' % user)
            else:
                logging.info("%s You are not logged in please login" % RestService.timestamp())
                return "No Login Found"
            # ----------------------------------------
           
            if (show_app_ticket == "false"):
                match_doc['user_status'] = 'Not Approved'
            else:
                match_doc['user_status'] = 'Approved'
                
            field_mapping = MappingPersistence.get_mapping_details(customer_id)
            
            ticket_id_field_name = field_mapping['Ticket_ID_Field_Name']
            description_field_name = field_mapping['Description_Field_Name']
            
            if (prev_pred_state == 'false'):
                match_doc['user'] = {'$exists': False}
            incident_numbers_to_map = []
            skips = page_size * (page_num - 1)
            
            logging.info(f"prev_pred_state: {prev_pred_state}")
            logging.info(f"match_doc: {match_doc}")
            logging.info(f"skips: {skips}")
            logging.info(f"page_size:{page_size}")

            if 'DatasetID' not in match_doc and dataset_id > 0:
                match_doc['DatasetID'] = dataset_id
            
            if (show_app_ticket == "false"):
                result = list(
                MongoDBPersistence.predicted_tickets_tbl.find(match_doc).sort('timestamp', -1).skip(skips).limit(
                    page_size))
            else:
                incidentsnum_to_map = list(MongoDBPersistence.rt_tickets_tbl.find({"CustomerID":customer_id, "DatasetID":dataset_id, "state": {"$nin": ["closed"]}, "user_status":{"$in":["Approved"]}}).sort('timestamp', -1).skip(skips).limit(
                    page_size))
                incident_numbers_to_map1 = []
                for i in incidentsnum_to_map:
                    if ticket_id_field_name not in i:
                        i[ticket_id_field_name] = i[ticket_id_field_name]
                    incident_numbers_to_map1.append(i[ticket_id_field_name])
                result = list(MongoDBPersistence.predicted_tickets_tbl.find({ticket_id_field_name: {"$in": incident_numbers_to_map1}}))

            if not result:
                resp = "no data"
                return resp

            prediction_to_show = []
            try:
                config = configparser.ConfigParser()
                config["DEFAULT"]['path'] = "config/"
                config.read(config["DEFAULT"]["path"] + "iia.ini")
                confidenceScore = None
                try:
                    confidenceScore = config["Account"]["confidenceScore"]
                except Exception as e:
                    logging.error("Taking default confidenceScore Configurations %s" % (str(e)))
                logging.info(f"confidenceScore: {confidenceScore}")
                if (confidenceScore is not None):
                    logging.info("Confidence Score is not none , Filtering on behalf Score %s" % (confidenceScore))
                    for pred in result:
                        if ticket_id_field_name not in pred:
                            pred[ticket_id_field_name] = pred[ticket_id_field_name]
                        if 'description' not in pred:
                           pred['description']=pred[description_field_name]
                        for feilds in pred["predicted_fields"]:
                            flag = True
                            if (float(feilds["ConfidenceScore"]) < float(confidenceScore)):
                                flag = False
                                break
                        if (flag):
                            incident_numbers_to_map.append(pred[ticket_id_field_name])
                            prediction_to_show.append(pred)
                else:
                    for incident in result:
                        
                        if ticket_id_field_name not in incident:
                            incident[ticket_id_field_name] = incident[ticket_id_field_name]
                        if 'description' not in incident:
                           incident['description']=incident[description_field_name]
                        incident_numbers_to_map.append(incident[ticket_id_field_name])
                    prediction_to_show = result
            except Exception as e:
                logging.error("No Entry of Confidence Score in .ini file %s" % (str(e)))

            if (prediction_to_show):
                logging.info('%s: Getting real time tickets.' % RestService.timestamp())
                incidents_to_map = list(
                    MongoDBPersistence.rt_tickets_tbl.find({ticket_id_field_name: {"$in": incident_numbers_to_map}}))
                
                final_result = []
                for index, incident in enumerate(prediction_to_show):
                  
                    for rt_incident in incidents_to_map:
                       
                        if ticket_id_field_name not in rt_incident:
                            rt_incident[ticket_id_field_name] = rt_incident[ticket_id_field_name]

                        if (incident[ticket_id_field_name] == rt_incident[ticket_id_field_name]):
                            for key in incident.keys():
                                if key in rt_incident.keys():
                                    continue
                                else:
                                    rt_incident[key] = incident[key]
                            final_result.append(rt_incident)
                            break

                prediction_to_show = final_result

                resp = json_util.dumps(prediction_to_show)
            else:
                logging.info('%s: Failed to get real time tickets.' % RestService.timestamp())
                resp=json_util.dumps(prediction_to_show)
                #resp = 'failure'
                return resp
        except Exception as e:
            logging.error('%s: Error: %s' % (RestService.timestamp(), str(e)))

        return resp

    @staticmethod
    def assignmentEnableStatus(field, current_status, customer_id, chosen_team):
        try:
            # these two values should come from front end
            dataset_id_all = MongoDBPersistence.teams_tbl.find_one({"CustomerID": customer_id, "TeamName": chosen_team},
                                                                   {"DatasetID": 1, "_id": 0})
            print('dataset id :', dataset_id_all['DatasetID'])
            dataset_id = dataset_id_all['DatasetID']

            MongoDBPersistence.assign_enable_tbl.update_one({'DatasetID': dataset_id},
                                                            {'$set': {field: current_status}}, upsert=True)
        except Exception as e:
            logging.error('%s: Error: %s' % (RestService.timestamp, str(e)))
            return "Failure"
        return "Success"

    @staticmethod
    def getSwitchStatus(customer_id, chosen_team):
        try:
            # these two values should come from front end
            dataset_id_all = MongoDBPersistence.teams_tbl.find_one({"CustomerID": customer_id, "TeamName": chosen_team},
                                                                   {"DatasetID": 1, "_id": 0})
            print('dataset id :', dataset_id_all['DatasetID'])
            dataset_id = dataset_id_all['DatasetID']

            res = {}
            logging.info('%s: assigning response document with default values' % RestService.timestamp())
            res['assignment_enabled'] = 'true'
            res['prediction_enabled'] = 'true'
            res['t_value_enabled'] = 'false'
            res['tValue'] = 0
            res['auto_refresh_state'] = 'false'
            res['train_NER_model_on'] = ''
            res['roundrobin_enabled'] = 'false'
            res['assignment_logic_dependancy_field'] = ''
            res['regex_enabled'] = 'false'
            res['db_enabled'] = 'false'
            res['spacy_enabled'] = 'false'
            res['sms_enabled'] = 'false'
            res['whatsapp_enabled'] = 'false'
            res['call_enabled'] = 'false'
            res['msteams_enabled'] = 'false'
            res['twilio_enabled'] = 'false'
            res['non_english_description_flag'] = 'false'
            logging.info('fetching details from "assign_enable_tbl"')
            # doc = MongoDBPersistence.assign_enable_tbl.find_one({})
            doc = MongoDBPersistence.assign_enable_tbl.find_one({"DatasetID": dataset_id}, {"_id": 0})
            if (doc):
                logging.info('found document from "assign_enable_tbl"!')
                keys = list(doc.keys())
                if ('assignment_enabled' in keys):
                    res['assignment_enabled'] = doc['assignment_enabled']

                if ('threshold_value' in keys):
                    res['tValue'] = doc['threshold_value']

                if ('t_value_enabled' in keys):
                    res['t_value_enabled'] = doc['t_value_enabled']

                if ('prediction_enabled' in keys):
                    res['prediction_enabled'] = doc['prediction_enabled']

                if ('non_english_description_flag' in keys):
                    res['non_english_description_flag'] = doc['non_english_description_flag']

                if ('auto_refresh_state' in keys):
                    res['auto_refresh_state'] = doc['auto_refresh_state']

                if ('train_NER_model_on' in keys):
                    res['train_NER_model_on'] = doc['train_NER_model_on']

                if ('roundrobin_enabled' in keys):
                    res['roundrobin_enabled'] = doc['roundrobin_enabled']
                if ('assignment_logic_dependancy_field' in keys):
                    res['assignment_logic_dependancy_field'] = doc['assignment_logic_dependancy_field']

                if ('regex_enabled' in keys):
                    res['regex_enabled'] = doc['regex_enabled']
                if ('db_enabled' in keys):
                    res['db_enabled'] = doc['db_enabled']
                if ('spacy_enabled' in keys):
                    res['spacy_enabled'] = doc['spacy_enabled']

                if ('sms_enabled' in keys):
                    res['sms_enabled'] = doc['sms_enabled']
                if ('whatsapp_enabled' in keys):
                    res['whatsapp_enabled'] = doc['whatsapp_enabled']
                if ('call_enabled' in keys):
                    res['call_enabled'] = doc['call_enabled']
                if ('msteams_enabled' in keys):
                    res['msteams_enabled'] = doc['msteams_enabled']
                if ('twilio_enabled' in keys):
                    res['twilio_enabled'] = doc['twilio_enabled']
            else:
                logging.info('not found any document from "assign_enable_tbl"!')

        except Exception as e:
            logging.error('%s: Error: %s' % (RestService.timestamp, str(e)))
            return "Failure"

        return json_util.dumps(res)

    @staticmethod
    def insertTValue(customer_id, chosen_team):
        try:
            # these two values should come from front end
            dataset_id_all = MongoDBPersistence.teams_tbl.find_one({"CustomerID": customer_id, "TeamName": chosen_team},
                                                                   {"DatasetID": 1, "_id": 0})
            print('dataset_id_all : ', dataset_id_all)
            print('dataset id :', dataset_id_all['DatasetID'])
            dataset_id = dataset_id_all['DatasetID']
            t_value_doc = request.get_json()
            print('t_value_doc : ', t_value_doc)
            if (t_value_doc != 'null'):
                print('Inside if')
                try:
                    MongoDBPersistence.assign_enable_tbl.update_one({'DatasetID': dataset_id},
                                                                    {'$set': {'threshold_value': t_value_doc}},
                                                                    upsert=True)
                    print('T Value Updated')
                except Exception as e:
                    print('Test exception ', str(e))

            t_value = t_value_doc[0]['tValue']
            print('t value : ', t_value)
            cust_ids = MongoDBPersistence.customer_tbl.distinct("CustomerID")
            dataset_ids = MongoDBPersistence.teams_tbl.distinct("DatasetID")
            print('cust_ids : ', cust_ids)
            print('dataset_ids : ', dataset_ids)
            for cust_id in cust_ids:
                for datast_id in dataset_ids:
                    try:
                        resp = Predict.update_user_status(cust_id, datast_id, t_value)
                        logging.info(
                            "User status updated for Customer_ID %s and DatasetID %s" % (str(cust_id), str(datast_id)))
                    except:
                        logging.info(
                            "%s Customer_ID or DatasetID is not presented in predictdata table" % RestService.timestamp())
        except Exception as e:
            logging.error('%s: Error: %s' % (RestService.timestamp, str(e)))
            return "Failure"
        return "Success"

    @staticmethod
    def insertAccuracyPercent(percent, customer_id):
        try:

            if (percent != 'null' and percent != 0):
                MongoDBPersistence.configuration_values_tbl.update_one({}, {
                    '$set': {'accuracy_percent': percent, 'CustomerID': customer_id}}, upsert=True)
       
        except Exception as e:
            logging.error('%s: Error: %s' % (RestService.timestamp, str(e)))
            print('Failure')
            return "Failure"
        print('Success')
        return "Success"

    @staticmethod
    def insertITSMSourceDetails():
        json_data = request.get_json()
        path_url = json_data['url']
        source_name = json_data['source']

        try:
            if (path_url != ' ' and path_url != ''):
                MongoDBPersistence.configuration_values_tbl.update_one({}, {
                    '$set': {'ITSMUrl': path_url, 'DefaultKBSource': source_name}}, upsert=True)
        
        except Exception as e:
            logging.error('%s: Error: %s' % (RestService.timestamp, str(e)))
            print('Failure')
            return "Failure"
        print('Success')
        return "Success"

    @staticmethod
    def insertFileSourceDetails():
        json_data = request.get_json()
        path_url = json_data['url']
        source_name = json_data['source']

        try:
            if (path_url != ' ' and path_url != ''):
                MongoDBPersistence.configuration_values_tbl.update_one({}, {
                    '$set': {'FilePath': path_url, 'DefaultKBSource': source_name}}, upsert=True)
       
        except Exception as e:
            logging.error('%s: Error: %s' % (RestService.timestamp, str(e)))
            print('Failure')
            return "Failure"
        print('Success')
        return "Success"

    @staticmethod
    def insertSharepointSourceDetails():
        json_data = request.get_json()
        path_url = json_data['url']
        source_name = json_data['source']

        if (source_name == 'ITSM'):
            url_fld_nme = 'ITSMUrl'
        elif (source_name == 'File Server'):
            url_fld_nme = 'FilePath'
        elif (source_name == 'Sharepoint'):
            url_fld_nme = 'SharepointUrl'
        try:
            if (path_url != ' ' and path_url != ''):
                MongoDBPersistence.configuration_values_tbl.update_one({}, {
                    '$set': {url_fld_nme: path_url, 'DefaultKBSource': source_name}}, upsert=True)
       
        except Exception as e:
            logging.error('%s: Error: %s' % (RestService.timestamp, str(e)))
            print('Failure')
            return "Failure"
        print('Success')
        return "Success"

    @staticmethod
    def getMatchPercentage():
        try:
            print(1)

            percent = MongoDBPersistence.configuration_values_tbl.find_one({}, {"accuracy_percent": 1, "_id": 0})
            print(2)
            if (percent):
                resp = json_util.dumps(percent)
            else:
                resp = 'Failure'
            print(resp)
            return resp
       
        except Exception as e:
            logging.error('%s: Error: %s' % (RestService.timestamp, str(e)))
            print('Failure')
            return "Failure"

    @staticmethod
    def saveDefaultKBSource(source):
        try:
            if (source != ' ' and source != ''):
                MongoDBPersistence.configuration_values_tbl.update_one({}, {'$set': {'DefaultKBSource': source}},
                                                                       upsert=True)
        
        except Exception as e:
            logging.error('%s: Error: %s' % (RestService.timestamp, str(e)))
            print('Failure')
            return "Failure"
        print('Success')
        return "Success"

    @staticmethod
    def getDefaultKBSource():
        try:

            source = MongoDBPersistence.configuration_values_tbl.find_one({}, {"DefaultKBSource": 1, "_id": 0})

            if (source):
                resp = json_util.dumps(source)
            else:
                resp = 'Failure'
            print(resp)
            return resp
       
        except Exception as e:
            logging.error('%s: Error: %s' % (RestService.timestamp, str(e)))
            
            return "Failure"

    @staticmethod
    def getDefaultSourceDetails():
        try:

            source = MongoDBPersistence.configuration_values_tbl.find_one({}, {"DefaultKBSource": 1, "SharepointUrl": 1,
                                                                               "FilePath": 1, "ITSMUrl": 1,
                                                                               "Related_Tickets_Algorithm": 1,
                                                                               "_id": 0})
            if (source):
                response = json_util.dumps(source)
            else:
                response = 'Failure'
            print("getDefaultSourceDetails", response)
            return response
        except Exception as e:
            logging.error('%s: Error: %s' % (RestService.timestamp, str(e)))
            
            return "Failure"

    @staticmethod
    def predictionEnableStatus(field, current_status, customer_id, chosen_team):
        try:
            # these two values should come from front end
            dataset_id_all = MongoDBPersistence.teams_tbl.find_one({"CustomerID": customer_id, "TeamName": chosen_team},
                                                                   {"DatasetID": 1, "_id": 0})
            print('dataset id :', dataset_id_all['DatasetID'])
            dataset_id = dataset_id_all['DatasetID']

            MongoDBPersistence.assign_enable_tbl.update_one({'DatasetID': dataset_id},
                                                            {'$set': {field: current_status}}, upsert=True)

        except Exception as e:
            logging.error('%s: Error: %s' % (RestService.timestamp, str(e)))
            return "Failure"

        return "Success"

    @staticmethod
    def roundrobinEnableStatus(field, current_status):
        try:

            MongoDBPersistence.assign_enable_tbl.update_one({}, {'$set': {field: current_status}}, upsert=True)
        except Exception as e:
            logging.info('%s: Error: %s' % (RestService.timestamp, str(e)))
            return 'Failure'
        return 'Success'

    @staticmethod
    def hinglishEnableStatus(field, current_status, customer_id, chosen_team):
        try:
            # these two values should come from front end
            dataset_id_all = MongoDBPersistence.teams_tbl.find_one({"CustomerID": customer_id, "TeamName": chosen_team},
                                                                   {"DatasetID": 1, "_id": 0})

            dataset_id = dataset_id_all['DatasetID']
            MongoDBPersistence.assign_enable_tbl.update_one({'DatasetID': dataset_id},
                                                            {'$set': {field: current_status}}, upsert=True)
            print("updated Succesfully ")
        except Exception as e:
            logging.info('%s: Error: %s' % (RestService.timestamp, str(e)))
            return 'Failure'
        return 'Success'

    @staticmethod
    def nerEnableStatus(regex_status, db_status, spacy_status):
        try:
            ()
            MongoDBPersistence.assign_enable_tbl.update_one({}, {
                '$set': {"regex_enabled": regex_status, "db_enabled": db_status, 'spacy_enabled': spacy_status}},
                                                            upsert=True)
        except Exception as e:
            logging.info('%s: Error: %s' % (RestService.timestamp, str(e)))
            return 'Failure'
        return 'Success'

    @staticmethod
    def saveAnnotationTag():
        json_data = request.get_json()
        path_url = json_data['url']
        source_name = json_data['source']

        try:
            ()
            if (path_url != ' ' and path_url != ''):
                MongoDBPersistence.configuration_values_tbl.update_one({}, {
                    '$set': {'FilePath': path_url, 'DefaultKBSource': source_name}}, upsert=True)
        
        except Exception as e:
            logging.error('%s: Error: %s' % (RestService.timestamp, str(e)))
            print('Failure')
            return "Failure"
        print('Success')
        return "Success"

    @staticmethod
    def insertIopsStatus(status, customer_id, chosen_team):
        try:
            ()
            # these two values should come from front end
            dataset_id_all = MongoDBPersistence.teams_tbl.find_one({"CustomerID": customer_id, "TeamName": chosen_team},
                                                                   {"DatasetID": 1, "_id": 0})
            print('dataset id :', dataset_id_all['DatasetID'])
            dataset_id = dataset_id_all['DatasetID']
            if (status != None):
                MongoDBPersistence.assign_enable_tbl.update_one({'DatasetID': dataset_id},
                                                                {'$set': {'iOpsStatus': status}}, upsert=True)
        except Exception as e:
            logging.error('%s: Error: %s' % (RestService.timestamp, str(e)))
            return "Failure"
        return "Success"

    @staticmethod
    def insertIopsPath():
        path = request.form['Path']
        try:
            ()
            print(path)
            if (len(path) != 0):
                if ("\\" in path):
                    path.replace("\\", "\\\\")
                elif ("//" in path):
                    path.replace("//", "////")
                print(path)
                MongoDBPersistence.assign_enable_tbl.update_one({}, {'$set': {'iOpsPath': path}}, upsert=True)
       
        except Exception as e:
            logging.error('%s: Error: %s' % (RestService.timestamp, str(e)))
            return "Failure"
        return "Success"

    @staticmethod
    def getiOpsValues(customer_id, chosen_team):
        try:
            ()
            # these two values should come from front end
            dataset_id_all = MongoDBPersistence.teams_tbl.find_one({"CustomerID": customer_id, "TeamName": chosen_team},
                                                                   {"DatasetID": 1, "_id": 0})
            print('dataset id :', dataset_id_all['DatasetID'])
            dataset_id = dataset_id_all['DatasetID']

            source = MongoDBPersistence.assign_enable_tbl.find_one({'DatasetID': dataset_id},
                                                                   {"iOpsStatus": 1, 'iOpsPath': 1, "_id": 0})

            if (source):
                resp = json_util.dumps(source)
            else:
                resp = 'Failure'
            print(resp)
            return resp
        except Exception as e:
            logging.error('%s: Error: %s' % (RestService.timestamp, str(e)))
            return "Failure"

    @staticmethod
    def importantFeaturesReport(customer_id, dataset_id, number):

        try:
            ()
            logging.info("Inside important Features Report Generation")
            
            field_mapping = MappingPersistence.get_mapping_details(customer_id)
            ticket_id_field_name = field_mapping['Ticket_ID_Field_Name']
            cust_name = \
            MongoDBPersistence.customer_tbl.find_one({"CustomerID": customer_id}, {"CustomerName": 1, "_id": 0})[
                "CustomerName"]
            dataset_name = \
            MongoDBPersistence.datasets_tbl.find_one({"DatasetID": dataset_id}, {"DatasetName": 1, "_id": 0})[
                "DatasetName"]
            fields_selection = \
            MongoDBPersistence.datasets_tbl.find_one({"CustomerID": customer_id, "DatasetID": dataset_id}, \
                                                     {"FieldSelections": 1, "_id": 0})["FieldSelections"]
            print("selected fields are --", fields_selection)
            weight_final = {}

            pred_list = []
            for field in fields_selection:

                if (field["FieldsStatus"] == "Approved"):
                    pred_dict, tmp_dict = {}, {}
                    for inner_field in field["PredictedFields"]:
                        tmp_dict = {}
                        tmp_dict["inputFields"] = inner_field["InputFields"]
                        tmp_dict["algoName"] = inner_field["AlgorithmName"]
                        pred_dict[inner_field["PredictedFieldName"]] = tmp_dict
                    pred_list.append(pred_dict)
        
            inci_feilds = MongoDBPersistence.rt_tickets_tbl.find_one(
                {"CustomerID": customer_id, "DatasetID": dataset_id \
                    , ticket_id_field_name: number})

            pred_dict = pred_list[0]
            for pred_field, pred_values in pred_dict.items():
                try:
                    svc_flag = 0
                    merge_input = ""
                    for field in pred_values['inputFields']:
                        merge_input += inci_feilds[field] + " "
                    list_words = []
                    merge_input = re.sub("[^0-9a-zA-Z]", " ", merge_input)
                    merge_input = merge_input.lower()
                    merge_input = merge_input.split()
                    list_words = [word for word in merge_input if not word in set(ENGLISH_STOP_WORDS)]

                    o_fieldselection_list = \
                    MongoDBPersistence.datasets_tbl.find_one({'CustomerID': customer_id, "DatasetID": dataset_id},
                                                                {'FieldSelections.PredictedFields': 1, '_id': 0})[
                        'FieldSelections'][0]['PredictedFields']
                    for key in o_fieldselection_list:
                        if (key['PredictedFieldName'] == pred_field):
                            if (key['AlgorithmName'] == "SVC"):
                                svc_flag = 1
                            else:
                                svc_flag = 0
                    vocab_path = 'data/' + cust_name + "__" + dataset_name + '__' + "in_field" + "__" + pred_field + "__" + "Vocab.pkl"
                    coef_path = 'models/' + cust_name + "__" + dataset_name + '__' + pred_values[
                        'algoName'] + "__" + pred_field + "__" + "Coef_.pkl"
                    vocab_file = Path(vocab_path)
                    coef_file = Path(coef_path)
                    if (vocab_file.is_file()):
                        vocab = joblib.load(vocab_path)
                    else:
                        logging.info(
                            '%s: Vocabulary file not found for %s field.. please train algo, save the choices & try again.' % (
                            RestService.timestamp(), pred_field))
                        return "failure"

                    if (coef_file.is_file()):
                        weightage = joblib.load(coef_path)
                    else:
                        if (svc_flag == 1):
                            print("SVC")
                            continue
                        else:
                            logging.info(
                                '%s: ML Model file not found for %s field.. please train algo, save the choices & try again.' % (
                                RestService.timestamp(), pred_field))
                            return 'failure'

                    inci_predict = MongoDBPersistence.predicted_tickets_tbl.find_one(
                        {"CustomerID": customer_id, "DatasetID": dataset_id \
                            , ticket_id_field_name: number}, {"predicted_fields": 1, "_id": 0})["predicted_fields"]
                    pred_f = ""
                    for field in inci_predict:
                        if (pred_field in field.keys()):
                            pred_f = field[pred_field]
                    idToLabel = {}
                    labels = \
                    MongoDBPersistence.datasets_tbl.find_one({"CustomerID": customer_id, "DatasetID": dataset_id}, \
                                                                {"IdToLabels": 1, "_id": 0})["IdToLabels"]

                    for key, value in labels.items():
                        if (str(key) == str(pred_field)):
                            idToLabel = value

                    if ("RandomForestClassifier" in str(pred_values['algoName'])):
                        predict_vocab = weightage
                    else:
                        predict_vocab = weightage[
                            int([key for key, value in idToLabel.items() if value == pred_f][0])]

                    weight_dict = {}
                    for i in range(len(list_words)):
                        if (list_words[i] in predict_vocab.keys()):
                            weight_dict[list_words[i]] = predict_vocab[list_words[i]]

                    weighted_list = sorted(weight_dict.items(), key=lambda x: x[1], reverse=True)[:10]
                    weight_final[pred_field] = weighted_list

                except Exception as e:
                    print("error in contributing feild", e)

            print("contribution words", weight_final)
            return json_util.dumps(weight_final)

        except Exception as e:
            # put logger instead of print statement
            print("Error in importantFeaturesReport function", e)
            return 'failure'

    @staticmethod
    def sortAndFilter(cstmr_id, dataset_id, fltr_fld, fltr_val, srt_fld, srt_ordr, page_size, page_num,
                      prev_pred_state, show_app_ticket):
        pred_doc_lst = []
        keys = []
        resp = []
        doc_count = 0
       
        field_mapping = MappingPersistence.get_mapping_details(customer_id=cstmr_id)
        ticket_id_field_name = field_mapping['Ticket_ID_Field_Name']
        description_field_name = field_mapping['Description_Field_Name']
        srt_doc = {ticket_id_field_name: "1"}

        try:
            # --fetching tickets specific for user--
            if (session.get('user')):
                logging.info("%s Catching User Session" % RestService.timestamp())
                user = session['user']
                role = session['role']
                logging.info("%s Session catched user as  %s" % (RestService.timestamp(), user))
                if (role == 'Admin'):
                    match_doc = {'CustomerID': cstmr_id}
                else:
                    user_doc = MongoDBPersistence.users_tbl.find_one({'UserID': user})
                    if (user_doc):
                        team_id = int(user_doc['TeamID'])
                        team_doc = MongoDBPersistence.teams_tbl.find_one({'TeamID': team_id})
                        if (team_doc):
                            dataset_id = team_doc['DatasetID']
                            match_doc = {'CustomerID': cstmr_id, "DatasetID": dataset_id}
                        else:
                            logging.warn('There is no document in Tbl_Teams with team id %s' % str(team_id))
                    else:
                        logging.warn('There is no document in Tbl_Users with user_id %s' % user)
            else:
                logging.info("%s You are not logged in please login" % RestService.timestamp())
                return "No Login Found"
            # ----------------------------------------

            keys = MongoDBPersistence.datasets_tbl.find_one(match_doc, {'_id': 0, 'ColumnNames': 1})['ColumnNames']
            if (str(fltr_fld) != 'undefined'):
                if ('predicted_' in fltr_fld):
                    if (fltr_fld == 'predicted_assignee'):
                        fltr_fld = 'predicted_assigned_to'
                    else:
                        fltr_fld = 'predicted_fields.' + fltr_fld[10:]
                    match_doc[fltr_fld] = {'$regex': fltr_val, '$options': 'i'}
                elif (fltr_fld in keys):
                    match_doc['rtDoc.' + fltr_fld] = {'$regex': fltr_val, '$options': 'i'}
                
                else:
                    match_doc[fltr_fld] = {'$regex': fltr_val, '$options': 'i'}
            
            if (prev_pred_state == 'false'):
                match_doc['user'] = {'$exists': False}

            if (str(srt_fld) != 'undefined'):
                if (srt_fld in keys):
                    srt_doc = {'rtDoc.' + srt_fld: int(srt_ordr)}
                else:
                    srt_doc = {srt_fld: int(srt_ordr)}

            skips = page_size * (page_num - 1)
            upto = page_size * (page_num)

            if(show_app_ticket) == 'false':
                match_doc['user_status'] = 'Not Approved'
            else:
                match_doc['user_status'] = 'Approved'

            logging.info(f"sort and filer match_doc: {match_doc}")

            pred_doc_lst = list(MongoDBPersistence.predicted_tickets_tbl.aggregate([{
                '$lookup': {
                    'from': 'TblIncidentRT',
                    'localField': 'number',
                    'foreignField': 'number',
                    'as': 'rtDoc'
                }}, {'$match': match_doc},
                {'$project': {
                    '_id': 0,
                    'rtDoc._id': 0
                }
                }, {'$sort': srt_doc}]))

            logging.info(f"sort and filer pred_doc_lst: {pred_doc_lst}")

            for pred_doc in pred_doc_lst:
                logging.info(f"sort and filer pred_doc: {pred_doc}")
                if ticket_id_field_name not in pred_doc:
                    pred_doc[ticket_id_field_name] = pred_doc[ticket_id_field_name]
                
                pred_doc.update(pred_doc['rtDoc'][0])
                del pred_doc['rtDoc']

            doc_count = len(pred_doc_lst)
            pred_doc_lst = pred_doc_lst[skips:upto]
            resp.append(pred_doc_lst)
            if (doc_count):
                resp.append(doc_count)
            logging.info(f"sort and filter resp: {resp}")
            return json_util.dumps(resp)
        except Exception as e:
            logging.error('sortAndFilter error: %s' % str(e))

        return json_util.dumps('failure')

    # Fetching the list of users for ITSM
    @staticmethod
    def itsm_users(customer_id, method):
        ()
        logging.info("Inside itsm users list for customer_id %s" % (customer_id))
        mapped_doc = {}
        match_doc = {}
        try:
            if (method == 'get'):
                users = list(MongoDBPersistence.itsm_user_mapping.find({"CustomerID": customer_id}))
                return json_util.dumps(users)
            
            elif (method == 'put' or method == 'post'):
                mapped_doc = request.get_json()
                key = list(mapped_doc.keys())
                match_doc[key[0]] = mapped_doc[key[0]]
                match_doc[key[1]] = mapped_doc[key[1]]
                match_doc[key[2]] = mapped_doc[key[2]]

                users = MongoDBPersistence.itsm_user_mapping.update_one(match_doc, {'$set': mapped_doc}, upsert=True)
            elif (method == 'delete'):
                mapped_doc = request.get_json()
                users = MongoDBPersistence.itsm_user_mapping.delete_one(mapped_doc)
            else:
                logging.info('passed an invalid method')
                return 'failure'
            return 'success'
        except Exception as e:
            logging.error("Error while fetching data for user from database %s" % (str(e)))
            return "failure"

    ##assuming that the assignee mapping is already present
    @staticmethod
    def tickets_assigned_to_user(customer_id, dataset_id, page_size, page_num, show_app_ticket):
        try:
            field_mapping = MappingPersistence.get_mapping_details(customer_id)
            ticket_id_field_name = field_mapping['Ticket_ID_Field_Name']
            if (session.get('user')):
                logging.info("%s Catching User Session" % RestService.timestamp())
                user = session['user']
                logging.info("%s Session catched user as  %s" % (RestService.timestamp(), user))
            else:
                logging.info("%s You are not logged in please login" % RestService.timestamp())
                return "No Login Found"

            logging.info("Inside tickets assigned to user method with assignee %s" % (user))

            #            itsm_user = MongoDBPersistence.itsm_user_mapping.find_one({"CustomerID":customer_id,"user":user},{"mapped_user":1,"_id":0})["mapped_user"]
            skips = page_size * (page_num - 1)

            if (user == "admin"):
                logging.info("Logging as Admin , hence showing all the records")
                if(show_app_ticket == 'false'):
                    all_data = list(MongoDBPersistence.predicted_tickets_tbl.find(
                    {"CustomerID": customer_id, "DatasetID": dataset_id, "state": {"$in": ["New", "InProgress"]}}).skip(
                    skips).limit(page_size))
                else:
                    all_data = list(MongoDBPersistence.predicted_tickets_tbl.find(
                    {"CustomerID": customer_id, "DatasetID": dataset_id, "user_status":{"$in":["Approved"]}, "state": {"$in": ["New", "InProgress"]}}).skip(
                    skips).limit(page_size))
                incident_numbers_to_map = []
                prediction_to_show = all_data
                for data in all_data:
                    incident_numbers_to_map.append(data[ticket_id_field_name])
                if (all_data):
                    logging.info('%s: Getting real time tickets.' % RestService.timestamp())
                    incidents_to_map = list(MongoDBPersistence.rt_tickets_tbl.find(
                        {ticket_id_field_name: {"$in": incident_numbers_to_map}}))

                    for index, incident in enumerate(prediction_to_show):

                        for key in incident.keys():
                            if key in incidents_to_map[index].keys():
                                continue
                            else:
                                incidents_to_map[index][key] = incident[key]
                    prediction_to_show = incidents_to_map
                    resp = json_util.dumps(prediction_to_show)
                else:
                    logging.info('%s: Failed to get real time tickets.' % RestService.timestamp())
                    resp = 'failure'

            else:
                user = MongoDBPersistence.users_tbl.find_one({"UserID": user}, {"UserName": 1, "_id": 0})['UserName']
                itsm_user = MongoDBPersistence.itsm_user_mapping.find_one({"CustomerID": customer_id, "user": user},
                                                                          {"mapped_user": 1, "_id": 0})
                logging.info(f"itsm_user: {itsm_user}")
                itsm_user = MongoDBPersistence.itsm_user_mapping.find_one({"CustomerID": customer_id, "user": user},
                                                                          {"mapped_user": 1, "_id": 0})["mapped_user"]
                logging.info(f"itsm_user: {itsm_user}")
                if (show_app_ticket == 'false'):
                    user_data = list(MongoDBPersistence.predicted_tickets_tbl.find(
                    {"CustomerID": customer_id, "DatasetID": dataset_id, "predicted_assigned_to": itsm_user,
                     "state": {"$in": ["New", "InProgress"]}}, {"_id": 0}).skip(skips).limit(page_size))
                else:
                    user_data = list(MongoDBPersistence.predicted_tickets_tbl.find(
                    {"CustomerID": customer_id, "DatasetID": dataset_id, "predicted_assigned_to": itsm_user, "user_status":{"$in":["Approved"]},
                     "state": {"$in": ["New", "InProgress"]}}, {"_id": 0}).skip(skips).limit(page_size))

                logging.info(f"user_data: {user_data}")
                incident_numbers_to_map = []
                prediction_to_show = user_data
                logging.info(f"prediction_to_show: {prediction_to_show}")
                for data in user_data:
                    incident_numbers_to_map.append(data[ticket_id_field_name])
                if (user_data):
                    logging.info('%s: Getting real time tickets for diffrent user.' % RestService.timestamp())
                    incidents_to_map = list(MongoDBPersistence.rt_tickets_tbl.find(
                        {ticket_id_field_name: {"$in": incident_numbers_to_map}}))
                    logging.info(f"incidents_to_map: {incidents_to_map}")
                    for index, incident in enumerate(prediction_to_show):

                        for key in incident.keys():
                            if key in incidents_to_map[index].keys():
                                continue
                            else:
                                incidents_to_map[index][key] = incident[key]
                    prediction_to_show = incidents_to_map
                    logging.info(f"prediction_to_show: {prediction_to_show}")
                    resp = json_util.dumps(prediction_to_show)
                else:
                    logging.info('%s: Failed to get real time tickets.' % RestService.timestamp())
                    resp = 'failure'

            return resp
        except Exception as e:
            logging.error("Error while fetching data for assigned_to user %s" % (str(e)))
            logging.error(e, exc_info=True)
            return "Failure"
