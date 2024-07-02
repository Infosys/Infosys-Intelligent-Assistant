__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

import numpy as np
from iia.persistence.mongodbpersistence import MongoDBPersistence
from iia.restservice import RestService
from iia.masterdata.applications import ApplicationMasterData
from iia.masterdata.resourceavailability import ResourceAvailabilityMasterData
import configparser
from bson import json_util
from iia.utils.log_helper import get_logger, log_setup

logging = get_logger(__name__)
from iia.masterdata.customers import CustomerMasterData

# default workload assignment
class WorkloadAssignment():
    def __init__(self, possible_assignee=None, possible_assignee_for_assignment=None):
        self.possible_assignee = possible_assignee
        self.possible_assignee_for_assignment = possible_assignee_for_assignment

    def find_possibleassignees(self):
        ()
        logging.info('%s: In "find_possibleassignees" method, argument - assign grp: %s' % (
            RestService.timestamp(), self.possible_assignee))
        customer_id = 1
        dataset_id = MongoDBPersistence.training_tickets_tbl.find_one({"CustomerID": customer_id})["DatasetID"]
        dataset_name = MongoDBPersistence.datasets_tbl.find_one({'CustomerID': customer_id, "DatasetID": dataset_id},
                                                                {'DatasetName': 1, '_id': 0})['DatasetName']
        customer_name = MongoDBPersistence.customer_tbl.find_one({'CustomerID': customer_id}, \
                                                                 {'CustomerName': 1, '_id': 0})['CustomerName']

        itsm_tool_name = MongoDBPersistence.itsm_details_tbl.find_one({}, {"_id": 0, "ITSMToolName": 1})["ITSMToolName"]

        app_lst = []
        resource_name_lst = []
        roaster_lst = []
        resource_lst = []
        res_names = []
        logging.info('Trying to call "getAppWeightage()" method of "ApplicationMasterData" to get "app_weightage"')
        logging.info(f"self.possible_assignee: {self.possible_assignee}")
        app_weightage = float(ApplicationMasterData.getAppWeightage(self.possible_assignee))
        logging.info('Trying to fetch documents from "applicationDetails_tbl"')
        app_lst = list(
            MongoDBPersistence.applicationDetails_tbl.find({'assignment_group': self.possible_assignee}, {"_id": 0}))
        logging.info(f"app_lst: {app_lst}")
        logging.info(
            'Trying to call "getRoasterList()" method of "ResourceAvailabilityMasterData" to get "roaster_lst"')
        roaster_lst = ResourceAvailabilityMasterData.getRoasterList(self.possible_assignee)
        logging.info(f"roaster_lst: {roaster_lst}")
        name_ticketcount = {}
        round_robin_flag = False
        doc = MongoDBPersistence.assign_enable_tbl.find_one({})
        if (doc['roundrobin_enabled'] == 'true'):
            round_robin_flag = True
        if round_robin_flag == True:
            for roaster_doc in roaster_lst:
                resource_name_lst.append(roaster_doc['resource_name'][0]['resource_name'])

            logging.info('Trying to fetch documents from "resource_details_tbl"')
            resource_lst = list(
                MongoDBPersistence.resource_details_tbl.find({'resource_name': {'$in': resource_name_lst}}))
            if (resource_lst):
                for resource_doc in resource_lst:
                    incident_lst = list(
                        MongoDBPersistence.rt_tickets_tbl.find({"assigned_to": resource_doc['resource_name']},
                                                               {'number': 1, "_id": 0}))
                    name_ticketcount[resource_doc['resource_name']] = len(incident_lst)

            data_sorted = {k: v for k, v in sorted(name_ticketcount.items(), key=lambda x: x[1])}
            res_names = list(data_sorted.keys())
            return res_names
        else:
            logging.info(f"app_weightage:{app_weightage}")
            logging.info(f"roaster_lst:{roaster_lst}")
            if ((app_weightage >= 0) and roaster_lst):
                for roaster_doc in roaster_lst:
                    logging.info(f"roaster_doc:{roaster_doc}")
                    resource_name_lst.append(roaster_doc['resource_name'][0]['resource_name'])

                # ------Newly Inserted ----------------------
                resource_choosen_lst = []
                logging.info('Trying to fetch documents from "resource_details_tbl"')
                resource_lst = list(
                    MongoDBPersistence.resource_details_tbl.find({'resource_name': {'$in': resource_name_lst}}))
                if (resource_lst):
                    # --Calculating current workload for resource----
                    workload = []
                    for resource_doc in resource_lst:
                        tickets_assigned = 0
                        resource_doc['current_workload'] = 0
                        resource_doc['tickets_assigned'] = 0
                        incident_lst = list(
                            MongoDBPersistence.rt_tickets_tbl.find({"assigned_to": resource_doc['resource_name']},
                                                                   {'workload': 1, "_id": 0}))
                        if (incident_lst):
                            for incident_doc in incident_lst:
                                workload.append(incident_doc["workload"])
                                tickets_assigned = tickets_assigned + 1
                            resource_doc['current_workload'] = sum(workload)

                            resource_doc['tickets_assigned'] = tickets_assigned
                            workload = []

                    for resource_doc in resource_lst:
                        availability_threshold_value = int(resource_doc['res_bandwidth']) / 100
                        if (resource_doc['current_workload'] <= (availability_threshold_value - app_weightage)):
                            resource_choosen_lst.append(resource_doc)

                    resource_lst = resource_choosen_lst
                    res_names = [''] * len(resource_lst)
                    k = 0
                    for res in resource_lst:
                        res_names[k] = res['resource_name']
                        k = k + 1
                else:
                    logging.error('Could not fetch documents from "resource_details_tbl"')
            else:
                logging.error(
                    'Could not found value Either from "getAppWeightage()" or from "getRoasterList()" for assign group: %s' % (
                        self.possible_assignee))
            logging.info(f"res_names: {res_names}")
            return res_names

    @staticmethod
    def find_roundrobin_assignees(assignment_group, incidentCount):
        ()
        logging.info('%s: in "def find_roundrobin_assignees" method, assign grp: %s, incident count: %s' % (
            RestService.timestamp(), assignment_group, incidentCount))
        try:
            resource_name_lst = []
            roaster_lst = []
            resource_lst = []
            assignments = []
            name_ticketcount = {}

            logging.info('calling "getRoasterList" method of "ApplicationMasterData"')
            roaster_lst = ResourceAvailabilityMasterData.getRoasterList(assignment_group)

            if (roaster_lst):
                for roaster_doc in roaster_lst:
                    resource_name_lst.append(roaster_doc['resource_name'][0]['resource_name'])
                logging.info('Trying to fetch documents from "resource_details_tbl"')
                resource_lst = list(MongoDBPersistence.resource_details_tbl.find({
                    'resource_name': {
                        '$in': resource_name_lst
                    }}, {
                    '_id': 0,
                    'resource_name': 1,
                }))

                if (resource_lst):
                    for resource_doc in resource_lst:
                        tickets_assigned = 0
                        workload = 0.0
                        incident_lst = list(
                            MongoDBPersistence.rt_tickets_tbl.find({"assigned_to": resource_doc['resource_name']},
                                                                   {"_id": 0, 'number': 1}))
                        name_ticketcount[resource_doc['resource_name']] = len(incident_lst)
                    data_sorted = {k: v for k, v in sorted(name_ticketcount.items(), key=lambda x: x[1])}

                    i = 0
                    assigned = True
                    assignments = []
                    while i < incidentCount and assigned:
                        assigned = False
                        try:
                            assignments.append({'resource_name': list(data_sorted.keys())[0]})
                            data_sorted[list(data_sorted.keys())[0]] = data_sorted[list(data_sorted.keys())[0]] + 1
                            data_sorted = {k: v for k, v in sorted(data_sorted.items(), key=lambda x: x[1])}

                        except Exception as e:
                            print("ex : 460", e)
                        i = i + 1
                        assigned = True

                        if i >= incidentCount:
                            break

                    if (i != incidentCount):
                        logging.info(
                            '%s: some of the assignment group cannot be assigned with assignee becoz, all resources having maximum bandwidth' % RestService.timestamp())
                    else:
                        logging.info('%s: all tickets are assigned with assignees!' % RestService.timestamp())
                else:
                    logging.error('Could not get documents from "resource_details_tbl"')
            else:
                logging.error('Could not get documents from "getRoasterList"')

        except Exception as e:
            logging.error("%s Here is an Exception %s" % (RestService.timestamp(), str(e)))
        return assignments

    @staticmethod
    def find_assignees(assignment_group, incidentCount, incident_tckts):
        ()
        logging.info('%s: in "find_assignees" method, assign grp: %s, incident count: %s' % (
            RestService.timestamp(), assignment_group, incidentCount))
        try:
            resource_name_lst = []
            roaster_lst = []
            resource_lst = []
            assignments = []

            # --Reading from Config file--
            try:
                config = configparser.ConfigParser()
                config['DEFAULT']['path'] = 'config/'
                config.read(config['DEFAULT']['path'] + 'iia.ini')
                priority_field = config['Fields']['priorityField']
            except Exception as e:
                logging.error(
                    'priorityField is not defined in "config/iia.ini" file. Define it for Assignee Prediction')
                priority_field = 'priority'
                logging.info('Taking default value as "priorityField"= priority.')

            logging.info('calling "getAppWeightage" method of "ApplicationMasterData"')
            app_weightage = float(ApplicationMasterData.getAppWeightage(assignment_group))
            logging.info('calling "getRoasterList" method of "ApplicationMasterData"')
            roaster_lst = ResourceAvailabilityMasterData.getRoasterList(assignment_group)

            if (roaster_lst):
                for roaster_doc in roaster_lst:
                    resource_name_lst.append(roaster_doc['resource_name'][0]['resource_name'])
                logging.info('Trying to fetch documents from "resource_details_tbl"')
                logging.info(f"resource_name_lst: {resource_name_lst}")
                resource_lst = list(MongoDBPersistence.resource_details_tbl.find({
                    'resource_name': {
                        '$in': resource_name_lst
                    }}, {
                    '_id': 0,
                    'resource_name': 1,
                    'res_bandwidth': 1
                }))

                logging.info(f"resource_lst: {resource_lst}")
                if (resource_lst):
                    for resource_doc in resource_lst:
                        tickets_assigned = 0
                        workload = 0.0
                        incident_lst = list(
                            MongoDBPersistence.rt_tickets_tbl.find({"assigned_to": resource_doc['resource_name']},
                                                                   {'workload': 1, "_id": 0}))
                        for incident_doc in incident_lst:
                            tickets_assigned = tickets_assigned + 1
                            workload = workload + float(incident_doc["workload"])

                        resource_doc['current_workload'] = workload
                        resource_doc['tickets_assigned'] = tickets_assigned
                    for res in resource_lst:
                        availability_threshold_value = int(res['res_bandwidth']) / 100
                        res['availableBandwidth'] = availability_threshold_value - res['current_workload']
                        res['incidents'] = []
                    i = 0
                    assigned = True
                    assignments = []
                    while i < incidentCount and assigned:
                        incident_no = incident_tckts[i]
                        incident_doc = MongoDBPersistence.rt_tickets_tbl.find_one({'number': incident_no},
                                                                                  {'_id': 0, 'state': 1,
                                                                                   priority_field: 1})
                        priority = incident_doc[priority_field].split()[2]
                        logging.info(f"priority: {priority}")
                        if priority == 'Moderate':
                            priority = 'Medium'
                        logging.info(f"priority: {priority}")
                        tckt_weightage_doc = MongoDBPersistence.tickets_weightage_tbl.find_one(
                            {'priority': priority, 'status': 'InProgress'}, {'_id': 0, 'ticket_weightage': 1})
                        if tckt_weightage_doc is not None:
                            tckt_weightage = float(tckt_weightage_doc['ticket_weightage'])
                        else:
                            logging.info(f"Ticket weightage not available for {priority}")
                            tckt_weightage = float(0.0001)

                        workload = float(app_weightage) * tckt_weightage
                        assigned = False
                        logging.info(f"app_weightage: {app_weightage}")
                        logging.info(f"tckt_weightage: {tckt_weightage}")
                        logging.info(f"workload: {workload}")
                        logging.info(f"resource_lst: {resource_lst}")
                        # --finding resource which is having more bandwidth--
                        res_hvg_mr_bandwidth = resource_lst[0]
                        for res in resource_lst:
                            if (res_hvg_mr_bandwidth['availableBandwidth'] < res['availableBandwidth']):
                                res_hvg_mr_bandwidth = res
                        logging.info(f"res_hvg_mr_bandwidth: {res_hvg_mr_bandwidth}")
                        res = res_hvg_mr_bandwidth
                        if i >= incidentCount:
                            break
                        if (res['availableBandwidth'] > workload):
                            res['availableBandwidth'] = round(res['availableBandwidth'] - workload, 4)
                            print('latest workload for selected resource : ', res['availableBandwidth'])
                            try:
                                assignments.append(res)
                            except Exception as e:
                                print("ex : 460", e)
                            i = i + 1
                            assigned = True

                    if (i != incidentCount):
                        logging.info(
                            '%s: some of the assignment group cannot be assigned with assignee becoz, all resources having maximum bandwidth' % RestService.timestamp())
                    else:
                        logging.info('%s: all tickets are assigned with assignees!' % RestService.timestamp())
                else:
                    logging.error('Could not get documents from "resource_details_tbl"')

            else:
                logging.error('Could not get documents from "getRoasterList"')
        except Exception as e:
            logging.error("%s Here is an Exception %s" % (RestService.timestamp(), str(e)))
            logging.info(e, exc_info=True)
        logging.info(f"assignments: {assignments}")
        return assignments

    def find_assigneesForAssignmentGroups(self):
        ()
        logging.info('%s: In "find_assigneesForAssignmentGroups" method' % RestService.timestamp())
        counts = dict()
        assign_grp_dict = dict()
        # Finding the resource name by iteration
        for ag_doc in self.possible_assignee_for_assignment:
            key = list(ag_doc.keys())[0]
            ag = ag_doc[key]
            if ag not in counts:
                counts[ag] = 1
                assign_grp_dict[ag] = [key]
            else:
                counts[ag] = counts[ag] + 1
                assign_grp_dict[ag].append(key)
        assignees = [''] * len(self.possible_assignee_for_assignment)

        try:
            logging.info('calling find_assignees function for each assignmnet group')
            for ag in counts.keys():

                round_robin_flag = False
                doc = MongoDBPersistence.assign_enable_tbl.find_one({})
                if (doc['roundrobin_enabled'] == 'true'):
                    round_robin_flag = True
                if round_robin_flag == True:
                    res = WorkloadAssignment.find_roundrobin_assignees(ag, counts[ag])
                else:
                    res = WorkloadAssignment.find_assignees(ag, counts[ag], assign_grp_dict[ag])
                if (res):
                    j = 0
                    for k in range(0, len(self.possible_assignee_for_assignment)):
                        ag_key = list(self.possible_assignee_for_assignment[k].keys())[0]
                        if self.possible_assignee_for_assignment[k][ag_key] == ag:
                            assignees[k] = res[j]['resource_name']
                            j = j + 1
                            if (j == len(res)):
                                j = 0
                else:
                    logging.info('empty assignees list for assign grp: %s' % ag)
        except Exception as e:
            logging.error('%s: Error: %s ' % (RestService.timestamp(), str(e)))
        return np.array(assignees)


# one by one mapping assignment
class OneByOneMappingAssignment():

    def __init__(self, customer_id, dataset_id, mapping_assignemnt):
        self.customer_id = customer_id
        self.dataset_id = dataset_id
        self.mapping_assignemnt = mapping_assignemnt

    def manualassignee(self):
        assignee_list = MongoDBPersistence.manual_assignee_tbl.find_one(
            {"CustomerID": self.customer_id, "DatasetID": self.dataset_id}, {"_id": 0, "MappingFields": 1})
        for i in assignee_list["MappingFields"]:
            if (i["AssignmentGroup"] == self.mapping_assignemnt):
                users = i["Users"]
                break
        print("Returning User list to front end")
        return (json_util.dumps(users))


### other methods also get implemented here :
class AssignmentAdapter():
    def __init__(self, resourceCount, applicationCount, mappingTableCount, customer_id=None, dataset_id=None, \
                 mapping_assignemnt=None, possible_assignee=None, possible_assignee_for_assignment=None):

        self.resourceCount = resourceCount
        self.applicationCount = applicationCount
        self.mappingTableCount = mappingTableCount
        self.customer_id = customer_id
        self.dataset_id = dataset_id
        self.mapping_assignemnt = mapping_assignemnt
        self.possible_assignee = possible_assignee
        self.possible_assignee_for_assignment = possible_assignee_for_assignment

    def invokeAssignment(self):
        ()
        logging.info("Inside Invoke Assignment Method ")

        logging.info("%s: Checking if Custom Assignment is present or Not" % RestService.timestamp())
        custom_assignment_flag, custom_url = CustomerMasterData.check_custom("customAssignment")
        if (custom_assignment_flag == 'failure'):
            logging.info("%s: Not able to read values from Configure File" % RestService.timestamp())
            return "Failure"

        elif (custom_assignment_flag == "True"):
            logging.info("%s Custom Assignment is present invoking Custom Assignment " % RestService.timestamp())
            api = custom_url + "api/dummy_assignment"
            pass

        else:
            if (self.resourceCount >= 1 and self.applicationCount >= 1):
                logging.info("Invoking default workload assignment")

                obj = WorkloadAssignment(self.possible_assignee, self.possible_assignee_for_assignment)
                logging.info(f"WorkloadAssignment: {obj}")
                if (self.possible_assignee):
                    return obj.find_possibleassignees()

                elif (self.possible_assignee_for_assignment):
                    return obj.find_assigneesForAssignmentGroups()
                else:
                    return "Failure"

            elif (self.mappingTableCount >= 1):
                logging.info("Invoking One to One Mapping Assignment")
                obj = OneByOneMappingAssignment(self.customer_id, self.dataset_id, self.mapping_assignemnt)
                return obj.manualassignee()
            else:
                logging.info("No Assignment module is configured for these Configurations !!! \
                        Please make right Configurations")
                return "Failure"