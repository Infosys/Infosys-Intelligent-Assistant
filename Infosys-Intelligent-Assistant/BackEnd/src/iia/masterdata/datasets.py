__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

from iia.persistence.mongodbpersistence import MongoDBPersistence
from iia.persistence.mappingpersistence import MappingPersistence
from iia.restservice import RestService
from flask import request
from bson import json_util
import os
import joblib
import json
import pandas as pd
from flask import session
from iia.utils.config_helper import get_config
import numpy as np
import configparser
from iia.utils.log_helper import get_logger, log_setup
from datetime import datetime

logging = get_logger(__name__)
app = RestService.getApp()

@app.route("/api/updateRetrainPreference/<int:customer_id>/<int:dataset_id>/<status>", methods=["PUT"])
def updateRetrainPreference(customer_id, dataset_id, status):
    return DatasetMasterData.updateRetrainPreference(customer_id, dataset_id, status)


@app.route('/api/allValues/<int:customer_id>/<int:dataset_id>/<predicted_field>', methods=["GET"])
def allValues(customer_id, dataset_id, predicted_field):
    return DatasetMasterData.allValues(customer_id, dataset_id, predicted_field)


@app.route('/api/priorityList/<int:customer_id>/<int:dataset_id>', methods=["GET"])
def priorityList(customer_id, dataset_id):
    return DatasetMasterData.priorityList(customer_id, dataset_id)


@app.route('/api/allDatasetNames/<int:customer_id>', methods=["GET"])
def allDatasetNames(customer_id):
    return DatasetMasterData.allDatasetNames(customer_id)


@app.route("/api/saveFieldSelections/<int:customer_id>/<int:dataset_id>", methods=["PUT"])
def saveFieldSelections(customer_id, dataset_id):
    return DatasetMasterData.saveFieldSelections(customer_id, dataset_id)


@app.route("/api/updateUserPreference/<int:customer_id>/<int:dataset_id>/<status>", methods=["PUT"])
def updateUserPreference(customer_id, dataset_id, status):
    return DatasetMasterData.updateUserPreference(customer_id, dataset_id, status)


@app.route('/api/getDatasetID/<int:customer_id>/<int:team_id>', methods=["GET"])
def getDatasetID(customer_id, team_id):
    return DatasetMasterData.getDatasetID(customer_id, team_id)


@app.route('/api/getDatasetDetails/<int:customer_id>/<int:dataset_id>', methods=["GET"])
def getDatasetDetails(customer_id, dataset_id):
    return DatasetMasterData.getDatasetDetails(customer_id, dataset_id)


@app.route('/api/deleteDataset/<int:customer_id>/<int:dataset_id>', methods=["DELETE"])
def deleteDataset(customer_id, dataset_id):
    try:
        environment = os.environ['build_environment']
    except:
        environment = 'prod'
    if str(environment).lower() == 'demo':
        return "success"

    return DatasetMasterData.deleteDataset(customer_id, dataset_id)


@app.route('/api/getTagsDatasetDetails/<int:customer_id>/<int:dataset_id>', methods=["GET"])
def getTagsDatasetDetails(customer_id, dataset_id):
    return DatasetMasterData.getTagsDatasetDetails(customer_id, dataset_id)


@app.route('/api/getTagDatasetID/<int:customer_id>/<int:team_id>', methods=["GET"])
def getTagDatasetID(customer_id, team_id):
    return DatasetMasterData.getTagDatasetID(customer_id, team_id)


@app.route('/api/deleteTagDataset/<int:customer_id>/<int:dataset_id>', methods=["DELETE"])
def deleteTagDataset(customer_id, dataset_id):
    return DatasetMasterData.deleteTagDataset(customer_id, dataset_id)


@app.route('/api/getTrainedTicketsCount')
def getTrainedTicketsCount():
    return DatasetMasterData.getTrainedTicketsCount()


class DatasetMasterData(object):
    '''
    classdocs
    '''

    def __init__(self, params):
        '''
        Constructor
        '''

    @staticmethod
    def guessDataset(tickets, customer_id):
        ################# if unique field is not configured in .ini file #########
        logging.info("Inside Guess Dataset ")
        unique_field_flag = False
        default_dataset_id = 0
        config = configparser.ConfigParser()
        config["DEFAULT"]['path'] = "config/"
        config.read(config["DEFAULT"]["path"] + "iia.ini")
        try:
            uniqueFlag = str(config["Fields"]["uniqueFieldFlag"])
            if (uniqueFlag.lower() == "no"):
                datasets = list(MongoDBPersistence.datasets_tbl.find({}, {'_id': 0, "DatasetID": 1, "ColumnNames": 1}))
                logging.info(f"datasets: {datasets}")
                for dataset in datasets:
                    if all(item in list(tickets[0].keys()) for item in dataset['ColumnNames']):
                        default_dataset_id = dataset['DatasetID']
                logging.info("Default dataset value is %s" % (default_dataset_id))
                unique_field_flag = True
        except Exception as e:
            logging.error("Taking default Unique key settings .%s" % (str(e)))

        field_mapping = MappingPersistence.get_mapping_details(customer_id)
        ticket_id_field_name = field_mapping['Ticket_ID_Field_Name']
        status_field_name = field_mapping['Status_Field_Name']

        garbage_tickets = []
        if (session.get('user')):
            logging.info("%s Catching User Session" % RestService.timestamp())
            user = session['user']
            logging.info("%s Session catched user as  %s" % (RestService.timestamp(), user))
        else:
            logging.info("%s You are not logged in please login" % RestService.timestamp())
            return "No Login Found"

        login_user = MongoDBPersistence.users_tbl.find_one({"UserID": user}, {"_id": 0})
        if (login_user):
            accessible_datasets = DatasetMasterData.guess_dataset_access(user)
            logging.info(f"accessible_datasets: {accessible_datasets}")
            datasets = list(MongoDBPersistence.datasets_tbl.find({"DatasetID": {"$in": accessible_datasets}}))
            logging.info(f"datasets: {datasets}")
            for ticket in tickets:
                dataset_id = 0 
                if (unique_field_flag):
                    logging.info(
                        "Unique field is not required , Going for default dataset id %s" % (default_dataset_id))
                    dataset_id = default_dataset_id
                else:
                    for dataset in datasets:
                        fields = dataset['UniqueFields']
                        match_flag = 0
                        for field in fields:
                            try:
                                dataset_values = MongoDBPersistence.training_tickets_tbl.find(
                                    {"CustomerID": customer_id, "DatasetID": dataset["DatasetID"]}).distinct(
                                    field['FieldName']) 
                                logging.info('%s: distinct values of %s are %s' % (
                                    RestService.timestamp(), field['FieldName'], dataset_values))
                            except Exception as e:
                                logging.error('%s: Error: %s' % (RestService.timestamp(), str(e)))
                                logging.info(
                                    '%s: Column name %s not found.' % (RestService.timestamp(), field['FieldName']))
                                break
                            logging.info(f"field['FieldName']:{field['FieldName']}")
                            logging.info(f"ticket.keys():{ticket.keys()}")
                            if (field['FieldName'] in ticket.keys()):
                                logging.info('%s: real time ticket with number %s %s value is %s' % (
                                    RestService.timestamp(), ticket[ticket_id_field_name], field['FieldName'],
                                    ticket[field['FieldName']]))
                                if (ticket[field['FieldName']] in set(dataset_values)):
                                    match_flag = match_flag + 1
                        if (match_flag == len(fields)):
                            dataset_id = dataset['DatasetID']
                            # Write insert logic: into tableRT
                            break
                # Insert into database
                if (dataset_id == 0):
                    logging.info('%s: the ticket (Incident Number: %s) do not match with any of the datasets.' % (
                        RestService.timestamp(), ticket[ticket_id_field_name]))
                    garbage_tickets.append(ticket[ticket_id_field_name])
                    continue
                workload = 0.0
                tickets_assigned = 0
                ticket.update({"DatasetID": dataset_id})
                ticket.update({status_field_name: 'New'})
                ticket.update({"user_status": 'Not Approved'})
                ticket.update({"CustomerID": customer_id})
                ticket.update({"workload": workload})
                ticket.update({"tickets_assigned": tickets_assigned})
                ticket.update({"related_tic_flag": False})
                dataset_info_dict = MongoDBPersistence.datasets_tbl.find_one(
                    {'CustomerID': customer_id, "DatasetID": dataset_id}, {'FieldSelections': 1, '_id': 0})
                if (dataset_info_dict):
                    fieldselection_list = dataset_info_dict['FieldSelections']
                else:
                    logging.info(
                        '%s: For a given customer, FieldSelections not found in the record. Please train the models with appropriate dataset to predict your ticket fields.' % RestService.timestamp())
                    return "failure"

                # Pick up Approved customer choices
                for pred_fields in fieldselection_list:
                    if (pred_fields['FieldsStatus'] == 'Approved'):
                        pred_fields_choices_list = pred_fields['PredictedFields']
                        break
                pred_field_list = []
                for pre_field in pred_fields_choices_list:
                    pred_field_list.append(pre_field['PredictedFieldName'])

                for pred_field in pred_field_list:
                    input_field_list = []
                    for input_field in pred_fields_choices_list:
                        if (input_field['PredictedFieldName'] == pred_field):
                            input_field_list = input_field['InputFields']
                            break
                    if (set(input_field_list) == set(set(input_field_list) & set(ticket.keys()))):
                        logging.info('%s: All required input customer choices for %s are there with csv data.' % (
                            RestService.timestamp(), pred_field))
                        continue
                    else:
                        logging.error('%s: Incomplete input data in the ticket for a prediction field %s' % (
                            RestService.timestamp(), pred_field))
                try:
                    logging.info('%s: Trying to insert tickets into TblIncidentRT...' % RestService.timestamp())
                    MongoDBPersistence.rt_tickets_tbl.update_one({ticket_id_field_name: ticket[ticket_id_field_name]},
                                                                 {'$set': ticket}, upsert=True)
                except Exception as e:
                    logging.error('%s: Error occurred: %s ' % (RestService.timestamp(), str(e)))
            return garbage_tickets
        else:
            logging.info("%s User is not authenticated" % RestService.timestamp())
            return "failure"

    @staticmethod
    def guess_dataset_access(user_id):
        '''
        This method takes user_id as input and return a list of dataset the user has access to
        '''
        user_details = MongoDBPersistence.users_tbl.find_one({"UserID": user_id}, {"_id": 0, "Role": 1, "TeamID": 1})
        if (user_details['Role'] == 'Admin'):
            accessible_datasets = MongoDBPersistence.datasets_tbl.find().distinct('DatasetID')
        else:
            team_id = user_details['TeamID']
            dataset_id = MongoDBPersistence.teams_tbl.find_one({"TeamID": team_id}, {"_id": 0, "DatasetID": 1})
            accessible_datasets = [dataset_id['DatasetID']]

        return accessible_datasets

    @staticmethod
    def priorityList(customer_id, dataset_id):
        priority_List = list(
            MongoDBPersistence.training_tickets_tbl.find({"CustomerID": customer_id, "DatasetID": dataset_id}).distinct(
                'priority'))
        if (priority_List):
            # Return array of distinct values
            return json.dumps(priority_List)
        else:
            logging.info('%s: training data not found for %s.' % (RestService.timestamp(), 'priority'))
            return 'failure'

    @staticmethod
    def allValues(customer_id, dataset_id, predicted_field):
        all_values = list(
            MongoDBPersistence.training_tickets_tbl.find({"CustomerID": customer_id, "DatasetID": dataset_id}).distinct(
                predicted_field))
        if (all_values):
            # Return array of distinct values
            return json.dumps(all_values)
        else:
            logging.info('%s: training data not found for %s.' % (RestService.timestamp(), predicted_field))
            return 'failure'

    @staticmethod
    def allDatasetNames(customer_id):
        all_datasetNames = list(
            MongoDBPersistence.datasets_tbl.find({"CustomerID": customer_id}).distinct('DatasetName'))
        if (all_datasetNames):
            # Return array of distinct values
            return json.dumps(all_datasetNames)
        else:
            logging.info('%s: training datasets not found.' % (RestService.timestamp()))
            return 'failure'

    @staticmethod
    def saveFieldSelections(customer_id, dataset_id):
        index_count = 0
        data = request.get_json()

        logging.info(f"data: {data}")
        o_fieldselection_doc = MongoDBPersistence.datasets_tbl.find_one(
            {'CustomerID': customer_id, "DatasetID": dataset_id},
            {'FieldSelections': 1, '_id': 0, 'DependedPredict': 1})
        if (o_fieldselection_doc):
            o_fieldselection_list = o_fieldselection_doc['FieldSelections']
            o_depended_list = o_fieldselection_doc['DependedPredict']
            n_fieldselection_list = o_fieldselection_list
            for fieldselection_dict in o_fieldselection_list:
                if (fieldselection_dict['FieldsStatus'] == 'Approved') or (
                        fieldselection_dict['FieldsStatus'] == 'InProgress'):
                    n_fieldselection_list.remove(fieldselection_dict)
                    o_depended_list.remove(o_depended_list[index_count])
                index_count += 1
            n_fieldselection_dict = {"FieldsStatus": 'Approved'}
            n_fieldselection_dict["PredictedFields"] = data["FieldSelections"]
            n_fieldselection_list.append(n_fieldselection_dict)
            # -- using predict field as input field --
            DependedPredict = {}
            if len(data['DependedPredict']) > 0:
                DependedPredict['flag'] = 'true'
            else:
                DependedPredict['flag'] = 'false'
            DependedPredict['values'] = data['DependedPredict']
            o_depended_list.append(DependedPredict)
        else:
            n_fieldselection_list = []
            o_depended_list = []
            DependedPredict = {}

            n_fieldselection_dict = {"FieldsStatus": 'InProgress'}
            n_fieldselection_dict["PredictedFields"] = data["FieldSelections"]
            n_fieldselection_list.append(n_fieldselection_dict)

            if len(data['DependedPredict']) > 0:
                DependedPredict['flag'] = 'true'
            else:
                DependedPredict['flag'] = 'false'
            DependedPredict['values'] = data['DependedPredict']
            o_depended_list.append(DependedPredict)
        try:
            MongoDBPersistence.datasets_tbl.update_one({'CustomerID': customer_id, "DatasetID": dataset_id}, {
                "$set": {"FieldSelections": n_fieldselection_list, "DependedPredict": o_depended_list}}, upsert=True)
            # First time when user uploading dataset, He will have to select UniqueFields that identify him
            if (data["UniqueFields"]):
                MongoDBPersistence.datasets_tbl.update_one({'CustomerID': customer_id, "DatasetID": dataset_id},
                                                           {"$set": {"UniqueFields": data["UniqueFields"]}},
                                                           upsert=False)
            logging.info('%s: FieldSelections have been saved successfully into TblDataset' % RestService.timestamp())
            ######## DATA BELOW THRESHOLD LOGIC ##############
            data_balance = pd.DataFrame(list(
                MongoDBPersistence.training_tickets_tbl.find({'CustomerID': customer_id, "DatasetID": dataset_id},
                                                             {"_id": 0})))
            output_data = MongoDBPersistence.datasets_tbl.find_one({'CustomerID': customer_id, "DatasetID": dataset_id},
                                                                   {'FieldSelections': 1, '_id': 0})
            output = output_data['FieldSelections'][0]['PredictedFields'][0]['PredictedFieldName']
            df_table = data_balance[[output]]
            df_table['count'] = df_table.groupby(output)[output].transform('count')
            df_table = df_table.groupby(output).count().reset_index()

            Q1 = np.percentile(df_table['count'], 10, interpolation='midpoint')
            Q1 = Q1.astype(int)
            data_below_threshold = data_balance[output].value_counts().to_frame()
            data_below_threshold_list = data_below_threshold[data_below_threshold[output] <= Q1].index.to_list()
            if (data_below_threshold_list):
                if len(data_below_threshold_list) < 5:
                    resp = {'Status': 'success', 'Classes having less number of tickets': data_below_threshold_list,
                            'Warning': True,
                            'Message': 'The above mentioned classes do not have required minimum tickets for Training. Please add more tickets for corresponding classes'}
                elif len(data_below_threshold_list) > 5:
                    resp = {'Status': 'success', 'Warning': True,
                            'Classes having less number of tickets': data_below_threshold_list[0:5],
                            'Message': 'Many classes do not have required minimum tickets for Training. Please add more tickets for corresponding classes.\n Refer EDA advanced report for more details'}
            else:
                resp = {'Status': 'success', 'Warning': True}
            print(resp)
        except Exception as e:
            logging.error('%s: Error occurred: %s ' % (RestService.timestamp(), str(e)))
            logging.error(e, exc_info=True)
            resp = 'failure'
        return json_util.dumps(resp)

    @staticmethod
    def updateRetrainPreference(customer_id, dataset_id, status):  # status = Approved/Discarded
        data = request.get_json()
        o_fieldselection_list = MongoDBPersistence.datasets_tbl.find_one(
            {'CustomerID': customer_id, "DatasetID": dataset_id}, {'DatasetName': 1, 'FieldSelections': 1, '_id': 0})
        customer_name = MongoDBPersistence.customer_tbl.find_one({'CustomerID': customer_id},
                                                                 {'CustomerName': 1, '_id': 0})
        customer_name = customer_name['CustomerName']
        if (o_fieldselection_list):
            dataset_name = o_fieldselection_list['DatasetName']
            if (status == "Approved"):
                FieldSelections = []
                FieldSelections_dict = {}
                FieldSelections_dict['FieldsStatus'] = "Approved"
                o_fieldselection_list = o_fieldselection_list['FieldSelections']

                for fieldselection_dict in o_fieldselection_list:
                    if (fieldselection_dict['FieldsStatus'] == 'Approved'):
                        updated_selections = []
                        for o_choice in fieldselection_dict["PredictedFields"]:
                            for n_choice in data:
                                tmpdict = {}
                                if (o_choice['PredictedFieldName'] == n_choice['PredictedFieldName']):
                                    tmpdict = o_choice
                                    tmpdict['AlgorithmName'] = n_choice['AlgorithmName']
                                if (tmpdict):
                                    updated_selections.append(tmpdict)
                                    break
                        FieldSelections_dict['PredictedFields'] = updated_selections
                    elif (fieldselection_dict['FieldsStatus'] == 'InProgress'):
                        FieldSelections.append(fieldselection_dict)

                FieldSelections.append(FieldSelections_dict)
                for filename in os.listdir("models"):
                    file_list = filename.split('__')
                    if (customer_name in file_list):
                        if (dataset_name in file_list):
                            if ('Approved' in filename.split('__')):
                                # Remove
                                os.remove("models/" + filename)

                for filename in os.listdir("data"):
                    file_list = filename.split('__')
                    if (customer_name in file_list):
                        if (dataset_name in file_list):
                            if ('Approved' in filename.split('__')):
                                # remove previous accepted
                                os.remove("data/" + filename)
                    # Make existing "Approved"
                for filename in os.listdir("models"):
                    file_list = filename.split('__')
                    if (customer_name in file_list):
                        if (dataset_name in file_list):
                            if ('Retraining' in filename.split('__')):
                                n_filename = filename.replace("Retraining", "Approved")

                                os.rename("models/" + filename, "models/" + n_filename)
                for filename in os.listdir("data"):
                    file_list = filename.split('__')
                    if (customer_name in file_list):
                        if (dataset_name in file_list):
                            if ('Retraining' in filename.split('__')):
                                n_filename = filename.replace("Retraining", "Approved")
                                os.rename("data/" + filename, "data/" + n_filename)
                logging.info(
                    '%s: moved previous "Approved" to "Archived" pkls & amking current Retraining as Approved.' % RestService.timestamp())

            elif (status == "Discarded"):
                # As training status remains Retraining, it will get deleted next time...no need of this step.. previous Inprogress pickle files get removed before train
                # remove pkl files with Retraining status
                for filename in os.listdir("models"):
                    file_list = filename.split('__')
                    if (customer_name in file_list):
                        if (dataset_name in file_list):
                            if ("Retraining" in file_list):
                                os.remove("models/" + filename)
                for filename in os.listdir("data"):
                    file_list = filename.split('__')
                    if (customer_name in file_list):
                        if (dataset_name in file_list):
                            if ("Retraining" in file_list):
                                os.remove("data/" + filename)
                logging.info(
                    '%s: Pickle files for current selections deleted successfully.. Also updated the TblTraining.' % RestService.timestamp())
                return 'success'

        else:
            logging.info('%s: No user selections found in TblCustomer.' % RestService.timestamp())
            return 'failure'

        # Update Training status
        # Recieving last training ID to update TblTraining
        last_training_dict = MongoDBPersistence.training_hist_tbl.find_one(
            {"CustomerID": customer_id, "DatasetID": dataset_id, \
             "TrainingStatus": "Retraining", "TrainingID": {"$exists": True}}, {'_id': 0, "TrainingID": 1},
            sort=[("TrainingID", -1)])
        if (last_training_dict):
            last_training_id = last_training_dict['TrainingID']
        else:
            # It should be non-Registered Customer
            logging.info(
                '%s: Failure: Last InProgress training info not found for the customer.' % RestService.timestamp())
            return json_util.dumps("failure")
        # Update both the statuses in TblCustomer & TblTraining
        try:
            logging.info('%s: Updating TblCustomer & TblTraining for the selected choices.' % RestService.timestamp())

            MongoDBPersistence.datasets_tbl.update_one({'CustomerID': customer_id, "DatasetID": dataset_id}, \
                                                       {"$set": {"FieldSelections": FieldSelections}}, upsert=False)

            logging.info('%s: Updated: TblDataset' % RestService.timestamp())

            MongoDBPersistence.training_hist_tbl.update_one({'CustomerID': customer_id, "DatasetID": dataset_id, \
                                                             "TrainingStatus": "Approved"},
                                                            {"$set": {"TrainingStatus": "Archived"}}, upsert=False)

            MongoDBPersistence.training_hist_tbl.update_one({'CustomerID': customer_id, "TrainingID": last_training_id, \
                                                             "DatasetID": dataset_id},
                                                            {"$set": {"TrainingStatus": status}}, upsert=False)
            algo_name = data[0]['AlgorithmName']
            print("algo_name:", algo_name)
            best_algo_score = MongoDBPersistence.training_hist_tbl.find_one(
                {"CustomerID": customer_id, "DatasetID": dataset_id, "TrainingStatus": status},
                {'PredictedFields': 1, "AlgorithmParameters": 1, '_id': 0})
            score_params = best_algo_score
            print("best_algo_score:", best_algo_score)
            print("score_params:", score_params)
            update_dict = {}
            for i in score_params['PredictedFields'][0]['Algorithms']:
                if i['AlgorithmName'] == algo_name:
                    update_dict['AlgorithmName'] = i['AlgorithmName']
                    update_dict['F1_score_train'] = ''
                    update_dict['F1_score_test'] = i['F1_score']

            for i in score_params['AlgorithmParameters']:
                if i['AlgorithmName'] == algo_name:
                    update_dict['Parameters'] = i['Parameters']

            print("update_dict: ", update_dict)
            MongoDBPersistence.datasets_tbl.update_one({'CustomerID': customer_id, "DatasetID": dataset_id},
                                                       {"$set": {"BestAlgoParams": update_dict}}, upsert=True)

            logging.info('%s: Updated: TblTraining' % RestService.timestamp())
            resp = 'success'
        except Exception as e:
            logging.error('%s: Error occurred: %s ' % (RestService.timestamp(), str(e)))
            resp = 'failure'
        return resp

    @staticmethod
    def updateUserPreference(customer_id, dataset_id, status):  # status = Approved/Discarded
        data = request.get_json()
        index_count = 0
        prev_inprogress_flg = 0
        o_fieldselection_list = MongoDBPersistence.datasets_tbl.find_one(
            {'CustomerID': customer_id, "DatasetID": dataset_id},
            {'DatasetName': 1, 'FieldSelections': 1, 'DependedPredict': 1, '_id': 0})
        customer_name = MongoDBPersistence.customer_tbl.find_one({'CustomerID': customer_id},
                                                                 {'CustomerName': 1, '_id': 0})
        customer_name = customer_name['CustomerName']
        if (o_fieldselection_list):
            o_depended_list = o_fieldselection_list['DependedPredict']
            dataset_name = o_fieldselection_list['DatasetName']
            if (status == "Approved"):
                FieldSelections = []
                FieldSelections_dict = {}
                FieldSelections_dict['FieldsStatus'] = "Approved"
                o_fieldselection_list = o_fieldselection_list['FieldSelections']

                for fieldselection_dict in o_fieldselection_list:
                    if (fieldselection_dict['FieldsStatus'] == 'InProgress' or fieldselection_dict[
                        'FieldsStatus'] == 'Approved'):

                        prev_inprogress_flg = 1
                        updated_selections = []
                        for o_choice in fieldselection_dict["PredictedFields"]:
                            for n_choice in data:
                                tmpdict = {}
                                if (o_choice['PredictedFieldName'] == n_choice['PredictedFieldName']):
                                    tmpdict = o_choice
                                    tmpdict['AlgorithmName'] = n_choice['AlgorithmName']
                                if (tmpdict):
                                    updated_selections.append(tmpdict)
                                    break
                        FieldSelections_dict['PredictedFields'] = updated_selections
                        if len(o_depended_list) > 1: o_depended_list.pop(index_count)
                        break

                if (prev_inprogress_flg == 1):
                    FieldSelections.append(FieldSelections_dict)
                    # move previous "Approved" to "Archived" pkls
                    for filename in os.listdir("models"):
                        file_list = filename.split('__')
                        if (customer_name in file_list):
                            if (dataset_name in file_list):
                                if ('Approved' in filename.split('__')):
                                    # Remove
                                    os.remove("models/" + filename)
                    for filename in os.listdir("data"):
                        file_list = filename.split('__')
                        if (customer_name in file_list):
                            if (dataset_name in file_list):
                                if ('Approved' in filename.split('__')):
                                    # remove previous accepted
                                    os.remove("data/" + filename)
                    # Make existing "Approved"
                    for filename in os.listdir("models"):
                        file_list = filename.split('__')
                        if (customer_name in file_list):
                            if (dataset_name in file_list):
                                if ('InProgress' in filename.split('__')):
                                    n_filename = filename.replace("InProgress", "Approved")
                                    os.rename("models/" + filename, "models/" + n_filename)
                    for filename in os.listdir("data"):
                        file_list = filename.split('__')
                        if (customer_name in file_list):
                            if (dataset_name in file_list):
                                if ('InProgress' in filename.split('__')):
                                    n_filename = filename.replace("InProgress", "Approved")
                                    os.rename("data/" + filename, "data/" + n_filename)
                    logging.info(
                        '%s: moved previous "Approved" to "Archived" pkls & amking current InProgress as Approved.' % RestService.timestamp())
                else:
                    logging.info('%s: Selected choices have been saved successfully.' % RestService.timestamp())
                    logging.info(
                        '%s: Updating TblCustomer & TblTraining for the selected choices.' % RestService.timestamp())
                    MongoDBPersistence.datasets_tbl.update_one({'CustomerID': customer_id, "DatasetID": dataset_id},
                                                               {"$set": {"FieldSelections": FieldSelections}},
                                                               upsert=False)
                    logging.info('%s: Updated: TblDataset' % RestService.timestamp())
                    return 'success'
            elif (status == "Discarded"):
                # As training status remains InProgress, it will get deleted next time...no need of this step.. previous Inprogress pickle files get removed before train
                # remove pkl files with InProgress status
                for filename in os.listdir("models"):
                    file_list = filename.split('__')
                    if (customer_name in file_list):
                        if (dataset_name in file_list):
                            if ("InProgress" in file_list):
                                os.remove("models/" + filename)
                for filename in os.listdir("data"):
                    file_list = filename.split('__')
                    if (customer_name in file_list):
                        if (dataset_name in file_list):
                            if ("InProgress" in file_list):
                                os.remove("data/" + filename)
                logging.info(
                    '%s: Pickle files for current selections deleted successfully.. Also updated the TblTraining.' % RestService.timestamp())
                return 'success'

        else:
            logging.info('%s: No user selections found in TblCustomer.' % RestService.timestamp())
            return 'failure'

        # Update Training status
        # Recieving last training ID to update TblTraining
        last_training_dict = MongoDBPersistence.training_hist_tbl.find_one(
            {"CustomerID": customer_id, "DatasetID": dataset_id, "TrainingStatus": "InProgress",
             "TrainingID": {"$exists": True}}, {'_id': 0, "TrainingID": 1}, sort=[("TrainingID", -1)])
        if (last_training_dict):
            last_training_id = last_training_dict['TrainingID']
        else:
            # It should be non-Registered Customer
            logging.info(
                '%s: Failure: Last InProgress training info not found for the customer.' % RestService.timestamp())
            return json_util.dumps("failure")
        # Update both the statuses in TblCustomer & TblTraining
        try:
            logging.info('%s: Updating TblCustomer & TblTraining for the selected choices.' % RestService.timestamp())
            MongoDBPersistence.datasets_tbl.update_one({'CustomerID': customer_id, "DatasetID": dataset_id}, {
                "$set": {"FieldSelections": FieldSelections, 'DependedPredict': o_depended_list}}, upsert=False)
            logging.info('%s: Updated: TblDataset' % RestService.timestamp())
            MongoDBPersistence.training_hist_tbl.update_one(
                {'CustomerID': customer_id, "DatasetID": dataset_id, "TrainingStatus": "Approved"},
                {"$set": {"TrainingStatus": "Archived"}}, upsert=False)
            MongoDBPersistence.training_hist_tbl.update_one(
                {'CustomerID': customer_id, "TrainingID": last_training_id, "DatasetID": dataset_id},
                {"$set": {"TrainingStatus": status}}, upsert=False)
            logging.info('%s: Updated: TblTraining' % RestService.timestamp())
            resp = 'success'
        except Exception as e:
            logging.error('%s: Error occurred: %s ' % (RestService.timestamp(), str(e)))
            resp = 'failure'
        return json_util.dumps(resp)

    @staticmethod
    def getDatasetID(customer_id, team_id):
        dataset_ = MongoDBPersistence.teams_tbl.find_one({"CustomerID": customer_id, "TeamID": team_id},
                                                         {"DatasetID": 1, "_id": 0})
        if (dataset_):
            logging.info('%s: Getting dataset details.' % RestService.timestamp())
            dataset_id = dataset_["DatasetID"]
        else:
            logging.info('%s: Dataset not found for the team.' % RestService.timestamp())
            dataset_id = -1
        return json_util.dumps(dataset_id)

    @staticmethod
    def getDatasetDetails(customer_id, dataset_id):
        # getting value from config file
        config = configparser.ConfigParser()
        config["DEFAULT"]['path'] = "config/"
        config.read(config["DEFAULT"]["path"] + "iia.ini")
        try:
            comment_field = str(config["Fields"]["commentField"])
            priority_field = str(config["Fields"]["priorityField"])
        except Exception as e:
            comment_field = ""
            priority_field = ""
            logging.error("Taking default predict Configurations %s" % (str(e)))
        # customer_tbl is a pymongo object to TblCustomer
        train_dict = {}
        dataset_dict = MongoDBPersistence.datasets_tbl.find_one({"CustomerID": customer_id, "DatasetID": dataset_id},
                                                                {"DatasetName": 1, "ColumnNames": 1, "TicketCount": 1,
                                                                 "training_mode": 1, "_id": 0})
        logging.debug(f"dataset_dict: {dataset_dict}")
        field_mapping = MappingPersistence.get_mapping_details(customer_id)
        ticket_id_field_name = field_mapping['Ticket_ID_Field_Name']
        description_field_name = field_mapping['Description_Field_Name']
        if (dataset_dict):
            if 'number' not in dataset_dict['ColumnNames']:
                dataset_dict['ColumnNames'].append('number')

            train_dict['name'] = dataset_dict["DatasetName"]
            train_dict['fields'] = dataset_dict['ColumnNames']
            train_dict['count'] = dataset_dict['TicketCount']
            try:
                train_dict['training_mode'] = dataset_dict['training_mode']
            except:
                train_dict['training_mode'] = 'IIA'

            train_dict['comment_field'] = comment_field
            train_dict['priority_field'] = priority_field
            train_dict['ticket_id_field_name'] = ticket_id_field_name
            train_dict['description_field_name'] = description_field_name
            logging.info(f"dataset_dict: {dataset_dict}")
        else:
            logging.info('%s: Dataset details not found for the team.' % RestService.timestamp())

        return json_util.dumps(train_dict)

    @staticmethod
    def deleteDataset(customer_id, dataset_id):
        # Delete both TblIncidentTraining
        try:
            customer_name = \
                MongoDBPersistence.customer_tbl.find_one({'CustomerID': customer_id}, {'CustomerName': 1, '_id': 0})[
                    'CustomerName']
            dataset_name = \
                MongoDBPersistence.datasets_tbl.find_one({'CustomerID': customer_id, "DatasetID": dataset_id},
                                                         {'DatasetName': 1, '_id': 0})['DatasetName']
            MongoDBPersistence.datasets_tbl.delete_many({"CustomerID": customer_id, 'DatasetID': dataset_id})
            MongoDBPersistence.teams_tbl.update_many({"CustomerID": customer_id, 'DatasetID': dataset_id},
                                                     {"$unset": {"DatasetID": 1}})

            MongoDBPersistence.training_tickets_tbl.delete_many({'CustomerID': customer_id, 'DatasetID': dataset_id})
            MongoDBPersistence.rt_tickets_tbl.delete_many({'CustomerID': customer_id, 'DatasetID': dataset_id})
            MongoDBPersistence.predicted_tickets_tbl.delete_many({'CustomerID': customer_id, 'DatasetID': dataset_id})

            MongoDBPersistence.training_hist_tbl.delete_many({'CustomerID': customer_id, 'DatasetID': dataset_id})

            MongoDBPersistence.resource_details_tbl.delete_many({'CustomerID': customer_id, 'DatasetID': dataset_id})
            MongoDBPersistence.applicationDetails_tbl.delete_many({'CustomerID': customer_id, 'DatasetID': dataset_id})
            MongoDBPersistence.roaster_tbl.delete_many({'CustomerID': customer_id, 'DatasetID': dataset_id})
            MongoDBPersistence.application_analyst_mapping_tbl.delete_many({'DatasetID': dataset_id})
            MongoDBPersistence.roster_mapping_tbl.delete_many({'DatasetID': dataset_id})
            MongoDBPersistence.tickets_weightage_tbl.delete_many({'CustomerID': customer_id, 'DatasetID': dataset_id})

            MongoDBPersistence.whitelisted_word_tbl.delete_many({'CustomerID': customer_id, 'DatasetID': dataset_id})
            MongoDBPersistence.known_errors_tbl.delete_many({'CustomerID': customer_id, 'DatasetID': dataset_id})
            MongoDBPersistence.cluster_details_tbl.delete_many({'CustomerID': customer_id, 'DatasetID': dataset_id})
            MongoDBPersistence.named_entity_tbl.delete_many({'CustomerID': customer_id, 'DatasetID': dataset_id})
            MongoDBPersistence.related_tickets_tbl.delete_many({'CustomerID': customer_id, 'DatasetID': dataset_id})
            MongoDBPersistence.approved_tickets_tbl.delete_many({'CustomerID': customer_id, 'DatasetID': dataset_id})

            for filename in os.listdir("models"):
                file_list = filename.split('__')
                if (customer_name in file_list):
                    if (dataset_name in file_list):
                        os.remove("models/" + filename)
            for filename in os.listdir("data"):
                file_list = filename.split('__')
                if (customer_name in file_list):
                    if (dataset_name in file_list):
                        os.remove("data/" + filename)

            # UPDATING DEFAULT ALGORITM PARAMETERS
            MongoDBPersistence.algo_tbl.drop()
            Algorithm_dict_Lr = {"AlgorithmID": 1, "AlgorithmName": "LogisticRegression", "RecordCreatedBy": "System",
                                 "DefaultParametersSingle": [
                                     {
                                         "ParameterName": "C",
                                         "Value": 1
                                     }
                                 ], 'RecordCreatedDate': str(datetime.now())[:19]}
            MongoDBPersistence.algo_tbl.insert_one(Algorithm_dict_Lr)

            Algorithm_dict_rf = {"AlgorithmID": 2, "AlgorithmName": "RandomForestClassifier",
                                 "RecordCreatedBy": "System", "DefaultParametersSingle": [
                    {
                        "ParameterName": "criterion",
                        "Value": "gini"
                    },
                    {
                        "ParameterName": "max_depth",
                        "Value": 3
                    },
                    {
                        "ParameterName": "n_estimators",
                        "Value": 10
                    }
                ], "DropdownParams": [
                    {
                        "ParameterName": "criterion",
                        "Value": [
                            "gini",
                            "entropy"
                        ]
                    }
                ], 'RecordCreatedDate': str(datetime.now())[:19]}
            MongoDBPersistence.algo_tbl.insert_one(Algorithm_dict_rf)

            Algorithm_dict_svc = {"AlgorithmID": 3, "AlgorithmName": "SVC", "RecordCreatedBy": "System",
                                  "DefaultParametersSingle": [
                                      {
                                          "ParameterName": "C",
                                          "Value": 1
                                      },
                                      {
                                          "ParameterName": "kernel",
                                          "Value": "rbf"
                                      }
                                  ], "DropdownParams": [
                    {
                        "ParameterName": "kernel",
                        "Value": [
                            "linear",
                            "poly",
                            "rbf",
                            "sigmoid",
                            "precomputed"
                        ]
                    }
                ], 'RecordCreatedDate': str(datetime.now())[:19]}
            MongoDBPersistence.algo_tbl.insert_one(Algorithm_dict_svc)

            Algorithm_dict_mb = {"AlgorithmName": "MultinomialNB", "RecordCreatedBy": "System",
                                 "DefaultParametersSingle": [
                                     {
                                         "ParameterName": "alpha",
                                         "Value": 1
                                     }
                                 ], 'RecordCreatedDate': str(datetime.now())[:19]}
            MongoDBPersistence.algo_tbl.insert_one(Algorithm_dict_mb)

            Algorithm_dict_xg = {"AlgorithmID": 5, "AlgorithmName": "XGBClassifier", "RecordCreatedBy": "System",
                                 "DefaultParametersSingle": [
                                     {
                                         "ParameterName": "n_estimators",
                                         "Value": 1
                                     },
                                     {
                                         "ParameterName": "objective",
                                         "Value": "binary:logistic"
                                     }
                                 ], "DropdownParams": [
                    {
                        "ParameterName": "objective",
                        "Value": [
                            "binary:logistic",
                            "multi:softprob"
                        ]
                    }
                ], 'RecordCreatedDate': str(datetime.now())[:19]}
            MongoDBPersistence.algo_tbl.insert_one(Algorithm_dict_xg)

            logging.info('%s: Dataset has been deleted successfully.' % RestService.timestamp())
            resp = 'success'
        except Exception as e:
            logging.error('%s: Error occurred: %s ' % (RestService.timestamp(), str(e)))
            resp = 'failure'
        try:
            for filename in os.listdir("models/Related_Ticket_Model"):
                file_list = filename.split('_')
                if (dataset_name in file_list):
                    os.remove("models/Related_Ticket_Model/" + filename)
            logging.info(
                '%s: Related Tickets models and Preprocessed dataset has been deleted successfully from Related_Ticket_Model folder.' % RestService.timestamp())
        except Exception as e:
            logging.error('%s: Error occurred: %s ' % (RestService.timestamp(), str(e)))
        return resp

    @staticmethod
    def updateDaemonTraining(customer_id, dataset_id, training_completed_flag, completed_status, training_start_date,
                             training_end_date=''):
        training_stats = {}
        training_stats['TrainingCompletedFlag'] = training_completed_flag
        training_stats['TrainingStartedBy'] = os.getlogin()
        training_stats['TrainingStartDate'] = training_start_date
        training_stats['TrainingEndDate'] = training_end_date
        training_stats['CompletedStatus'] = completed_status
        try:
            MongoDBPersistence.datasets_tbl.update_one({"CustomerID": customer_id, 'DatasetID': dataset_id},
                                                       {"$set": {"TrainingStatus": training_stats}})
            resp = 'success'
        except Exception as e:
            logging.error('%s: Error occurred: %s ' % (RestService.timestamp(), str(e)))
            resp = 'failure'
        return resp

    @staticmethod
    def getTagsDatasetDetails(customer_id, dataset_id):
        # customer_tbl is a pymongo object to TblCustomer
        train_dict = {}
        dataset_dict = MongoDBPersistence.tag_dataset_tbl.find_one(
            {"CustomerID": customer_id, "TagsDatasetID": dataset_id},
            {"TagsDatasetName": 1, "ColumnNames": 1, "TicketCount": 1, "_id": 0})
        if (dataset_dict):
            train_dict['name'] = dataset_dict["TagsDatasetName"]
            train_dict['fields'] = dataset_dict['ColumnNames']
            train_dict['count'] = dataset_dict['TicketCount']
        else:
            logging.info('%s: Dataset details not found for the team.' % RestService.timestamp())

        return json_util.dumps(train_dict)

    @staticmethod
    def getTagDatasetID(customer_id, team_id):
        dataset_ = MongoDBPersistence.teams_tbl.find_one({"CustomerID": customer_id, "TeamID": team_id},
                                                         {"TagsDatasetID": 1, "_id": 0})
        if (dataset_):
            logging.info('%s: Getting tag dataset details.' % RestService.timestamp())
            dataset_id = dataset_["TagsDatasetID"]
        else:
            logging.info('%s: Tag Dataset not found for the team.' % RestService.timestamp())
            dataset_id = -1
        return json_util.dumps(dataset_id)

    @staticmethod
    def deleteTagDataset(customer_id, dataset_id):
        # Delete both TblIncidentTraining
        try:
            customer_name = \
                MongoDBPersistence.customer_tbl.find_one({'CustomerID': customer_id}, {'CustomerName': 1, '_id': 0})[
                    'CustomerName']
            dataset_name = \
                MongoDBPersistence.tag_dataset_tbl.find_one({'CustomerID': customer_id, "TagsDatasetID": dataset_id},
                                                            {'TagsDatasetName': 1, '_id': 0})['TagsDatasetName']
            MongoDBPersistence.tag_dataset_tbl.delete_many({"CustomerID": customer_id, 'TagsDatasetID': dataset_id})
            MongoDBPersistence.teams_tbl.update_many({"CustomerID": customer_id, 'TagsDatasetID': dataset_id},
                                                     {"$unset": {"TagsDatasetID": 1}})

            MongoDBPersistence.tag_training_tbl.delete_many({'CustomerID': customer_id, 'TagsDatasetID': dataset_id})
            
            for filename in os.listdir("models/tagging"):
                file_list = filename.split('__')
                if (customer_name in file_list):
                    if (dataset_name in file_list):
                        if ('tags' in file_list):
                            os.remove("models/tagging/" + filename)
            logging.info('%s:Tags Dataset has been deleted successfully.' % RestService.timestamp())
            resp = 'success'
        except Exception as e:
            logging.error('%s: Error occurred: %s ' % (RestService.timestamp(), str(e)))
            resp = 'failure'
        return resp

    @staticmethod
    def getTrainedTicketsCount():
        count = '0'
        try:
            count = str(MongoDBPersistence.training_tickets_tbl.count())
        except Exception as e:
            logging.error('%s' % str(e))
        return count
