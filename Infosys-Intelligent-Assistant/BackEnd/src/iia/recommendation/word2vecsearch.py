__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

import configparser
import csv
import json
import os
from pathlib import Path

import nltk
import numpy as np
import pandas as pd
from gensim.models import Word2Vec
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from nltk.tokenize import word_tokenize
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from iia.environ import *

from iia.restservice import RestService
from iia.utils.log_helper import get_logger

bertmodel_path = "./models/bert_base"
model_data_dir = './models/Related_Ticket_Model'

if not os.path.exists(model_data_dir):
    os.makedirs(model_data_dir)

if not os.path.exists(bertmodel_path):
    os.makedirs(bertmodel_path)

bertmodel = bertmodel_path + "/pytorch_model.bin"
bertmodel_check = Path(bertmodel)
if bertmodel_check.is_file():
    logging.info("%s: BERT model presented in model/xlnet directory" % (RestService.timestamp))
    sbert_model = SentenceTransformer(bertmodel_path)
else:
    logging.info("%s: BERT pretrained Model not presented in the directory" % (RestService.timestamp))
    logging.info("%s: BERT Pretrained model downloading..." % (RestService.timestamp))
    model = SentenceTransformer('bert-base-nli-mean-tokens')
    model.save("./models/bert_base")
    logging.info("%s: BERT pretrained model saved in model/bert_base directory" % (RestService.timestamp))
    bertmodel_path = "./models/bert_base"
    sbert_model = SentenceTransformer(bertmodel_path)

logging = get_logger(__name__)
PATH_TO_FREQUENCIES_FILE = './data/frequencies.tsv'

with open('data/stopwords.csv', 'r') as readFile:
    reader = csv.reader(readFile)
    list1 = list(reader)
    stopwords_english = list1[0]
    readFile.close()


def read_tsv(f):
    frequencies = {}
    with open(f) as tsv:
        tsv_reader = csv.reader(tsv, delimiter='\t')
        for row in tsv_reader:
            frequencies[row[0]] = int(row[1])

    return frequencies


frequencies = read_tsv(PATH_TO_FREQUENCIES_FILE)

class Sentence:

    def __init__(self, sentence):
        self.raw = sentence
        normalized_sentence = sentence.replace("‘", "'").replace("’", "'")
        # Doing only for english vocabulary words
        normalized_sentence = " ".join(w for w in nltk.word_tokenize(normalized_sentence) \
                                       if w.lower() in frequencies.keys())
        self.normalized_sentence = normalized_sentence
        self.tokens = [t.lower() for t in nltk.word_tokenize(normalized_sentence)]
        self.tokens_without_stop = [t for t in self.tokens if t not in stopwords_english]


class RelatedSearch:
    def __init__(self):
        pass

    @staticmethod
    def concatinateFields(customer_id, dataset_id, type_of_tickets, incident_number=0):
       
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

        input_df = pd.DataFrame()
        try:
            if (type_of_tickets == 'closed'):
                if (incident_number == 0):  
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
            logging.error('%s: Error occured in Concatinating input fields in vectorSearchModel: %s' % (
            RestService.timestamp(), str(e)))
            return 'failure'
            raise
        input_df['in_field'] = ''
        for field in input_field_list:
            input_df['in_field'] += input_df[field] + ' '
        json_str = input_df.to_json(orient='records')
        json_data = json.loads(json_str)
        return json_data

    @staticmethod
    def remove_first_principal_component(x):

        svd = TruncatedSVD(n_components=1, n_iter=7, random_state=0)
        svd.fit(x)
        pc = svd.components_
        xx = x - x.dot(pc.transpose()) * pc

        return xx

    @staticmethod
    def create_doc2vec_model(descriptions, use_stop_list=False):
        """
        Arguments:

        Input:
        descriptions <List>: A list of descriptions 
        Output:
        model <object>: A Doc2Vec model trained on desciptions

        """
        print("inside create_doc2vec_model")
        documents = [TaggedDocument(words=word_tokenize(_d.lower()), tags=[str(i)]) for i, _d in
                     enumerate(descriptions)]
        model = Doc2Vec(dm=0, min_count=1, vector_size=100, workers=1, window=3, hs=0, alpha=0.03, min_alpha=0.0025)
        model.build_vocab(documents)

        return model

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
    def similarity_measures(real_time_descr, descriptions, model, search_alogorithm, use_stop_list=False, freqs={},
                            a=0.001):
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

        if (search_alogorithm == "word2Vec"):
            print("inside word2vec_model 3")
            tokens1 = [token for token in tokens1 if token in model.wv.key_to_index]
        else:
            print("inside doc2vec_model 3")
            tokens1 = [token for token in tokens1 if token in model.wv.key_to_index]

        weights1 = [a / (a + freqs.get(token, 0) / total_freq) for token in tokens1]

        embedding1 = np.average([model.wv[token] for token in tokens1], axis=0, weights=weights1)
        for sentence in descriptions:
            tokens2 = sentence.tokens_without_stop if use_stop_list else sentence.tokens
            if (search_alogorithm == "word2Vec"):
               
                tokens2 = [token for token in tokens2 if token in model.wv.key_to_index]
            else:
                
                tokens2 = [token for token in tokens2 if token in model.wv.key_to_index]
            if len(tokens2) != 0:
                weights2 = [a / (a + freqs.get(token, 0) / total_freq) for token in tokens2]
                embedding2 = np.average([model.wv[token] for token in tokens2], axis=0, weights=weights2)
                
            else:
                weights2 = [1]
                embedding2 = -embedding1
           

            embeddings.append(embedding1)
            embeddings.append(embedding2)

        embeddings = RelatedSearch.remove_first_principal_component(np.array(embeddings))
        sims = [cosine_similarity(embeddings[idx * 2].reshape(1, -1),
                                  embeddings[idx * 2 + 1].reshape(1, -1))[0][0]
                for idx in range(int(len(embeddings) / 2))]

        return sims

    @staticmethod
    def normalize_description(description):
        try:

            
            if not description or description is None:
                print('The text to be tokenized is a None Type, so defaulting it to empty string')
                description = ''
            descr_english = " ".join(w for w in nltk.word_tokenize(description)
                                     if w.lower() in frequencies.keys())
            return descr_english
        except Exception as e:
            print("Exception in normalize description using vectorsearch..", e)
            logging.info("%s Exception occured in normalize description using vectorsearch.." % RestService.timestamp())
            raise
        
        return ""

    @staticmethod
    def get_raw_text(customer_id, dataset_id, field_name, incident_number, type_of_tickets='closed'):

        try:

            string = ''
            field_mapping = MappingPersistence.get_mapping_details(customer_id)
            ticket_id_field_name = field_mapping['Ticket_ID_Field_Name']

            if (type_of_tickets == 'closed'):
                string = MongoDBPersistence.training_tickets_tbl.find_one(
                    {"CustomerID": customer_id, "DatasetID": dataset_id, ticket_id_field_name: incident_number},
                    {'_id': 0, field_name: 1})
                # print("String is", string)
            elif (type_of_tickets == 'open'):
                string = MongoDBPersistence.rt_tickets_tbl.find_one(
                    {"CustomerID": customer_id, "DatasetID": dataset_id, ticket_id_field_name: incident_number},
                    {'_id': 0, field_name: 1})
            return string[field_name]
        except Exception as e:
            print("Key not found in Tbl Incident Training while working with get_raw_text in vectorSearchmodel",
                  field_name)
            logging.info(
                " %s Key not found in Tbl Incident Training while working with get_raw_text in vectorSearchmodel- %s" % (
                RestService.timestamp(), str(e)))
            raise

    @staticmethod
    def getRelatedTickets(customer_id, dataset_id, incident_number, search_alogorithm):
        field_mapping = MappingPersistence.get_mapping_details(customer_id)
        group_field_name = field_mapping['Group_Field_Name']
        ticket_id_field_name = field_mapping['Ticket_ID_Field_Name']
        status_field_name = field_mapping['Status_Field_Name']
        description_field_name = field_mapping['Description_Field_Name']
        try:
            print("inside word2vec get related Tickets")
            if field_mapping['Source_ITSM_Name'] == 'SNOW':
                close_notes_field_name = field_mapping['Close_Notes_Field_Name']
            else:
                close_notes_field_name = 'close_notes'

            num_tickets = 5  # hardcoded value for related tickets
            incident_list = pd.DataFrame(RelatedSearch.concatinateFields(customer_id, dataset_id, 'closed'))
            query = RelatedSearch.concatinateFields(customer_id, dataset_id, 'closed', incident_number)
            datasetname = MongoDBPersistence.teams_tbl.find_one({'DatasetID': dataset_id}, {"TeamName": 1})
            datasetname = datasetname['TeamName']
            df = pd.DataFrame(incident_list)
            df['Normalized_Description'] = df['in_field'].apply(RelatedSearch.normalize_description)
            df['Normalized_Description'].replace('', np.nan, inplace=True)
            df.dropna(inplace=True)
            df.reset_index(drop=True, inplace=True)

            descriptions = [Sentence(s) for s in df['Normalized_Description']]
            if (search_alogorithm == 'BERT'):
                print("inside BERT")
                BERTembedding_dir = model_data_dir + "/" + datasetname + "_CloseTicketBERT.npy"
                BERTemb = Path(BERTembedding_dir)
                if BERTemb.is_file():
                    print("BERT embedding presented")
                    Trainedembeddings = np.load(BERTembedding_dir)
                else:
                    print("BERT Model creation")
                    clean_tickets = df.Normalized_Description
                    Trainedembeddings = sbert_model.encode(clean_tickets)
                    np.save(model_data_dir + '/' + datasetname + "_CloseTicketBERT.npy", Trainedembeddings)
                tf_idf = TfidfVectorizer()
                tf_idf.fit(df['in_field'])
                real_time_descr = query[0]['in_field']
                non_english_rt = " ".join(word for word in nltk.word_tokenize(real_time_descr)
                                          if word.lower() not in frequencies.keys())
                real_time_tfidf = tf_idf.transform([non_english_rt])

                clean_query = RelatedSearch.normalize_description(real_time_descr)
                query_vector = sbert_model.encode([clean_query])

                pairwise_similarities = cosine_similarity(query_vector, Trainedembeddings)
                similar_ix = (-pairwise_similarities[:3]).argsort()

                ticket_details = []
                for i in range(5):
                    tick_row = similar_ix[0][i]
                    ticket_num = df.iloc[tick_row][ticket_id_field_name]
                    ticket_des = df.iloc[tick_row][description_field_name]
                    in_field = df.iloc[tick_row]['in_field']
                    metrics = pairwise_similarities[0][tick_row]
                    Normalized_Description = df.iloc[tick_row]['Normalized_Description']
                    suggestion = {ticket_id_field_name: ticket_num, "sims": float(metrics), "closed_tickets": in_field,
                                  "Normalized_Description": Normalized_Description}
                    ticket_details.append(suggestion)
                similarity_df = pd.DataFrame(ticket_details)
            else:
                if (search_alogorithm == "word2Vec"):
                    print("inside word2vec 1")
                    model = RelatedSearch.create_word2vec_model(descriptions)
                elif (search_alogorithm == "doc2Vec"):
                    print("inside doc2vec 2")
                    logging.info("%s Selected  Doc2Vec MOdel for related Search  " % RestService.timestamp())
                    model = RelatedSearch.create_doc2vec_model(df['Normalized_Description'])
                else:
                    print("check Configuration table")

                tf_idf = TfidfVectorizer()
                tf_idf.fit(df['in_field'])
                real_time_descr = query[0]['in_field']
                non_english_rt = " ".join(word for word in nltk.word_tokenize(real_time_descr)
                                          if word.lower() not in frequencies.keys())
                real_time_tfidf = tf_idf.transform([non_english_rt])
                sims = RelatedSearch.similarity_measures(real_time_descr, descriptions, model, search_alogorithm,
                                                         freqs=frequencies)
                print("Length of Similarity Vector ", len(sims))
                similarity_df = pd.DataFrame()
                similarity_df[ticket_id_field_name] = df[ticket_id_field_name]
                print("Length of Similarity DataFrame: ", len(similarity_df))
                similarity_df['sims'] = sims
                similarity_df['closed_tickets'] = df['in_field']
                similarity_df['Normalized_Description'] = df['Normalized_Description']
                similarity_df['real_time'] = [real_time_descr] * len(similarity_df)
                similarity_df.sort_values(by='sims', ascending=False, inplace=True)
                similarity_df = similarity_df.iloc[0:20]

            similarity_df['Non_English_Description'] = [
                " ".join(word for word in nltk.word_tokenize(descr) if word not in english_descr.split())
                for descr, english_descr in
                zip(similarity_df['closed_tickets'], similarity_df['Normalized_Description'])]

            similarity_df['Non_English_Similarity'] = [cosine_similarity(tf_idf.transform([non_english_descr]),
                                                                         real_time_tfidf)[0][0] for non_english_descr in
                                                       similarity_df['Non_English_Description']]

            similarity_df.sort_values(by='Non_English_Similarity', ascending=False, inplace=True)

            config_values = MongoDBPersistence.configuration_values_tbl.find_one({}, {"accuracy_percent": 1, "_id": 0})
            match_percentage = int(config_values['accuracy_percent']) / 100
            try:
                config = configparser.ConfigParser()
                config["DEFAULT"]['path'] = "config/"
                config.read(config["DEFAULT"]["path"] + "iia.ini")
                display_fields = config["ModuleConfig"]["displayFieldList"]
                display_field_list = display_fields.split(',')
                
            except Exception as e:
                logging.error("Error occured: Hint: 'displayFieldList' is not defined in 'config/iia.ini' file.")
                display_field_list = [description_field_name, ticket_id_field_name, close_notes_field_name]
                logging.info("Taking default as 'displayFieldList = [description, number , close_notes]'..")

            result_list = []
            for i in range(len(similarity_df)):
                ticket_number = similarity_df.iloc[i][ticket_id_field_name]
                if similarity_df.iloc[i]['Non_English_Similarity'] == 0:
                    rel_weight = similarity_df.iloc[i]['sims']
                    if rel_weight > match_percentage:
                        related_ticket = {}
                        for field_name in display_field_list:
                            related_ticket[field_name] = RelatedSearch.get_raw_text(customer_id, dataset_id, field_name,
                                                                                    ticket_number)
                        
                        result_list.append(related_ticket)

                else:
                    rel_weight = (similarity_df.iloc[i]['sims'] + similarity_df.iloc[i]['Non_English_Similarity']) / 2
                    rel_weight = similarity_df.iloc[i]['sims']
                    if rel_weight > match_percentage:
                        related_ticket = {}
                        for field_name in display_field_list:
                            related_ticket[field_name] = RelatedSearch.get_raw_text(customer_id, dataset_id, field_name,
                                                                                    ticket_number)
                        
                        result_list.append(related_ticket)

                if len(result_list) == num_tickets:
                    break

            if len(result_list) > 0:
                return result_list

            else:
                result = []
                return result
        except Exception as e:
            result = []
            print("Exception occurred in vector_getRelatedTickets()", e)
            logging.info(
                "%s exception occured in vector_getRelatedTickets Method for a Incident -%s with exception details as - %s" % (
                RestService.timestamp(), incident_number, str(e)))
            return result
            raise

    @staticmethod
    def getRelatedOpenTickets(customer_id, dataset_id, incident_number, search_alogorithm):
        try:

            if field_mapping['Source_ITSM_Name'] == 'SNOW':
                close_notes_field_name = field_mapping['Close_Notes_Field_Name']
            else:
                close_notes_field_name = 'close_notes'

            num_tickets = 5  # hardcoded value for related tickets
            related_concatenated_tickets = RelatedSearch.concatinateFields(customer_id, dataset_id, 'open')
            if (related_concatenated_tickets == 'failure'):
                result = ['No Results Found']
                return result
            else:
                incident_list = pd.DataFrame(related_concatenated_tickets)
            query = RelatedSearch.concatinateFields(customer_id, dataset_id, 'open', incident_number)
            if query == 'failure':
                result = ['No Results Found']
                return result

            df = pd.DataFrame(incident_list)
            df['Normalized_Description'] = df['in_field'].apply(RelatedSearch.normalize_description)
            df['Normalized_Description'].replace('', np.nan, inplace=True)
           
            df.dropna(inplace=True)
            df.reset_index(drop=True, inplace=True)

            descriptions = [Sentence(s) for s in df['Normalized_Description']]

            if (search_alogorithm == 'BERT'):
                print("inside BERT")
                BERTembedding_dir = model_data_dir + "/OpenTicketBERT.npy"
                BERTemb = Path(BERTembedding_dir)
                if BERTemb.is_file():
                    print("BERT embedding presented")
                    Trainedembeddings = np.load(BERTembedding_dir)
                else:
                    print("BERT Model creation")
                    clean_tickets = df.Normalized_Description
                    Trainedembeddings = sbert_model.encode(clean_tickets)
                    np.save(model_data_dir + '/OpenTicketBERT.npy', Trainedembeddings)
                tf_idf = TfidfVectorizer()
                tf_idf.fit(df['in_field'])
                real_time_descr = query[0]['in_field']
                non_english_rt = " ".join(word for word in nltk.word_tokenize(real_time_descr)
                                          if word.lower() not in frequencies.keys())
                real_time_tfidf = tf_idf.transform([non_english_rt])

                clean_query = RelatedSearch.normalize_description(real_time_descr)
                query_vector = sbert_model.encode([clean_query])

                pairwise_similarities = cosine_similarity(query_vector, Trainedembeddings)
                similar_ix = (-pairwise_similarities[:3]).argsort()

                ticket_details = []
                for i in range(5):
                    tick_row = similar_ix[0][i]
                    ticket_num = df.iloc[tick_row][ticket_id_field_name]
                    ticket_des = df.iloc[tick_row][description_field_name]
                    in_field = df.iloc[tick_row]['in_field']
                    metrics = pairwise_similarities[0][tick_row]
                    Normalized_Description = df.iloc[tick_row]['Normalized_Description']
                    suggestion = {"number": ticket_num, "sims": float(metrics), "closed_tickets": in_field,
                                  "Normalized_Description": Normalized_Description}
                    ticket_details.append(suggestion)
                similarity_df = pd.DataFrame(ticket_details)
            else:
                if (search_alogorithm == "word2Vec"):
                    print("inside word2vec 1")
                    model = RelatedSearch.create_word2vec_model(descriptions)
                elif (search_alogorithm == "doc2Vec"):
                    print("inside doc2vec 2")
                    logging.info("%s Selected  Doc2Vec MOdel for related Search  " % RestService.timestamp())
                    model = RelatedSearch.create_doc2vec_model(df['Normalized_Description'])
                else:
                    print("check Configuration table")

                tf_idf = TfidfVectorizer()
                tf_idf.fit(df['in_field'])
                real_time_descr = query[0]['in_field']
                non_english_rt = " ".join(word for word in nltk.word_tokenize(real_time_descr)
                                          if word.lower() not in frequencies.keys())
                real_time_tfidf = tf_idf.transform([non_english_rt])
                sims = RelatedSearch.similarity_measures(real_time_descr, descriptions, model, search_alogorithm,
                                                         freqs=frequencies)
                print("Length of Similarity Vector ", len(sims))
                similarity_df = pd.DataFrame()
                similarity_df[ticket_id_field_name] = df[ticket_id_field_name]
                print("Length of Similarity DataFrame: ", len(similarity_df))
                similarity_df['sims'] = sims
                similarity_df['closed_tickets'] = df['in_field']
                similarity_df['Normalized_Description'] = df['Normalized_Description']
                similarity_df['real_time'] = [real_time_descr] * len(similarity_df)
                similarity_df.sort_values(by='sims', ascending=False, inplace=True)
                similarity_df = similarity_df.iloc[0:20]

            similarity_df['Non_English_Description'] = [
                " ".join(word for word in nltk.word_tokenize(descr) if word not in english_descr.split())
                for descr, english_descr in
                zip(similarity_df['closed_tickets'], similarity_df['Normalized_Description'])]

            similarity_df['Non_English_Similarity'] = [cosine_similarity(tf_idf.transform([non_english_descr]),
                                                                         real_time_tfidf)[0][0] for non_english_descr in
                                                       similarity_df['Non_English_Description']]

            similarity_df.sort_values(by='Non_English_Similarity', ascending=False, inplace=True)

            config_values = MongoDBPersistence.configuration_values_tbl.find_one({}, {"accuracy_percent": 1, "_id": 0})
            match_percentage = int(config_values['accuracy_percent']) / 100
            try:
                config = configparser.ConfigParser()
                config["DEFAULT"]['path'] = "config/"
                config.read(config["DEFAULT"]["path"] + "iia.ini")
                display_fields = config["ModuleConfig"]["displayFieldList_Open"]
                display_field_list = display_fields.split(',')
              
            except Exception as e:
                logging.error("Error occured: Hint: 'displayFieldList' is not defined in 'config/iia.ini' file.")
                display_field_list = [description_field_name, ticket_id_field_name]
                logging.info("Taking default as 'displayFieldList = [description, number ]'..")

            result_list = []
            for i in range(len(similarity_df)):
                ticket_number = similarity_df.iloc[i][ticket_id_field_name]
                if similarity_df.iloc[i]['Non_English_Similarity'] == 0:
                    rel_weight = similarity_df.iloc[i]['sims']
                    if rel_weight > match_percentage:
                        related_ticket = {}
                        if (ticket_number == incident_number):
                            continue
                        for field_name in display_field_list:
                            related_ticket[field_name] = RelatedSearch.get_raw_text(customer_id, dataset_id, field_name,
                                                                                    ticket_number, 'open')
                       

                        result_list.append(related_ticket)
                else:
                    rel_weight = (similarity_df.iloc[i]['sims'] + similarity_df.iloc[i]['Non_English_Similarity']) / 2
                    rel_weight = similarity_df.iloc[i]['sims']
                    if rel_weight > match_percentage:
                        related_ticket = {}
                        if (ticket_number == incident_number):
                            continue
                        for field_name in display_field_list:
                            related_ticket[field_name] = RelatedSearch.get_raw_text(customer_id, dataset_id, field_name,
                                                                                    ticket_number, 'open')
                       
                        result_list.append(related_ticket)

                if len(result_list) == num_tickets:
                    break

            if len(result_list) > 0:
                return result_list

            else:
                result = ["No Results Found"]
                return result
        except Exception as e:
            print("Exception occurred in vector_getRelatedOpenTickets()", e)
            logging.info(
                "%s exception occured in vector_getRelatedOpenTickets Method for a Incident -%s with exception details as - %s" % (
                RestService.timestamp(), incident_number, str(e)))
            raise
