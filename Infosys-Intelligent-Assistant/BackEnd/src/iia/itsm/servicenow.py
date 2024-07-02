__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

#--Imports for service now--
import pysnow
from servicenow import ServiceNow
from servicenow import Connection
from iia.persistence.mongodbpersistence import MongoDBPersistence
from iia.restservice import RestService
from iia.masterdata.datasets import DatasetMasterData
from iia.persistence.mappingpersistence import MappingPersistence
from iia.masterdata.resources import ResourceMasterData
from flask import request
from bson import json_util
from datetime import datetime, timedelta
import os
from matplotlib import pyplot as plt
import configparser
from flask import session
import importlib
import collections
import itertools
import json
import seaborn as sns
from bson import json_util
import pandas as pd
import datetime
from iia.environ import *
from iia.utils.log_helper import get_logger, log_setup
from iia.utils.config_helper import get_config

logging = get_logger(__name__)


app = RestService.getApp()

from urllib import request
logging.info(request.getproxies())
     
@app.route('/api/getDashboardOpenTicketsCount', methods=['GET'])
def get_prev_week_openIncidents():
    return ServiceNow.get_prev_week_openIncidents()

@app.route('/api/getDashboardClosedTicketsCount', methods=['GET'])
def get_prev_week_closedIncidents():
    return ServiceNow.get_prev_week_closedIncidents()
@app.route('/api/approvedTicketsCount', methods=['GET'])
def get_approved_tickets():
    return ServiceNow.get_approved_tickets()

@app.route('/api/getautoapprovedtickets', methods=['GET'])
def get_Auto_approved_tickets():
    return ServiceNow.get_Auto_approved_tickets()

@app.route('/api/getmanuallyapprovedtickets', methods=['GET'])
def get_manually_approved_tickets():
    return ServiceNow.get_manually_approved_tickets()

@app.route('/api/getDashboardTicketsfetched', methods=['GET'])
def get_total_tickets():
    return ServiceNow.get_total_tickets()


@app.route('/api/getDashboardTicketsfetchedReort', methods=['GET'])
def generateTicketsFetchedReport():
    return ServiceNow.generateTicketsFetchedReport()


@app.route('/api/generateTotalTicketsFetchedReport/<string:datefrom>/<string:dateto>/<string:category>', methods=['GET'])
def generateTotalTicketsFetchedReport(datefrom, dateto,category):
    return ServiceNow.generateTotalTicketsFetchedReport(datefrom, dateto,category)

@app.route('/api/gettotaltickets/<int:customer_id>/<int:dataset_id>', methods=['GET'])
def genenerateTotaltickets(customer_id,dataset_id):
    return ServiceNow.genenerateTotaltickets(customer_id,dataset_id)


@app.route('/api/generateuserdetails/<int:customer_id>/<int:dataset_id>', methods=['GET'])
def generateAutoapprovalByUser(customer_id,dataset_id):
    return ServiceNow.generateAutoapprovalByUser(customer_id,dataset_id)

@app.route('/api/openTickets', methods=['GET'])
def opentickets():
    return ServiceNow.opentickets()

@app.route('/api/closed_Tickets', methods=['GET'])
def closedtickets():
    return ServiceNow.closedtickets()

@app.route('/api/predicted_Tickets', methods=['GET'])
def predictedtickets():
    return ServiceNow.predictedtickets()
 
@app.route('/api/users', methods=['GET'])
def users():
    return ServiceNow.users()

@app.route('/api/generateOpenTicketsByAssignee/<int:customer_id>/<int:dataset_id>/<string:dropdown>', methods=['GET'])
def generateOpenTicketsByAssignee(customer_id,dataset_id,dropdown):
    return ServiceNow.generateOpenTicketsByAssignee(customer_id,dataset_id,dropdown)

@app.route('/api/generatestackedgraph/<int:customer_id>/<string:assignee>', methods=['GET'])
def GenerateAssigneeByAssignmentgroup(customer_id,assignee):
    return ServiceNow.GenerateAssigneeByAssignmentgroup(customer_id,assignee)

  
@app.route('/api/generateassignee/<int:customer_id>', methods=['GET'])
def GenerateAssignee(customer_id):
    return ServiceNow.GenerateAssignee(customer_id)

@app.route('/api/generateassignmentgraph/<int:customer_id>', methods=['GET'])
def generateassignmentgraph(customer_id):
    return ServiceNow.generateassignmentgraph(customer_id)


class ServiceNow(object):
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

            if(ServiceNow.c is None):   
                # Connect to Service Now using default api method (JSON)
                instance = MongoDBPersistence.customer_tbl.find_one({"CustomerID":1}, {'SNOWInstance':1, '_id':0})
                username = MongoDBPersistence.customer_tbl.find_one({"CustomerID":1}, {'SNOWUserName':1, '_id':0})
                password = MongoDBPersistence.customer_tbl.find_one({"CustomerID":1}, {'SNOWPassword':1, '_id':0})
                logging.info(f"username: {username}, password: {password}, instance :{instance}")
                config_service_now = get_config('service_now')
                logging.info(request.getproxies())
                ServiceNow.c = pysnow.Client(instance=instance['SNOWInstance'], user=username['SNOWUserName'], password=password['SNOWPassword'])
                #To display actual values of fields instead of external reference link or GUID - Service Now
                ServiceNow.c.parameters.display_value = True
                ServiceNow.c.parameters.exclude_reference_link = True
                ServiceNow.servicenow_incidents = ServiceNow.c.resource(api_path='/table/incident')
            return ServiceNow.servicenow_incidents
        except Exception as e:
             raise
    
    @staticmethod
    def get_prev_week_openIncidents():

        customer_details = MongoDBPersistence.customer_tbl.find_one({}, {"_id":0})
        customer_id = customer_details['CustomerID']

        customer_name = MongoDBPersistence.customer_tbl.find_one({'CustomerID':customer_id},\
                                                                    {'CustomerName':1, '_id':0})['CustomerName']   
        itsm_tool_name = MongoDBPersistence.itsm_details_tbl.find_one({},{"_id":0,"ITSMToolName":1})["ITSMToolName"]
        class_name = customer_name + "_"+ itsm_tool_name +"_"+ "Configurations"
        module_name = "iia.customITSM." + class_name
        logging.info("class name formed here is  %s and module is %s in get_prev_week_openIncidents"%(class_name,module_name))
        try:
            module = importlib.import_module(module_name)
            class_ = getattr(module, class_name)
            response = class_.get_prev_week_openIncidents()
            logging.info("Custom ITSM file called for get_prev_week_openIncidents and returning the response to UI %s"%(response))
            return response
        except Exception as e:
            logging.error('%s: Error occurred: %s ' % (RestService.timestamp(), str(e)))
            logging.info("Error can be ignored, there is no customized ItSM module uploaded. \
                Going for basic ITSM configurations ")

        logging.info("Going for Default workflow in get_prev_week_openIncidents")
		
        today = datetime.today()
        one_week_ago = today - timedelta(days=100)
        incident_no_lst=[]
        application_groups=[]
        if(itsm_tool_name=="SNOW"):

            try:
                servicenow_incidents = ServiceNow.getClient()
                
                queryBuilder = (pysnow.QueryBuilder().field(status_field_name).equals("1").AND()
                .field(sys_created_on_field_name).between(one_week_ago, today))
                
                response = servicenow_incidents.get(query=queryBuilder)
                if(response):
                    for responce_doc in response.all():
                        incident_no_lst.append(responce_doc[ticket_id_field_name])
                
                print("In get open tickets for one week...",len(incident_no_lst))
                
                return (json_util.dumps(len(incident_no_lst)))
            except Exception as e:
                return 'exception'
        else:
            logging.error("No Configurations present for this %s "%(itsm_tool_name))
            return 'exception'

    
    @staticmethod
    def get_prev_week_closedIncidents():

        customer_details = MongoDBPersistence.customer_tbl.find_one({}, {"_id":0})
        customer_id = customer_details['CustomerID']
        customer_name = MongoDBPersistence.customer_tbl.find_one({'CustomerID':customer_id},\
                                                                    {'CustomerName':1, '_id':0})['CustomerName']   
        itsm_tool_name = MongoDBPersistence.itsm_details_tbl.find_one({},{"_id":0,"ITSMToolName":1})["ITSMToolName"]
        class_name = customer_name + "_"+ itsm_tool_name +"_"+ "Configurations"
        module_name = "iia.customITSM." + class_name
        logging.info("class name formed here is  %s and module is %s in get_prev_week_closedIncidents"%(class_name,module_name))
        try:
            module = importlib.import_module(module_name)
            class_ = getattr(module, class_name)
            response = class_.get_prev_week_closedIncidents()
            logging.info("Custom ITSM file called for get_prev_week_closedIncidents and returning the response to UI %s"%(response))
            return response
        except Exception as e:
            logging.error('%s: Error occurred: %s ' % (RestService.timestamp(), str(e)))
            logging.info("Error can be ignored, there is no customized ItSM module uploaded. \
                Going for basic ITSM configurations ")

        logging.info("Going for Default workflow in get_prev_week_closedIncidents")

        today = datetime.today()
        one_week_ago = today - timedelta(days=100)
        incident_no_lst=[]
        application_groups=[]
        
        if(itsm_tool_name=="SNOW"):
            try:
                servicenow_incidents = ServiceNow.getClient()
                
                queryBuilder = (pysnow.QueryBuilder().field(status_field_name).equals("7").AND()
                .field(closed_at_field_name).between(one_week_ago, today))
                
                response = servicenow_incidents.get(query=queryBuilder)
                if(response):
                    for responce_doc in response.all():
                        incident_no_lst.append(responce_doc[ticket_id_field_name])
                
                print("In get closed tickets for one week...",len(incident_no_lst))
                return (json_util.dumps(len(incident_no_lst)))
            except Exception as e:
                logging.error("error in get_prev_week_closedIncidents",str(e))
                return 'exception'
            
        else:
            logging.error("No Configurations present for this %s "%(itsm_tool_name))
            return 'exception'
            
    @staticmethod
    def get_total_tickets():
        ticket_details = MongoDBPersistence.rt_tickets_tbl.find({}).count()
        print(type(ticket_details))
        return json_util.dumps(ticket_details)

    @staticmethod
    def get_approved_tickets():
        closed_tickets = MongoDBPersistence.approved_tickets_tbl.find({}).count()
        print(closed_tickets)
        return json_util.dumps(closed_tickets)

    @staticmethod
    def get_manually_approved_tickets():
        print("hello...inside manually approved tickets")
        category_list=MongoDBPersistence.approved_tickets_tbl.find({'auto_approve':False}).count()
        print(category_list)
        print("inside manually approved")
        return json_util.dumps(category_list)

    @staticmethod
    def get_Auto_approved_tickets():
        category_list1=MongoDBPersistence.approved_tickets_tbl.find({'auto_approve':True}).count()
        print(category_list1)
        print("inside Auto Approved")
        return json_util.dumps(category_list1)
    @staticmethod
    def generateAutoapprovalGraph(customer_id, dataset_id):
        print("inside function...")
        category_list1 = list(MongoDBPersistence.approved_tickets_tbl.find({'CustomerID': 1, "DatasetID": 1}))
        pd_dataframe = pd.DataFrame(category_list1)
        auto = pd_dataframe['auto_approve'].value_counts()
        print(auto)

        try:
            vocab_path = os.path.join('static/assets/video/Dashboard_'+'auto_approval'+'.png')

            list1 = auto.index.to_list() 
            list2 = auto.values
            print(auto.values)
            p=sns.barplot(list1,list2)
            p.set(xlabel="AutoApproval",ylabel="Count")
            plt.savefig(vocab_path)
            plt.figure()
            plt.show()
                
            print("done....")
            logging.info('done....')

            return "Success"

        except Exception as ex:
            logging.info(str(ex))
            print('Exception...', ex)

    @staticmethod
    def generateAutoapprovalByUser(customer_id, dataset_id):
        print("inside function...")
        category_list = list(MongoDBPersistence.approved_tickets_tbl.find({'CustomerID': 1, "DatasetID": 1}))
        pd_data = pd.DataFrame(category_list)
        try:
            vocab_path = os.path.join('static/assets/video/user_'+'ApprovedTickets'+'.png')

            ddf = pd.DataFrame(columns=['Assigned_to'])
            for (i,r) in pd_data.iterrows():
                e = r['approved_data']
                ddf.loc[i] = [e['assigned_to']]
            pd_data= pd.concat([pd_data, ddf], axis=1)
            
            z = pd_data.groupby(['Assigned_to']).size()
            print(z)
            list1 = z.index.to_list() 
            list2 = z.values
            list2 = list2.tolist()
            print(z.values)
            result={'keys': list1, 'values': list2}
                
            print("done....")
            return json_util.dumps(result)

        except Exception as ex:
            logging.info(str(ex))
            print('Exception..',ex)


    @staticmethod
    def genenerateTotaltickets(customer_id, dataset_id):

        print("inside function...")
        sns.set(style = 'whitegrid')
        category_list = list(MongoDBPersistence.rt_tickets_tbl.find(
        {'CustomerID': 1, "DatasetID": 1}))
        pd_data = pd.DataFrame(category_list)
        pd_data
        z = pd_data['assignment_group'].value_counts()
        try:
            vocab_path = os.path.join('static/assets/video/Dashboard_'+'TicketsFetched'+'.png')
            list1 = z.index.to_list() 
            list2 = z.values
            a = list2.tolist()
            print(type(z.values))
            result = collections.defaultdict(list)                
            logging.info('done....')

            print(list1, list2,a)
            result={'keys': list1, 'values': a}
            return json_util.dumps(result)
        except Exception as ex:
            logging.info(str(ex))
            print('Exception...', ex)


    @staticmethod
    def generateTicketsFetchedReport():
        print("inside generateticketfetchedreport...")
        Liste = MongoDBPersistence.approved_tickets_tbl.find(
        {}).count()
        print(Liste)
        Predictcount = MongoDBPersistence.predicted_tickets_tbl.find(
        {}).count()
        print(Predictcount)
        category_list = MongoDBPersistence.approved_tickets_tbl.find(
        {'auto_approve': False}).count()
        print(type(category_list))
        category_list1 = MongoDBPersistence.approved_tickets_tbl.find(
        {'auto_approve': True}).count()
        print(category_list1)
        try:
            vocab_path = os.path.join('static/assets/video/')
            d = {}
            d['ApprovedTickets'] = Liste
            d['AutoApprovedTickets'] = category_list1
            d['ManuallyApprovedTickets'] = category_list
            d['PredictedTickets'] = Predictcount
            completeName = os.path.join(vocab_path, '_DashboardReport' +'.xlsx')     
            df = pd.DataFrame(d, index =['1'])
            df.to_excel(completeName,encoding='utf-8')
            print("done....")
            logging.info('done....')
            return "Success"
        except Exception as ex:
            logging.info(str(ex))
            print('Exception...', ex)

    @staticmethod
    def generateTotalTicketsFetchedReport(datefrom, dateto,category):
        print("inside Ticket Fetched function...")
        datefrom = datefrom +'00:00:00'
        dateto = dateto +'00:00:00'
        ReqDate = datefrom[:10] +' '+'to'+' '+ dateto[:10]
        sns.set(style = 'whitegrid')
        category_list = list(MongoDBPersistence.rt_tickets_tbl.find(
        {'CustomerID': 1, "DatasetID": 1,'opened_at':{'$gte':datefrom,'$lt':dateto}}))
        pd_data = pd.DataFrame(category_list)
        try:
            z = pd_data[category].value_counts()
            z = z.to_frame()
            c =z.reset_index()
            print(c.columns , 'Columns')
            c.rename(columns = {'index':category,c.columns[1]: 'count'}, inplace = True)
            c['Duration']=ReqDate
            print(c)
            vocab_path = os.path.join('static/assets/video/TicketsFetched.xlsx')
            c.to_excel(vocab_path,encoding='utf-8')

            print("done....")
            logging.info('done....')
            return "Success"
        except Exception as ex:
            logging.info(str(ex))
            print('Exception...', ex)


    @staticmethod
    def closedtickets():
        print("insideclosedtickets")
        a1 = MongoDBPersistence.rt_tickets_tbl.find({"state":"CLOSED" }).count()
        print(a1)
        return json_util.dumps(a1)

    @staticmethod
    def opentickets():
        print("insideopentickets")
        b1= MongoDBPersistence.rt_tickets_tbl.find({"state":"In Progress" }).count()
        print(type(b1))
        b2= MongoDBPersistence.rt_tickets_tbl.find({"state":"New" }).count()
        
        print(int(b1)+int(b2))
        B=b1+b2
        return json_util.dumps(B)

    @staticmethod
    def predictedtickets():
        print("insidepredictedtickets")
        c1=MongoDBPersistence.predicted_tickets_tbl.find({}).count()
        print(c1)
        return json_util.dumps(c1)

    @staticmethod
    def users():

        list1=[]
        closed_lst=list(MongoDBPersistence.predicted_tickets_tbl.find({"CustomerID" : 1},{"predicted_assigned_to" :1, "assignment_group" : 1 }))
        pd_data = pd.DataFrame(closed_lst)
        c = pd_data["predicted_assigned_to"].unique().tolist()
        
        print(c)
        return json.dumps(c)   

    @staticmethod
    def generateOpenTicketsByAssignee(customer_id, dataset_id, dropdown):
        try:
            if dropdown == 'Select_All':
                closed_lst=list(MongoDBPersistence.predicted_tickets_tbl.find({"state": { "$in": [ "New", "In Progress" ] }}))

                pd_data = pd.DataFrame(closed_lst)
                z = pd_data['predicted_assigned_to'].value_counts()
                print('--',z)
                list1 = z.index.to_list()
                list2 = z.values
                a = list2.tolist()

            else:
                closed_lst=list(MongoDBPersistence.predicted_tickets_tbl.find({"predicted_assigned_to":dropdown,"state": { "$in": [ "New", "In Progress" ] }},{"number":1,"predicted_assigned_to":1}))
                pd_data = pd.DataFrame(closed_lst)
                z = pd_data['predicted_assigned_to'].value_counts()
                list1 = z.index.to_list()
                if dropdown not in list1:
                    raise Exception('Assiggnee dont have any tickets')
                list2 = z.values
                a = list2.tolist()
            result={'response': 'success', 'keys': list1, 'values': a}
        except Exception as ex:
            print('Exception...', ex)
            print("the assignee dont have any tickets")
            result={'response': 'failure'}
        return json.dumps(result)

    @staticmethod
    def GenerateAssigneeByAssignmentgroup(customerid,assignee):
        closed_lst=list(MongoDBPersistence.predicted_tickets_tbl.find({"CustomerID" : 1},{"predicted_assigned_to" :1, "assignment_group" : 1 }))
        pd_data = pd.DataFrame(closed_lst)
        z = pd_data.groupby(['predicted_assigned_to', 'assignment_group']).size().reset_index()

        d = [tuple(x) for x in z.to_records(index=False)]
        list4 = []
        list5 = []
        for i in d :
            a = list(i)
            if assignee in a[0] :
                list4.append(a[1])
                list5.append(int(a[2]))
        result={'keys': list4, 'values': list5}
        print(result)
        return json_util.dumps(result)

    @staticmethod
    def GenerateAssignee(customerid):
        closed_lst=list(MongoDBPersistence.predicted_tickets_tbl.find({"CustomerID" : 1},{"predicted_assigned_to" :1, "assignment_group" : 1 }))
        pd_data = pd.DataFrame(closed_lst)
        z = pd_data.groupby(['predicted_assigned_to', 'assignment_group']).size().reset_index()
        d = [tuple(x) for x in z.to_records(index=False)]
        l = []
        for i in d :
            x =list(i)
            l.append(x)
        for j in l:
            j[2] = int(j[2])
        print(l)
        return json_util.dumps(l)

    @staticmethod
    def generateassignmentgraph(customer_id):
        closed_lst11=list(MongoDBPersistence.predicted_tickets_tbl.find({"CustomerID" : 1},{"assignment_group" : 1 }))
        pd_data = pd.DataFrame(closed_lst11)
        z = pd_data['assignment_group'].value_counts()
        assignment_list= z.index.to_list()
        list22 = z.values
        count_list = list22.tolist()

        result11={'response': 'success', 'keys': assignment_list, 'values': count_list}
        print(result11)
        return json_util.dumps(result11)