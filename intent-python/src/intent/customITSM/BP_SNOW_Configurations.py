__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

import json
import requests
from bson import json_util
from flask import request
from flask import session
from requests.auth import HTTPBasicAuth
from intent.itsm.servicenow import ServiceNow
from intent.masterdata.resources import ResourceMasterData
from intent.persistence.mappingpersistence import MappingPersistence
from intent.persistence.mongodbpersistence import MongoDBPersistence
from intent.restservice import RestService
from intent.utils.log_helper import get_logger

logging = get_logger(__name__)
# log_setup()
class BP_SNOW_Configurations(object):
    '''
    classdocs
    '''
    
    def __init__(self, params):
        '''
        Constructor
        '''

    @staticmethod
    def remove_tags(text):
        return TAG_RE.sub('', text)

    @staticmethod
    def get_Current_ITSM_tickets(customer_id):    
        try:

            #Fetch tickets through API Call
            #print("fetch tickets")
            IncidentUrl_details = MongoDBPersistence.itsm_details_tbl.find_one({},{"_id":0})
            IncidentUrl = IncidentUrl_details['IncidentUrl']
            userid = IncidentUrl_details['UserID']
            password = IncidentUrl_details['Password']
            response = requests.get(IncidentUrl,auth=HTTPBasicAuth(userid,password))
            print("response success")
            #url = 'https://bp.service-now.com/api/snc/bp_rest_api/getList/19d29df20f9e5b00c1931b2be1050e67/getIncidents?searchVal=assignment_group.name%3DOPS%20-%20Sharepoint%20-%20ITSVC0001041%5Estate%3D12'
            #req = requests.get(url,auth=HTTPBasicAuth('-svc-ifp-spfarmdev03','64Q66E76RI84NC')) 
            if(len(response.json()) >= 1):
             #   print('response')
                API_Response = response.json()
            for key,value in API_Response.items():
                #print(value)
                #print(type(value))
                for item in value:  
                    item['user_status'] = "Not Approved"
                    item['Source'] = "SNOW"
                    item['CustomerID'] = 1
                    item["workload"] = 0.0
                    item["tickets_assigned"] = 0
                    item['DatasetID'] = 1
                    item['configuration_item'] = str(item['cmdb_ci.name'])
                    #print('value of configuration item',item['configuration_item'])
                    print("push tickets to DB")
                    for key1,value1 in item.items():
                        #print(key1)
                        #print(value1)
                        data={}
                        name = key1.split('.')[0]
                        data[name]=value1
                        #print(data)
                        MongoDBPersistence.rt_tickets_tbl.update_one({'number':item['number']},{'$set': data}, upsert=True)
                         
            
                #response_incident = MongoDBPersistence.db.TblIncidentRT.find({})
            
            ServicetaskURL_details = MongoDBPersistence.itsm_details_tbl.find_one({},{"_id":0})
            #print(BPURL_details)
            ServicetaskURL = ServicetaskURL_details['ServicetaskURL']
            userid = ServicetaskURL_details['UserID']
            password = ServicetaskURL_details['Password']
            #print(BPurl)
            response = requests.get(ServicetaskURL,auth=HTTPBasicAuth(userid,password))
            print("response success")
            if(len(response.json()) >= 1):
                API_Response = response.json()
                
            for key,value in API_Response.items():
                #print(value)
                #print(type(value))
                for item in value:
                    item['user_status'] = "Not Approved"
                    item['Source'] = "SNOW"
                    item['CustomerID'] = 1
                    item["workload"] = 0.0
                    item["tickets_assigned"] = 0
                    item['DatasetID'] = 1
                    item['configuration_item'] = str(item['cmdb_ci.name'])
                    item['u_requested_for_user_name'] = item.pop('u_requested_for.user_name')
                    item['u_current_location_name'] = item.pop('u_current_location.name')
                    #print('value of configuration item',item['configuration_item'])
                    print("push tickets to DB")
                    for key1,value1 in item.items():
                        #key1 = key1.replace("u_requested_for.user_name", "u_requested_for_user_name")
                        data={}
                        name = key1.split('.')[0]
                        data[name]=value1
                        MongoDBPersistence.rt_tickets_tbl.update_one({'number':item['number']},{'$set': data}, upsert=True) 

            response_tmp = MongoDBPersistence.db.TblIncidentRT.find({'state':'Assigned','user_status':'Not Approved'})
            return(json_util.dumps(response_tmp))   
        except Exception as e:
            raise

    @staticmethod
    def updatePredictedDetails(customer_id, dataset_id):
        
        field_mapping = MappingPersistence.get_mapping_details(customer_id)
        group_field_name = field_mapping['Group_Field_Name']
        ticket_id_field_name = field_mapping['Ticket_ID_Field_Name']
        status_field_name = field_mapping['Status_Field_Name']
        description_field_name = field_mapping['Description_Field_Name']
        ()
        logging.info('%s: In "updatePredictedDetails()" method'%RestService.timestamp())
        #print(ticket_id_field_name)

        if (session.get('user')):
            # logging.info("%s Catching User Session"%RestService.timestamp())
            user = session['user']
            try:
                #servicenow_incidents = ServiceNow.getClient()
                data = request.get_json()
                #incidentNumber = ''
                incident_lst=[]
                approved_tickets = []
                servicenow_exists = MongoDBPersistence.customer_tbl.find_one({"CustomerID":customer_id},{"_id":0, "SNOWInstance":1})
                if (servicenow_exists):
                    servicenow_flag = 1
                else:
                    servicenow_flag = 0
                if(data):
                    #print(data)
                    for ticketToUpdate in data:
                        if("INC" in ticketToUpdate[ticket_id_field_name]): 
                            print("inside update pred data.1...",data)
                            incidentNumber = ''
                            #incident_lst=[]
                            incidentNumber = ticketToUpdate[ticket_id_field_name]
                            
                            ticket_status = MongoDBPersistence.rt_tickets_tbl.find_one({'CustomerID':customer_id,ticket_id_field_name:incidentNumber, 'DatasetID':dataset_id},{"_id": 0, "user_status": 1,"description":1})
                            #print('user status',user_status)
                            print(ticket_status)
                            if (ticket_status['user_status'] == 'Not Approved'):
                                incident_lst.append(incidentNumber)
                                print(incidentNumber)  
                                #the following code is for inserting approved tickets into Training table for Retraining 
                                ticketToUpdate['CustomerID'] = customer_id
                                ticketToUpdate["DatasetID"] = dataset_id
                                ticketToUpdate['state'] = 2
                                logging.info('Trying to get document from "rt_tickets_tbl"')
                                incidentToinsert = MongoDBPersistence.rt_tickets_tbl.find_one({ticket_id_field_name:incidentNumber})
                                if(not incidentToinsert):
                                    logging.error('Could not get document from "rt_tickets_tbl" for ticket %s'%str(incidentNumber))
                                #incidentToinsert['TrainingFlag'] = 0
                                #try:
                                #    MongoDBPersistence.training_tickets_tbl.update_one({'number': incidentToinsert['number']},{"$set": incidentToinsert},upsert=True)
                                #except Exception as e:
                                #    logging.error('Error: %s'%str(e))
                            
                                for key,value in ticketToUpdate.items():
                                    print("inside update pred data.2...",key,value)
                                    logging.info('Trying to update "predicted_tickets_tbl" with new predicted details')
                                    MongoDBPersistence.predicted_tickets_tbl.update_one({'CustomerID':customer_id,ticket_id_field_name:incidentNumber, 'DatasetID':dataset_id}, {"$set": {key:value}}, upsert=False)
                                    #--update servicenow--
                                    key = key.lower()
                                    if(key=='predicted_assigned_to'):
                                        key='assigned_to'
                                    #if(key != ticket_id_field_name and key != 'DataSetID' and key !='CustomerID'):
                                    if(key != ticket_id_field_name):
                                        if(servicenow_flag):
                                            #if(servicenow_incidents):
                                            if(key == "configuration_item"):
                                                key = "cmdb_ci"
                                            logging.info('Trying to update service now field "%s" with value: "%s"'%(key,value))
                                            #Fetching URL Details
                                            IncidentUrl_details = MongoDBPersistence.itsm_details_tbl.find_one({},{"_id":0})
                                            AssignIncidentURL = IncidentUrl_details['AssignIncidentURL']
                                            userid = IncidentUrl_details['UserID']
                                            password = IncidentUrl_details['Password']
                                            AssignIncidentURL = AssignIncidentURL + incidentNumber
                                            try:
                                                unwanted_lst = ['user','number','customerid','datasetid']
                                                if(key not in unwanted_lst):
                                                    approved_data = {}
                                                    approved_data[key] = value
                                                    #key_value = {}
                                                    #key_value[key] = value
                                                    print(approved_data)
                                                #print(AssignIncidentURL)
                                                headers = {"Content-Type":"application/json","Accept":"application/json"}
                                                response = requests.put(AssignIncidentURL, headers=headers,auth=HTTPBasicAuth(userid,password) ,data=json.dumps(approved_data))
                                                #servicenow_incidents.update(query = {'number': incidentNumber}, payload = {key:value})
                                                
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
                                                                            'approved_data':approved_data
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
                                resp = 'success'
                            else:
                                approved_user = MongoDBPersistence.predicted_tickets_tbl.find_one({"CustomerID":customer_id, "DatasetID":dataset_id}, {"_id":0, "user":1})
                                approved_user = approved_user['user']
                                logging.info("%s: The ticket with ticket number %s has already been approved by user %s "%(RestService.timestamp(),incidentNumber, approved_user))
                                approved_ticket = MongoDBPersistence.predicted_tickets_tbl.find_one({"CustomerID":customer_id, "DatasetID":dataset_id}, {"_id":0, ticket_id_field_name:1, 'user':1})
                                approved_tickets.append(approved_ticket)  # List of tickets which are already approved

                        #------------------------
                        elif("TASK" in ticketToUpdate[ticket_id_field_name]):
                            print("inside update pred data.1...",data)
                            servicetaskNumber = ''
                            #servicetask_lst=[]
                            servicetaskNumber = ticketToUpdate[ticket_id_field_name]
                            incident_lst.append(servicetaskNumber)

                            ticket_status = MongoDBPersistence.rt_tickets_tbl.find_one({'CustomerID':customer_id,ticket_id_field_name:incidentNumber, 'DatasetID':dataset_id},{"_id": 0, "user_status": 1,"description":1})
                            if (ticket_status['user_status'] == 'Not Approved'):
                                incident_lst.append(incidentNumber)
                                    
                                #the following code is for inserting approved tickets into Training table for Retraining 
                                ticketToUpdate['CustomerID'] = customer_id
                                ticketToUpdate["DatasetID"] = dataset_id
                                ticketToUpdate['state'] = 2
                                logging.info('Trying to get document from "rt_tickets_tbl"')
                                servicetaskToinsert =MongoDBPersistence.rt_tickets_tbl.find_one({ticket_id_field_name:servicetaskNumber})
                                if(not servicetaskToinsert):
                                    logging.error('Could not get document from "rt_tickets_tbl" for ticket %s'%str(servicetaskNumber))
                                #servicetaskToinsert['TrainingFlag'] = 0
                                #try:
                                #    MongoDBPersistence.training_tickets_tbl.update_one({ticket_id_field_name: servicetaskToinsert['number']},{"$set": servicetaskToinsert},upsert=True)
                                #except Exception as e:
                                #    logging.error('Error: %s'%str(e))
                            
                            
                                for key,value in ticketToUpdate.items():
                                    print("inside update pred data.2...",key,value)
                                    logging.info('Trying to update "predicted_tickets_tbl" with new predicted details')
                                    MongoDBPersistence.predicted_tickets_tbl.update_one({'CustomerID':customer_id,"number":servicetaskNumber, 'DatasetID':dataset_id}, {"$set": {key:value}}, upsert=False)
                                    #--update servicenow--
                                    key = key.lower()
                                    if(key=='predicted_assigned_to'):
                                        key='assigned_to'
                                    #if(key != 'number' and key != 'DataSetID' and key !='CustomerID'):
                                    if(key != ticket_id_field_name):    
                                        if (servicenow_flag):
                                            #if(servicenow_incidents):
                                            if(key == "configuration_item"):
                                                key = "cmdb_ci"
                                            logging.info('Trying to update service now field "%s" with value: "%s"'%(key,value))
                                            #Fetching URL Details
                                            ServicetaskUrl_details = MongoDBPersistence.itsm_details_tbl.find_one({},{"_id":0})
                                            AssignServiceTaskURL = ServicetaskUrl_details['AssignServiceTaskURL']
                                            userid = ServicetaskUrl_details['UserID']
                                            password = ServicetaskUrl_details['Password']
                                            AssignServiceTaskURL = AssignServiceTaskURL + servicetaskNumber
                                            try:
                                                unwanted_lst = ['user','number','customerid','datasetid']
                                                if(key not in unwanted_lst):
                                                    approved_data = {}
                                                    approved_data[key] = value
                                                    #key_value = {}
                                                    #key_value[key] = value
                                                    print(approved_data)
                                                #print(AssignServiceTaskURL)
                                                headers = {"Content-Type":"application/json","Accept":"application/json"}
                                                response = requests.put(AssignServiceTaskURL, headers=headers,auth=HTTPBasicAuth(userid,password) ,data=json.dumps(approved_data))
                                                #servicenow_incidents.update(query = {'number': incidentNumber}, payload = {key:value})
                                                servicetask_present= None
                                                servicetask_present = MongoDBPersistence.approved_tickets_tbl.find_one({"CustomerID":customer_id,"ticket_number":servicetaskNumber})
                                                logging.info('Tickets Got Approved in SNOW now trying to insert approved details to "approved_tickets_tbl"')
                                                if(servicetask_present is None):
                                                    MongoDBPersistence.approved_tickets_tbl.insert_one({
                                                                            'CustomerID':customer_id,
                                                                            'DatasetID':dataset_id,
                                                                            'UserID':user,
                                                                            'ticket_number':servicetaskNumber,
                                                                            'ticket_description':ticket_status['description'],
                                                                            'approved_data':approved_data
                                                                            })
                                            except:
                                                logging.info("%s: servicenow of ticket with number %s is not possible check if ticket is present in servicenow or not "%(RestService.timestamp(), servicetaskNumber))                                        
                                        else:
                                            logging.info("Servicenow Incident is none updating only DB")
                            #-------------------
                            # End of key, value looping
                                logging.info('%s: Predicted Details has been successfully updated into a collection TblPredictedData by user %s.'%(RestService.timestamp(), user))
                                logging.info('Trying to update document of "rt_tickets_tbl" with "user_status" "Approved"')
                                MongoDBPersistence.rt_tickets_tbl.update_one({'CustomerID':customer_id,ticket_id_field_name: incidentNumber, 'DatasetID':dataset_id}, {"$set": {'user_status':'Approved'}}, upsert=False)
                                logging.info('Trying to update "predicted_tickets_tbl" with approver details')
                                MongoDBPersistence.predicted_tickets_tbl.update_one({'CustomerID':customer_id,ticket_id_field_name:incidentNumber, 'DatasetID':dataset_id}, {"$set": {'user': user}}, upsert=False)
                                resp = 'success'
                            else:
                                approved_user = MongoDBPersistence.predicted_tickets_tbl.find_one({"CustomerID":customer_id, "DatasetID":dataset_id}, {"_id":0, "user":1})
                                approved_user = approved_user['user']
                                logging.info("%s: The ticket with ticket number %s has already been approved by user %s "%(RestService.timestamp(),incidentNumber, approved_user))
                                approved_ticket = MongoDBPersistence.predicted_tickets_tbl.find_one({"CustomerID":customer_id, "DatasetID":dataset_id}, {"_id":0, ticket_id_field_name:1, 'user':1})
                                approved_tickets.append(approved_ticket)  # List of tickets which are already approved
                        else:
                            print('No Incident and ServiceTask tickets')   
                            status = 'failure'
                            result = [{"Status": status}]
                        #---------------------    

                    #--Workload calculation--
                    try:
                        #--Workload calculation--
                        #ResourceMasterData.incident_workload_update(customer_id, dataset_id, incident_lst)
                        status = "success"                    
                        result = [{"Status": status}]
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
                    status = 'empty'
                    result = [{"Status": status}]
            except Exception as e:
                logging.error('%s: Error occurred: %s '%(RestService.timestamp(),str(e)))
                status = 'failure'
                result = [{"Status": status}]
            return json_util.dumps(result)
        else:
            logging.info("%s You are not logged in please login" %RestService.timestamp())
            status = "No Login Found"
            result = [{"Status": status}]
            return json_util.dumps(result)
    
    @staticmethod
    def automaticTicketApproval(customer_id, dataset_id, data=[]):
        #print('automaticTicketApproval',data)
        #get data in [{"Assignment_group": "SAP FICO Support", "Subcategory": "ERP Misc"}]
        try:
            # log_setup()
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
                    incidentNumber = incidentToUpdate['number']
                    incident_lst.append(incidentNumber)  
                    MongoDBPersistence.rt_tickets_tbl.update_one({'CustomerID':customer_id,"number":incidentNumber, 'DatasetID':dataset_id}, {"$set": {'user_status':'Approved'}}, upsert=False)
                    #the following code is for inserting approved tickets into Training table for Retraining 
                    incidentToUpdate['CustomerID'] = customer_id
                    incidentToUpdate["DatasetID"] = dataset_id
                    #print('Hi ')
                    incidentToinsert =MongoDBPersistence.rt_tickets_tbl.find_one({'number':incidentNumber})
                    incidentToinsert['TrainingFlag'] = 0
                    #print(incidentToinsert)
                    try:
                        MongoDBPersistence.training_tickets_tbl.update_one({'number': incidentToinsert['number']},{"$set": incidentToinsert},upsert=True)
                    except Exception as e:
                        print(str(e))
                    
                    
                    
                    for key,value in incidentToUpdate.items():
                        #predicted_tickets.update_one({'CustomerID':customer_id,"Number":incident_number}, {"$set": {key:value}}, upsert=False)
                        MongoDBPersistence.predicted_tickets_tbl.update_one({'CustomerID':customer_id,"number":incidentNumber, 'DatasetID':dataset_id}, {"$set": {key:value}}, upsert=False)
                        
                        #--update servicenow--
                        if (servicenow_flag and ServiceNow.servicenow_incidents!=None):
                            key = key.lower()
                            if(key=='predicted_assigned_to'):
                                key='assigned_to'
                            if(key!='number'):
                                ServiceNow.servicenow_incidents.update(query = {'number': incidentNumber}, payload = {key:value})
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
    
