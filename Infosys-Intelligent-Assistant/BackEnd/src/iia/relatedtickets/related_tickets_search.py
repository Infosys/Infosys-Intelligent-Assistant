__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

import time
from time import time

from iia.persistence.mongodbpersistence import MongoDBPersistence
from iia.relatedtickets.related_tickets_seach_batch import RelatedSearch
from iia.relatedtickets.textRankSearch import TextRankSearch
from iia.utils.log_helper import get_logger

customer_id = 1
dataset_id = 1

logging = get_logger(__name__)


class MappingPersistence(object):
    @staticmethod
    def get_mapping_details(customer_id):
        itsm_details = MongoDBPersistence.itsm_details_tbl.find_one({}, {"_id": 0, "ITSMToolName": 1})
        itsm_tool_name = itsm_details['ITSMToolName']
        field_mapping = MongoDBPersistence.mapping_tbl.find_one({"Source_ITSM_Name": itsm_tool_name}, {"_id": 0})
        return field_mapping


class relatedticket(object):

    @staticmethod
    def startProcess(customer_id):
        field_mapping = MappingPersistence.get_mapping_details(customer_id)
        group_field_name = field_mapping['Group_Field_Name']
        ticket_id_field_name = field_mapping['Ticket_ID_Field_Name']
        status_field_name = field_mapping['Status_Field_Name']
        description_field_name = field_mapping['Description_Field_Name']

        start_time = time()
        print("inside start process")
        config_values = MongoDBPersistence.configuration_values_tbl.find_one({},
                                                                             {"Related_Tickets_Algorithm": 1, "_id": 0})
        list_search_algorithms = ['textRank', 'word2Vec', 'doc2Vec', 'BERT']
        logging.info(f"search_algorithms: {list_search_algorithms}")

        realTimeincidents = list(MongoDBPersistence.rt_tickets_tbl.find({"user_status": {"$in": ["Not Approved"]}},
                                                                        {ticket_id_field_name: 1, '_id': 0,
                                                                         group_field_name: 1, 'opened_by': 1,
                                                                         "CustomerID": 1, "DatasetID": 1}))
        realTimeApprovedincidents = list(MongoDBPersistence.rt_tickets_tbl.find(
            {"state": {"$nin": ["closed"]}, "user_status": {"$in": ["Approved"]}},
            {ticket_id_field_name: 1, '_id': 0, group_field_name: 1, 'opened_by': 1, "CustomerID": 1, "DatasetID": 1}))
        realTimeincidents.extend(realTimeApprovedincidents)
        print("here results ", realTimeincidents)

        
        Related_Ticket_number = []
        for unique_tickets in MongoDBPersistence.related_tickets_tbl.find().distinct('RT_Ticket_Number'):
            if MongoDBPersistence.related_tickets_tbl.count_documents({"RT_Ticket_Number": unique_tickets}) == 4:
                Related_Ticket_number.append(unique_tickets)

        realTimeincidents_updated = []
        for num in realTimeincidents:
            incident_number = (num[ticket_id_field_name])
            if incident_number in Related_Ticket_number:
                continue
            else:
                realTimeincidents_updated.append(num)

        print(realTimeincidents_updated)

        # assuming all the real time incidents has same set of  column names and values
        # check for 'assignmentgroup' and 'createdby' in dispalyField List should be same in TblIncident Training and RtIncident Table
        if (realTimeincidents_updated):
            for search_algorithm in list_search_algorithms:
                logging.info(f"Running {search_algorithm} algorithm")
                related_tic_flag = "textrank_related_tic_flag"

                if search_algorithm == "word2Vec":
                    related_tic_flag = "word2vec_related_tic_flag"
                if search_algorithm == "doc2Vec":
                    related_tic_flag = "doc2vec_related_tic_flag"
                if search_algorithm == "BERT":
                    related_tic_flag = "BERT_related_tic_flag"

                if group_field_name and 'createdby' in realTimeincidents_updated[0]:
                    for num in realTimeincidents_updated:
                        try:
                            incident_number = (num[ticket_id_field_name])
                            rt_assignemnt_group = (num[group_field_name])
                            rt_created_by = (num['createdby'])
                            customer_id = num["CustomerID"]
                            dataset_id = num["DatasetID"]
                            ticketflag = MongoDBPersistence.related_tickets_tbl.find_one(
                                {"RT_Ticket_Number": incident_number, "Algorithm_name": search_algorithm})
                            if ticketflag:
                                logging.info("Related ticket with %s for this %s ticket number is presented" % (
                                    search_algorithm, incident_number))
                                continue
                            else:
                                if (
                                        search_algorithm == "word2Vec" or search_algorithm == "doc2Vec" or search_algorithm == "BERT"):
                                    relatedResults = RelatedSearch.getRelatedTickets(customer_id, dataset_id,
                                                                                     incident_number, search_algorithm,
                                                                                     rt_assignemnt_group)
                                    
                                    print("closedresults from startProcess", relatedResults)
                                    relatedOpenResults = RelatedSearch.getRelatedOpenTickets(customer_id, dataset_id,
                                                                                             incident_number,
                                                                                             search_algorithm)
                                    print("open results from startProcess", relatedOpenResults)
                                else:
                                    relatedResults = TextRankSearch.getRelatedTickets(customer_id, dataset_id,
                                                                                      incident_number)
                                    print("related_results using TextRankSearch.py", relatedResults)
                                    relatedOpenResults = TextRankSearch.getRelatedOpenTickets(customer_id, dataset_id,
                                                                                              incident_number)
                                    print("related_openresults using TextRankSearch.py", relatedOpenResults)
                                logging.info(
                                    f"insering algorithm name: {search_algorithm} in related_tickets for ticket_number: {incident_number}")
                                MongoDBPersistence.related_tickets_tbl.insert_one(
                                    {"RT_Ticket_Number": incident_number, 'Related_ticket_info': relatedResults,
                                     'Related_Open_ticket_info': relatedOpenResults,
                                     'Algorithm_name': search_algorithm})
                                MongoDBPersistence.rt_tickets_tbl.update_one(
                                    {"CustomerID": customer_id, "number": incident_number},
                                    {"$set": {related_tic_flag: True}})
                        except Exception as e:
                            print('exception in main function.......', e)
                            MongoDBPersistence.rt_tickets_tbl.update_one(
                                {"CustomerID": customer_id, "number": incident_number},
                                {"$set": {related_tic_flag: "Could not Processed"}})
                            logging.info("Skipped this %s incident because of following exception-  %s  " % (
                                num[ticket_id_field_name], str(e)))
                            continue
                elif group_field_name in realTimeincidents_updated[0] and 'createdby' not in realTimeincidents_updated[
                    0]:
                    for num in realTimeincidents_updated:
                        try:
                            incident_number = (num[ticket_id_field_name])
                            rt_assignemnt_group = (num[group_field_name])
                            customer_id = num["CustomerID"]
                            dataset_id = num["DatasetID"]
                            
                            ticketflag = MongoDBPersistence.related_tickets_tbl.find_one(
                                {"RT_Ticket_Number": incident_number, "Algorithm_name": search_algorithm})
                            if ticketflag:
                                logging.info("Related ticket with %s for this %s ticket number is presented" % (
                                    search_algorithm, incident_number))
                                continue
                            else:
                                if (
                                        search_algorithm == "word2Vec" or search_algorithm == "doc2Vec" or search_algorithm == "BERT"):
                                    relatedResults = RelatedSearch.getRelatedTickets(customer_id, dataset_id,
                                                                                     incident_number, search_algorithm,
                                                                                     rt_assignemnt_group)
                                    
                                    print("closedresults from startProcess", relatedResults)
                                    relatedOpenResults = RelatedSearch.getRelatedOpenTickets(customer_id, dataset_id,
                                                                                             incident_number,
                                                                                             search_algorithm)
                                    print("open results from startProcess", relatedOpenResults)
                                else:
                                    relatedResults = TextRankSearch.getRelatedTickets(customer_id, dataset_id,
                                                                                      incident_number)
                                    print("related_results using TextRankSearch.py", relatedResults)
                                    relatedOpenResults = TextRankSearch.getRelatedOpenTickets(customer_id, dataset_id,
                                                                                              incident_number)
                                    print("related_openresults using TextRankSearch.py", relatedOpenResults)
                                logging.info(
                                    f"insering algorithm name: {search_algorithm} in related_tickets for ticket_number: {incident_number}")
                                MongoDBPersistence.related_tickets_tbl.insert_one(
                                    {"RT_Ticket_Number": incident_number, 'Related_ticket_info': relatedResults,
                                     'Related_Open_ticket_info': relatedOpenResults,
                                     'Algorithm_name': search_algorithm})
                                MongoDBPersistence.rt_tickets_tbl.update_one(
                                    {"CustomerID": customer_id, "number": incident_number},
                                    {"$set": {related_tic_flag: True}})
                        except Exception as e:
                            print('exception in main function.......', e)
                            MongoDBPersistence.rt_tickets_tbl.update_one(
                                {"CustomerID": customer_id, "number": incident_number},
                                {"$set": {related_tic_flag: "Could not Processed"}})
                            logging.info("Skipped this %s incident because of following exception-  %s  " % (
                                num[ticket_id_field_name], str(e)))
                            continue
                else:
                    for num in realTimeincidents_updated:
                        try:
                            incident_number = (num[ticket_id_field_name])
                            customer_id = num["CustomerID"]
                            dataset_id = num["DatasetID"]
                            rt_assignemnt_group = (num[group_field_name])
                           
                            ticketflag = MongoDBPersistence.related_tickets_tbl.find_one(
                                {"RT_Ticket_Number": incident_number, "Algorithm_name": search_algorithm})
                            if ticketflag:
                                logging.info("Related ticket with %s for this %s ticket number is presented" % (
                                    search_algorithm, incident_number))
                                continue
                            else:
                                if (
                                        search_algorithm == "word2Vec" or search_algorithm == "doc2Vec" or search_algorithm == "BERT"):
                                    relatedResults = RelatedSearch.getRelatedTickets(customer_id, dataset_id,
                                                                                     incident_number, search_algorithm,
                                                                                     rt_assignemnt_group)
                                    
                                    print("closedresults from startProcess", relatedResults)
                                    relatedOpenResults = RelatedSearch.getRelatedOpenTickets(customer_id, dataset_id,
                                                                                             incident_number,
                                                                                             search_algorithm)
                                    print("open results from startProcess", relatedOpenResults)
                                else:
                                    relatedResults = TextRankSearch.getRelatedTickets(customer_id, dataset_id,
                                                                                      incident_number)
                                    print("related_results using TextRankSearch.py", relatedResults)
                                    relatedOpenResults = TextRankSearch.getRelatedOpenTickets(customer_id, dataset_id,
                                                                                              incident_number)
                                    print("related_openresults using TextRankSearch.py", relatedOpenResults)
                                logging.info(
                                    f"insering algorithm name: {search_algorithm} in related_tickets for ticket_number: {incident_number}")
                                MongoDBPersistence.related_tickets_tbl.insert_one(
                                    {"RT_Ticket_Number": incident_number, 'Related_ticket_info': relatedResults,
                                     'Related_Open_ticket_info': relatedOpenResults,
                                     'Algorithm_name': search_algorithm})
                                MongoDBPersistence.rt_tickets_tbl.update_one(
                                    {"CustomerID": customer_id, "number": incident_number},
                                    {"$set": {related_tic_flag: True}})
                        except Exception as e:
                            print('exception in main function.......', e)
                            MongoDBPersistence.rt_tickets_tbl.update_one(
                                {"CustomerID": customer_id, "number": incident_number},
                                {"$set": {related_tic_flag: "Could not Processed"}})
                            logging.info("Skipped this %s incident because of following exception-  %s  " % (
                                num[ticket_id_field_name], str(e)))
                            continue
        else:
            logging.info("No new incident found in IncidentRT table")
            print("No new incident found in IncidentRT table")

        end_time = time()
        seconds_elapsed = end_time - start_time
        logging.info("Time taken: %s " % (seconds_elapsed))
        print("Time taken:", seconds_elapsed)
