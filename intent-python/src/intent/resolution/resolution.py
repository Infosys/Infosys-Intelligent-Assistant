__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

from intent.masterdata.customers import CustomerMasterData
from intent.persistence.mongodbpersistence import MongoDBPersistence
from intent.restservice import RestService
# from intent.utils.stringutils import StringUtils
# from intent.predict.predict import Predict
from intent.masterdata.resources import ResourceMasterData
from intent.itsm.servicenow import ServiceNow
from pathlib import Path
import joblib
from nltk.cluster.util import cosine_distance
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from bson import json_util
from flask import request
# import logging
import json
import pandas as pd
import re
import importlib
import configparser
import subprocess
import sys
from intent.incident.incidenttraining import IncidentTraining
import requests
import getpass, signal
import os, time, csv, subprocess
from os import listdir
from os.path import isfile, join
# import py_compile
import ast
import inspect
import datetime
import xml.etree.ElementTree as ET
# from flask_cors import CORS
import time
from cryptography.fernet import Fernet
from intent.utils.log_helper import get_logger, log_setup
from intent.utils.config_helper import get_config
import xmltodict
import string
import random
import base64
import pysnow

logging = get_logger(__name__)
# log_setup()

app = RestService.getApp()


@app.route("/api/executePowershellScript/<script>", methods=["GET"])
def executePowershellScript(script):
    return Resolution.executePowershellScript(script)


@app.route("/api/executeBatch/<jobs>", methods=["GET"])
def executeBatch(jobs):
    return Resolution.executeBatch(jobs)


@app.route("/api/executeRPA/<process_name>", methods=["GET"])
def executeRPA(process_name):
    return Resolution.executeRPA(process_name)


@app.route("/api/saveScriptDetails", methods=["POST"])
def saveScriptDetails():
    return Resolution.saveScriptDetails()


@app.route("/api/saveScriptMatchPercent/<percent>", methods=["POST"])
def saveScriptMatchPercent(percent):
    return Resolution.saveScriptMatchPercent(percent)


@app.route("/api/getScriptMatchPercent", methods=["GET"])
def getScriptMatchPercent():
    return Resolution.getScriptMatchPercent()


@app.route("/api/getTopFiveScripts", methods=["GET"])
def getTopFiveScripts():
    return Resolution.getTopFiveScripts()


@app.route("/api/getAllIopsScripts", methods=["GET"])
def getAllIopsScripts():
    return Resolution.getAllIopsScripts()


@app.route("/api/invokeIopsScripts", methods=["POST"])
def invokeIopsScripts():
    script_name = request.form['ScriptName']
    env = request.form['Environment']
    script_type = request.form['Type']
    args = ast.literal_eval(request.form['Args'])
    #args = json.loads(request.form['Args'])
    #args.update({'auto_resolution':False})
    return Resolution.invokeIopsScripts(script_name=script_name,env=env,script_type=script_type,args=args)


@app.route("/api/getScripts", methods=["GET"])
def getScripts():
    return Resolution.getScripts()


@app.route("/api/deleteiOpsScript", methods=["POST"])
def deleteiOpsScript():
    return Resolution.deleteiOpsScript()


@app.route("/api/compileCode", methods=["POST"])
def compileCode():
    return Resolution.compileCode()


@app.route("/api/SaveCode", methods=["POST"])
def SaveCode():
    return Resolution.SaveCode()


@app.route("/api/getScriptsFromPath", methods=["GET"])
def getScriptsFromPath():
    return Resolution.getScriptsFromPath()


@app.route("/api/getDiagnosticScriptsFromPath", methods=["GET"])
def getDiagnosticScriptsFromPath():
    return Resolution.getDiagnosticScriptsFromPath()


@app.route("/api/getScriptContent/<name>/<script_type>", methods=["GET"])
def getScriptContent(name, script_type):
    return Resolution.getScriptContent(name, script_type)


@app.route("/api/SaveResolutionDetails", methods=["POST"])
def SaveResolutionDetails():
    return Resolution.SaveResolutionDetails()


@app.route("/api/getResolutionHistory/<desc>/<resolution_type>", methods=["GET"])
def getResolutionHistory(desc, resolution_type):
    return Resolution.getResolutionHistory(desc, resolution_type)


@app.route("/api/getEnvironments", methods=["GET"])
def getEnvironments():
    return Resolution.getEnvironments()


@app.route("/api/SaveEnvironments", methods=["POST"])
def SaveEnvironments():
    return Resolution.SaveEnvironments()


@app.route("/api/deleteEnvironments", methods=["POST"])
def deleteEnvironments():
    return Resolution.deleteEnvironments()


@app.route("/api/ping", methods=["POST"])
def ping():
    return Resolution.ping()


@app.route("/api/getPossibleResolutions", methods=["POST"])
def getPossibleResolutions():
    number = request.form['Number']
    desc = request.form['Desc']
    tags = json.loads(request.form['Tags'])
    return Resolution.getPossibleResolutions(number=number,desc=desc,tags=tags)


@app.route("/api/getAuditLogs/<incident_no>", methods=["GET"])
def getAuditLogs(incident_no):
    return Resolution.getAuditLogs(incident_no)


@app.route("/api/getArguments/<script_type>/<script_name>", methods=["GET"])
def getArguments(script_type, script_name):
    return Resolution.getArguments(script_type, script_name)


@app.route("/api/getDiagnosticScript/<name>", methods=["GET"])
def getDiagnosticScript(name):
    return Resolution.getDiagnosticScript(name)


@app.route("/api/getArgumentsFromFile", methods=["POST"])
def getArgumentsFromFile():
    return Resolution.getArgumentsFromFile()


@app.route("/api/getworkflow", methods=["Get"])
def getworkflow():
    return Resolution.getworkflow()


@app.route("/api/saveBPMN/<name>", methods=["POST"])
def saveBPMN(name):
    return Resolution.saveBPMN(name)


@app.route("/api/editBPMN/<name>", methods=["GET"])
def editBPMN(name):
    return Resolution.editBPMN(name)


@app.route("/api/saveworkflowkeywords", methods=["Post"])
def saveworkflowkeywords():
    return Resolution.saveworkflowkeywords()


@app.route("/api/saveWorkflow", methods=["POST"])
def saveWorkflow():
    return Resolution.saveWorkflow()


@app.route("/api/executeWorkFlow/<workflow_name>/<incident_no>", methods=["GET", "POST"])
def executeWorkFlow(workflow_name, incident_no):
    print("workflow_name:", workflow_name)
    print("incident_no:", incident_no)
    return Resolution.executeWorkFlow(workflow_name, incident_no)


@app.route("/api/assignmentmodule", methods=["GET"])
def assignmentmodule():
    return Resolution.assignmentmodule()


@app.route("/api/saveColName/<column_name>", methods=["POST"])
def saveColName(column_name):
    return Resolution.saveColName(column_name)


@app.route('/api/incident_entity/<int:customer_id>/<ticket_number>', methods=['GET'])
def incident_entity(customer_id, ticket_number):
    return Resolution.incident_entity(customer_id, ticket_number)


@app.route("/api/get_entity_tags/<ticket_number>", methods=['GET'])
def get_entity_tags(ticket_number):
    return Resolution.get_entity_tags(ticket_number)


@app.route('/api/get_annoted_data')
def get_annoted_data():
    return Resolution.get_annoted_data()


@app.route('/api/save_tag_name/<int:customer_id>/<int:dataset_id>/<tag_name>', methods=['PUT'])
def save_tag_name(customer_id, dataset_id, tag_name):
    return Resolution.save_tag_name(customer_id, dataset_id, tag_name)


@app.route("/api/annotated_data/<ticket_number>", methods=['PUT'])
def annotated_data(ticket_number):
    return Resolution.annotated_data(ticket_number)


@app.route("/api/remove_tag_name/<int:customer_id>/<int:dataset_id>/<ticket_number>", methods=['POST'])
def remove_tag_name(customer_id, dataset_id, ticket_number):
    return Resolution.remove_tag_name(customer_id, dataset_id, ticket_number)


@app.route("/api/clearResolutionLogs/<ticketNumber>", methods=["GET"])
def clearResolutionLogs(ticketNumber):
    return Resolution.clearResolutionLogs(ticketNumber)


@app.route("/api/botfactoryListenersResponse/<process_id>", methods=['POST'])
def botfactoryListenersResponse(process_id):
    return Resolution.botfactoryListenersResponse(process_id)


@app.route("/api/saveMappingKeywords", methods=["POST"])
def saveMappingKeywords():
    return Resolution.saveMappingKeywords()


class Resolution(object):
    '''
    classdocs
    '''

    def __init__(self, params):
        '''
        Constructor
        '''

    @staticmethod
    def executePowershellScript(script):
        try:

            if (script == "Script 1"):
                filepath = ".\scripts\powershellScript1.ps1"
                resp = subprocess.Popen(["powershell.exe", filepath], stdout=sys.stdout)
                resp.communicate()
                # print(resp.communicate)
                # print(resp)
                return 'success'
            elif (script == "Script 2"):
                filepath = ".\scripts\powershellScript2.ps1"
                resp = subprocess.Popen(["powershell.exe", filepath], stdout=sys.stdout)
                resp.communicate()
                # print(resp.communicate)
                # print(resp)
                return 'success'
            elif (script == "Script 3"):
                filepath = ".\scripts\powershellScript3.ps1"
                resp = subprocess.Popen(["powershell.exe", filepath], stdout=sys.stdout)
                resp.communicate()
                # print(resp.communicate)
                # print(resp)
                return 'success'
            elif (script == "Script 4"):
                filepath = ".\scripts\powershellScript4.ps1"
                resp = subprocess.Popen(["powershell.exe", filepath], stdout=sys.stdout)
                resp.communicate()
                # print(resp.communicate)
                # print(resp)
                return 'success'
        except Exception as e:
            logging.error('%s: Error inside executePowershellScript: %s' % (RestService.timestamp(), str(e)))
            return str(e)

    @staticmethod
    def executeBatch(jobs):
        try:

            if (jobs == "Jobs 1"):
                filepath = ".\scripts\script1.bat"
                resp = subprocess.call([filepath])
                # print(resp)
                if resp == 0:
                    return 'success'
                else:
                    return 'failure'
            elif (jobs == "Jobs 2"):
                filepath = ".\scripts\script2.bat"
                resp = subprocess.call([filepath])
                # print(resp)
                if resp == 0:
                    return 'success'
                else:
                    return 'failure'
            elif (jobs == "Jobs 3"):
                filepath = ".\scripts\script3.bat"
                resp = subprocess.call([filepath])
                # print(resp)
                if resp == 0:
                    return 'success'
                else:
                    return 'failure'
            elif (jobs == "Jobs 4"):
                filepath = ".\scripts\script4.bat"
                resp = subprocess.call([filepath])
                # print(resp)
                if resp == 0:
                    return 'success'
                else:
                    return 'failure'
        except Exception as e:
            logging.error('%s: Error in executeBatch: %s' % (RestService.timestamp(), str(e)))
            return str(e)

        # print(resp)

    @staticmethod
    def saveScriptDetails():

        try:

            operation = request.form['Operation']
            scripts = json.loads(request.form['Scripts'])
            if (operation == 'Management'):

                for script in scripts:

                    MongoDBPersistence.script_configuration_tbl.update_one({'scriptName': script['scriptName']},
                                                                           {'$set': script})
            else:
                for script in scripts:
                    MongoDBPersistence.script_configuration_tbl.update_one({'scriptName': script['scriptName']},
                                                                           {'$set': {'keyword': script['keyword']}},
                                                                           upsert=False)
            return "Success"
        except Exception as e:
            logging.error('%s: Error in saveScriptDetails: %s' % (RestService.timestamp, str(e)))
            return "Failure"

    @staticmethod
    def saveMappingKeywords():

        try:
            scripts_fe = json.loads(request.form['Scripts'])
            print('scripts......', scripts_fe)
            py_scripts_tbl = MongoDBPersistence.script_configuration_tbl.find({}, {"_id": 0})
            for script in py_scripts_tbl:
                for i in scripts_fe:
                    if i['scriptName'] == script['scriptName']:
                        if ('str' in str(type(i['keyword']))):
                            keyword_lst1 = i['keyword'].split(',')
                        else:
                            keyword_lst1 = i['keyword']
                            if keyword_lst1 in ['',[],['']]:
                                return 'Failure: Keywords not provided.'
                        script['keyword'] = keyword_lst1
                MongoDBPersistence.script_configuration_tbl.update_one({'scriptName': script['scriptName']},
                                                                       {'$set': {'keyword': script['keyword']}})
            rpa_scripts_tbl = MongoDBPersistence.rpa_configuration_tbl.find({}, {"_id": 0})
            for script in rpa_scripts_tbl:
                for i in scripts_fe:
                    if i['scriptName'] == script['scriptName']:
                        if ('str' in str(type(i['keyword']))):
                            keyword_lst2 = i['keyword'].split(',')
                        else:
                            keyword_lst2 = i['keyword']
                            if keyword_lst1 in ['',[],['']]:
                                return 'Failure: Keywords not provided.'
                        script['keyword'] = keyword_lst2
                MongoDBPersistence.rpa_configuration_tbl.update_one({'scriptName': script['scriptName']},
                                                                    {'$set': {'keyword': script['keyword']}})
            return "Success"
        except Exception as e:
            logging.error('%s: Error: %s' % (RestService.timestamp, str(e)))
            return "Failure"

    @staticmethod
    def saveScriptMatchPercent(percent):
        temp = float(percent)
        try:
            if (temp != None and temp > 0 and temp <= 100):
                MongoDBPersistence.configuration_values_tbl.update_one({}, {'$set': {'script_match_percent': temp}},
                                                                       upsert=True)
                return "Success"
        except Exception as e:
            logging.error('%s: Error in saveScriptMatchPercent: %s' % (RestService.timestamp, str(e)))
        return "Failure"

    @staticmethod
    def getScriptMatchPercent():

        try:

            source = MongoDBPersistence.configuration_values_tbl.find_one({}, {"script_match_percent": 1, "_id": 0})

            if (source):
                resp = json_util.dumps(source)
            else:
                resp = 'Failure'

            return resp
        #            else:
        #                MongoDBPersistence.assign_enable_tbl.update_one({},{'$unset':{'threshold_value':1}})
        except Exception as e:
            logging.error('%s: Error in getScriptMatchPercent: %s' % (RestService.timestamp, str(e)))
            #            print('Failure')
            return "Failure"

    @staticmethod
    def getTopFiveScripts():

        try:

            scripts = MongoDBPersistence.script_configuration_tbl.find({}, {"_id": 0})


            if (scripts):
                return json_util.dumps(scripts)
            else:
                return "No Scripts"


        except Exception as e:
            logging.error('%s: Error in getTopFiveScripts: %s' % (RestService.timestamp, str(e)))
            # print(e)
            #            print('Failure')
            return "Failure"

    @staticmethod
    def scriptMatch(script1, script2, stopwords_english):

        try:

            script1 = [w.lower() for w in script1]
            script2 = [w.lower() for w in script2]

            logging.debug(f"script1: {script1}")
            logging.debug(f"script2: {script2}")

            script1 = ''.join([str(elem) for elem in script1])
            script2 = ' '.join([str(elem) for elem in script2])

            logging.debug(f"script1: {script1}")
            logging.debug(f"script2: {script2}")

            script1 = re.sub(r'\n', " ", script1)
            script1 = re.sub("[^A-Za-z0-9]+", " ", script1)

            script2 = re.sub(r'\n', " ", script2)
            script2 = re.sub("[^A-Za-z0-9]+", " ", script2)

            logging.debug(f"script1: {script1}")
            logging.debug(f"script2: {script2}")

            logging.debug(f"script1: {script1}")
            logging.debug(f"script2: {script2}")
            X_list = word_tokenize(script1)
            Y_list = word_tokenize(script2)

            # sw contains the list of stopwords
            if stopwords_english is None:
                stopwords_english = stopwords.words('english')

            l1 = []
            l2 = []

            # remove stop words from the string
            X_set = {w for w in X_list if not w in stopwords_english}
            Y_set = {w for w in Y_list if not w in stopwords_english}

            # form a set containing keywords of both strings
            rvector = X_set.union(Y_set)
            for w in rvector:
                if w in X_set:
                    l1.append(1)  # create a vector
                else:
                    l1.append(0)
                if w in Y_set:
                    l2.append(1)
                else:
                    l2.append(0)
            c = 0

            # cosine formula
            for i in range(len(rvector)):
                c += l1[i] * l2[i]
            cosine = c / float((sum(l1) * sum(l2)) ** 0.5)
            cosine = cosine * 100
            logging.debug(f"cosine: {cosine}")
            return cosine



        except Exception as e:
            logging.error('%s: Error in scriptMatch: %s' % (RestService.timestamp, str(e)))
            return 0.0

    @staticmethod
    def inputArguments(args, file):
        try:
            with open(file) as f:
                s = f.read()
            if args:
                text = "main("
                for key, value in args.items():
                    if (str(type(value)).__contains__('str')):
                        text = text + "'" + value + "',"
                    else:
                        text = text + str(value) + ','
                text = text[:-1] + ')'
            with open('Temp.py', 'w') as f:
                f.write(s)
            
            with open('Temp.py', 'a') as f:
                f.write('\n' + text)
            
            return 'Success'

        except Exception as e:
            logging.error(str(e),exc_info=True)
            return 'Failure' + '\n' + str(e)

    @staticmethod
    def invokeIopsScripts(script_name:str,env:str,script_type:str,args:dict):

        logging.info(f"script_name: {script_name}")
        logging.info(f"env: {env}")
        logging.info(f"script_type: {script_type}")
        logging.info(f"args: {args}")
        try:
            #--------------Manual Resolution-----------------------------
            #if(args['auto_resolution']==False):
            #    del args['auto_resolution']
            #Checking arguments
            print("before loads...",args)
            #args=ast.literal_eval(args)
            print('loads...',args," ",type(args))
            for k,v in args.items():
                if('str' in str(type(v))):
                    v=v.replace("'","\"")
                try:
                    # v=json.loads(v)
                    v=ast.literal_eval(v)
                except:
                    pass
                args[k]=v
            
            print("args123........loads...2",args," ",type(args))

            if (env.lower() == 'local'):
                if (script_type == 'main'): 
                    #Validating arguments datatype from DB
                    args_db=MongoDBPersistence.script_configuration_tbl.find_one({"scriptName": script_name}, {"_id": 0,"arguments":1})
                    
                    for k,v in args.items():
                        if args_db['arguments'][k] not in str(type(v)):
                            res='Failure: Please enter argument with correct datatype.'
                            return res

                    mypath = 'scripts\\' + script_name
                    Resolution.inputArguments(args, mypath)
                else:
                    #Validating arguments datatype from DB
                    args_db=MongoDBPersistence.diagnostic_tbl.find_one({"scriptName": script_name}, {"_id": 0,"arguments":1})

                    for k,v in args.items():
                        if args_db['arguments'][k] not in str(type(v)):
                            res='Failure: Please enter argument with correct datatype.'
                            return res

                    mypath = 'scripts\\diagnostic-scripts\\' + script_name
                    Resolution.inputArguments(args, mypath)
                return_text = ''
                #                cmd_to_execute='python '+mypath
                cmd_to_execute = 'python -W ignore Temp.py'
                sub = subprocess.Popen(cmd_to_execute, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, universal_newlines=True, shell=True)

                sub_out, sub_err = sub.communicate()
                # print('sub_out, sub_err....',sub_out, sub_err)
                sub_err = sub_err.strip()
                # print('sub_err...',sub_err)
                return_text = str(sub_out) + str(sub_err)
                return_text = return_text.strip()
                # print(str(return_text))
                return str(return_text)
            else:
                envs = MongoDBPersistence.environments_tbl.find_one({'name': env}, {"_id": 0})
                # print(envs)
                decode = envs['password']
                key = Resolution.callKey()
                b = Fernet(key)
                decoded_slogan = b.decrypt(decode)
                decoded_slogan = decoded_slogan.decode('ascii')
                if (script_type == 'main'):
                    mypath = 'scripts\\' + script_name
                    Resolution.inputArguments(args, mypath)
                    cmd2_to_execute = 'cmd.exe /c echo y | plink.exe ' + envs['username'] + '@' + envs[
                        'name'] + ' -pw ' + envs['password'] + ' python C:\Temp.py'

                else:
                    mypath = 'scripts\\diagnostic-scripts\\' + script_name
                    Resolution.inputArguments(args, mypath)
                    cmd2_to_execute = 'cmd.exe /c echo y | plink.exe ' + envs['username'] + '@' + envs[
                        'name'] + ' -pw ' + envs['password'] + ' python C:\Temp.py'

                cmd_to_execute = 'cmd.exe /c echo y | pscp.exe -pw ' + decoded_slogan + ' Temp.py ' + envs[
                    'username'] + '@' + envs['name'] + ':C:\\'
                sub = subprocess.Popen(cmd_to_execute, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, universal_newlines=True, shell=True)
                sub_out, sub_err = sub.communicate()
                sub_err = sub_err.strip()
                return_text = str(sub_out) + str(sub_err)
                return_text = return_text.strip()
                time.sleep(1)

                sub = subprocess.Popen(cmd2_to_execute, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, universal_newlines=True, shell=True)
                sub_out, sub_err = sub.communicate()

                sub_err = sub_err.strip()
                return_text = return_text + '\n' + str(sub_out) + str(sub_err)
                return_text = return_text.strip()
                # print('1'+str(os.path.exists('Temp.py')))
                # print('2'+str(os.path.exists('Temp.txt')))
                if (os.path.exists('Temp.py')):
                    os.remove('Temp.py')
                if (os.path.exists('Temp.txt')):
                    os.remove('Temp.txt')
                # print(str(return_text))
                return str(return_text)
        except Exception as e:
            # print(str(e))
            if (os.path.exists('Temp.py')):
                os.remove('Temp.py')
            if (os.path.exists('Temp.txt')):
                os.remove('Temp.txt')
            return 'Command execution exception: ' + str(e)

    @staticmethod
    def getScripts():
        try:

            scripts = MongoDBPersistence.script_configuration_tbl.find({}, {"scriptName": 1, "argument": 1, "_id": 0})

            if (scripts):
                return json_util.dumps(scripts)
            else:

                return "No Scripts"


        except Exception as e:
            logging.error('%s: Error in getScripts: %s' % (RestService.timestamp, str(e)))
            # print(e)
            #            print('Failure')
            return "Failure"

    @staticmethod
    def getworkflow():
        try:

            workflow = MongoDBPersistence.workflow_tbl.find({}, {"_id": 0, 'BPMN_Content': 0})

            if (workflow):
                return json_util.dumps(workflow)
            else:
                return "No workflow"

        except Exception as e:
            # logging.error('%s: Error: %s'%(RestService.timestamp,str(e)))
            # print(e)

            return "Failure"

    @staticmethod
    def executeRPA(process_name):

        try:

            URL = "UI_PATH_URL"+"/api/Account/Authenticate"

            body = {"tenancyName": "Default", "usernameOrEmailAddress": "admin", "password": "password"}
            headers = {'Content-Type': 'application/json'}
            r = requests.post(URL, data=json.dumps(body), headers=headers, verify=False).json()
            auth_token = "Bearer " + r['result']
            URL = "UI_PATH_URL"+"/odata/Releases"
            headers = {'Content-Type': 'application/json', 'Authorization': auth_token}
            r = requests.get(URL, headers=headers, verify=False).json()
            key = ' '
            for item in r['value']:
                if item['ProcessKey'] == process_name:
                    key = item['Key']
                    env_name = item['EnvironmentName']
            if key == ' ':
                return "Process Name is not found."
            pname = "'" + process_name + "'"
            URL = "UI_PATH_URL"+"/odata/Robots/UiPath.Server.Configuration.OData.GetRobotsForProcess(processId=" + pname + ')'
            headers = {'Content-Type': 'application/json', 'Authorization': auth_token}
            r = requests.get(URL, headers=headers, verify=False).json()
            robot_ids = []
            user = getpass.getuser().lower()
            domain = os.environ['userdomain'].lower()
            username = domain + "\\" + user
            for i in r['value']:
                if i['Username'] == username and i['MachineName'] == env_name:
                    robot_ids.append(i['Id'])
            if (len(robot_ids) == 0):
                return "No robots found to run the process."

            URL = "UI_PATH_URL"+"odata/Jobs/UiPath.Server.Configuration.OData.StartJobs"
            body = {"startInfo": {"ReleaseKey": key, "RobotIds": robot_ids, "NoOfRobots": 0, "Strategy": "Specific"}}
            headers = {'Content-Type': 'application/json', 'Authorization': auth_token}
            r = requests.post(URL, data=json.dumps(body), headers=headers, verify=False).json()
            job_keys = []
            for j in r['value']:
                job_keys.append(j['Key'])
            # print(job_keys)
            job_info = []
            for k in job_keys:
                while True:
                    URL = "UI_PATH_URL"+"/odata/Jobs?$filter=Key eq" + k
                    headers = {'Content-Type': 'application/json', 'Authorization': auth_token}
                    r = requests.get(URL, headers=headers, verify=False).json()
                    # print(r)
                    # print("1")
                    for h in r['value']:
                        state = h['State']
                        info = h['Info']
                    if state != "Running":

                        job_info.append(info)
                        break
                    else:
                        time.sleep(15)

            return json_util.dumps(job_info)
        except Exception as e:
            logging.error('%s: Error in executeRPA: %s' % (RestService.timestamp(), str(e)))
            return json_util.dumps(str(e))

    @staticmethod
    def getAllIopsScripts():

        try:

            scripts = MongoDBPersistence.script_configuration_tbl.find({}, {"_id": 0})
            # print(scripts)
            if (scripts):
                return json_util.dumps(scripts)
            else:
                return "No Scripts"

        except Exception as e:
            logging.error('%s: Error in getAllIopsScripts: %s' % (RestService.timestamp, str(e)))
            print(e)
            #            print('Failure')
            return "Failure"

    @staticmethod
    def deleteiOpsScript():
        script_names = request.form['Scripts'].split(',')
        try:

            for i in script_names:
                # print(i)
                MongoDBPersistence.script_configuration_tbl.delete_one({'scriptName': i})
                
                os.remove('scripts//'+i)

            return "Success"
        except Exception as e:
            logging.error('%s: Error in deleteiOpsScript: %s' % (RestService.timestamp, str(e)))
            print(e)
            #            print('Failure')
            return "Failure"

    @staticmethod
    def getScriptsFromPath():

        try:

            mypath = 'scripts'
            Resolution.check_path(mypath)
            onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
            return json_util.dumps(onlyfiles)
        except Exception as e:
            logging.error('%s: Error in getScriptsFromPath: %s' % (RestService.timestamp, str(e)))
            print(e)
            #            print('Failure')
            return "Failure"

    @staticmethod
    def getDiagnosticScriptsFromPath():

        try:

            mypath = mypath = 'scripts\\diagnostic-scripts'
            Resolution.check_path(mypath)
            onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
            return json_util.dumps(onlyfiles)
        except Exception as e:
            logging.error('%s: Error in getDiagnosticScriptsFromPath: %s' % (RestService.timestamp, str(e)))
            print(e)
            #            print('Failure')
            return "Failure"

    @staticmethod
    def getDiagnosticScript(name):

        try:

            scripts = MongoDBPersistence.script_configuration_tbl.find_one({'scriptName': name}, {"_id": 0})[
                'diagnostic_script']
            # print(scripts)
            if (scripts):
                return json_util.dumps(scripts)
            else:
                return "No Scripts"
        except Exception as e:
            logging.error('%s: Error in getDiagnosticScript: %s' % (RestService.timestamp, str(e)))
            print(e)
            #            print('Failure')
            return "Failure"

    @staticmethod
    def getArguments(script_type, script_name):

        try:

            if (script_type == 'main'):
                args = MongoDBPersistence.script_configuration_tbl.find_one({'scriptName': script_name}, {"_id": 0})[
                    'arguments']
            else:
                args = MongoDBPersistence.diagnostic_tbl.find_one({'scriptName': script_name}, {"_id": 0})['arguments']

            return json_util.dumps(args)
        except Exception as e:
            logging.error('%s: Error in getArguments: %s' % (RestService.timestamp, str(e)))
            print(e)
            #            print('Failure')
            return "Failure"

    @staticmethod
    def getArgumentsFromFile():

        script = request.form['Script']
        # print(script)
        try:
            arg_string = ''
            with open('Temp.txt', 'w') as f:
                f.write(script)
            
            with open("Temp.txt", "r") as f:
                for x in f:
                    if (not (x.startswith('#'))):
                        temp = x.replace(' ', '')
                        if (temp.__contains__('defmain')):
                            arg_string = x
                            break
            arg_list = []
            if (len(arg_string) == 0):
                return json_util.dumps(arg_list)
            # a=arg_string.index('{')
            # b=arg_string.index('}')

            sub = arg_string[arg_string.index('(') + 1:arg_string.index(')')]
            arg_list = sub.replace(" ","").split(',')

            try:
                arg_list.remove('auto_resolution=False')
            except:
                pass
            try:
                arg_list.remove('auto_resolution=True')
            except:
                pass

            f.close()
            if (os.path.exists('Temp.py')):
                os.remove('Temp.py')
            if (os.path.exists('Temp.txt')):
                os.remove('Temp.txt')
            return json_util.dumps(arg_list)

        except Exception as e:
            if (os.path.exists('Temp.py')):
                os.remove('Temp.py')
            if (os.path.exists('Temp.txt')):
                os.remove('Temp.txt')
            res = json_util.dumps('Failure' + '\n' + 'Arguments are not declared or used properly' + '\n' + str(e))

        return res

    @staticmethod
    def compileCode():
        script = request.form['Script']
        args = request.form['Args']
        
        #args = json.loads(args)
        print(f'args...{args}')
        args=ast.literal_eval(args)
        print('loads...',args," ",type(args))
        for k,v in args.items():
            v=v.replace("'","\"")
            try:
                # v=json.loads(v)
                v=ast.literal_eval(v)
            except:
                pass
            args[k]=v
        print("args123........",args," ",type(args))
        try:
            with open('Temp.txt', 'w') as f:
                f.write(script)

            with open("Temp.txt") as f:
                s = f.read()
            if args:
                text = "main("
                for key, value in args.items():
                    #if (str(type(value)).__contains__('str')):
                    if 'str' in str(type(value)):
                        text = text + "'" + value + "',"
                    else:
                        text = text + str(value) + ','
                text = text[:-1] + ')'
            with open('Temp.py', 'w') as f: 
                f.write(s)
            
            with open('Temp.py', 'a') as f:
                f.write('\n' + text)

            return_text = ''
            cmd_to_execute = 'python Temp.py'
            sub = subprocess.Popen(cmd_to_execute, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, universal_newlines=True, shell=True)
            sub_out, sub_err = sub.communicate()
            sub_err = sub_err.strip()
            return_text = str(sub_out) + str(sub_err)
            return_text = return_text.strip()
            # print(sub_err)
            # print(str(return_text))
            #            os.kill(sub.pid, signal.SIGTERM)
            res = str(return_text)
            print(f'Result: {res}')
        #            sys.path.append('D:\INTENT\Akhil\intent-python\intent-python')
        #            import Temp
        #            res="Success"
        except Exception as e:
            res = str(e) + 'Failure'

        if (os.path.exists('Temp.py')):
            os.remove('Temp.py')
        if (os.path.exists('Temp.txt')):
            os.remove('Temp.txt')
        return res

    @staticmethod
    def SaveCode():
        arg_list_from_fe = []
        script = request.form['Script']
        name = request.form['Name']
        name = name.split('.py')
        name = name[0]
        script_type = request.form['Type']
        argments_from_fe = request.form['Arguments']
        arg_list_from_fe = argments_from_fe.split(",")
        arg_list_from_fe = [x.strip() for x in arg_list_from_fe]
        print('arg_list_from_fe...', arg_list_from_fe)
        print('argments_from_fe...', argments_from_fe)

        valid_datatypes=['str', 'int', 'float', 'list', 'tuple', 'range', 'dict', 'set', 'bool', 'bytes', 'bytearray']
        for arg in arg_list_from_fe:
            if arg not in valid_datatypes:
                return('Error: Kindly enter valid datatypes')
        try:
            iops_home_path = MongoDBPersistence.assign_enable_tbl.find_one({}, {'iOpsPath': 1, '_id': 0})
            if (script_type == 'main'):
                mypath = 'scripts'
                Resolution.check_path(mypath)

                with open(mypath + '\\' + name + '.py', 'w') as f:
                    script_list = script.split('\n')
                    f.writelines(script_list)
                # file.write(script)
                arg_list = Resolution.getArgumentsFromFile()
                print('arg_list..........', arg_list)
                arg_list = json.loads(arg_list)
                arg_list = [x.strip() for x in arg_list]
                print('arg_list..........', arg_list)

                print('len of arg_list...', len(arg_list))
                print('len of arg_list_from_fe...', len(arg_list_from_fe))
                
                #Checking length of arguments and datatype.
                if len(arg_list) != len(arg_list_from_fe):
                    return('Error: The number of arguments and datatypes provided do not match.')
                
                res_args = {key: value for key, value in zip(arg_list, arg_list_from_fe)}
                print('res_args...', res_args)
                dbDict = {}
                dbDict['scriptName'] = name + '.py'
                dbDict['arguments'] = res_args
                # content=json.loads(script)
                checkEntry = MongoDBPersistence.script_configuration_tbl.find_one({'scriptName': dbDict['scriptName']})
                print('checkEntry')
                if checkEntry:
                    MongoDBPersistence.script_configuration_tbl.update_one({'scriptName': dbDict['scriptName']},
                                                                           {'$set': {'arguments': dbDict['arguments']}})
                else:
                    dbDict['keyword'] = []
                    MongoDBPersistence.script_configuration_tbl.insert_one(dbDict)
            else:
                mypath = 'scripts\\diagnostic-scripts\\'
                Resolution.check_path(mypath)
                with open(mypath + '\\' + name + '.py', 'w') as f:
                    script_list = script.split('\n')
                    f.writelines(script_list)
                # file.write(script)
                arg_list = Resolution.getArgumentsFromFile()
                print('arg_list..........', arg_list)
                arg_list = json.loads(arg_list)
                print('len of arg_list...', len(arg_list))
                print('len of arg_list_from_fe...', len(arg_list_from_fe))

                #Checking length of arguments and datatypes
                if len(arg_list) != len(arg_list_from_fe):
                    return('Error: The number of arguments and datatypes provided do not match.')
                
                res_args = {key: value for key, value in zip(arg_list, arg_list_from_fe)}
                print('res_args...', res_args)
                dbDict = {}
                dbDict['scriptName'] = name + '.py'
                dbDict['arguments'] = res_args
                # content=json.loads(script)
                checkEntry = MongoDBPersistence.diagnostic_tbl.find_one({'scriptName': dbDict['scriptName']})
                print('checkEntry')
                if checkEntry:
                    MongoDBPersistence.diagnostic_tbl.update_one({'scriptName': dbDict['scriptName']},
                                                                 {'$set': {'arguments': dbDict['arguments']}})
                else:
                    MongoDBPersistence.diagnostic_tbl.insert_one(dbDict)
            # print(mypath)

            res = "Success"
        except Exception as e:
            res = str(e)

        return res

    @staticmethod
    def getScriptContent(name, script_type):

        try:

            if (script_type == 'main'):
                mypath = 'scripts\\'
                Resolution.check_path(mypath)
            else:
                mypath = 'scripts\\diagnostic-scripts\\'
                Resolution.check_path(mypath)
            with open(mypath + name, "r") as f:
                contents = f.read()
            return json_util.dumps(contents)
        except Exception as e:
            logging.error('%s: Error in getScriptContent: %s' % (RestService.timestamp, str(e)))
            print(e)
            #            print('Failure')
            return "Failure"

    @staticmethod
    def SaveResolutionDetails():
        number = request.form['Number']
        desc = request.form['Description']
        resolution_type = request.form['Type']
        name = request.form['Name']
        status = request.form['Status']
        logs = request.form['Logs']
        time = str(datetime.datetime.now()).split('.')
        try:
            MongoDBPersistence.resolution_history_tbl.insert_one(
                {'number': number, 'description': desc, 'resolution_type': resolution_type, 'name': name,
                 'time': time[0], 'logs': logs, 'status': status})
            res = "Success"
        except Exception as e:
            res = str(e)

        return res

    @staticmethod
    def getAuditLogs(incident_no):

        try:

            res = MongoDBPersistence.resolution_history_tbl.find({'number': incident_no}, {'_id': 0})
            return json_util.dumps(res)
        except Exception as e:
            logging.error('%s: Error in getAuditLogs: %s' % (RestService.timestamp, str(e)))
            print(e)
            #            print('Failure')
            return "Failure"

    @staticmethod
    def getResolutionHistory(desc, resolution_type):

        try:

            desc = re.sub('([^\s\w]|_)+', ' ', desc).split()
            with open('data/stopwords.csv', 'r') as readFile:
                reader = csv.reader(readFile)
                list1 = list(reader)
                stopwords_english = list1[0]
                readFile.close()
            contents = MongoDBPersistence.resolution_history_tbl.find(
                {'resolution_type': resolution_type, 'status': 'success'}, {'name': 1, 'description': 1, '_id': 0})
            scripts = MongoDBPersistence.script_configuration_tbl.find({}, {"scriptName": 1, "_id": 0})
            match = MongoDBPersistence.configuration_values_tbl.find_one({}, {"script_match_percent": 1, "_id": 0})
            match = float(match["script_match_percent"]) / 100
            scripts_dict = {}
            scripts_match_list = []
            scripts_list = []

            if (contents):
                for script in contents:
                    ticket_desc = re.sub('([^\s\w]|_)+', ' ', script['description']).split()
                    logging.debug(f"ticket_description: {ticket_desc}")
                    logging.debug(f"desc: {desc}")
                    start_time = datetime.datetime.now()
                    print(f"start_time: {start_time}")
                    match_percent = Resolution.scriptMatch(desc, ticket_desc, stopwords_english)
                    end_time = datetime.datetime.now()
                    print(f"end_time: {end_time}")
                    print(f"match_percent time taken: {end_time-start_time}")
                    logging.debug(f"match_percent: {match_percent}")
                    logging.debug(f"match: {match}")
                    match_percent = float(match_percent)

                    if (match_percent >= match):
                        #                        type_dict[match_percent]=script['resolution_type']
                        if script['name'] not in scripts_dict:

                            scripts_dict[script['name']] = match_percent
                            scripts_match_list.append(match_percent)
                        else:
                            if (scripts_dict[script['name']] < match_percent):
                                scripts_dict[script['name']] = match_percent
                                scripts_match_list.append(match_percent)
                scripts_match_list.sort()
                scripts_match_list.reverse()
                for item in scripts_match_list:
                    scripts_list.append(list(scripts_dict.keys())[list(scripts_dict.values()).index(item)])
                    scripts_dict.pop(list(scripts_dict.keys())[list(scripts_dict.values()).index(item)])
                # print(scripts_dict)
                # print(scripts_match_list)
                scripts_list = list(set(scripts_list))
                added_scripts = []
                for item in scripts:
                    added_scripts.append(item['scriptName'])
                for value in scripts_list:
                    if value not in added_scripts:
                        scripts_list.remove(value)

                scripts_list = scripts_list[0:5]
                # print(scripts_dict)
                # print(scripts_match_list)
                # print(scripts_list)
            else:

                return "No Scripts"

            return json_util.dumps(scripts_list)
        except Exception as e:
            logging.error('%s: Error in getResolutionHistory: %s' % (RestService.timestamp, str(e)))
            print(e)
            #            print('Failure')
            return "Failure"

    @staticmethod
    def getEnvironments():

        try:

            env = MongoDBPersistence.environments_tbl.find({}, {"_id": 0})
            if (env):
                return json_util.dumps(env)
            else:
                return "No Environments"
        except Exception as e:
            logging.error('%s: Error in getEnvironments: %s' % (RestService.timestamp, str(e)))
            print(e)
            #            print('Failure')
            return "Failure"

    @staticmethod
    def SaveEnvironments():
        envs = json.loads(request.form['Environments'])
        # print(envs)
        try:

            for env in envs:
                key = Resolution.callKey()
                slogan = env['password'].encode()
                a = Fernet(key)
                coded_slogan = a.encrypt(slogan)
                MongoDBPersistence.environments_tbl.delete_one({'name': env['environment']})
                MongoDBPersistence.environments_tbl.insert_one(
                    {'name': env['environment'], 'username': env['username'], 'password': coded_slogan})
            res = "Success"
        except Exception as e:
            res = str(e)

        return res

    @staticmethod
    def deleteEnvironments():
        env_names = request.form['Environments'].split(',')
        try:

            for i in env_names:
                #                print(i)
                MongoDBPersistence.environments_tbl.delete_one({'name': i})
            return "Success"
        except Exception as e:
            logging.error('%s: Error: %s' % (RestService.timestamp, str(e)))
            print(e)
            #            print('Failure')
            return "Failure"

    @staticmethod
    def ping():
        env = json.loads(request.form['Environments'])
        try:

            return_text = ''
            cmd_to_execute = 'cmd.exe /c echo y | plink.exe ' + env['username'] + '@' + env['environment'] + ' -pw ' + \
                             env['password']
            sub = subprocess.Popen(cmd_to_execute, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, universal_newlines=True, shell=True)
            sub_out, sub_err = sub.communicate()
            sub_err = sub_err.strip()
            # if sub_err and "No files found" not in sub_err:
            #     print('Popen failed: '+str(sub_err),'ERROR')
            return_text = str(sub_out) + str(sub_err)
            return_text = return_text.strip()
            # print(str(return_text))
            return str(return_text)
        except Exception as e:
            print(str(e))
            logging.error(str(e) + "Access denied")
            return str(e) + "Access denied"

    @staticmethod
    def getPossibleResolutions(number: str = None, desc: str = None, tags:list=[] ):

        logging.info("inside getPossibleResolutionsossible ")
        try:
            #desc = re.sub('([^\s\w]|_)+', ' ', desc).split()
            with open('data/stopwords.csv', 'r') as readFile:
                reader = csv.reader(readFile)
                list1 = list(reader)
                stopwords_english = list1[0]
                readFile.close()
            contents = MongoDBPersistence.resolution_history_tbl.find(
                {'number': {'$ne': number}, 'logs': {'$regex': '^((?!running diagnostic script).)*$', '$options': 'i'}},
                {'_id': 0})
            scripts = MongoDBPersistence.script_configuration_tbl.find({}, {"scriptName": 1, 'keyword': 1, "_id": 0})
            # --fetching workflow--
            workflow_lst = list(MongoDBPersistence.workflow_tbl.find({}, {'_id': 0}))
            RPA_lst = MongoDBPersistence.rpa_configuration_tbl.find({}, {"scriptName": 1, 'keyword': 1, "_id": 0})
            match = MongoDBPersistence.configuration_values_tbl.find_one({}, {"script_match_percent": 1, "_id": 0})
            match = float(match["script_match_percent"])
            scripts_match_list = {}
            rpa_match_list = {}
            # print(contents)
            # print(scripts)
            logging.info("inside possible resolutions..2...")
            res_list = []
            scripts_list = []
            if (contents and scripts):
                for script in scripts:
                    scripts_dict = {}
                    logging.debug(f"script['keyword']: {script['keyword']}")
                    logging.debug(f"desc: {desc}")
                    start_time = datetime.datetime.now()
                    logging.info(f"start_time: {start_time}")
                    match_percent = Resolution.scriptMatch(desc, script['keyword'], stopwords_english)
                    end_time = datetime.datetime.now()
                    logging.info(f"end_time: {end_time}")
                    logging.info(f"time_taken: {end_time-start_time}")
                    logging.debug(f"match_percent: {match_percent}")
                    match_percent = float(match_percent)
                    temp = []
                    match_tags = []
                    flag = False
                    for key in script['keyword']:
                        # print(script)               
                        key = key.lower()
                        temp.append(key)
                    for tag in tags:
                        t = tag[1:]
                        t = t.lower()
                        if t in temp:
                            flag = True
                            match_tags.append(tag)
                    logging.debug(f"match: {match}")
                    logging.debug(f"match_percent: {match_percent}")
                    if (match_percent >= match):

                        if script['scriptName'] not in scripts_list:

                            scripts_list.append(script['scriptName'])
                            scripts_dict['name'] = script['scriptName']
                            scripts_dict['score'] = float("{0:.2f}".format(match_percent))
                            scripts_dict['source'] = 'Mapped'
                            scripts_dict['type'] = 'script'
                            scripts_dict['incident_no'] = 'Nil'
                            print("inside possible resolutions..2.1..")
                            scripts_dict['description'] = script['keyword']
                            print("inside possible resolutions..2.2..")
                            # print(scripts_dict)
                            res_list.append(scripts_dict)
                            scripts_match_list[script['scriptName']] = float("{0:.2f}".format(match_percent))
                        else:
                            if (scripts_match_list[script['scriptName']] < match_percent):
                                #                                type_dict[script['scriptName']]='script'
                                #                                scripts_dict[script['scriptName']]=match_percent
                                for i in res_list:
                                    if (i['name'] == script['scriptName']):
                                        res_list.remove(i)
                                scripts_dict['name'] = script['scriptName']
                                scripts_dict['score'] = float("{0:.2f}".format(match_percent))
                                scripts_dict['source'] = 'Mapped'
                                scripts_dict['type'] = 'script'
                                scripts_dict['incident_no'] = 'Nil'
                                print("inside possible resolutions..2.3..")
                                scripts_dict['description'] = script['keyword']
                                print("inside possible resolutions..2.4..")
                                # print(scripts_dict)
                                res_list.append(scripts_dict)
                                scripts_match_list[script['scriptName']] = float("{0:.2f}".format(match_percent))

                    elif (flag == True):
                        # print(scripts_list)
                        if script['scriptName'] not in scripts_list:
                            #                            type_dict[script['scriptName']]='script'
                            #                            scripts_dict[script['scriptName']]=match_percent
                            scripts_list.append(script['scriptName'])
                            scripts_dict['name'] = script['scriptName']
                            scripts_dict['score'] = 0
                            scripts_dict['source'] = 'Tagging'
                            scripts_dict['type'] = 'script'
                            scripts_dict['incident_no'] = 'Nil'
                            print("inside possible resolutions..2.5..")
                            scripts_dict['description'] = match_tags
                            print("inside possible resolutions..2.6..")
                            # print(scripts_dict)
                            res_list.append(scripts_dict)
                            scripts_match_list[script['scriptName']] = 0
                if (not res_list):
                    logging.warn('Could not find out any script which is having match percent > %s' % str(match))
                for content in contents:
                    scripts_dict = {}
                    ticket_desc = re.sub('([^\s\w]|_)+', ' ', content['description']).split()
                    match_percent = Resolution.scriptMatch(desc, ticket_desc, stopwords_english)
                    match_percent = float(match_percent)
                    print(content['name'] + ' ' + str(match_percent))
                    if (match_percent >= match):
                        #                        type_dict[match_percent]=content['resolution_type']
                        if content['name'] not in scripts_list:
                            #                            type_dict[content['name']]=content['resolution_type']
                            #                            scripts_dict[content['name']]=match_percent
                            scripts_list.append(content['name'])
                            scripts_dict['name'] = content['name']
                            scripts_dict['score'] = float("{0:.2f}".format(match_percent))
                            scripts_dict['source'] = 'Historical'
                            scripts_dict['type'] = content['resolution_type']
                            scripts_dict['incident_no'] = content['number']
                            print("inside possible resolutions..2.7..")
                            scripts_dict['description'] = content['description']
                            print("inside possible resolutions..2.8..")
                            # print(scripts_dict)
                            res_list.append(scripts_dict)
                            scripts_match_list[content['name']] = float("{0:.2f}".format(match_percent))
                        else:
                            if (scripts_match_list[content['name']] < match_percent):
                                #                                type_dict[content['name']]=content['resolution_type']
                                #                                scripts_dict[content['name']]=match_percent
                                for i in res_list:
                                    if (i['name'] == content['name']):
                                        res_list.remove(i)
                                scripts_dict['name'] = content['name']
                                scripts_dict['score'] = float("{0:.2f}".format(match_percent))
                                scripts_dict['source'] = 'Historical'
                                scripts_dict['type'] = content['resolution_type']
                                scripts_dict['incident_no'] = content['number']
                                print("inside possible resolutions..2.9..")
                                scripts_dict['description'] = content['description']
                                print("inside possible resolutions..2.10.")
                                # print(scripts_dict)
                                res_list.append(scripts_dict)
                                scripts_match_list[script['scriptName']] = float("{0:.2f}".format(match_percent))
            #                print(scripts_dict)
            #                print(scripts_match_list)
            #                print(type_dict)

            #                scripts_match_list.sort()
            #                scripts_match_list.reverse()
            #                for item in scripts_match_list:
            #                    for res in res_list:
            #                        if (item==res['score']):
            #
            #                    script_type_dict[list(scripts_dict.keys())[list(scripts_dict.values()).index(item)]]=type_dict[list(scripts_dict.keys())[list(scripts_dict.values()).index(item)]]
            #                    scripts_dict.pop(list(scripts_dict.keys())[list(scripts_dict.values()).index(item)])

            #                print(scripts_dict)
            #                print(scripts_match_list)
            #                print(script_type_dict)
            else:
                logging.warn('There is no any script or content available in the database')

            rpa_list = []
            if (contents and RPA_lst):
                for rpa in RPA_lst:
                    rpa_dict = {}
                    match_percent = Resolution.scriptMatch(desc, rpa['keyword'], stopwords_english)
                    match_percent = float(match_percent)
                    temp = []
                    match_tags = []
                    flag = False
                    for key in rpa['keyword']:
                        # print(script)               
                        key = key.lower()
                        temp.append(key)
                    for tag in tags:
                        t = tag[1:]
                        t = t.lower()
                        if t in temp:
                            flag = True
                            match_tags.append(tag)
                    # print(flag)
                    #                    print(script['scriptName']+' '+str(match_percent))
                    if (match_percent >= match):
                        #                        type_dict[match_percent]=script['resolution_type']
                        if rpa['scriptName'] not in rpa_list:
                            #                            type_dict[script['scriptName']]='script'
                            #                            scripts_dict[script['scriptName']]=match_percent
                            rpa_list.append(rpa['scriptName'])
                            rpa_dict['name'] = rpa['scriptName']
                            rpa_dict['score'] = float("{0:.2f}".format(match_percent))
                            rpa_dict['source'] = 'Mapped'
                            rpa_dict['type'] = 'RPA'
                            rpa_dict['incident_no'] = number
                            print("inside possible resolutions..2.1..")
                            rpa_dict['description'] = rpa['keyword']
                            print("inside possible resolutions..2.2..")
                            # print(scripts_dict)
                            res_list.append(rpa_dict)
                            rpa_match_list[rpa['scriptName']] = float("{0:.2f}".format(match_percent))
                        else:
                            if (rpa_match_list[rpa['scriptName']] < match_percent):
                                #                                type_dict[script['scriptName']]='script'
                                #                                scripts_dict[script['scriptName']]=match_percent
                                for i in res_list:
                                    if (i['name'] == rpa['scriptName']):
                                        res_list.remove(i)
                                rpa_dict['name'] = rpa['scriptName']
                                rpa_dict['score'] = float("{0:.2f}".format(match_percent))
                                rpa_dict['source'] = 'Mapped'
                                rpa_dict['type'] = 'RPA'
                                rpa_dict['incident_no'] = number
                                print("inside possible resolutions..2.3..")
                                rpa_dict['description'] = rpa['keyword']
                                print("inside possible resolutions..2.4..")
                                # print(scripts_dict)
                                res_list.append(rpa_dict)
                                rpa_match_list[rpa['scriptName']] = float("{0:.2f}".format(match_percent))

                    elif (flag == True):
                        # print(scripts_list)
                        if rpa['scriptName'] not in rpa_list:
                            #                            type_dict[script['scriptName']]='script'
                            #                            scripts_dict[script['scriptName']]=match_percent
                            rpa_list.append(rpa['scriptName'])
                            rpa_dict['name'] = rpa['scriptName']
                            rpa_dict['score'] = 0
                            rpa_dict['source'] = 'Tagging'
                            rpa_dict['type'] = 'RPA'
                            rpa_dict['incident_no'] = number
                            print("inside possible resolutions..2.5..")
                            rpa_dict['description'] = match_tags
                            print("inside possible resolutions..2.6..")
                            # print(scripts_dict)
                            res_list.append(rpa_dict)
                            rpa_match_list[rpa['scriptName']] = 0
                if (not res_list):
                    logging.warn('Could not find out any RPA which is having match percent > %s' % str(match))
                for content in contents:
                    rpa_dict = {}
                    ticket_desc = re.sub('([^\s\w]|_)+', ' ', content['description']).split()
                    match_percent = Resolution.scriptMatch(desc, ticket_desc, stopwords_english)
                    match_percent = float(match_percent)
                    print(content['name'] + ' ' + str(match_percent))
                    if (match_percent >= match):
                        #                        type_dict[match_percent]=content['resolution_type']
                        if content['name'] not in rpa_list:
                            #                            type_dict[content['name']]=content['resolution_type']
                            #                            scripts_dict[content['name']]=match_percent
                            rpa_list.append(content['name'])
                            rpa_dict['name'] = content['name']
                            rpa_dict['score'] = float("{0:.2f}".format(match_percent))
                            rpa_dict['source'] = 'Historical'
                            rpa_dict['type'] = content['resolution_type']
                            rpa_dict['incident_no'] = content['number']
                            print("inside possible resolutions..2.7..")
                            rpa_dict['description'] = content['description']
                            print("inside possible resolutions..2.8..")
                            # print(scripts_dict)
                            res_list.append(rpa_dict)
                            rpa_match_list[content['name']] = float("{0:.2f}".format(match_percent))
                        else:
                            if (rpa_match_list[content['name']] < match_percent):
                                #                                type_dict[content['name']]=content['resolution_type']
                                #                                scripts_dict[content['name']]=match_percent
                                for i in res_list:
                                    if (i['name'] == content['name']):
                                        res_list.remove(i)
                                rpa_dict['name'] = content['name']
                                rpa_dict['score'] = float("{0:.2f}".format(match_percent))
                                rpa_dict['source'] = 'Historical'
                                rpa_dict['type'] = content['resolution_type']
                                rpa_dict['incident_no'] = content['number']
                                print("inside possible resolutions..2.9..")
                                rpa_dict['description'] = content['description']
                                print("inside possible resolutions..2.10.")
                                # print(scripts_dict)
                                res_list.append(rpa_dict)
                                rpa_match_list[rpa['scriptName']] = float("{0:.2f}".format(match_percent))
            #                print(scripts_dict)
            #                print(scripts_match_list)
            #                print(type_dict)

            #                scripts_match_list.sort()
            #                scripts_match_list.reverse()
            #                for item in scripts_match_list:
            #                    for res in res_list:
            #                        if (item==res['score']):
            #
            #                    script_type_dict[list(scripts_dict.keys())[list(scripts_dict.values()).index(item)]]=type_dict[list(scripts_dict.keys())[list(scripts_dict.values()).index(item)]]
            #                    scripts_dict.pop(list(scripts_dict.keys())[list(scripts_dict.values()).index(item)])

            #                print(scripts_dict)
            #                print(scripts_match_list)
            #                print(script_type_dict)
            else:
                logging.warn('There is no any RPA or content available in the database')
            if (workflow_lst):
                print("inside possible resolutions..3...")
                for workflow in workflow_lst:
                    wrkflow_dict = {}
                    match_percent = 0
                    if ('keyword_mapping' in workflow.keys()):
                        keywords_lst = workflow['keyword_mapping'].split(',')
                        match_percent = float(Resolution.scriptMatch(desc, keywords_lst, stopwords_english))
                        # match_percent=float(match_percent)

                    flag = False
                    for key in keywords_lst:
                        # print(script)               
                        key = key.lower()
                        temp.append(key)
                    for tag in tags:
                        t = tag[1:]
                        t = t.lower()
                        if t in temp:
                            flag = True
                            match_tags.append(tag)
                    # print('------------------------------',match_percent,' >= ',match,', flag : ',flag)
                    if (workflow['workflow_name'] == 'IIA_user_access'):
                        user_mailid = ''
                        predict_ticket = MongoDBPersistence.predicted_tickets_tbl.find_one({'number': number},
                                                                                           {'_id': 0,
                                                                                            'NamedEntities': 1,
                                                                                            'description': 1})
                        if (predict_ticket):
                            for entities in predict_ticket['NamedEntities']:
                                if entities['Entity'] == 'EMAIL':
                                    user_mailid = entities.Value[0]
                        if (user_mailid == ''):
                            continue
                    print("inside possible resolutions..4...")
                    logging.info("inside possible resolutions..4...")
                    if (match_percent >= match):
                        print("inside possible resolutions..4.1...")
                        wrkflow_dict['name'] = workflow['workflow_name']
                        wrkflow_dict['score'] = 0
                        wrkflow_dict['source'] = 'Mapped'
                        wrkflow_dict['type'] = 'orchestrator'
                        wrkflow_dict['incident_no'] = 'Nil'
                        wrkflow_dict['description'] = workflow['keyword_mapping']
                        print("inside possible resolutions..5...")
                        if 'input_params_list' in workflow.keys():
                            wrkflow_dict['input_params_list'] = workflow['input_params_list']
                        # print(wrkflow_dict)
                        res_list.append(wrkflow_dict)
                    elif (flag):
                        print("inside possible resolutions..6.1...")
                        wrkflow_dict['name'] = workflow['workflow_name']
                        wrkflow_dict['score'] = 0
                        wrkflow_dict['source'] = 'Tagging'
                        wrkflow_dict['type'] = 'orchestrator'
                        wrkflow_dict['incident_no'] = 'Nil'
                        wrkflow_dict['description'] = match_tags
                        print("inside possible resolutions..6...")
                        if 'input_params_list' in workflow.keys():
                            wrkflow_dict['input_params_list'] = workflow['input_params_list']
                        # print(wrkflow_dict)
                        res_list.append(wrkflow_dict)
                        # scripts_match_list[script['scriptName']]=0

                # print(res_list)
            else:
                logging.info('There is no any workflow document available in the database!')
                # return "No Scripts"
            res_list.reverse()
            print("inside possible resolutions..before return...", res_list)
            return json_util.dumps(res_list)
        except Exception as e:
            logging.error(f'Error in  getpossibleresolutions:{e}', exc_info=True)
            print("Exception in possible resolutions..", e)
            #            print('Failure')
            return "Failure"

    @staticmethod
    def saveBPMN(name):
        try:

            print("xml")
            xml = request.values.get('xmlData')
            # byte_xml= bytearray(xml, encoding="utf-8")
            MongoDBPersistence.workflow_tbl.update_one({'workflow_name': name},
                                                       {'$set': {'BPMN_Content': xml, 'keyword_mapping': ''}},
                                                       upsert=True)
            return "Success"
        except Exception as e:
            print(e)
            return e

    @staticmethod
    def editBPMN(name):
        try:

            xml = MongoDBPersistence.workflow_tbl.find_one({'workflow_name': name}, {"BPMN_Content": 1, "_id": 0})[
                'BPMN_Content']
            # xml=byte_xml.decode()
            return xml
        except Exception as e:
            logging.error("Inside editBPMN", str(e))
            print(e)
            return e

    @staticmethod
    def saveworkflowkeywords():
        try:

            data = request.get_json()
            for doc in data:
                if ('keyword_mapping' in doc.keys()):
                    MongoDBPersistence.workflow_tbl.update_one({'workflow_name': doc['workflow_name']},
                                                               {'$set': {'keyword_mapping': doc['keyword_mapping']}})
            return "success"
        except Exception as e:
            logging.error('%s: Error inside saveworkflowkeywords: %s' % (RestService.timestamp, str(e)))
        return 'failure'

    @staticmethod
    def saveWorkflow():
        try:

            # xml=request.form['xml']
            # name=request.form['name']
            # proccess_id=request.form['id']
            # print(xml)
            body = request.get_json()
            xml = body['xml']
            name = body['name']
            response = body['response']
            # response={"deployedProcessDefinitions":"test_value"}
            print(response)
            print(type(response))
            root = ET.fromstring(xml)
            configurable_dict = {}
            for movie in root.iter('{http://camunda.org/schema/1.0/bpmn}property'):
                # print(movie.attrib)
                if 'Configurable' in movie.attrib['name'] and movie.attrib['value'] == 'true':
                    # print(movie.attrib['name'].split(' ')[0])
                    configurable_dict[movie.attrib['name'].split(' ')[0]] = ""
            print("configurable_dict:", configurable_dict)
            # key=response['deployedProcessDefinitions']
            # print(type(key))
            # for obj,value in key.items():
            # print(obj)
            #   proccess_id=key[obj]['id']
            proccess_id = response
            if configurable_dict:
                MongoDBPersistence.workflow_tbl.update_one({'workflow_name': name}, {
                    '$set': {'BPMN_Content': xml, 'proccess_id': proccess_id,
                             "input_params_list": [configurable_dict]}}, upsert=True)
            else:
                MongoDBPersistence.workflow_tbl.update_one({'workflow_name': name}, {
                    '$set': {'BPMN_Content': xml, 'proccess_id': proccess_id, "input_params_list": []}}, upsert=True)

            return "success"
        except Exception as e:
            logging.error('%s: Error in saveWorkflow: %s' % (RestService.timestamp, str(e)))
            print(e)
        return 'failure'

    @staticmethod
    def executeWorkFlow(workflow_name, incident_no):
        try:

            config = get_config('ICAS')
            ICAS_url = config['icas_url']

            if 'workflow_parameters' in request.form:
                data = request.form['workflow_parameters']
                args = ast.literal_eval(data)
                print('loads...', args, " ", type(args))
                for k, v in args.items():
                    v = v.replace("'", "\"")
                    try:
                        # v=json.loads(v)
                        v = ast.literal_eval(v)
                    except:
                        pass
                    args[k] = v

                args_db = MongoDBPersistence.workflow_tbl.find_one({"workflow_name": workflow_name},
                                                                   {"_id": 0, "input_params_list": 1})

            else:
                data = ""
                print("data is empty ")

            time = str(datetime.datetime.now()).split('.')
            if data:
                # execute workflow with parameters
                print("executeWorkFlow work flow", workflow_name)

                processId = MongoDBPersistence.workflow_tbl.find_one({'workflow_name': workflow_name},
                                                                     {'workflow_id': 1, '_id': 0})['workflow_id']
                print(f"process id: {processId}")
                URL = f"{ICAS_url}/api/automation-work-flow-testing/WorkFlow/{processId}"
                headers = {'Content-Type': 'application/json'}
                print("before the request...")
                resp = requests.post(URL, data=json.dumps(args), headers=headers, verify=False, timeout=120)
                print("response", resp)
                if resp.status_code == 200:
                    print("inside status 200")
                    id_dict = resp.text
                    print(id_dict)
                    print("executeWorkFlow work flow end:", workflow_name)
                    return json_util.dumps(id_dict)
                else:
                    return json_util.dumps('failure')

            else:
                # execute workflow without parameters
                print("executeWorkFlow work flow inside else", workflow_name)
                processId = MongoDBPersistence.workflow_tbl.find_one({'workflow_name': workflow_name},
                                                                     {'workflow_id': 1, '_id': 0})['workflow_id']
                URL = f"{ICAS_url}/api/automation-work-flow-testing/WorkFlow/{processId}"
                headers = {'Content-Type': 'application/json'}
                resp = requests.post(URL, data=json.dumps({}), headers=headers, verify=False, timeout=120)
                if resp.status_code == 200:
                    # id_dict = eval(resp.text)
                    print(f"response : {resp.text}")
                    print("executeWorkFlow work flow end:", workflow_name)
                    return json_util.dumps("success")
                else:
                    print("Failed to run workflow")
                    return json_util.dumps('failure')

        except Exception as e:
            print("executeWorkFlow work flow Exception block", str(e))
            logging.error('%s: Error: %s' % (RestService.timestamp, str(e)))
        return json_util.dumps('failure')

    @staticmethod
    def assignmentmodule():
        try:

            data = json_util.dumps({})
            assignment = MongoDBPersistence.datasets_tbl.find_one({})['ColumnNames']
            return json_util.dumps(assignment)
        except Exception as e:
            logging.error('%s: Error in assignmentmodule: %s' % (RestService.timestamp, str(e)))
        return json_util.dumps('failure')

    @staticmethod
    def saveColName(column_name):
        try:

            MongoDBPersistence.assign_enable_tbl.update_one({}, {
                '$set': {'assignment_logic_dependancy_field': column_name}}, upsert=True)
            return 'success'
        except Exception as e:
            logging.error('%s: Error in saveColName: %s' % (RestService.timestamp, str(e)))
            print(e)
        return 'failure'

    @staticmethod
    def incident_entity(customer_id, ticket_number):
        # print("Inside Incident entity method ")
        inci_data = MongoDBPersistence.rt_tickets_tbl.find_one({'number': ticket_number}, {"_id": 0, "description": 1})
        all_doc = list(MongoDBPersistence.annotation_mapping_tbl.find({}, {'_id': 0}))
        # final_json={}
        json_data = {}
        final_json = []
        try:

            inci_data = MongoDBPersistence.rt_tickets_tbl.find_one({"number": ticket_number},
                                                                   {"_id": 0, "description": 1})
            all_doc = list(MongoDBPersistence.ticket_annotation_tbl.find({"number": ticket_number},
                                                                         {'_id': 0, "AnnotatedTags": 1}))
            json_data = {}
            final_json = []

            desc = inci_data["description"]
            word_list = desc.split(' ')
            for word in word_list:
                json_data = {}
                word = re.sub(r'\n|\t', '', word)
                word = word.strip('.:,*-)(!')  # -- Include all possible special characters here --
                if word != '':
                    json_data[word] = 'O'
                    if (len(all_doc) > 0):
                        for doc in all_doc[0]['AnnotatedTags']["TagDetails"]:
                            if (word in doc['values']):
                                json_data[word] = doc['TagName']
                                break
                final_json.append(json_data)
            data = json_util.dumps(final_json, sort_keys=False)

            # final_result = [{"msg":"success","Tags": data}]
            final_result = [{"Tags": data}]

            return data
        except Exception as e:
            print(e)
            logging.error('Could not remove Tag name! Error : %s' % str(e))
        return 'failure'

        # if(len(inci_data['description']) == len(inci_data['entity'])):
        #     logging.info("error throw here ")

        # for i in range(len(inci_data['entity'])):
        # tmp_tokens = inci_data['description'].split(" ")
        # tmp_entity = inci_data['entity']
        # tmp_ent=''
        # tmp_str=''

        # for word in tmp_tokens:
        #     json_data = {}
        #     json_data[word] = 'O'
        #     final_json.append(json_data)
        # for j ,k in zip(tmp_tokens,tmp_entity):
        #     json_data = {}
        #     json_data[j] = k
        #     final_json.append(json_data)

        #     data=json_util.dumps(final_json,sort_keys=False)
        #     return data 
        # except Exception as e:
        #     logging.error('Could not return entity data! Error : %s'%str(e))
        #     return "failure"

    @staticmethod
    def get_entity_tags(ticket_number):
        # useful_tags=[]
        # print("Inside get tags list")
        # tags = MongoDBPersistence.entity_tags_tbl.find_one({},{"rt_tags":1,"_id":0})["rt_tags"]
        # print("Tags are.....................",tags)
        # all_tags=['B-art','O','I-nat','B-gpe','B-eve','I-eve','I-art','B-tim','I-gpe','I-tim','B-nat']
        # useful_tags = list(set(tags) - set(all_tags))
        # return json_util.dumps(useful_tags)
        # return json_util.dumps(all_tags)

        # tags = MongoDBPersistence.annotation_mapping_tbl.find({},{"entity":1,"_id":0}).distinct("entity")
        tags = MongoDBPersistence.ticket_annotation_tbl.find({"number": ticket_number},
                                                             {"AnnotatedTags.TagDetails.TagName": 1,
                                                              "_id": 0}).distinct("AnnotatedTags.TagDetails.TagName")
        # tags = MongoDBPersistence.annotation_mapping_tbl.find({},{"entity":1,"_id":0}).distinct("entity")

        # all_tags=['B-art','O','I-nat','B-gpe','B-eve','I-eve','I-art','B-tim','I-gpe','I-tim','B-nat']
        # print("tags are",tags)
        # updated_tag_list = MongoDBPersistence.ticket_annotation_tbl.find({},{"AnnotatedTags.TagDetails.TagName":1,"_id":0}).distinct("AnnotatedTags.TagDetails.TagName")

        # all_tags = ['SERVER','Email',"Name","Environment","service Name","Application Name",'Region']
        # useful_tags = list(set(tags) - set(all_tags))
        # print("updated tags list=",updated_tag_list)
        # for item in updated_tag_list:
        #     if(item not in tags):
        #         useful_tags.append(item)
        #         print("inside get entity tags",json_util.dumps(list(set(tags))))
        #         return json_util.dumps(list(set(tags)))
        return json_util.dumps(list(set(tags)))
        # print("useful tags are",useful_tags)
        # try:

        #     inci_data =MongoDBPersistence.rt_tickets_tbl.find_one({"number" : ticket_number},{"_id":0,"description":1})
        #     all_doc = list(MongoDBPersistence.ticket_annotation_tbl.find({"number" : ticket_number},{'_id':0,"AnnotatedTags":1}))
        #     json_data = {}
        #     final_json = []

        #     desc=inci_data["description"]
        #     word_list = desc.split(' ')
        #     for word in word_list:
        #         json_data = {}
        #         json_data[word]='O'

        #         for doc in all_doc[0]['AnnotatedTags']["TagDetails"]:

        #             if(word in doc['values']):
        #                 json_data[word]=doc['TagName']
        #                 break
        #         final_json.append(json_data)
        #     data=json_util.dumps(final_json,sort_keys=False)

        #     # final_result = [{"msg":"success","Tags": data}]
        #     final_result = [{"Tags": data}]

        #     return data
        # except Exception as e:
        #     print(e)
        #     logging.error('Could not remove Tag name! Error : %s'%str(e))
        # return 'failure'

    @staticmethod
    def get_annoted_data():
        annoted_doc = {}
        desc_word_lst = []
        resp_lst = []

        logging.info('trying to fetch documents from Named-Entity collection')
        nmd_entity_lst = list(MongoDBPersistence.named_entity_tbl.find({}, {'_id': 0, 'entity': 1, 'description': 1}))
        if (nmd_entity_lst):
            for nmd_entity_doc in nmd_entity_lst:
                count = 0
                desc_word_lst = nmd_entity_doc['description'].split()
                if (len(desc_word_lst) == len(nmd_entity_doc['entity'])):
                    for tag in nmd_entity_doc['entity']:
                        if (tag != 'O' and tag in annoted_doc.keys()):
                            annoted_doc[tag].append(desc_word_lst[count])
                        elif tag != 'O':
                            annoted_doc[tag] = [desc_word_lst[count]]
                        count = count + 1
                else:
                    logging.warn('Document skipped because of mismatch in length! --- ', nmd_entity_doc)
            for key, value in annoted_doc.items():
                resp_lst.append({'tag_name': key, 'values': value})
            return json_util.dumps(resp_lst)
        else:
            logging.warn('Could not get any doc from Named-Entity collection')
        return json_util.dumps('failure')

    @staticmethod
    def save_tag_name(customer_id, dataset_id, tag_name):
        try:

            logging.info('Trying to update new Tag Name to Dataset collection')
            # MongoDBPersistence.entity_tags_tbl.update_one({},{'$addToSet':{'rt_tags':tag_name}})
            entity_found_count = list(MongoDBPersistence.annotation_mapping_tbl.find({"entity": tag_name}, {"_id": 0}))
            if (len(entity_found_count) == 0):
                MongoDBPersistence.annotation_mapping_tbl.update_one({"entity": tag_name},
                                                                     {'$set': {'description': []}}, upsert=True)
                # MongoDBPersistence.ticket_annotation_tbl.update_one({"Tags":tag_name},{'$set': {'description':[]}}, upsert = True)
            return 'success'
        except Exception as e:
            logging.error('Could not save Tag name! Error : %s' % str(e))
        return 'failure'

    @staticmethod
    def annotated_data(ticket_number):
        try:

            entity_data_lst = request.get_json()
            print("annotated words....", entity_data_lst)
            MongoDBPersistence.ticket_annotation_tbl.delete_one({"number": ticket_number})
            for entry in entity_data_lst:
                for key, value in entry.items():
                    if (value != 'O'):
                        key = key.replace('"', '').replace("'", '')
                        print(value, key)

                        MongoDBPersistence.annotation_mapping_tbl.update_one({"entity": value},
                                                                             {'$addToSet': {'description': key}},
                                                                             upsert=True)
                        entity_found_count = list(
                            MongoDBPersistence.ticket_annotation_tbl.find({"number": ticket_number}, {"_id": 0}))
                        entities = []
                        entities.append(key)
                        if (len(entity_found_count) == 0):
                            tag_details = {"TagName": value, "values": entities}
                            MongoDBPersistence.ticket_annotation_tbl.update_one({"number": ticket_number}, {
                                '$addToSet': {"AnnotatedTags.TagDetails": tag_details}}, upsert=True)
                        else:
                            tag_found = list(MongoDBPersistence.ticket_annotation_tbl.find(
                                {"number": ticket_number, "AnnotatedTags.TagDetails.TagName": value}, {"_id": 0}))
                            if (len(tag_found) == 0):
                                tag_details = {"TagName": value, "values": entities}
                                MongoDBPersistence.ticket_annotation_tbl.update_one({"number": ticket_number}, {
                                    '$addToSet': {"AnnotatedTags.TagDetails": tag_details}})

                            MongoDBPersistence.ticket_annotation_tbl.update_one(
                                {"number": ticket_number, "AnnotatedTags.TagDetails.TagName": value},
                                {'$addToSet': {'AnnotatedTags.TagDetails.$.values': key}})

                    elif (value == 'O'):
                        obj = list(MongoDBPersistence.annotation_mapping_tbl.find({"description": key}, {"_id": 0}))
                        for item in obj:
                            # print(item['entity'])
                            MongoDBPersistence.annotation_mapping_tbl.update_one({"entity": item['entity']},
                                                                                 {'$pull': {'description': key}},
                                                                                 upsert=False)

            return 'success'
        except Exception as e:
            print("inside tbl annotate...", e)
            logging.error('Could not update! Error : %s' % str(e))
        return 'failure'

    @staticmethod
    def remove_tag_name(customer_id, dataset_id, ticket_number):
        try:

            tags = request.get_json()
            print(tags, ticket_number)
            logging.info('Trying to remove Tag Name from Dataset collection')
            for item in tags:
                print(item)
                # MongoDBPersistence.ticket_annotation_tbl.delete_one({"number" : "INC0010319","AnnotatedTags.TagDetails.$.TagName":item})
                MongoDBPersistence.ticket_annotation_tbl.update({"number": ticket_number}, {
                    "$pull": {"AnnotatedTags.TagDetails": {"TagName": item}}}, upsert=False, multi=True)

            # updated_list = list(MongoDBPersistence.ticket_annotation_tbl.find({"number" : ticket_number},{"AnnotatedTags.TagDetails.TagName":1,"_id":0}).distinct("AnnotatedTags.TagDetails.TagName"))
            # final_result = []
            # final_result = [{"msg":"success","Tags": updated_list}]
            # print("final return....",final_result)

            inci_data = MongoDBPersistence.rt_tickets_tbl.find_one({"number": ticket_number},
                                                                   {"_id": 0, "description": 1})
            all_doc = list(MongoDBPersistence.ticket_annotation_tbl.find({"number": ticket_number},
                                                                         {'_id': 0, "AnnotatedTags": 1}))
            json_data = {}
            final_json = []

            desc = inci_data["description"]
            word_list = desc.split(' ')
            for word in word_list:
                json_data = {}
                json_data[word] = 'O'

                for doc in all_doc[0]['AnnotatedTags']["TagDetails"]:

                    if (word in doc['values']):
                        json_data[word] = doc['TagName']
                        break
                final_json.append(json_data)
            data = json_util.dumps(final_json, sort_keys=False)

            # final_result = [{"msg":"success","Tags": data}]
            final_result = [{"Tags": data, "msg": "success"}]

            return data

            # return json_util.dumps(final_result)
        except Exception as e:
            print(e)
            logging.error('Could not remove Tag name! Error : %s' % str(e))
        return 'failure'

    @staticmethod
    def clearResolutionLogs(ticketNumber):
        try:

            MongoDBPersistence.resolution_history_tbl.delete_many({"number": ticketNumber})
            return 'success'
        except Exception as e:
            logging.error('%s: Error in clearResolutionLogs: %s' % (RestService.timestamp, str(e)))
            print(e)
        return 'failure'

    @staticmethod
    def botfactoryListenersResponse(process_id):
        try:

            print("inside botfactoryListenersResponse")
            data = request.get_json()
            print("data:", data)
            print("data type:", type(data))
            output = data['output']
            print("output", output)
            state = data['state']
            print("type of state", type(state))
            print("state:", state)
            print("data1:", data)
            print("data1 type:", type(data))
            time = str(datetime.datetime.now()).split('.')
            if data:
                print("process ID", process_id, type(process_id))
                # outputparam = eval(data)
                # MongoDBPersistence.resolution_history_tbl.insert_one({'number':incident_no,'processInstanceID':id_dict['processInstanceID'],'status':"workflow execution started"})
                # MongoDBPersistence.resolution_history_tbl.insert_one({'number':incident_no,'processInstanceID':id_dict['processInstanceID'],'status':"workflow execution started"})
                MongoDBPersistence.resolution_history_tbl.update_one({'processInstanceID': process_id}, {
                    '$set': {'OutputParams': data, 'time': time[0], 'logs': "Workflow Execution Completed"}})
                return 'success'
            else:
                return 'failure'

        except Exception as e:
            logging.error('%s: Error in botfactoryListenersResponse: %s' % (RestService.timestamp, str(e)))
            print(e)
        return 'failure'

    @staticmethod
    def genWriteKey():
        mypath = 'config\\'
        key = Fernet.generate_key()
        with open(mypath + "pass.key", "wb") as key_file:
            key_file.write(key)
        return "success"

    @staticmethod
    def callKey():
        mypath = 'config\\'
        with open(mypath + "pass.key", "rb") as f:
            key = f.read()
        return key
        
    @staticmethod
    def check_path(mypath):
        try:
            if not os.path.exists(mypath):
                os.mkdir(mypath)
        except:
            pass

        # Function to get the XML of bmpn content and parse to get the input arguments
    @staticmethod
    def deployBpmn(name):
        config = get_config('ICAS')
        ICAS_url = config['icas_url']

        print("inside deployBpmn method.......")
        xml = request.values.get('xmlData')
        # print("xml from ICAS",xml)
        file = open('workflow.xml', 'w')
        file.write(xml)
        file.close()

        l = []
        t = {}
        arg_list = []
        arg_list1 = []
        c = 0
        l1 = []
        t1 = {}
        l2 = []
        t2 = {}
        arg_list2 = []
        exculde_types = ['camunda:script', 'camunda:list', 'camunda:map']
        with open('workflow.xml') as xml_file:
            xml_config = xmltodict.parse(xml_file.read())
        try:
            workflowName = xml_config['bpmn2:definitions']['bpmn2:process']['@id']
            print(f"workflowName : {workflowName}")
        except Exception as e:
            print(f'workflowName not found...{str(e)}')
        try:
            for d in xml_config['bpmn2:definitions']['bpmn2:process']['bpmn2:subProcess'][0]:
                if 'bpmn2:task' in d:
                    list_inputParameter = \
                    xml_config['bpmn2:definitions']['bpmn2:process']['bpmn2:subProcess'][0]['bpmn2:task'][
                        'bpmn2:extensionElements']['camunda:inputOutput']['camunda:inputParameter']
                    # print(type(list_inputParameter))
                    if 'list' in str(type(list_inputParameter)):
                        for i in list_inputParameter:
                            for key, val in i.items():
                                if key in exculde_types:
                                    c = c + 1
                            if c == 1:
                                c = 0
                                continue
                            else:
                                if (len(i) != 1):
                                    if i['#text'] == "${" + i['@name'] + "}":
                                        k = i['@name'] + ' Type'
                                        if k not in l1:
                                            l1.append(k)
                    else:
                        i = list_inputParameter
                        for key, val in i.items():
                            if key in exculde_types:
                                c = c + 1
                            if c == 1:
                                c = 0
                                continue
                            else:
                                if (len(i) != 1):
                                    if i['#text'] == "${" + i['@name'] + "}":
                                        k = i['@name'] + ' Type'
                                        if k not in l1:
                                            l1.append(k)

                    list_inputParameterTypes = \
                    xml_config['bpmn2:definitions']['bpmn2:process']['bpmn2:subProcess'][0]['bpmn2:task'][
                        'bpmn2:extensionElements']['camunda:properties']['camunda:property']
                    # print(list_inputParameterTypes)
                    for item in list_inputParameterTypes:
                        # print(item['@name'])
                        if item['@name'] in l1:
                            r = {item['@name'].replace(" Type", ""): item['@value']}
                            # print(r)
                            t1.update(r)
            arg_list1.append(t1)
        except Exception as e:
            print(f'Error while fetching arguments...{str(e)}')
        try:
            for dict_item in xml_config['bpmn2:definitions']['bpmn2:process']['bpmn2:subProcess'][0][
                'bpmn2:serviceTask']:
                # print(len(xml_config['bpmn2:definitions']['bpmn2:process']['bpmn2:subProcess'][0]['bpmn2:serviceTask'])
                if 'dict' in str(type(dict_item)):
                    list_inputParameter = dict_item['bpmn2:extensionElements']['camunda:inputOutput'][
                        'camunda:inputParameter']
                    # print((list_inputParameter))
                    #                     print(c)
                    if 'list' in str(type(list_inputParameter)):
                        for i in list_inputParameter:
                            for key, val in i.items():
                                if key in exculde_types:
                                    c = c + 1
                                    # print(c)
                            if c == 1:
                                c = 0
                                continue
                            else:
                                if (len(i) != 1):
                                    # print(i)
                                    if i['#text'] == "${" + i['@name'] + "}":
                                        k = i['@name'] + ' Type'
                                        if k not in l:
                                            l.append(k)
                    else:
                        i = list_inputParameter
                        for key, val in i.items():
                            if key in exculde_types:
                                c = c + 1
                            if c == 1:
                                c = 0
                                continue
                            else:
                                if (len(i) != 1):
                                    if i['#text'] == "${" + i['@name'] + "}":
                                        k = i['@name'] + ' Type'
                                        if k not in l:
                                            l.append(k)
                    list_inputParameterTypes = dict_item['bpmn2:extensionElements']['camunda:properties'][
                        'camunda:property']
                    for item in list_inputParameterTypes:
                        # print("1")
                        if item['@name'] in l:
                            r = {item['@name'].replace(" Type", ""): item['@value']}
                            t.update(r)

                else:
                    list_inputParameter = \
                    xml_config['bpmn2:definitions']['bpmn2:process']['bpmn2:subProcess'][0]['bpmn2:serviceTask'][
                        'bpmn2:extensionElements']['camunda:inputOutput']['camunda:inputParameter']
                    if 'list' in str(type(list_inputParameter)):
                        for i in list_inputParameter:
                            for key, val in i.items():
                                if key in exculde_types:
                                    c = c + 1
                            if c == 1:
                                c = 0
                                continue
                            else:
                                if (len(i) != 1):
                                    if i['#text'] == "${" + i['@name'] + "}":
                                        k = i['@name'] + ' Type'
                                        if k not in l:
                                            l.append(k)
                    else:
                        i = list_inputParameter
                        for key, val in i.items():
                            if key in exculde_types:
                                c = c + 1
                            if c == 1:
                                c = 0
                                continue
                            else:
                                if (len(i) != 1):
                                    if i['#text'] == "${" + i['@name'] + "}":
                                        k = i['@name'] + ' Type'
                                        if k not in l:
                                            l.append(k)
                    list_inputParameterTypes = \
                    xml_config['bpmn2:definitions']['bpmn2:process']['bpmn2:subProcess'][0]['bpmn2:serviceTask'][
                        'bpmn2:extensionElements']['camunda:properties']['camunda:property']
                    for item in list_inputParameterTypes:
                        if item['@name'] in l:
                            r = {item['@name'].replace(" Type", ""): item['@value']}
                            t.update(r)
            arg_list.append(t)
        except Exception as e:
            print(f'Error while fetching arguments...{str(e)}')

        try:
            for dict_item in xml_config['bpmn2:definitions']['bpmn2:process']['bpmn2:subProcess'][0][
                'bpmn2:callActivity']:
                # print(len(xml_config['bpmn2:definitions']['bpmn2:process']['bpmn2:subProcess'][0]['bpmn2:serviceTask'])
                if 'dict' in str(type(dict_item)):
                    list_inputParameter = dict_item['bpmn2:extensionElements']['camunda:inputOutput'][
                        'camunda:inputParameter']
                    # print((list_inputParameter))
                    #                     print(c)
                    if 'list' in str(type(list_inputParameter)):
                        for i in list_inputParameter:
                            for key, val in i.items():
                                if key in exculde_types:
                                    c = c + 1
                                    # print(c)
                            if c == 1:
                                c = 0
                                continue
                            else:
                                if (len(i) != 1):
                                    # print(i)
                                    if i['#text'] == "${" + i['@name'] + "}":
                                        k = i['@name'] + ' Type'
                                        if k not in l2:
                                            l2.append(k)
                    else:
                        i = list_inputParameter
                        for key, val in i.items():
                            if key in exculde_types:
                                c = c + 1
                            if c == 1:
                                c = 0
                                continue
                            else:
                                if (len(i) != 1):
                                    if i['#text'] == "${" + i['@name'] + "}":
                                        k = i['@name'] + ' Type'
                                        if k not in l2:
                                            l2.append(k)
                    list_inputParameterTypes = dict_item['bpmn2:extensionElements']['camunda:properties'][
                        'camunda:property']
                    for item in list_inputParameterTypes:
                        # print("1")
                        if item['@name'] in l:
                            r = {item['@name'].replace(" Type", ""): item['@value']}
                            t2.update(r)

                else:
                    list_inputParameter = \
                    xml_config['bpmn2:definitions']['bpmn2:process']['bpmn2:subProcess'][0]['bpmn2:callActivity'][
                        'bpmn2:extensionElements']['camunda:inputOutput']['camunda:inputParameter']
                    if 'list' in str(type(list_inputParameter)):
                        for i in list_inputParameter:
                            for key, val in i.items():
                                if key in exculde_types:
                                    c = c + 1
                            if c == 1:
                                c = 0
                                continue
                            else:
                                if (len(i) != 1):
                                    if i['#text'] == "${" + i['@name'] + "}":
                                        k = i['@name'] + ' Type'
                                        if k not in l2:
                                            l2.append(k)
                    else:
                        i = list_inputParameter
                        for key, val in i.items():
                            if key in exculde_types:
                                c = c + 1
                            if c == 1:
                                c = 0
                                continue
                            else:
                                if (len(i) != 1):
                                    if i['#text'] == "${" + i['@name'] + "}":
                                        k = i['@name'] + ' Type'
                                        if k not in l2:
                                            l2.append(k)
                    list_inputParameterTypes = \
                    xml_config['bpmn2:definitions']['bpmn2:process']['bpmn2:subProcess'][0]['bpmn2:callActivity'][
                        'bpmn2:extensionElements']['camunda:properties']['camunda:property']
                    for item in list_inputParameterTypes:
                        if item['@name'] in l2:
                            r = {item['@name'].replace(" Type", ""): item['@value']}
                            t2.update(r)
            arg_list2.append(t2)
        except Exception as e:
            print(f'Error while fetching arguments...{str(e)}')
        s = [{**t1, **t, **t2}]
        try:
            config = get_config('ICAS')
            ICAS_url = config['icas_url']
            wfDetails = requests.get(ICAS_url+'/api/automation-work-flows/byName/' + workflowName)
            print(f"wfDetails : {wfDetails}")
            wfDetails = json.loads(wfDetails.text)
            process_id = wfDetails['id']
            print(f"Args list : {s}")
            if s != [{}]:
                print('inside if condition...')
                MongoDBPersistence.workflow_tbl.update_one({'workflow_name': workflowName},
                                                           {'$set': {'BPMN_Content': xml, 'workflow_id': process_id,
                                                                     'keyword_mapping': '',
                                                                     'input_params_list': s}},
                                                           upsert=True)
            else:
                print('inside else condition...')
                MongoDBPersistence.workflow_tbl.update_one({'workflow_name': workflowName},
                                                           {'$set': {'BPMN_Content': xml, 'workflow_id': process_id,
                                                                     'keyword_mapping': ''},
                                                            '$unset': {'input_params_list': ''}},
                                                           upsert=True)
            if (os.path.exists('workflow.xml')):
                os.remove('workflow.xml')
            return "success"
        except Exception as e:
            logging.error('Error in getting workflow details : {str(e)}')
            return "failure"

    # Function to clone the existing workflow and get the new workflow id by changing the required fields in thwe workflow object
    @staticmethod
    def getWFDetails(name):
        try:
            config = get_config('ICAS')
            ICAS_url = config['icas_url']
            # var1 = 0
            workflow_id = MongoDBPersistence.workflow_tbl.find_one({'workflow_name': name},
                                                                   {"workflow_id": 1, "_id": 0})
            print(workflow_id['workflow_id'])
            print(type(workflow_id['workflow_id']))
            workflowObj = requests.get(
                ICAS_url+"/api/automation-work-flows/" + str(workflow_id['workflow_id']))
            dict1 = json.loads(workflowObj.text)
            tasks_dict = {}
            for key in list(dict1):
                if key == 'workflowUniqueName':
                    previous_workflowUniqueName = dict1['workflowUniqueName']
                    if dict1[key].startswith('IIA_'):
                        print(111)
                        # var1=1
                        dict1['workflowUniqueName'] = dict1['workflowUniqueName'] + '_' + ''.join(
                            random.choices(string.digits, k=8))
                    else:
                        dict1['workflowUniqueName'] = 'IIA_' + dict1['workflowUniqueName'] + '_' + ''.join(
                            random.choices(string.digits, k=8))
                    # dict1['workflowUniqueName']='IIA_'+dict1['workflowUniqueName']+'_'+''.join(random.choices(string.digits, k=8))
                if key == 'id':
                    del dict1[key]
                    print(123)
                # if key == 'workflowUniqueName':
                #     dict1['workflowUniqueName']='IIA_'+dict1['workflowUniqueName']
                if key == 'processDefinitionId':
                    dict1['processDefinitionId'] = dict1['workflowUniqueName']
                if key == 'workflowName':
                    dict1['workflowName'] = dict1['workflowUniqueName']
                if key == 'accessLevel':
                    dict1['accessLevel'] = "public"
                if key == 'createdBy':
                    dict1['createdBy'] = 433
                if key == 'modifiedBy':
                    dict1['modifiedBy'] = 433
                if key == 'portfolioId':
                    dict1['portfolioId'] = 3
                if key == 'projectId':
                    dict1['projectId'] = 3
                if key == 'tasks':
                    if dict1['tasks'] != [{}]:
                        print(345)
                        for key1 in list(dict1['tasks']):
                            for k in list(key1):
                                if k == 'id':
                                    del key1[k]
                                if k == 'taskUniqueName':
                                    task_unique_name_old = key1[k]
                                    key1[k] = key1[k].replace('_', '_IIA_', 1)
                                    task_unique_name_new = key1[k]
                                    tasks_dict[task_unique_name_old] = task_unique_name_new
                                if k == 'inputs':
                                    print(456)
                                    for v in key1[k]:
                                        for v1 in list(v):
                                            if v1 == 'id':
                                                del v[v1]
                                            if v1 == 'parameterUniqueName':
                                                v[v1] = v[v1].replace('_', '_IIA_', 1)
                                if k == 'outputs':
                                    for v in key1[k]:
                                        for v1 in list(v):
                                            if v1 == 'id':
                                                del v[v1]
                                            if v1 == 'parameterUniqueName':
                                                v[v1] = v[v1].replace('_', '_IIA_', 1)
                                if k == 'errors':
                                    for v in key1[k]:
                                        for v1 in list(v):
                                            if v1 == 'id':
                                                del v[v1]
                                            if v1 == 'errorUniqueName':
                                                v[v1] = v[v1].replace('_', '_IIA_', 1)
            # print(f"var1:  {var1}")
            print(dict1)
            print(f"tasks_dict : {tasks_dict}")
            bpmn_content = dict1['bpmnContent']
            base64ToString = base64.b64decode(bpmn_content).decode('utf-8')
            print(f"previous_workflowUniqueName : {previous_workflowUniqueName}")
            print(f"dict1['workflowUniqueName'] : {dict1['workflowUniqueName']}")
            base64ToString = base64ToString.replace(previous_workflowUniqueName, dict1['workflowUniqueName'])
            for k, v in tasks_dict.items():
                base64ToString = base64ToString.replace(k, v)
            stringToBase64 = base64.b64encode(base64ToString.encode('utf-8'))
            updated_bpmnContent = stringToBase64.decode()
            dict1['bpmnContent'] = updated_bpmnContent
            # if var1==0:

            URL = ICAS_url+"/api/automation-work-flows"
            headers = {'Content-Type': 'application/json'}
            resp = requests.post(URL, data=json.dumps(dict1), headers=headers, verify=False)
            # print("inside if block")
            print(resp.text)
            workflow_id = resp.text
            return workflow_id
            # else:
            #     print("inside else block")
            #     return json_util.dumps(workflow_id['workflow_id'])

        except Exception as e:
            logging.info(f"Exception while getting workflow_id...{str(e)}")
            return json_util.dumps(workflow_id['workflow_id'])

    @staticmethod
    def getWFDetails1(name):
        try:
            workflow_id = MongoDBPersistence.workflow_tbl.find_one({'workflow_name': name},
                                                                   {"workflow_id": 1, "_id": 0})
            print(workflow_id['workflow_id'])
            print(type(workflow_id['workflow_id']))
        except Exception as e:
            logging.info(f"Exception while getting workflow_id...{str(e)}")
        return json_util.dumps(workflow_id['workflow_id'])

    # Function to update incident ticket after completing workflow execution
    @staticmethod
    def updateTicketStatus(incident_no):

        try:
            print("inside updateTicketStatus method")
            # Close the ticket in SNOW
            snow_details = MongoDBPersistence.itsm_details_tbl.find_one(
                {'ITSMToolName': 'SNOW'}, {"_id": 0})
            c = pysnow.Client(instance=snow_details['ITSMInstance'],
                              user=snow_details['UserID'],
                              password=snow_details['Password'])

            incident = c.resource(api_path='/table/incident')
            print("inside updateTicketStatus method 111")
            try:
                user_status = \
                MongoDBPersistence.predicted_tickets_tbl.find_one({'number': incident_no}, {'_id': 0})[
                    'user_status']
            except:
                user_status = 'Not Approved'

            update = {'state': 'Resolved',
                      'close_code': 'Resolved by request',
                      'close_notes': 'Auto Resolved By IIA. Resolution by through microbots workflow.'}
            print("inside updateTicketStatus method 123")
            if user_status != 'Approved':
                predicted_ticket = MongoDBPersistence.predicted_tickets_tbl.find_one({'number': incident_no},
                                                                                     {'_id': 0})
                assignment_group = predicted_ticket['predicted_fields'][0]['assignment_group']
                update.update({'assigned_to': predicted_ticket['predicted_assigned_to']})
                update.update({'assignment_group': assignment_group})
                update.update({'user_status': 'Approved'})
                update.update({'work_notes': 'Auto Resolved By IIA. Resolution by through microbots workflow.'})

            print("inside updateTicketStatus method 321")
            updated_record = incident.update(
                query={'number': incident_no}, payload=update)
            MongoDBPersistence.predicted_tickets_tbl.update_one({'number': incident_no},
                                                                {'$set': {'user_status': 'Approved'}},
                                                                upsert=True)
            print("inside updateTicketStatus method 222")
            return {"status": "success"}

        except Exception as e:
            print(f"Exception while updating ITSM: {str(e)}")
            return {"status": "failure"}