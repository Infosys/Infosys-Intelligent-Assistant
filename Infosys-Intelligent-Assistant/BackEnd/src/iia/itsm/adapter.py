__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""
from iia.persistence.mongodbpersistence import MongoDBPersistence
import pysnow
from servicenow import ServiceNow
from servicenow import Connection
from iia.restservice import RestService
from iia.masterdata.datasets import DatasetMasterData
from iia.persistence.mappingpersistence import MappingPersistence
from iia.masterdata.resources import ResourceMasterData
from iia.masterdata.customers import CustomerMasterData
from iia.usermanagement.usermanagement import UserManagement
from flask import request
from bson import json_util
from datetime import datetime, timedelta
from twilio.rest import Client
import os, sys
import configparser
from flask import session
import importlib
import requests
import requests, json
import pymsteams
import configparser
from datetime import datetime
from iia.utils.config_helper import get_config
from pathlib import Path

from iia.environ import *
from iia.utils.log_helper import get_logger, log_setup
import requests
import msal
import atexit
import os.path
logging = get_logger(__name__)


# Changed the name of class ServiceNow to SNOW since servicenow package already has ServiceNow
class SNOW(object):

    def __init__(self, itsm_details):
        self.itsm_details = itsm_details
        # Needs to set self.filter criteria

    c = None
    servicenow_incidents = None

    @staticmethod
    def getClient(itsm_details):
        try:

            if (SNOW.c is None):
                # Connect to Service Now using default api method (JSON)
                logging.info(f"Connecting to {itsm_details['ITSMInstance']}")
                logging.info(f"userid: {itsm_details['UserID']}")
                logging.info(f"password: {itsm_details['Password']}")

                SNOW.c = pysnow.Client(instance=itsm_details['ITSMInstance'], user=itsm_details['UserID'],
                                       password=itsm_details['Password'])
                # To display actual values of fields instead of external reference link or GUID - Service Now
                SNOW.c.parameters.display_value = True
                SNOW.c.parameters.exclude_reference_link = True

                SNOW.servicenow_incidents = SNOW.c.resource(api_path='/table/incident')

            return SNOW.servicenow_incidents
        except Exception as e:
            logging.info("%s: Error in connecting to SNOW %s " % (RestService.timestamp(), str(e)))

    # Changed the method name from get_Current_ServiceNow_incidents to get_itsm_instance_data
    def get_itsm_instance_data(self, customer_id):

        before_itsm_pull = datetime.now()
        logging.debug(f"before_itsm_pull: {before_itsm_pull}")

        path1 = str(Path.cwd()) + "\\static\\assets\\uploads\\"
        print("Static path : ", path1)
        path2 = str(Path.cwd()) + "\\data\\AttachementAnalysis\\uploads\\"
        print("Attachment Analysis path : ", path2)
        # Creating directory for image attachements in static folder
        if not os.path.exists(str(Path.cwd()) + "\\static\\assets\\uploads\\"):
            os.makedirs(str(Path.cwd()) + "\\static\\assets\\uploads\\")

        # Creating directory for image attachements in AttachementAnalysis folder
        if not os.path.exists(str(Path.cwd()) + "\\data\\AttachementAnalysis\\uploads\\"):
            os.makedirs(str(Path.cwd()) + "\\data\\AttachementAnalysis\\uploads\\")

        DIR = [path1, path2]
        incident_no_lst = []
        application_groups = []
        assigned_incdnt_no_lst = []
        # checking if session exists or not
        user = session['user']

        accessible_datasets = DatasetMasterData.guess_dataset_access(user)
        try:

            servicenow_incidents = SNOW.getClient(self.itsm_details)
            print("Client", servicenow_incidents)
            application_groups = MongoDBPersistence.applicationDetails_tbl.find().distinct(group_field_name)
            logging.info(f"application_groups : {application_groups}")
            if (not application_groups):
                application_groups = MongoDBPersistence.training_tickets_tbl.find({"CustomerID": customer_id}).distinct(
                    group_field_name)
                logging.info("inside if ")

            logging.info("%s: Going for default configurations of SNOW" % RestService.timestamp())
            # Get all New and In progress tickets and filter them based on assignment groups
            queryBuilder = status_field_name + '=1^OR' + status_field_name + '=2^' + group_field_name + '!=is_empty^'

            for app_group in application_groups:
                queryBuilder = queryBuilder + group_field_name + 'LIKE' + app_group + '^OR'

            try:
                logging.info(f"querybuilder: {queryBuilder[:-3]}")
                response = servicenow_incidents.get(query=queryBuilder[:-3])
                response = response.all()
                logging.info(f"response : {len(list(response))}")

            except Exception as e:
                logging.error(f" error inside get_itsm_instance_data {str(e)}")
                print("exceptioon in getting tickets from service now", str(e))

            for responce_doc in response:
                logging.info("rt tickets %s" % (responce_doc[ticket_id_field_name]))
                incident_no_lst.append(responce_doc[ticket_id_field_name])

            logging.info(f"servicenow response incident_no_lst: {incident_no_lst}")
            # Remove all inicidents from DB, which are not present in Service Now dump
            MongoDBPersistence.rt_tickets_tbl.update_many({ticket_id_field_name: {'$nin': incident_no_lst}},
                                                          {'$set': {status_field_name: 'closed'}})

            datasets = list(MongoDBPersistence.datasets_tbl.find({"DatasetID": {"$in": accessible_datasets}}))

            incident_number_lst = MongoDBPersistence.rt_tickets_tbl.find({},
                                                                         {'_id': 0, ticket_id_field_name: 1}).distinct(
                ticket_id_field_name)
            for record in response:
                dataset_id = 0
                logging.info('%s: START - Tickets Update in DB from Service Now....' % (RestService.timestamp()))
                if (record[ticket_id_field_name] not in incident_number_lst):
                    # Update status and other columns of Incidents in DB and Insert the new incidents in DB
                    record['CustomerID'] = customer_id
                    record["workload"] = 0.0
                    record["tickets_assigned"] = 0
                    record['user_status'] = 'Not Approved'
                    record['Source'] = 'SNOW'
                    record['auto_resolution'] = False

                    record['configuration_item'] = str(record['cmdb_ci'])
                    record['doc2vec_related_tic_flag'] = False
                    record['textrank_related_tic_flag'] = False
                    record['word2vec_related_tic_flag'] = False
                    record['attachment_parsed']= False

                    if (record['state'] != 'New'):
                        assigned_incdnt_no_lst.append(record[ticket_id_field_name])

                for dataset in datasets:
                    fields = dataset['UniqueFields']
                    match_flag = 0
                    for field in fields:
                        try:
                            # path for saving attachemnts
                            dataset_values = MongoDBPersistence.training_tickets_tbl.find(
                                {"CustomerID": customer_id, "DatasetID": dataset['DatasetID']}).distinct(
                                field['FieldName'])  # "DatasetID":dataset['DatasetID']
                            logging.info('distinct %s values are %s ' % (field['FieldName'], dataset_values))
                            logging.info(
                                'real time ticket %s value is %s' % (field['FieldName'], record[field['FieldName']]))
                        except Exception as e:
                            logging.error('%s: Error: %s' % (RestService.timestamp(), str(e)))
                            logging.info(
                                '%s: Column name %s not found.' % (RestService.timestamp(), field['FieldName']))
                            break
                        if (field['FieldName'] in record.keys()):
                            logging.info(
                                'real time ticket %s value is %s' % (field['FieldName'], record[field['FieldName']]))
                            if (record[field['FieldName']] in set(dataset_values)):
                                match_flag = match_flag + 1
                    if (match_flag == len(fields)):
                        dataset_id = dataset['DatasetID']
                        record['DatasetID'] = dataset_id
                        logging.info('real time ticket dataset ID is %s' % (record['DatasetID']))
                        break
                if (dataset_id == 0):
                    logging.info('%s: the ticket (Incident Number: %s) do not match with any of the datasets.' % (
                    RestService.timestamp(), record[ticket_id_field_name]))
                    continue
                    
                MongoDBPersistence.rt_tickets_tbl.update_one({ticket_id_field_name: record[ticket_id_field_name]},
                                                             {'$set': record}, upsert=True)

                logging.info('%s: END - Tickets Udapte in DB from Service Now....' % (RestService.timestamp()))

            if (response):
                assignment_enabled_flag = MongoDBPersistence.assign_enable_tbl.find_one({}, {"_id": 0})[
                    'assignment_enabled']
                if (assignment_enabled_flag == "false"):
                    assignment_enabled_flag = 0
                if (assignment_enabled_flag):
                    logging.info(
                        'Trying to call incident_workload_update() method of ResourceMasterData to calculate workload for tickets which are not New')
                    ResourceMasterData.incident_workload_update(customer_id, dataset_id, assigned_incdnt_no_lst)

                logging.info('%s: Tickets received from Service Now' % (RestService.timestamp()))
                response_tmp = MongoDBPersistence.db.TblIncidentRT.find(
                    {status_field_name: 'New', 'user_status': 'Not Approved'})

                after_itsm_pull = datetime.now()
                logging.debug(f"after_itsm_pull: {after_itsm_pull}")
                logging.debug(f"time_taken: {after_itsm_pull - before_itsm_pull}")

                return (json_util.dumps(response_tmp))
            else:
                logging.info('%s: Could not get tickets from Service Now' % (RestService.timestamp()))
                return 'no tickets found in Service Now'
        except Exception as e:
            return (json_util.dumps({'exception': str(e)}))

    def get_itsm_url_data(self, customer_id):
        print("Method to get Data using URL of SERVINCENOW instead of instance")


class ManageEngine:

    def __init__(self, manage_engine):
        print("Inside Manage Engnie Constructor, Currently no definition please provide definition")

    def get_itsm_url_data(self):
        pass


class ITSMUpdate:

    def __init__(self, customer_id=None, dataset_id=None, itsm_details=None):
        '''
        Constructor
        '''

    def snow_update_fields(self, customer_id, dataset_id, itsm_details):
        try:
            config = configparser.ConfigParser()
            config["DEFAULT"]['path'] = "config/"
            config.read(config["DEFAULT"]["path"] + "iia.ini")

        except Exception as e:
            logging.error('someField is not defined in "config/iia.ini" file. Define it for Assignee Prediction')
            logging.error(e, exc_info=True)

        logging.info("Snow update fields in Adapter file")
        customer_name = MongoDBPersistence.customer_tbl.find_one({'CustomerID': customer_id}, \
                                                                 {'CustomerName': 1, '_id': 0})['CustomerName']

        itsm_tool_name = MongoDBPersistence.itsm_details_tbl.find_one({}, {"_id": 0, "ITSMToolName": 1})["ITSMToolName"]

        logging.info("Going for default flow in update Predicted Field.")
        user = session['user']
        try:
            servicenow_incidents = SNOW.getClient(itsm_details)
            data = request.get_json()
            print("User Selected Data", data)
            incidentNumber = ''
            incident_lst = []
            approved_tickets = []
            UpdatedTicketDump = {}
            FailedTickets = []

            servicenow_exists = MongoDBPersistence.customer_tbl.find_one({"CustomerID": customer_id},
                                                                         {"_id": 0, "SNOWInstance": 1})
            if (servicenow_exists):
                servicenow_flag = 1
            else:
                servicenow_flag = 0
            if (data):
                for incidentToUpdate in data:

                    incidentNumber = incidentToUpdate[ticket_id_field_name]
                    assigned_to = ''
                    try:
                        assigned_to = incidentToUpdate['predicted_assigned_to']
                        incidentToUpdate[
                            'work_notes'] = f"Ticket Manually Approved and Assigned to {assigned_to} by admin"
                    except Exception as e:
                        logging.error(e, exc_info=True)

                    ticket_status = MongoDBPersistence.rt_tickets_tbl.find_one(
                        {"CustomerID": customer_id, "DatasetID": dataset_id, ticket_id_field_name: incidentNumber},
                        {"_id": 0, "user_status": 1, description_field_name: 1, "short_description": 1})

                    if (ticket_status != None):
                        if (ticket_status['user_status'] == 'Not Approved'):
                            incident_lst.append(incidentNumber)

                            # the following code is for inserting approved tickets into Training table for Retraining
                            incidentToUpdate['CustomerID'] = customer_id
                            incidentToUpdate["DatasetID"] = dataset_id
                            incidentToUpdate['user'] = user
                            logging.info('Trying to get document from "rt_tickets_tbl"')
                            incidentToinsert = MongoDBPersistence.rt_tickets_tbl.find_one(
                                {ticket_id_field_name: incidentNumber})

                            if (not incidentToinsert):
                                logging.error(
                                    'Could not get document from "rt_tickets_tbl" for ticket %s' % str(incidentNumber))


                            MongoDBPersistence.rt_tickets_tbl.update_one(
                                {ticket_id_field_name: incidentNumber}
                                , {"$set": {'assigned_to': assigned_to}})

                            logging.info('Trying to update "predicted_tickets_tbl)()" with new predicted details')
                            MongoDBPersistence.predicted_tickets_tbl.update_one(
                                {'CustomerID': customer_id, ticket_id_field_name: incidentNumber,
                                 'DatasetID': dataset_id}, {"$set": incidentToUpdate}, upsert=False)
                            MongoDBPersistence.rt_tickets_tbl.update_one(
                                {'CustomerID': customer_id, ticket_id_field_name: incidentNumber,
                                 'DatasetID': dataset_id}, {"$set": incidentToUpdate}, upsert=False)

                            approved_data = {}

                            for key, value in incidentToUpdate.items():
                                key = key.lower()
                                unwanted_lst = ['user', 'number', 'customerid', 'datasetid']
                                if (key == 'predicted_assigned_to'):
                                    key = 'assigned_to'
                                if (key not in unwanted_lst):
                                    approved_data[key] = value

                            if (servicenow_flag):
                                if (servicenow_incidents):
                                    try:
                                        response = servicenow_incidents.update(
                                            query={ticket_id_field_name: incidentNumber},
                                            payload=approved_data)

                                    except Exception as e:
                                        print("error in updating values to itsm ", e)

                            inci_present = None
                            try:
                                inci_present = MongoDBPersistence.approved_tickets_tbl.find_one(
                                    {"CustomerID": customer_id, "ticket_number": incidentNumber})
                            except Exception as e:
                                print("error ", e)
                            logging.info(
                                'Tickets Got Approved in SNOW now trying to insert approved details to "approved_tickets_tbl"')
                            if (inci_present is None):
                                desc_or_short_desc = MongoDBPersistence.rt_tickets_tbl.find_one(
                                    {"CustomerID": customer_id, "DatasetID": dataset_id,
                                     ticket_id_field_name: incidentNumber},
                                    {"_id": 0, "user_status": 1, description_field_name: 1,
                                     "short_description": 1})
                                if "description" in desc_or_short_desc.keys():
                                    MongoDBPersistence.approved_tickets_tbl.insert_one({
                                        'CustomerID': customer_id,
                                        'DatasetID': dataset_id,
                                        'UserID': user,
                                        'ticket_number': incidentNumber,
                                        'ticket_description': ticket_status['description'],
                                        'assigned_to': approved_data["assigned_to"],
                                        'approved_data': approved_data,
                                        'auto_approve': False
                                    })
                                elif "short_description" in desc_or_short_desc.keys():
                                    MongoDBPersistence.approved_tickets_tbl.insert_one({
                                        'CustomerID': customer_id,
                                        'DatasetID': dataset_id,
                                        'UserID': user,
                                        'ticket_number': incidentNumber,
                                        'short_description': ticket_status['short_description'],
                                        'assigned_to': approved_data["assigned_to"],
                                        'approved_data': approved_data,
                                        'auto_approve': False
                                    })

                            incidentToinsert1 = MongoDBPersistence.rt_tickets_tbl.find_one(
                                {ticket_id_field_name: incidentNumber})
                            incidentToinsert1['TrainingFlag'] = 0

                            try:
                                MongoDBPersistence.training_tickets_tbl.update_one(
                                    {ticket_id_field_name: incidentToinsert1[ticket_id_field_name]},
                                    {"$set": incidentToinsert1}, upsert=True)
                            except Exception as e:
                                print(str(e))

                            try:

                                print("....................ready to fetch the data...............")

                                PMA_data = list(MongoDBPersistence.predicted_tickets_tbl.find(
                                    {'number': incidentNumber, "predicted_assigned_to": {"$ne": ''}},
                                    {"number": 1, "_id": 0, "predicted_assigned_to": 1, "priority": 1}))

                                try:
                                    for i in PMA_data:
                                        try:
                                            ITSMAdapter.notifications(i, ticket_id_field_name)
                                        except Exception as e:
                                            logging.error(e, exc_info=True)
                                except Exception as e:
                                    logging.error(e)

                            except Exception as ex:
                                print('Exception.....', ex)
                            # End of key, value looping
                            logging.info(
                                ' Predicted Details has been successfully updated into a collection TblPredictedData by user %s.' % (
                                    user))
                            logging.info('Trying to update document of "rt_tickets_tbl" with "user_status" "Approved"')
                            MongoDBPersistence.rt_tickets_tbl.update_one(
                                {'CustomerID': customer_id, ticket_id_field_name: incidentNumber,
                                 'DatasetID': dataset_id}, {"$set": {'user_status': 'Approved'}}, upsert=False)
                            logging.info('Trying to update "predicted_tickets_tbl" with approver details')
                            MongoDBPersistence.predicted_tickets_tbl.update_one(
                                {'CustomerID': customer_id, ticket_id_field_name: incidentNumber,
                                 'DatasetID': dataset_id}, {"$set": {'user': user, "user_status": "Approved"}},
                                upsert=False)
                            resp = 'success'
                        else:
                            logging.info(f"CustomerID : {customer_id}, DatasetID : {dataset_id}")
                            approved_user = MongoDBPersistence.predicted_tickets_tbl.find_one(
                                {"CustomerID": customer_id, "DatasetID": dataset_id}, {"_id": 0, "user": 1})
                            logging.info(f"approved_user: {approved_user}")
                            approved_user = approved_user['user']
                            logging.info(
                                "self. The ticket with ticket number %s has already been approved by user %s " % (
                                incidentNumber, approved_user))
                            approved_ticket = MongoDBPersistence.predicted_tickets_tbl.find_one(
                                {"CustomerID": customer_id, "DatasetID": dataset_id},
                                {"_id": 0, ticket_id_field_name: 1, 'user': 1})
                            approved_tickets.append(approved_ticket)  # List of tickets which are already approved
                    else:
                        UpdatedTicketDump['display_id'] = ticket_status['display_id']
                        FailedTickets.append({'display_id': UpdatedTicketDump['display_id']})
                try:
                    # --Workload calculation--
                    ResourceMasterData.incident_workload_update(customer_id, dataset_id, incident_lst)
                except Exception as e:
                    logging.info("%s Error Occured in workload update %s " % (RestService.timestamp(), str(e)))
                    logging.error(e, exc_info=True)
                if (approved_tickets):
                    status = "ApprovedTickets"
                    result = [{"Status": status, "Approved_Tickets": approved_tickets}]
                if (FailedTickets):
                    status = "partial"
                    result[0]['Status'] = status
                    result[0]['Failed_Tickets'] = FailedTickets
                else:
                    status = "success"
                    result = [{"Status": status}]
            else:
                logging.info(
                    '%s: Getting empty JSON from Angular component, returning string empty...' % RestService.timestamp())
                status = "empty"
                result = [{"Status": status}]
        except Exception as e:
            logging.error(e,exc_info=True)
            status = "failure"
            result = [{"Status": status}, {"Error": str(e)}]
        return json_util.dumps(result)


class ITSMAdapter(object):

    def __init__(self, itsm_details, customer_id=False, dataset_id=False, data=False):
        '''
        Constructor
        '''
        self.itsm_details = itsm_details
        self.customer_id = customer_id
        self.dataset_id = dataset_id
        self.data = data

    def invoke_itsm(self):

        user_status = UserManagement.loginState()
        if (user_status == 'Logged in'):
            user = session['user']
            login_user = MongoDBPersistence.users_tbl.find_one({"UserID": user}, {"_id": 0})

            if (login_user):
                custom_itsm_flag, custom_url = CustomerMasterData.check_custom("customITSM")

                if (custom_itsm_flag == 'failure'):
                    logging.info("%s: Not able to read values from Configure File" % RestService.timestamp())
                    return "failure"

                elif (custom_itsm_flag == "True"):
                    logging.info("%s Custom ITSM is present invoking Custom ITSM" % RestService.timestamp())
                    proxies = {"http": None, "https": None}

                    api = custom_url + "api/get_itsm_instance_data/" + str(self.customer_id)
                    print("api created", api)
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

                    itsm_name = self.itsm_details['ITSMToolName']
                    # Check ITSM Tool
                    if (itsm_name == 'SNOW'):
                        itsm_url_var = 'ITSMUrl'
                        # if we are using ITSM instance or ITSM dev instance
                        if (itsm_url_var in self.itsm_details.keys()):
                            pass
                        else:
                            return self.snow_instance_invoke()
                    else:
                        pass
            else:
                logging.info("%s User is not authenticated" % RestService.timestamp())
                return "failure"
        else:
            logging.info("%s You are not logged in please login" % RestService.timestamp())
            return "failure"

    # Method to invoke SNOW using a dev instance
    def snow_instance_invoke(self):
        customer_id = self.itsm_details['CustomerID']
        snow_obj = SNOW(self.itsm_details)
        resp = snow_obj.get_itsm_instance_data(customer_id)
        return resp

    # Method to invoke SNOW using REST API url
    def snow_url_invoke(self, itsm_url, user_id, password):
        pass

    # Method to invoke MananeEngine using url and tokens
    def manage_engine_invoke(self, me_url, authentication_token, api_key, user_id, password):
        pass

    def updateITSMFields(self):

        user_status = UserManagement.loginState()
        if (user_status == 'Logged in'):
            user = session['user']
            login_user = MongoDBPersistence.users_tbl.find_one({"UserID": user}, {"_id": 0})

            if (login_user):

                itsm_obj = ITSMUpdate()
                custom_itsm_flag, custom_url = CustomerMasterData.check_custom("customITSM")
                if (custom_itsm_flag == 'failure'):
                    logging.info("%s: Not able to read values from Configure File" % RestService.timestamp())
                    return "failure"

                elif (custom_itsm_flag == "True"):
                    logging.info("%s Custom ITSM is present invoking Custom ITSM" % RestService.timestamp())
                    proxies = {"http": None, "https": None}
                    api = custom_url + "api/update_itsm_fields"

                    req_head = {"Content-Type": "application/json"}
                    post_data = {"CustomerID": self.customer_id, "DatasetID": self.dataset_id, "data": self.data,
                                 "user_id": user}
                    req_response = requests.post(api, headers=req_head, data=json.dumps(post_data), proxies=proxies)

                    return json_util.dumps(req_response.json())
                else:
                    return itsm_obj.snow_update_fields(self.customer_id, self.dataset_id, self.itsm_details)
            else:
                logging.info("%s You are not Authenticated" % RestService.timestamp())
                status = "No Login Found"
                result = [{"Status": status}]
                return json_util.dumps(result)
        else:
            logging.info("%s You are not logged in please login" % RestService.timestamp())
            status = "No Login Found"
            result = [{"Status": status}]
            return json_util.dumps(result)

    @staticmethod
    def notifications(incidentToUpdate, ticket_id_field_name):
        config = configparser.ConfigParser()
        config["DEFAULT"]['path'] = "config/"
        config.read(config["DEFAULT"]["path"] + "iia.ini")
        MSteams_url = config["Notification"]["MSteams_url"]
        twilio_account_sid = config["Notification"]["twilio_account_sid"]
        print(twilio_account_sid, "----------------------line 219")
        twilio_authentication_token = config["Notification"]["twilio_authentication_token"]
        twilio_sms_call_from_number = config["Notification"]["twilio_sms_call_from_number"]
        twilio_whatsapp_from_number = config["Notification"]["twilio_whatsapp_from_number"]
        twilio_call_record = config["Notification"]["twilio_call_record"]
        country_code = config["Notification"]['country_code']
        priority_field = config["Fields"]["priorityField"]
        incident_number = incidentToUpdate[ticket_id_field_name]
        if incidentToUpdate['predicted_assigned_to'] == '':
            incidentToUpdate['predicted_assigned_to'] = 'None'
        try:
            if incidentToUpdate['priority'] == '':
                incidentToUpdate['priority'] = 'None'
            notification_str =  ' is assigned to ' + incidentToUpdate[
                'predicted_assigned_to'] + ' with priority ' + incidentToUpdate[
                                   priority_field]
        except:
            incidentToUpdate['priority'] = 'None'
            notification_str =  ' is assigned to ' + incidentToUpdate[
                'predicted_assigned_to']

        resource_name = incidentToUpdate["predicted_assigned_to"]

        myTeamsmessage = pymsteams.connectorcard(MSteams_url)
        enable_notifications = list(MongoDBPersistence.assign_enable_tbl.find({}, {"sms_enabled": 1,
                                                                                   "call_enabled": 1,
                                                                                   "whatsapp_enabled": 1,
                                                                                   "msteams_enabled": 1,
                                                                                   "twilio_enabled": 1}))
        logging.info(f"notificatione enabled : {enable_notifications}")
        sms = enable_notifications[0]["sms_enabled"]
        twilio = enable_notifications[0]['twilio_enabled']
        call = enable_notifications[0]["call_enabled"]
        whatsapp = enable_notifications[0]["whatsapp_enabled"]
        msteams = enable_notifications[0]["msteams_enabled"]

        if (msteams == "true"):
            myTeamsmessage.text(notification_str)
            myTeamsmessage.send()

            #personal chat code
            try:               
                TENANT_ID = config["Notification"]["TENANT_ID"]
                CLIENT_ID = config["Notification"]["CLIENT_ID"]
                AUTHORITY = ""+config["Notification"]["AUTHORITY"] + TENANT_ID
                print("tenant,---------",TENANT_ID,AUTHORITY)
                #Metioned Scopes permission should be enabled in azure.
                SCOPES = [
                    'Files.ReadWrite.All',
                    'Sites.ReadWrite.All',
                    'User.Read',
                    'User.ReadBasic.All','User.Export.All','Chat.ReadWrite','Chat.Create','Chat.Read','Chat.ReadBasic','ChatMessage.Read','ChatMessage.Send']
                #storing token in cache and copying it to token_cache.bin file
                #if oken_cache.bin file already present ,it will deserialzie and use that for next run
                cache = msal.SerializableTokenCache()
                if os.path.exists('token_cache.bin'):
                    logging.info("%s----------------inside token_cache "%RestService.timestamp())
                    print("----------------inside token_cache")
                    with open('token_cache.bin', 'r') as f:
                        cache.deserialize(f.read())

                with open('token_cache.bin', 'w') as f:
                    atexit.register(lambda: f.write(cache.serialize()) if cache.has_state_changed else None)
                app = msal.PublicClientApplication(CLIENT_ID,authority=AUTHORITY, token_cache=cache)            
                accounts = app.get_accounts()
                result = None
                if len(accounts) > 0:
                    result = app.acquire_token_silent(SCOPES, account=accounts[1])

                if result is None:
                    flow = app.initiate_device_flow(scopes=SCOPES)
                    logging.info("%s Flow-----: %s"%(RestService.timestamp(),flow))
                    print("FLOW------",flow)
                    if 'user_code' not in flow:
                        raise Exception('Failed to create device flow')
                    print(flow['message'])
                    result = app.acquire_token_by_device_flow(flow)
                    print("result-----",result)
                    logging.info("%s result-----: %s"%(RestService.timestamp(),result))
                    access_token=''

                if 'access_token' in result:
                    access_token=result['access_token']
                    print('access_token: ',access_token)    
                    logging.info("%s access_token : %s"%(RestService.timestamp(),access_token))                 
                else:
                    raise Exception('no access token in result')
                                  
                chat_id = list(MongoDBPersistence.resource_details_tbl.find({"resource_name" :resource_name }, {"msteams_chat_id": 1 }))
                print("chat_id----------" ,chat_id)
                logging.info("%s chat_id :%s"%(RestService.timestamp(),chat_id))
                base_url=""+config["Notification"]["base_url"]
                endpoint=base_url+chat_id[0]['msteams_chat_id']+'/messages'
                #
                snow_list = list(MongoDBPersistence.customer_tbl.find({'CustomerID': 1},{"SNOWInstance":1,"_id": 0}))
                print(type(snow_list))
                for i in snow_list:
                    dev_instance_name=i['SNOWInstance']
                number=incidentToUpdate[ticket_id_field_name]
                href="https://%s.service-now.com/nav_to.do?uri=/incident.do?sysparm_query=number=%s"%(dev_instance_name,number)
                logging.info("%s ticket url: %s"%(RestService.timestamp(),href))
                print("href------",href)
                #
                data={
                    "body": {
                          "contentType": "html",
                          "content": "<a href=%s>%s</a>%s"%(href,number,notification_str)
                       
                    }
                    }                                                                      
                access_token_id=access_token
                headers={'Authorization':'Bearer ' + access_token_id}               
                response=requests.request("POST",endpoint,headers=headers,json=data)
                print("response----------",response)
                logging.info("%s  chat sent with response: %s"%(RestService.timestamp(),response))
                print(response.json())
            except Exception as e:
                logging.error("%s error in sending msg to personal chat :%s" %(RestService.timestamp(),e))
                print("error in sending msg to personal chat",e)

        if call == "true" or whatsapp == "true" or sms == "true":
            contact_number_dict = list(MongoDBPersistence.resource_details_tbl.find(
                {"resource_name": resource_name}, {"contact_no": 1}))
            cont_no = contact_number_dict[0]["contact_no"]

            account_sid = twilio_account_sid
            auth_token = twilio_authentication_token
            twilio_number = twilio_sms_call_from_number
            contact_number = str(cont_no)
            if not contact_number.__contains__(country_code) or len(contact_number) == 10:
                cont_no = country_code + contact_number

            target_number = cont_no

            client = Client(account_sid, auth_token)

            print(call, whatsapp, sms)
            if (twilio == "true"):
                if (sms == "true"):
                    print("inside sms")
                    message = client.messages.create(
                        body=notification_str,
                        from_=twilio_number,
                        to=target_number
                    )
                    print("sms sent-----------------", message.body)
                if (whatsapp == "true"):
                    time = list(
                        MongoDBPersistence.predicted_tickets_tbl.find({'number': incident_number},
                                                                      {"timestamp": 1}))
                    message_whatsapp = client.messages.create(
                        from_=twilio_whatsapp_from_number,
                        body=notification_str,
                        to='whatsapp:' + target_number)
                    print("whatsapp message sent-----------------", message_whatsapp.sid)
                if (call == "true"):
                    call = client.calls.create(url=twilio_call_record,
                                               to=target_number,
                                               from_=twilio_number)
