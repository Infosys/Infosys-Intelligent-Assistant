__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

import ast
import binascii
import hashlib
import json
import os
import random
import string
import time
from os import listdir
from os.path import isfile, join

import requests
from bson import json_util
from cryptography.fernet import Fernet
from flask import request
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client
from zeep import helpers
from zeep.transports import Transport

from iia.persistence.mongodbpersistence import MongoDBPersistence
from iia.restservice import RestService
from iia.utils.config_helper import get_config
from iia.utils.log_helper import get_logger

logging = get_logger(__name__)

app = RestService.getApp()


@app.route("/api/execute_AA_RPA/<process_name>", methods=["GET"])
def execute_AA_RPA(process_name):
    return RPA_Resolution.execute_AA_RPA(process_name)


@app.route("/api/SaveRPA1", methods=["POST"])
def SaveRPA1():
    return RPA_Resolution.SaveRPA1()


@app.route("/api/getRPAFromPath", methods=["GET"])
def getRPAFromPath():
    return RPA_Resolution.getRPAFromPath()


@app.route("/api/getAllRPAConfig1", methods=["GET"])
def getAllRPAConfig1():
    return RPA_Resolution.getAllRPAConfig1()


@app.route("/api/saveRPADetails", methods=["POST"])
def saveRPADetails():
    return RPA_Resolution.saveRPADetails()


@app.route("/api/deleteRPAFile", methods=["POST"])
def deleteRPAFile():
    return RPA_Resolution.deleteRPAFile()


@app.route("/api/getRPAContent/<name>/<script_type>", methods=["GET"])
def getRPAContent(name, script_type):
    return RPA_Resolution.getRPAContent(name, script_type)


@app.route("/api/getRPA_Arguments/<script_type>/<script_name>/<incident_number>", methods=["GET"])
def getRPA_Arguments(script_type, script_name, incident_number):
    return RPA_Resolution.getRPA_Arguments(script_type, script_name, incident_number)


@app.route("/api/invokeRPA1", methods=["POST"])
def invokeRPA1():
    return RPA_Resolution.invokeRPA1()


@app.route("/api/getDiagnosticRPA/<name>", methods=["GET"])
def getDiagnosticRPA(name):
    return RPA_Resolution.getDiagnosticRPA(name)


@app.route("/api/getDiagnosticRPAFromPath", methods=["GET"])
def getDiagnosticRPAFromPath():
    return RPA_Resolution.getDiagnosticRPAFromPath()


class RPA_Resolution(object):
    '''
    classdocs
    '''

    def __init__(self, params):
        '''
        Constructor
        '''

        # Fetching details from FE and calling respective function for the RPA bot.

    @staticmethod
    def invokeRPA1():

        script_name = request.form['ScriptName']
        env = request.form['Environment']
        script_type = request.form['Type']
        args = (request.form['Args'])
        print('FrontEndArgs...', args, " ", type(args))
        # args=json.loads(args)
        args = ast.literal_eval(args)
        print('loads...', args, " ", type(args))
        for k, v in args.items():
            v = v.replace("'", "\"")
            try:
                v = ast.literal_eval(v)
            except:
                pass
            args[k] = v

        print("args........", args, " ", type(args))
        try:
            if (script_type == 'RPA'):
                if ("AutomationAnywhere_" in script_name):
                    logging.info("calling Automation Anywhere Bot...")
                    return RPA_Resolution.execute_AA_RPA(script_name, args, script_type)
                elif ("UIPath_" in script_name):
                    logging.info("calling UiPath Bot...")
                    return RPA_Resolution.execute_UIPath_RPA(script_name, args, script_type)
                elif ("BluePrism_" in script_name):
                    logging.info("calling BluePrism Bot...")
                    return RPA_Resolution.execute_BluePrism_RPA(script_name, args, script_type)
            else:
                print('In Diagnostic block...........')
                if ("AutomationAnywhere_" in script_name):
                    logging.info("calling Automation Anywhere Diagnostic Bot...")
                    return RPA_Resolution.execute_AA_RPA(script_name, args, script_type)
                elif ("UIPath_" in script_name):
                    logging.info("calling UiPath Diagnostic Process...")
                    return RPA_Resolution.execute_UIPath_RPA(script_name, args, script_type)
        except Exception as e:
            logging.error(f'Error in invokeRPA1...{str(e)}')
            return 'Command execution exception: ' + str(e)

    # Function to create dict for value of "key:value" pair to be passed to the AA API.
    @staticmethod
    def createValDict(val):
        try:
            valType = str(type(val))
            if 'str' in valType:
                valType = 'String'
            elif 'int' in valType:
                valType = 'Number'
                val = str(val)
            elif 'list' in valType:
                tempList = []
                valType = 'List'
                for i in val:
                    insideDict = RPA_Resolution.createValDict(i)
                    tempList.append(insideDict)
                val = tempList
            elif 'dict' in valType:
                tempList = []
                valType = 'Dictionary'
                for key, val in val.items():
                    insideDict = {}
                    insideDict['key'] = key
                    insideDict['value'] = RPA_Resolution.createValDict(val)
                    tempList.append(insideDict)
                val = tempList
            elif 'bool' in valType:
                valType = 'Boolean'

            outDict = {}
            outDict['type'] = valType.upper()
            outDict[valType.lower()] = val
            return outDict

        except Exception as e:
            logging.error(f'Error in creating inArguments...{str(e)}')
            return {}

    # Function to execute Automation Anywhere Bot
    @staticmethod
    def execute_AA_RPA(workflow_name, inArguments, script_type):
        try:

            # Fetching req. details for executing the Bot from the config file in DB.
            try:
                if (workflow_name == 'AutomationAnywhere_sendEmail.json'):
                    env = 'vm' #Please enter the actual virtual machine/environment name instead of vm 
                else:
                    env = request.form['Environment']
                envs = MongoDBPersistence.environments_tbl.find_one({'name': env}, {"_id": 0})
                username = envs['username']
                decode = envs['password']
            except Exception as e:
                logging.error(f'EnvironmentNotFound Error...{str(e)}')
                return json_util.dumps('Failure : EnvironmentNotFound')

            # Fetching Key
            try:
                mypath = 'config\\'
                RPA_Resolution.check_path(mypath)
                with open(mypath + "pass.key", "rb") as f:
                    key = f.read()
            except Exception as e:
                logging.error(f'KeyNotFound Error... {str(e)}')
                return json_util.dumps(f'Failure : KeyNotFoundError')

            try:
                b = Fernet(key)
                decoded_slogan = b.decrypt(decode)
                decoded_slogan = decoded_slogan.decode('ascii')
                password = decoded_slogan
            except Exception as e:
                logging.error(f'KeyDecodeError...{str(e)}')
                return json_util.dumps('Failure : KeyDecodeError')

            if (script_type == 'RPA'):
                config_Details = MongoDBPersistence.rpa_configuration_tbl.find_one({'scriptName': workflow_name},
                                                                                   {"_id": 0})
            else:
                config_Details = MongoDBPersistence.rpa_diag_configuration_tbl.find_one({'scriptName': workflow_name},
                                                                                        {"_id": 0})
            botname = config_Details['content']['BotName']
            devicepoolName = config_Details['content']['DevicePoolName']
            controlRoomUrl = config_Details['content']['ControlRoomUrl']

            if inArguments:
                dict1 = {}
                for key, val in inArguments.items():
                    dict1[key] = RPA_Resolution.createValDict(val)
                    if (dict1[key] == {}):
                        return json_util.dumps('Failure : InvalidInputArguments')

            # Authenticating the user and generating the auth_token
            try:
                URL = controlRoomUrl + "/v1/authentication"
                body = {"username": username, "password": password}
                headers = {'Content-Type': 'application/json'}
                r = requests.post(URL, data=json.dumps(body), headers=headers, verify=False).json()
                print(r)
                auth_token = r['token']
                user_Id = r['user']['id']
            except Exception as e:
                logging.error(f'UserAuthenticationError...{str(e)}')
                return json_util.dumps('Failure : UserAuthenticationError')

            # Finding the bot_id for the bot.
            try:
                URL = controlRoomUrl + "/v2/repository/file/list"
                headers = {'Content-Type': 'application/json', 'X-Authorization': auth_token}
                body = {"filter": {
                    "operator": "substring",
                    "value": botname,
                    "field": "name"
                }}
                r = requests.post(URL, data=json.dumps(body), headers=headers, verify=False).json()
                # print(r)
                bot_Id = r['list'][0]['id']
            except Exception as e:
                logging.error(f'BotNotFoundError...{str(e)}')
                return json_util.dumps('Failure : BotNotFoundError')

            # Finding pool_id from the devicepoolName in the config
            # -------pool_id is optional.----------
            try:
                URL = controlRoomUrl + "/v2/devices/pools/list"
                headers = {'X-Authorization': auth_token}
                body = {"filter": {
                    "operator": "substring",
                    "field": "name",
                    "value": devicepoolName
                }}
                r = requests.post(URL, data=json.dumps(body), headers=headers, verify=False).json()
                pool_Id = r['list'][0]['id']
            except Exception as e:
                logging.error(f'DevicePoolNotFoundError...{str(e)}')
                return json_util.dumps('Failure : DevicePoolNotFoundError')

            # Deploying the bot and generating the deployment_id
            try:
                URL = controlRoomUrl + "/v3/automations/deploy"
                headers = {'X-Authorization': auth_token}
                body = {
                    "fileId": bot_Id,
                    "fileName": botname,
                    "botInput": dict1,
                    "rdpEnabled": False,
                    "runAsUserIds": [user_Id],
                    "poolIds": [pool_Id]}
                print(body)
                r_deploy = requests.post(URL, data=json.dumps(body), headers=headers, verify=False).json()
                print(r_deploy)
                deployment_Id = r_deploy['deploymentId']
            except Exception as e:
                logging.error(f'BotDeploymentFailed...{str(e)}')
                return json_util.dumps('Failure : BotDeploymentFailed')

            # Waiting in interval of 1s till 10s to fetch the status from AA Control Room

            counter = 0
            while (counter < 10):
                counter += 1
                time.sleep(1)
                rb = RPA_Resolution.getRPABotStatus(deployment_Id, auth_token, controlRoomUrl)
                if rb['list'] != []:
                    break
            print(rb)

            class BotStatusNotFoundError(Exception):
                pass

            try:
                if rb != []:
                    AA_status = rb['list'][0]['status']
                    AA_msg = rb['list'][0]['message']
                else:
                    raise BotStatusNotFoundError
            except BotStatusNotFoundError:
                logging.error(f'BotStatusNotFoundError...')
                return json_util.dumps('Failure : BotStatusNotFoundError')

            # Waiting in interval of 15s to check if the Bot has been executed
            i = 0
            while AA_status == "QUEUED" or AA_status == "PENDING_EXECUTION" or AA_status == "UPDATE":
                i += 1
                if i <= 1:
                    logging.info("Current status of bot execution: " + AA_status)
                time.sleep(15)
                rb = RPA_Resolution.getRPABotStatus(deployment_Id, auth_token, controlRoomUrl)
                AA_status = rb['list'][0]['status']
                AA_msg = rb['list'][0]['message']
                AA_msg = AA_msg.replace('\n', '')
                AA_Device = rb['list'][0]['deviceName']

                varDict = {}
                if AA_status != "QUEUED" and AA_status != "PENDING_EXECUTION" and AA_status != "UPDATE":
                    logging.info("Bot ended with status: " + AA_status)
                    AA_outVarDict = rb['list'][0]['botOutVariables']['values']

                    for key, val in AA_outVarDict.items():
                        outVarType = val['type'].lower()
                        outVarVal = val[outVarType]
                        varDict[key] = outVarVal

                    break
                if i > 10:
                    break

            finalOutDict = {}

            finalOutDict['Execution_Status'] = AA_status
            finalOutDict['WorkFlow_Name'] = workflow_name
            finalOutDict['Machine'] = AA_Device
            finalOutDict['Output_Variables'] = varDict

            if (AA_status != "COMPLETED"):
                finalOutDict['ErrorMessage'] = AA_msg

            return json_util.dumps(finalOutDict)


        except Exception as e:
            logging.error('%s: Error in execute_AA_RPA...: %s' % (RestService.timestamp, str(e)))
            return json_util.dumps(f'Failure : {str(e)}')

    # Function to get AA Bot status from AA Control Room after deploying
    @staticmethod
    def getRPABotStatus(deployment_Id, auth_token, controlRoomUrl):
        try:
            URL = controlRoomUrl + "/v2/activity/list"
            headers = {'X-Authorization': auth_token}
            body = {"filter": {
                "operator": "eq",
                "field": "deploymentId",
                "value": deployment_Id
            }}
            print(f"body: {body}")
            r = requests.post(URL, data=json.dumps(body), headers=headers, verify=False).json()
            print(f"RPA Bot Status response : {r}")
            return r
        except Exception as e:
            logging.error(f'BotStatusNotFoundError...{str(e)}')

    @staticmethod
    def callKey():
        try:

            mypath = 'config\\'

            return open(mypath + "pass.key", "rb").read()
        except Exception as e:
            logging.error(f'KeyNotFound Error... {str(e)}')
            errorMsg = str(e)
            return json_util.dumps('failure : ' + errorMsg)

    # Fetching RPA Config File from the IIA folder
    @staticmethod
    def getRPAFromPath():
        try:

            mypath = 'scripts\\RPA'
            RPA_Resolution.check_path(mypath)
            onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
            return json_util.dumps(onlyfiles)
        except Exception as e:
            logging.error('%s: Error: %s' % (RestService.timestamp, str(e)))
            logging.info('Error in getRPAFromPath...', str(e))
            return "Failure"

    # Function to save RPA Config File in IIA Folder and DB
    @staticmethod
    def SaveRPA1():
        try:
            script = request.form['Script']
            print(script)
            rpaType = request.form['RpaType']
            print(rpaType)
            name = request.form['Name']
            print(name)
            script_type = request.form['Type']
            name = name.split('.json')
            name = name[0]
            if 'diag_' in name:
                name = name.replace('diag_', '')
            if (name.startswith('AutomationAnywhere_')):
                name = name.replace('AutomationAnywhere_', '')
            elif (name.startswith('UIPath_')):
                name = name.replace('UIPath_', '')
            elif (name.startswith('BluePrism_')):
                name = name.replace('BluePrism_', '')

            # Saving in IIA Folder
            iops_home_path = MongoDBPersistence.assign_enable_tbl.find_one({}, {'iOpsPath': 1, '_id': 0})
            print(iops_home_path)

            if (script_type == 'RPA'):
                mypath = 'scripts\RPA'
                RPA_Resolution.check_path(mypath)
                with open(mypath + '\\' + rpaType + '_' + name + '.json', 'w') as f:
                    script_list = script.split('\n')
                    f.writelines(script_list)

                # Saving in DB
                dbDict = {}
                dbDict['scriptName'] = rpaType + '_' + name + '.json'
                content = json.loads(script)
                dbDict['content'] = content
                checkEntry = MongoDBPersistence.rpa_configuration_tbl.find_one({'scriptName': dbDict['scriptName']})
                if checkEntry:
                    MongoDBPersistence.rpa_configuration_tbl.update({'scriptName': dbDict['scriptName']},
                                                                    {'$set': {'content': dbDict['content']}})
                else:
                    dbDict['keyword'] = []
                    MongoDBPersistence.rpa_configuration_tbl.insert_one(dbDict)
            else:
                mypath = 'scripts\diagnostic-RPA'
                RPA_Resolution.check_path(mypath)
                with open(mypath + '\\' + rpaType + '_' + name + '.json', 'w') as f:
                    script_list = script.split('\n')
                    f.writelines(script_list)

                # Saving in DB
                dbDict = {}
                dbDict['scriptName'] = rpaType + '_' + name + '.json'
                content = json.loads(script)
                dbDict['content'] = content
                checkEntry = MongoDBPersistence.rpa_diag_configuration_tbl.find_one(
                    {'scriptName': dbDict['scriptName']})
                if checkEntry:
                    MongoDBPersistence.rpa_diag_configuration_tbl.update({'scriptName': dbDict['scriptName']},
                                                                         {'$set': {'content': dbDict['content']}})
                else:
                    dbDict['keyword'] = []
                    MongoDBPersistence.rpa_diag_configuration_tbl.insert_one(dbDict)

            res = "Success"
        except Exception as e:
            res = str(e)
            logging.info('Error in SaveRPA1...', res)
        return res

    # Fetch ALL RPA Config Files from DB
    @staticmethod
    def getAllRPAConfig1():
        try:
            scripts = MongoDBPersistence.rpa_configuration_tbl.find({}, {"_id": 0})
            print('...................', scripts)
            if (scripts):
                return json_util.dumps(scripts)
            else:
                return "No Scripts"

        except Exception as e:
            logging.error('%s: Error: %s' % (RestService.timestamp, str(e)))
            logging.info('Error in getAllRPAConfig1...', str(e))
            return "Failure json is inavalid"

    # Function to save keywords and config details for bot in DB
    @staticmethod
    def saveRPADetails():
        try:
            scripts = json.loads(request.form['Scripts'])
            print('scripts......', scripts)

            for script in scripts:
                print(script)
                contents1 = RPA_Resolution.getRPAContent(script['scriptName'], 'RPA')
                contents1 = json.loads(contents1)
                contents1 = json.loads(contents1)
                MongoDBPersistence.rpa_configuration_tbl.delete_one({'scriptName': script['scriptName']})
                MongoDBPersistence.rpa_configuration_tbl.insert_one(script)
                MongoDBPersistence.rpa_configuration_tbl.update({'scriptName': script['scriptName']},
                                                                {'$set': {'content': contents1}})

            return "Success"
        except Exception as e:
            logging.error('%s: Error: %s' % (RestService.timestamp, str(e)))
            logging.info('Error in saveRPADetails...', str(e))
            return "Failure"

    # Fetch content of RPA Config File from IIA folder
    @staticmethod
    def getRPAContent(name, script_type):
        try:
            if (script_type == 'RPA'):
                mypath = 'scripts\\RPA\\'
                RPA_Resolution.check_path(mypath)
            else:
                mypath = 'scripts\\diagnostic-RPA\\'
                RPA_Resolution.check_path(mypath)
            with open(mypath + name, "r") as f:
                contents = f.read()
            print('Content>>>', contents)
            return json_util.dumps(contents)
        except Exception as e:
            logging.error('%s: Error: %s' % (RestService.timestamp, str(e)))
            logging.info('Error in getRPAContent...', str(e))

    @staticmethod
    def getDiagnosticRPA(name):

        try:
            scripts = MongoDBPersistence.rpa_configuration_tbl.find_one({'scriptName': name}, {"_id": 0})[
                'diagnostic_script']
            if (scripts):
                return json_util.dumps(scripts)
            else:
                return "No Scripts"
        except Exception as e:
            logging.error('%s: Error: %s' % (RestService.timestamp, str(e)))
            print(e)
            return "Failure"

    @staticmethod
    def getDiagnosticRPAFromPath():

        try:
            mypath = 'scripts\\diagnostic-RPA'
            RPA_Resolution.check_path(mypath)

            onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
            return json_util.dumps(onlyfiles)
        except Exception as e:
            logging.error('%s: Error: %s' % (RestService.timestamp, str(e)))
            print(e)
            return "Failure"

    # Delete RPA Config file from DB
    @staticmethod
    def deleteRPAFile():
        script_names = request.form['Scripts'].split(',')
        try:
            for i in script_names:
                MongoDBPersistence.rpa_configuration_tbl.delete_one({'scriptName': i})
            return "Success"
        except Exception as e:
            logging.error('%s: Error: %s' % (RestService.timestamp, str(e)))
            logging.info('Error in deleteRPAFile...', str(e))
            return "Failure"

    # Fetch input args for the RPA bot from config file in DB
    @staticmethod
    def getRPA_Arguments(script_type, script_name, incident_number):
        try:
            if (script_type == 'RPA'):
                args = \
                MongoDBPersistence.rpa_configuration_tbl.find_one({'scriptName': script_name}, {"_id": 0})['content'][
                    'InArguments']
                incident_number_config = get_config('RPA')
                incident_number_list = incident_number_config['incident_number_column_name']
                incident_number_list = incident_number_list.split(",")
                args_dict_list = list(args.keys())
                for i in args_dict_list:
                    if i in incident_number_list:
                        args[i] = {'type': incident_number}
            else:
                args = MongoDBPersistence.rpa_diag_configuration_tbl.find_one({'scriptName': script_name}, {"_id": 0})[
                    'content']['InArguments']
                incident_number_config = get_config('RPA')
                incident_number_list = incident_number_config['incident_number_column_name']
                incident_number_list = incident_number_list.split(",")
                args_dict_list = list(args.keys())
                for i in args_dict_list:
                    if i in incident_number_list:
                        args[i] = {'type': incident_number}
            return json_util.dumps(args)
        except Exception as e:
            logging.error('%s: Error: %s' % (RestService.timestamp, str(e)))
            logging.info('Error in getRPA_Arguments...', str(e))
            return "Failure"

    @staticmethod
    def execute_UIPath_RPA(script_name, args, script_type):
        try:
            # Fetching req. details for executing the Process from the config file in DB.
            try:
                env = request.form['Environment']
                envs = MongoDBPersistence.environments_tbl.find_one({'name': env}, {"_id": 0})
                username = envs['username']
                decode = envs['password']
            except Exception as e:
                logging.error(f'EnvironmentNotFound Error... {str(e)}')
                return json_util.dumps(f'Failure : EnvironmentNotFound')

            # Fetching Key
            try:
                mypath = 'config\\'
                RPA_Resolution.check_path(mypath)
                with open(mypath + "pass.key", "rb") as f:
                    key = f.read()
            except Exception as e:
                logging.error(f'KeyNotFound Error... {str(e)}')
                return json_util.dumps(f'Failure : KeyNotFoundError')

            try:
                b = Fernet(key)
                decoded_slogan = b.decrypt(decode)
                decoded_slogan = decoded_slogan.decode('ascii')
                password = decoded_slogan
            except Exception as e:
                logging.error(f'KeyDecodeError...{str(e)}')
                return json_util.dumps('Failure : KeyDecodeError')

            if (script_type == 'RPA'):
                config_Details = MongoDBPersistence.rpa_configuration_tbl.find_one({'scriptName': script_name},
                                                                                   {"_id": 0})
            else:
                config_Details = MongoDBPersistence.rpa_diag_configuration_tbl.find_one({'scriptName': script_name},
                                                                                        {"_id": 0})

            processName = config_Details['content']['ProcessName']
            orchestratorUrl = config_Details['content']['OrchestratorUrl']
            tenantName = config_Details['content']['TenantName']

            # Authenticating the user and generating the token
            try:
                URL = orchestratorUrl + "/api/Account/Authenticate"
                body = {"usernameOrEmailAddress": username, "password": password, "tenancyName": tenantName}
                headers = {'Content-Type': 'application/json'}
                r = requests.post(URL, data=json.dumps(body), headers=headers, verify=False).json()
                token = "Bearer " + str(r["result"])
            except Exception as e:
                logging.error(f'UserAuthenticationError...{str(e)}')
                return json_util.dumps('Failure : UserAuthenticationError')

            # Finding the process_Id for the process.
            try:
                URL = f"{orchestratorUrl}/odata/Releases?$filter=ProcessKey+eq%20'{processName}'"
                headers = {"Content-Type": "application/json",
                           "X-UIPATH-TenantName": tenantName,
                           "X-UIPATH-OrganizationUnitId": "1",
                           "Authorization": token}
                r = requests.get(URL, headers=headers, verify=False).json()
                process_Id = r["value"][0]["Key"]
            except Exception as e:
                logging.error(f'ProcessNotFoundError...{str(e)}')
                return json_util.dumps('Failure : ProcessNotFoundError')

            # Deploying the job and generating the job_id
            try:
                URL = f"{orchestratorUrl}/odata/Jobs/UiPath.Server.Configuration.OData.StartJobs"
                headers = {"Content-Type": "application/json",
                           "X-UIPATH-TenantName": tenantName,
                           "X-UIPATH-OrganizationUnitId": "1",
                           "Authorization": token}
                InputArguments = json.dumps(args)
                body = {
                    "startInfo": {
                        "ReleaseKey": process_Id,
                        "Strategy": "All",
                        "InputArguments": InputArguments
                    }
                }
                print(body)
                r_deploy = requests.post(URL, json=body, headers=headers, verify=False).json()
                print(r_deploy)
                job_Id = r_deploy["value"][0]["Id"]

            except Exception as e:
                logging.error(f'JobDeploymentFailed...{str(e)}')
                return json_util.dumps(f'Failure : JobDeploymentFailed {r_deploy["message"]}')

            # Waiting in interval of 1s till 10s to fetch the job status from UiPath orchestrator

            counter = 0
            while (counter < 10):
                counter += 1
                time.sleep(1)
                rb = RPA_Resolution.getUiPathJobStatus(orchestratorUrl, job_Id, token, tenantName)
                if rb['value'] != []:
                    break
            print(rb)

            class JobStatusNotFoundError(Exception):
                pass

            try:
                if rb != []:
                    job_status = rb['value'][0]['State']
                    HostMachineName = rb['value'][0]['HostMachineName']
                    Info = rb['value'][0]['Info']
                else:
                    raise JobStatusNotFoundError
            except JobStatusNotFoundError:
                logging.error(f'JobStatusNotFoundError...')
                return json_util.dumps('Failure : JobStatusNotFoundError')

            # Waiting in interval of 15s to check if the Job has been executed
            i = 0
            uiPath_outVarDict = {}
            if job_status == "Successful":
                uiPath_outVarDict = rb['value'][0]['OutputArguments']
                if (uiPath_outVarDict != None):
                    print('-------------', type(uiPath_outVarDict))
                    uiPath_outVarDict = json.loads(uiPath_outVarDict)
                else:
                    uiPath_outVarDict = {}
            else:

                while job_status != "Successful":
                    i += 1
                    logging.info("Current status of Job execution: " + job_status)
                    time.sleep(5)
                    rb = RPA_Resolution.getUiPathJobStatus(orchestratorUrl, job_Id, token, tenantName)
                    job_status = rb['value'][0]['State']
                    HostMachineName = rb['value'][0]['HostMachineName']
                    Info = rb['value'][0]['Info']

                    if job_status == "Successful" or job_status == "Faulted" or job_status == "Stopped":
                        logging.info("Job ended with status: " + job_status)
                        uiPath_outVarDict = rb['value'][0]['OutputArguments']
                        if (uiPath_outVarDict != None):
                            print('-------------', type(uiPath_outVarDict))
                            uiPath_outVarDict = json.loads(uiPath_outVarDict)
                        else:
                            uiPath_outVarDict = {}
                        break

                    if i > 10:
                        break

            finalOutDict = {}

            finalOutDict['Execution_Status'] = job_status
            finalOutDict['WorkFlow_Name'] = script_name
            finalOutDict['Machine'] = HostMachineName

            if (job_status != "Successful"):
                finalOutDict['ErrorMessage'] = Info
            else:
                finalOutDict['Info'] = Info
                finalOutDict['Output_Variables'] = uiPath_outVarDict 
            return json_util.dumps(finalOutDict)

        except Exception as e:
            logging.error('%s: Error in execute_UiPath_RPA...: %s' % (RestService.timestamp, str(e)))
            return json_util.dumps('Failure')

    # Function to get Job status from UiPath orchestrator after deploying
    @staticmethod
    def getUiPathJobStatus(orchestrator_url, job_Id, token, tenantName):
        try:
            URL = f"{orchestrator_url}/odata/Jobs?$filter=Id+eq%20{job_Id}"
            headers = {"Content-Type": "application/json",
                       "X-UIPATH-TenantName": tenantName,
                       "X-UIPATH-OrganizationUnitId": "1",
                       "Authorization": token}
            process_data = requests.get(URL, headers=headers, verify=False).json()
            return process_data
        except Exception as e:
            logging.error(f'JobStatusNotFoundError...{str(e)}')
            return json_util.dumps('Failure : JobStatusNotFoundError')

    @staticmethod
    def execute_BluePrism_RPA(script_name, args, script_type):
        try:
            # Fetching req. details for executing the Bot from the config file in DB.
            try:
                env = request.form['Environment']
                envs = MongoDBPersistence.environments_tbl.find_one({'name': env}, {"_id": 0})
                username = envs['username']
                decode = envs['password']
            except Exception as e:
                logging.error(f'EnvironmentNotFound Error...{str(e)}')
                return json_util.dumps('Failure : EnvironmentNotFound')

            # Fetching Key
            try:
                mypath = 'config\\'
                RPA_Resolution.check_path(mypath)
                with open(mypath + "pass.key", "rb") as f:
                    key = f.read()
            except Exception as e:
                logging.error(f'KeyNotFound Error... {str(e)}')
                return json_util.dumps(f'Failure : KeyNotFoundError')

            try:
                b = Fernet(key)
                decoded_slogan = b.decrypt(decode)
                decoded_slogan = decoded_slogan.decode('ascii')
                password = decoded_slogan
            except Exception as e:
                logging.error(f'KeyDecodeError...{str(e)}')
                return json_util.dumps('Failure : KeyDecodeError')

            # Fetch config details from DB
            if (script_type == 'RPA'):
                config_Details = MongoDBPersistence.rpa_configuration_tbl.find_one({'scriptName': script_name},
                                                                                   {"_id": 0})
            else:
                config_Details = MongoDBPersistence.rpa_diag_configuration_tbl.find_one({'scriptName': script_name},
                                                                                        {"_id": 0})

            xmlName = config_Details['content']['XmlName']
            serviceName = config_Details['content']['ServiceName']

            # creating BP session
            session = Session()
            session.auth = HTTPBasicAuth(username, password)

            # fetching xml of the required bot
            wsdl = f'scripts\RPA\BP_XML\{xmlName}'

            client = Client(str(wsdl), transport=Transport(session=session))
            service = client.service

            # invoking the Bot
            serviceMethod = getattr(service, serviceName)
            res = serviceMethod(**args)

            res_dict = helpers.serialize_object(res, dict)
            res_json = json_util.dumps(res_dict)
            session.close()
            return res_json

        except Exception as e:
            logging.error(f'Error in executing Blueprism Bot...{str(e)}')
            return json_util.dumps('Failure : BPExecutionError')

    # ====================================================IIA reset password use case=========================================#

    @staticmethod
    def random_pswd_genr():
        characters = list(string.ascii_letters + string.digits + "#$%&")
        length = 8
        random.shuffle(characters)
        password = []

        for i in range(length):
            password.append(random.choice(characters))

        password[-1] = '@'
        random.shuffle(password)
        generated_pswd = "".join(password)
        return (generated_pswd)

    @staticmethod
    def hash_pswd(password):
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
        pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
        pwdhash = binascii.hexlify(pwdhash)
        return (salt + pwdhash).decode('ascii')

    @staticmethod
    def check_path(mypath):
        try:
            if not os.path.exists(mypath):
                os.mkdir(mypath)
        except:
            pass
