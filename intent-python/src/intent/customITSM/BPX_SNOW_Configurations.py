__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""
#--Imports for service now--
import pysnow
#import logging
from servicenow import ServiceNow
from servicenow import Connection
from intent.persistence.mongodbpersistence import MongoDBPersistence
from intent.masterdata.datasets import DatasetMasterData
from intent.persistence.mappingpersistence import MappingPersistence
from flask import request
from bson import json_util
from datetime import datetime, timedelta
import os
import configparser
from flask import session
from intent.restservice import RestService
from intent.masterdata.resources import ResourceMasterData
from pathlib import Path
import joblib
from bson import json_util
import json
import pandas as pd
import re
import importlib
import subprocess
from intent.incident.incidenttraining import IncidentTraining
from intent.utils.log_helper import get_logger, log_setup
logging = get_logger(__name__)
# log_setup()
class BPX_SNOW_Configurations(object):
    '''
    classdocs
    '''
    c = None
    servicenow_incidents = None
    servicenow_service_requests = None
    def __init__(self, params):
        '''
        Constructor
        '''
      
    @staticmethod
    def getClient():    
        try:
            ()
            if(BPX_SNOW_Configurations.c is None):   
                # Connect to Service Now using default api method (JSON)
                instance = MongoDBPersistence.customer_tbl.find_one({"CustomerID":1}, {'SNOWInstance':1, '_id':0})
                username = MongoDBPersistence.customer_tbl.find_one({"CustomerID":1}, {'SNOWUserName':1, '_id':0})
                password = MongoDBPersistence.customer_tbl.find_one({"CustomerID":1}, {'SNOWPassword':1, '_id':0})
                BPX_SNOW_Configurations.c = pysnow.Client(instance=instance['SNOWInstance'], user=username['SNOWUserName'], password=password['SNOWPassword'])
                #To display actual values of fields instead of external reference link or GUID - Service Now
                BPX_SNOW_Configurations.c.parameters.display_value = True
                BPX_SNOW_Configurations.c.parameters.exclude_reference_link = True
                BPX_SNOW_Configurations.servicenow_incidents = BPX_SNOW_Configurations.c.resource(api_path='/table/incident')
            return (BPX_SNOW_Configurations.servicenow_incidents)
        except Exception as e:
             raise

    @staticmethod
    def getClient_ServiceRequests():    
        try:
            ()
            instance = MongoDBPersistence.customer_tbl.find_one({"CustomerID":1}, {'SNOWInstance':1, '_id':0})
            username = MongoDBPersistence.customer_tbl.find_one({"CustomerID":1}, {'SNOWUserName':1, '_id':0})
            password = MongoDBPersistence.customer_tbl.find_one({"CustomerID":1}, {'SNOWPassword':1, '_id':0})
            BPX_SNOW_Configurations.c = pysnow.Client(instance=instance['SNOWInstance'], user=username['SNOWUserName'], password=password['SNOWPassword'])
            #To display actual values of fields instead of external reference link or GUID - Service Now
            BPX_SNOW_Configurations.c.parameters.display_value = True
            BPX_SNOW_Configurations.c.parameters.exclude_reference_link = True
            BPX_SNOW_Configurations.servicenow_service_requests = BPX_SNOW_Configurations.c.resource(api_path='/table/sc_task')
            return (BPX_SNOW_Configurations.servicenow_service_requests)
        except Exception as e:
             raise  
            
    #New Service Now changes
    #@app.route('/serviceNow/<int:customer_id>', methods=['GET'])
    @staticmethod
    def get_Current_ITSM_tickets( customer_id):
        ()
        logging.info("Inside Custom Itsm configuration file for Customer %s"%(customer_id))
        user_dataset_id=MongoDBPersistence.training_tickets_tbl.find_one({"CustomerID":customer_id})["DatasetID"]
        incident_no_lst=[]
        application_groups=[]
        # user = os.getlogin()
        if (session.get('user')):
            logging.info("%s Catching User Session"%RestService.timestamp())
            user = session['user']
            logging.info("%s Session catched user as  %s"%(RestService.timestamp(), user))
        else:
            logging.info("%s You are not logged in please login" %RestService.timestamp())
            return "failure"

        field_mapping = MappingPersistence.get_mapping_details(customer_id)
        group_field_name = field_mapping['Group_Field_Name']
        Assigned_To_Field_Name = field_mapping['Assigned_To_Field_Name']
        ticket_id_field_name = field_mapping['Ticket_ID_Field_Name']
        status_field_name = field_mapping['Status_Field_Name']
        contact_type = field_mapping['Contact_type']
        login_user = MongoDBPersistence.users_tbl.find_one({"UserID": user}, {"_id": 0})
        if (login_user):
            user_role = login_user['Role']
            if (user_role == 'Admin'):
                try:
                   #for Incidents - START
                    servicenow_incidents = BPX_SNOW_Configurations.getClient()
                    
                    application_groups=MongoDBPersistence.db.TblApplication.find().distinct(group_field_name)
                    if(not application_groups):            
                        application_groups = MongoDBPersistence.training_tickets_tbl.find({"CustomerID":customer_id,"DatasetID": user_dataset_id}).distinct(group_field_name)
                        
                                        #### RB specific code ############
                    accountName=None
                    states=''
                    config = configparser.ConfigParser()
                    config["DEFAULT"]['path'] = "config/"
                    config.read(config["DEFAULT"]["path"]+"Intent.ini")
                    try:
                        accountName = str(config["Account"]["accountName"])
                        application_groups = config["Account"]["assignmentGroup"].strip().split(",")
                        states = config["Account"]["states"].strip().split(",")
                        
                    except Exception as e:
                        logging.error("Taking default SNOW Configurations %s"%(str(e)))

                    queryBuilder=""
                    if(accountName=="RB"):
                        state_builder=''
                        for state in states:
                            state_builder += status_field_name + '='+state+'^OR'
                        queryBuilder=state_builder[:-3]+'^' + group_field_name + '!=is_empty^'
                    
                    else:
                        logging.info("Going for default configurations")
                        #group_field_name = state/status
                        #Get all New and In progress tickets and filter them based on assignment groups
                        queryBuilder= status_field_name + '=1^OR' + status_field_name + '=2^OR' + status_field_name + '=3^' + Assigned_To_Field_Name + '='''
                        #queryBuilder= status_field_name + '=1^' + group_field_name + '!=is_empty^'
                        # """for app_group in application_groups:
                        #     queryBuilder = queryBuilder + group_field_name + 'LIKE'+app_group +'^OR'"""
                        print("querybuilde...",queryBuilder)
                        response = servicenow_incidents.get(query=queryBuilder)
                        print("post response....",response)
                        for responce_doc in response.all():
                            logging.info("rt tickets %s"%(responce_doc[ticket_id_field_name]))
                            incident_no_lst.append(responce_doc[ticket_id_field_name])

                                           
                    
                        #Remove all inicidents from DB, which are not present in Service Now dump
                        MongoDBPersistence.rt_tickets_tbl.update_many({ticket_id_field_name:{'$nin':incident_no_lst}},{'$set':{status_field_name:'closed'}})
                    
                    
                        datasets = list(MongoDBPersistence.datasets_tbl.find({"CustomerID" : customer_id}))

                        
                        incident_number_lst=MongoDBPersistence.rt_tickets_tbl.find({},{'_id':0, ticket_id_field_name:1}).distinct(ticket_id_field_name)
                        #print("SNOW response ...",response.all())
                        for record in response.all():
                            dataset_id = 0
                            logging.info('%s: START - Tickets Update in DB from Service Now....'%(RestService.timestamp()))                
                            if(record[ticket_id_field_name] not in incident_number_lst):
                                #Update status and other columns of Incidents in DB and Insert the new incidents in DB
                                record['CustomerID'] = customer_id
                                record["workload"] = 0.0
                                record["tickets_assigned"] = 0
                                record['user_status'] = 'Not Approved'
                                record['Source'] = 'SNOW'
                                if(str(record['description']) == 'null' or str(record['description']) == 'None'):
                                    record['description'] = " "
                                record["description"] = str(record["description"])
                                record['configuration_item']=str(record['cmdb_ci'])
                              
                            for dataset in datasets:
                                #print("dataset details...",dataset)
                                fields = dataset['UniqueFields']
                                match_flag = 0
                                for field in fields:
                                    try:
                                        #print("fields",fields)
                                        dataset_values = MongoDBPersistence.training_tickets_tbl.find({"CustomerID":customer_id, "DatasetID": dataset['DatasetID']}).distinct(field['FieldName']) #"DatasetID":dataset['DatasetID']
                                        logging.info('distinct %s values are %s '%(field['FieldName'],dataset_values))
                                        logging.info('real time ticket %s value is %s'%(field['FieldName'],record[field['FieldName']]))
                                    except Exception as e:
                                            logging.error('%s: Error: %s'%(RestService.timestamp(),str(e)))
                                            logging.info('%s: Column name %s not found.'%(RestService.timestamp(),field['FieldName']))
                                            break
                                    if(field['FieldName'] in record.keys()):
                                        logging.info('real time ticket %s value is %s'%(field['FieldName'],record[field['FieldName']]))
                                        if(record[field['FieldName']] in set(dataset_values)):
                                            match_flag = match_flag + 1
                                if(match_flag == len(fields)):
                                    dataset_id = dataset['DatasetID']
                                    record['DatasetID'] = dataset_id
                                    logging.info('real time ticket dataset ID is %s'%(record['DatasetID']))
                                    break
                            if(dataset_id == 0):
                                logging.info('%s: the ticket (Incident Number: %s) do not match with any of the datasets.'%(RestService.timestamp(),record[ticket_id_field_name]))
                                continue
                

                            MongoDBPersistence.rt_tickets_tbl.update_one({ticket_id_field_name:record[ticket_id_field_name]},{'$set': record}, upsert=True)
                
                        logging.info('%s: END - Tickets Udapte in DB from Service Now....'%(RestService.timestamp()))
                   #for incidents - END
                    


                    #for service requests - START

                    servicenow_service_requests = BPX_SNOW_Configurations.getClient_ServiceRequests()
                    
                    application_groups=MongoDBPersistence.db.TblApplication.find().distinct(group_field_name)
                    if(not application_groups):            
                        application_groups = MongoDBPersistence.training_tickets_tbl.find({"CustomerID":customer_id,"DatasetID": user_dataset_id}).distinct(group_field_name)
                        
                    #### RB specific code ############
                    accountName=None
                    states=''
                    config = configparser.ConfigParser()
                    config["DEFAULT"]['path'] = "config/"
                    config.read(config["DEFAULT"]["path"]+"Intent.ini")
                    try:
                        accountName = str(config["Account"]["accountName"])
                        application_groups = config["Account"]["assignmentGroup"].strip().split(",")
                        states = config["Account"]["states"].strip().split(",")
                        
                    except Exception as e:
                        logging.error("Taking default SNOW Configurations %s"%(str(e)))

                    queryBuilder=""
                    if(accountName=="RB"):
                        state_builder=''
                        for state in states:
                            state_builder += status_field_name + '='+state+'^OR'
                        queryBuilder=state_builder[:-3]+'^' + group_field_name + '!=is_empty^'
                    
                    else:
                        logging.info("Going for default configurations")
                        #group_field_name = state/status
                        #Get all New and In progress tickets and filter them based on assignment groups
                        queryBuilder= status_field_name + '=1^OR' + status_field_name + '=2^OR' + status_field_name + '=-5^' + Assigned_To_Field_Name + '='''
                        #queryBuilder= status_field_name + '=1^' + group_field_name + '!=is_empty^'
                
                        # """for app_group in application_groups:
                        #     queryBuilder = queryBuilder + group_field_name + 'LIKE'+app_group +'^OR'"""
                        print("query builder..",queryBuilder,servicenow_service_requests)
                        response = servicenow_service_requests.get(query=queryBuilder)
                        
                        for responce_doc in response.all():
                            logging.info("rt tickets %s"%(responce_doc[ticket_id_field_name]))
                            incident_no_lst.append(responce_doc[ticket_id_field_name])                

                        #print("incident number list..",incident_no_lst)
                        #Remove all inicidents from DB, which are not present in Service Now dump
                        MongoDBPersistence.rt_tickets_tbl.update_many({ticket_id_field_name:{'$nin':incident_no_lst}},{'$set':{status_field_name:'closed'}})
                    
                    
                        datasets = list(MongoDBPersistence.datasets_tbl.find({"CustomerID" : customer_id}))
                        #print(datasets)
                        #initial
                        
                        service_number_lst=MongoDBPersistence.rt_tickets_tbl.find({},{'_id':0, ticket_id_field_name:1}).distinct(ticket_id_field_name)
                        #print("SNOW response ...",response.all())
                        for record in response.all():
                            dataset_id = 0
                            logging.info('%s: START - Tickets Update in DB from Service Now....'%(RestService.timestamp()))                
                            if(record[ticket_id_field_name] not in service_number_lst):
                                #Update status and other columns of Incidents in DB and Insert the new incidents in DB
                                record['CustomerID'] = customer_id
                                record["workload"] = 0.0
                                record["tickets_assigned"] = 0
                                record['user_status'] = 'Not Approved'
                                record['Source'] = 'SNOW'
                                if(str(record['description']) == 'null' or str(record['description']) == 'None'):
                                    record['description'] = " "
                                record["description"] = str(record["description"])
                                record['configuration_item']=str(record['cmdb_ci'])
                              
                            for dataset in datasets:
                                #print("dataset details...",dataset)
                                fields = dataset['UniqueFields']
                                match_flag = 0
                                for field in fields:
                                    try:
                                        #print("fields",fields)
                                        dataset_values = MongoDBPersistence.training_tickets_tbl.find({"CustomerID":customer_id, "DatasetID": dataset['DatasetID']}).distinct(field['FieldName']) #"DatasetID":dataset['DatasetID']
                                        logging.info('distinct %s values are %s '%(field['FieldName'],dataset_values))
                                        logging.info('real time ticket %s value is %s'%(field['FieldName'],record[field['FieldName']]))
                                    except Exception as e:
                                            logging.error('%s: Error: %s'%(RestService.timestamp(),str(e)))
                                            logging.info('%s: Column name %s not found.'%(RestService.timestamp(),field['FieldName']))
                                            break
                                    if(field['FieldName'] in record.keys()):
                                        logging.info('real time ticket %s value is %s'%(field['FieldName'],record[field['FieldName']]))
                                        if(record[field['FieldName']] in set(dataset_values)):
                                            match_flag = match_flag + 1
                                if(match_flag == len(fields)):
                                    dataset_id = dataset['DatasetID']
                                    record['DatasetID'] = dataset_id
                                    logging.info('real time ticket dataset ID is %s'%(record['DatasetID']))
                                    break
                            if(dataset_id == 0):
                                logging.info('%s: the ticket (Incident Number: %s) do not match with any of the datasets.'%(RestService.timestamp(),record[ticket_id_field_name]))
                                continue
                

                            MongoDBPersistence.rt_tickets_tbl.update_one({ticket_id_field_name:record[ticket_id_field_name]},{'$set': record}, upsert=True)
                
                        logging.info('%s: END - Tickets Udapte in DB from Service Now....'%(RestService.timestamp()))

                         #for service requests - END


                    if(response):
                        logging.info('%s: Tickets received from Service Now'%(RestService.timestamp()))
                        response_tmp = MongoDBPersistence.db.TblIncidentRT.find({'user_status':'Not Approved'})
                        return(json_util.dumps(response_tmp))
                    else:
                        logging.info('%s: Could not get tickets from Service Now'%(RestService.timestamp()))
                        return 'no tickets found in Service Now'
                except Exception as e:
                    return(json_util.dumps({'exception':str(e)}))
            else:
                team_id = login_user['TeamID']
                user_dataset_id = MongoDBPersistence.teams_tbl.find_one({"TeamID": int(team_id)},{"_id":0, "DatasetID":1})
        
                try:
                     #for Incidents - START
                    servicenow_incidents = BPX_SNOW_Configurations.getClient()
                    
                    application_groups=MongoDBPersistence.db.TblApplication.find().distinct(group_field_name)
                    if(not application_groups):            
                        application_groups = MongoDBPersistence.training_tickets_tbl.find({"CustomerID":customer_id,"DatasetID": user_dataset_id}).distinct(group_field_name)
                        
                                        #### RB specific code ############
                    accountName=None
                    states=''
                    config = configparser.ConfigParser()
                    config["DEFAULT"]['path'] = "config/"
                    config.read(config["DEFAULT"]["path"]+"Intent.ini")
                    try:
                        accountName = str(config["Account"]["accountName"])
                        application_groups = config["Account"]["assignmentGroup"].strip().split(",")
                        states = config["Account"]["states"].strip().split(",")
                        
                    except Exception as e:
                        logging.error("Taking default SNOW Configurations %s"%(str(e)))

                    queryBuilder=""
                    if(accountName=="RB"):
                        state_builder=''
                        for state in states:
                            state_builder += status_field_name + '='+state+'^OR'
                        queryBuilder=state_builder[:-3]+'^' + group_field_name + '!=is_empty^'
                    
                    else:
                        logging.info("Going for default configurations")
                        #group_field_name = state/status
                        #Get all New and In progress tickets and filter them based on assignment groups
                        queryBuilder= status_field_name + '=1^OR' + status_field_name + '=2^OR' + status_field_name + '=3^' + Assigned_To_Field_Name + '=""'
                        #queryBuilder= status_field_name + '=1^' + group_field_name + '!=is_empty^'
                        """for app_group in application_groups:
                            queryBuilder = queryBuilder + group_field_name + 'LIKE'+app_group +'^OR'"""
                    
                        response = servicenow_incidents.get(query=queryBuilder[:-3])
                        
                        for responce_doc in response.all():
                            logging.info("rt tickets %s"%(responce_doc[ticket_id_field_name]))
                            incident_no_lst.append(responce_doc[ticket_id_field_name])  
                            print(responce_doc[ticket_id_field_name])
                            print(responce_doc[contact_type])            
                    
                        #Remove all inicidents from DB, which are not present in Service Now dump
                        MongoDBPersistence.rt_tickets_tbl.update_many({ticket_id_field_name:{'$nin':incident_no_lst}},{'$set':{status_field_name:'closed'}})
                    
                    
                        datasets = list(MongoDBPersistence.datasets_tbl.find({"CustomerID" : customer_id}))
                        #print(datasets)
                        #initial
                        
                        incident_number_lst=MongoDBPersistence.rt_tickets_tbl.find({},{'_id':0, ticket_id_field_name:1}).distinct(ticket_id_field_name)
                        #print("SNOW response ...",response.all())
                        for record in response.all():
                            dataset_id = 0
                            logging.info('%s: START - Tickets Update in DB from Service Now....'%(RestService.timestamp()))                
                            if(record[ticket_id_field_name] not in incident_number_lst):
                                #Update status and other columns of Incidents in DB and Insert the new incidents in DB
                                record['CustomerID'] = customer_id
                                record["workload"] = 0.0
                                record["tickets_assigned"] = 0
                                record['user_status'] = 'Not Approved'
                                record['Source'] = 'SNOW'
                                if(str(record['description']) == 'null' or str(record['description']) == 'None'):
                                    record['description'] = " "
                                record["description"] = str(record["description"])
                                record['configuration_item']=str(record['cmdb_ci'])
                              
                            for dataset in datasets:
                                #print("dataset details...",dataset)
                                fields = dataset['UniqueFields']
                                match_flag = 0
                                for field in fields:
                                    try:
                                        #print("fields",fields)
                                        dataset_values = MongoDBPersistence.training_tickets_tbl.find({"CustomerID":customer_id, "DatasetID": dataset['DatasetID']}).distinct(field['FieldName']) #"DatasetID":dataset['DatasetID']
                                        logging.info('distinct %s values are %s '%(field['FieldName'],dataset_values))
                                        logging.info('real time ticket %s value is %s'%(field['FieldName'],record[field['FieldName']]))
                                    except Exception as e:
                                            logging.error('%s: Error: %s'%(RestService.timestamp(),str(e)))
                                            logging.info('%s: Column name %s not found.'%(RestService.timestamp(),field['FieldName']))
                                            break
                                    if(field['FieldName'] in record.keys()):
                                        logging.info('real time ticket %s value is %s'%(field['FieldName'],record[field['FieldName']]))
                                        if(record[field['FieldName']] in set(dataset_values)):
                                            match_flag = match_flag + 1
                                if(match_flag == len(fields)):
                                    dataset_id = dataset['DatasetID']
                                    record['DatasetID'] = dataset_id
                                    logging.info('real time ticket dataset ID is %s'%(record['DatasetID']))
                                    break
                            if(dataset_id == 0):
                                logging.info('%s: the ticket (Incident Number: %s) do not match with any of the datasets.'%(RestService.timestamp(),record[ticket_id_field_name]))
                                continue
                

                            MongoDBPersistence.rt_tickets_tbl.update_one({ticket_id_field_name:record[ticket_id_field_name]},{'$set': record}, upsert=True)
                
                        logging.info('%s: END - Tickets Udapte in DB from Service Now....'%(RestService.timestamp()))
                   #for incidents - END
                    


                    #for service requests - START

                    servicenow_service_requests = BPX_SNOW_Configurations.getClient_ServiceRequests()
                    
                    application_groups=MongoDBPersistence.db.TblApplication.find().distinct(group_field_name)
                    if(not application_groups):            
                        application_groups = MongoDBPersistence.training_tickets_tbl.find({"CustomerID":customer_id,"DatasetID": user_dataset_id}).distinct(group_field_name)
                        
                    #### RB specific code ############
                    accountName=None
                    states=''
                    config = configparser.ConfigParser()
                    config["DEFAULT"]['path'] = "config/"
                    config.read(config["DEFAULT"]["path"]+"Intent.ini")
                    try:
                        accountName = str(config["Account"]["accountName"])
                        application_groups = config["Account"]["assignmentGroup"].strip().split(",")
                        states = config["Account"]["states"].strip().split(",")
                        
                    except Exception as e:
                        logging.error("Taking default SNOW Configurations %s"%(str(e)))

                    queryBuilder=""
                    if(accountName=="RB"):
                        state_builder=''
                        for state in states:
                            state_builder += status_field_name + '='+state+'^OR'
                        queryBuilder=state_builder[:-3]+'^' + group_field_name + '!=is_empty^'
                    
                    else:
                        logging.info("Going for default configurations")
                        #group_field_name = state/status
                        #Get all New and In progress tickets and filter them based on assignment groups
                        queryBuilder= status_field_name + '=1^OR' + status_field_name + '=2^OR' + status_field_name + '=-5^' + Assigned_To_Field_Name + '=""'
                        #queryBuilder= status_field_name + '=1^' + group_field_name + '!=is_empty^'
                        """for app_group in application_groups:
                            queryBuilder = queryBuilder + group_field_name + 'LIKE'+app_group +'^OR'"""
                        print("query builder..",queryBuilder,servicenow_service_requests)
                        response = servicenow_service_requests.get(query=queryBuilder[:-3])
                        print("after resp..",response)
                        
                        for responce_doc in response.all():
                            logging.info("rt tickets %s"%(responce_doc[ticket_id_field_name]))
                            incident_no_lst.append(responce_doc[ticket_id_field_name])                

                        print("incident number list..",incident_no_lst)
                        #Remove all inicidents from DB, which are not present in Service Now dump
                        MongoDBPersistence.rt_tickets_tbl.update_many({ticket_id_field_name:{'$nin':incident_no_lst}},{'$set':{status_field_name:'closed'}})
                    
                    
                        datasets = list(MongoDBPersistence.datasets_tbl.find({"CustomerID" : customer_id}))
                        #print(datasets)
                        #initial
                        
                        service_number_lst=MongoDBPersistence.rt_tickets_tbl.find({},{'_id':0, ticket_id_field_name:1}).distinct(ticket_id_field_name)
                        #print("SNOW response ...",response.all())
                        for record in response.all():
                            dataset_id = 0
                            logging.info('%s: START - Tickets Update in DB from Service Now....'%(RestService.timestamp()))                
                            if(record[ticket_id_field_name] not in service_number_lst):
                                #Update status and other columns of Incidents in DB and Insert the new incidents in DB
                                record['CustomerID'] = customer_id
                                record["workload"] = 0.0
                                record["tickets_assigned"] = 0
                                record['user_status'] = 'Not Approved'
                                record['Source'] = 'SNOW'
                                if(str(record['description']) == 'null' or str(record['description']) == 'None'):
                                    record['description'] = " "
                                record["description"] = str(record["description"])
                                record['configuration_item']=str(record['cmdb_ci'])
                              
                            for dataset in datasets:
                                #print("dataset details...",dataset)
                                fields = dataset['UniqueFields']
                                match_flag = 0
                                for field in fields:
                                    try:
                                        #print("fields",fields)
                                        dataset_values = MongoDBPersistence.training_tickets_tbl.find({"CustomerID":customer_id, "DatasetID": dataset['DatasetID']}).distinct(field['FieldName']) #"DatasetID":dataset['DatasetID']
                                        logging.info('distinct %s values are %s '%(field['FieldName'],dataset_values))
                                        logging.info('real time ticket %s value is %s'%(field['FieldName'],record[field['FieldName']]))
                                    except Exception as e:
                                            logging.error('%s: Error: %s'%(RestService.timestamp(),str(e)))
                                            logging.info('%s: Column name %s not found.'%(RestService.timestamp(),field['FieldName']))
                                            break
                                    if(field['FieldName'] in record.keys()):
                                        logging.info('real time ticket %s value is %s'%(field['FieldName'],record[field['FieldName']]))
                                        if(record[field['FieldName']] in set(dataset_values)):
                                            match_flag = match_flag + 1
                                if(match_flag == len(fields)):
                                    dataset_id = dataset['DatasetID']
                                    record['DatasetID'] = dataset_id
                                    logging.info('real time ticket dataset ID is %s'%(record['DatasetID']))
                                    break
                            if(dataset_id == 0):
                                logging.info('%s: the ticket (Incident Number: %s) do not match with any of the datasets.'%(RestService.timestamp(),record[ticket_id_field_name]))
                                continue
                

                            MongoDBPersistence.rt_tickets_tbl.update_one({ticket_id_field_name:record[ticket_id_field_name]},{'$set': record}, upsert=True)
                
                        logging.info('%s: END - Tickets Udapte in DB from Service Now....'%(RestService.timestamp()))

                        #for service requests - END


                    if(response):
                        logging.info('%s: Tickets received from Service Now'%(RestService.timestamp()))
                        response_tmp = MongoDBPersistence.db.TblIncidentRT.find({status_field_name:'New','user_status':'Not Approved'})
                        return(json_util.dumps(response_tmp))
                    else:
                        logging.info('%s: Could not get tickets from Service Now'%(RestService.timestamp()))
                        return 'no tickets found in Service Now'
                except Exception as e:
                     return(json_util.dumps({'exception':str(e)}))
       
        else:
            logging.info("%s User is not authenticated"%RestService.timestamp())
            return "failure"
    
    
    
    
    #@app.route('/guessServiceNowDataset/<int:customer_id>',methods=['POST'])
    @staticmethod
    def guessServiceNowDataset( customer_id):
        data = request.get_json()
        #print(data)
        result = DatasetMasterData.guessDataset(data, customer_id)
        if(result == 'failure'):
            return result
        if(result):
            response = 'warning'
        else:
            response = 'success'
        return response 
    
    @staticmethod
    def get_prev_week_openIncidents():
        today = datetime.today()
        ()
        one_week_ago = today - timedelta(days=100)
    
        customer_details = MongoDBPersistence.customer_tbl.find_one({}, {"_id":0})
        customer_id = customer_details['CustomerID']
        field_mapping = MappingPersistence.get_mapping_details(customer_id)
        group_field_name = field_mapping['Group_Field_Name']
        Assigned_To_Field_Name = field_mapping['Assigned_To_Field_Name']
        ticket_id_field_name = field_mapping['Ticket_ID_Field_Name']
        status_field_name = field_mapping['Status_Field_Name']
        sys_created_on_field_name = field_mapping['Sys_Created_On_Field_Name']
        incident_no_lst=[]
        application_groups=[]
        
        try:
            servicenow_incidents = BPX_SNOW_Configurations.getClient()
            
            queryBuilder = (pysnow.QueryBuilder().field(status_field_name).equals("1").AND()
            .field(sys_created_on_field_name).between(one_week_ago, today))
            
            response = servicenow_incidents.get(query=queryBuilder)
            #print("In get open tickets for one week...",response.all())
            if(response):
                for responce_doc in response.all():
                    incident_no_lst.append(responce_doc[ticket_id_field_name])
            
            print("In get open tickets for one week...",len(incident_no_lst))
            
            return (json_util.dumps(len(incident_no_lst)))
        except Exception as e:
            return 'exception'

    
    @staticmethod
    def get_prev_week_closedIncidents():
        today = datetime.today()
        one_week_ago = today - timedelta(days=100)

        customer_details = MongoDBPersistence.customer_tbl.find_one({}, {"_id":0})
        customer_id = customer_details['CustomerID']
        field_mapping = MappingPersistence.get_mapping_details(customer_id)
        group_field_name = field_mapping['Group_Field_Name']
        Assigned_To_Field_Name = field_mapping['Assigned_To_Field_Name']
        ticket_id_field_name = field_mapping['Ticket_ID_Field_Name']
        status_field_name = field_mapping['Status_Field_Name']
        closed_at_field_name = field_mapping['Closed_At_Field_Name']
        incident_no_lst=[]
        application_groups=[]
        
        try:
            ()
            servicenow_incidents = BPX_SNOW_Configurations.getClient()
            
            queryBuilder = (pysnow.QueryBuilder().field(status_field_name).equals("7").AND()
            .field(closed_at_field_name).between(one_week_ago, today))
            
            response = servicenow_incidents.get(query=queryBuilder)
            #print("In get closed tickets for one week...",response.all())
            if(response):
                for responce_doc in response.all():
                    incident_no_lst.append(responce_doc[ticket_id_field_name])
            
            print("In get closed tickets for one week...",len(incident_no_lst))
            
            return (json_util.dumps(len(incident_no_lst)))
        except Exception as e:
            return 'exception'

    @staticmethod
    def updatePredictedDetails(customer_id, dataset_id):
        ()
        logging.info('%s : Trying to get date have to be approved from front end'%RestService.timestamp())
        data = request.get_json()
        if(data):
            resp = BPX_SNOW_Configurations.automaticTicketApproval(customer_id, dataset_id, data)
            return resp
        else:
            logging.error('No data recieved from front end')

    @staticmethod
    def automaticTicketApproval(customer_id, dataset_id, data=[]):
    # def updatePredictedDetails(customer_id, dataset_id):

        customer_name = MongoDBPersistence.customer_tbl.find_one({'CustomerID':customer_id},\
                                                                    {'CustomerName':1, '_id':0})['CustomerName']
            
        itsm_tool_name = MongoDBPersistence.itsm_details_tbl.find_one({},{"_id":0,"ITSMToolName":1})["ITSMToolName"]
        class_name = customer_name + "_"+ itsm_tool_name +"_"+ "Configurations"
        module_name = "intent.customITSM." + class_name
        ()
        logging.info("class name formed here is  %s and module is %s in updatePredictedDetails"%(class_name,module_name))

        logging.info("Going for default flow in update Predicted Field.")
        field_mapping = MappingPersistence.get_mapping_details(customer_id)
        group_field_name = field_mapping['Group_Field_Name']
        Assigned_To_Field_Name = field_mapping['Assigned_To_Field_Name']
        ticket_id_field_name = field_mapping['Ticket_ID_Field_Name']
        status_field_name = field_mapping['Status_Field_Name']
        description_field_name = field_mapping['Description_Field_Name']
        logging.info('%s: In "updatePredictedDetails()" method'%RestService.timestamp())

        if (session.get('user')):
            # logging.info("%s Catching User Session"%RestService.timestamp())
            user = session['user']
            # logging.info("%s Session catched user as  %s"%(RestService.timestamp(), user))
            #get data in [{"Assignment_group": "SAP FICO Support", "Subcategory": "ERP Misc"}]
            try:
                servicenow_incidents = BPX_SNOW_Configurations.getClient()
                
                # data = request.get_json()
                print("User Selected Data", data)
                incidentNumber = ''
                assignment_group = ''
                incident_lst=[]
                approved_tickets = []
                
                servicenow_exists = MongoDBPersistence.customer_tbl.find_one({"CustomerID":customer_id},{"_id":0, "SNOWInstance":1})
                if (servicenow_exists):
                    servicenow_flag = 1
                else:
                    servicenow_flag = 0
                if(data):
                    for incidentToUpdate in data: 
                        approved_data = {}
                        incidentNumber = incidentToUpdate[ticket_id_field_name]
                        assignment_group = incidentToUpdate[group_field_name]
                        if ("INC" in incidentNumber):
                            ticket_status = MongoDBPersistence.rt_tickets_tbl.find_one({"CustomerID":1, "DatasetID": dataset_id, ticket_id_field_name: incidentNumber, group_field_name : assignment_group}, {"_id": 0, "user_status": 1,"description":1})
                            if (ticket_status['user_status'] == 'Not Approved'):
                                incident_lst.append(incidentNumber)
                                
                                #the following code is for inserting approved tickets into Training table for Retraining 
                                incidentToUpdate['CustomerID'] = customer_id
                                incidentToUpdate["DatasetID"] = dataset_id
                                incidentToUpdate['user'] = user
                                logging.info('Trying to get document from "rt_tickets_tbl"')
                                incidentToinsert = MongoDBPersistence.rt_tickets_tbl.find_one({ticket_id_field_name:incidentNumber})
                                
                                
                                if(not incidentToinsert):
                                    logging.error('Could not get document from "rt_tickets_tbl" for ticket %s'%str(incidentNumber))
                                # Not inserting approved tickets to training table
                                # incidentToinsert['TrainingFlag'] = 0
                                # try:
                                #     MongoDBPersistence.training_tickets_tbl.update_one({ticket_id_field_name: incidentToinsert[ticket_id_field_name]},{"$set": incidentToinsert},upsert=True)
                                # except Exception as e:
                                #     logging.error('Error: %s'%str(e))
                            
                            
                                for key,value in incidentToUpdate.items():
                                    logging.info('Trying to update "predicted_tickets_tbl" with new predicted details')
                                    MongoDBPersistence.predicted_tickets_tbl.update_one({'CustomerID':customer_id,ticket_id_field_name:incidentNumber, 'DatasetID':dataset_id}, {"$set": {key:value}}, upsert=False)
                                    # MongoDBPersistence.predicted_tickets_tbl.update_one({'CustomerID':customer_id,ticket_id_field_name:incidentNumber, 'DatasetID':dataset_id}, {"$set": {'user': user}}, upsert=False)
                                    #--update servicenow--
                                    key = key.lower()
                                    if(key=='predicted_assigned_to'):
                                        key='assigned_to'
                                    if(key != ticket_id_field_name):
                                        if (servicenow_flag):
                                            if(servicenow_incidents):
                                                logging.info('Trying to update service now field "%s" with value: "%s"'%(key,value))
                                                try:
                                                    unwanted_lst = ['user','number','customerid','datasetid']
                                                    if(key not in unwanted_lst):
                                                        approved_data[key] = value
                                                    servicenow_incidents.update(query = {ticket_id_field_name: incidentNumber}, payload = {key:value})
                                                    inci_present= None
                                                    inci_present = MongoDBPersistence.approved_tickets_tbl.find_one({"CustomerID":customer_id,"ticket_number":incidentNumber})
                                                    print("incident status on approve ticket table", inci_present)
                                                    logging.info('Tickets Got Approved in SNOW now trying to insert approved details to "approved_tickets_tbl"')
                                                    if(inci_present is None):
                                                        logging.info('Tickets Got Approved in SNOW now trying to insert approved details to "approved_tickets_tbl"')
                                                        MongoDBPersistence.approved_tickets_tbl.insert_one({
                                                                                'CustomerID':customer_id,
                                                                                'DatasetID':dataset_id,
                                                                                'UserID':user,
                                                                                'ticket_number':incidentNumber,
                                                                                'ticket_description':ticket_status['description'],
                                                                                'approved_data':approved_data,
                                                                                'assignment_group':assignment_group
                                                                                })
                                    
                                                except:
                                                    logging.info("%s: servicenow of ticket with number %s is not possible check if ticket is present in servicenow or not "%(RestService.timestamp(), incidentNumber))
                                            else:
                                                logging.info("Servicenow Incident is none updating only DB")
                                    #-------------------
                                    
                                # End of key, value looping
                                logging.info('%s: Predicted Details has been successfully updated into a collection TblPredictedData by user %s.'%(RestService.timestamp(), user))
                                logging.info('Trying to update document of "rt_tickets_tbl" with "user_status" "Approved"')
                                MongoDBPersistence.rt_tickets_tbl.update_one({'CustomerID':customer_id,ticket_id_field_name: incidentNumber, 'DatasetID':dataset_id}, {"$set": {'user_status':'Approved'}}, upsert=False)
                                try:
                                    MongoDBPersistence.training_tickets_tbl.update_one({ticket_id_field_name: incidentToinsert[ticket_id_field_name]},{"$set": incidentToinsert},upsert=True)
                                except Exception as e:
                                    print(str(e))
                                logging.info('Trying to update "predicted_tickets_tbl" with approver details')
                                MongoDBPersistence.predicted_tickets_tbl.update_one({'CustomerID':customer_id,ticket_id_field_name:incidentNumber, 'DatasetID':dataset_id}, {"$set": {'user': user}}, upsert=False)
                                resp = 'success'
                            else:
                                approved_user = MongoDBPersistence.predicted_tickets_tbl.find_one({"CustomerID":customer_id, "DatasetID":dataset_id}, {"_id":0, "user":1})
                                approved_user = approved_user['user']
                                logging.info("%s: The ticket with ticket number %s has already been approved by user %s "%(RestService.timestamp(),incidentNumber, approved_user))
                                approved_ticket = MongoDBPersistence.predicted_tickets_tbl.find_one({"CustomerID":customer_id, "DatasetID":dataset_id}, {"_id":0, ticket_id_field_name:1, 'user':1})
                                approved_tickets.append(approved_ticket)  # List of tickets which are already approved

                        elif("SCTASK" in incidentNumber):
                            print("Inside SCTASK")
                            servicenow_service_requests = BPX_SNOW_Configurations.getClient_ServiceRequests()
                            ticket_status = MongoDBPersistence.rt_tickets_tbl.find_one({"CustomerID":1, "DatasetID": dataset_id, ticket_id_field_name: incidentNumber, group_field_name : assignment_group}, {"_id": 0, "user_status": 1,"description":1})
                            if (ticket_status['user_status'] == 'Not Approved'):
                                incident_lst.append(incidentNumber)
                                
                                #the following code is for inserting approved tickets into Training table for Retraining 
                                incidentToUpdate['CustomerID'] = customer_id
                                incidentToUpdate["DatasetID"] = dataset_id
                                incidentToUpdate['user'] = user
                                logging.info('Trying to get document from "rt_tickets_tbl"')
                                incidentToinsert = MongoDBPersistence.rt_tickets_tbl.find_one({ticket_id_field_name:incidentNumber})
                                
                                
                                if(not incidentToinsert):
                                    logging.error('Could not get document from "rt_tickets_tbl" for ticket %s'%str(incidentNumber))
                           
                            
                                for key,value in incidentToUpdate.items():
                                    logging.info('Trying to update "predicted_tickets_tbl" with new predicted details')
                                    MongoDBPersistence.predicted_tickets_tbl.update_one({'CustomerID':customer_id,ticket_id_field_name:incidentNumber, 'DatasetID':dataset_id}, {"$set": {key:value}}, upsert=False)
                                    key = key.lower()
                                    if(key=='predicted_assigned_to'):
                                        key='assigned_to'
                                    if(key != ticket_id_field_name):
                                        if (servicenow_flag):
                                            if(servicenow_service_requests):
                                                logging.info('Trying to update service now field "%s" with value: "%s"'%(key,value))
                                                try:
                                                    unwanted_lst = ['user','number','customerid','datasetid']
                                                    if(key not in unwanted_lst):
                                                        approved_data[key] = value
                                                    servicenow_service_requests.update(query = {ticket_id_field_name: incidentNumber}, payload = {key:value})
                                                    inci_present= None
                                                    inci_present = MongoDBPersistence.approved_tickets_tbl.find_one({"CustomerID":customer_id,"ticket_number":incidentNumber})
                                                    print("incident status on approve ticket table", inci_present)
                                                    logging.info('Tickets Got Approved in SNOW now trying to insert approved details to "approved_tickets_tbl"')
                                                    if(inci_present is None):
                                                        logging.info('Tickets Got Approved in SNOW now trying to insert approved details to "approved_tickets_tbl"')
                                                        MongoDBPersistence.approved_tickets_tbl.insert_one({
                                                                                'CustomerID':customer_id,
                                                                                'DatasetID':dataset_id,
                                                                                'UserID':user,
                                                                                'ticket_number':incidentNumber,
                                                                                'ticket_description':ticket_status['description'],
                                                                                'approved_data':approved_data,
                                                                                'assignment_group':assignment_group
                                                                                })
                                    
                                                except:
                                                    logging.info("%s: servicenow of ticket with number %s is not possible check if ticket is present in servicenow or not "%(RestService.timestamp(), incidentNumber))
                                            else:
                                                logging.info("Servicenow Incident is none updating only DB")
                                    #-------------------
                                    
                                # End of key, value looping
                                logging.info('%s: Predicted Details has been successfully updated into a collection TblPredictedData by user %s.'%(RestService.timestamp(), user))
                                logging.info('Trying to update document of "rt_tickets_tbl" with "user_status" "Approved"')
                                MongoDBPersistence.rt_tickets_tbl.update_one({'CustomerID':customer_id,ticket_id_field_name: incidentNumber, 'DatasetID':dataset_id}, {"$set": {'user_status':'Approved'}}, upsert=False)
                                try:
                                    MongoDBPersistence.training_tickets_tbl.update_one({ticket_id_field_name: incidentToinsert[ticket_id_field_name]},{"$set": incidentToinsert},upsert=True)
                                except Exception as e:
                                    print(str(e))
                                logging.info('Trying to update "predicted_tickets_tbl" with approver details')
                                MongoDBPersistence.predicted_tickets_tbl.update_one({'CustomerID':customer_id,ticket_id_field_name:incidentNumber, 'DatasetID':dataset_id}, {"$set": {'user': user}}, upsert=False)
                                resp = 'success'
                            else:
                                approved_user = MongoDBPersistence.predicted_tickets_tbl.find_one({"CustomerID":customer_id, "DatasetID":dataset_id}, {"_id":0, "user":1})
                                approved_user = approved_user['user']
                                logging.info("%s: The ticket with ticket number %s has already been approved by user %s "%(RestService.timestamp(),incidentNumber, approved_user))
                                approved_ticket = MongoDBPersistence.predicted_tickets_tbl.find_one({"CustomerID":customer_id, "DatasetID":dataset_id}, {"_id":0, ticket_id_field_name:1, 'user':1})
                                approved_tickets.append(approved_ticket)  # List of tickets which are already approved

                    try:
                        #--Workload calculation--
                        ResourceMasterData.incident_workload_update(customer_id, dataset_id, incident_lst)
                        # resp='success'
                    except Exception as e:
                        logging.info("%s Error Occured in workload update %s "%(RestService.timestamp(), str(e)))
                        
                    if (approved_tickets):
                        # resp = "found some approved tickets"
                        status = "ApprovedTickets"
                        result = [{"Status": status, "Approved_Tickets": approved_tickets}]
                    else:
                        # resp = "success"
                        status = "success"
                        result = [{"Status": status}]
                    #------------------------
                else:
                    logging.info('%s: Getting empty JSON from Angular component, returning string empty...'%RestService.timestamp())
                    # resp = 'empty'  # No tickets from front end
                    status = "empty"
                    result = [{"Status": status}]
            except Exception as e:
                logging.error('%s: Error occurred: %s '%(RestService.timestamp(),str(e)))
                # resp = 'failure'
                status = "failure"
                result = [{"Status": status}, {"Error": str(e)}]
            return json_util.dumps(result)
        else:
            logging.info("%s You are not logged in please login" %RestService.timestamp())
            status = "No Login Found"
            result = [{"Status": status}]
            return json_util.dumps(result)
