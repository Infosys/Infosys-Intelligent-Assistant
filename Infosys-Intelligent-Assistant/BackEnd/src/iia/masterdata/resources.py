__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

import configparser
import numpy as np
from iia.persistence.mongodbpersistence import MongoDBPersistence
from iia.restservice import RestService
from iia.masterdata.applications import ApplicationMasterData
from iia.masterdata.resourceavailability import ResourceAvailabilityMasterData
from bson import json_util
from datetime import timedelta, datetime, date
from flask import request
from dateutil import parser
from urllib.parse import unquote
import json
import pandas as pd
import io
import csv
import yaml
import importlib
from iia.masterdata.assignment import Assignment
from iia.utils.log_helper import get_logger, log_setup
from time import strftime
from dateutil.relativedelta import relativedelta

logging = get_logger(__name__)
app = RestService.getApp()


@app.route('/api/findpossibleassignees/<incident_number>/<assignment_group>', methods=['GET'])
def findpossibleassignees(incident_number, assignment_group):
    return ResourceMasterData.findpossibleassignees(incident_number, assignment_group)


@app.route('/api/assignee/', methods=["GET"])
def find_assignee():
    return ResourceMasterData.find_assignee()


@app.route('/api/uploadResourceDetails/<int:customer_id>/<team_name>', methods=["POST"])
def db_insert_resource_details(customer_id, team_name):
    return ResourceMasterData.db_insert_resource_details(customer_id, team_name)


@app.route('/api/getResourceDetails/<int:customer_id>/<team_name>', methods=['GET'])
def get_resource_details(customer_id, team_name):
    return ResourceMasterData.get_resource_details(customer_id, team_name)


@app.route('/api/getResourcesForTeam/<int:customer_id>/<team_name>', methods=['GET'])
def get_resources_forteam(customer_id, team_name):
    return ResourceMasterData.get_resources_forteam(customer_id, team_name)


@app.route('/api/deleteResource/<int:customer_id>/<team_name>/<resource_id>', methods=['DELETE'])
def delete_resource(customer_id, team_name, resource_id):
    return ResourceMasterData.delete_resource(customer_id, team_name, resource_id)


@app.route('/api/deleteAllResources/<int:customer_id>/<team_name>', methods=['DELETE'])
def delete_all_resources(customer_id, team_name):
    return ResourceMasterData.delete_all_resources(customer_id, team_name)


@app.route('/api/deleteAllRoasters/<int:customer_id>/<team_name>', methods=['DELETE'])
def delete_all_roasters(customer_id, team_name):
    return ResourceMasterData.delete_all_roasters(customer_id, team_name)


@app.route('/api/getResourceTeamNames', methods=['GET'])
def get_resource_team_names():
    return ResourceMasterData.get_resource_team_names()


@app.route('/api/updateResource/<int:customer_id>/<int:dataset_id>/<resource_id>', methods=['PUT'])
def update_resource_details(customer_id, dataset_id, resource_id):
    return ResourceMasterData.update_resource_details(customer_id, dataset_id, resource_id)


@app.route('/api/applicationResourceMapping', methods=['GET'])
def applicationResourceMapping():
    return ResourceMasterData.applicationResourceMapping()


@app.route('/api/getAllResourceNames', methods=['GET'])
def getAllResourceNames():
    return ResourceMasterData.getAllResourceNames()


@app.route('/api/getMappedResourceNames', methods=['GET'])
def getMappedResourceNames():
    return ResourceMasterData.getMappedResourceNames()


@app.route('/api/getAllMappedResourceNames', methods=['GET'])
def getAllMappedResourceNames():
    return ResourceMasterData.getAllMappedResourceNames()


@app.route('/api/getAllApplications', methods=['GET'])
def getAllApplications():
    return ResourceMasterData.getAllApplications()


@app.route('/api/updateApplication/<int:currentMonthDays>', methods=['PUT'])
def updateApplication(currentMonthDays):
    return ResourceMasterData.updateApplication(currentMonthDays)


@app.route('/api/deleteAnalystMapping/<customer_id>/<team_name>/<resource_id>', methods=['DELETE'])
def deleteAnalystMapping(customer_id, team_name, resource_id):
    return ResourceMasterData.deleteAnalystMapping(customer_id, team_name, resource_id)


@app.route('/api/deleteAllAnalystMapping', methods=['DELETE'])
def deleteAllAnalystMapping():
    return ResourceMasterData.deleteAllAnalystMapping()

@app.route('/api/getRoasterMappingCount/<int:customer_id>/<team_name>/<resource_name>/<month_name>', methods=['GET'])
def getRoasterMappingCount(customer_id, team_name,resource_name,month_name):
    return ResourceMasterData.getRoasterMappingCount(customer_id, team_name,resource_name,month_name)


@app.route('/api/getRosterScreenMappingDetails1/<int:currentMonthDays>', methods=['GET'])
def getRosterScreenMappingDetails1(currentMonthDays):
    return ResourceMasterData.getRosterScreenMappingDetails1(currentMonthDays)

@app.route('/api/getRosterScreenMappingDetails/<int:customer_id>/<team_name>/<int:currentMonthDays>/<resource_name>/<month_name>/<int:page_size>/<int:page_num>')
def getRosterScreenMappingDetails(customer_id, team_name, currentMonthDays, resource_name,month_name,page_size, page_num):
    return ResourceMasterData.getRosterScreenMappingDetails(customer_id, team_name, currentMonthDays,resource_name,month_name, page_size,page_num)


@app.route('/api/updateRosterMappingDetails/<int:currentMonthDays>', methods=['POST'])
def updateRosterMappingDetails(currentMonthDays):
    print("inside updateRosterMappingDetails")
    return ResourceMasterData.updateRosterMappingDetails(currentMonthDays)


@app.route('/api/saveAPplicationDetails', methods=['POST'])
def saveAPplicationDetails():
    return ResourceMasterData.saveAPplicationDetails()


@app.route('/api/saveResourceDetails', methods=['POST'])
def saveResourceDetails():
    return ResourceMasterData.saveResourceDetails()


@app.route('/api/getRosterUniqueShifts', methods=['GET'])
def getRosterUniqueShifts():
    return ResourceMasterData.getRosterUniqueShifts()


@app.route('/api/calculateResourceWorkload')
def calculate_resource_workload():
    return ResourceMasterData.calculate_resource_workload()


@app.route('/api/resourceInfoOfGroup/<assignment_group>')
def resource_info_of_group(assignment_group):
    return ResourceMasterData.resource_info_of_group(assignment_group)


class ResourceMasterData(object):
    '''
    classdocs
    '''

    def __init__(self, params):
        '''
        Constructor
        '''

    @staticmethod
    def assign_incident(incident_no, resource_id, assignment_group):

        logging.info(
            '%s: In "assign_incident", Trying to fetch documents from "rt_tickets_tbl"' % RestService.timestamp())
        incident_doc = MongoDBPersistence.rt_tickets_tbl.find_one({'Number': incident_no},
                                                                  {'_id': 0, 'State': 1, 'Task_type': 1, 'Priority': 1})
        if (incident_doc):
            status = incident_doc['State']
            task_type = incident_doc['Task_type']
            priority_fld_nme = None
            try:
                config = configparser.ConfigParser()
                config["DEFAULT"]['path'] = "config/"
                config.read(config["DEFAULT"]["path"] + "iia.ini")
                priority_fld_nme = config["Fields"]["priorityField"]
            except Exception as e:
                logging.info(
                    'No priority field name found from config file, taking default priority field name : priority')

            priority = incident_doc[priority_fld_nme].split()[2]
            logging.info('Trying to fetch documents from "tickets_weightage_tbl"')
            ticket_doc = MongoDBPersistence.tickets_weightage_tbl.find_one({
                "TicketType": task_type,
                "Priority": priority,
                "Status": status
            }, {
                "TicketWeigtage": 1,
                "_id": 0
            })
            if (ticket_doc):
                ticket_weightage = ticket_doc['TicketWeigtage']
                logging.info(
                    'Trying to fetch documents from "applicationDetails_tbl" for assign grp: %s' % assignment_group)
                app_doc = MongoDBPersistence.applicationDetails_tbl.find_one({'assignment_group': assignment_group},
                                                                             {"app_weightage": 1, 'application_name': 1,
                                                                              "_id": 0})
                if (app_doc):
                    app_weightage = app_doc['app_weightage']
                    app_name = app_doc['application_name']

                    # calculating workload based on App weightage and Ticket weightage
                    workload = app_weightage * ticket_weightage

                    logging.info(
                        'Checking for the existence of document from "resource_details_tbl" for assign grp: %s' % RestService.timestamp())
                    duplicate_doc = MongoDBPersistence.resource_details_tbl.find_one(
                        {'resource_id': resource_id, 'assignment_details.IncidentNo': incident_no})

                    if (duplicate_doc == None):
                        MongoDBPersistence.resource_details_tbl.update_one({
                            "resource_name": resource_id
                        }, {
                            '$push': {
                                'assignment_details': {
                                    "IncidentNo": incident_no, "Priority": priority,
                                    "ApplicationName": app_name, "ApplicationWeightage": app_weightage,
                                    "Status": status, 'task_type': task_type, "IsReduced": False, "workload": workload
                                }
                            }
                        })
                    else:
                        logging.info('Document already exist')
                        return ("Incident Number Already Exist")

                    # increasing the worklod when updating the assignment field
                    logging.info(
                        'Trying to update "resource_details_tbl" with details "calculated_workload" and "tickets_assigned"')
                    MongoDBPersistence.resource_details_tbl.update_one({
                        "resource_name": resource_id
                    }, {
                        '$set': {'$inc': {'calculated_workload': workload, 'tickets_assigned': 1}}
                    })

                    MongoDBPersistence.rt_tickets_tbl.update_one({'Number': incident_no},
                                                                 {'$set': {'State': 'Inprogress'}})
                else:
                    logging.error('Could not fetch documents from "applicationDetails_tbl"')
            else:
                logging.error('Could not fetch documents from "tickets_weightage_tbl"')
        else:
            logging.error('Could not get documents from "rt_tickets_tbl"')

    
    @staticmethod
    def update_workload(status, task_type, priority, ResourceAssigned, AssignmentGrp, incident_no):

        logging.info(
            '%s: In "update_workload()" method, Trying to fetch documents from "tickets_weightage_tbl"' % RestService.timestamp())
        ticket_doc = MongoDBPersistence.tickets_weightage_tbl.find_one({
            "ticket_type": task_type, "priority": priority, "status": 'InProgress'
        }, {
            "ticket_weightage": 1, "_id": 0
        })
        logging.info('Trying to fetch documents from "applicationDetails_tbl" for assign grp: %s' % AssignmentGrp)
        app_doc = MongoDBPersistence.applicationDetails_tbl.find_one({"assignment_group": AssignmentGrp},
                                                                     {"app_weightage": 1, "_id": 0})
        logging.info(f"ticket_doc:{ticket_doc}")
        logging.info(f"app_doc:{app_doc}")
        if (ticket_doc and app_doc):
            ticket_Weightage = float(ticket_doc['ticket_weightage'])
            app_Weightage = float(app_doc['app_weightage'])
            workload = ticket_Weightage * app_Weightage
            logging.info('Trying to update "TicketWeightage", "workload" in "rt_tickets_tbl"')
            logging.info(
                f'Updating workload: {workload}, ticket_Weightage: {ticket_Weightage} incident_no :{incident_no}')
            MongoDBPersistence.rt_tickets_tbl.update_one({
                "number": incident_no
            }, {
                '$set': {"TicketWeightage": ticket_Weightage, "workload": workload}
            })
        else:
            logging.error(
                'Could not found document either from "tickets_weightage_tbl" or from "applicationDetails_tbl"')

    @staticmethod
    def incident_workload_update(customer_id, dataset_id, incident_lst):

        logging.info('%s: In "incident_workload_update()" method')

        dataset_name = MongoDBPersistence.datasets_tbl.find_one({'CustomerID': customer_id, "DatasetID": dataset_id},
                                                                {'DatasetName': 1, '_id': 0})['DatasetName']
        customer_name = MongoDBPersistence.customer_tbl.find_one({'CustomerID': customer_id}, \
                                                                 {'CustomerName': 1, '_id': 0})['CustomerName']

        itsm_tool_name = MongoDBPersistence.itsm_details_tbl.find_one({}, {"_id": 0, "ITSMToolName": 1})["ITSMToolName"]
        class_name = customer_name + "_" + "".join(dataset_name.split()) + "_resources"
        module_name = "iia.custommasterdata." + class_name

        logging.info(
            "class name formed here is  %s and module is %s in incident_workload_update" % (class_name, module_name))
        priority_fld_nme = None
        try:
            config = configparser.ConfigParser()
            config["DEFAULT"]['path'] = "config/"
            config.read(config["DEFAULT"]["path"] + "iia.ini")
            priority_fld_nme = config["Fields"]["priorityField"]
        except Exception as e:
            logging.info('No priority field name found from config file, taking default priority field name : priority')

        try:
            module = importlib.import_module(module_name)
            class_ = getattr(module, class_name)
            response = class_.incident_workload_update(customer_id, dataset_id, incident_lst)
            logging.info(
                "Custom ITSM file called for incident_workload_update and returning the response to UI for LTFS %s" % (
                    response))
            return response
        except Exception as e:
            logging.error('%s: Error occurred: %s ' % (RestService.timestamp(), str(e)))
            logging.info("Error can be ignored, there is no customized ItSM module uploaded. \
            Going for basic ITSM configurations ")

        try:
            logging.info('Trying to fetch documents from "rt_tickets_tbl"')
            incident_doc_lst = list(MongoDBPersistence.rt_tickets_tbl.find({
                'number': {'$in': incident_lst},
                'DatasetID': dataset_id, 'CustomerID': customer_id
            }, {
                '_id': 0, 'state': 1, 'sys_class_name': 1, 'impact': 1,
                'assigned_to': 1, "assignment_group": 1, 'number': 1,
                priority_fld_nme: 1
            }))
            if (incident_doc_lst):
                logging.info('Trying to itrate throug all documents and to update the same')
                for incident_doc in incident_doc_lst:
                    status = incident_doc['state']
                    task_type = incident_doc['sys_class_name']
                    priority = None
                    if priority_fld_nme is not None:
                        priority = incident_doc[priority_fld_nme].split()[2]
                    ResourceAssigned = incident_doc['assigned_to']
                    AssignmentGrp = incident_doc['assignment_group']
                    incident_no = incident_doc['number']

                    ResourceMasterData.update_workload(status, task_type, priority, ResourceAssigned, AssignmentGrp,
                                                       incident_no)
            else:
                logging.error('Could not found document from "rt_tickets_tbl"')
        except TypeError as e:
            incident_doc = None
            logging.error('%s: Error: %s' % (RestService.timestamp(), str(e)))

    @staticmethod
    def calculate_resource_workload():
        resource_workload_doc = {}
        response = 'success'
        try:

            resource_details_lst = list(
                MongoDBPersistence.resource_details_tbl.find({}, {'_id': 0, 'resource_name': 1}))
            if (len(resource_details_lst) > 0):
                for resource_doc in resource_details_lst:
                    workload = []
                    resource_name = resource_doc['resource_name']
                    incident_lst = list(MongoDBPersistence.rt_tickets_tbl.find(
                        {"assigned_to": resource_name, "state": {"$ne": "closed"}}, {'workload': 1, "_id": 0}))
                    for incident_doc in incident_lst: workload.append(incident_doc["workload"])
                    resource_workload_doc[resource_name] = sum(workload)
            else:
                response = 'failure'
                logging.warn(
                    'From calculate_resource_workload(): There are no records in Resource and Roaster Collections!')

            return json_util.dumps({'response': response, 'resourceAndWorkload': resource_workload_doc})
        except Exception as e:
            logging.error('From calculate_resource_workload(): %s' % str(e))
        return json_util.dumps({'response': 'failure'})

    @staticmethod
    def resource_info_of_group(assignment_group):
        response = 'success'
        resourcesOfGroup = []
        roaster_doc = {}
        try:

            todays_date = str(date.today())
            tomo_date = str(date.today() + timedelta(days=1))
            time = datetime.now().time()
            now_date = todays_date + ' T' + str(format(time.hour, '02d')) + ':' + str(time.minute) + ':' + str(
                time.second)
            now = str(format(time.hour, '02d')) + ':' + str(time.minute) + ':' + str(time.second)
            start_date = todays_date + ' T00:00:00'
            end_date = tomo_date + ' T24:00:00'

            email_lst = MongoDBPersistence.roaster_tbl.find({'assignment_group': assignment_group}).distinct('email_id')
            resource_lst = list(MongoDBPersistence.resource_details_tbl.find({'email_id': {'$in': email_lst}},
                                                                             {'email_id': 1, 'resource_name': 1,
                                                                              '_id': 0}))
            print('email_lst', email_lst)
            print('resource_lst', resource_lst)
            print('---------------------')
            print(assignment_group)
            roaster_lst = list(MongoDBPersistence.roaster_tbl.aggregate([
                {'$match': {
                    'assignment_group': assignment_group, 'availability': True,
                    '$or': [
                        {'$and': [{'start_date': {'$gte': start_date}}, {'start_date': {'$lte': end_date}}]},
                        {'$and': [{'end_date': {'$gte': now_date}}, {'end_date': {'$lte': end_date}}]}
                    ]
                }}, {'$lookup': {
                    'from': 'TblResource', 'localField': 'email_id', 'foreignField': 'email_id', 'as': 'resource_lst'
                }}, {'$project': {
                    '_id': 0, 'email_id': 1, 'start_date': 1, 'end_date': 1,
                    'resource_name': {'$arrayElemAt': ['$resource_lst.resource_name', 0]}
                }}]))
            print('roaster_lst', roaster_lst)
            if (len(roaster_lst) > 0):
                for doc in roaster_lst:
                    to_roaster_doc = {}
                    email_id = doc['email_id']

                    if email_id not in roaster_doc.keys(): roaster_doc[email_id] = {}
                    if (tomo_date in doc['start_date']):
                        to_roaster_doc['tomo_start_date'] = doc.pop('start_date')
                        to_roaster_doc['tomo_end_date'] = doc.pop('end_date')
                    elif (todays_date not in doc['start_date']):
                        end_date = doc['end_date'].split(' ')[1][1:]
                        if (end_date > now):
                            to_roaster_doc['yes_start_date'] = doc.pop('start_date')
                            to_roaster_doc['end_date'] = doc.pop('end_date')
                    else:
                        to_roaster_doc['start_date'] = doc.pop('start_date')
                        to_roaster_doc['end_date'] = doc.pop('end_date')
                    for key, value in to_roaster_doc.items(): to_roaster_doc[key] = value.split(' ')[1][1:]

                    roaster_doc[email_id].update(to_roaster_doc)

                FMT = '%H:%M:%S'
                for resource_doc in resource_lst:
                    workload = []
                    availability = False
                    available_till = '__'
                    next_available_in = 'Not till Tomo'
                    resource_name = resource_doc['resource_name']
                    email_id = resource_doc['email_id']

                    incident_lst = list(MongoDBPersistence.rt_tickets_tbl.find(
                        {"assigned_to": resource_name, 'state': {'$ne': 'Closed'}}, {
                            'workload': 1, 'number': 1, 'state': 1, 'description': 1, 'category': 1, 'priority': 1,
                            "_id": 0
                        }))

                    if (incident_lst):
                        for incident_doc in incident_lst:
                            if (incident_doc['state'] != 'Closed'): workload.append(incident_doc["workload"])

                    roaster_keys = roaster_doc.keys()
                    if (email_id in roaster_keys):
                        roaster_doc_keys = roaster_doc[email_id].keys()
                        if ('start_date' in roaster_doc_keys):
                            start_time = roaster_doc[email_id]['start_date']
                            end_time = roaster_doc[email_id]['end_date']

                        if ('yes_start_date' in roaster_doc_keys):
                            end_time = roaster_doc[email_id]['end_date']
                            print(end_time, ' + ', now)
                            availability = True
                            time_diff = str(datetime.strptime(end_time, FMT) - datetime.strptime(now, FMT)).split(':')
                            available_till = (
                                time_diff[0] + 'h ' + time_diff[1] + 'm' if int(time_diff[0]) > 0 else time_diff[
                                                                                                           1] + 'm')

                        elif ('start_date' in roaster_doc_keys and now < start_time):
                            time_diff = str(datetime.strptime(start_time, FMT) - datetime.strptime(now, FMT)).split(':')
                            available_till = '__'
                            next_available_in = (
                                time_diff[0].strip() + 'h ' + time_diff[1] + 'm' if int(time_diff[0]) > 0 else
                                time_diff[1] + 'm')

                        elif ('start_date' in roaster_doc_keys and now >= start_time and now <= end_time):
                            availability = True
                            time_diff = str(datetime.strptime(end_time, FMT) - datetime.strptime(now, FMT)).split(':')
                            available_till = (
                                time_diff[0] + 'h ' + time_diff[1] + 'm' if int(time_diff[0]) > 0 else time_diff[
                                                                                                           1] + 'm')

                        if ('tomo_start_date' in roaster_doc_keys):
                            next_available_in = ''
                            start_time = roaster_doc[email_id]['tomo_start_date']

                            time_diff = str(datetime.strptime(start_time, FMT) - datetime.strptime(now, FMT))
                            if (len(time_diff.split(',')) > 1):
                                time_diff = time_diff.split(',')[1].split(':')
                            else:
                                next_available_in = '1 day '
                                time_diff = time_diff.split(':')
                            next_available_in += (
                                time_diff[0] + 'h ' + time_diff[1] + 'm' if int(time_diff[0]) > 0 else time_diff[
                                                                                                           1] + 'm')

                    resourcesOfGroup.append({
                        'name': resource_name, 'tickets_assigned': len(workload), 'workload': sum(workload),
                        'availability': availability,
                        'available_till': available_till, 'next_available_in': next_available_in,
                        'incidentsLst': incident_lst
                    })
            else:
                response = 'failure'
                logging.warn('From resource_info_of_group(): There are no records in Resource and Roaster Collections!')

            return json_util.dumps({'response': response, 'resourceOfGroup': resourcesOfGroup})
        except Exception as e:
            logging.error('From calculate_resource_workload(): %s' % str(e))
            logging.error(e, exc_info=True)
        return json_util.dumps({'response': 'failure'})

    @staticmethod
    def findpossibleassignees(incident_number, assignment_group):

        logging.info('%s: In "findpossibleassignees()" method')
        assignment_group = unquote(assignment_group)
        res = {}
        logging.info('calling "find_possibleassignees()" method of "ResourceMasterData"')
        obj = Assignment(possible_assignee=assignment_group)

        res['possibleAssignees'] = obj.assignmentRouting()
        ags = []
        ags.append({incident_number: assignment_group})
        logging.info('calling "find_assigneesForAssignmentGroups()" method of "ResourceMasterData"')
        obj = Assignment(possible_assignee_for_assignment=ags)
        res['predictedAssignedTo'] = obj.assignmentRouting()
        return json_util.dumps(res)

    @staticmethod
    def find_assignee():

        logging.info('%s: In "find_assignee()" method' % RestService.timestamp())
        assignment_group = request.args.get('assignment_group')
        incidentCount = 1

        if not (request.args.get('incidentCount')) is None:
            incidentCount = int(request.args.get('incidentCount'))
        logging.info(
            'Trying to call "find_assignees()" method with values assign grp: %s, incidentCount: %s' % assignment_group)
        return Assignment.find_assignees(assignment_group, incidentCount)

    @staticmethod
    def db_insert_resource_details(customer_id, team_name):

        logging.info('%s: In "db_insert_resource_details()" method' % RestService.timestamp())
        new_dataset_flag = 0
        file = request.files['resourceDetails']
        dataset_ = MongoDBPersistence.teams_tbl.find_one({"CustomerID": customer_id, "TeamName": team_name},
                                                         {"DatasetID": 1, "_id": 0})

        if (dataset_):
            # Dataset exist for the team
            logging.info('%s: Getting old dataset details.' % RestService.timestamp())
            dataset_id = dataset_["DatasetID"]
        else:
            # Newly adding the dataset
            logging.info('%s: Adding new dataset.' % RestService.timestamp())
            # getting max dataset id for the customer, so that new dataset id = old + 1
            dataset_dict = MongoDBPersistence.datasets_tbl.find_one(
                {"CustomerID": customer_id, "DatasetID": {"$exists": True}}, {'_id': 0, "DatasetID": 1},
                sort=[("DatasetID", -1)])

            if (dataset_dict):
                last_dataset_id = dataset_dict['DatasetID']
            else:
                last_dataset_id = 0
                logging.info('%s: Adding dataset for very first team.' % RestService.timestamp())

            # New dataset id for the customer
            dataset_id = last_dataset_id + 1

            new_dataset_dict = {}
            new_dataset_dict["DatasetID"] = dataset_id
            new_dataset_dict["DatasetName"] = team_name
            new_dataset_dict["CustomerID"] = customer_id
            new_dataset_flag = 1

        if not file:
            return "No file"
        elif (not '.csv' in str(file)):
            return "Upload csv file."
        stream = io.StringIO(file.stream.read().decode("latin-1"), newline=None)

        stream.seek(0)
        result = stream.read()

        # create list of dictionaries keyed by header row   k.lower()
        csv_dicts = [{k.lower(): v for k, v in row.items()} for row in csv.DictReader(result.splitlines(), \
                                                                                      skipinitialspace=True)]
        # duplicate skip id not working properly... it iterating alternativly
        for item in csv_dicts:
            item.update({"CustomerID": customer_id})
            item.update({"DatasetID": dataset_id})
            item.update({"TrainingFlag": 0})

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
            logging.info('%s: Trying to insert records into TblResource...' % RestService.timestamp())
            for resource_doc in json_data:
                MongoDBPersistence.resource_details_tbl.update_one(
                    {'email_id': resource_doc['email_id'], 'DatasetID': dataset_id}, {'$set': resource_doc},
                    upsert=True)
            logging.info('%s: Completed with insertion of resource data...' % RestService.timestamp())

            if (new_dataset_flag):
                logging.info('%s: Trying to insert new dataset into TblDataset...' % RestService.timestamp())
                MongoDBPersistence.datasets_tbl.insert_one(new_dataset_dict)
                logging.info('%s: Trying to update TblTeams with Dataset details...' % RestService.timestamp())
                MongoDBPersistence.teams_tbl.update_one({'CustomerID': customer_id, "TeamName": team_name},
                                                        {"$set": {"DatasetID": dataset_id}}, upsert=False)

            logging.info('%s: Records inserted successfully.' % RestService.timestamp())
            resp = "success"

        except Exception as e:
            logging.error('%s: Error occurred: %s ' % (RestService.timestamp(), str(e)))
            logging.error(
                '%s: Possible error: Data format in csv not matching with database constarints.(unique key & not null)' % RestService.timestamp())
            resp = 'failure'
        logging.info('%s: success ' % RestService.timestamp())
        return resp

    @staticmethod
    def get_resource_details(customer_id, team_name):

        logging.info('%s: In "get_resource_details()" method' % RestService.timestamp())
        try:
            logging.info('Trying to get documents from "teams_tbl" for team: %s' % team_name)
            team_doc = MongoDBPersistence.teams_tbl.find_one({'TeamName': team_name, 'DatasetID': {'$exists': True}},
                                                             {'_id': 0, 'DatasetID': 1})

            if (team_doc != None):
                resource_lst = []
                dataset_id = team_doc['DatasetID']
                logging.info('Trying to get documents from "resource_details_tbl"')
                resource_lst = list(
                    MongoDBPersistence.resource_details_tbl.find({'CustomerID': customer_id, 'DatasetID': dataset_id},
                                                                 {'_id': 0}).sort('resource_name', 1))
                # --Calculating current workload for resource----
                workload = []
                for resource_doc in resource_lst:
                    tickets_assigned = 0
                    incident_lst = list(MongoDBPersistence.rt_tickets_tbl.find(
                        {"assigned_to": resource_doc['resource_name'], "user_status": "Approved",
                         "state": {"$ne": "closed"}}, {'workload': 1, "_id": 0}))
                    for incident_doc in incident_lst:
                        workload.append(incident_doc["workload"])
                        tickets_assigned = tickets_assigned + 1
                    resource_doc['current_workload'] = round(sum(workload), 3)
                    resource_doc['tickets_assigned'] = tickets_assigned
                    workload = []
            else:
                resource_lst = []
                logging.error('Could not get documents from "teams_tbl"')
        except Exception as e:
            logging.error('%s: Error: %s' % (RestService.timestamp(), str(e)))

        return (json_util.dumps(resource_lst))

    @staticmethod
    def get_resources_forteam(customer_id, team_name):
        logging.info('%s: In "get_resource_details()" method' % RestService.timestamp())
        try:
            logging.info('Trying to get documents from "teams_tbl" for team: %s' % team_name)
            team_doc = MongoDBPersistence.teams_tbl.find_one({'TeamName': team_name, 'DatasetID': {'$exists': True}},
                                                             {'_id': 0, 'DatasetID': 1})

            if (team_doc != None):
                resource_lst = []
                dataset_id = team_doc['DatasetID']
                logging.info('Trying to get documents from "resource_details_tbl"')
                resource_lst = list(
                    MongoDBPersistence.resource_details_tbl.find({'CustomerID': customer_id, 'DatasetID': dataset_id},
                                                                 {'_id': 0, 'resource_name': 1}).sort('resource_name',
                                                                                                      1))
                resource_lst = [resource['resource_name'] for resource in resource_lst]
            else:
                resource_lst = []
                logging.error('Could not get documents from "teams_tbl"')
        except Exception as e:
            logging.error('%s: Error: %s' % (RestService.timestamp(), str(e)))

        return (json_util.dumps(resource_lst))

    def delete_resource(customer_id, team_name, resource_id):

        logging.info('%s: In "delete_resource()" method')
        try:
            logging.info('Trying to get documents from "teams_tbl"')
            team_doc = MongoDBPersistence.teams_tbl.find_one({'TeamName': team_name, 'DatasetID': {'$exists': True}},
                                                             {'_id': 0, 'DatasetID': 1})

            if (team_doc != None):
                dataset_id = team_doc['DatasetID']
                logging.info('Trying to get documents from "resource_details_tbl"')
                resource_doc = MongoDBPersistence.resource_details_tbl.find_one(
                    {'CustomerID': customer_id, 'DatasetID': dataset_id, 'resource_id': resource_id},
                    {'_id': 0, 'resource_name': 1})
                logging.info('Trying to delete one document from "resource_details_tbl"')
                MongoDBPersistence.resource_details_tbl.delete_one(
                    {'CustomerID': customer_id, 'DatasetID': dataset_id, 'resource_id': resource_id})
                logging.info('Trying to delete multiple documents from "roaster_tbl"')
                MongoDBPersistence.roaster_tbl.delete_many({'CustomerID': customer_id, 'DatasetID': dataset_id,
                                                            'resource_name': resource_doc['resource_name']})
            else:
                logging.error('Could not get documents from "teams_tbl"')
        except Exception as e:
            logging.error('%s: Error: ' % (RestService.timestamp(), str(e)))
            return ('failure')

        return 'success'

    @staticmethod
    def delete_all_resources(customer_id, team_name):

        logging.info('%s: In "delete_all_resources()" method' % RestService.timestamp())
        try:
            logging.info('Trying to get document from "teams_tbl" for team: %s' % team_name)
            team_doc = MongoDBPersistence.teams_tbl.find_one({'TeamName': team_name, 'DatasetID': {'$exists': True}},
                                                             {'_id': 0, 'DatasetID': 1})
            if (team_doc != None):
                dataset_id = team_doc['DatasetID']
                logging.info('Trying to delete multiple documents from "resource_details_tbl"')
                MongoDBPersistence.resource_details_tbl.delete_many(
                    {'CustomerID': customer_id, 'DatasetID': dataset_id})
                logging.info('Trying to call "delete_all_roasters()" mehtod')
                delete_all_roasters(customer_id, team_name)
            else:
                logging.error('Could not get documents from "teams_tbl"')
        except Exception as e:
            logging.error('%s: Error: %s' % (RestService.timestamp(), str(e)))
            return 'failure'
        return 'success'

    @staticmethod
    def delete_all_roasters(customer_id, team_name):

        logging.info('%s: In "delete_all_roasters()" method' % RestService.timestamp())
        try:
            logging.info('Trying to get document from "teams_tbl" for team: %s' % team_name)
            team_doc = MongoDBPersistence.teams_tbl.find_one({'TeamName': team_name, 'DatasetID': {'$exists': True}},
                                                             {'_id': 0, 'DatasetID': 1})
            if (team_doc != None):
                dataset_id = team_doc['DatasetID']
                print("DatasetID------------------------>", dataset_id)
                logging.info('Trying to delete multiple documents from "roaster_tbl"')
                MongoDBPersistence.roaster_tbl.delete_many({'CustomerID': customer_id, 'DatasetID': dataset_id})
                MongoDBPersistence.roster_mapping_tbl.delete_many({'DatasetID': dataset_id})
                MongoDBPersistence.application_analyst_mapping_tbl.delete_many({'DatasetID': dataset_id})
            else:
                logging.error('Could not get documents from "teams_tbl"')

        except Exception as e:
            logging.error('%s: Error: %s' % (RestService.timestamp(), str(e)))
            return ('failure')
        return 'success'

    @staticmethod
    def get_resource_team_names():
        resource_doc = MongoDBPersistence.resource_details_tbl.find_one({}, {'_id': 0, 'CustomerID': 1, 'DatasetID': 1})

        if (resource_doc):
            team = MongoDBPersistence.teams_tbl.find_one(
                {"CustomerID": resource_doc['CustomerID'], "DatasetID": resource_doc['DatasetID']},
                {'_id': 0, 'TeamName': 1})['TeamName']
            return (team);

        return ('no team')

    @staticmethod
    def update_resource_details(customer_id, dataset_id, resource_id):

        logging.info('%s: In "update_resource_details()" method' % RestService.timestamp())
        resource_doc = request.get_json()
        try:
            logging.info('Trying to get document from "teams_tbl"')
            team_doc = MongoDBPersistence.teams_tbl.find_one({'CustomerID': customer_id, 'DatasetID': dataset_id})
            if (team_doc != None):
                if ('email_id' in resource_doc):
                    logging.info('Trying to get document from "resource_details_tbl"')
                    email_id_doc = MongoDBPersistence.resource_details_tbl.find_one({
                        'CustomerID': customer_id, 'DatasetID': dataset_id, 'resource_id': resource_id
                    }, {'_id': 0, 'email_id': 1})

                    email_id = email_id_doc['email_id']
                    logging.info('Trying to update "roaster_tbl"')
                    MongoDBPersistence.roaster_tbl.update_many({'email_id': email_id},
                                                               {'$set': {'email_id': resource_doc['email_id']}})
                logging.info('Trying to update "reasource_details_tbl"')
                MongoDBPersistence.resource_details_tbl.update_one({
                    'CustomerID': customer_id, 'DatasetID': dataset_id, 'resource_id': resource_id
                }, {
                    '$set': resource_doc
                })
            else:
                logging.error('Could not get document from "teams_tbl"')

        except Exception as e:
            logging.error('%s: Error: %s' % (RestService.timestamp(), str(e)))
            return ('failure')

        return 'success'

    @staticmethod
    def applicationResourceMapping():

        try:
            records = list(
                MongoDBPersistence.application_analyst_mapping_tbl.find({}, {"_id": 0}).sort('resource_name', 1))
            records = sorted(records, key=lambda i: (i['resource_name'].lower()))
            records_final = []
            for dict_ in records:
                resourcedetails = list(
                    MongoDBPersistence.resource_details_tbl.find({'resource_name': dict_['resource_name']},
                                                                 {"_id": 0, "CustomerID": 1, "DatasetID": 1}))
                dict_['CustomerID'] = list(set([i["CustomerID"] for i in resourcedetails]))
                dict_['DatasetID'] = list(set([i["DatasetID"] for i in resourcedetails]))
                records_final.append(dict_)
        except Exception as e:
            return (e)

        return json_util.dumps(records_final)

    @staticmethod
    def getAllResourceNames():

        try:
            records = list(MongoDBPersistence.resource_details_tbl.find({},
                                                                        {"_id": 0, "email_id": 1, "resource_name": 1,
                                                                         "resource_id": 1}).sort('resource_name', 1))
            records = sorted(records, key=lambda i: (i['resource_name'].lower()))
        except Exception as e:
            return (e)

        return json_util.dumps(records)

    @staticmethod
    def getMappedResourceNames():

        try:
            records = list(MongoDBPersistence.application_analyst_mapping_tbl.find({}, {"_id": 0, "email_id": 1,
                                                                                        "resource_name": 1,
                                                                                        "resource_id": 1}).sort(
                'resource_name', 1))
            records = sorted(records, key=lambda i: (i['resource_name'].lower()))
        except Exception as e:
            return (e)

        return json_util.dumps(records)

    @staticmethod
    def getAllMappedResourceNames():

        try:
            records = list(MongoDBPersistence.application_analyst_mapping_tbl.find({}, {"_id": 0, "email_id": 1,
                                                                                        "resource_name": 1,
                                                                                        "resource_id": 1}).sort(
                'resource_name', 1))
            
            records = sorted(records, key=lambda i: (i['resource_name'].lower()))
        except Exception as e:
            return (e)

        return json_util.dumps(records)

    @staticmethod
    def getAllApplications():

        applications_list = []
        try:
            records = list(MongoDBPersistence.applicationDetails_tbl.find({}, {"_id": 0, "assignment_group": 1}).sort(
                'assignment_group', 1))

            for item in records:
                applications_list.append(item["assignment_group"])
            
        except Exception as e:
            return (e)

        return json_util.dumps(applications_list)

    @staticmethod
    def updateApplication(currentMonthDays):

        mapping_doc = request.get_json()

        print("mapping doc", mapping_doc)
       
        ## get email id from roster table based on resource id and add it to mapping_doc json
        email_id_doc = list(MongoDBPersistence.resource_details_tbl.find({"resource_id": mapping_doc["resource_id"]},
                                                                         {"email_id": 1, "DatasetID": 1, "_id": 0}))
        emailid = email_id_doc[0]['email_id']
        datasetid = email_id_doc[0]['DatasetID']
        mapping_doc['email_id'] = emailid
        mapping_doc['DatasetID'] = datasetid
        # new start
        listApp1 = list(
            MongoDBPersistence.application_analyst_mapping_tbl.find({"resource_name": mapping_doc["resource_name"]},
                                                                    {"resource_group": 1}))
        res_group1 = []
        if (listApp1):
            listdoc1 = listApp1[0]
            res_group1 = listdoc1['resource_group']
            print("mappings before updation.....", res_group1)
        MongoDBPersistence.application_analyst_mapping_tbl.update_many({"resource_id": mapping_doc["resource_id"]},
                                                                       {'$set': mapping_doc}, upsert=True)
        listApp = list(
            MongoDBPersistence.application_analyst_mapping_tbl.find({"resource_name": mapping_doc["resource_name"]},
                                                                    {"resource_group": 1}))
        if (listApp):
            listdoc = listApp[0]
            res_group = listdoc['resource_group']
            print("mappings after updation........", res_group)

        new_app = []
        for i in res_group:
            if (i not in res_group1):
                new_app.append(i)

        if (listApp1 and listApp):
            ## For adding roster of newly added assignment group in the mapping.
            roster_mapping = list(MongoDBPersistence.roster_mapping_tbl.find({"email_id": mapping_doc["email_id"]}))
            db_data = list(MongoDBPersistence.application_analyst_mapping_tbl.find({}, {"_id": 0}))
            for item in roster_mapping:
                now = datetime.now()
                date = now.date().strftime('%Y/%m/%d')
                for dbitem in db_data:
                    if (item["email_id"] == dbitem["email_id"]):
                        if ((item["start_date"] <= date <= item["end_date"]) or (item["start_date"] >= date)):
                            item["resource_group"] = new_app
                            print("Roaster Mapping---", item)
                            result = ResourceMasterData.insertDBShiftDetails([item], currentMonthDays,
                                                                             deleteRosterData=[])
                            logging.info(
                                "Finding rosters with date greater or equal to today's date for the new assignment group added")
                        else:
                            print("date not matching")
                            logging.info("date not matching - roster date is less than today's date")
            print("Roster mapping....", roster_mapping)

            ## For deleting roster of removed assignment group from mapping.
            for k in res_group1:
                if (k not in res_group):
                    MongoDBPersistence.roaster_tbl.delete_many(
                        {"email_id": mapping_doc["email_id"], "application_name": k})
        
        return "success"

    @staticmethod
    def deleteAnalystMapping(customer_id, team_name, resourceId):

        try:
            logging.info(
                '%s: Trying to get documents from "teams_tbl" for team: %s' % (RestService.timestamp(), team_name))
            team_doc = MongoDBPersistence.teams_tbl.find_one({'TeamName': team_name, 'DatasetID': {'$exists': True}},
                                                             {'_id': 0, 'DatasetID': 1})
            if (team_doc != None):
                dataset_id = team_doc['DatasetID']
            MongoDBPersistence.application_analyst_mapping_tbl.delete_one(
                {'DatasetID': dataset_id, "resource_id": resourceId})
            email_id = MongoDBPersistence.resource_details_tbl.find_one({"resource_id": resourceId}, {"email_id": 1})
            MongoDBPersistence.roster_mapping_tbl.delete_many({"email_id": email_id["email_id"]})
            MongoDBPersistence.roaster_tbl.delete_many({"email_id": email_id["email_id"]})
        except Exception as ex:
            print("exception in deleteAnalystMapping...", ex)
        return "success"

    @staticmethod
    def deleteAllAnalystMapping():

        try:
            MongoDBPersistence.application_analyst_mapping_tbl.delete_many({})

            MongoDBPersistence.roster_mapping_tbl.delete_many({})
            MongoDBPersistence.roaster_tbl.delete_many({})
        except Exception as ex:
            print("exception in deleteAllAnalystMapping...", ex)
        return "success"

    
    @staticmethod
    def getRosterScreenMappingDetails(customer_id, team_name, currentMonthDays, resource_name, month_name, page_size,
                                      page_num):
        log_setup()
        result = []
        try:
            team_doc = MongoDBPersistence.teams_tbl.find_one({'TeamName': team_name, 'DatasetID': {'$exists': True}},
                                                             {'_id': 0, 'DatasetID': 1})
            dataset_id = 0
            if (team_doc != None):
                dataset_id = team_doc['DatasetID']

            skips = page_size * (page_num - 1)
            print("skips:", skips)
            datetime_object = datetime.strptime(month_name, "%B")
            c_month = datetime_object.month
            if c_month < 10:
                current_month = "0" + str(c_month)
            else:
                current_month = str(datetime_object.month)

            current_year = strftime('%Y')
            current_year = str(current_year)
            temp_date = '01'

            search_date = current_year + '/' + current_month + '/' + temp_date
            end_date = (datetime.strptime(search_date, "%Y/%m/%d") + relativedelta(months=1)).strftime("%Y/%m/%d")
            
            if (resource_name != "All"):
                res = list(MongoDBPersistence.roster_mapping_tbl.find(
                    {"DatasetID": dataset_id, "resource_name": resource_name, "start_date": {"$gte": search_date},
                     "end_date": {"$lte": end_date}}))
            else:
                res = list(MongoDBPersistence.roster_mapping_tbl.find(
                    {"DatasetID": dataset_id, "start_date": {"$gte": search_date},
                     "end_date": {"$lte": end_date}}).sort('resource_name', 1))
                
            print("table res--:", res)
            l = []
            for i in res:
                if i not in l:
                    l.append(i)
                    
            j = 0
            for i in range(skips, len(l)):
                if j < page_size:
                    result.append(l[i])
                    j = j + 1
                if j == 10:
                    break

            for record in result:
                date_form = parser.parse(record["start_date"])
                date_form1 = parser.parse(record["end_date"])

                d0 = date_form
                d1 = date_form1
                delta = (d1 - d0)

                startIndex = date_form.day
                endindex = date_form1.day
                list_shift = []
                if ('list_shift' in record.keys() and record["list_shift"] is not None and len(
                        record["list_shift"]) > 0):
                    list_shift = record["list_shift"]
                else:
                    list_shift = [''] * int(currentMonthDays)
                for i in range(0, int(currentMonthDays)):
                    if (i >= startIndex - 1 and i <= endindex - 1):
                        list_shift[i] = record["resource_shift"]
                    else:
                        list_shift[i] = ''

                if ('weekoff' in record.keys() and record["weekoff"] is not None and len(record["weekoff"]) > 0):
                    weekoffdates = record["weekoff"]
                    for dateentry in weekoffdates:
                        date_form = parser.parse(dateentry)
                        startIndex = date_form.day
                        for i in range(0, int(currentMonthDays)):
                            if (i == startIndex - 1):
                                list_shift[i] = "H"
                record["list_shift"] = list_shift


        except Exception as ex:
            print("exception in adding roasterdetails...", ex)

        result = sorted(result, key=lambda i: (i['resource_name'].lower()))
        return json.dumps(result, default=str)
        

    @staticmethod
    def getRoasterMappingCount(customer_id, team_name, resource_name, month_name):
        try:
            team_doc = MongoDBPersistence.teams_tbl.find_one({'TeamName': team_name, 'DatasetID': {'$exists': True}},
                                                             {'_id': 0, 'DatasetID': 1})
            dataset_id = 0
            if (team_doc != None):
                dataset_id = team_doc['DatasetID']

            datetime_object = datetime.strptime(month_name, "%B")
            c_month = datetime_object.month
            if c_month < 10:
                current_month = "0" + str(c_month)
            else:
                current_month = str(datetime_object.month)

            current_year = strftime('%Y')
            current_year = str(current_year)
            temp_date = '01'

            search_date = current_year + '/' + current_month + '/' + temp_date
            end_date = (datetime.strptime(search_date, "%Y/%m/%d") + relativedelta(months=1)).strftime("%Y/%m/%d")
            
            if (resource_name != "All"):
                roaster_mapping_count = MongoDBPersistence.roster_mapping_tbl.find(
                    {"DatasetID": dataset_id, "resource_name": resource_name, "start_date": {"$gte": search_date},
                     "end_date": {"$lte": end_date}}).count()
            else:
                roaster_mapping_count = MongoDBPersistence.roster_mapping_tbl.find(
                    {"DatasetID": dataset_id, "start_date": {"$gte": search_date},
                     "end_date": {"$lte": end_date}}).count()
        except Exception as ex:
            print("exception in getting count", ex)
            roaster_mapping_count = 0

        print("roaster_mapping_count", roaster_mapping_count)
        resp = json_util.dumps({'count': roaster_mapping_count})
        return resp

    @staticmethod
    def getRosterScreenMappingDetails1(currentMonthDays):

        result = []
        try:
            result = list(MongoDBPersistence.roster_mapping_tbl.find({}, {"_id": 0}).sort('resource_name', 1))
            members_lst = []
            unique_resource = list(MongoDBPersistence.roster_mapping_tbl.aggregate(
                [{"$group": {"_id": {"resource_name": "$resource_name", "list_shift": "$list_shift"}}},
                 {"$sort": {"_id.resource_name": 1, "_id.list_shift": 1}}]))
            for i in unique_resource:
                members_lst.append(i["_id"])

            for record in result:
                date_form = parser.parse(record["start_date"])
                date_form1 = parser.parse(record["end_date"])

                d0 = date_form
                d1 = date_form1
                delta = (d1 - d0)

                startIndex = date_form.day
                endindex = date_form1.day
                list_shift = []
                if ('list_shift' in record.keys() and record["list_shift"] is not None and len(
                        record["list_shift"]) > 0):
                    list_shift = record["list_shift"]
                else:
                    list_shift = [''] * int(currentMonthDays)
                for i in range(0, int(currentMonthDays)):
                    if (i >= startIndex - 1 and i <= endindex - 1):
                        list_shift[i] = record["resource_shift"]
                    else:
                        list_shift[i] = ''

                if ('weekoff' in record.keys() and record["weekoff"] is not None and len(record["weekoff"]) > 0):
                    weekoffdates = record["weekoff"]
                    for dateentry in weekoffdates:
                        date_form = parser.parse(dateentry)
                        startIndex = date_form.day
                        for i in range(0, int(currentMonthDays)):
                            if (i == startIndex - 1):
                                list_shift[i] = "H"
                record["list_shift"] = list_shift


        except Exception as ex:
            print("exception in deleteAnalystMapping...", ex)

        result = sorted(result, key=lambda i: (i['resource_name'].lower()))
        return json_util.dumps(members_lst)

    @staticmethod
    def deletingExtraRows(day_tomorrow, curMonthDays, day, email_id, shift, year, month):
        try:
            with open('./config/shift_roaster_config.yaml') as roaster_file:
                roaster_config = yaml.safe_load(roaster_file)
            print("deletingExtraRows----")
            if (int(day_tomorrow) <= curMonthDays):
                if (len(str(day)) == 1):
                    day = '0' + str(day)
                if (len(str(day_tomorrow)) == 1):
                    day_tomorrow = '0' + str(day_tomorrow)
                if (len(str(month)) == 1):
                    month = '0' + str(month)

                date = year + '-' + str(month) + '-' + str(day) + ' T'
                date_tomorrow = year + '-' + str(month) + '-' + str(day_tomorrow) + ' T'

            elif (int(day_tomorrow) > curMonthDays):
                day_tomorrow = str(1)
                prv_month = str(month)
                month = int(month) + 1
                if (len(str(day)) == 1):
                    day = '0' + str(day)
                if (len(str(day_tomorrow)) == 1):
                    day_tomorrow = '0' + str(day_tomorrow)
                if (len(str(month)) == 1):
                    month = '0' + str(month)
                if (len(str(prv_month)) == 1):
                    prv_month = '0' + str(prv_month)
                date = year + '-' + str(prv_month) + '-' + str(day) + ' T'
                date_tomorrow = year + '-' + str(month) + '-' + str(day_tomorrow) + ' T'

            if (shift == 'G'):
                start_date = date + roaster_config[shift]['start_time']
                end_date = date + roaster_config[shift]['end_time']
            elif (shift == 'O'):
                start_date = date + roaster_config[shift]['start_time']
                end_date = date + roaster_config[shift]['end_time']
            elif (shift == 'S'):
                start_date = date + roaster_config[shift]['start_time']
                end_date = date + roaster_config[shift]['end_time']
            elif (shift in ['F', 'M']):
                start_date = date + roaster_config[shift]['start_time']
                end_date = date + roaster_config[shift]['end_time']
            elif (shift == 'N'):
                start_date = date + roaster_config[shift]['start_time']
                print("start_date", start_date)
                end_date = date_tomorrow + roaster_config[shift]['end_time']
                print("end_date", end_date)
            elif (shift == 'U'):
                start_date = date + roaster_config[shift]['start_time']
                end_date = date_tomorrow + roaster_config[shift]['end_time']
            print("start_date,end_date,shift,email_id", start_date, end_date, shift, email_id)
            toBeDeletedRos1 = list(MongoDBPersistence.roaster_tbl.aggregate([
                {
                    '$match': {
                        '$and': [
                            {'start_date': {'$eq': start_date}},
                            {'end_date': {'$eq': end_date}}
                        ],
                        'shift': shift,
                        'availability': True,

                        "email_id": email_id, 'CustomerID': 1,
                        'DatasetID': 1
                    }
                }
            ]))
            print("toBeDeletedRos1---,", toBeDeletedRos1)
            if (len(toBeDeletedRos1) > 0):
                for ele in toBeDeletedRos1:
                    id = ele["_id"]
                    MongoDBPersistence.roaster_tbl.delete_one({"_id": id})
        except Exception as ex:
            print("exception in delete...", ex)
            logging.info("exception in delete", ex)
        return "Success"

    @staticmethod
    def updateRosterMappingDetails(currentMonthDays):

        try:
           
            roster_mapping = request.get_json()["modifiedRosterDetails"]
            deleted_data = request.get_json()["deleteRosterList"]
           
            for record in roster_mapping:
                print("......record.....", record)
                if (
                        "prev_enddate" in record.keys() and "prev_startdate" in record.keys() and "prev_resource_shift" in record.keys()):
                    MongoDBPersistence.roster_mapping_tbl.delete_many({
                        'resource_id': record["resource_id"],
                        'resource_shift': record["prev_resource_shift"],
                        'email_id': record["email_id"],
                        'start_date': record["prev_startdate"],
                        'end_date': record["prev_enddate"]
                    })

                    ## if the start date and end dates are different from previous start date and end date and shift is different from previous shift
                    if ((record["start_date"] > record["prev_startdate"] and record["end_date"] < record[
                        "prev_enddate"] and record["resource_shift"] != record["prev_resource_shift"])
                            or (record["end_date"] < record["prev_enddate"] and record["resource_shift"] != record[
                                "prev_resource_shift"])
                            or (record["start_date"] > record["prev_startdate"] and record["resource_shift"] != record[
                                "prev_resource_shift"])
                            or (record["end_date"] > record["prev_enddate"] and record["resource_shift"] != record[
                                "prev_resource_shift"])
                            or (record["start_date"] < record["prev_startdate"] and record["resource_shift"] != record[
                                "prev_resource_shift"])
                            or (record["start_date"] < record["prev_startdate"] and record["end_date"] > record[
                                "prev_enddate"] and record["resource_shift"] != record["prev_resource_shift"])):

                        start_date1 = record["prev_startdate"]
                        end_date1 = record["prev_enddate"]
                        k = pd.date_range(start_date1, end_date1, freq='d').strftime('%Y-%m-%d').tolist()
                        for date in k:
                            date = date + ' 00:00:00'
                            date_form = parser.parse(date)
                            d = date_form
                            month = d.month
                            year = str(d.year)
                            day = d.day
                            curMonthDays = ResourceMasterData.numberOfDays(int(year), month)
                            email_id = record["email_id"]
                            shift = record["prev_resource_shift"]
                            day_tomorrow = str((day) + 1)
                            ResourceMasterData.deletingExtraRows(day_tomorrow, curMonthDays, day, email_id, shift, year,
                                                                 month)

                    ## if the start date is greater than previous start date and end date is less than previous end date
                    elif (record["start_date"] > record["prev_startdate"] and record["end_date"] < record[
                        "prev_enddate"]):
                        starting_date1 = record["prev_startdate"]
                        ending_date1 = record["start_date"]
                        k1 = pd.date_range(starting_date1, ending_date1, freq='d').strftime('%Y-%m-%d').tolist()
                        del k1[-1]
                        for date in k1:
                            date = date + ' 00:00:00'
                            # print("date is", date)
                            date_form = parser.parse(date)
                            d = date_form
                            month = d.month
                            year = str(d.year)
                            day = d.day
                            curMonthDays = ResourceMasterData.numberOfDays(int(year), month)
                            email_id = record["email_id"]
                            shift = record["resource_shift"]
                            day_tomorrow = str((day) + 1)

                            ResourceMasterData.deletingExtraRows(day_tomorrow, curMonthDays, day, email_id, shift, year,
                                                                 month)

                        starting_date2 = record["end_date"]
                        ending_date2 = record["prev_enddate"]
                        k2 = pd.date_range(starting_date2, ending_date2, freq='d').strftime('%Y-%m-%d').tolist()
                        del k2[0]
                        for date in k2:
                            date = date + ' 00:00:00'
                            date_form = parser.parse(date)
                            d = date_form
                            month = d.month
                            year = str(d.year)
                            day = d.day
                            curMonthDays = ResourceMasterData.numberOfDays(int(year), month)
                            email_id = record["email_id"]
                            shift = record["resource_shift"]
                            day_tomorrow = str((day) + 1)

                            ResourceMasterData.deletingExtraRows(day_tomorrow, curMonthDays, day, email_id, shift, year,
                                                                 month)


                    ## if the start date is greater than previous start date
                    elif (record["start_date"] > record["prev_startdate"]):
                        starting_date = record["prev_startdate"]
                        ending_date = record["start_date"]
                        k = pd.date_range(starting_date, ending_date, freq='d').strftime('%Y-%m-%d').tolist()
                        del k[-1]
                        for date in k:
                            date = date + ' 00:00:00'
                            date_form = parser.parse(date)
                            d = date_form
                            month = d.month
                            year = str(d.year)
                            day = d.day
                            curMonthDays = ResourceMasterData.numberOfDays(int(year), month)
                            email_id = record["email_id"]
                            shift = record["resource_shift"]
                            day_tomorrow = str((day) + 1)

                            ResourceMasterData.deletingExtraRows(day_tomorrow, curMonthDays, day, email_id, shift, year,
                                                                 month)


                    ## if end date is less than prev end date
                    elif (record["end_date"] < record["prev_enddate"]):
                        starting_date = record["end_date"]
                        ending_date = record["prev_enddate"]
                        k = pd.date_range(starting_date, ending_date, freq='d').strftime('%Y-%m-%d').tolist()
                        del k[0]
                        for date in k:
                            date = date + ' 00:00:00'
                            date_form = parser.parse(date)
                            d = date_form
                            month = d.month
                            year = str(d.year)
                            day = d.day
                            curMonthDays = ResourceMasterData.numberOfDays(int(year), month)
                            email_id = record["email_id"]
                            shift = record["resource_shift"]
                            day_tomorrow = str((day) + 1)

                            ResourceMasterData.deletingExtraRows(day_tomorrow, curMonthDays, day, email_id, shift, year,
                                                                 month)



                    ## if no change in start date and end date and shift is different from previous one.
                    elif (record["end_date"] == record["prev_enddate"] and record["start_date"] == record[
                        "prev_startdate"] and record["resource_shift"] != record["prev_resource_shift"]):
                        starting_date = record["start_date"]
                        ending_date = record["end_date"]
                        k = pd.date_range(starting_date, ending_date, freq='d').strftime('%Y-%m-%d').tolist()
                        for date in k:
                            date = date + ' 00:00:00'
                            date_form = parser.parse(date)
                            d = date_form
                            month = d.month
                            year = str(d.year)
                            day = d.day
                            curMonthDays = ResourceMasterData.numberOfDays(int(year), month)
                            email_id = record["email_id"]
                            shift = record["prev_resource_shift"]
                            day_tomorrow = str((day) + 1)

                            ResourceMasterData.deletingExtraRows(day_tomorrow, curMonthDays, day, email_id, shift, year,
                                                                 month)
                datasetid = list(MongoDBPersistence.resource_details_tbl.find({'email_id': record["email_id"]},
                                                                              {'_id': 0, "DatasetID": 1}))
                dataset_id = datasetid[0]['DatasetID']
                MongoDBPersistence.roster_mapping_tbl.update_one({
                    'resource_id': record["resource_id"],
                    'resource_shift': record["resource_shift"],
                    'email_id': record["email_id"],
                    'start_date': record["start_date"],
                    'end_date': record["end_date"],
                    'DatasetID': dataset_id
                }, {
                    '$set': record
                }, upsert=True)

            for record in deleted_data:
                MongoDBPersistence.roster_mapping_tbl.delete_many({
                    'resource_id': record["resource_id"],
                    'resource_shift': record["resource_shift"],
                    'email_id': record["email_id"],
                    'start_date': record["start_date"],
                    'end_date': record["end_date"]
                })

            db_data = list(MongoDBPersistence.application_analyst_mapping_tbl.find({}, {"_id": 0}))
            roster_data = []
            for item in roster_mapping:
                roster_row = {}
                for dbitem in db_data:
                    if (item["email_id"] == dbitem["email_id"]):
                        item["resource_group"] = dbitem["resource_group"]

            result = ResourceMasterData.insertDBShiftDetails(roster_mapping, currentMonthDays, deleted_data)

            if (result == "Success"):
                return "success"
            elif (result == "failure"):
                return "failure"
        except Exception as e:
            print("upload failed...", e)
            return "failure"

        return "success"

    @staticmethod
    def numberOfDays(y, m):

        leap = 0
        if y % 400 == 0:
            leap = 1
        elif y % 100 == 0:
            leap = 0
        elif y % 4 == 0:
            leap = 1
        if m == 2:
            return 28 + leap
        list = [1, 3, 5, 7, 8, 10, 12]
        if m in list:
            return 31
        return 30

    @staticmethod
    def insertDBShiftDetails(roster_data, currentMonthDays, deleteRosterData):

        try:
            if (roster_data):
                with open('./config/shift_roaster_config.yaml') as roaster_file:
                    roaster_config = yaml.safe_load(roaster_file)

                for item in roster_data:
                    print("Item.....", item)
                    if "weekoff" not in item.keys():
                        item["weekoff"] = []
                    print("Item After.....", item)
                    if 'resource_group' in item.keys():

                        date_form = parser.parse(item["start_date"])
                        date_form1 = parser.parse(item["end_date"])
                        weekoffdates = item["weekoff"]

                        d0 = date_form
                        d1 = date_form1

                        delta = timedelta(days=1)
                        startIndex = date_form.day
                        endindex = date_form1.day
                        month = date_form.month
                        year = str(date_form.year)
                       
                        for assign_grp in item["resource_group"]:
                            # for day in range(startIndex,endindex+1):
                            d0 = date_form
                            d1 = date_form1
                            while d0 <= d1:
                                month = d0.month
                                year = str(d0.year)
                                day = d0.day
                                
                                curMonthDays = ResourceMasterData.numberOfDays(int(year), month)
                                document = {}
                                email_id = item["email_id"]
                                shift = item["resource_shift"]
                                datasetid = list(MongoDBPersistence.resource_details_tbl.find({'email_id': email_id},
                                                                                              {'_id': 0,
                                                                                               "DatasetID": 1}))
                                dataset_id = datasetid[0]['DatasetID']
                                document['shift'] = shift
                                document['CustomerID'] = 1
                                document['DatasetID'] = dataset_id
                                document['availability'] = True
                                document['application_name'] = assign_grp
                                document['assignment_group'] = assign_grp
                                day_tomorrow = str((day) + 1)
                                date = ''
                                if (int(day_tomorrow) <= curMonthDays):
                                    if (len(str(day)) == 1):
                                        day = '0' + str(day)
                                    if (len(str(day_tomorrow)) == 1):
                                        day_tomorrow = '0' + str(day_tomorrow)
                                    if (len(str(month)) == 1):
                                        month = '0' + str(month)
                                    date = year + '-' + str(month) + '-' + str(day) + ' T'
                                    date_tomorrow = year + '-' + str(month) + '-' + str(day_tomorrow) + ' T'


                                elif (int(day_tomorrow) > curMonthDays):
                                    day_tomorrow = str(1)
                                    prv_month = str(month)
                                    month = int(month) + 1
                                    
                                    if (len(str(day)) == 1):
                                        day = '0' + str(day)
                                    if (len(str(day_tomorrow)) == 1):
                                        day_tomorrow = '0' + str(day_tomorrow)
                                    if (len(str(month)) == 1):
                                        month = '0' + str(month)
                                    if (len(str(prv_month)) == 1):
                                        prv_month = '0' + str(prv_month)
                                    date = year + '-' + str(prv_month) + '-' + str(day) + ' T'
                                    date_tomorrow = year + '-' + str(month) + '-' + str(day_tomorrow) + ' T'

                                if (shift in ['M', 'O']):
                                    document['support_type'] = roaster_config[shift]['support_type']
                                else:
                                    document['support_type'] = roaster_config[shift]['support_type']

                                if (shift == 'G'):
                                    start_date = date + roaster_config[shift]['start_time']
                                    document['start_date'] = start_date
                                    end_date = date + roaster_config[shift]['end_time']
                                    document['end_date'] = end_date
                                elif (shift == 'O'):
                                    start_date = date + roaster_config[shift]['start_time']
                                    document['start_date'] = start_date
                                    end_date = date + roaster_config[shift]['end_time']
                                    document['end_date'] = end_date
                                elif (shift == 'S'):
                                    start_date = date + roaster_config[shift]['start_time']
                                    document['start_date'] = start_date
                                    end_date = date + roaster_config[shift]['end_time']
                                    document['end_date'] = end_date
                                elif (shift in ['F', 'M']):
                                    start_date = date + roaster_config[shift]['start_time']
                                    document['start_date'] = start_date
                                    end_date = date + roaster_config[shift]['end_time']
                                    document['end_date'] = end_date
                                elif (shift == 'N'):
                                    # --date from today nyt to tommorrow morning--
                                    start_date = date + roaster_config[shift]['start_time']
                                    document['start_date'] = start_date
                                    end_date = date_tomorrow + roaster_config[shift]['end_time']
                                    document['end_date'] = end_date
                                elif (shift == 'U'):
                                    start_date = date + roaster_config[shift]['start_time']
                                    document['start_date'] = start_date
                                    end_date = date_tomorrow + roaster_config[shift]['end_time']
                                    document['end_date'] = end_date
                                
                                MongoDBPersistence.roaster_tbl.update_one({
                                    'CustomerID': 1,
                                    'DatasetID': 1,
                                    'email_id': email_id,
                                    'start_date': start_date,
                                    'end_date': end_date,
                                    'assignment_group': assign_grp,
                                    'application_name': assign_grp
                                }, {
                                    '$set': document
                                }, upsert=True)
                                d0 += delta
                            
                            # weekoff changes - START
                            for date in weekoffdates:
                                email_id = item["email_id"]
                                date_form_weekoff = parser.parse(date)
                                day = date_form_weekoff.day
                                month = date_form_weekoff.month
                                year = str(date_form_weekoff.year)
                                if (len(str(day)) == 1):
                                    day = '0' + str(day)
                                if (len(str(month)) == 1):
                                    month = '0' + str(month)

                                date = year + '-' + str(month) + '-' + str(day) + ' T'

                                start_date = date + '00:00:00'
                                end_date = date + '24:00:00'

                                document = {}
                                email_id = item["email_id"]
                                document['shift'] = "H"
                                document['CustomerID'] = 1
                                document['DatasetID'] = 1
                                document['availability'] = False
                                document['start_date'] = start_date
                                document['end_date'] = end_date
                                document['application_name'] = assign_grp
                                document['assignment_group'] = assign_grp

                                MongoDBPersistence.roaster_tbl.update_one({
                                    'CustomerID': 1,
                                    'DatasetID': 1,
                                    'email_id': email_id,
                                    'start_date': start_date,
                                    'end_date': end_date,
                                    'assignment_group': assign_grp,
                                    'application_name': assign_grp,
                                    'availability': False,
                                    'shift': "H"

                                }, {
                                    '$set': document
                                }, upsert=True)

                                toBeDeleted = []
                                toBeDeleted_nightshift = []
                                toBeDeleted = list(MongoDBPersistence.roaster_tbl.aggregate([
                                    {
                                        '$match': {
                                            '$and': [
                                                {'start_date': {'$gte': start_date}},
                                                {'end_date': {'$lte': end_date}},
                                                {'shift': {'$nin': ['N', 'U']}},
                                            ], 'availability': True, 'assignment_group': assign_grp,
                                            'application_name': assign_grp, "email_id": email_id, 'CustomerID': 1,
                                            'DatasetID': 1
                                        }
                                    }
                                ]))
                                dayafter = date_form_weekoff + timedelta(days=1)
                                print("DayAfter....", dayafter)
                                dayafterDay = dayafter.day
                                nextMonth = date_form_weekoff.month
                                if (len(str(dayafterDay)) == 1):
                                    day = '0' + str(dayafterDay)
                                if (len(str(nextMonth)) == 1):
                                    nextMonth = '0' + str(nextMonth)
                                dateNext = year + '-' + str(nextMonth) + '-' + str(dayafterDay) + ' T'

                                for i in weekoffdates:
                                    datetimeobject = datetime.strptime(i, '%Y/%m/%d')
                                    new_format = datetimeobject.strftime('%Y-%m-%d')
                                    date_form_weekoff = parser.parse(i)
                                    day = date_form_weekoff.day
                                    start_dateN = new_format + ' T21:00:00'
                                    start_dateU = new_format + ' T18:00:00'
                                    dayafter = date_form_weekoff + timedelta(days=1)
                                    dayafterDay = dayafter.day
                                    nextMonth = date_form_weekoff.month
                                    if (len(str(dayafterDay)) == 1):
                                        dayafterDay = '0' + str(dayafterDay)
                                    if (len(str(nextMonth)) == 1):
                                        nextMonth = '0' + str(nextMonth)
                                    dateNextN = year + '-' + str(nextMonth) + '-' + str(dayafterDay) + ' T06:00:00'
                                    dateNextU = year + '-' + str(nextMonth) + '-' + str(dayafterDay) + ' T03:00:00'
                                    toBeDeleted_nightshift1 = []

                                    toBeDeleted_nightshiftN = list(MongoDBPersistence.roaster_tbl.aggregate([
                                        {
                                            '$match': {
                                                '$and': [
                                                    {'start_date': {'$eq': start_dateN}},
                                                    {'end_date': {'$eq': dateNextN}},
                                                    {'shift': {'$eq': 'N'}},
                                                    {'availability': {'$eq': True}},
                                                ],

                                                "email_id": email_id, 'CustomerID': 1,
                                                'DatasetID': 1
                                            }
                                        }
                                    ]))


                                    toBeDeleted_nightshiftU = list(MongoDBPersistence.roaster_tbl.aggregate([
                                        {
                                            '$match': {
                                                '$and': [
                                                    {'start_date': {'$eq': start_dateU}},
                                                    {'end_date': {'$eq': dateNextU}},
                                                    {'shift': {'$eq': 'U'}},
                                                    {'availability': {'$eq': True}},
                                                ], "email_id": email_id, 'CustomerID': 1,
                                                'DatasetID': 1
                                            }
                                        }
                                    ]))

                                    toBeDeleted_nightshift1 = toBeDeleted_nightshiftN + toBeDeleted_nightshiftU
                                    toBeDeleted_nightshift = toBeDeleted_nightshift + toBeDeleted_nightshift1

                                # previous day to handle previous day NIght or Usa ('U') shift - START
                                daybefore = date_form_weekoff - timedelta(days=1)
                                daybeforeDay = daybefore.day
                                prevMonth = date_form_weekoff.month
                                if (len(str(daybeforeDay)) == 1):
                                    day = '0' + str(daybeforeDay)
                                if (len(str(prevMonth)) == 1):
                                    prevMonth = '0' + str(prevMonth)
                                datePrev = year + '-' + str(prevMonth) + '-' + str(daybeforeDay) + ' T'
                                datePrev_start_date = datePrev + '00:00:00'
                                datePrev_end_date = datePrev + '24:00:00'

                                prevdayHolidayShift = list(MongoDBPersistence.roaster_tbl.aggregate([
                                    {
                                        '$match': {
                                            '$and': [
                                                {'start_date': {'$gte': datePrev_start_date}},
                                                {'end_date': {'$eq': datePrev_end_date}},
                                                {'shift': 'H'},
                                            ], 'assignment_group': assign_grp,
                                            'application_name': assign_grp, "email_id": email_id, 'CustomerID': 1,
                                            'DatasetID': 1
                                        }
                                    }
                                ]))
                                if (len(prevdayHolidayShift) == 0):
                                    print(".......inside if...........")
                                    MongoDBPersistence.roaster_tbl.update_one({
                                        'CustomerID': 1,
                                        'DatasetID': 1,
                                        'email_id': email_id,
                                        'start_date': start_date,
                                        'end_date': end_date,
                                        'assignment_group': assign_grp,
                                        'application_name': assign_grp,
                                        'availability': False,
                                        'shift': "H"

                                    }, {
                                        '$set': {"start_date": date + '06:00:00', "end_date": date + '24:00:00'}
                                    }, upsert=True)

                                    # previous day to handle previous day NIght or Usa ('U') shift - END

                                toBeDeleted = toBeDeleted + toBeDeleted_nightshift

                                print(toBeDeleted)
                                if (len(toBeDeleted) > 0):
                                    print("##########", toBeDeleted)
                                    for ele in toBeDeleted:
                                        id = ele["_id"]
                                        print(id)
                                        MongoDBPersistence.roaster_tbl.delete_one({"_id": id})

            toBeDeletedRos = []
            
            for record in deleteRosterData:

                date_form = parser.parse(record["start_date"])
                date_form1 = parser.parse(record["end_date"])
                weekoffdates1 = record["weekoff"]
                # weekoff changes - END
                d0 = date_form
                d1 = date_form1
                delta = timedelta(days=1)
                startIndex = date_form.day
                endindex = date_form1.day
                month = date_form.month
                year = str(date_form.year)

                d0 = date_form
                d1 = date_form1
                while d0 <= d1:
                    month = d0.month
                    year = str(d0.year)
                    day = d0.day
                    curMonthDays = ResourceMasterData.numberOfDays(int(year), month)
                    document = {}
                    email_id = record["email_id"]
                    shift = record["resource_shift"]

                    day_tomorrow = str((day) + 1)

                    if (int(day_tomorrow) <= curMonthDays):
                        if (len(str(day)) == 1):
                            day = '0' + str(day)
                        if (len(str(day_tomorrow)) == 1):
                            day_tomorrow = '0' + str(day_tomorrow)
                        if (len(str(month)) == 1):
                            month = '0' + str(month)

                        date = year + '-' + str(month) + '-' + str(day) + ' T'
                        date_tomorrow = year + '-' + str(month) + '-' + str(day_tomorrow) + ' T'


                    elif (int(day_tomorrow) > curMonthDays):
                        day_tomorrow = str(1)
                        prv_month = str(month)
                        month = int(month) + 1
                        
                        if (len(str(day)) == 1):
                            day = '0' + str(day)
                        if (len(str(day_tomorrow)) == 1):
                            day_tomorrow = '0' + str(day_tomorrow)
                        if (len(str(month)) == 1):
                            month = '0' + str(month)
                        if (len(str(prv_month)) == 1):
                            prv_month = '0' + str(prv_month)
                        date = year + '-' + str(prv_month) + '-' + str(day) + ' T'
                        date_tomorrow = year + '-' + str(month) + '-' + str(day_tomorrow) + ' T'

                    if (shift == 'G'):
                        start_date = date + roaster_config[shift]['start_time']
                        document['start_date'] = start_date
                        end_date = date + roaster_config[shift]['end_time']
                    elif (shift == 'O'):
                        start_date = date + roaster_config[shift]['start_time']
                        end_date = date + roaster_config[shift]['end_time']
                    elif (shift == 'S'):
                        start_date = date + roaster_config[shift]['start_time']
                        end_date = date + roaster_config[shift]['end_time']
                    elif (shift in ['F', 'M']):
                        start_date = date + roaster_config[shift]['start_time']
                        end_date = date + roaster_config[shift]['end_time']
                    elif (shift == 'N'):
                        start_date = date + roaster_config[shift]['start_time']
                        end_date = date_tomorrow + roaster_config[shift]['end_time']
                    elif (shift == 'U'):
                        start_date = date + roaster_config[shift]['start_time']
                        end_date = date_tomorrow + roaster_config[shift]['end_time']


                    toBeDeletedRos = list(MongoDBPersistence.roaster_tbl.aggregate([
                        {
                            '$match': {
                                '$and': [
                                    {'start_date': {'$eq': start_date}},
                                    {'end_date': {'$eq': end_date}}
                                ],
                                'shift': shift,
                                'availability': True,

                                "email_id": email_id, 'CustomerID': 1,
                                'DatasetID': 1
                            }
                        }
                    ]))

                    toBeDeletedHolidayRos = []

                    TotalList = []
                    for i in weekoffdates1:
                        datetimeobject = datetime.strptime(i, '%Y/%m/%d')
                        new_format = datetimeobject.strftime('%Y-%m-%d')
                        start_date1 = new_format + ' T00:00:00'
                        end_date1 = new_format + ' T24:00:00'
                        start_date2 = new_format + ' T06:00:00'
                        end_date2 = new_format + ' T24:00:00'
                        TotalList1 = []

                        toBeDeletedHolidayRos1 = list(MongoDBPersistence.roaster_tbl.aggregate([
                            {
                                '$match': {
                                    '$and': [
                                        {'start_date': {'$eq': start_date1}},
                                        {'end_date': {'$eq': end_date1}},
                                        {'availability': {'$eq': False}},
                                        {'shift': {'$eq': 'H'}}
                                    ],

                                    "email_id": email_id, 'CustomerID': 1,
                                    'DatasetID': 1
                                }
                            }
                        ]))

                        toBeDeletedHolidayRos2 = list(MongoDBPersistence.roaster_tbl.aggregate([
                            {
                                '$match': {
                                    '$and': [
                                        {'start_date': {'$eq': start_date2}},
                                        {'end_date': {'$eq': end_date2}},
                                        {'availability': {'$eq': False}},
                                        {'shift': {'$eq': 'H'}}
                                    ],

                                    "email_id": email_id, 'CustomerID': 1,
                                    'DatasetID': 1
                                }
                            }
                        ]))

                        TotalList1 = toBeDeletedHolidayRos1 + toBeDeletedHolidayRos2
                        TotalList = TotalList + TotalList1

                    toBeDeletedRos = toBeDeletedRos + TotalList
                    if (len(toBeDeletedRos) > 0):
                        for ele in toBeDeletedRos:
                            id = ele["_id"]
                            MongoDBPersistence.roaster_tbl.delete_one({"_id": id})

                    d0 += delta

            return "Success"
        except Exception as e:
            print("exception occurred while saving the data", e)
            logging.info("Exception in insertDB shift details function%s" % e)
            return "failure"

    @staticmethod
    def getRosterUniqueShifts():

        result = None
        try:
            db_result = list(MongoDBPersistence.roster_shifts_tbl.find({}, {"_id": 0}))
            result = db_result[0]["shifts"]
        except Exception as ex:
            print("exception in deleteAnalystMapping...", ex)
        return json_util.dumps(result)

    @staticmethod
    def saveAPplicationDetails():

        try:
            application_data = request.get_json()["applicationDetails"]
            delete_app_data = request.get_json()["deleteAppList"]

            print("delete_app_data", delete_app_data)
            print("application data...", application_data)

            for record in application_data:
                record_to_update = MongoDBPersistence.applicationDetails_tbl.find_one({'record_id': record["record_id"],
                                                                                       'assignment_group': record[
                                                                                           'assignment_group'],
                                                                                       'app_name': record['app_name']})

                print("***************record to update*************")
                print(record_to_update)

                MongoDBPersistence.applicationDetails_tbl.update_one({'record_id': record["record_id"]
                                                                      },
                                                                     {'$set': record},
                                                                     upsert=True)

                currentApplication = MongoDBPersistence.applicationDetails_tbl.find_one(
                    {"record_id": record["record_id"]},
                    {"assignment_group": 1})

                if currentApplication.get("assignment_group"):
                    MongoDBPersistence.roaster_tbl.update_many(
                        {'assignment_group': currentApplication["assignment_group"]},
                        {'$set': {"assignment_group": record["assignment_group"],
                                  "application_name": record["assignment_group"]}
                         },
                        upsert=False)

                    MongoDBPersistence.roster_mapping_tbl.update_many(
                        {"resource_group": currentApplication["assignment_group"]},
                        {"$set": {"resource_group.$": record["assignment_group"]}})

                    MongoDBPersistence.application_analyst_mapping_tbl.update_many(
                        {"resource_group": currentApplication["assignment_group"]},
                        {"$set": {"resource_group.$": record["assignment_group"]}})

            # use appname and dataset id combination to delete
            if delete_app_data:
                for appdata in delete_app_data:
                    app_to_delete = appdata["assignment_group"]
                    MongoDBPersistence.application_analyst_mapping_tbl.update_many({}, {
                        '$pull': {"resource_group": appdata["assignment_group"]}})
                    MongoDBPersistence.roaster_tbl.delete_many({'assignment_group': app_to_delete})
                    app_analyst = MongoDBPersistence.application_analyst_mapping_tbl.find({}, {"resource_group": 1,
                                                                                               "email_id": 1})
                    for i in app_analyst:
                        if (len(i["resource_group"]) == 0):
                            MongoDBPersistence.roster_mapping_tbl.delete_many({'email_id': i["email_id"]})
                            MongoDBPersistence.application_analyst_mapping_tbl.delete_many({'email_id': i["email_id"]})
                    MongoDBPersistence.applicationDetails_tbl.delete_many(
                        {'assignment_group': appdata["assignment_group"],
                         'app_name': appdata["app_name"]}
                    )

            return "success"
        except Exception as e:
            print("error", e)
            return "Failure"

    @staticmethod
    def saveResourceDetails():

        try:
            print(request.get_json())
            print(len(request.get_json()["deleteResList"]))
            resource_data = request.get_json()["resourceDetails"]
            deleted_data = request.get_json()["deleteResList"]

            for record in resource_data:
                MongoDBPersistence.resource_details_tbl.update_one({'resource_id': record["resource_id"],
                                                                    'DatasetID': record["DatasetID"]},
                                                                   {'$set': record},
                                                                   upsert=True)

                currentEmailid = MongoDBPersistence.resource_details_tbl.find_one({"resource_id": record["resource_id"],
                                                                                   "DatasetID": record["DatasetID"]},
                                                                                  {"_id": 0,
                                                                                   "email_id": 1})

                if currentEmailid.get("email_id") and record.get("email_id"):
                    MongoDBPersistence.roaster_tbl.update_many({'email_id': currentEmailid["email_id"]},
                                                               {'$set': {"email_id": record["email_id"]}},
                                                               upsert=False)

                    MongoDBPersistence.roster_mapping_tbl.update_many({'email_id': currentEmailid["email_id"]},
                                                                      {'$set': {"email_id": record["email_id"],
                                                                                "resource_name": record[
                                                                                    "resource_name"]}
                                                                       },
                                                                      upsert=False)

                    MongoDBPersistence.application_analyst_mapping_tbl.update_many(
                        {'email_id': currentEmailid["email_id"]},
                        {'$set': {"email_id": record["email_id"],
                                  "resource_name": record["resource_name"]
                                  }
                         },
                        upsert=False)
            for resemail in deleted_data:
                # delete entry in analyst mapping table, rostertable, roster mapping table
                MongoDBPersistence.application_analyst_mapping_tbl.delete_many({'email_id': resemail})
                MongoDBPersistence.roaster_tbl.delete_many({'email_id': resemail})
                MongoDBPersistence.roster_mapping_tbl.delete_many({'email_id': resemail})
                MongoDBPersistence.resource_details_tbl.delete_many({'email_id': resemail})

            return "success"
        except Exception as e:
            print("Exception in save resource details...", e)
            return "Failure"