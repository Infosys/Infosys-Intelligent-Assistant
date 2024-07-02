__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

from iia.persistence.mongodbpersistence import MongoDBPersistence
from iia.restservice import RestService
from datetime import datetime,date
from flask import request
from bson import json_util
import json
import pandas as pd
import io
import csv
from iia.utils.log_helper import get_logger, log_setup
logging = get_logger(__name__)
app = RestService.getApp();
@app.route('/api/uploadApplicationDetails/<int:customer_id>/<team_name>', methods=["POST"])
def db_insert_application_details( customer_id,team_name):
    return ApplicationMasterData.db_insert_application_details(customer_id, team_name)
    
@app.route("/api/segmentID/<assignment_group>",methods=["GET"])
def getSegmentId( assignment_group):
    return ApplicationMasterData.getSegmentId(assignment_group)
    
@app.route('/api/getApplicationDetails/<int:customer_id>/<team_name>',methods=['GET'])
def get_application_details( customer_id,team_name):
    return ApplicationMasterData.get_application_details(customer_id, team_name)

@app.route('/api/getApplicationsForTeam/<int:customer_id>/<team_name>',methods=['GET'])
def get_applications_forteam( customer_id,team_name):
    return ApplicationMasterData.get_applications_forteam(customer_id, team_name)

@app.route('/api/deleteApplication/<int:customer_id>/<team_name>/<record_id>',methods=['DELETE'])
def delete_application(customer_id,team_name,record_id):
    return ApplicationMasterData.delete_application(customer_id,team_name,record_id)

@app.route('/api/deleteAllApplications/<int:customer_id>/<team_name>',methods=['DELETE'])
def delete_all_applications(customer_id,team_name):
    return ApplicationMasterData.delete_all_applications(customer_id,team_name)

@app.route('/api/getApplicationTeamNames',methods=['GET'])
def get_application_team_names():
    return ApplicationMasterData.get_application_team_names()

@app.route('/api/updateApplication/<int:customer_id>/<int:dataset_id>/<record_id>', methods=['PUT'])
def update_application_details(customer_id,dataset_id,record_id):
    return ApplicationMasterData.update_application_details(customer_id,dataset_id,record_id)

@app.route('/api/getTicketWeightageTeamNames',methods=['GET'])
def get_ticketweightage_team_names():
    return ApplicationMasterData.get_ticketweightage_team_names()
    
class ApplicationMasterData(object):
    '''
    classdocs
    '''
    
    def __init__(self, params):
        '''
        Constructor
        '''
       
    @staticmethod
    def getAppWeightage(assignment_group):

        logging.info('%s: In "getAppWeightage" method, trying to fetch details from "TblApplication" for assignment grp: %s'%(RestService.timestamp(),assignment_group))
        app_doc=MongoDBPersistence.db.TblApplication.find_one({'assignment_group': assignment_group},{'_id':0,'app_weightage':1})
        logging.info(f"app_doc: {app_doc}")
        if(app_doc):
            app_weightage = app_doc['app_weightage']
        else:
            app_weightage = 0
            logging.error('No document for assignment grp: %s, returning 0 as "app_weightage"'%assignment_group)
        logging.info(f"assignment_group: {assignment_group}")
        logging.info(f"app_weightage: {app_weightage}")
        return app_weightage
    
    @staticmethod
    def db_insert_application_details( customer_id,team_name):

        logging.info('%s: In "db_insert_application_details" customer_id: %s, team_name: %s'%(RestService.timestamp(), customer_id, team_name))
        new_dataset_flag = 0
        file = request.files['applicationDetails']
        logging.info('trying to fetch team document')
        dataset_ = MongoDBPersistence.teams_tbl.find_one({"CustomerID": customer_id,"TeamName":team_name},{"DatasetID":1,"_id":0})
        
        if(dataset_):
            logging.info('%s: Getting old dataset details.'%RestService.timestamp())
            dataset_id = dataset_["DatasetID"]
        else:
            last_dataset_id = 0
            dataset_name = team_name
            logging.info('%s: Adding new dataset.' % RestService.timestamp())
            # getting max dataset id for the customer, so that new dataset id = old + 1
            dataset_dict = MongoDBPersistence.datasets_tbl.find_one(
                {"CustomerID": customer_id, "DatasetID": {"$exists": True}},
                {'_id': 0, "DatasetID": 1, "DatasetName": 1}, sort=[("DatasetID", -1)])

            if dataset_dict:
                last_dataset_id = dataset_dict.get('DatasetID')
                dataset_name = dataset_dict.get('DatasetName')
            else:

                logging.info('%s: Adding dataset for very first team.' % RestService.timestamp())

            dataset_id = last_dataset_id + 1
            
            new_dataset_dict = {}
            new_dataset_dict["DatasetID"] = dataset_id
            new_dataset_dict["DatasetName"] = dataset_name
            new_dataset_dict["CustomerID"] =  customer_id
            new_dataset_flag = 1
    
        if not file:
            logging.error('file not found')
            return "No file"
        elif '.csv' not in str(file):
            logging.error('file format is incorrect')
            return "Upload csv file."

        stream = io.StringIO(file.stream.read().decode("latin-1"), newline=None)
        stream.seek(0)
        result = stream.read()
    
        #create list of dictionaries keyed by header row   k.lower()
        csv_dicts = [{k.lower(): v for k, v in row.items()} for row in csv.DictReader(result.splitlines(), \
            skipinitialspace=True)]
        for item in csv_dicts:
            item.update( {"CustomerID":customer_id})
            item.update( {"DatasetID":dataset_id})
            item.update( {"TrainingFlag":0})
            
        #Clease data before inserting into DB
        csv_df = pd.DataFrame(csv_dicts)
        # remove spaces between the name of column
        csv_df.columns = ['_'.join(col.split(' ')) for col in csv_df.columns]
        #Remove duplicate columns if there any (Based on Incident number)
        csv_df_cols = csv_df.columns
        
        if(len(set(csv_df_cols))<len(csv_df_cols)):
            logging.info('%s: Duplicate columns, please rename the duplicate column names..'%RestService.timestamp())
            return 'failure'
        
        json_str = csv_df.to_json(orient='records')
        json_data = json.loads(json_str)
        try:
            logging.info('%s: Trying to insert records into TblResource...'%RestService.timestamp())
            for app_doc in json_data:    
                MongoDBPersistence.applicationDetails_tbl.update_one({'assignment_group':app_doc['assignment_group']},{'$set':app_doc}, upsert=True)
            logging.info('%s: Completed with inserting applciation documents...'%RestService.timestamp())
            
            if(new_dataset_flag):
                logging.info('%s: Trying to insert new dataset into TblDataset...'%RestService.timestamp())
                MongoDBPersistence.datasets_tbl.insert_one(new_dataset_dict)
                logging.info('%s: Trying to update TblTeams with Dataset details...'%RestService.timestamp())
                MongoDBPersistence.teams_tbl.update_one({'CustomerID':customer_id, "TeamName":team_name}, {"$set": {"DatasetID":dataset_id}}, upsert=False)
                
            logging.info('%s: Records inserted successfully.'%RestService.timestamp())
            resp = "success"
            
        except Exception as e:
            logging.error('%s: Error occurred: %s '%(RestService.timestamp(),str(e)))
            logging.error('%s: Possible error: Data format in csv not matching with database constarints.(unique key & not null)'%RestService.timestamp())
            resp = 'failure'
        return resp
    
    @staticmethod
    def getSegmentId( assignment_group):

        logging.info('%s :In "getSegmentId" method, assignment grp: %s'%(RestService.timestamp(), assignment_group))
        segment = MongoDBPersistence.applicationDetails_tbl.find_one({"Application_group": assignment_group},{"seg_id":1,"_id":0})
        if(segment):
            try:
                resp = segment['seg_id']
            except Exception as e:
                logging.error('%s: Error occurred: %s '%(RestService.timestamp(),str(e)))
        else:
            logging.info('%s: Segment not found for an assignment group %s.'%(RestService.timestamp(),assignment_group))
            resp = 'failure'
        
        return json_util.dumps(resp)
    
    @staticmethod
    def get_application_details( customer_id,team_name):
        try:

            logging.info('%s: Trying to get documents from "teams_tbl" for team: %s'%(RestService.timestamp(),team_name))
            team_doc=MongoDBPersistence.teams_tbl.find_one({'TeamName':team_name,'DatasetID':{'$exists':True}},{'_id':0,'DatasetID':1}) 
            if(team_doc != None):
                dataset_id=team_doc['DatasetID']
                app_lst=list(MongoDBPersistence.db.TblApplication.find({'DatasetID':dataset_id,'CustomerID':customer_id},{"_id":0}))
            else:
                app_lst=[]
                logging.error('Could not get document from "teams_tbl"')
                
        except Exception as e:
            logging.error('Error: ',e)
            
        return json_util.dumps(app_lst,indent=1)

    @staticmethod
    def get_applications_forteam( customer_id,team_name):
        try:

            logging.info('%s: Trying to get documents from "teams_tbl" for team: %s'%(RestService.timestamp(),team_name))
            team_doc=MongoDBPersistence.teams_tbl.find_one({'TeamName':team_name,'DatasetID':{'$exists':True}},{'_id':0,'DatasetID':1}) 
            if(team_doc != None):
                dataset_id=team_doc['DatasetID']
                app_lst=list(MongoDBPersistence.db.TblApplication.find({'DatasetID':dataset_id,'CustomerID':customer_id},{"_id":0,"assignment_group":1}))
                app_lst = [app['assignment_group'] for app in app_lst]
            else:
                app_lst=[]
                logging.error('Could not get document from "teams_tbl"')
                
        except Exception as e:
            logging.error('Error: ',e)
            
        return json_util.dumps(app_lst)
    
    @staticmethod
    def delete_application(customer_id,team_name,record_id):
        try:

            logging.info('%s: Trying to get documents from "teams_tbl" for team: %s'%(RestService.timestamp(),team_name))
            team_doc=MongoDBPersistence.teams_tbl.find_one({'TeamName':team_name,'DatasetID':{'$exists':True}},{'_id':0,'DatasetID':1})
            if(team_doc!=None):
                dataset_id=team_doc['DatasetID']
                logging.info('%s: Trying to delete document from "applicationDetails_tbl"'%RestService.timestamp())
                MongoDBPersistence.applicationDetails_tbl.delete_one({'CustomerID':customer_id,'DatasetID':dataset_id,'record_id':record_id})
            else:
                logging.error('Could not get document from "teams_tbl"')
        except Exception as e:
            logging.error('%s :Error: %s'%(RestService.timestamp(), str(e)))
            return('failure')
    
        return('success')
    
    @staticmethod
    def delete_all_applications(customer_id,team_name):
        try:

            logging.info('%s: Trying to get documents from "teams_tbl" for team: %s'%(RestService.timestamp(),team_name))
            team_doc=MongoDBPersistence.teams_tbl.find_one({'TeamName':team_name,'DatasetID':{'$exists':True}},{'_id':0,'DatasetID':1})
            if(team_doc!=None):
                dataset_id=team_doc['DatasetID']
                logging.info('%s: Trying to delete all documents from "applicationDetails_tbl"'%RestService.timestamp())
                MongoDBPersistence.applicationDetails_tbl.delete_many({'CustomerID':customer_id,'DatasetID':dataset_id})
                logging.info('Trying to delete multiple documents from "resource_details_tbl"')
                MongoDBPersistence.resource_details_tbl.delete_many({'CustomerID':customer_id,'DatasetID':dataset_id})
                logging.info('Trying to delete multiple documents from "roaster_tbl"')
                MongoDBPersistence.roaster_tbl.delete_many({'CustomerID':customer_id,'DatasetID':dataset_id})
            else:
                logging.error('Could not get document from "teams_tbl"')
        except Exception as e:
            logging.error('%s: Error: %s'%(RestService.timestamp(), str(e)))
            return 'failure'
        return 'success'
    
    @staticmethod
    def get_application_team_names():
        resource_doc=MongoDBPersistence.applicationDetails_tbl.find_one({},{'_id':0,'CustomerID':1,'DatasetID':1})

        if(resource_doc):
            team=MongoDBPersistence.teams_tbl.find_one({"CustomerID" : resource_doc['CustomerID'], "DatasetID":resource_doc['DatasetID']},{'_id':0,'TeamName':1})['TeamName']
            return team;
        else:
            logging.info('%s: Could not fetch document from "applicationDetails_tbl"')
        return 'no team'
        
    @staticmethod
    def update_application_details(customer_id,dataset_id,record_id):

        logging.info('%s: In "update_application_details()" method'%RestService.timestamp())
        app_doc=request.get_json()
        
        try:
            logging.info('Trying to get document from "teams_tbl"')
            team_doc=MongoDBPersistence.teams_tbl.find_one({'CustomerID':customer_id,'DatasetID':dataset_id})
            if(team_doc!=None):
                MongoDBPersistence.applicationDetails_tbl.update_one({
                        'CustomerID':customer_id,'DatasetID':dataset_id,'record_id':record_id
                        },{
                                '$set':app_doc
                        })
            else:
                logging.error('Could not get document from "teams_tbl"')
                
        except Exception as e:
            logging.error('%s: Error: %s'%(RestService.timestamp(), str(e)))
            return('failure')
        return 'success'
    
    @staticmethod
    def get_ticketweightage_team_names():

        logging.info('%s: In "get_ticketweightage_team_names()" method, Trying to get document from "tickets_weightage_tbl"'%RestService.timestamp())
        team_doc=MongoDBPersistence.tickets_weightage_tbl.find_one({},{'_id':0,'CustomerID':1,'DatasetID':1})
        if(team_doc):
            team=MongoDBPersistence.teams_tbl.find_one({"CustomerID" : team_doc['CustomerID'], "DatasetID":team_doc['DatasetID']},{'_id':0,'TeamName':1})['TeamName']
            return(team);
        else:
            logging.info('%s: Could not get document from "tickets_weightage_tbl", returning failure'%RestService.timestamp())
        return('no team')