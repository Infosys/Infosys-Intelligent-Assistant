__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

import pandas as pd
from iia.utils.log_helper import get_logger, log_setup
from iia.persistence.mongodbpersistence import MongoDBPersistence
from flask import session
from iia.restservice import RestService
from bson import json_util
import numpy as np
from datetime import datetime
from datetime import timedelta
import pdfkit
import base64
from flask import send_file
import os

from pathlib import Path

logging = get_logger(__name__)
# log_setup()
app = RestService.getApp()
app.secret_key = "iia-secret-key"


@app.route('/api/getDashboardSummary/<string:start_date>/<string:end_date>/<string:teamname>', methods=['GET'])
def getDashboardSummary(start_date, end_date, teamname):
    return Dashboard.get_dashboard_summary(start_date=start_date, end_date=end_date, teamname=teamname)


@app.route('/api/getDatasetDetails/<string:teamname>', methods=['GET'])
def getDataset(teamname):
    return json_util.dumps(Dashboard.get_dataset(teamname=teamname).to_dict('records'))


@app.route('/api/getTicketsUser/<string:start_date>/<string:end_date>/<string:assignment_group>/<string:teamname>',
           methods=['GET'])
def getTicketsUser(start_date, end_date, assignment_group, teamname):
    return Dashboard.get_tickets_assignedto_user(start_date=start_date, end_date=end_date, teamname=teamname,
                                                 assignment_group=assignment_group)


@app.route('/api/getTicketsGroup/<string:start_date>/<string:end_date>/<string:teamname>', methods=['GET'])
def getTicketsGroup(start_date, end_date, teamname):
    return Dashboard.get_tickets_assignedto_group(start_date=start_date, end_date=end_date, teamname=teamname)

@app.route('/api/getAssignmentGroup/<string:start_date>/<string:end_date>/<string:teamname>', methods=['GET'])
def getAssignmentGroup(start_date,end_date,teamname):
    return Dashboard.get_assignment_group(start_date=start_date,end_date=end_date,teamname=teamname)


@app.route('/api/getApprovedTickets/<string:start_date>/<string:end_date>/<string:teamname>', methods=['GET'])
def getApprovedTickets(start_date, end_date, teamname):
    return Dashboard.get_approved_tickets(start_date=start_date, end_date=end_date, teamname=teamname)


@app.route('/api/getCorrectIncorrectPrediction/<string:start_date>/<string:end_date>/<string:teamname>',
           methods=['GET'])
def getCorrectIncorrectPrediction(start_date, end_date, teamname):
    return Dashboard.get_correct_incorrect_prediction(start_date=start_date, end_date=end_date, teamname=teamname)


@app.route('/api/getDashboardReport/<string:start_date>/<string:end_date>/<string:assignment_group>/<string:teamname>',
           methods=['GET'])
def getDashboardReport(start_date, end_date, assignment_group, teamname):
    return Dashboard.download_pdf(start_date=start_date,
                                  end_date=end_date,
                                  assignment_group=assignment_group,
                                  teamname=teamname)


class Dashboard(object):
    '''
    classdocs
    '''

    def __init__(self):
        pass

    @staticmethod
    def get_dataset(start_date=None, end_date=None, teamname=None):

        try:
            logging.info(f"session: {session}")
            role = session['role']
            logging.debug(f"role: {role}")
            user = session['user']
            logging.debug(f"user: {user}")
        except:
            role = 'Admin'

        total_tickets_fetched = list(MongoDBPersistence.rt_tickets_tbl.find({}, {
            "number": 1,
            "assigned_to": 1,
            "assignment_group": 1,
            "user_status": 1,
            "state": 1,
            "auto_resolution": 1,
            "DatasetID": 1,
            "_id": 0}))

        total_tickets_fetched = pd.DataFrame(total_tickets_fetched)

        logging.debug(f"rt_tickets: {total_tickets_fetched}")

        total_tickets_processed = list(MongoDBPersistence.predicted_tickets_tbl.find({}, {
            "number": 1,
            "predicted_fields": 1,
            "predicted_assigned_to": 1,
            "assignment_group": 1,
            "timestamp": 1,
            "_id": 0}))

        total_tickets_processed = pd.DataFrame(total_tickets_processed)
        total_tickets_processed = total_tickets_processed.rename(
            columns={'assignment_group': 'approved_assignment_group'})

        if 'approved_assignment_group' not in total_tickets_processed.columns:
            total_tickets_processed['approved_assignment_group'] = ''

        predicted_fields = total_tickets_processed['predicted_fields']

        predicted_fields_list = []

        drop_predicted_columns = ['ConfidenceScore', 'prediction_by']

        rename_predicted_columns = {'assignment_group': 'predicted_assignment_group'}

        for fields in predicted_fields:
            for item in fields:
                predicted_fields_list.append(item)

        df_predicted_fields = pd.DataFrame(predicted_fields_list)

        df_predicted_fields = df_predicted_fields.drop(columns=drop_predicted_columns)
        df_predicted_fields = df_predicted_fields.rename(columns=rename_predicted_columns)

        total_tickets_processed = total_tickets_processed.drop(columns=['predicted_fields'])

        total_tickets_processed = pd.merge(total_tickets_processed, df_predicted_fields, left_index=True,
                                           right_index=True)

        logging.debug(f"predicted_tickets: {total_tickets_processed}")

        approved_tickets = list(MongoDBPersistence.approved_tickets_tbl.find({}, {
            "ticket_number": 1,
            "auto_approve": 1,
            "_id": 0}))

        merged_df = pd.merge(total_tickets_fetched, total_tickets_processed, how='inner', on='number')

        if approved_tickets:
            approved_tickets = pd.DataFrame(approved_tickets)
            approved_tickets = approved_tickets.rename(columns={'ticket_number': 'number'})

            merged_df = pd.merge(merged_df, approved_tickets, how='left', on='number')
        else:
            merged_df['auto_approve'] = ''

        if role != 'Admin':
            UserName = MongoDBPersistence.users_tbl.find_one({'UserID': user}, {"UserName": 1, "_id": 0})
            logging.debug(f"UserName: {UserName}")
            merged_df = merged_df.loc[merged_df['assigned_to'] == UserName['UserName']]

        if start_date != None and end_date != None:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            merged_df['timestamp'] = pd.to_datetime(merged_df['timestamp'], format='%Y/%m/%d %H:%M:%S')
            merged_df = merged_df.loc[
                (merged_df['timestamp'] >= start_date) & (merged_df['timestamp'] <= end_date + timedelta(1))]
        logging.info(f"teamname: {teamname}")
        if teamname != None:
            dataset = MongoDBPersistence.teams_tbl.find_one({"TeamName": teamname}, {"DatasetID": 1, "_id": 0})
            logging.info(f"dataset: {dataset}")
            if 'DatasetID' not in dataset:
                dataset['DatasetID'] = None
            if dataset:
                merged_df = merged_df.loc[merged_df['DatasetID'] == dataset['DatasetID']]
            else:
                merged_df = merged_df.loc[merged_df['DatasetID'] == None]

        merged_df.loc[(merged_df['assigned_to'] != "") & (
                    merged_df['user_status'] == "Not Approved"), 'user_status'] = "Updated in ITSM"
        logging.debug(f"merged_df: {merged_df}")
        return merged_df

    @staticmethod
    def get_dashboard_summary(start_date, end_date, teamname):
        logging.debug(f"session : {session}")

        try:
            merged_df = Dashboard.get_dataset(start_date, end_date, teamname)
            total_tickets_fetched = merged_df['number'].count()
            logging.info(f"total_tickets_fetched: {total_tickets_fetched}")
            total_tickets_processed = merged_df.loc[merged_df['user_status'] != 'Updated in ITSM'][
                'predicted_assignment_group'].count()
            logging.debug(f"total_tickets_processed: {total_tickets_processed}")
            auto_classification = merged_df['predicted_assignment_group'].count()
            logging.debug(f"auto_classification: {auto_classification}")
            auto_approved = merged_df.loc[merged_df['auto_approve'] == True]['predicted_assigned_to'].count()
            logging.debug(f"auto_approved: {auto_approved}")
            manual_approved = merged_df.loc[merged_df['auto_approve'] == False]['predicted_assigned_to'].count()
            logging.debug(f"manual_approved: {manual_approved}")
            auto_resolution = merged_df.loc[merged_df['auto_resolution'] == True]['number'].count()
            logging.debug(f"auto_resolution: {auto_resolution}")
            total_tickets_processed_outside_iia = merged_df.loc[merged_df['user_status'] == 'Updated in ITSM'][
                'number'].count()
            logging.debug(f"auto_resolution: {auto_resolution}")
            closed_tickets_count = merged_df.loc[merged_df['state'] == 'closed']['number'].count()
            logging.debug(f"closed_tickets_count: {closed_tickets_count}")
            open_tickets_count = merged_df.loc[merged_df['state'] != 'closed']['number'].count()
            logging.debug(f"open_tickets_count: {open_tickets_count}")

            dict_fields = {'Total Tickets Fetched': total_tickets_fetched,
                           'Total Tickets Processed': total_tickets_processed,
                           'Auto Classification': auto_classification,
                           'Auto Approved': auto_approved,
                           'Manually Approved': manual_approved,
                           'Closed Tickets': closed_tickets_count,
                           'Open Tickets': open_tickets_count,
                           "Tickets Processed Outside IIA": total_tickets_processed_outside_iia
                           }

            df_summary = pd.DataFrame(list(dict_fields.items()), columns=['Summary', 'Count'])
            resp = json_util.dumps(df_summary.to_dict('records'))
            logging.info(f"resp: {resp}")
            return resp

        except Exception as e:
            logging.error(e, exc_info=True)
            dict_fields = {'Total Tickets Fetched': 0,
                           'Total Tickets Processed': 0,
                           'Auto Classification': 0,
                           'Auto Approved': 0,
                           'Manually Approved': 0,
                           'Closed Tickets': 0,
                           'Open Tickets': 0,
                           "Tickets Processed Outside IIA": 0
                           }
            df_summary = pd.DataFrame(list(dict_fields.items()), columns=['Summary', 'Count'])
            resp = json_util.dumps(df_summary.to_dict('records'))
            logging.info(f"resp: {resp}")
            return resp

    @staticmethod
    def get_tickets_assignedto_user(start_date, end_date, teamname, assignment_group: str = None):

        try:
            df = Dashboard.get_dataset(start_date, end_date, teamname)
            df = df.loc[df['user_status'] == "Approved"]

            if assignment_group is not None and assignment_group.lower() != 'select all':
                logging.debug(f"df: {df[['assigned_to', 'assignment_group', 'approved_assignment_group']]}")
                df = df.loc[df['approved_assignment_group'] == assignment_group]
                logging.debug(f"df: {df}")
                logging.debug(f"assignment_group: {assignment_group}")

            df = df[['assigned_to']]

            df = df.groupby(['assigned_to'])['assigned_to'].count().reset_index(name="values")
            response = {"response": "success",
                        "keys": df['assigned_to'].tolist(),
                        "values": df['values'].tolist()}

            logging.debug(f"resp: {response}")
            logging.debug(f"len resp: {len(response)}")
            resp = json_util.dumps(response)
        except Exception as e:
            logging.error(e, exc_info=True)
            response = {"response": "success",
                        "keys": '',
                        "values": 0}

            logging.debug(f"resp: {response}")
            logging.debug(f"len resp: {len(response)}")
            resp = json_util.dumps(response)
        return resp

    @staticmethod
    def get_tickets_assignedto_group(start_date, end_date, teamname):

        try:
            df = Dashboard.get_dataset(start_date, end_date, teamname)
            df = df.loc[df['user_status'] == "Approved"]

            df = df[['assignment_group']]

            df = df.groupby(['assignment_group'])['assignment_group'].count().reset_index(name="values")
            response = {"response": "success",
                        "keys": df['assignment_group'].tolist(),
                        "values": df['values'].tolist()}

            logging.debug(f"resp: {response}")
            logging.debug(f"len resp: {len(response)}")
            resp = json_util.dumps(response)
        except Exception as e:
            logging.error(e, exc_info=True)
            resp = json_util.dumps({"response": "failure"})
        return resp

    @staticmethod
    def get_assignment_group(start_date, end_date, teamname):
        print('Under get_assignment_group')

        try:
            df = Dashboard.get_dataset(start_date, end_date, teamname)
            if not df.empty:

                df = df[['assignment_group_from_approved_Tbl']]
                df = df.dropna()
                df = df['assignment_group_from_approved_Tbl'].unique()

                logging.info(f"unique df: {df}")
                df = pd.DataFrame(df, columns=['assignment_group'])
                df = df.to_dict('records')
                logging.debug(f"dict df: {df}")
                resp = [{'assignment_group': 'Select All'}] + df
                logging.debug(f"resp: {resp}")
                resp = json_util.dumps(resp)
                logging.debug(f"resp: {resp}")
                logging.debug(f"len resp: {len(resp)}")
                if len(resp) <= 1:
                    resp = json_util.dumps([{'assignment_group': 'Select All'}])
            else:
                resp = json_util.dumps([{'assignment_group': 'Select All'}])
        except Exception as e:
            logging.error(e, exc_info=True)
            resp = json_util.dumps([{'assignment_group': 'Select All'}])
        return resp

    @staticmethod
    def get_approved_tickets(start_date, end_date, teamname):
        try:
            df = Dashboard.get_dataset(start_date, end_date, teamname)
            df = df.loc[df['user_status'] == "Approved"]

            df = df[['auto_approve']]

            df['auto_approve'] = df['auto_approve'].replace({True: 'Auto Approved', False: 'Manual Approved'})

            response = {'response': 'success'}
            dict_approved_count = {
                'Auto Approved': len(df.loc[df['auto_approve'] == "Auto Approved"]["auto_approve"].to_list())}
            response.update(dict_approved_count)
            dict_approved_count = {
                'Manual Approved': len(df.loc[df['auto_approve'] == "Manual Approved"]["auto_approve"].to_list())}
            response.update(dict_approved_count)
            resp = json_util.dumps([response])

        except Exception as e:
            logging.error(e, exc_info=True)
            response = {'response': 'success'}
            dict_approved_count = {
                'Auto Approved': 0}
            response.update(dict_approved_count)
            dict_approved_count = {
                'Manual Approved': 0}
            response.update(dict_approved_count)
            resp = json_util.dumps([{'response': 'failure'}])
        return resp

    @staticmethod
    def get_correct_incorrect_prediction(start_date, end_date, teamname):
        try:
            df = Dashboard.get_dataset(start_date, end_date, teamname)
            df = df.loc[df['user_status'] == "Approved"]

            df = df[['approved_assignment_group', 'predicted_assignment_group']]
            df['match'] = df['predicted_assignment_group'].eq(df['approved_assignment_group'])
            df = df[['match']]

            df['match'] = df['match'].replace({True: 'Predicted Correctly', False: 'Predicted Incorrectly'})

            response = {'response': 'success'}
            dict_approved_count = {
                'Predicted Correctly': len(df.loc[df['match'] == "Predicted Correctly"]["match"].to_list())}
            response.update(dict_approved_count)
            dict_approved_count = {
                'Predicted Incorrectly': len(df.loc[df['match'] == "Predicted Incorrectly"]["match"].to_list())}
            response.update(dict_approved_count)

            resp = json_util.dumps([response])
        except Exception as e:
            logging.error(e, exc_info=True)
            response = {'response': 'success'}
            dict_approved_count = {
                'Predicted Correctly': 0}
            response.update(dict_approved_count)
            dict_approved_count = {
                'Predicted Incorrectly': 0}
            response.update(dict_approved_count)
            resp = json_util.dumps([response])
        return resp

    @staticmethod
    def download_pdf(start_date, end_date, teamname, assignment_group: str = None):

        try:
            summary = Dashboard.get_dashboard_summary(
                start_date,
                end_date,
                teamname)
            summary = json_util.loads(summary)

            df = pd.DataFrame(summary)
            df_summary_html = df.to_html(index=False)

            flag_approved_tickets = False
            flag_predicted_tickets = False
            flag_assigned_to_user = False
            flag_assignment_group = False

            try:
                approved_tickets = json_util.loads(Dashboard.get_approved_tickets(start_date, end_date, teamname))[0]
                del approved_tickets['response']

                Dashboard.generate_donut_graph(list(approved_tickets.keys()),
                                               list(approved_tickets.values()),
                                               filename="data/approved_tickets.png",
                                               title="Tickets Approved")
                flag_approved_tickets = True

            except Exception as e:
                logging.error(e, exc_info=True)
            try:
                predicted_tickets = json_util.loads(
                    Dashboard.get_correct_incorrect_prediction(
                        start_date,
                        end_date,
                        teamname)
                )[0]

                del predicted_tickets['response']

                Dashboard.generate_donut_graph(columns=list(predicted_tickets.keys()),
                                               count=list(predicted_tickets.values()),
                                               filename="data/predicted_tickets.png",
                                               title="Tickets Predicted")
                flag_predicted_tickets = True
            except Exception as e:
                logging.error(e, exc_info=True)

            try:
                tickets_assigned_to_user = Dashboard.get_tickets_assignedto_user(
                    start_date,
                    end_date,
                    teamname,
                    assignment_group
                )
                tickets_assigned_to_user = json_util.loads(tickets_assigned_to_user)

                del tickets_assigned_to_user['response']

                Dashboard.generate_inverted_bar_graph(
                    x=tickets_assigned_to_user['keys'],
                    y=tickets_assigned_to_user['values'],
                    x_label="Count of Tickets",
                    y_label="Name of Assignee",
                    title="Tickets Assigned to each Assignee",
                    filename='data/tickets_assigned_to_user.png',
                    color='green'
                )
                flag_assigned_to_user = True
            except Exception as e:
                logging.error(e, exc_info=True)

            try:
                tickets_assigned_to_assignment_group = Dashboard.get_tickets_assignedto_group(
                    start_date,
                    end_date,
                    teamname
                )
                tickets_assigned_to_assignment_group = json_util.loads(tickets_assigned_to_assignment_group)

                del tickets_assigned_to_assignment_group['response']

                Dashboard.generate_inverted_bar_graph(
                    x=tickets_assigned_to_assignment_group['keys'],
                    y=tickets_assigned_to_assignment_group['values'],
                    x_label="Count of Tickets",
                    y_label="Assignment Group",
                    title="Tickets classification based on Assignment Group",
                    filename='data/tickets_assigned_to_assignment_group.png',
                    color="#CDDC39"
                )
                flag_assignment_group = True
            except Exception as e:
                logging.error(e, exc_info=True)

            with open('data/dashboard.css','r') as css_file:
                css_string = css_file.read()

            file_string = "<html>\n"
            file_string = file_string + '<style>' + css_string +'</style>\n'
            file_string = file_string + "<div>\n"
            file_string = file_string + '<div class="row">\n'
            file_string = file_string + df_summary_html + "\n"
            file_string = file_string + "</div>\n"
            file_string = file_string + '<div class="row">\n'
            file_string = file_string + '<div class="col_50">\n'

            if flag_approved_tickets:
                with open('data/approved_tickets.png', "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode()

                file_string = file_string + f"<img class='donut' src=data:image/png;base64,{encoded_string}>\n"

            file_string = file_string + '</div>\n'
            file_string = file_string + '<div class="col_50">\n'

            if flag_predicted_tickets:

                with open('data/predicted_tickets.png', "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode()

                file_string = file_string + f"<img class='donut' src=data:image/png;base64,{encoded_string}>\n"

            file_string = file_string + '</div>\n'
            file_string = file_string + '</div>\n'
            file_string = file_string + '<div class="row">\n'
            file_string = file_string + '<div class="col_70">\n'

            if flag_assigned_to_user:

                with open('data/tickets_assigned_to_user.png', "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode()

                file_string = file_string + f"<img class='bar' src=data:image/png;base64,{encoded_string}>\n"

            file_string = file_string + '</div>\n'

            file_string = file_string + '<div class="col_30">\n'
            file_string = file_string + '</div>\n'

            file_string = file_string + '</div>\n'
            file_string = file_string + '<div class="row">\n'
            file_string = file_string + '<div class="col_70">\n'

            if flag_assignment_group:
                with open('data/tickets_assigned_to_assignment_group.png', "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode()

                file_string = file_string + f"<img class='bar' src=data:image/png;base64,{encoded_string}>\n"

            file_string = file_string + '</div>\n'

            file_string = file_string + '<div class="col_30">\n'
            file_string = file_string + '</div>\n'

            file_string = file_string + '</div>\n'

            file_string = file_string + "</div>\n"
            file_string = file_string + "</html>\n"

            try:
                with open('data/dashboard.html', "w") as html_file:
                    html_file.write(file_string)

                wkhtml_path = pdfkit.configuration(wkhtmltopdf="data/wkhtmltopdf.exe")

                now = datetime.now()
                current_time = now.strftime("%Y-%m-%d %H:%M:%S")

                options = {
                    'page-height': '300mm',
                    'page-width': '280mm',
                    'footer-center': '[page]/[topage]',
                    'footer-right': "IIA-Dashboard",
                    'header-right': f"{current_time}",
                    'footer-line': '',
                    'header-line': '',
                }

                pdfkit.from_file(
                    input ='data/dashboard.html',
                    output_path='data/Dashboard.pdf',
                    configuration=wkhtml_path,
                    options=options,
                    verbose=True)


            except Exception as e:
                logging.error(e,exc_info=True)

            str_datetime = str(datetime.now()).replace('-',"_").replace(':',"_").replace(' ','_').replace('.','_')
            return send_file(str(Path.cwd()) + "\\data\\Dashboard.pdf"
                             ,attachment_filename=f'Dashboard_{str_datetime}.pdf'
                             ,as_attachment=True
                             )
        except Exception as e:
            logging.error(e,exc_info=True)
            return "failure"

    @staticmethod
    def generate_donut_graph(columns: list, count: list, filename: str, title: str):

        import matplotlib.pyplot as plt
        # colors
        colors = ['#ffeb3b', '#ff9800']
        # explosion
        explode = (0.01, 0.01)

        # Pie Chart
        plt.pie(count, colors=colors,
                autopct='%1.1f%%', pctdistance=0.85,
                explode=explode)

        # draw circle
        centre_circle = plt.Circle((0, 0), 0.50, fc='white')
        fig = plt.gcf()

        # Adding Circle in Pie chart
        fig.gca().add_artist(centre_circle)

        # Adding Title of chart
        plt.title(title)

        plt.legend(columns, loc="upper center")

        # Displaying Chart
        plt.savefig(filename,bbox_inches='tight')

        plt.clf()


    @staticmethod
    def generate_inverted_bar_graph(
            x: list,
            y: list,
            x_label: str,
            y_label: str,
            title: str,
            filename: str,
            color: str):

        import matplotlib.pyplot as plt

        plt.figure(figsize=(15, 5))

        plt.barh(x, y, color=color)

        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(title)
        plt.gca().invert_yaxis()
        plt.savefig(filename,bbox_inches='tight')
        plt.clf()

