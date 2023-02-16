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
from intent.restservice import RestService
from intent.masterdata.datasets import DatasetMasterData
from intent.persistence.mappingpersistence import MappingPersistence
from flask import request
from bson import json_util
from datetime import datetime, timedelta
import os
import configparser
from flask import session
from intent.itsm.servicenow import ServiceNow
import importlib
from intent.utils.log_helper import get_logger, log_setup
logging = get_logger(__name__)
# log_setup()

class RB_SNOW_Configurations(object):
    '''
    classdocs
    '''
    c = None
    servicenow_incidents = None
    def __init__(self, params):
        '''
        Constructor
        '''
      
    @staticmethod
    def getClient():    
        try:
            ()
            if(RB_SNOW_Configurations.c is None):   
                # Connect to Service Now using default api method (JSON)
                instance = MongoDBPersistence.customer_tbl.find_one({"CustomerID":1}, {'SNOWInstance':1, '_id':0})
                username = MongoDBPersistence.customer_tbl.find_one({"CustomerID":1}, {'SNOWUserName':1, '_id':0})
                password = MongoDBPersistence.customer_tbl.find_one({"CustomerID":1}, {'SNOWPassword':1, '_id':0})
                RB_SNOW_Configurations.c = pysnow.Client(instance=instance['SNOWInstance'], user=username['SNOWUserName'], password=password['SNOWPassword'])
                #To display actual values of fields instead of external reference link or GUID - Service Now
                RB_SNOW_Configurations.c.parameters.display_value = True
                RB_SNOW_Configurations.c.parameters.exclude_reference_link = True
                RB_SNOW_Configurations.servicenow_incidents = RB_SNOW_Configurations.c.resource(api_path='/table/incident')
            return RB_SNOW_Configurations.servicenow_incidents
        except Exception as e:
             raise
            
    #New Service Now changes
    #@app.route('/serviceNow/<int:customer_id>', methods=['GET'])
    @staticmethod
    def get_Current_ITSM_tickets(customer_id):
        incident_no_lst=[]
        application_groups=[]
        ()
        # user = os.getlogin()s
        if (session.get('user')):
            logging.info("%s Catching User Session"%RestService.timestamp())
            user = session['user']
            logging.info("%s Session catched user as  %s"%(RestService.timestamp(), user))
        else:
            logging.info("%s You are not logged in please login" %RestService.timestamp())
            return "failure"

        field_mapping = MappingPersistence.get_mapping_details(customer_id)
        group_field_name = field_mapping['Group_Field_Name']
        ticket_id_field_name = field_mapping['Ticket_ID_Field_Name']
        status_field_name = field_mapping['Status_Field_Name']
        login_user = MongoDBPersistence.users_tbl.find_one({"UserID": user}, {"_id": 0})
        if (login_user):
            user_role = login_user['Role']
            if (user_role == 'Admin'):
                try:
                    servicenow_incidents = RB_SNOW_Configurations.getClient()
                    
                    application_groups=MongoDBPersistence.db.TblApplication.find().distinct(group_field_name)
                    if(not application_groups):            
                        application_groups = MongoDBPersistence.training_tickets_tbl.find({"CustomerID":customer_id}).distinct(group_field_name)
                        
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
                        queryBuilder= status_field_name + '=1^OR' + status_field_name + '=2^' + group_field_name + '!=is_empty^'
                
                    for app_group in application_groups:
                        queryBuilder = queryBuilder + group_field_name + 'LIKE'+app_group +'^OR'
                
                    response = servicenow_incidents.get(query=queryBuilder[:-3])
                    
                    
                    ############### reassignemnt logic ###############
                    for responce_doc in response.all():
                        logging.info("rt tickets %s with reassignemtn count %s"%(responce_doc[ticket_id_field_name],responce_doc["reassignment_count"]))
                        
                        if(int(responce_doc["reassignment_count"]) <= 1 and responce_doc["assigned_to"] == "" ):
                            #if not responce_doc["assigned_to"]:
                            
                            incident_no_lst.append(responce_doc[ticket_id_field_name]) 

                    ##########################################

                        #incident_no_lst.append(responce_doc[ticket_id_field_name])                
                    #Remove all inicidents from DB, which are not present in Service Now dump
                    MongoDBPersistence.rt_tickets_tbl.update_many({ticket_id_field_name:{'$nin':incident_no_lst}},{'$set':{status_field_name:'closed'}})
                
                
                    datasets = list(MongoDBPersistence.datasets_tbl.find({"CustomerID" : customer_id}))
                    #print(datasets)
                    #initial
                    
                    incident_number_lst=MongoDBPersistence.rt_tickets_tbl.find({},{'_id':0, ticket_id_field_name:1}).distinct(ticket_id_field_name)
                    for record in response.all():
                        
                        if(int(record["reassignment_count"]) <= 1 and record["assigned_to"] == ""):
                            #print("Do")
                            dataset_id = 0
                            logging.info('%s: START - Tickets Update in DB from Service Now....'%(RestService.timestamp()))                
                            if(record[ticket_id_field_name] not in incident_number_lst):
                                #Update status and other columns of Incidents in DB and Insert the new incidents in DB
                                record['CustomerID'] = customer_id
                                record["workload"] = 0.0
                                record["tickets_assigned"] = 0
                                record['user_status'] = 'Not Approved'
                                record['Source'] = 'SNOW'
                                #print("cmdb ci..",record['cmdb_ci'])
                                record['configuration_item']=str(record['cmdb_ci'])
                    
                            for dataset in datasets:
                                fields = dataset['UniqueFields']
                                match_flag = 0
                                for field in fields:
                                    try:
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
                
                            # if(dataset_id == 0):
                            #     logging.info('%s: the ticket (Incident Number: %s) do not match with any of the datasets.'%(RestService.timestamp(),record['number']))
                            #     break
                
            #            if(list(MongoDBPersistence.db.TblIncidentRT.find({"number":record['number']})) == []):    
            #                record['user_status'] = 'Not Approved'
                            #print("record before insertion..",record)
                            MongoDBPersistence.rt_tickets_tbl.update_one({ticket_id_field_name:record[ticket_id_field_name]},{'$set': record}, upsert=True)
                    
                            logging.info('%s: END - Tickets Udapte in DB from Service Now....'%(RestService.timestamp()))
                        
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
                team_id = login_user['TeamID']
                user_dataset_id = MongoDBPersistence.teams_tbl.find_one({"TeamID": int(team_id)},{"_id":0, "DatasetID":1})
                try:
                    servicenow_incidents = RB_SNOW_Configurations.getClient()
                    #Get distinct assignment groups from DB - Incidents are filtered based on these groups

                    application_groups=MongoDBPersistence.db.TblApplication.find().distinct(group_field_name)
                    if(not application_groups):            
                        application_groups = MongoDBPersistence.training_tickets_tbl.find({"CustomerID":customer_id, "DatasetID": user_dataset_id}).distinct(group_field_name)
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
                        queryBuilder= status_field_name + '=1^OR' + status_field_name + '=2^' + group_field_name + '!=is_empty^'
                
                    for app_group in application_groups:
                        queryBuilder = queryBuilder + group_field_name + 'LIKE'+app_group +'^OR'
                
                    response = servicenow_incidents.get(query=queryBuilder[:-3])
                    
                    ############### reassignemnt logic ###############
                    for responce_doc in response.all():
                        logging.info("rt tickets %s with reassignemnt count %s"%(responce_doc[ticket_id_field_name],responce_doc["reassignment_count"]))
                        if(int(responce_doc["reassignment_count"]) <= 1 and responce_doc["assigned_to"] == ""):
                            #print("re")
                            incident_no_lst.append(responce_doc[ticket_id_field_name]) 

                    ###########################################                
                
                    #Remove all inicidents from DB, which are not present in Service Now dump
                    MongoDBPersistence.rt_tickets_tbl.update_many({ticket_id_field_name :{'$nin':incident_no_lst}},{'$set':{status_field_name:'closed'}})
                
                
                    dataset = MongoDBPersistence.datasets_tbl.find_one({"CustomerID" : customer_id, "DatasetID": user_dataset_id['DatasetID']}, {"_id":0})
                    #print(datasets)
                    #initial
                    
                    incident_number_lst=MongoDBPersistence.rt_tickets_tbl.find({},{'_id':0,ticket_id_field_name:1}).distinct(ticket_id_field_name)
                    for record in response.all():
                        if(int(record["reassignment_count"]) <= 1 and record["assigned_to"] == ""):
                            #print("me")
                            dataset_id = 0
                            logging.info('%s: START - Tickets Update in DB from Service Now....'%(RestService.timestamp()))                
                            if(record[ticket_id_field_name] not in incident_number_lst):
                                #Update status and other columns of Incidents in DB and Insert the new incidents in DB
                                record['CustomerID'] = customer_id
                                record["workload"] = 0.0
                                record["tickets_assigned"] = 0
                                record['user_status'] = 'Not Approved'
                                record['Source'] = 'SNOW'
                            # for dataset in datasets:
                            fields = dataset['UniqueFields']
                            match_flag = 0
                            for field in fields:
                                try:
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
                                # break
                            if(dataset_id == 0):
                                logging.info('%s: the ticket (Incident Number: %s) do not match with any of the datasets.'%(RestService.timestamp(),record[ticket_id_field_name]))
                                continue
                
                            # if(dataset_id == 0):
                            #     logging.info('%s: the ticket (Incident Number: %s) do not match with any of the datasets.'%(RestService.timestamp(),record['number']))
                            #     break
                
            #            if(list(MongoDBPersistence.db.TblIncidentRT.find({"number":record['number']})) == []):    
            #                record['user_status'] = 'Not Approved'
                            #print("record before insertion..",record)
                            MongoDBPersistence.rt_tickets_tbl.update_one({ticket_id_field_name:record[ticket_id_field_name]},{'$set': record}, upsert=True)
                    
                            logging.info('%s: END - Tickets Udapte in DB from Service Now....'%(RestService.timestamp()))
                        
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
    

    @staticmethod
    def get_prev_week_openIncidents():
        today = datetime.today()
        one_week_ago = today - timedelta(days=100)
        ()
        customer_details = MongoDBPersistence.customer_tbl.find_one({}, {"_id":0})
        customer_id = customer_details['CustomerID']
        field_mapping = MappingPersistence.get_mapping_details(customer_id)
        group_field_name = field_mapping['Group_Field_Name']
        ticket_id_field_name = field_mapping['Ticket_ID_Field_Name']
        status_field_name = field_mapping['Status_Field_Name']
        sys_created_on_field_name = field_mapping['Sys_Created_On_Field_Name']
        incident_no_lst=[]
        application_groups=[]
        print("here")
        try:
            servicenow_incidents = RB_SNOW_Configurations.getClient()
            
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
            logging.error("error %s"%(str(e)))
            return 'exception'

    
    @staticmethod
    def get_prev_week_closedIncidents():
        today = datetime.today()
        one_week_ago = today - timedelta(days=100)

        customer_details = MongoDBPersistence.customer_tbl.find_one({}, {"_id":0})
        customer_id = customer_details['CustomerID']
        field_mapping = MappingPersistence.get_mapping_details(customer_id)
        group_field_name = field_mapping['Group_Field_Name']
        ticket_id_field_name = field_mapping['Ticket_ID_Field_Name']
        status_field_name = field_mapping['Status_Field_Name']
        closed_at_field_name = field_mapping['Closed_At_Field_Name']
        incident_no_lst=[]
        application_groups=[]
        print("here")
        try:
            ()
            servicenow_incidents = RB_SNOW_Configurations.getClient()
            
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
            logging.error("error %s"%(str(e)))
            return 'exception'
    
    @staticmethod
    def updatePredictedDetails(customer_id, dataset_id):
        ()
        logging.info("Going for default flow in update Predicted Field RB.")
        field_mapping = MappingPersistence.get_mapping_details(customer_id)
        group_field_name = field_mapping['Group_Field_Name']
        ticket_id_field_name = field_mapping['Ticket_ID_Field_Name']
        status_field_name = field_mapping['Status_Field_Name']
        description_field_name = field_mapping['Description_Field_Name']
        logging.info('%s: In "updatePredictedDetails()" method'%RestService.timestamp())
        approved_tickets = {}
        if (session.get('user')):
            user = session['user']
            try:
                servicenow_incidents = ServiceNow.getClient()
                data = request.get_json()

                print("User Selected Data for RB", data)
                incidentNumber = ''
                incident_lst=[]
                
                servicenow_exists = MongoDBPersistence.customer_tbl.find_one({"CustomerID":customer_id},{"_id":0, "SNOWInstance":1})
                if (servicenow_exists):
                    servicenow_flag = 1
                else:
                    servicenow_flag = 0
                if(data):
                    for incidentToUpdate in data: 
                        approved_data = {}
                        incidentNumber = incidentToUpdate[ticket_id_field_name]
                        predicted_field = MongoDBPersistence.predicted_tickets_tbl.find_one({"CustomerID":1, "DatasetID": dataset_id, ticket_id_field_name: incidentNumber}, {"_id": 0, "predicted_fields": 1})
                        # print(predicted_field)
                        # pred= []
                        # for key,value in predicted_field.items():
                        #     preds = pred.append(value)
                        # Intent_predicted_data = pred[0]
                        # print(Intent_predicted_data)
                        


                        ticket_status = MongoDBPersistence.rt_tickets_tbl.find_one({"CustomerID":1, "DatasetID": dataset_id, ticket_id_field_name: incidentNumber}, {"_id": 0, "user_status": 1,"description":1})
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
                                # MongoDBPersistence.predicted_tickets_tbl.update_one({'CustomerID':customer_id,ticket_id_field_name:incidentNumber, 'DatasetID':dataset_id}, {"$set": {'user': user}}, upsert=False)
                                #--update servicenow--
                                key = key.lower()
                                #print(key)
                                # if(key=='predicted_assigned_to'):
                                #     logging.info('Skip Assignment')
                                if(key != ticket_id_field_name and key !='predicted_assigned_to'):
                                    if (servicenow_flag):
                                        if(servicenow_incidents):
                                            logging.info('Trying to update service now field "%s" with value: "%s"'%(key,value))
                                            try:
                                                unwanted_lst = ['user','number','customerid','datasetid']
                                                if(key not in unwanted_lst):
                                                    approved_data[key] = value
                                                #print("keys ",key ,"vlaue ",value)
                                                # if(str(key == resolution_notes)):
                                                #     key = work_notes


                                                if(key.lower() =="priority"):
                                                    #print("Key passed here is...",key)
                                                    priority_mapping_doc = MongoDBPersistence.priority_mapping_tbl.find_one({},{"Priority_Field_Mapping":{"$elemMatch":{"Field_Name":value}}})
                                                    #print("Priority mapping from DB...",priority_mapping_doc)
                                                    urgency = priority_mapping_doc['Priority_Field_Mapping'][0]['Urgency']
                                                    impact = priority_mapping_doc["Priority_Field_Mapping"][0]['Impact']
                                                    #print("Priority values from DB...",urgency,impact)
                                                    response = servicenow_incidents.update(query = {ticket_id_field_name: incidentNumber}, payload = {"impact":impact})
                                                    response = servicenow_incidents.update(query = {ticket_id_field_name: incidentNumber}, payload = {"urgency":urgency})
                                                    # response = servicenow_incidents.update(query = {ticket_id_field_name: incidentNumber}, payload = {"Priority":value})
                                                    

                                                #Priority changes - SNOW - END

                                                else:
                                                    response = servicenow_incidents.update(query = {ticket_id_field_name: incidentNumber}, payload = {key:value})
                                                
                                                
                                                
                                                #print("response ",response)
                                                inci_present= None
                                                inci_present = MongoDBPersistence.approved_tickets_tbl.find_one({"CustomerID":customer_id,"ticket_number":incidentNumber})
                                                logging.info('Tickets Got Approved in SNOW now trying to insert approved details to "approved_tickets_tbl"')
                                                if(inci_present is None):
                                                    MongoDBPersistence.approved_tickets_tbl.insert_one({
                                                                            'CustomerID':customer_id,
                                                                            'DatasetID':dataset_id,
                                                                            'UserID':user,
                                                                            'ticket_number':incidentNumber,
                                                                            'ticket_description':ticket_status['description'],
                                                                            'approved_data':approved_data,
                                                                            'Intent_predicted_data':predicted_field
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
                            logging.info('Trying to update "predicted_tickets_tbl" with approver details')
                            MongoDBPersistence.predicted_tickets_tbl.update_one({'CustomerID':customer_id,ticket_id_field_name:incidentNumber, 'DatasetID':dataset_id}, {"$set": {'user': user}}, upsert=False)
                            status = "success"
                            result = [{"Status": status}]
                        else:
                            approved_user = MongoDBPersistence.predicted_tickets_tbl.find_one({"CustomerID":customer_id, "DatasetID":dataset_id}, {"_id":0, "user":1})
                            approved_user = approved_user['user']
                            logging.info("%s: The ticket with ticket number %s has already been approved by user %s "%(RestService.timestamp(),incidentNumber, approved_user))
                            approved_ticket = MongoDBPersistence.predicted_tickets_tbl.find_one({"CustomerID":customer_id, "DatasetID":dataset_id}, {"_id":0, ticket_id_field_name:1, 'user':1})
                            approved_tickets.append(approved_ticket)  # List of tickets which are already approved
                
                    try:
                        #--Workload calculation--
                        ResourceMasterData.incident_workload_update(customer_id, dataset_id, incident_lst)
                        status = "success"
                        result=[{"Status": status}]
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

    @staticmethod
    def automaticTicketApproval(customer_id, dataset_id, data=[]):
        #        print('automaticTicketApproval',data)
        #get data in [{"Assignment_group": "SAP FICO Support", "Subcategory": "ERP Misc"}]
        field_mapping = MappingPersistence.get_mapping_details(customer_id)
        group_field_name = field_mapping['Group_Field_Name']
        ticket_id_field_name = field_mapping['Ticket_ID_Field_Name']
        status_field_name = field_mapping['Status_Field_Name']
        description_field_name = field_mapping['Description_Field_Name']
        try:
            ()
            #data=list(data)
            incidentNumber = ''
            incident_lst=[]
            servicenow_exists = MongoDBPersistence.customer_tbl.find_one({"CustomerID":customer_id},{"_id":0, "SNOWInstance":1})
            if (servicenow_exists):
                servicenow_flag = 1
            else:
                servicenow_flag = 0
            if(data):
                #data = data[0]
                for incidentToUpdate in data:
                    incidentNumber = incidentToUpdate[ticket_id_field_name]
                    incident_lst.append(incidentNumber)  
                    MongoDBPersistence.rt_tickets_tbl.update_one({'CustomerID':customer_id,ticket_id_field_name:incidentNumber, 'DatasetID':dataset_id}, {"$set": {'user_status':'Approved'}}, upsert=False)
                    #the following code is for inserting approved tickets into Training table for Retraining 
                    incidentToUpdate['CustomerID'] = customer_id
                    incidentToUpdate["DatasetID"] = dataset_id
                    #print('Hi ')
                    incidentToinsert =MongoDBPersistence.rt_tickets_tbl.find_one({ticket_id_field_name:incidentNumber})
                    incidentToinsert['TrainingFlag'] = 0
                    #print(incidentToinsert)
                    try:
                        MongoDBPersistence.training_tickets_tbl.update_one({ticket_id_field_name: incidentToinsert[ticket_id_field_name]},{"$set": incidentToinsert},upsert=True)
                    except Exception as e:
                        print(str(e))
                    
                    
                    
                    for key,value in incidentToUpdate.items():
                        #predicted_tickets.update_one({'CustomerID':customer_id,"Number":incident_number}, {"$set": {key:value}}, upsert=False)
                        MongoDBPersistence.predicted_tickets_tbl.update_one({'CustomerID':customer_id,ticket_id_field_name:incidentNumber, 'DatasetID':dataset_id}, {"$set": {key:value}}, upsert=False)
                        
                        #--update servicenow--
                        if (servicenow_flag and ServiceNow.servicenow_incidents!=None):
                            key = key.lower()
                            if(key=='predicted_assigned_to'):
                                key='assigned_to'
                            if(key!=ticket_id_field_name):
                                ServiceNow.servicenow_incidents.update(query = {ticket_id_field_name: incidentNumber}, payload = {key:value})
                        #-------------------
    
                    logging.info('%s: Predicted Details has been successfully updated into a collection TblPredictedData.'%RestService.timestamp())
                    resp = 'success'
                #--Workload calculation--
                ResourceMasterData.incident_workload_update(customer_id, dataset_id, incident_lst)
                resp='success'
                #------------------------
            else:
                logging.info('%s: Getting empty JSON from Angular component, returning string empty...'%RestService.timestamp())
                resp = 'empty'
        except Exception as e:
            logging.error('%s: Error occurred: %s '%(RestService.timestamp(),str(e)))
            resp = 'failure'

        return resp
