__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

from intent.persistence.mongodbpersistence import MongoDBPersistence
from intent.persistence.mappingpersistence import MappingPersistence
from intent.restservice import RestService
from intent.masterdata.datasets import DatasetMasterData
from intent.masterdata.resources import ResourceMasterData
from flask import request
from bson import json_util
import requests
import json
import re
import time
#import logging
import configparser
from flask import session
from intent.utils.log_helper import get_logger, log_setup
logging = get_logger(__name__)
# log_setup()
app = RestService.getApp();
TAG_RE = re.compile(r'<[^>]+>')

class LTFS_ManageEngine_Configurations(object):
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
            # log_setup()
           # cust_name = MongoDBPersistence.customer_tbl.find_one({'CustomerID':customer_id},{'CustomerName':1, '_id':0})['CustomerName']
            MEURL_details = MongoDBPersistence.itsm_details_tbl.find_one({}, {"_id":0})
            ManageEngineurl = MEURL_details['MEUrl']
            print(ManageEngineurl)
            MEAuth_Token = MEURL_details['MEAuthToken']
            response = requests.get(ManageEngineurl,headers={"Accept":"application/vnd.manageengine.sdp.v3+json",'Authorization': MEAuth_Token})
            header = {"Accept":"application/vnd.manageengine.sdp.v3+json","Authorization":MEAuth_Token}

            ServiceRequestIDJson={}
            RTTicketDump = []
            if(response):
                #API_Response = response.json()
                finaloutput=[]
                j=1
                for i in range(0, 5):
                    listInfo = {"list_info": {"start_index":j, "row_count": 100,
                                "sort_fields": [{"field": "created_time","order": "desc"}],
                                "search_criteria": [{"field": "status.in_progress", "condition": "is", "values": [ True ]},
                                {"field": "status.name", "condition": "is", "logical_operator": "or", "values": [ "Open" ]}]}};
                    # listInfo = {"list_info":{"start_index":j,"row_count":100,
                    #             "sort_fields": [{"field": "created_time","order": "desc"}],
                    #             "fields_required": ["status", "created_time", "group", "id", "display_id"],
                    #             "search_criteria": [{"field": "group.name","condition": "is","value": "Shift Lead L1 Support Team"}]}};
                    listInfo = json.dumps(listInfo)
                    getParams = {'input_data':listInfo}
                    proxies={''}
                    r = requests.get(ManageEngineurl,headers = header, proxies=proxies, params = getParams)
                    time.sleep(5)
                    j = j + 100
                    #print(r.json())
                    finaloutput.append(r.json())


                dictList = []
                for key1 in finaloutput:                    
                    for dictKey in key1.keys():
                        if (dictKey == 'requests'):                                         
                            #print(output[key])
                            
                            temp_dict = {}
                            for item in key1[dictKey]:
                                temp_dict = {}                
                                for key, value in item.items():
                                    temp_dict[key] = value
                                dictList.append(temp_dict)
                
                #print("loop done....",len(dictList))
                # for ticket in dictList:
                #         print(ticket['id'])


                # for key in API_Response.keys():
                #     if (key == 'requests'):                                         
                #         #print(output[key])
                #         dictList = []
                #         temp_dict = {}
                #         for item in API_Response[key]:
                #             temp_dict = {}
                #             for key, value in item.items():
                #                 temp_dict[key] = value
                #             dictList.append(temp_dict)
            
                # for ticket in dictList:
                #     print(ticket['id'])

                assigned_incdnt_no_lst = []
                for ticket in dictList:
                    ServiceRequestIDJson={}
                    ServiceRequestIDJson["id"]=str(ticket['id'])
                    ServiceRequestIDJson["CustomerID"] = customer_id
                    ServiceRequestIDJson["workload"] = 0.0
                    ServiceRequestIDJson["tickets_assigned"] = 0
                    ServiceRequestIDJson["user_status"] = 'Not Approved'
                    ServiceRequestIDJson["DatasetID"] = 1
                    ServiceRequestIDJson["Source"] = "ManageEngine"
                    #Noor Added
                    if(ticket['status'] in ['Assigned','Acknowledged & Work-In-Progress']):
                        assigned_incdnt_no_lst = str(ticket['id'])

                    urlRequest = ManageEngineurl + str(ticket['id'])
                    
                    #urlRequest = "https://servicedesk.ltfs.com/app/itdesk/api/v3/requests/" + str(ticket['id'])
                    #print(ticket)
                    header = {"Accept":"application/vnd.manageengine.sdp.v3+json","Authorization":MEAuth_Token}
                    reqData = requests.get(urlRequest,headers=header)
                    #reqData = requests.get(urlRequest,headers={'Authorization': '0b77d111b594e9a30155555aacf95f3d'})
                    #print(reqData)
                    servRequestJson = reqData.json()    

                    field_mapping = MappingPersistence.get_mapping_details(customer_id)
                    DB_Subject = field_mapping['Subject_Field_Name']
                    DB_Description = field_mapping['Description_Field_Name']
                    DB_Category = field_mapping['Category_Field_Name']
                    DB_SubCategory =field_mapping['Subcategory_Field_Name']
                    DB_Item = field_mapping['Item_Field_Name']
                    DB_Status = field_mapping['Status_Field_Name']
                    DB_Group = field_mapping['Group_Field_Name']
                    DB_RequestId = field_mapping['RequestID_Field_Name']
                    DB_Technician = field_mapping['Technician_Field_Name']
                    DB_Priority = field_mapping['Priority_Field_Name']
                    DB_ServiceReqType = field_mapping['ServiceReqType_Field_Name']
                    DB_ReqType = field_mapping['ReqType_Field_Name']
                    # 
                    for key,value in servRequestJson["request"].items():
                        
                        if(key ==DB_Subject):
                            ServiceRequestIDJson[DB_Subject] = value

                        if(key ==DB_RequestId):
                            ServiceRequestIDJson[DB_RequestId] = value
                            #print(value)
                        
                        # if(key ==DB_Technician):
                        #     ServiceRequestIDJson[DB_Technician] = value

                        if(key ==DB_Description):
                            parsedData = LTFS_ManageEngine_Configurations.remove_tags(str(value))
                            parsedData = parsedData.replace("&nbsp;","")
                            ServiceRequestIDJson[DB_Description] = str(parsedData)
                            
                        if(type(value) == dict):
                            item = ''
                            for objKey,objValue in value.items():
                                
                                if(key ==DB_Category):
                                    ServiceRequestIDJson[DB_Category] = value['name']
                                    category = str(value['name'])

                                if(key ==DB_SubCategory):
                                    ServiceRequestIDJson[DB_SubCategory] = value['name']
                                    subcategory = str(value['name'])

                                if(key ==DB_Status):
                                    ServiceRequestIDJson[DB_Status] = value['name']
                                    status = str(value['name'])

                                if(key == DB_Item):
                                    ServiceRequestIDJson[DB_Item] = value['name']
                                    item = str(value['name'])

                                if(key ==DB_Group):
                                    ServiceRequestIDJson[DB_Group] = value['name']
                                    group = str(value['name'])
                                
                                if(key ==DB_Technician):
                                    ServiceRequestIDJson[DB_Technician] = value['name']
                                    technician = str(value['name'])

                                if(key ==DB_Priority):
                                    ServiceRequestIDJson[DB_Priority] = value['name']
                                    priority = str(value['name'])
                                
                                # if(key ==DB_ServiceReqType):
                                #     ServiceRequestIDJson[DB_ServiceReqType] = value['udfchar16']
                                #     servicereqtype = str(value['udfchar16'])
                                if(key ==DB_ReqType):
                                    ServiceRequestIDJson[DB_ReqType] = value['name']
                                    reqtype = str(value['name'])
                                

                    #if item and not item.isspace():
                    #print("bfore insert into DB...",item)
                    #and item != ''
                    if 'item' not in ServiceRequestIDJson:
                        ServiceRequestIDJson[DB_Item] = ""
                    if 'category' not in ServiceRequestIDJson:
                        ServiceRequestIDJson[DB_Category] = ""  
                    if 'subcategory' not in ServiceRequestIDJson:
                        ServiceRequestIDJson[DB_SubCategory] = ""
                    if 'group' not in ServiceRequestIDJson:
                        ServiceRequestIDJson[DB_Group] = "" 
                    if 'technician' not in ServiceRequestIDJson:
                        ServiceRequestIDJson[DB_Technician] = "" 
                    if 'priority' not in ServiceRequestIDJson:
                        ServiceRequestIDJson[DB_Priority] = "" 
                    # if 'servicereqtype' not in ServiceRequestIDJson:
                    #     ServiceRequestIDJson[DB_ServiceReqType] = ""
                    if 'reqtype' not in ServiceRequestIDJson:
                        ServiceRequestIDJson[DB_ReqType] = ""
                    #if status == "Open" and "item" in ServiceRequestIDJson:
                        #print("insert into DB...",item)
                    RTTicketDump.append(ServiceRequestIDJson)
                    MongoDBPersistence.rt_tickets_tbl.update_one({'id': ServiceRequestIDJson["id"]},{'$set': ServiceRequestIDJson}, upsert=True)
                
                if(r and len(assigned_incdnt_no_lst) != 0):
                    logging.info('Trying to call incident_workload_update() method of ResourceMasterData to calculate workload for tickets which are not New')
                    ResourceMasterData.incident_workload_update(customer_id, dataset_id, assigned_incdnt_no_lst)
                # else:
                #     logging.info('%s: Could not get tickets from Manage Engine'%(RestService.timestamp()))
                #     return 'no tickets found in Manage Engine' 
                #print("final output in Manage Engine",RTTicketDump)
            return json_util.dumps(RTTicketDump)
        except Exception as e:
             raise

    @staticmethod
    def updatePredictedDetails(customer_id, dataset_id):
        field_mapping = MappingPersistence.get_mapping_details(customer_id)
        ticket_id_field_name = field_mapping['Ticket_ID_Field_Name']
        DB_Category = field_mapping['Category_Field_Name']
        DB_SubCategory =field_mapping['Subcategory_Field_Name']
        DB_Group = field_mapping['Group_Field_Name']
        DB_Technician = field_mapping['Technician_Field_Name']
        # log_setup()
        logging.info('%s: In "updatePredictedDetails()" LTFS method'%RestService.timestamp())
        MEURL_details = MongoDBPersistence.itsm_details_tbl.find_one({}, {"_id":0})
        ManageEngineurl = MEURL_details['MEUrl']
        MEAuth_Token = MEURL_details['MEAuthToken']
        header = {"Accept":"application/vnd.manageengine.sdp.v3+json","Authorization":MEAuth_Token,"Content-Type":"application/x-www-form-urlencoded"}
        proxies={'https':'https:// Nidhi_Ratnawat:LnT@2019@10.81.82.184:80/'}
        print("Manage Engine User Check......")
        approved_tickets = []
        if (session.get('user')):
            # logging.info("%s Catching User Session"%RestService.timestamp())
            user = session['user']
            
            print("Approve in progress.....")
            try:
                #manageengine_incidents = LTFS_ManageEngine_Configurations.get_Current_ITSM_tickets(customer_id)
                manageengine_incidents = MongoDBPersistence.rt_tickets_tbl.find({},{'_id':0})
                data = request.get_json()
                print("Approve data Fetched.....")
                print(data)
                incidentNumber = ''
                incident_lst=[]
                config = configparser.ConfigParser()
                config["DEFAULT"]['path'] = "config/"
                config.read(config["DEFAULT"]["path"]+"Intent.ini")
                servicereq = str(config["LTFSServiceRequestField"]["servicereq"])
                
                if(data):
                    for incidentToUpdate in data: 
                        approved_data = {}
                        incidentNumber = incidentToUpdate[ticket_id_field_name]
                        listInfo = {}
                        listInfo['request'] = {}
                        urlRequest = ManageEngineurl + incidentNumber
                        ticket_status = MongoDBPersistence.rt_tickets_tbl.find_one({"CustomerID":1, "DatasetID": dataset_id, ticket_id_field_name: incidentNumber}, {"_id": 0, "user_status": 1,"description":1})
                        if (ticket_status['user_status'] == 'Not Approved'):
                            incident_lst.append(incidentNumber)
                            logging.info('Trying to update document of "rt_tickets_tbl" with "user_status" "Approved"')
                            #MongoDBPersistence.rt_tickets_tbl.update_one({'CustomerID':customer_id,ticket_id_field_name: incidentNumber, 'DatasetID':dataset_id}, {"$set": {'user_status':'Approved'}}, upsert=False)
                            #the following code is for inserting approved tickets into Training table for Retraining 
                            incidentToUpdate['CustomerID'] = customer_id
                            incidentToUpdate["DatasetID"] = dataset_id
                            logging.info('Trying to get document from "rt_tickets_tbl"')
                            incidentToinsert =MongoDBPersistence.rt_tickets_tbl.find_one({ticket_id_field_name:incidentNumber})
                            if(not incidentToinsert):
                                logging.error('Could not get document from "rt_tickets_tbl" for ticket %s'%str(incidentNumber))
                            incidentToinsert['TrainingFlag'] = 0
                            try:
                                MongoDBPersistence.training_tickets_tbl.update_one({ticket_id_field_name: incidentToinsert[ticket_id_field_name]},{"$set": incidentToinsert},upsert=True)
                            except Exception as e:
                                logging.error('Error: %s'%str(e))
                            #print(incidentToUpdate)
                            for key,value in incidentToUpdate.items():
                                logging.info('Trying to update "predicted_tickets_tbl" with new predicted details')
                                MongoDBPersistence.predicted_tickets_tbl.update_one({'CustomerID':customer_id,ticket_id_field_name:incidentNumber, 'DatasetID':dataset_id}, {"$set": {key:value}}, upsert=False)
                                #--update manageengine--
                                key = key.lower()
                                if(key=='predicted_assigned_to'):
                                    key = DB_Technician
                                    if str(value) != "":
                                        technical={}
                                        finaltechnical={}
                                        technical["name"] = value
                                        emailid = MongoDBPersistence.resource_details_tbl.find_one({'CustomerID':customer_id, 'DatasetID':dataset_id, 'resource_name':value},{'email_id':1, '_id':0})['email_id']
                                        technical["email_id"] = emailid
                                        listInfo['request'][key] = technical
                                if(key != ticket_id_field_name):                                     
                                    if(manageengine_incidents):
                                        logging.info('Trying to update Manage Engine field "%s" with value: "%s"'%(key,value))
                                        if (key == DB_Category):
                                            category={}
                                            finalCat={}
                                            category["name"] = value
                                            finalCat[DB_Category]=category
                                            listInfo['request']['category'] = finalCat['category'] 
                                        elif(key == DB_SubCategory):
                                            subcategory={}
                                            finalSubCat={}
                                            subcategory["name"] = value
                                            finalSubCat[DB_SubCategory]=subcategory
                                            listInfo['request']['subcategory'] = finalSubCat['subcategory']
                                        elif(key == DB_Group):
                                            group={}
                                            finalgroup={}
                                            group["name"] = value
                                            finalgroup[DB_Group]=group
                                            listInfo['request']['group'] = finalgroup['group']
                                    else:
                                        logging.info("Manage Engine Incident is none updating only DB")
                                
                                #Track
                                #Create / Update in approve table whose tickets are approved 
                                try:
                                    unwanted_lst = ['user','number','customerid','datasetid',ticket_id_field_name]
                                    if(key not in unwanted_lst):
                                        approved_data[key] = value
                                    inci_present= None
                                    inci_present = MongoDBPersistence.approved_tickets_tbl.find_one({"CustomerID":customer_id,ticket_id_field_name:incidentNumber})
                                    logging.info('Tickets Got Approved in Manage Engine now trying to insert approved details to "approved_tickets_tbl"')
                                    if(inci_present is None):
                                        MongoDBPersistence.approved_tickets_tbl.insert_one({
                                                                'CustomerID':customer_id,
                                                                'DatasetID':dataset_id,
                                                                'UserID':user,
                                                                'id':incidentNumber,
                                                                'ticket_description':ticket_status['description'],
                                                                'approved_data':approved_data
                                                                })
                                    else:
                                        #MongoDBPersistence.approved_tickets_tbl.update_one({'CustomerID':customer_id,ticket_id_field_name: incidentNumber, 'DatasetID':dataset_id},{'approved_data':approved_data},, upsert=False)
                                        if((key != 'datasetid' and key !='customerid') and key != 'id'):
                                            approved_data[key] = value
                                            MongoDBPersistence.approved_tickets_tbl.update_one({'CustomerID':customer_id,ticket_id_field_name:incidentNumber, 'DatasetID':dataset_id}, {"$set": {'approved_data': approved_data}}, upsert=False)
                                except:
                                    logging.info("%s: Manage Engine of ticket with number %s is not possible check if ticket is present in manage engine or not "%(RestService.timestamp(), incidentNumber))
                            #if(key !="datasetid" and key!="customerid"):  
                            listInfo = json.dumps(listInfo)
                            logging.info('Json in Manage Engine insertion %s'%listInfo)      
                            response = requests.put(urlRequest,headers=header,proxies=proxies,params=getParams)
                            print(response)
                            #-------------------
                            # End of key, value looping
                            logging.info('%s: Predicted Details has been successfully updated into a collection TblPredictedData by user %s.'%(RestService.timestamp(), user))
                            logging.info('Trying to update document of "rt_tickets_tbl" with "user_status" "Approved"')
                            #print(ticket_id_field_name + incidentNumber)
                            MongoDBPersistence.rt_tickets_tbl.update_one({'CustomerID':customer_id,ticket_id_field_name: incidentNumber, 'DatasetID':dataset_id}, {"$set": {'user_status':'Approved'}}, upsert=False)
                            logging.info('Trying to update "predicted_tickets_tbl" with approver details')
                            MongoDBPersistence.predicted_tickets_tbl.update_one({'CustomerID':customer_id,ticket_id_field_name:incidentNumber, 'DatasetID':dataset_id}, {"$set": {'user': user}}, upsert=False)
                            status = "success"
                            result=[{"Status": status}]
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
                else:
                    logging.info('%s: Getting empty JSON from Angular component, returning string empty...'%RestService.timestamp())
                    status = "empty"
                    result = [{"Status": status}]
            except Exception as e:
                print("Approve error")
                logging.error('%s: Error occurred: %s '%(RestService.timestamp(),str(e)))
                status = "failure"
                result = [{"Status": status}, {"Error": str(e)}]
            return json_util.dumps(result)
            #return json_util.dumps(resp)
        else:
            logging.info("%s You are not logged in please login" %RestService.timestamp())
            status = "No Login Found"
            result = [{"Status": status}]
            return json_util.dumps(result)

    @staticmethod
    def automaticTicketApproval(customer_id, dataset_id, data=[]):
        print('automaticTicketApproval',data)
        # log_setup()
        field_mapping = MappingPersistence.get_mapping_details(customer_id)
        group_field_name = field_mapping['Group_Field_Name']
        ticket_id_field_name = field_mapping['Ticket_ID_Field_Name']
        status_field_name = field_mapping['Status_Field_Name']
        description_field_name = field_mapping['Description_Field_Name']
        technician_name = field_mapping['Technician_Field_Name']
        DB_Category = field_mapping['Category_Field_Name']
        DB_SubCategory =field_mapping['Subcategory_Field_Name']
        MEURL_details = MongoDBPersistence.itsm_details_tbl.find_one({}, {"_id":0})
        ManageEngineurl = MEURL_details['MEUrl']
        MEAuth_Token = MEURL_details['MEAuthToken']
        header = {"Accept":"application/vnd.manageengine.sdp.v3+json","Authorization":MEAuth_Token,"Content-Type":"application/x-www-form-urlencoded"}
        proxies={'https':'https:// Nidhi_Ratnawat:LnT@2019@10.81.82.184:80/'}
        try:
            incidentNumber = ''
            incident_lst=[]
            manageengine_incidents = MongoDBPersistence.rt_tickets_tbl.find({},{'_id':0})
            if(data):
                for incidentToUpdate in data:
                    approved_data = {}
                    incidentNumber = incidentToUpdate[ticket_id_field_name]
                    listInfo = {}
                    listInfo['request'] = {}
                    urlRequest = ManageEngineurl + incidentNumber
                    ticket_status = MongoDBPersistence.rt_tickets_tbl.find_one({"CustomerID":1, "DatasetID": dataset_id, ticket_id_field_name: incidentNumber}, {"_id": 0, "user_status": 1,"description":1})
                    if (ticket_status['user_status'] == 'Not Approved'):
                        incidentNumber = incidentToUpdate[ticket_id_field_name]
                        incident_lst.append(incidentNumber)  
                        incidentToUpdate['CustomerID'] = customer_id
                        incidentToUpdate["DatasetID"] = dataset_id
                        incidentToinsert =MongoDBPersistence.rt_tickets_tbl.find_one({ticket_id_field_name:incidentNumber})
                        incidentToinsert['TrainingFlag'] = 0
                        urlRequest = ManageEngineurl + incidentNumber
                        try:
                            MongoDBPersistence.training_tickets_tbl.update_one({ticket_id_field_name: incidentToinsert[ticket_id_field_name]},{"$set": incidentToinsert},upsert=True)
                        except Exception as e:
                            print(str(e))

                        for key,value in incidentToUpdate.items():
                            MongoDBPersistence.predicted_tickets_tbl.update_one({'CustomerID':customer_id,ticket_id_field_name:incidentNumber, 'DatasetID':dataset_id}, {"$set": {key:value}}, upsert=False)
                            #--update Manage Engine--
                            if (manageengine_incidents!=None):
                                key = key.lower()
                                if(key=='predicted_assigned_to'):
                                    key = DB_Technician
                                    if str(value) != "":
                                        technical={}
                                        finaltechnical={}
                                        technical["name"] = value
                                        emailid = MongoDBPersistence.resource_details_tbl.find_one({'CustomerID':customer_id, 'DatasetID':dataset_id, 'resource_name':value},{'email_id':1, '_id':0})['email_id']
                                        technical["email_id"] = emailid
                                        listInfo['request'][key] = technical
                                elif(key!=ticket_id_field_name):
                                    if(manageengine_incidents):
                                        logging.info('Trying to Auto update Manage Engine field "%s" with value: "%s"'%(key,value))
                                        listInfo = {"request":{key:value}}
                                        if (key == DB_Category):
                                            category={}
                                            finalCat={}
                                            category["name"] = value
                                            finalCat[DB_Category]=category
                                            listInfo = {"request":finalCat}
                                        elif(key == DB_SubCategory):
                                            subcategory={}
                                            finalSubCat={}
                                            subcategory["name"] = value
                                            finalSubCat[DB_SubCategory]=subcategory
                                            listInfo['request']['subcategory'] = finalSubCat['subcategory']
                                        elif(key == group_field_name):
                                            group={}
                                            finalgroup={}
                                            group["name"] = value
                                            finalgroup[DB_Group]=group
                                            listInfo['request'][DB_Group] = finalgroup[DB_Group]
                                    else:
                                        logging.info("Manage Engine Incident is none Auto updating only DB")
                                #Track
                                #Create / Update in approve table whose tickets are approved 
                                try:
                                    unwanted_lst = ['user','number','customerid','datasetid',ticket_id_field_name]
                                    if(key not in unwanted_lst):
                                        approved_data[key] = value
                                    inci_present= None
                                    inci_present = MongoDBPersistence.approved_tickets_tbl.find_one({"CustomerID":customer_id,ticket_id_field_name:incidentNumber})
                                    logging.info('Tickets Got Approved in Manage Engine now trying to insert approved details to "approved_tickets_tbl"')
                                    if(inci_present is None):
                                        MongoDBPersistence.approved_tickets_tbl.insert_one({
                                                                'CustomerID':customer_id,
                                                                'DatasetID':dataset_id,
                                                                'UserID':user,
                                                                'id':incidentNumber,
                                                                'ticket_description':ticket_status['description'],
                                                                'approved_data':approved_data
                                                                })
                                    else:
                                        #MongoDBPersistence.approved_tickets_tbl.update_one({'CustomerID':customer_id,ticket_id_field_name: incidentNumber, 'DatasetID':dataset_id},{'approved_data':approved_data},, upsert=False)
                                        if((key != 'datasetid' and key !='customerid') and key != 'id'):
                                            approved_data[key] = value
                                            MongoDBPersistence.approved_tickets_tbl.update_one({'CustomerID':customer_id,ticket_id_field_name:incidentNumber, 'DatasetID':dataset_id}, {"$set": {'approved_data': approved_data}}, upsert=False)
                                except:
                                    logging.info("%s: Manage Engine of ticket with number %s is not possible check if ticket is present in manage engine or not "%(RestService.timestamp(), incidentNumber)) 
                        listInfo = json.dumps(listInfo)
                        logging.info('Auto Approve Json in Manage Engine insertion %s'%listInfo)      
                        response = requests.put(urlRequest,headers=header,proxies=proxies,params=getParams)
                        print(response)
                        #-------------------
                        # End of key, value looping
                        logging.info('%s: Auto Approve Predicted Details has been successfully updated into a collection TblPredictedData by user %s.'%(RestService.timestamp(), user))
                        logging.info('Auto Approve  Trying to update document of "rt_tickets_tbl" with "user_status" "Approved"')
                        #print(ticket_id_field_name + incidentNumber)
                        MongoDBPersistence.rt_tickets_tbl.update_one({'CustomerID':customer_id,ticket_id_field_name: incidentNumber, 'DatasetID':dataset_id}, {"$set": {'user_status':'Approved'}}, upsert=False)
                        logging.info('Auto Approve Trying to update "predicted_tickets_tbl" with approver details')
                        MongoDBPersistence.predicted_tickets_tbl.update_one({'CustomerID':customer_id,ticket_id_field_name:incidentNumber, 'DatasetID':dataset_id}, {"$set": {'user': user}}, upsert=False)
                        status = "success"
                        result=[{"Status": status}]       
                    else:
                        approved_user = MongoDBPersistence.predicted_tickets_tbl.find_one({"CustomerID":customer_id, "DatasetID":dataset_id}, {"_id":0, "user":1})
                        approved_user = approved_user['user']
                        logging.info("%s: Auto Approve The ticket with ticket number %s has already been approved by user %s "%(RestService.timestamp(),incidentNumber, approved_user))
                        approved_ticket = MongoDBPersistence.predicted_tickets_tbl.find_one({"CustomerID":customer_id, "DatasetID":dataset_id}, {"_id":0, ticket_id_field_name:1, 'user':1})
                        approved_tickets.append(approved_ticket)  # List of tickets which are already approved
                try:
                    #--Workload calculation--
                    ResourceMasterData.incident_workload_update(customer_id, dataset_id, incident_lst)
                    status = "success"
                    result=[{"Status": status}]
                except Exception as e:
                    logging.info("%s Error Occured in Auto Approve workload update %s "%(RestService.timestamp(), str(e)))
                #------------------------
            else:
                logging.info('%s: Auto Approve Getting empty JSON from Angular component, returning string empty...'%RestService.timestamp())
                status = "empty"
                result = [{"Status": status}]
        except Exception as e:
            print("Auto Approve error")
            logging.error('%s: Auto Approve Error occurred: %s '%(RestService.timestamp(),str(e)))
            status = "failure"
            result = [{"Status": status}, {"Error": str(e)}]
        return json_util.dumps(result)
