__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

import binascii
import configparser
import hashlib
import os
import socket

from bson import json_util
from flask import request
from flask import session

from iia.persistence.mongodbpersistence import MongoDBPersistence
from iia.restservice import RestService
from iia.sso.sso import SSOAuthentication
from iia.utils.log_helper import get_logger, log_setup

logging = get_logger(__name__)
app = RestService.getApp()
app.secret_key = "iia-secret-key"


@app.route('/api/getconfig', methods=['GET', 'POST'])
def getconfig():
    log_setup()

    logging.info(f"User IP Address: {request.remote_addr}")
    logging.info(f"User hostname: {socket.gethostbyaddr(request.remote_addr)}")
    if request.method == 'POST' or request.method == 'GET':
        try:
            session['Access'] = 'getconfig'
            config = configparser.ConfigParser()
            config.read('config/' + "iia.ini")
            sso = config['sso']['sso'].lower()
            resp = [{"Status": "Success", "sso": f"{sso}"}]
            return json_util.dumps(resp)
        except Exception as e:
            resp = [{"Status": "Success", "sso": "false"}]
            return json_util.dumps(resp)
    else:
        resp = [{"Status": "Failure"}]
        return json_util.dumps(resp)


@app.route('/api/validateUser', methods=['GET', 'POST'])
def validateUser():
    log_setup()
    if (request.method == 'POST'):
        try:
            config = configparser.ConfigParser()
            config.read('config/' + "iia.ini")
            logging.info(f"sso: {config['sso']['sso'].lower()}")
            if bool(config['sso']['sso'].lower() == 'true'):
                return SSOAuthentication.login()
        except Exception as e:
            logging.error(e, exc_info=True)
        return UserManagement.validateUser(request.form['User'], request.form['Password'])
    else:
        logging.info("%s Invalid HTTP method" % RestService.timestamp())
        resp = [{"Status": "Failure", "Access": "None"}]
        return json_util.dumps(resp)


@app.route('/auth', methods=['GET', 'POST'])
def authentication():
    try:
        if request.method == 'GET':

            resp = [{"Status": "Failure"}]

            try:
                if session.get('state'):
                    session.pop('state')
                    session.pop('code')

                if session.get('UserId'):
                    session.pop('UserId')
                    session.pop('TeamID')
                    session.pop('Access')

            except Exception as e:
                logging.error(e, exc_info=True)

            session['state'] = request.args['state']
            session['code'] = request.args['code']

            form_params = {
                'state': f"{request.args['state']}",
                'code': f"{request.args['code']}"
            }
            sso_result = json_util.loads(SSOAuthentication.auth(form_params))

            if sso_result[0]['Status'] == 'Success':
                user_status = json_util.loads(
                    UserManagement.validateUser(sso_result[0]['UserId'], password='', sso=True))
                if user_status[0]['Status'] == 'Success':

                    session['Access'] = f"{user_status[0]['Access']}"
                    session["TeamID"] = f"{user_status[0]['TeamID']}"
                    session["UserId"] = f"{sso_result[0]['UserId']}"
                    session["Auth_Status"] = 'Success'
                    resp = [{"Status": "Success"}]

                else:
                    session["Auth_Status"] = 'Failure'
                    resp = json_util.dumps(user_status)
            else:
                session["Auth_Status"] = 'Failure'
                resp = [{"Status": "Failure", "Access": "None"}]
            resp = json_util.dumps(resp)

        else:
            session["Auth_Status"] = 'Failure'
            logging.info("%s Invalid HTTP method" % RestService.timestamp())
            resp = [{"Status": "Failure", "Access": "None"}]
            resp = json_util.dumps(resp)

    except Exception as e:
        logging.error(e)
        logging.info("%s Invalid HTTP method" % RestService.timestamp())
        resp = [{"Status": "Failure", "Access": "None"}]
        resp = json_util.dumps(resp)

    script = "<script type='text/javascript'>" \
             "window.open('','_parent','');" \
             "window.close();" \
             "</script>"

    response_html = f"<html> <h2> Authentication Status </h2> <body> {resp}</body> {script}</html>"

    logging.info(f"response_html : {response_html}")
    return response_html


@app.route('/api/auth', methods=['GET', 'POST'])
def auth():
    try:
        if (request.method == 'POST'):
            try:
                received_state = request.form['State']

                if session.get('Auth_Status'):

                    Auth_Status = session['Auth_Status']

                    if Auth_Status == 'Failure':
                        resp = [{"Status": "Failure"}]

                    elif received_state == session['state']:
                        resp = [{"Status": "Success",
                                 "Access": f"{session['Access']}",
                                 "UserId": f"{session['UserId']}",
                                 "TeamID": f"{session['TeamID']}",
                                 "State": f"{session['state']}"}]
                    else:
                        resp = [{"Status": "Retry"}]
                else:
                    resp = [{"Status": "Retry"}]

                return json_util.dumps(resp)

            except Exception as e:
                logging.info("%s Invalid HTTP method" % RestService.timestamp())
                resp = [{"Status": "Retry", "Access": "None"}]
                return json_util.dumps(resp)
        else:
            logging.info("%s Invalid HTTP method" % RestService.timestamp())
            resp = [{"Status": "Failure", "Access": "None"}]
            return json_util.dumps(resp)
    except Exception as e:
        logging.error(e)
        resp = [{"Status": "Failure", "Access": "None"}]
        return json_util.dumps(resp)


@app.route('/api/resetPassword', methods=['GET', 'PUT'])
def resetPassword():
    if (request.method == 'PUT'):
        return UserManagement.resetPassword()
    else:
        logging.info("%s Invalid HTTP method" % RestService.timestamp())
        resp = [{"Status": "Failure", "Access": "None"}]
        return json_util.dumps(resp)


@app.route('/api/addUser', methods=['GET', 'POST'])
def addUser():
    if (request.method == 'POST'):
        return UserManagement.addUser()
    else:
        logging.info("%s Invalid HTTP method" % RestService.timestamp())
        resp = "Failure"
        return resp


# checking if the user has come to reset for first time or not
@app.route('/api/checkUser', methods=['GET', 'POST'])
def checkUser():
    if (request.method == 'POST'):
        return UserManagement.checkUser()
    else:
        logging.info("%s Invalid HTTP method" % RestService.timestamp())
        resp = [{"Status": "Failure", "Access": "None"}]
        return json_util.dumps(resp)


@app.route('/api/logout', methods=['POST'])
def logout():
    return UserManagement.logout()


@app.route('/api/loginState', methods=['GET'])
def loginState():
    return UserManagement.loginState()


@app.route('/api/getUsers', methods=['GET'])
def getUsers():
    return UserManagement.getUsers()


@app.route('/api/deleteUser/<user_id>', methods=['DELETE'])
def deleteUser(user_id):
    return UserManagement.deleteUser(user_id)


class UserManagement(object):

    def __init__(self):
        pass

    @staticmethod
    def validateUser(username, password='', sso=False):

        user = username
        password = password

        user_details = MongoDBPersistence.users_tbl.find_one({"UserID": user},
                                                             {"_id": 0, "UserID": 1, "Role": 1, 'Password': 1,
                                                              'TeamID': 1})
        if (user_details):
            if bool(sso):
                result = True
                pass
            else:
                result = UserManagement.verifyPassword(user_details['Password'], password)
            if (result):

                logging.info("%sYou are logged in as: %s" % (RestService.timestamp(), user))
                logging.info("%s Creating User Session" % RestService.timestamp())
                session["user"] = user
                session["role"] = user_details['Role']
                logging.info("%s Session Object " % RestService.timestamp())
                resp = [{"Status": "Success", "Access": user_details['Role'], "TeamID": user_details['TeamID']}]
            else:
                logging.info("%s Wrong Password for user" % RestService.timestamp())
                resp = [{"Status": "Failure", "Access": "None"}]
        else:
            logging.info("%s No User with provided User ID exists" % RestService.timestamp())
            resp = [{"Status": "Failure", "Access": "None"}]
        return json_util.dumps(resp)

    @staticmethod
    def hashPassword(password):
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
        pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
        pwdhash = binascii.hexlify(pwdhash)
        return (salt + pwdhash).decode('ascii')

    @staticmethod
    def verifyPassword(stored_password, provided_password):
        logging.info(f"stored_password: {stored_password}")
        logging.info(f"provided_password: {provided_password}")
        salt = stored_password[:64]
        stored_password = stored_password[64:]
        pwdhash = hashlib.pbkdf2_hmac('sha512', provided_password.encode('utf-8'), salt.encode('ascii'), 100000)
        pwdhash = binascii.hexlify(pwdhash).decode('ascii')
        logging.info(f"stored_password: {stored_password}")
        logging.info(f"pwdhash: {pwdhash}")
        return pwdhash == stored_password

    @staticmethod
    def resetPassword():
        user_id = request.form['User']
        user_details = MongoDBPersistence.users_tbl.find_one({"UserID": user_id}, {"_id": 0})
        if (user_details):
            user_pass_details = MongoDBPersistence.users_tbl.find_one(
                {"UserID": user_id, "Password": {"$exists": True}}, {"_id": 0})
            if (user_pass_details):
                old_password = request.form['OldPassword']
                new_password = request.form['NewPassword']
                stored_password = user_details['Password']
                hashed_new_password = UserManagement.hashPassword(new_password)
                match = UserManagement.verifyPassword(stored_password, old_password)
                if (match):
                    MongoDBPersistence.users_tbl.update_one({"UserID": user_id},
                                                            {"$set": {"Password": hashed_new_password}})
                    resp = [{"Status": "Success", "Access": "LoginAgain"}]
                    logging.info("Reset of Password is successful")
                else:
                    logging.info("%s Wrong Password for user" % RestService.timestamp())
                    resp = [{"Status": "Failure", "Access": "None"}]
            else:
                logging.info("%s User Setting Password for first time" % RestService.timestamp())
                new_password = request.form['NewPassword']
                hashed_new_password = UserManagement.hashPassword(new_password)
                MongoDBPersistence.users_tbl.update_one({"UserID": user_id},
                                                        {"$set": {"Password": hashed_new_password}})
                resp = [{"Status": "Success", "Access": "LoginAgain"}]
        else:
            logging.info("%s No User with provided User ID exists" % RestService.timestamp())
            resp = [{"Status": "Failure", "Access": "None"}]
        return json_util.dumps(resp)

    @staticmethod
    def checkUser():
        user_id = request.form['User']
        user_details = MongoDBPersistence.users_tbl.find_one({"UserID": user_id}, {"_id": 0})

        if (user_details):
            user_pass_details = MongoDBPersistence.users_tbl.find_one(
                {"UserID": user_id, "Password": {"$exists": True}}, {"_id": 0})
            if (user_pass_details):
                logging.info("%s User Not Coming for First Time" % RestService.timestamp())
                resp = [{"Status": "Success", "Access": "NormalUser"}]
            else:
                logging.info("%s User Coming for First Time" % RestService.timestamp())
                resp = [{"Status": "Success", "Access": "FirstTimeUser"}]
        else:
            logging.info("%s No User with provided User ID exists" % RestService.timestamp())
            resp = [{"Status": "Failure", "Access": "None"}]
        return json_util.dumps(resp)

    @staticmethod
    def addUser():
        user_id = request.form['UserID']
        user_name = request.form['UserName']
        team_id = request.form['TeamID']
        role = request.form['Role']
        team_id = int(team_id)

        # Do not create duplicate users
        userFlag = False

        check_user_id = list(
            MongoDBPersistence.users_tbl.find({'UserID': user_id}, {'_id': 0, 'TeamID': 1, 'UserID': 1, 'Role': 1}))
        print('Testing User_id : ', check_user_id)

        if len(check_user_id) > 0:
            userFlag = False
            print('User email id is already present')
        else:
            status = MongoDBPersistence.users_tbl.insert_one(
                {"UserID": user_id, "UserName": user_name, "TeamID": team_id, "Role": role})
            print('New email id. User Created Successfully!!!')
            userFlag = True

        if (userFlag):
            logging.info("%s User Added Successfully" % RestService.timestamp())
            resp = "Success"
        else:
            logging.info("%s Some error occured in Inserting new User" % RestService.timestamp())
            resp = "Failure"
        return resp

    @staticmethod
    def logout():
        try:
            config = configparser.ConfigParser()
            config.read('config/' + "iia.ini")
            if bool(config['sso']['sso'].lower() == 'true'):
                logout = SSOAuthentication.logout()
                resp = [{"Status": "logout", "Link": f"{logout}"}]
                return json_util.dumps(resp)

        except Exception as e:
            logging.error(e, exc_info=True)

        if (session.get('user')):
            logging.info("%s Destorying User Session" % RestService.timestamp())
            session.pop('user')
            session.pop('role')
            return "Successfully logged out"
        else:
            logging.info("%s You are not logged in please login" % RestService.timestamp())
            return "No Login Found"

    @staticmethod
    def loginState():

        if (session.get('user')):
            logging.info("%s User login found" % RestService.timestamp())
            return "Logged in"
        else:
            logging.info("%s You are not logged in please login" % RestService.timestamp())
            return "No Login Found"

    @staticmethod
    def getUsers():
        try:

            users_lst = list(MongoDBPersistence.users_tbl.aggregate([{
                '$lookup': {
                    'from': 'TblTeam',
                    'localField': 'TeamID',
                    'foreignField': 'TeamID',
                    'as': 'teamDoc'
                }}, {'$match': {'UserID': {'$ne': 'admin'}}},
                {'$project': {
                    '_id': 0, 'Password': 0, 'teamDoc._id': 0
                }}]))
            if (users_lst):
                for user_doc in users_lst:
                    if len(user_doc['teamDoc']) > 0:
                        user_doc['Team'] = user_doc['teamDoc'][0]['TeamName']
                    else:
                        user_doc['Team'] = ''
                    try:
                        del user_doc['teamDoc']
                        del user_doc['TeamID']
                    except Exception as e:
                        logging.error(e, exc_info=True)
                return json_util.dumps(users_lst)
        except Exception as e:
            logging.error(e, exc_info=True)
            logging.error('Error in getUsers : %s' % str(e))

        return json_util.dumps('failure')

    @staticmethod
    def deleteUser(user_id):

        MongoDBPersistence.users_tbl.delete_one({'UserID': user_id})
        logging.info("User deleted Successfully")
        return 'success'