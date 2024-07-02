__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

from iia.persistence.mongodbpersistence import MongoDBPersistence
from iia.restservice import RestService
from iia.masterdata.datasets import DatasetMasterData
from iia.persistence.mappingpersistence import MappingPersistence
from iia.masterdata.customers import CustomerMasterData
from flask import request
from flask import make_response
from bson import json_util
import json
import pandas as pd
import re
import numpy as np
import io
import csv
import configparser
from iia.environ import *
from flask import session
import requests
from iia.utils.log_helper import get_logger, log_setup
logging = get_logger(__name__)
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

app = RestService.getApp()

@app.route('/api/insert/<int:customer_id>', methods=["POST"])
def db_insert_input_tickets(customer_id):
    return IncidentRT.db_insert_input_tickets(customer_id)
    
@app.route("/api/updateRT/<int:customer_id>/<incident_number>/<dataset_name>",methods=["PUT"])
def update_RT(customer_id, incident_number, dataset_name):
    return IncidentRT.update_RT(customer_id, incident_number, dataset_name)
      
@app.route("/api/tickets/<int:customer_id>/<int:dataset_id>",methods=["GET"])
def getTickets(customer_id, dataset_id):
    return IncidentRT.getTickets(customer_id, dataset_id)
    
@app.route("/api/tickets/<int:customer_id>/<int:dataset_id>/<ticket_id>",methods=["GET"])
def getRawData(customer_id,dataset_id,ticket_id):
    return IncidentRT.getRawData(customer_id, dataset_id, ticket_id)
    
@app.route('/api/exportPredToCSV/<int:customer_id>', methods=["GET"])
def exportPredToCSV(customer_id):
    return IncidentRT.exportPredToCSV(customer_id)

@app.route('/api/UploadLeapIncidentData', methods=["POST"])
def UploadLeapIncidentData():
    return IncidentRT.UploadLeapIncidentData()
    
class IncidentRT(object):
    '''
    classdocs
    '''

    def __init__(self, params):
        '''
        Constructor
        '''
        
    @staticmethod
    def db_insert_input_tickets( customer_id):
        try:
            file = request.files['files']
        except:
            raise Exception('File has not been recieved.')
    
        #Check if file is json or csv file
        if(not file):
            logging.error("%s: No file uploaded. please upload csv file."%RestService.timestamp())
            return 'failure'
        elif(not '.csv' in str(file)):
            logging.error("%s: Supports only csv file format. please upload csv file."%RestService.timestamp())
            return 'failure'
        custom_incidentrt_flag, custom_url = CustomerMasterData.check_custom("customIncidentRT")
        if (custom_incidentrt_flag=='failure'):
            logging.info("%s: Not able to read values from Configure File"%RestService.timestamp())
            return "failure"

        elif (custom_incidentrt_flag=="True"):
            logging.info("%s Custom incidentRT is present invoking Custom code"%RestService.timestamp())
            api = custom_url + "api/custom_insertRT/"+str(customer_id)  
            proxies = {"http": None,"https": None}
            req_head = { "Content-Type": "application/json"}
            stream = io.StringIO(file.stream.read().decode("latin-1"), newline=None)
            stream.seek(0)
            result = stream.read()
            #create list of dictionaries keyed by header row
            csv_dicts = [{k.lower(): v for k, v in row.items()} for row in csv.DictReader(result.splitlines(), \
                skipinitialspace=True)]
            csv_df = pd.DataFrame(csv_dicts)
            
            #getting session user
            if (session.get('user')):
                user = session['user']
                logging.info("%s Session catched user as  %s"%(RestService.timestamp(), user))
            else:
                logging.info("%s You are not logged in please login" %RestService.timestamp())
                return "No Login Found"
            new_postdata={}
            new_postdata['user']=user
            new_postdata['post_data']=csv_df.to_dict()
            req_res = requests.post(api,headers = req_head,json=json.dumps(new_postdata), proxies=proxies)
            response=req_res.text
            return response

        else:
            stream = io.StringIO(file.stream.read().decode("latin-1"), newline=None)
        
            stream.seek(0)
            result = stream.read()
        
            #create list of dictionaries keyed by header row
            csv_dicts = [{k.lower(): v for k, v in row.items()} for row in csv.DictReader(result.splitlines(), \
                skipinitialspace=True)]

            #Clease data before inserting into DB
            csv_df = pd.DataFrame(csv_dicts)

            # remove special chars between the name of column
            csv_df.columns = ["_".join(re.sub("[^A-Za-z0-9]+", " ", col).strip().split(" ")) for col in csv_df.columns]

            if(ticket_id_field_name not in csv_df.columns):
                logging.info(f"csv_df.columns: {csv_df.columns}")
                logging.info(f"ticket_id_field_name: {ticket_id_field_name}")
                logging.info('%s: Please rename ticket_id/Incident_id column to "number".'%RestService.timestamp())
                return 'failure'
            

            #Remove duplicate columns if there any (Based on Incident number)
            csv_df['auto_resolution'] = False
            csv_df.drop_duplicates(subset = ticket_id_field_name, keep = 'first', inplace = True)
            csv_df = csv_df.reset_index(drop=True)
            csv_df_cols = csv_df.columns
            
            csv_df = csv_df.loc[csv_df[ticket_id_field_name].notna()]
            csv_df = csv_df.loc[csv_df[ticket_id_field_name]!='']
            csv_df = csv_df.dropna(axis=0,how='all')
        
            json_str = csv_df.to_json(orient='records')
            json_data = json.loads(json_str)
            
            if(len(set(csv_df_cols))<len(csv_df_cols)):
                logging.info('%s: Duplicate columns, please rename/correct the duplicate column names..'%RestService.timestamp())
                return 'failure'
            
            # Analysing the input tickets: Finding out which dataset it belongs to
            logging.info('%s: Analysing the input tickets: Finding out which dataset it belongs to.'%RestService.timestamp())
            garbage_tickets = DatasetMasterData.guessDataset(json_data, customer_id)#garbage_tickets are the tickets whose unique fields pattern does not match with datasets
            logging.info(f"garbage_tickets:{garbage_tickets}")
            if(len(garbage_tickets)==0):
                resp = 'success'
            else:
                resp = 'warn'
            return resp
        
    @staticmethod
    def update_RT( customer_id, incident_number, dataset_name):
        dataset_id = MongoDBPersistence.datasets_tbl.find_one({"CustomerID": customer_id, "DatasetName": dataset_name},{"DatasetID":1,"_id":0})
        if(dataset_id):
            try:
                dataset_id = dataset_id['DatasetID']
            except Exception as e:
                logging.error('%s: Error occurred: %s '%(RestService.timestamp(),str(e)))
                resp = 'failure'
                return resp
        else:
            logging.info('%s: Failure: We are sorry, there is no dataset ID with name %s registerd with us.'%(RestService.timestamp(),dataset_name))
            resp = 'failure'
            return resp
        try:
            MongoDBPersistence.rt_tickets_tbl.update_one({'CustomerID':customer_id ,ticket_id_field_name : incident_number}, {"$set": {"DatasetID":dataset_id}}, upsert=False)
            resp = 'success'
        except Exception as e:
            resp = 'failure'
        return resp
    
    @staticmethod
    def getTickets( customer_id,dataset_id):
        rt_tkts = MongoDBPersistence.rt_tickets_tbl.find({'CustomerID': customer_id, "DatasetID":dataset_id})
        if(rt_tkts):
            logging.info('%s: Getting real time tickets.'%RestService.timestamp())
            resp = json_util.dumps(rt_tkts)
        else:
            logging.info('%s: Failed to get real time tickets.'%RestService.timestamp())
            resp = 'failure'
        return resp
    
    @staticmethod
    def getRawData( customer_id,dataset_id,ticket_id):
        result = MongoDBPersistence.rt_tickets_tbl.find({'CustomerID': customer_id, "DatasetID":dataset_id,ticket_id_field_name: ticket_id})
        if(result):
            logging.info('%s: Getting real time ticket.'%RestService.timestamp())
            resp = json_util.dumps(result)
        else:
            logging.info('%s: Failed to get requested real time ticket.'%RestService.timestamp())
            resp = 'failure'
        return resp
    
    @staticmethod
    def exportPredToCSV( customer_id):
        match_doc = {"CustomerID" : 1}
        try:
            # --fetching tikets specific for team--
            if (session.get('user')):
                logging.info("%s Catching User Session"%RestService.timestamp())
                user = session['user']
                role = session['role']
                logging.info("%s Session catched user as  %s"%(RestService.timestamp(), user))
                if(role == 'Admin'):
                    match_doc = {'CustomerID': customer_id}
                else:
                    user_doc = MongoDBPersistence.users_tbl.find_one({'UserID':user})
                    if(user_doc):
                        team_id =  int(user_doc['TeamID'])
                        team_doc = MongoDBPersistence.teams_tbl.find_one({'TeamID':team_id})
                        if(team_doc):
                            dataset_id = team_doc['DatasetID']
                            match_doc = {'CustomerID': customer_id, "DatasetID":dataset_id}
                        else:
                            logging.warn('There is no document in Tbl_Teams with team id %s'%str(team_id))
                    else:
                        logging.warn('There is no document in Tbl_Users with user_id %s'%user)
            else:
                logging.info("%s You are not logged in please login" %RestService.timestamp())
                return "No Login Found"
            rt_tkts_lst = list(MongoDBPersistence.rt_tickets_tbl.find(match_doc,{'_id':0,"CustomerID" : 0,"user_status":0,"DatasetID":0}))
            pred_tkts_lst = list(MongoDBPersistence.predicted_tickets_tbl.find(match_doc,{'_id':0,"CustomerID":0,"DatasetID":0}))
        except Exception as e:
            logging.error("Error:%s"%str(e))
        if(not pred_tkts_lst and not rt_tkts_lst):
            logging.info("No records in predict table OR no records in realtime incident table.")
            return 'failure'
        else:
            try:
                config = configparser.ConfigParser()
                config["DEFAULT"]['path'] = "config/"
                config.read(config["DEFAULT"]["path"]+"iia.ini")
                assignment_ini = config["ModuleConfig"]["assignmentModule"]
            except Exception as e:
                logging.error("Error occured: Hint: 'assignmentModule' is not defined in 'config/iia.ini' file.")
                assignment_ini = "No"
                logging.info("Taking default as 'assignmentModule = No'..")
            result = []
            for ticket in pred_tkts_lst:
                new_ticket = {}
                if(assignment_ini.lower()=="yes"):
                    new_ticket['Predicted_assigned_to'] = ticket['predicted_assigned_to']
                new_ticket[ticket_id_field_name] = ticket[ticket_id_field_name]
                for field in ticket['predicted_fields']:
                    pred_field_name = ''
                    for key, value in field.items():
                        if(not key=="ConfidenceScore"):
                            new_ticket["Predicted_"+key] = value
                            pred_field_name=key
                        else:
                            new_ticket["Confidence Score for "+ pred_field_name] = value
                result.append(new_ticket)
        combined_df = pd.merge(pd.DataFrame([dict(t) for t in set(tuple(sorted(d.items())) for d in result)]), pd.DataFrame([dict(t) for t in set(tuple(sorted(d.items())) for d in rt_tkts_lst)]), on=[ticket_id_field_name])
        json_str = combined_df.to_json(orient='records')
        combined_df_list = json.loads(json_str)
        csv_data_format = []
        csv_data_format.append(combined_df_list[0].keys())
        for flattened_record in combined_df_list:
            csv_data_format.append(list(flattened_record.values()))
        si = StringIO()
        cw = csv.writer(si)
        cw.writerows(csv_data_format)
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=export.csv"
        output.headers["Content-type"] = "text/csv"
        logging.info('%s: Predicted tickets have been exported successfully into a csv.'%RestService.timestamp())
        return output


    @staticmethod
    def UploadLeapIncidentData():
        try:
            input_data = request.get_json()
            print("input_data:",input_data)
            print("profile data..",input_data['incidents'])
            incidents = input_data['incidents']
            MongoDBPersistence.rt_tickets_tbl.insert_many(incidents)
            response = "success"
            logging.info("inserted successfully")
        except Exception as e:
            print("Exception inside UploadLeapIncidentData data",e)
            response = "failure"            
            logging.error("failed to upload")
        return json_util.dumps({'response': response})