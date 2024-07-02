__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

import re
from datetime import datetime
from datetime import timedelta

import pythoncom
import win32com.client as win32

from iia.persistence.mongodbpersistence import MongoDBPersistence
# import logging
from iia.restservice import RestService
from iia.utils.log_helper import get_logger

logging = get_logger(__name__)
app = RestService.getApp()


@app.route("/api/approval_email_send/<incident_no>", methods=["GET"])
def approval_email_send(incident_no):
    return ProvideAccessToIIA.approval_email_send(incident_no)


@app.route("/api/approval_email_receive/<incident_no>", methods=["GET"])
def approval_email_receive(incident_no):
    return ProvideAccessToIIA.approval_email_receive(incident_no)


@app.route("/api/approved_email/<incident_no>", methods=["GET"])
def approved_email(incident_no):
    return ProvideAccessToIIA.approved_email(incident_no)


@app.route("/api/rejected_email/<incident_no>", methods=["GET"])
def rejected_email(incident_no):
    return ProvideAccessToIIA.rejected_email(incident_no)


@app.route("/api/insert_user_dtls/<incident_no>", methods=["GET"])
def insert_user_dtls(incident_no):
    return ProvideAccessToIIA.insert_user_dtls(incident_no)


class ProvideAccessToIIA(object):
    def __init__(self, params):
        '''
        Constructor
        '''

    @staticmethod
    def send_mail(user_mailid, cc_mailid, user, subject, message):
        try:

            logging.info('Trying to send mail to Manager for Approval')
            pythoncom.CoInitialize()
            outlook = win32.Dispatch('outlook.application')
            mail = outlook.CreateItem(0)
            mail.To = user_mailid
            if (cc_mailid):
                mail.CC = user_mailid
            mail.Subject = subject
            mail.Body = 'Hi ' + user + ',\n\n' + message + '\n\nRegards,\nIIA Team'
            mail.Send()
            return 'success'
        except Exception as e:
            logging.error('%s' % str(e))
        return 'failure'

    @staticmethod
    def approval_email_send(incident_no):
        incidentNumber = incident_no

        logging.info('%s: In approval email send method' % RestService.timestamp())
        user_mailid = ''
        wrkflw_tckt_dtls_doc = {}
        wrkflw_tckt_dtls_doc['IncidentNo'] = incidentNumber
        try:
            predict_ticket = MongoDBPersistence.predicted_tickets_tbl.find_one({'number': incidentNumber},
                                                                               {'_id': 0, 'NamedEntities': 1})
           
            if (predict_ticket):
               
                for entities in predict_ticket['NamedEntities']:
                    if entities['Entity'] == 'EMAIL':
                        user_mailid = entities['Value'][0]
                        user = user_mailid.split('@')[0].replace('.', ' ')
                        wrkflw_tckt_dtls_doc['user'] = user

                subject = incidentNumber + ':Approve IIA access request for user ' + user
                message = 'Reply Approved/Rejected. \n' \
                          'FYI : This is a system generated mail please do not replay anything except the mentioned words'
                logging.info('Trying to call send mail method')
                resp = ProvideAccessToIIA.send_mail(user_mailid, user_mailid, '', subject, message)
                if (resp == 'success'):
                    date = datetime.now()
                    
                    wrkflw_tckt_dtls_doc['chckd_mail_till'] = str(date)
                    wrkflw_tckt_dtls_doc['reminder_date'] = str((date + timedelta(days=4)).date()) + ' 00:00:00'
                    wrkflw_tckt_dtls_doc['send_rmndr_state'] = False
                    wrkflw_tckt_dtls_doc['expire_date'] = str((date + timedelta(days=6)).date()) + ' 00:00:00'
                    wrkflw_tckt_dtls_doc['approve_reject_state'] = False
                    wrkflw_tckt_dtls_doc['user_mailid'] = user_mailid
                    logging.info('Trying to insert Workflow Ticket details into workflow_tickets_tbl')
                    MongoDBPersistence.workflow_tickets_tbl.update_one({'IncidentNo': incidentNumber},
                                                                       {'$set': wrkflw_tckt_dtls_doc}, upsert=True)
                else:
                    # --failed to send mail--
                    pass
            return 'success'
        except Exception as e:
            logging.error('%s:%s' % (RestService.timestamp(), str(e)))
        return 'failure'

    @staticmethod
    def approval_email_receive(incident_no):
        try:

            incidentNumber = incident_no
            logging.info('%s: Trying to fetch details from workflow_tickets_tbl' % RestService.timestamp())
            wrkflw_tckt_dtls_doc = MongoDBPersistence.workflow_tickets_tbl.find_one(
                {"IncidentNo": incidentNumber, 'approve_reject_state': False})
            if (wrkflw_tckt_dtls_doc):
                chck_mail_till_time = wrkflw_tckt_dtls_doc['chckd_mail_till']
                user = wrkflw_tckt_dtls_doc['user']
                user_mailid = wrkflw_tckt_dtls_doc['user_mailid']

                pythoncom.CoInitialize()
                outlook = win32.Dispatch("Outlook.Application").GetNamespace("MAPI")
                account = win32.Dispatch("Outlook.Application").Session.Accounts[0]
                logging.info('Trying to read mails from account : %s for ticket : %s' % (account, incidentNumber))
                global inbox
                inbox = outlook.Folders(account.DeliveryStore.DisplayName)
                folders = inbox.Folders

                for folder in folders:
                    if (str(folder) == 'Inbox'):
                        messages = folder.Items  # --fetching mails from Inbox and storing it into messages variable--
                        index = len(messages) - 1  # --taking the index of last recieved mail--

                if index > 0:
                    loopstatus = True
                    last_mail_rcvd_on = str(messages[index].ReceivedTime)
                    while (loopstatus):
                        
                        if (str(messages[index].ReceivedTime) > chck_mail_till_time):
                            match_lst = re.findall('\\bINC[0-9]{3,7}\\b', messages[index].Subject, re.I)
                            if (len(match_lst) > 0):
                               
                                if match_lst[0] == incidentNumber:
                                    
                                    if ('Approved' or 'approved') in messages[index].Body.split('\r\n')[0]:
                                        status = 'approved'
                                    elif ('Rejected' or 'rejected') in messages[index].Body.split('\r\n')[0]:
                                        status = 'rejected'
                                    logging.info(
                                        'Trying to update workflow_tickets_tbl with approve_reject_state as true')
                                    MongoDBPersistence.workflow_tickets_tbl.update_one({'IncidentNo': match_lst[0]}, {
                                        '$set': {'approve_reject_state': True}}, upsert=True)
                                    return status
                        else:
                            logging.info('Completed checking all the mails till the mail checked in the previous loop')
                            loopstatus = False
                        index = index - 1
                    # --Logic to resend approve request mail once after specific time period--
                    if (not wrkflw_tckt_dtls_doc['send_rmndr_state']):
                        if (last_mail_rcvd_on > wrkflw_tckt_dtls_doc['reminder_date']):
                            logging.info('Found no response till last 2 days, Trying to send remainder mail')
                           
                            subject = 'Reminder for ' + incidentNumber + ' :Approve IIA access request for user ' + user
                            message = 'Reply Approved/Rejected. \n' \
                                      'If you are not responding to this mail in 3 days the request get auto rejected' \
                                      '\nNote : This is a system generated mail please do not reply anything except the mentioned words'
                            logging.info('Trying to call send mail method')
                            ProvideAccessToIIA.send_mail(user_mailid, user_mailid, user, subject, message)
                            logging.info('Trying to update workflow_tickets_tbl: setting send_rmndr_state to true')
                            MongoDBPersistence.workflow_tickets_tbl.update_one({'IncidentNo': incidentNumber},
                                                                               {'$set': {'send_rmndr_state': True}})
                            return 'mail resended'
                    # --logic to stop waiting for response mail after a specific time period--
                    elif (last_mail_rcvd_on > wrkflw_tckt_dtls_doc['expire_date']):
                        logging.info('Found no response till last 5 days, Trying to send response as rejected')
                        MongoDBPersistence.workflow_tickets_tbl.update_one({'IncidentNo': incidentNumber},
                                                                           {'$set': {'approve_reject_state': True}},
                                                                           upsert=True)
                        return 'rejected'
                MongoDBPersistence.workflow_tickets_tbl.update_one({'IncidentNo': incidentNumber},
                                                                   {'$set': {'chckd_mail_till': last_mail_rcvd_on}},
                                                                   upsert=True)
            else:
                logging.warn(
                    'No Tickets found from workflow_tickets_tbl which is having approve_reject_status as false')
                return "no_data"
        except Exception as e:
            logging.error('%s:%s' % (RestService.timestamp(), str(e)))
        return 'no_response'

    @staticmethod
    def approved_email(incident_no):
        try:

            logging.info('Trying to read date from workflow_tickets_tbl for incident : %s' % incident_no)
            wrkflw_tckt_dtls_doc = MongoDBPersistence.workflow_tickets_tbl.find_one({"IncidentNo": incident_no})
            user_mailid = wrkflw_tckt_dtls_doc['user_mailid']
            user_mailid = 'semail_id'
            user = wrkflw_tckt_dtls_doc['user']
            subject = incident_no + ': Approved'
            message = 'The Access request has been approved!\n\nuser name : ' + user_mailid + \
                      '\n\n kindly follow the below steps to set the password: \n' \
                      '\t 1 : open IIA Login page\n' \
                      '\t 2 : enter your user name\n' \
                      '\t 3 : click on reset password option\n' \
                      '\t 4 : verify user name\n' \
                      '\t 5 : set new password'
            resp = ProvideAccessToIIA.send_mail(user_mailid, None, user, subject, message)
            if (resp == 'success'):
                logging.info('mail sent')
                
                pass
            else:
                
                pass
            return 'success'
        except Exception as e:
            logging.error('%s' % str(e))
        return 'failure'

    @staticmethod
    def rejected_email(incident_no):
        try:

            logging.info('Trying to read date from workflow_tickets_tbl for incident : %s' % incident_no)
            wrkflw_tckt_dtls_doc = MongoDBPersistence.workflow_tickets_tbl.find_one({"IncidentNo": incident_no})
            user_mailid = wrkflw_tckt_dtls_doc['user_mailid']
            user = wrkflw_tckt_dtls_doc['user']
            subject = incident_no + ':Rejected'
            message = 'The Access request has been rejected!'
            resp = ProvideAccessToIIA.send_mail(user_mailid, None, user, subject, message)
            if (resp == 'success'):
                # --mail sended--
                pass
            else:
                # --failed to send mail
                pass
            return 'success'
        except Exception as e:
            logging.error('%s' % str(e))
        return 'failure'

    @staticmethod
    def insert_user_dtls(incident_no):
        try:

            logging.info('Trying to read date from workflow_tickets_tbl for incident : %s' % incident_no)
            wrkflw_tckt_dtls_doc = MongoDBPersistence.workflow_tickets_tbl.find_one({"IncidentNo": incident_no})
            user_id = wrkflw_tckt_dtls_doc['user_mailid']
            user_name = user_id.split('@')[0].replace('.', ' ')
            logging.info('Trying to insert user details to users_tbl')
            MongoDBPersistence.users_tbl.insert_one(
                {"UserID": user_id, 'UserName': user_name, "TeamID": 1, "Role": "Admin"})
            return 'success'
        except Exception as e:
            logging.error('%s' % str(e))
        return 'failure'
