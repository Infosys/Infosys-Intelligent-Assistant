__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

import numpy as np
from intent.persistence.mongodbpersistence import MongoDBPersistence
from intent.restservice import RestService
from intent.masterdata.applications import ApplicationMasterData
from intent.masterdata.resourceavailability import ResourceAvailabilityMasterData
from bson import json_util
from datetime import datetime
from flask import request
from urllib.parse import unquote
#import logging
import json
import pandas as pd
import io
import csv
from intent.persistence.mappingpersistence import MappingPersistence
from intent.utils.log_helper import get_logger, log_setup
logging = get_logger(__name__)
        
class LTFS_IRSR_resources(object):
    '''
    classdocs
    '''

    def __init__(self, params):
        '''
        Constructor
        '''
    @staticmethod
    def update_workload(status,priority,ResourceAssigned,AssignmentGrp,incident_no):
        # log_setup()
        logging.info('%s: In "update_workload()" method, Trying to fetch documents from "tickets_weightage_tbl"'%RestService.timestamp())
        customer_id = 1
        field_mapping = MappingPersistence.get_mapping_details(customer_id)
        group_field_name = field_mapping['Group_Field_Name']
        ticket_id_field_name = field_mapping['Ticket_ID_Field_Name']
        status_field_name = field_mapping['Status_Field_Name']
        description_field_name = field_mapping['Description_Field_Name']
        technician_field_name = field_mapping['Technician_Field_Name']
        priority_field_name = field_mapping['Priority_Field_Name']
        AssignmentGrp = str(AssignmentGrp)
        ticket_doc= MongoDBPersistence.tickets_weightage_tbl.find_one({
                            priority_field_name:priority,status_field_name:status
                    },{
                            "ticket_weightage":1,"_id":0
                    })
        logging.info('LTFS Trying to fetch documents from "applicationDetails_tbl" for assign grp: %s'%AssignmentGrp)
        app_doc = MongoDBPersistence.applicationDetails_tbl.find_one({'assignment_group':AssignmentGrp},{"app_weightage":1,"_id":0})

        #ticket_doc = 1
        if(ticket_doc and app_doc):
            ticket_Weightage = float(ticket_doc['ticket_weightage'])
            #ticket_Weightage = 1
            logging.info('ticket_Weightage here')
            app_Weightage = float(app_doc['app_weightage'])  
            logging.info('ticket_Weightage here 1')
            workload = ticket_Weightage * app_Weightage  
            logging.info('ticket_Weightage here 3')
            logging.info('Trying to update "TicketWeightage", "workload" in "rt_tickets_tbl"')
            MongoDBPersistence.rt_tickets_tbl.update_one({
                        ticket_id_field_name:incident_no
                },{
                        '$set': {"TicketWeightage":ticket_Weightage,"workload":workload}
                })
        else:
            logging.error('Could not found document either from "tickets_weightage_tbl" or from "applicationDetails_tbl"')
    
    #---------------------
    @staticmethod
    def incident_workload_update(customer_id, dataset_id, incident_lst):
        # log_setup()
        logging.info('%s: In "incident_workload_update() for LTFS" method')
        field_mapping = MappingPersistence.get_mapping_details(customer_id)
        group_field_name = field_mapping['Group_Field_Name']
        ticket_id_field_name = field_mapping['Ticket_ID_Field_Name']
        status_field_name = field_mapping['Status_Field_Name']
        description_field_name = field_mapping['Description_Field_Name']
        technician_field_name = field_mapping['Technician_Field_Name']
        priority_field_name = field_mapping['Priority_Field_Name']
        try:
            logging.info('Trying to fetch documents from "rt_tickets_tbl" for LTFS')
            #incident_doc_lst = MongoDBPersistence.rt_tickets_tbl.find({ticket_id_field_name:incident_lst,'DatasetID':dataset_id,'CustomerID':customer_id},{'_id':0})

            print(ticket_id_field_name)
            incident_id = str(incident_lst[0])
            incident_doc_lst = list(MongoDBPersistence.rt_tickets_tbl.find({ticket_id_field_name:incident_id, "CustomerID" : 1,"DatasetID":1},{'_id':0}))
            if(incident_doc_lst):
                logging.info('Trying to itrate throug all documents and to update the same in LTFS')
                for incident_doc in incident_doc_lst:
                    status=incident_doc[status_field_name]
                    priority=incident_doc[priority_field_name]
                    ResourceAssigned = incident_doc[technician_field_name]
                    AssignmentGrp = incident_doc[group_field_name]
                    incident_no=incident_id
                    LTFS_IRSR_resources.update_workload(status,priority,ResourceAssigned,AssignmentGrp,incident_no)
            else:
                logging.error('Could not found document from "rt_tickets_tbl"  in LTFS')
        except TypeError as e:
            incident_doc = None
            logging.error('%s: Error: %s'%(RestService.timestamp(),str(e)))
    #---------------------
    @staticmethod
    def find_possibleassignees(assignment_group):
        # log_setup()
        logging.info('LTFS %s: In "find_possibleassignees" method, argument - assign grp: %s'%(RestService.timestamp(), assignment_group))
        app_lst=[]
        resource_name_lst=[]
        roaster_lst=[]
        resource_lst=[]
        res_names=[]
        logging.info('LTFS Trying to call "getAppWeightage()" method of "ApplicationMasterData" to get "app_weightage"')
        app_weightage = float(ApplicationMasterData.getAppWeightage(assignment_group))
        logging.info('LTFS Trying to fetch documents from "applicationDetails_tbl"')
        app_lst=list(MongoDBPersistence.applicationDetails_tbl.find({'assignment_group':assignment_group}, {"_id":0}))        
        logging.info('LTFS Trying to call "getRoasterList()" method of "ResourceAvailabilityMasterData" to get "roaster_lst"')
        roaster_lst = ResourceAvailabilityMasterData.getRoasterList(assignment_group)
        
        if((app_weightage >= 0) and roaster_lst):
            for roaster_doc in roaster_lst:
                resource_name_lst.append(roaster_doc['resource_name'][0]['resource_name'])
            
            #resource_lst=list(resource_details_tbl.find({'$and':[{'resource_name':{'$in':resource_name_lst}},{'calculated_workload':{'$lte':(1-app_weightage)}}]},{"resource_id":1,"resource_name":1,"calculated_workload":1,"_id":0}).sort([("calculated_workload", pymongo.ASCENDING)]))
            #------Newly Inserted ----------------------
            resource_choosen_lst=[]
            logging.info('LTFS Trying to fetch documents from "resource_details_tbl"')
            resource_lst=list(MongoDBPersistence.resource_details_tbl.find({'resource_name':{'$in':resource_name_lst}}))
            if(resource_lst):
                #--Calculating current workload for resource----
                workload =[]
                for resource_doc in resource_lst:
                    tickets_assigned=0
                    resource_doc['current_workload']=0
                    resource_doc['tickets_assigned']=0
                    incident_lst= list(MongoDBPersistence.rt_tickets_tbl.find({"technician":resource_doc['resource_name']},{'workload':1,"_id":0}))
                    if(incident_lst):
                        for incident_doc in incident_lst:
                            workload.append(incident_doc["workload"])
                            tickets_assigned=tickets_assigned+1
                        resource_doc['current_workload']=sum(workload)
            
                        resource_doc['tickets_assigned']=tickets_assigned
                        workload=[]
                        
                for resource_doc in resource_lst:
                    availability_threshold_value = int(resource_doc['res_bandwidth'])/100
                    if(resource_doc['current_workload']<=(availability_threshold_value-app_weightage)):
                        resource_choosen_lst.append(resource_doc)
                
                resource_lst=resource_choosen_lst
                    #-------------------------------------------  
                res_names=['']*len(resource_lst)
                k=0
                for res in resource_lst:
                    res_names[k]=res['resource_name']
                    k=k+1
            else:
                logging.error('LTFS Could not fetch documents from "resource_details_tbl"')
        else:
            logging.error('LTFS Could not found value Either from "getAppWeightage()" or from "getRoasterList()" for assign group: %s'%assignment_group)
        return res_names