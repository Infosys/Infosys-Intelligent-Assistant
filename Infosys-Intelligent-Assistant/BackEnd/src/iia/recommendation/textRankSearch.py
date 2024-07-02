__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

import configparser
import csv
import json
import time
from datetime import datetime
from operator import itemgetter

import pandas as pd
from nltk.cluster.util import cosine_distance

from iia.environ import *

from iia.restservice import RestService
from iia.utils.log_helper import get_logger

logging = get_logger(__name__)
with open('data/stopwords.csv', 'r') as readFile:
    reader = csv.reader(readFile)
    list1 = list(reader)
    stopwords_english = list1[0]
    readFile.close()


class TextRankSearch:
    def __init__(self):
        pass

    @staticmethod
    def concatinateFields(customer_id, dataset_id, type_of_tickets, incident_number=0):
        field_mapping = MappingPersistence.get_mapping_details(customer_id)
        group_field_name = field_mapping['Group_Field_Name']
        ticket_id_field_name = field_mapping['Ticket_ID_Field_Name']
        status_field_name = field_mapping['Status_Field_Name']
        description_field_name = field_mapping['Description_Field_Name']
        if (field_mapping['Source_ITSM_Name'] == 'SNOW'):
            close_notes_field_name = field_mapping['Close_Notes_Field_Name']
        else:
            close_notes_field_name = 'close_notes'
        
        try:
            ()
            config = configparser.ConfigParser()
            config["DEFAULT"]['path'] = "config/"
            config.read(config["DEFAULT"]["path"] + "iia.ini")
            input_fields = config["ModuleConfig"]["inputFieldList"]
            
            input_field_list = input_fields.split(',')
            
        except Exception as e:
            logging.error("Error occured: Hint: 'inputFieldList' is not defined in 'config/iia.ini' file.")
            input_field_list = [description_field_name]
            logging.info("%s Taking default as 'input_field_list = [description]'.." % RestService.timestamp())

        input_df = pd.DataFrame()
        try:
            if (type_of_tickets == 'closed'):
                if (incident_number == 0):  # Generate TF for all corpus
                    # Concatinating input fields together into in_field
                    input_df = pd.DataFrame(list(MongoDBPersistence.training_tickets_tbl.find(
                        {'CustomerID': customer_id, "DatasetID": dataset_id}, {ticket_id_field_name: 1, '_id': 0,
                                                                               input_field_list[
                                                                                   0]: 1})))  
                    for input_field_ in input_field_list[1:]:
                        input_df[input_field_] = pd.DataFrame(list(
                            MongoDBPersistence.training_tickets_tbl.find(
                                {'CustomerID': customer_id, "DatasetID": dataset_id}, {'_id': 0, input_field_: 1})))

                else:
                    input_df = pd.DataFrame(list(MongoDBPersistence.rt_tickets_tbl.find(
                        {'CustomerID': customer_id, "DatasetID": dataset_id, ticket_id_field_name: incident_number},
                        {ticket_id_field_name: 1, '_id': 0,
                         input_field_list[0]: 1})))  
                    for input_field_ in input_field_list[1:]:
                        input_df[input_field_] = pd.DataFrame(list(MongoDBPersistence.rt_tickets_tbl.find(
                            {'CustomerID': customer_id, "DatasetID": dataset_id, ticket_id_field_name: incident_number},
                            {'_id': 0, input_field_: 1})))
            elif (type_of_tickets == 'open'):
                if (incident_number == 0):
                    # Concatinating input fields together into in_field
                    input_df = pd.DataFrame(list(MongoDBPersistence.rt_tickets_tbl.find(
                        {'CustomerID': customer_id, "DatasetID": dataset_id, status_field_name: "New",
                         "user_status": "Not Approved"}, {ticket_id_field_name: 1, '_id': 0, input_field_list[
                            0]: 1})))  
                    if (not input_df.empty):
                        for input_field_ in input_field_list[1:]:
                            input_df[input_field_] = pd.DataFrame(list(
                                MongoDBPersistence.training_tickets_tbl.find(
                                    {'CustomerID': customer_id, "DatasetID": dataset_id}, {'_id': 0, input_field_: 1})))
                    else:
                        logging.info("%s There are no open tickets in RT table" % RestService.timestamp())
                        return 'failure'
                else:
                    input_df = pd.DataFrame(list(MongoDBPersistence.rt_tickets_tbl.find(
                        {'CustomerID': customer_id, "DatasetID": dataset_id, ticket_id_field_name: incident_number},
                        {ticket_id_field_name: 1, '_id': 0,
                         input_field_list[0]: 1})))  
                    for input_field_ in input_field_list[1:]:
                        input_df[input_field_] = pd.DataFrame(list(MongoDBPersistence.rt_tickets_tbl.find(
                            {'CustomerID': customer_id, "DatasetID": dataset_id, ticket_id_field_name: incident_number},
                            {'_id': 0, input_field_: 1})))

        except Exception as e:
            logging.error('%s: Error occured in Concatinating input fields using textRankAlgorithm: %s' % (
            RestService.timestamp(), str(e)))
            return 'failure'
        input_df['in_field'] = ''
        for field in input_field_list:
            input_df['in_field'] += input_df[field] + ' '
        json_str = input_df.to_json(orient='records')
        json_data = json.loads(json_str)
        return json_data

    @staticmethod
    def get_raw_text(customer_id, dataset_id, field_name, incident_number, type_of_tickets='closed'):
        try:
            string = ''
            logging.info(f"customer_id: {customer_id}")
            logging.info(f"dataset_id: {dataset_id}")
            logging.info(f"field_name: {field_name}")
            logging.info(f"incident_number: {incident_number}")
            logging.info(f"type_of_tickets: {type_of_tickets}")
            field_mapping = MappingPersistence.get_mapping_details(customer_id)
            ticket_id_field_name = field_mapping['Ticket_ID_Field_Name']

            if (type_of_tickets == 'closed'):
                string = MongoDBPersistence.training_tickets_tbl.find_one(
                    {"CustomerID": customer_id, "DatasetID": dataset_id, ticket_id_field_name: incident_number},
                    {'_id': 0, field_name: 1})
            elif (type_of_tickets == 'open'):
                string = MongoDBPersistence.rt_tickets_tbl.find_one(
                    {"CustomerID": customer_id, "DatasetID": dataset_id, ticket_id_field_name: incident_number},
                    {'_id': 0, field_name: 1})
            return string[field_name]
        except Exception as e:
            print("Key not found in Tbl Incident Training while working with get_raw_text", field_name)
            logging.info(" %s Key not found in Tbl Incident Training while working with get_raw_text- %s" % (
            RestService.timestamp(), str(e)))
            raise

    @staticmethod
    def sentence_similarity(sent1, sent2, stopwords_english=None):
        if stopwords_english is None:
            stopwords_english = []

        sent1 = [w.lower() for w in sent1]
        sent2 = [w.lower() for w in sent2]

        all_words = list(set(sent1 + sent2))

        vector1 = [0] * len(all_words)
        vector2 = [0] * len(all_words)

        # build the vector for the first sentence
        for w in sent1:
            if w in stopwords_english:
                continue
            vector1[all_words.index(w)] += 1

        # build the vector for the second sentence
        for w in sent2:
            if w in stopwords_english:
                continue
            vector2[all_words.index(w)] += 1
        return 1 - cosine_distance(vector1, vector2)

    @staticmethod
    def getRelatedTickets(customer_id, dataset_id, incident_number):
        try:
            ()
            print("Related tickets start time--", datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S"))
            field_mapping = MappingPersistence.get_mapping_details(customer_id)
            group_field_name = field_mapping['Group_Field_Name']
            ticket_id_field_name = field_mapping['Ticket_ID_Field_Name']
            status_field_name = field_mapping['Status_Field_Name']
            description_field_name = field_mapping['Description_Field_Name']
            if (field_mapping['Source_ITSM_Name'] == 'SNOW'):
                close_notes_field_name = field_mapping['Close_Notes_Field_Name']
            else:
                close_notes_field_name = 'close_notes'

            num_tickets = 5  # hardcoded value for related tickets
            incident_list = pd.DataFrame(TextRankSearch.concatinateFields(customer_id, dataset_id, 'closed'))
            query = TextRankSearch.concatinateFields(customer_id, dataset_id, 'closed', incident_number)
            df = pd.DataFrame(incident_list)
            weight = []
            num_of_tickets = len(df[ticket_id_field_name])
            config_values = MongoDBPersistence.configuration_values_tbl.find_one({}, {"accuracy_percent": 1, "_id": 0})
            match_percentage = int(config_values['accuracy_percent']) / 100
            
            weight = [0] * (num_of_tickets)
            counter = 0
            for i in range(num_of_tickets):
                rel_weight = TextRankSearch.sentence_similarity(query[0]['in_field'].split(), df['in_field'][i].split(),
                                                                stopwords_english)
                if (rel_weight >= match_percentage):
                    weight[i] = rel_weight
                    counter += 1
                if (counter >= num_tickets):
                    break
            
            weightDict = {}
            
            for index, item in enumerate(weight):
                if (item > 0):
                    weightDict[index] = item
           
            if (weightDict):
                sorted_weights = sorted(weightDict.items(), key=itemgetter(1))[::-1]
                ranked_sentence_indexes = [item[0] for item in sorted_weights]
                
                SELECTED_SENTENCES = sorted(ranked_sentence_indexes[:5])

                related_tickets = itemgetter(*SELECTED_SENTENCES)(df[ticket_id_field_name])
                if (not isinstance(related_tickets, tuple)):
                    related_tickets = (related_tickets,)
                result_list = []
                results_matched = len(related_tickets)
                print("related_tickets fetched", related_tickets)
                if (results_matched == 0):
                    logging.info("%s: Sorry No matches found..." % RestService.timestamp())
                else:
                    logging.info("%s: Number of search results : %d" % (RestService.timestamp(), results_matched))
                    try:
                        config = configparser.ConfigParser()
                        config["DEFAULT"]['path'] = "config/"
                        config.read(config["DEFAULT"]["path"] + "iia.ini")
                        display_fields = config["ModuleConfig"]["displayFieldList"]
                        display_field_list = display_fields.split(',')
                        print("display field list--", display_field_list)
                        
                    except Exception as e:
                        logging.error(
                            "Error occured: Hint: 'displayFieldList' is not defined in 'config/iia.ini' file.")
                        display_field_list = [description_field_name, ticket_id_field_name, close_notes_field_name]
                        logging.info("Taking default as 'displayFieldList = [description, number , close_notes]'..")
                    
                    customer_choices = display_field_list
                    logging.info("%s: customer_choices : %s" % (RestService.timestamp(), customer_choices))
                    for inc_number in related_tickets:
                        if inc_number == incident_number:
                            continue
                        related_ticket = {}
                        for field_name in customer_choices:
                            related_ticket[field_name] = TextRankSearch.get_raw_text(customer_id, dataset_id,
                                                                                     field_name, inc_number)
                        result_list.append(related_ticket)
                print("Related tickets end time--", datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S"))
                return result_list
            else:
                result = ["No Results Found"]
                return result
        except Exception as e:
            print("Exception occurred in textRank_getRelatedTickets()", e)
            logging.info(
                "%s exception occured in textRank_getRelatedTickets Method for a Incident -%s with exception details as - %s" % (
                RestService.timestamp(), incident_number, str(e)))
            raise

    @staticmethod
    def getRelatedOpenTickets(customer_id, dataset_id, incident_number):
        try:
            ()
            field_mapping = MappingPersistence.get_mapping_details(customer_id)
            group_field_name = field_mapping['Group_Field_Name']
            ticket_id_field_name = field_mapping['Ticket_ID_Field_Name']
            status_field_name = field_mapping['Status_Field_Name']
            description_field_name = field_mapping['Description_Field_Name']
            if (field_mapping['Source_ITSM_Name'] == 'SNOW'):
                close_notes_field_name = field_mapping['Close_Notes_Field_Name']
            else:
                close_notes_field_name = 'close_notes'
            related_concatenated_tickets = TextRankSearch.concatinateFields(customer_id, dataset_id, 'open')
            if (related_concatenated_tickets == 'failure'):
                result = ['No Results Found']
                return result
            else:
                incident_list = pd.DataFrame(related_concatenated_tickets)
            query = TextRankSearch.concatinateFields(customer_id, dataset_id, 'open', incident_number)

            if (query == 'failure'):
                result = ['No Results Found']
                return result

            df = pd.DataFrame(incident_list)
            weight = []
            num_of_tickets = len(df[ticket_id_field_name])
            config_values = MongoDBPersistence.configuration_values_tbl.find_one({}, {"accuracy_percent": 1, "_id": 0})
            match_percentage = int(config_values['accuracy_percent']) / 100
            for i in range(num_of_tickets):
                weight.append(
                    TextRankSearch.sentence_similarity(query[0]['in_field'].split(), df['in_field'][i].split(),
                                                       stopwords_english))
            weightDict = {}
            
            for index, item in enumerate(weight):
                if (item > match_percentage):
                    weightDict[index] = item
            
            if (weightDict):
                sorted_weights = sorted(weightDict.items(), key=itemgetter(1))[::-1]
                ranked_sentence_indexes = [item[0] for item in sorted_weights]
               
                try:
                    SELECTED_SENTENCES = sorted(ranked_sentence_indexes[:5])
                except:
                    logging.info("%s: Less than 5 sentences found from RT table..." % RestService.timestamp())
                    SELECTED_SENTENCES = sorted(
                        ranked_sentence_indexes)  
                related_tickets = itemgetter(*SELECTED_SENTENCES)(df[ticket_id_field_name])
                
                if (not isinstance(related_tickets, tuple)):
                    related_tickets = (related_tickets,)
                
                result_list = []
                results_matched = len(related_tickets)
                if (results_matched == 0):
                    logging.info("%s: Sorry No matches found..." % RestService.timestamp())
                else:
                    logging.info("%s: Number of search results : %d" % (RestService.timestamp(), results_matched))
                    try:
                        config = configparser.ConfigParser()
                        config["DEFAULT"]['path'] = "config/"
                        config.read(config["DEFAULT"]["path"] + "iia.ini")
                        display_fields = config["ModuleConfig"]["displayFieldList"]
                        display_field_list = display_fields.split(',')
                        
                    except Exception as e:
                        logging.error(
                            "Error occured: Hint: 'displayFieldList' is not defined in 'config/iia.ini' file.")
                        display_field_list = [description_field_name, ticket_id_field_name]
                        logging.info("Taking default as 'displayFieldList = [description, number ]'..")
                    
                    display_field_list = display_field_list[0:2]
                    customer_choices = display_field_list
                    logging.info("%s: customer_choices : %s" % (RestService.timestamp(), customer_choices))
                    for inc_number in related_tickets:
                        
                        related_ticket = {}
                        if (inc_number == incident_number):
                            continue
                        for field_name in customer_choices:
                            related_ticket[field_name] = TextRankSearch.get_raw_text(customer_id, dataset_id,
                                                                                     field_name, inc_number, 'open')
                        result_list.append(related_ticket)

                return result_list
            else:
                result = ["No Results Found"]
                return result
        except Exception as e:
            print("Exception occurred in textRank_getRelatedOpenTickets()", e)
            logging.info(
                "%s exception occured in textRank_getRelatedOpenTickets Method for a Incident -%s with exception details as - %s" % (
                RestService.timestamp(), incident_number, str(e)))
            raise
