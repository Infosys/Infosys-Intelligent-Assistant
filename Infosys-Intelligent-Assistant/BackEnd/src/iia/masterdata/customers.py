__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

from iia.persistence.mongodbpersistence import MongoDBPersistence
from iia.restservice import RestService
from iia.utils.config_helper import get_config
from bson import json_util
from flask import request
import pandas as pd
import json
import io
import csv
import configparser
from iia.utils.log_helper import get_logger, log_setup

logging = get_logger(__name__)
app = RestService.getApp();

@app.route("/api/customer/<customer_name>", methods=["GET"])
def getCustomerId(customer_name):
    return CustomerMasterData.getCustomerId(customer_name)

@app.route("/api/uploadTicketWeightage/<int:customer_id>/<chosen_team>", methods=["POST"])
def db_insert_ticket_weightage_details(customer_id, chosen_team):
    return CustomerMasterData.db_insert_ticket_weightage_details(customer_id, chosen_team)


@app.route("/api/getTicketWeightage/<int:customer_id>/<chosen_team>", methods=["GET"])
def get_ticket_weightage_details(customer_id, chosen_team):
    return CustomerMasterData.get_ticket_weightage_details(customer_id, chosen_team)


@app.route('/api/deleteAllTicketWeightage/<int:customer_id>/<chosen_team>', methods=['DELETE'])
def delete_all_ticket_weightage(customer_id, chosen_team):
    return CustomerMasterData.delete_all_ticket_weightage(customer_id, chosen_team)


@app.route('/api/insertITSMDetails', methods=['POST'])
def insert_ITSM_details():
    return CustomerMasterData.insert_ITSM_details()


@app.route('/api/getITSMTools', methods=['GET'])
def getITSMTools():
    return CustomerMasterData.get_ITSM_tools()


@app.route('/api/getConfigKey/<string:key>', methods=['GET'])
def getConfigKey(key):
    if request.method == 'GET':
        try:
            config = get_config(key)
            resp = {"Status": "Success"}
            resp.update(config)
            return json_util.dumps(resp)
        except Exception as e:
            resp = {"Status": "Failure"}
            return json_util.dumps(resp)
    else:
        resp = {"Status": "Failure"}
        return json_util.dumps(resp)


class CustomerMasterData(object):
    '''
    classdocs
    '''

    def __init__(self, params):
        '''
        Constructor
        '''
    @staticmethod
    def getCustomerId(customer_name):
        # customer_tbl is a pymongo object to TblCustomer
        customer = MongoDBPersistence.customer_tbl.find_one({"CustomerName": customer_name},
                                                            {"CustomerID": 1, "_id": 0})
        if (customer):
            try:
                resp = customer['CustomerID']
            except Exception as e:
                logging.error('%s: Error occurred: %s ' % (RestService.timestamp(), str(e)))
        else:
            logging.info(
                '%s: Failure: We are sorry, there is no customer with name %s registerd with us. please register with us before using ML algos.' % (
                RestService.timestamp(), customer_name))
            resp = 'failure'
        return json_util.dumps(resp)

    @staticmethod
    def db_insert_ticket_weightage_details(customer_id, chosen_team):
        new_dataset_flag = 0
        file = request.files['ticketWeightageDetails']
        dataset_ = MongoDBPersistence.teams_tbl.find_one({"CustomerID": customer_id, "TeamName": chosen_team},
                                                         {"DatasetID": 1, "_id": 0})

        if (dataset_):
            # Dataset exist for the team
            logging.info('%s: Getting old dataset details.' % RestService.timestamp())
            dataset_id = dataset_["DatasetID"]
        else:
            last_dataset_id = 0
            dataset_name = chosen_team
            # Newly adding the dataset
            logging.info('%s: Adding new dataset.' % RestService.timestamp())
            # getting max dataset id for the customer, so that new dataset id = old + 1
            dataset_dict = MongoDBPersistence.datasets_tbl.find_one(
                {"CustomerID": customer_id, "DatasetID": {"$exists": True}},
                {'_id': 0, "DatasetID": 1, "DatasetName": 1}, sort=[("DatasetID", -1)])

            if (dataset_dict):
                last_dataset_id = dataset_dict['DatasetID']
                dataset_name = dataset_dict['DatasetName']
            else:
                logging.info('%s: Adding dataset for very first team.' % RestService.timestamp())

            # New dataset id for the customer
            dataset_id = last_dataset_id + 1

            new_dataset_dict = {}
            new_dataset_dict["DatasetID"] = dataset_id
            new_dataset_dict["DatasetName"] = dataset_name
            new_dataset_dict["CustomerID"] = customer_id
            new_dataset_flag = 1

        if not file:
            return "No file"
        elif '.csv' not in str(file):
            return "Upload csv file."
        stream = io.StringIO(file.stream.read().decode("latin-1"), newline=None)
        stream.seek(0)
        result = stream.read()

        # create list of dictionaries keyed by header row   k.lower()
        csv_dicts = [{k.lower(): v for k, v in row.items()} for row in csv.DictReader(result.splitlines(), \
                                                                                      skipinitialspace=True)]

        for item in csv_dicts:
            item.update({"CustomerID": customer_id})
            item.update({"DatasetID": dataset_id})

        # Clease data before inserting into DB
        csv_df = pd.DataFrame(csv_dicts)

        # remove spaces between the name of column
        csv_df.columns = ['_'.join(col.split(' ')) for col in csv_df.columns]
        # Remove duplicate columns if there any (Based on Incident number)
        csv_df_cols = csv_df.columns

        if (len(set(csv_df_cols)) < len(csv_df_cols)):
            logging.info('%s: Duplicate columns, please rename the duplicate column names..' % RestService.timestamp())
            return 'failure'

        json_str = csv_df.to_json(orient='records')
        json_data = json.loads(json_str)
        try:
            logging.info('%s: Trying to insert records into TblTicketWeightage...' % RestService.timestamp())
            for ticket_weightage_doc in json_data:
                MongoDBPersistence.tickets_weightage_tbl.update_one(
                    {'ticket_type': ticket_weightage_doc['ticket_type'], 'priority': ticket_weightage_doc['priority'],
                     'status': ticket_weightage_doc['status'], 'DatasetID': ticket_weightage_doc['DatasetID']},
                    {'$set': ticket_weightage_doc}, upsert=True)
            logging.info('%s: Completed with inserting TicketWeightage documents...' % RestService.timestamp())

            if (new_dataset_flag):
                logging.info('%s: Trying to insert new dataset into TblDataset...' % RestService.timestamp())
                MongoDBPersistence.datasets_tbl.insert_one(new_dataset_dict)
                logging.info('%s: Trying to update TblTeams with Dataset details...' % RestService.timestamp())
                MongoDBPersistence.teams_tbl.update_one({'CustomerID': customer_id, "TeamName": chosen_team},
                                                        {"$set": {"DatasetID": dataset_id}}, upsert=False)

            logging.info('%s: Records inserted successfully.' % RestService.timestamp())
            resp = "success"

        except Exception as e:
            logging.error('%s: Error occurred: %s ' % (RestService.timestamp(), str(e)))
            logging.error(
                '%s: Possible error: Data format in csv not matching with database constarints.(unique key & not null)' % RestService.timestamp())
            resp = 'failure'

        return resp

    @staticmethod
    def get_ticket_weightage_details(customer_id, chosen_team):
        ticket_weightage_lst = []

        try:
            team_doc = MongoDBPersistence.teams_tbl.find_one({'TeamName': chosen_team, 'DatasetID': {'$exists': True}},
                                                             {'_id': 0, 'DatasetID': 1})

            if team_doc:
                dataset_id = team_doc.get('DatasetID')
                if dataset_id:
                    ticket_weightage_lst = list(MongoDBPersistence.tickets_weightage_tbl.find({'DatasetID': dataset_id,
                                                                                               'CustomerID': customer_id}
                                                                                              )
                                                )
            else:
                ticket_weightage_lst = []
                logging.info("Unable to fetch ticket weightage details for the chosen team")

        except Exception as e:
            logging.error('%s: Error occurred: %s ' % (RestService.timestamp(), str(e)))

        return json_util.dumps(ticket_weightage_lst)

    @staticmethod
    def delete_all_ticket_weightage(customer_id, chosen_team):
        response = {}
        dataset_ = MongoDBPersistence.teams_tbl.find_one({"CustomerID": customer_id, "TeamName": chosen_team},
                                                         {"DatasetID": 1, "_id": 0})
        print("Dataset id in tickets weightage ", dataset_.get('DatasetID'))
        dataset_id = dataset_.get('DatasetID')
        try:
            if dataset_id:
                response = MongoDBPersistence.tickets_weightage_tbl.delete_many(
                    {"CustomerID": customer_id, 'DatasetID': dataset_id})
                print(response.deleted_count)
                logging.info('%s: All ticket weightage details are deleted' % (RestService.timestamp()))

        except Exception as e:
            print('Some error occurred in delete_all_applications(): ', e)
            return ('Some error occured in delete_all_applications(): ', e)

        return 'success'

    @staticmethod
    def insert_ITSM_details():
        try:

            document = request.get_json()
            doc = document[0]
            user_id = doc["UserID"]
            password = doc["Password"]
            itsm_toolname = doc["ITSMToolName"]

            MongoDBPersistence.itsm_details_tbl.insert(
                {"UserID": user_id, "Password": password, "ITSMToolName": itsm_toolname})
            logging.info('%s: successfully inserted ITSM Details!' % RestService.timestamp)
            status = "success"
        except Exception as e:
            logging.error('%s: Error occurred: %s ' % (RestService.timestamp, str(e)))
            status = "failure"

        return status

    @staticmethod
    def get_ITSM_tools():
        try:
            itsm_tools = MongoDBPersistence.itsm_tool_names.find({}, {'ITSMToolNames': 1, '_id': 0})
            logging.info(f"itsm_tools: {itsm_tools[0]}")
            return json_util.dumps(list(itsm_tools)[0])
        except Exception as e:
            logging.error(e, exc_info=True)
            itsm_tools = {'ITSMToolNames': 'Others'}
            return json_util.dumps(itsm_tools)

    @staticmethod
    def check_custom(field):
        try:

            config = configparser.ConfigParser()
            config["DEFAULT"]["path"] = "config/"
            config.read(config["DEFAULT"]["path"] + "iia.ini")
            custom_flag = config["CustomConfig"][field]
            custom_module_url = config["CustomConfig"]["customUrl"]
            return (custom_flag, custom_module_url)
        except:
            logging.info(
                "%s: Unable to connect to Config Files, check if custom fields are present or not" % RestService.timestamp())
            return ("failure", "failure")

    @staticmethod
    def get_botOrchestratorUrl(field):
        try:
            config = configparser.ConfigParser()
            config["DEFAULT"]["path"] = "config/"
            config.read(config["DEFAULT"]["path"] + "iia.ini")
            custom_flag = config["BOT ORCH"][field]
            custom_module_url = config["BOT ORCH"]["bot_orch"]
            return (custom_flag, custom_module_url)
        except:
            logging.info(
                "%s: Unable to connect to Config Files, check if custom fields are present or not" % RestService.timestamp())
            return ("failure", "failure")
