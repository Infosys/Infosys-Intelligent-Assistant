__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

from iia.persistence.mongodbpersistence import MongoDBPersistence
from iia.restservice import RestService
from bson import json_util
from flask import session
from flask import request
from iia.utils.log_helper import get_logger, log_setup

logging = get_logger(__name__)
app = RestService.getApp()


@app.route('/api/getTeamID/<int:customer_id>/<team_name>', methods=["GET"])
def getTeamID(customer_id, team_name):
    return TeamMasterData.getTeamID(customer_id, team_name)


@app.route('/api/getTeams/<int:customer_id>', methods=["GET"])
def getTeams(customer_id):
    return TeamMasterData.getTeams(customer_id)


@app.route('/api/getDatasetTeamNames/<int:customer_id>', methods=["GET"])
def getDatasetTeamNames(customer_id):
    return TeamMasterData.getDatasetTeamNames(customer_id)

@app.route('/api/getDatasetTeamNamesTraining/<int:customer_id>', methods=["GET"])
def getDatasetTeamNamesTraining( customer_id):
    return TeamMasterData.getDatasetTeamNamesTraining(customer_id)


@app.route('/api/getAllOpenIncidentCount/<int:customer_id>', methods=["GET"])
def getAllOpenIncidentCount(customer_id):
    return TeamMasterData.getAllOpenIncidentCount(customer_id)


@app.route('/api/getOpenIncidentCountTeam/<int:customer_id>/<team_name>', methods=["GET"])
def getOpenIncidentCountTeam(customer_id, team_name):
    return TeamMasterData.getOpenIncidentCountTeam(customer_id, team_name)


@app.route('/api/getNoDatasetTeamNames/<int:customer_id>', methods=["GET"])
def getNoDatasetTeamNames(customer_id):
    return TeamMasterData.getNoDatasetTeamNames(customer_id)


@app.route('/api/getTeamName/<int:customer_id>/<int:dataset_id>', methods=["GET"])
def getTeamName(customer_id, dataset_id):
    return TeamMasterData.getTeamName(customer_id, dataset_id)


@app.route('/api/getTeamsWithPredictedData/<int:customer_id>', methods=["GET"])
def getTeamsWithPredictedData(customer_id):
    return TeamMasterData.getTeamsWithPredictedData(customer_id)


@app.route('/api/getTeamNameWithId/<int:customer_id>', methods=["GET"])
def getTeamNameWithId(customer_id):
    return TeamMasterData.getTeamNameWithId(customer_id)


@app.route('/api/addTeam/<int:customer_id>', methods=['POST'])
def addTeam(customer_id):
    return TeamMasterData.addTeam(customer_id)


@app.route('/api/removeTeam/<int:customer_id>/<team_list>', methods=["DELETE"])
def removeTeam(customer_id, team_list):
    return TeamMasterData.removeTeam(customer_id, team_list)


@app.route('/api/getTagDatasetTeamNames/<int:customer_id>', methods=["GET"])
def getTagDatasetTeamNames(customer_id):
    return TeamMasterData.getTagDatasetTeamNames(customer_id)


@app.route('/api/getNoTagDatasetTeamNames/<int:customer_id>', methods=["GET"])
def getNoTagDatasetTeamNames(customer_id):
    return TeamMasterData.getNoTagDatasetTeamNames(customer_id)


@app.route('/api/getTagTeamID/<int:customer_id>/<team_name>', methods=["GET"])
def getTagTeamID(customer_id, team_name):
    return TeamMasterData.getTagTeamID(customer_id, team_name)


@app.route('/api/getEDATeamDetails', methods=["GET"])
def getEDATeamDetails():
    return TeamMasterData.getEDATeamDetails()


class TeamMasterData(object):
    '''
    classdocs
    '''

    def __init__(self, params):
        '''
        Constructor
        '''
    @staticmethod
    def getTeamID(customer_id, team_name):

        team_ = MongoDBPersistence.teams_tbl.find_one({"CustomerID": customer_id, "TeamName": team_name},
                                                      {"TeamID": 1, "_id": 0})
        if (team_):
            logging.info('%s: Getting dataset details.' % RestService.timestamp())
            team_id = team_["TeamID"]
        else:
            logging.info('%s: Dataset not found for the team.' % RestService.timestamp())
            return 'failure'
        return json_util.dumps(team_id)

    @staticmethod
    def getTeamName(customer_id, dataset_id):

        team_ = MongoDBPersistence.teams_tbl.find_one({"CustomerID": customer_id, "DatasetID": dataset_id},
                                                      {"TeamName": 1, "_id": 0})
        if (team_):
            logging.info('%s: Getting team name.' % RestService.timestamp())
            team_name = team_["TeamName"]
        else:
            logging.info('%s: Dataset not found for the team.' % RestService.timestamp())
            return 'failure'
        return json_util.dumps(team_name)

    @staticmethod
    def getTeams(customer_id):
        teams_dict = {}
        teams_list = []
        for team in list(MongoDBPersistence.teams_tbl.find({"CustomerID": customer_id}, {"TeamName": 1, "_id": 0})):
            teams_list.append(team['TeamName'])
        teams_dict['Teams'] = teams_list
        return json_util.dumps(teams_dict)

    @staticmethod
    def getDatasetTeamNames(customer_id):
        teams_dict = {}
        teams_list = []
        datasetid_list = []
        for team in list(MongoDBPersistence.teams_tbl.find({"CustomerID": customer_id, "DatasetID": {"$exists": True}},
                                                           {'_id': 0, "TeamName": 1, "DatasetID": 1})):
            teams_list.append(team['TeamName'])
            datasetid_list.append(team['DatasetID'])
        teams_dict['Teams'] = teams_list
        teams_dict['TeamCount'] = len(teams_list)
        teams_dict['DatasetIDs'] = datasetid_list
        return json_util.dumps(teams_dict)

    @staticmethod
    def getDatasetTeamNamesTraining(customer_id):
        teams_dict = {}
        teams_list = []
        datasetid_list = []
        for team in list(MongoDBPersistence.teams_tbl.find({"CustomerID" : customer_id, "DatasetID": {"$exists": True}},{'_id':0,"TeamName":1,"DatasetID":1})):
            teams_list.append(team['TeamName'])
            datasetid_list.append(team['DatasetID'])
        teams_dict['Teams'] = teams_list
        teams_dict['TeamCount'] = len(teams_list)
        teams_dict['DatasetIDs'] = datasetid_list
        return json_util.dumps(teams_dict)

    @staticmethod
    def getTeamsWithPredictedData(customer_id):

        teams_dict = {}
        teams_list = []
        datasetid_list = []

        if (session.get('user')):
            logging.info("%s Catching User Session" % RestService.timestamp())
            user = session['user']
            role = session['role']
            logging.info("%s Session catched user as  %s" % (RestService.timestamp(), user))
            if (role == 'Admin'):
                dataset_values = MongoDBPersistence.predicted_tickets_tbl.find({"CustomerID": customer_id}).distinct(
                    "DatasetID")
                logging.info(f"dataset_values: {dataset_values}")
                for dataset in dataset_values:

                    team = MongoDBPersistence.teams_tbl.find_one({"CustomerID": customer_id, "DatasetID": dataset},
                                                                 {'_id': 0, "TeamName": 1})
                    print(team)
                    if team != None:
                        teams_list.append(team['TeamName'])

                teams_dict['Teams'] = teams_list
            else:
                match_doc = {'UserID': user}
                logging.info(f"match_doc: {match_doc}")
                team_ids = MongoDBPersistence.users_tbl.find(match_doc).distinct(
                    "TeamID")
                logging.info(f"team_ids: {team_ids}")
                if (team_ids):
                    for team_id in team_ids:
                        logging.info(f"team_id: {team_id}")
                        team_doc = MongoDBPersistence.teams_tbl.find_one({'TeamID': int(team_id)})
                        logging.info(f"team_doc: {team_doc}")
                        if (team_doc):
                            DatasetId = team_doc['DatasetID']
                            dataset_id = MongoDBPersistence.predicted_tickets_tbl.find_one(
                                {"CustomerID": customer_id, 'DatasetID': DatasetId})

                            if dataset_id:
                                teams_list.append(team_doc['TeamName'])

                            teams_dict['Teams'] = teams_list
                        else:
                            logging.warn('There is no document in Tbl_Teams with team id %s' % str(team_id))
                else:
                    logging.warn('There is no document in Tbl_Users with user_id %s' % user)
        else:
            logging.info("%s You are not logged in please login" % RestService.timestamp())
            return "No Login Found"

        logging.info(f"teams_dict: {teams_dict}")
        return json_util.dumps(teams_dict)

    @staticmethod
    def getAllOpenIncidentCount(customer_id):
        count = MongoDBPersistence.rt_tickets_tbl.find(
            {"CustomerID": customer_id, "state": "New", "DatasetID": {"$exists": True}}).count()
        if (count):
            return json_util.dumps(str(count))
        else:
            return json_util.dumps('empty')

    @staticmethod
    def getOpenIncidentCountTeam(customer_id, team_name):

        dataset_id_dict = MongoDBPersistence.teams_tbl.find_one({"CustomerID": customer_id, "TeamName": team_name},
                                                                {"DatasetID": 1, "_id": 0})
        if (dataset_id_dict):
            dataset_id = dataset_id_dict['DatasetID']
            count = MongoDBPersistence.rt_tickets_tbl.find(
                {"CustomerID": customer_id, "state": "New", "DatasetID": dataset_id}).count()
            if (count):
                resp = str(count)
            else:
                resp = 'empty'
        else:
            logging.info("Dataset not found for the team.")
            resp = 'empty'
        return json_util.dumps(resp)

    @staticmethod
    def getNoDatasetTeamNames(customer_id):
        teams_dict = {}
        teams_list = []
        for team in list(MongoDBPersistence.teams_tbl.find({"CustomerID": customer_id, "DatasetID": {"$exists": False}},
                                                           {'_id': 0, "TeamName": 1})):
            teams_list.append(team['TeamName'])
        teams_dict['Teams'] = teams_list
        return json_util.dumps(teams_dict)

    @staticmethod
    def getTeamNameWithId(customer_id):
        teams_list = MongoDBPersistence.teams_tbl.find({"CustomerID": customer_id}, {"_id": 0})

        return json_util.dumps(teams_list)

    @staticmethod
    def addTeam(customer_id):
        team_list = request.get_json()
        team_doc_lst = []

        team_doc = MongoDBPersistence.teams_tbl.find_one(sort=[('TeamID', -1)])
        if (team_doc):
            team_id = team_doc['TeamID']
        else:
            team_id = 1
        team_names = MongoDBPersistence.teams_tbl.find({}, {'_id': 0, 'TeamName': 1}).distinct('TeamName')

        for team in team_list:
            team.pop('Selected', None)
            keys = team.keys()
            if ('TeamID' not in keys and team['TeamName'] not in team_names):
                team_id = team_id + 1
                team['TeamID'] = team_id
                team['CustomerID'] = customer_id

                team_doc_lst.append(team)
                team_names.append(team['TeamName'])

                assign_enable_lst = []
                assign = {}
                assign["TeamID"] = team_id
                assign["assignment_enabled"] = "true"
                assign["t_value_enabled"] = "false"
                assign["prediction_enabled"] = "true"
                assign["threshold_value"] = 0
                assign["iOpsStatus"] = "false"
                assign["iOpsPath"] = ""
                assign["regex_enabled"] = "false"
                assign["db_enabled"] = "false"
                assign["spacy_enabled"] = "false"
                assign["roundrobin_enabled"] = "false"
                assign["non_english_description_flag"] = "false"
                assign_enable_lst.append(assign)
                MongoDBPersistence.assign_enable_tbl.insert_many(assign_enable_lst)


            elif (team['TeamName'] not in team_names):
                logging.info('%s: trying to update team documents to team collection' % RestService.timestamp)
                MongoDBPersistence.teams_tbl.update_one({'TeamID': team['TeamID'], 'CustomerID': customer_id},
                                                        {'$set': team})
                logging.info('%s: documents updated successfully' % RestService.timestamp)

        if (team_doc_lst):
            logging.info('%s: trying to insert new team documents to team collection' % RestService.timestamp)
            MongoDBPersistence.teams_tbl.insert_many(team_doc_lst)
            logging.info('%s: documents inserted successfully' % RestService.timestamp)

        return ('success')

    @staticmethod
    def removeTeam(customer_id, team_list):

        if (team_list):
            team_string_lst = team_list.split(',')

            for team_id_str in team_string_lst:
                team_id = int(team_id_str)
                logging.info('%s: trying to update team documents to team collection' % RestService.timestamp)
                MongoDBPersistence.teams_tbl.delete_one(
                    {'CustomerID': customer_id, 'TeamID': team_id, 'DatasetID': {'$exists': False}})
                MongoDBPersistence.assign_enable_tbl.delete_one({'TeamID': team_id})
                logging.info('%s: documents updated successfully' % RestService.timestamp)
            return 'success'
        else:
            logging.info("couldnt delete team")
            return 'failure'

    @staticmethod
    def getTagDatasetTeamNames(customer_id):
        teams_dict = {}
        teams_list = []
        datasetid_list = []
        for team in list(
                MongoDBPersistence.teams_tbl.find({"CustomerID": customer_id, "TagsDatasetID": {"$exists": True}},
                                                  {'_id': 0, "TeamName": 1, "TagsDatasetID": 1})):
            teams_list.append(team['TeamName'])
            datasetid_list.append(team['TagsDatasetID'])
        teams_dict['Teams'] = teams_list
        teams_dict['TeamCount'] = len(teams_list)
        teams_dict['TagsDatasetIDs'] = datasetid_list
        return json_util.dumps(teams_dict)

    @staticmethod
    def getNoTagDatasetTeamNames(customer_id):
        teams_dict = {}
        teams_list = []
        trained_teams_list = []
        datasets_list = []
        tags_team_list = []
        for team in list(
                MongoDBPersistence.teams_tbl.find({"CustomerID": customer_id, "TagsDatasetID": {"$exists": False}},
                                                  {'_id': 0, "TeamName": 1})):
            teams_list.append(team['TeamName'])
        for dataset_team in list(MongoDBPersistence.training_hist_tbl.find(
                {"CustomerID": customer_id, "TrainingStatus": {"$exists": True, "$in": ['Approved']}},
                {'_id': 0, "DatasetID": 1})):
            datasets_list.append(dataset_team['DatasetID'])
        for dataset in datasets_list:
            trained_teams_list.append(
                MongoDBPersistence.teams_tbl.find_one({"CustomerID": customer_id, "DatasetID": dataset},
                                                      {"_id": 0, "TeamName": 1})['TeamName'])

        for team in teams_list:
            if team in trained_teams_list:
                tags_team_list.append(team)
        teams_dict['Teams'] = tags_team_list
        return json_util.dumps(teams_dict)

    @staticmethod
    def getTagTeamID(customer_id, team_name):

        team_ = MongoDBPersistence.teams_tbl.find_one({"CustomerID": customer_id, "TeamName": team_name},
                                                      {"TeamID": 1, "_id": 0})
        if (team_):
            logging.info('%s: Getting dataset details.' % RestService.timestamp())
            team_id = team_["TeamID"]
        else:
            logging.info('%s: Dataset not found for the team.' % RestService.timestamp())
            return 'failure'
        return json_util.dumps(team_id)

    @staticmethod
    def getEDATeamDetails():
        teams = MongoDBPersistence.teams_tbl.find({}, {"_id": 0})
        return json_util.dumps(list(teams))
