__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

import configparser
import csv
import json
import os
import re
from collections import Counter
from math import log
from operator import itemgetter
from pathlib import Path

import nltk
import numpy as np
import pandas as pd
import urllib3
from bson import json_util
from flask import request
from gensim.models import Word2Vec
from nltk.cluster.util import cosine_distance
from sentence_transformers import SentenceTransformer
from shareplum import Office365
from shareplum import Site
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
from textblob import TextBlob

from iia.environ import *
from iia.recommendation.KASearch import KAreleatedsearch
from iia.recommendation.textRankSearch import TextRankSearch
from iia.recommendation.word2vecsearch import RelatedSearch
from iia.restservice import RestService
from iia.utils.log_helper import get_logger

logging = get_logger(__name__)
PATH_TO_FREQUENCIES_FILE = './data/frequencies.tsv'

with open('data/stopwords.csv', 'r') as readFile:
    reader = csv.reader(readFile)
    list1 = list(reader)
    stopwords_english = list1[0]
    readFile.close()

stopword_path = './data/stopwords.csv'

with open(stopword_path, 'r') as fh:
    stopwords = fh.read().split(",")


def read_tsv(f):
    frequencies = {}
    with open(f) as tsv:
        tsv_reader = csv.reader(tsv, delimiter='\t')
        for row in tsv_reader:
            frequencies[row[0]] = int(row[1])

    return frequencies


frequencies = read_tsv(PATH_TO_FREQUENCIES_FILE)

app = RestService.getApp()

bertmodel_path = "./models/bert_base"

if not os.path.exists(bertmodel_path):
    os.makedirs(bertmodel_path)

bertmodel = bertmodel_path + "/pytorch_model.bin"
bertmodel_check = Path(bertmodel)
if bertmodel_check.is_file():
    logging.info("BERT model presented in model/bert_base directory")
    sbert_model = SentenceTransformer(bertmodel_path)
else:
    logging.info("BERT pretrained Model not presented in the directory")
    logging.info("BERT Pretrained model downloading...")
    model = SentenceTransformer('bert-base-nli-mean-tokens')
    model.save("./models/bert_base")
    logging.info("BERT pretrained model saved in model/bert_base directory")
    bertmodel_path = "./models/bert_base"
    sbert_model = SentenceTransformer(bertmodel_path)


@app.route("/api/getRelatedTickets/<int:customer_id>/<int:dataset_id>/<incident_number>/<algorithm_name>",
           methods=['GET'])
def getRelatedTickets(customer_id, dataset_id, incident_number, algorithm_name):
    return Recommendation.getRelatedTickets(customer_id, dataset_id, incident_number, algorithm_name)


@app.route("/api/getKnownErrors/<int:customer_id>/<int:dataset_id>/<incident_number>", methods=['GET'])
def getKnownErrors(customer_id, dataset_id, incident_number):
    return Recommendation.getKnownErrors(customer_id, dataset_id, incident_number)


@app.route("/api/getOpenTicketsCount/<int:customer_id>/<int:dataset_id>", methods=["GET"])
def getOpenTicketsCount(customer_id, dataset_id):
    return Recommendation.getOpenTicketsCount(customer_id, dataset_id)


@app.route("/api/getOpenTickets/<int:customer_id>/<int:dataset_id>", methods=["GET"])
def getOpenTickets(customer_id, dataset_id):
    return Recommendation.getOpenTickets(customer_id, dataset_id)


@app.route("/api/getRelatedOpenTickets/<int:customer_id>/<int:dataset_id>/<incident_number>", methods=['GET'])
def getRelatedOpenTickets(customer_id, dataset_id, incident_number):
    return Recommendation.getRelatedOpenTickets(customer_id, dataset_id, incident_number)


@app.route(
    "/api/display_resolution/<int:customer_id>/<int:dataset_id>/<incident_number>/<tab_name>/<cloud_type>/<algorithm_name>",
    methods=['GET'])
def display_resolution(customer_id, dataset_id, incident_number, tab_name, cloud_type, algorithm_name):
    return Recommendation.display_resolution(customer_id, dataset_id, incident_number, tab_name, cloud_type,
                                             algorithm_name)

@app.route("/api/getRelatedKnowledgeArticles/<int:customer_id>/<int:dataset_id>/<incident_number>/<algorithm_name>",
           methods=['GET'])
def getRelatedKnowledgeArticles(customer_id, dataset_id, incident_number, algorithm_name):
    return Recommendation.getRelatedKnowledgeArticles(customer_id, dataset_id, incident_number, algorithm_name)


@app.route("/api/getNER/<int:customer_id>/<int:dataset_id>/<incident_number>")
def getNER(customer_id, dataset_id, incident_number):
    return Recommendation.getNER(customer_id, dataset_id, incident_number)


@app.route("/api/updateNER/<int:customer_id>/<int:dataset_id>/<incident_number>", methods=["PUT"])
def updateNER(customer_id, dataset_id, incident_number):
    return Recommendation.updateNER(customer_id, dataset_id, incident_number)


@app.route("/api/getAttachmentsData/<incident_number>")
def getAttachmentsData(incident_number):
    return Recommendation.getAttachmentsData(incident_number)


@app.route('/api/updateRTChosenAlgorithm/<algorithm_name>', methods=['PUT'])
def update_rt_chosen_algorithm(algorithm_name):
    return Recommendation.update_rt_chosen_algorithm(algorithm_name)


@app.route('/api/getCurrentSnowInstance', methods=['GET'])
def getCurrentSnowInstance():
    return Recommendation.getCurrentSnowInstance()


class Sentence:

    def __init__(self, sentence):
        self.raw = sentence
        normalized_sentence = sentence.replace("‘", "'").replace("’", "'")
        normalized_sentence = " ".join(w for w in nltk.word_tokenize(normalized_sentence) \
                                       if w.lower() in frequencies.keys())
        self.normalized_sentence = normalized_sentence
        self.tokens = [t.lower() for t in nltk.word_tokenize(normalized_sentence)]
        self.tokens_without_stop = [t for t in self.tokens if t not in stopwords_english]

class Recommendation:

    def __init__(self):
        pass

    @staticmethod
    def concatinateFields(customer_id, dataset_id, type_of_tickets, incident_number=0):
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
            logging.error('%s: Error: %s' % (RestService.timestamp(), str(e)))
            return 'failure'
        input_df['in_field'] = ''
        for field in input_field_list:
            input_df['in_field'] += input_df[field] + ' '
        json_str = input_df.to_json(orient='records')
        json_data = json.loads(json_str)
        return json_data

    @staticmethod
    def getCurrentSnowInstance():
        snow_list = list(MongoDBPersistence.customer_tbl.find({'CustomerID': 1}, {"SNOWInstance": 1, "_id": 0}))
        print(type(snow_list))
        for i in snow_list:
            dev_instance_name = i['SNOWInstance']
        print(dev_instance_name)
        return json_util.dumps(dev_instance_name)

    # Generate term frequency vector for training data
    @staticmethod
    def generate_TF(customer_id, dataset_id, type_of_tickets='closed'):
        ()
       
        if (field_mapping['Source_ITSM_Name'] == 'SNOW'):
            close_notes_field_name = field_mapping['Close_Notes_Field_Name']
        else:
            close_notes_field_name = 'close_notes'
        
        incident_list = Recommendation.concatinateFields(customer_id, dataset_id, type_of_tickets)
        
        word_doc_dict = {}
        for ticket in incident_list:
            # Parse the string to get individual words
            list_words = [w.lower() for w in re.split(r'\W+', ticket['in_field']) if
                          w.isalpha() and len(w) > 1 and w.lower() not in stopwords_english]

            for word in list_words:
                if (word_doc_dict.get(word, 0) == 0):
                    word_doc_dict[word] = {}
                    word_doc_dict[word][ticket[ticket_id_field_name]] = 1
                else:
                    word_doc_dict[word][ticket[ticket_id_field_name]] = word_doc_dict[word].get(
                        ticket[ticket_id_field_name], 0)
                    word_doc_dict[word][ticket[ticket_id_field_name]] += 1
        MongoDBPersistence.datasets_tbl.update_one({'CustomerID': customer_id, "DatasetID": dataset_id},
                                                   {"$set": {"TermFrequency": word_doc_dict}})
        logging.info("%s: Term Frequency vector generated successfully..." % RestService.timestamp())

    # Gets raw data for the incident
    @staticmethod
    def get_raw_text(customer_id, dataset_id, field_name, incident_number, type_of_tickets='closed'):
        string = ''
        
        if (field_mapping['Source_ITSM_Name'] == 'SNOW'):
            close_notes_field_name = field_mapping['Close_Notes_Field_Name']
        else:
            close_notes_field_name = 'close_notes'
        # print(string)
        if (type_of_tickets == 'closed'):
            string = MongoDBPersistence.training_tickets_tbl.find_one(
                {"CustomerID": customer_id, "DatasetID": dataset_id, ticket_id_field_name: incident_number},
                {'_id': 0, field_name: 1})
            print("String is", string)
        elif (type_of_tickets == 'open'):
            string = MongoDBPersistence.rt_tickets_tbl.find_one(
                {"CustomerID": customer_id, "DatasetID": dataset_id, ticket_id_field_name: incident_number},
                {'_id': 0, field_name: 1})
        return string[field_name]

    # Calculating tf-idf scores
    @staticmethod
    def getRelatedTickets_(customer_id, dataset_id, incident_number):
       
        if (field_mapping['Source_ITSM_Name'] == 'SNOW'):
            close_notes_field_name = field_mapping['Close_Notes_Field_Name']
        else:
            close_notes_field_name = 'close_notes'
        ## Getting the query from the user
        result_tfidf_dict = {}
        
        ()
        query = Recommendation.concatinateFields(customer_id, dataset_id, 'closed', incident_number)
        if (not query):
            logging.info("%s: Incident not found. Incident ID: %s" % (RestService.timestamp(), incident_number))
            return "Incient not found"
        query = query[0]

        query_list = [w.lower() for w in re.split(r'\W+', query['in_field']) if
                      w.isalpha() and len(w) > 1 and w.lower() \
                      not in stopwords_english]
        num_docs = MongoDBPersistence.training_tickets_tbl.find({"CustomerID": customer_id, "DatasetID": dataset_id},
                                                                {'_id': 0}).count()
        # query ~ word
        for query in query_list:
            term_frequencies = \
                MongoDBPersistence.datasets_tbl.find_one({"CustomerID": customer_id, "DatasetID": dataset_id},
                                                         {'_id': 0, "TermFrequency": 1})['TermFrequency']
            doc = term_frequencies.get(query, 0)
            if doc != 0:
                length = len(doc)
                for incident_number in doc.keys():
                    result_tfidf_dict[incident_number] = result_tfidf_dict.get(
                        incident_number, 0)
                    result_tfidf_dict[incident_number] += (
                            (1 + log(doc[incident_number])) * (log(num_docs / length) / log(10)))
        result_tfidf_indices = sorted(result_tfidf_dict.items(), key=lambda x: x[1], reverse=True)
        logging.info("%s: TFIDF weightage calculated successfully..." % RestService.timestamp())
        if (len(result_tfidf_indices) == 0):
            logging.info("%s: Sorry No matches found..." % (RestService.timestamp))
        else:
            logging.info("%s: Number of search results : %d" % (RestService.timestamp(), len(result_tfidf_indices)))
            
            customer_choices = [description_field_name, ticket_id_field_name, close_notes_field_name]
            logging.info("%s: customer_choices : %s" % (RestService.timestamp(), customer_choices))
            result_list = []
            for (index, tup) in enumerate(result_tfidf_indices):
                related_ticket = {}
                if index == 5:
                    break
                for field_name in customer_choices:
                    related_ticket[field_name] = Recommendation.get_raw_text(customer_id, dataset_id, field_name,
                                                                             tup[0])
                result_list.append(related_ticket)

        return json_util.dumps(result_list)

    @staticmethod
    def sentence_similarity(sent1, sent2, stopwords_english=None):
        if stopwords_english is None:
            stopwords_english = []
        """ Added ticket cleaning """
        clean_text = lambda x: "".join(re.sub(r'[^a-zA-Z]', ' ', w).lower() for w in sent2)
        sent_incident = clean_text(sent2)

        sent1 = [w.lower() for w in sent1]
        
        sent_incident_ticket = [w.lower() for w in sent_incident.split()]
        all_words = list(set(sent1 + sent_incident_ticket))

        vector1 = [0] * len(all_words)
        vector2 = [0] * len(all_words)
        for w in sent1:
            if w in stopwords_english:
                continue
            vector1[all_words.index(w)] += 1

        for w in sent_incident.split():
            if w in stopwords_english:
                continue
            vector2[all_words.index(w)] += 1
        return 1 - cosine_distance(vector1, vector2)

    @staticmethod
    def remove_first_principal_component(x):

        svd = TruncatedSVD(n_components=1, n_iter=7, random_state=0)
        svd.fit(x)
        pc = svd.components_
        xx = x - x.dot(pc.transpose()) * pc

        return xx

    @staticmethod
    def create_word2vec_model(descriptions, use_stop_list=False):
        """
        Arguments:

        Input:
        descriptions <List>: A list of descriptions of closed incidents

        Output:
        model <object>: A Word2Vec model trained on desciptions

        """
        descr_tokens = [sentence.tokens_without_stop if use_stop_list else sentence.tokens for sentence in
                        descriptions[:-1]]
        model = Word2Vec(descr_tokens, min_count=1)
        return model

    @staticmethod
    def similarity_measures(real_time_descr, descriptions, model, use_stop_list=False, freqs={}, a=0.001):
        """
        Arguments

        Input:
        incident_number <str>: Real Time ticket incident number to which related tickets needs to be found
        percentage_match <float>: The match percentage required

        Output:
        related_tickets <list>: List of incident number of related tickets

        """
        embeddings = []
        total_freq = sum(freqs.values())
        ticket_descr = real_time_descr
        ticket_descr = Sentence(ticket_descr)
        print(ticket_descr.normalized_sentence)

        tokens1 = ticket_descr.tokens_without_stop if use_stop_list else ticket_descr.tokens

        tokens1 = [token for token in tokens1 if token in model]

        weights1 = [a / (a + freqs.get(token, 0) / total_freq) for token in tokens1]

        embedding1 = np.average([model[token] for token in tokens1], axis=0, weights=weights1)
        for sentence in descriptions:
            tokens2 = sentence.tokens_without_stop if use_stop_list else sentence.tokens
            tokens2 = [token for token in tokens2 if token in model]

            weights2 = [a / (a + freqs.get(token, 0) / total_freq) for token in tokens2]

            embedding2 = np.average([model[token] for token in tokens2], axis=0, weights=weights2)

            embeddings.append(embedding1)
            embeddings.append(embedding2)

        embeddings = Recommendation.remove_first_principal_component(np.array(embeddings))
        sims = [cosine_similarity(embeddings[idx * 2].reshape(1, -1),
                                  embeddings[idx * 2 + 1].reshape(1, -1))[0][0]
                for idx in range(int(len(embeddings) / 2))]

        return sims

    @staticmethod
    def normalize_description(description):
        descr_english = " ".join(w for w in nltk.word_tokenize(description)
                                 if w.lower() in frequencies.keys())
        return descr_english

    @staticmethod
    def getRelatedTickets(customer_id, dataset_id, incident_number, algorithm_name):
        print("inside getRelatedTickets")

        logging.info("inside getRelatedTickets")

        if field_mapping['Source_ITSM_Name'] == 'SNOW':
            close_notes_field_name = field_mapping['Close_Notes_Field_Name']
        else:
            close_notes_field_name = 'close_notes'

        relatedClosedTickets = list(MongoDBPersistence.related_tickets_tbl.find(
            {"RT_Ticket_Number": incident_number, "Algorithm_name": algorithm_name},
            {'Related_ticket_info': 1, '_id': 0}))
        
        print("length of relatedclosed tickets in DB ", len(relatedClosedTickets))
        if len(relatedClosedTickets):
            relatedIncidentsList = relatedClosedTickets[0]['Related_ticket_info']
            related_results = []

            config = configparser.ConfigParser()
            config["DEFAULT"]['path'] = "config/"
            config.read(config["DEFAULT"]["path"] + "iia.ini")
            display_fields = config["ModuleConfig"]["displayFieldList"]
            display_field_list = display_fields.split(',')

            dict_select_fields = {}

            for field in display_field_list:
                dict_select_fields[field] = 1

            dict_select_fields.update({'_id': 0})
            for each in relatedIncidentsList:
                exam = list(
                    MongoDBPersistence.training_tickets_tbl.find({ticket_id_field_name: each}, dict_select_fields))
                dict_incident_fields = {}
                for field in display_field_list:
                    dict_incident_fields[field] = exam[0][field]
               
                related_results.append(dict_incident_fields)

            try:
                if close_notes_field_name in related_results[0].keys():
                    index = 0
                    for related_result in related_results:
                        related_results[index]['number'] = related_results[index][ticket_id_field_name]
                        related_results[index]['description'] = related_results[index][description_field_name]
                        related_results[index]['close_notes'] = related_results[index][close_notes_field_name]
                        index = index + 1
                    else:
                        index = 0
                        for related_result in related_results:
                            related_results[index]['number'] = related_results[index][ticket_id_field_name]
                            related_results[index]['description'] = related_results[index][description_field_name]
                            index = index + 1
            except Exception as e:
                print("Exception occurred in getRelatedTickets()", e)
                logging.info(
                    "%s exception occured in getRelatedTickets Method for a Incident -%s with exception details as - %s" % (
                    RestService.timestamp(), incident_number, str(e)))
                raise

            if len(related_results) > 0:
                return json_util.dumps(related_results)
            else:
                result = ["No Results Found"]
                return json_util.dumps(result)

        else:
            logging.info("Results not found in DataBase ,So we are baking  your results using Word2Vec.py")
            # calling getRelatedTickets in word2vec model/ Doc2vec model
            # we have to get from DB option
            search_alogorithm = algorithm_name
            print("algorithm selected is ", search_alogorithm)
            if (search_alogorithm == "word2Vec" or search_alogorithm == "doc2Vec" or search_alogorithm == "BERT"):
                related_results = RelatedSearch.getRelatedTickets(customer_id, dataset_id, incident_number,
                                                                  search_alogorithm)
                print("related_results using doc2vec_word2vec.py", related_results)
            else:
                # call text rank .py file
                related_results = TextRankSearch.getRelatedTickets(customer_id, dataset_id, incident_number)
                print("related_results using TextRankSearch.py", related_results)

            logging.info(f"related_results: {related_results}")

            try:
                if close_notes_field_name in related_results[0].keys():
                    index = 0
                    for related_result in related_results:
                        related_results[index]['number'] = related_results[index][ticket_id_field_name]
                        related_results[index]['description'] = related_results[index][description_field_name]
                        related_results[index]['close_notes'] = related_results[index][close_notes_field_name]
                        index = index + 1
                    else:
                        index = 0
                        for related_result in related_results:
                            related_results[index]['number'] = related_results[index][ticket_id_field_name]
                            related_results[index]['description'] = related_results[index][description_field_name]
                            index = index + 1
            except Exception as e:
                print("Exception occurred in getRelatedTickets()", e)
                logging.info(
                    "%s exception occured in getRelatedTickets Method for a Incident -%s with exception details as - %s" % (
                    RestService.timestamp(), incident_number, str(e)))
                raise

              

            logging.info(f"related_results: {related_results}")

            return json_util.dumps(related_results)


    @staticmethod
    def getRelatedOpenTickets(customer_id, dataset_id, incident_number):

        if field_mapping['Source_ITSM_Name'] == 'SNOW':
            close_notes_field_name = field_mapping['Close_Notes_Field_Name']
        else:
            close_notes_field_name = 'close_notes'

        relatedOpenTickets = list(MongoDBPersistence.related_tickets_tbl.find({"RT_Ticket_Number": incident_number},
                                                                              {'Related_Open_ticket_info': 1,
                                                                               '_id': 0}))
        logging.info(f"relatedOpenTickets: {relatedOpenTickets}")
        print("length of related open  tickets in DB ", len(relatedOpenTickets))
        if len(relatedOpenTickets):
            relatedOpenIncidentsList = relatedOpenTickets[0]['Related_Open_ticket_info']
            result_list = []
            for each in relatedOpenIncidentsList:
                exam = list(MongoDBPersistence.rt_tickets_tbl.find({ticket_id_field_name: each},
                                                                   {'_id': 0, ticket_id_field_name: 1,
                                                                    description_field_name: 1}))
                
                logging.info(f"exam: {exam}")
                result_list.append(
                    {'description': exam[0][description_field_name], 'number': exam[0][ticket_id_field_name]})

            

            if len(result_list) > 0:

              
                return json_util.dumps(result_list)

            else:

                
                result = ["No Results Found"]
                return json_util.dumps(result)
        else:
            logging.info("Realtime Results not found in DataBase ,So we are baking  your results using Word2Vec.py")
            
            config_values = MongoDBPersistence.configuration_values_tbl.find_one({}, {"Related_Tickets_Algorithm": 1,
                                                                                      "_id": 0})
            search_alogorithm = config_values['Related_Tickets_Algorithm']
            print("algorithm selected is ", search_alogorithm)
            if (search_alogorithm == "word2Vec" or search_alogorithm == "doc2Vec"):
                related_results = RelatedSearch.getRelatedOpenTickets(customer_id, dataset_id, incident_number,
                                                                      search_alogorithm)
                print("related_openresults using doc2vec_word2vec.py", related_results)
            else:
                # call text rank .py file
                related_results = TextRankSearch.getRelatedOpenTickets(customer_id, dataset_id, incident_number)
                print("related_open results using TextRankSearch.py", related_results)

            logging.info(f"related_results: {related_results}")

            index = 0
            for related_result in related_results:
                related_results[index]['number'] = related_results[index][ticket_id_field_name]
                related_results[index]['description'] = related_results[index][description_field_name]
                index = index + 1

            logging.info(f"related_results: {related_results}")

            return json_util.dumps(related_results)

    # Method to get count of all open tickets
    @staticmethod
    def getOpenTicketsCount(customer_id, dataset_id):
        
        ()
        if (field_mapping['Source_ITSM_Name'] == 'SNOW'):
            close_notes_field_name = field_mapping['Close_Notes_Field_Name']
        else:
            close_notes_field_name = 'close_notes'
        try:
            open_tickets_count = MongoDBPersistence.rt_tickets_tbl.find(
                {"CustomerID": customer_id, "DatasetID": dataset_id, status_field_name: "New",
                 "user_status": "Not Approved"}, {"_id": 0, ticket_id_field_name: 1}).count()
        except:
            logging.info("%s: Some error occured in Open Tickets Count" % RestService.timestamp())
            open_tickets_count = -1
        return json_util.dumps(open_tickets_count)

    @staticmethod
    def getOpenTickets(customer_id, dataset_id):
        
        ()
        if (field_mapping['Source_ITSM_Name'] == 'SNOW'):
            close_notes_field_name = field_mapping['Close_Notes_Field_Name']
        else:
            close_notes_field_name = 'close_notes'

        try:
            open_tickets = list(MongoDBPersistence.rt_tickets_tbl.find(
                {"CustomerID": customer_id, "DatasetID": dataset_id, status_field_name: "New",
                 "user_status": "Not Approved"},
                {"_id": 0, ticket_id_field_name: 1, description_field_name: 1, "opened_by": 1}))
        except:
            logging.info("%s: Some error occured in Open Tickets" % RestService.timestamp())
            open_tickets = ["failure"]

        if (len(open_tickets) == 0):
            open_tickets = ["failure"]
        return json_util.dumps(open_tickets)

    @staticmethod
    def getKnownErrors(customer_id, dataset_id, incident_number):
        try:
            known_errs = list(
                MongoDBPersistence.known_errors_tbl.find({"CustomerID": customer_id, "DatasetID": dataset_id}))
        except:
            print("No Known errors were found")
        if (known_errs):
            return json_util.dumps(known_errs)
        else:
            print("No Known errors were found")
            result = ["No known errors were found"]
            return json_util.dumps(result)

    @staticmethod
    def getRelatedKnowledgeArticles(customer_id, dataset_id, incident_number, algorithm_name):
        default_kb_source = MongoDBPersistence.configuration_values_tbl.find_one({"CustomerID": customer_id},
                                                                                 {"_id": 0, "DefaultKBSource": 1})
        ()
        if (default_kb_source):
            if (default_kb_source["DefaultKBSource"] == "ITSM"):
                print("defaultKB source is" + default_kb_source["DefaultKBSource"])
                return Recommendation.getSNOWRelatedKnowledgeArticles(customer_id, dataset_id, incident_number,
                                                                      algorithm_name)

            elif (default_kb_source["DefaultKBSource"] == "FileServer"):
                return Recommendation.getFileServerRelatedKnowledgeArticles(customer_id, dataset_id, incident_number,
                                                                            algorithm_name)
            elif (default_kb_source["DefaultKBSource"] == "Sharepoint"):
                # pass
                print('------------kb article is sharepoint ------------------')
                data = json.loads(request.form['word'])
                print("data coming from front end ", data)
                print("data type is ", type(data))
                return Recommendation.getSharePointRelatedKnowledgeArticles(data)
            else:
                logging.info(
                    "%s No Valid default KB source is present, please enter KB details again" % RestService.timestamp())
        else:
            logging.info("%s No default KB source was found, please enter KB details" % RestService.timestamp())
            return "Failure"

    @staticmethod
    def getSNOWRelatedKnowledgeArticles(customer_id, dataset_id, incident_number, search_alogorithm, source="SNOW"):
        cosine_value = []
      
        ()
        if (field_mapping['Source_ITSM_Name'] == 'SNOW'):
            close_notes_field_name = field_mapping['Close_Notes_Field_Name']
        else:
            close_notes_field_name = 'close_notes'

        try:
            config = configparser.ConfigParser()
            config["DEFAULT"]['path'] = "config/"
            config.read(config["DEFAULT"]["path"] + "iia.ini")
            input_fields = config["ModuleConfig"]["inputFieldList"]
           
            input_field_list = input_fields.split(',')

        except Exception as e:
            logging.error("Error occured: Hint: 'inputFieldList' is not defined in 'config/iia.ini' file.")
            input_field_list = [description_field_name]
            logging.info("%s Taking default as 'input_field_list = [description]'.." % RestService.timestamp())
        # print("Input Field List", input_field_list)

        try:
            logging.info("%s Inside getSNOWRelatedKnowledgeArticles" % RestService.timestamp())
            knowledge_article = list(
                MongoDBPersistence.knowledge_info_tbl.find({"CustomerID": customer_id, "Source": source}, {"_id": 0}))

            knowledge_df = pd.DataFrame(knowledge_article,
                                        columns=["KBNumber", "Summary", "Source", "CustomerID", "DatasetID"])
            if (not knowledge_df.empty):
                inci_desc = MongoDBPersistence.rt_tickets_tbl.find_one(
                    {"CustomerID": customer_id, "DatasetID": dataset_id, ticket_id_field_name: incident_number},
                    {"_id": 0, input_field_list[0]: 1})
                incident_description = inci_desc[input_field_list[0]]
                for input_field_ in input_field_list[1:]:
                    input_description = MongoDBPersistence.rt_tickets_tbl.find_one(
                        {"CustomerID": customer_id, "DatasetID": dataset_id, ticket_id_field_name: incident_number},
                        {"_id": 0, input_field_: 1})[input_field_]
                    incident_description += ' ' + input_description
                config_values = MongoDBPersistence.configuration_values_tbl.find_one({},
                                                                                     {"accuracy_percent": 1, "_id": 0})
                match_percentage = int(config_values['accuracy_percent']) / 100

                knowledge_df['Summary_cleaned'] = knowledge_df.Summary.apply(lambda x: " ".join(
                    re.sub(r'[^a-zA-Z]', ' ', w).lower() for w in x.split() if
                    re.sub(r'[^a-zA-Z]', ' ', w).lower() not in stopwords))
                KA_Sum_cleaned = knowledge_df.Summary_cleaned
                KA_Sum_cleaned = KA_Sum_cleaned.values.tolist()

                incident_description = re.sub('[^A-Za-z0-9]+', ' ', incident_description)
                ticket_descr = Sentence(incident_description)
                incident_ticket_descr = ticket_descr.normalized_sentence
                descriptions = [Sentence(s) for s in knowledge_df['Summary_cleaned']]
                if (search_alogorithm == 'word2Vec' or search_alogorithm == 'doc2Vec' or search_alogorithm == "BERT"):
                    if (search_alogorithm == 'BERT'):
                        clean_text1 = lambda x: " ".join(
                            re.sub(r'[^a-zA-Z]', ' ', w).lower() for w in incident_description.split() if
                            re.sub(r'[^a-zA-Z]', ' ', w).lower() not in stopwords)
                        clean_text = clean_text1(incident_description)
                        Trainedembeddings = sbert_model.encode(KA_Sum_cleaned)
                        query_vector = sbert_model.encode([clean_text])
                        pairwise_similarities = cosine_similarity(query_vector, Trainedembeddings)
                        similar_ix = (-pairwise_similarities[:3]).argsort()
                        related_articles_list = []
                        for i in range(2):
                            tick_row = similar_ix[0][i]
                            KBNumber = knowledge_df.iloc[tick_row]['KBNumber']
                            Summary = knowledge_df.iloc[tick_row]['Summary']
                            Score = pairwise_similarities[0][tick_row]
                            suggestion = {"KBNumber": KBNumber, "Summary": Summary, "Score": float(Score)}
                            related_articles_list.append(suggestion)
                    else:
                        if (search_alogorithm == 'word2Vec'):
                            Word2vecmodel = KAreleatedsearch.create_word2vec_model(descriptions)
                            sim_scores = KAreleatedsearch.similarity_measures(incident_ticket_descr, descriptions,
                                                                              Word2vecmodel, search_alogorithm,
                                                                              freqs=frequencies)
                           
                        else:
                            doc2Vecmodel = KAreleatedsearch.create_doc2vec_model(KA_Sum_cleaned)
                            sim_scores = KAreleatedsearch.similarity_measures(incident_ticket_descr, descriptions,
                                                                              doc2Vecmodel, search_alogorithm,
                                                                              freqs=frequencies)
                        knowledge_df['sims'] = sim_scores
                        print(knowledge_df.head())
                        knowledge_df.sort_values(by='sims', ascending=False, inplace=True)
                        related_articles_list = []
                        for i in range(3):
                            KBNumber = knowledge_df.iloc[i]['KBNumber']
                            Summary = knowledge_df.iloc[i]['Summary']
                            Score = knowledge_df.iloc[i]['sims']
                            suggestion = {"KBNumber": KBNumber, "Summary": Summary, "Score": float(Score)}
                            related_articles_list.append(suggestion)
                else:
                    for summary in range(len(knowledge_df['Summary'])):
                        cosine_value.append(Recommendation.sentence_similarity(knowledge_df['Summary'][summary].split(),
                                                                               incident_description,
                                                                               stopwords_english))
                    weightDict = {}
                    for index, item in enumerate(cosine_value):
                        if (item > match_percentage):
                            weightDict[index] = item
                    if (weightDict):
                        sorted_weights = sorted(weightDict.items(), key=itemgetter(1))[::-1]
                        ranked_knowledge_articles = [item[0] for item in sorted_weights]
                        ranked_KA_Score = [item[1] for item in sorted_weights]
                        ranked_KA_Score = [arr.tolist() for arr in ranked_KA_Score]

                        
                        try:
                            SELECTED_SENTENCES = sorted(ranked_knowledge_articles[:2])
                            SELECTED_ranked_KA_Score = sorted(ranked_KA_Score[:2])
                            SELECTED_ranked_KA_Score = SELECTED_ranked_KA_Score[::-1]
                        except:
                            logging.info("%s: Less than 2 articles found from RT table..." % RestService.timestamp())
                            SELECTED_SENTENCES = sorted(ranked_knowledge_articles)
                            SELECTED_ranked_KA_Score = sorted(ranked_KA_Score)
                            
                        related_articles = itemgetter(*SELECTED_SENTENCES)(knowledge_df['KBNumber'])
                        if (not isinstance(related_articles, tuple)):
                            related_articles = (related_articles,)
                        
                        related_articles_summary = itemgetter(*SELECTED_SENTENCES)(knowledge_df['Summary'])
                        if (not isinstance(related_articles_summary, tuple)):
                            related_articles_summary = (related_articles_summary,)
                        
                        related_articles_list = []
                        for KB_Number, Summary, Score in zip(related_articles, related_articles_summary,
                                                             SELECTED_ranked_KA_Score):
                            related_article = {}
                            related_article = {"KBNumber": KB_Number, "Summary": Summary, "Score": Score}
                            
                            related_articles_list.append(related_article)
                    else:
                        logging.info(
                            "%s No Results Found for Count Vectorization Related SNOW KB Articles with %s percent match in getSNOWRelatedKnowledgeArticles" % (
                                RestService.timestamp(), str(match_percentage * 100)))
                        result = ["No Results Found"]
                        return json_util.dumps(result)

                results_matched = len(related_articles_list)
                print(related_articles_list)
                if (results_matched == 0):
                    logging.info("%s: Sorry No matches found..." % RestService.timestamp())
                else:
                    logging.info("%s: Number of search results : %d" % (RestService.timestamp(), results_matched))
                    
                    return json_util.dumps(related_articles_list)
            else:
                
                logging.info(
                    "%s No Results Found for Related SNOW KB Articles in getSNOWRelatedKnowledgeArticles" % RestService.timestamp())
                result = ["No Results Found"]
                return json_util.dumps(result)

        except Exception as e:
            logging.info(" %s Error while getting related knowledge articles: %s " % (RestService.timestamp(), str(e)))
            result = ["No Results Found"]
            return json_util.dumps(result)

    # File Server Related Summary
    @staticmethod
    def getFileServerRelatedKnowledgeArticles(customer_id, dataset_id, incident_number, search_alogorithm):
        cosine_value = []
        
        ()
        try:
            config = configparser.ConfigParser()
            config["DEFAULT"]['path'] = "config/"
            config.read(config["DEFAULT"]["path"] + "iia.ini")
            input_fields = config["ModuleConfig"]["inputFieldList"]
            
            input_field_list = input_fields.split(',')
            KA_path = config["ModuleConfig"]["path"]
            
            print("Path is:", KA_path)
           

        except Exception as e:
            logging.error("Error occured: Hint: 'inputFieldList' is not defined in 'config/iia.ini' file.")
            input_field_list = [description_field_name]
            logging.info("%s Taking default as 'input_field_list = [description]'.." % RestService.timestamp())

        try:

            logging.info("%s Inside getFileServerRelatedKnowledgeArticles" % RestService.timestamp())
            knowledge_article = list(
                MongoDBPersistence.knowledge_info_tbl.find({"CustomerID": 1, "Source": "FileServer"}, {"_id": 0}))
            
            knowledge_df = pd.DataFrame(knowledge_article, columns=["CustomerID", "Name", "Summary", "Source"])
            
            if (not knowledge_df.empty):

                inci_desc = MongoDBPersistence.rt_tickets_tbl.find_one(
                    {"CustomerID": customer_id, "DatasetID": dataset_id, ticket_id_field_name: incident_number},
                    {"_id": 0, input_field_list[0]: 1})
                incident_description = inci_desc[input_field_list[0]]
                for input_field_ in input_field_list[1:]:
                    input_description = MongoDBPersistence.rt_tickets_tbl.find_one(
                        {"CustomerID": customer_id, "DatasetID": dataset_id, ticket_id_field_name: incident_number},
                        {"_id": 0, input_field_: 1})[input_field_]
                    incident_description += ' ' + input_description

                config_values = MongoDBPersistence.configuration_values_tbl.find_one({},
                                                                                     {"accuracy_percent": 1, "_id": 0})
                match_percentage = int(config_values['accuracy_percent']) / 100

                knowledge_df['Summary_cleaned'] = knowledge_df.Summary.apply(lambda x: " ".join(
                    re.sub(r'[^a-zA-Z]', ' ', w).lower() for w in x.split() if
                    re.sub(r'[^a-zA-Z]', ' ', w).lower() not in stopwords))
                KA_Sum_cleaned = knowledge_df.Summary_cleaned
                KA_Sum_cleaned = KA_Sum_cleaned.values.tolist()

                incident_description = re.sub('[^A-Za-z0-9]+', ' ', incident_description)
                ticket_descr = Sentence(incident_description)
                incident_ticket_descr = ticket_descr.normalized_sentence
                descriptions = [Sentence(s) for s in knowledge_df['Summary_cleaned']]
                if (search_alogorithm == 'word2Vec' or search_alogorithm == 'doc2Vec' or search_alogorithm == "BERT"):
                    if (search_alogorithm == 'BERT'):
                        clean_text1 = lambda x: " ".join(
                            re.sub(r'[^a-zA-Z]', ' ', w).lower() for w in incident_description.split() if
                            re.sub(r'[^a-zA-Z]', ' ', w).lower() not in stopwords)
                        clean_text = clean_text1(incident_description)
                        Trainedembeddings = sbert_model.encode(KA_Sum_cleaned)
                        query_vector = sbert_model.encode([clean_text])
                        pairwise_similarities = cosine_similarity(query_vector, Trainedembeddings)
                        similar_ix = (-pairwise_similarities[:3]).argsort()
                        related_articles_list = []
                        for i in range(2):
                            tick_row = similar_ix[0][i]
                            KBNumber = knowledge_df.iloc[tick_row]['KBNumber']
                            Summary = knowledge_df.iloc[tick_row]['Summary']
                            Score = pairwise_similarities[0][tick_row]
                            suggestion = {"KBNumber": KBNumber, "Summary": Summary, "Score": float(Score)}
                            related_articles_list.append(suggestion)
                    else:
                        if (search_alogorithm == 'word2Vec'):
                            Word2vecmodel = KAreleatedsearch.create_word2vec_model(descriptions)
                            sim_scores = KAreleatedsearch.similarity_measures(incident_ticket_descr, descriptions,
                                                                              Word2vecmodel, search_alogorithm,
                                                                              freqs=frequencies)
                        else:
                            doc2Vecmodel = KAreleatedsearch.create_doc2vec_model(KA_Sum_cleaned)
                            sim_scores = KAreleatedsearch.similarity_measures(incident_ticket_descr, descriptions,
                                                                              doc2Vecmodel, search_alogorithm,
                                                                              freqs=frequencies)
                        knowledge_df['sims'] = sim_scores
                        print(knowledge_df.head())
                        knowledge_df.sort_values(by='sims', ascending=False, inplace=True)
                        related_articles_list = []
                        for i in range(2):
                            KBNumber = knowledge_df.iloc[i]['Name']
                            Summary = knowledge_df.iloc[i]['Summary']
                            Score = knowledge_df.iloc[i]['sims']
                            suggestion = {"KBNumber": KBNumber, "Summary": Summary, "Score": float(Score),
                                          "Path": KA_path}
                            related_articles_list.append(suggestion)
                    
                else:
                    for summary in range(len(knowledge_df['Summary'])):
                        cosine_value.append(Recommendation.sentence_similarity(knowledge_df['Summary'][summary].split(),
                                                                               incident_description,
                                                                               stopwords_english))
                    weightDict = {}
                    for index, item in enumerate(cosine_value):
                        if (item > match_percentage):
                            weightDict[index] = item
                    if (weightDict):
                        sorted_weights = sorted(weightDict.items(), key=itemgetter(1))[::-1]
                        ranked_knowledge_articles = [item[0] for item in sorted_weights]
                        ranked_KA_Score = [item[1] for item in sorted_weights]
                        ranked_KA_Score = [arr.tolist() for arr in ranked_KA_Score]

                        
                        try:
                            SELECTED_SENTENCES = sorted(ranked_knowledge_articles[:2])
                            SELECTED_ranked_KA_Score = sorted(ranked_KA_Score[:2])
                            SELECTED_ranked_KA_Score = SELECTED_ranked_KA_Score[::-1]
                        except:
                            logging.info("%s: Less than 2 articles found from RT table..." % RestService.timestamp())
                            SELECTED_SENTENCES = sorted(ranked_knowledge_articles)
                            SELECTED_ranked_KA_Score = sorted(ranked_KA_Score)
                            
                        related_articles = itemgetter(*SELECTED_SENTENCES)(knowledge_df['Name'])
                        if (not isinstance(related_articles, tuple)):
                            related_articles = (related_articles,)
                        
                        related_articles_summary = itemgetter(*SELECTED_SENTENCES)(knowledge_df['Summary'])
                        if (not isinstance(related_articles_summary, tuple)):
                            related_articles_summary = (related_articles_summary,)
                        

                        related_articles_list = []

                        for key, Summary, Score in zip(related_articles, related_articles_summary,
                                                       SELECTED_ranked_KA_Score):
                            related_article = {}
                            related_article = {"KBNumber": key, "Summary": Summary, "Score": Score, "Path": KA_path}
                            
                            related_articles_list.append(related_article)
                        
                    else:
                        logging.info(
                            "%s No Results Found for Count vectorize Related Fileserver KB Articles with %s percent match in getFileServerRelatedKnowledgeArticles" % (
                                RestService.timestamp(), str(match_percentage * 100)))
                        result = ["No Results Found"]
                        return json_util.dumps(result)
                print(related_articles_list)
                results_matched = len(related_articles_list)
                if (results_matched == 0):
                    logging.info("%s: Sorry No matches found..." % RestService.timestamp())
                else:
                    logging.info("%s: Number of search results : %d" % (RestService.timestamp(), results_matched))
                   
                    return json_util.dumps(related_articles_list)
            else:
                
                logging.info(
                    "%s No Results Found for Related Fileserver KB Articles in getFileServerRelatedKnowledgeArticles" % RestService.timestamp())
                result = ["No Results Found"]
                return json_util.dumps(result)

        except Exception as e:
            logging.info(" %s Error while getting related knowledge articles: %s " % (RestService.timestamp(), str(e)))
            result = ["No Results Found"]
            return json_util.dumps(result)

    
    @staticmethod
    def display_resolution(customer_id, dataset_id, incident_number, tab_name, cloud_type, algorithm_name):
        ()
        if (field_mapping['Source_ITSM_Name'] == 'SNOW'):
            close_notes_field_name = field_mapping['Close_Notes_Field_Name']
        else:
            close_notes_field_name = 'close_notes'
        
        with open('data/stopwords.csv', 'r') as readFile:
            reader = csv.reader(readFile)
            list1 = list(reader)
        
            ENGLISH_STOP_WORDS = list1[0]
            readFile.close()

            try:
                config = configparser.ConfigParser()
                config["DEFAULT"]['path'] = "config/"
                config.read(config["DEFAULT"]["path"] + "iia.ini")
                display_fields = config["ModuleConfig"]["displayFieldList"]
                display_field_list = display_fields.split(',')
            
            except Exception as e:
                logging.error("Error occured: Hint: 'assignmentModule' is not defined in 'config/iia.ini' file.")
                display_field_list = [description_field_name, ticket_id_field_name, close_notes_field_name]
                logging.info("Taking default as 'displayFieldList = [description, number , close_notes]'..")

        word_cloud_field = display_field_list[0]
        resolution = {}
        resolution_ticket = {}
        resolution_errors = {}
        resolution_knowledge = {}

        resolution_ticket[word_cloud_field] = []
        resolution_errors[word_cloud_field] = []
        resolution_knowledge[word_cloud_field] = []
        resolution[word_cloud_field] = []

        # Get Related Ticket related Info
        jsonresult = getRelatedTickets(customer_id, dataset_id, incident_number, algorithm_name)
        decoded = json.loads(jsonresult)
        if (decoded[0] == "No Results Found"):
            logging.info("%s: No Related Tickets were found with more than 0.80 match" % RestService.timestamp())
        else:
            for record in decoded:
                resolution_ticket[word_cloud_field].append(record[word_cloud_field])

        # Get KnownError related Info
        jsonKnownErrors = getKnownErrors(customer_id, dataset_id, incident_number)
        decodedKnownOutput = json.loads(jsonKnownErrors)
        if (decodedKnownOutput[0] == "No known errors were found"):
            logging.info("%s: No Known Errors were found" % RestService.timestamp())
        
        else:
            for rec in decodedKnownOutput:
                resolution_errors[word_cloud_field].append(rec[word_cloud_field])

        # Get Knowledge related Info
        try:
            jsonKnowledgeArticles = Recommendation.getKnowledgeArticlesSummary(customer_id, dataset_id, incident_number)
            if (jsonKnowledgeArticles == "Failure"):
                logging.info("%s: No Related Knowledge Articles were found" % RestService.timestamp())
            else:
                
                decodedKnowledge = json.loads(jsonKnowledgeArticles)
                for rec in decodedKnowledge:
                    resolution_knowledge[word_cloud_field].append(rec['Summary'])
            
        except Exception as e:
            print(str(e))
            logging.info(
                "%s Error occured in display resolution...." % RestService.timestamp())  # giving it an empty summary if no knowledge article is present in DB

        clean_sentences = []
        resolution[word_cloud_field] = resolution_ticket[word_cloud_field] + resolution_errors[word_cloud_field] + \
                                       resolution_knowledge[word_cloud_field]
        if (len(resolution[word_cloud_field]) != 0):
            for sentence in resolution[word_cloud_field]:
                clean_sentence = re.sub("[^a-zA-Z]", " ", sentence)
                clean_sentence = clean_sentence.lower()
                clean_sentence = clean_sentence.split()
                clean_sentence = [word for word in clean_sentence if not word in set(ENGLISH_STOP_WORDS)]
                clean_sentence = " ".join(clean_sentence)
                clean_sentences.append(clean_sentence)

            if (cloud_type == 'Unigram'):
                clean_words_list = []
                for sentence in clean_sentences:
                    for word in sentence.split():
                        clean_words_list.append(word)
                clean_words_dict = dict(Counter(clean_words_list))

                
                sorted_dict = sorted(clean_words_dict.items(), key=lambda x: x[1])
                
                words_dict = {}
                for i in range(len(sorted_dict) - 1, -1, -1):
                    words_dict.update({sorted_dict[i][0]: sorted_dict[i][1]})
                if words_dict:
                    resp = json_util.dumps(words_dict)
                    logging.info('%s: Generated json based on Clean Words Frequency...' % RestService.timestamp())
                else:
                    resp = 'failure'
                    logging.info('%s: Not able to generate JSON some error occured...' % RestService.timestamp())
                return resp

            elif (cloud_type == 'Bigram'):
                clean_words_list_bigram = []
                # top 30 bigrams printing
                number_of_words = 100
                for i in range(0, len(clean_sentences) - 1):
                    bigram_list = TextBlob(clean_sentences[i]).ngrams(2)
                    for j in range(0, len(bigram_list) - 1):
                        biagram = bigram_list[j][0] + " " + bigram_list[j][1]
                        clean_words_list_bigram.append(biagram)
                clean_word_dict_bigram = dict(Counter(clean_words_list_bigram))
                
                if number_of_words > len(clean_word_dict_bigram):
                    number_of_words = len(
                        clean_word_dict_bigram)  # also send a default value of number of words from front end
                sorted_dict_bigram = sorted(clean_word_dict_bigram.items(), key=lambda x: x[1])
                words_dict_bigram = {}
                for i in range(len(sorted_dict_bigram) - 1, len(sorted_dict_bigram) - number_of_words - 1, -1):
                    words_dict_bigram.update({sorted_dict_bigram[i][0]: sorted_dict_bigram[i][1]})
                if words_dict_bigram:
                    resp = json_util.dumps(words_dict_bigram)
                    
                    logging.info('%s: Generated json based on Clean Words Frequency...' % RestService.timestamp())
                else:
                    resp = ''
                    logging.info('%s: Not able to generate JSON some error occured...' % RestService.timestamp())
                return resp
        else:
            logging.info('%s: Resolution for given ticket number is not found.' % RestService.timestamp())
            return 'Failure'

    @staticmethod
    def getNER(customer_id, dataset_id, incident_number):
        # Fetch Named Entities from DB and show in NER Infromation
        print("Inside NER")
        named_entities = MongoDBPersistence.predicted_tickets_tbl.find_one(
            {"CustomerID": customer_id, "DatasetID": dataset_id, ticket_id_field_name: incident_number},
            {"_id": 0, "NamedEntities": 1})
        print("named_entities : ", named_entities)
        if (named_entities):
           
            required_entities_lcase = ['Email', 'Server', 'Issue', 'Number', 'Applications', 'Platform', 'Person',
                                       'Gpe', 'LeaveApplication', 'Finance']
            try:
                config = configparser.ConfigParser()
                config["DEFAULT"]['path'] = "config/"
                config.read(config["DEFAULT"]["path"] + "iia.ini")
                required_entities = config["ModuleConfig"]["required_entities"]
                required_entities_list = required_entities.split(',')
                required_entities_list = required_entities_list + required_entities_lcase
                logging.info(f"required_entities_list: {required_entities_list}")
            except:
                logging.error(
                    "%s: Error occured: Hint: 'required_entities' is not defined in 'config/iia.ini' file.")
                required_entities_list = ['NAME', 'NUMBER', 'EMAIL', 'SERVER', 'ISSUE', 'GPE', 'PERSON',
                                          'TRANSACTION_CODE', 'TABLE']
                logging.info(
                    "%s Taking default as 'required_entities = ['NAME', 'PHONE', 'EMAIL', 'APPLICATION', 'TRANSACTION_CODE', 'TABLE']'.." % RestService.timestamp())
            resp = []

            for entity in named_entities['NamedEntities']:
                if (entity['Entity'] in required_entities_list):
                    temp = {}
                    temp['Entity'] = entity['Entity']
                    temp['Value'] = entity['Value']
                    resp.append(temp)
            resp = json_util.dumps(resp)

        else:
            logging.info("%s: Not able to find Named Entities for the ticket number %s " % (
                RestService.timestamp(), incident_number))
            resp = 'failure'

        return resp

    @staticmethod
    def updateNER(customer_id, dataset_id, incident_number):
        try:
            ()
            updated_NER = request.get_json()
            logging.info('%s: Trying to update Entity Values' % RestService.timestamp())
            MongoDBPersistence.predicted_tickets_tbl.update_one(
                {"CustomerID": customer_id, "DatasetID": dataset_id, ticket_id_field_name: incident_number},
                {"$set": {"NamedEntities": updated_NER}})
            return 'success'
        except Exception as e:
            logging.error('failed to update entity value for incident %s, cause: %s' % (str(e), incident_number))
        return 'failure'

    @staticmethod
    def getAttachmentsData(incident_number):
        try:
            ()
            attachments_data = []
            attachments_data = MongoDBPersistence.attachment_tbl.find_one({ticket_id_field_name: incident_number})
            print(attachments_data)
            resp = json_util.dumps(attachments_data)
            return resp
        except Exception as e:
            logging.error('failure to get attachments %s, cause: %s' % (str(e), incident_number))
        return 'failure'

    @staticmethod
    def getSharePointRelatedKnowledgeArticles(data):

        searchtext = data
        print("inside method", searchtext)
        json_url = MongoDBPersistence.configuration_values_tbl.find_one({}, {"SharepointUrl": 1, "_id": 0})
        
        site_url = json_url['SharepointUrl']
        office365url = site_url.split('.com')
        office365url = office365url[0] + '.com'
       
        try:
            ()
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            authcookie = Office365(office365url, username='username',
                                   password='password').GetCookies()
            site = Site(site_url, authcookie=authcookie, verify_ssl=True, ssl_version='TLSv1')
            data_list = site.List('KB_Articles')
      
            related_article_links = []
            for i in range(len(searchtext)):
                fields = ['Title', 'ID', 'URL Path']
                query = {'Where': [('Contains', 'Title', searchtext[i])]}
              
                sp_data = data_list.GetListItems(fields=fields, query=query)
                
                print('sharepoint list items data :', sp_data)
                # trying to get ids from form above filtered results and put ithem in list and use them while getting attachements
                iD_list = []
                for x in sp_data:
                    for y in x['ID']:
                        iD_list.append(y)
                print(iD_list)

                for i in iD_list:
                    link = data_list.GetAttachmentCollection(i)
                    for i in range(len(link)):
                        related_article_links.append(link[i])
                        
            result = related_article_links
            
            if len(result) == 0:
                result = ["No Results Found in sharepoint for the respective ticket "]
                return json_util.dumps(result)
                site.close
            else:
                return json_util.dumps(result)
                site.close

        except Exception as e:
            logging.info(" %s Error while getting related knowledge articles: %s " % (RestService.timestamp(), str(e)))
            print("Exception in sharepoint connect....", e)
            result = ["No Results Found,please try again "]
            return json_util.dumps(result)
            site.close

    @staticmethod
    def update_rt_chosen_algorithm(algorithm_name):
        try:
            ()
            logging.info('Trying to update configuration_values_tbl with new Algorithm name')
            MongoDBPersistence.configuration_values_tbl.update_one({}, {
                '$set': {'Related_Tickets_Algorithm': algorithm_name}}, upsert=True)
            return 'success'
        except Exception as e:
            logging.error('%s' % str(e))
        return 'failure'
