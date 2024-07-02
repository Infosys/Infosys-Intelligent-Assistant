__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

import pandas as pd
import gensim
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.stem.porter import *
import numpy as np
import nltk
from gensim import corpora, models
import re
from pprint import pprint
from iia.itsm.adapter import ITSMAdapter
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from iia.persistence.mongodbpersistence import MongoDBPersistence
from iia.persistence.mappingpersistence import MappingPersistence
from iia.masterdata.customers import CustomerMasterData
from iia.restservice import RestService
from nltk.cluster.util import cosine_distance
from iia.masterdata.resources import ResourceMasterData
from iia.itsm.servicenow import ServiceNow
from pathlib import Path
import joblib
from bson import json_util
from flask import request
from flask import make_response
import json
import pandas as pd
import re
import csv
import importlib
import configparser
import subprocess
from iia.incident.incidenttraining import IncidentTraining
import os
import requests
from flask import session
from iia.masterdata.assignment import Assignment
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
from iia.masterdata.datasets import DatasetMasterData
import spacy
import io
from iia.utils.log_helper import get_logger, log_setup

logging = get_logger(__name__)

app = RestService.getApp()
from datetime import datetime
import time

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


@app.route("/api/nerEnableStatus/<regex_status>/<db_status>/<spacy_status>/<int:customer_id>/<chosen_team>",methods=["PUT"])
def nerEnableStatus(regex_status, db_status, spacy_status, customer_id, chosen_team):
    #print("nerEnableStatus")
    return NER.nerEnableStatus(regex_status, db_status, spacy_status, customer_id, chosen_team)


@app.route("/api/twilioalert/<twilio_enabled>", methods=["PUT"])
def TwilioEnableStatus(twilio_enabled):
    return NER.TwilioEnableStatus(twilio_enabled)


@app.route("/api/alertEnableStatus/<sms_status>/<whatsapp_status>/<call_status>/<ms_teams_enabled>", methods=["PUT"])
def alertEnableStatus(sms_status, whatsapp_status, call_status, ms_teams_enabled):
    return NER.alertEnableStatus(sms_status, whatsapp_status, call_status, ms_teams_enabled)


@app.route('/api/ner/saveNerTags/<new_tag>', methods=['PUT'])
def saveNerTags(new_tag):
    return NER.saveNerTags(new_tag)


@app.route("/api/ner/getAnnotationTags", methods=['GET'])
def getAnnotationTags():
    return NER.getAnnotationTags()


@app.route("/api/ner/numberOfTopics", methods=['GET'])
def numberOfTopics():
    return NER.numberOfTopics()


@app.route("/api/ner/getTopicTags/<int:num_of_topics>", methods=['GET'])
def getTopicTags(num_of_topics):
    return NER.getTopicTags(num_of_topics)


@app.route("/api/ner/exportnerconfigtocsv", methods=['PUT'])
def exportNerConfigtoCSV():
    return NER.exportNerConfigtoCSV()


@app.route("/api/ner/saveTopicTags", methods=['PUT'])
def saveTopicTags():
    return NER.saveTopicTags()


@app.route('/api/ner/saveKnowledgeInfo', methods=['POST'])
def saveKnowledgeInfo():
    return NER.saveKnowledgeInfo()


@app.route('/api/ner/getKnowledgeInfoColumnNames', methods=['POST'])
def getKnowledgeInfoColumnNames():
    return NER.getKnowledgeInfoColumnNames()


@app.route('/api/ner/getKnowledgeInfo', methods=['GET'])
def getKnowledgeInfo():
    return NER.getKnowledgeInfo()


@app.route('/api/ner/getKnowledgeInfo/<number>/<entity_name>', methods=['GET'])
def getKnowledgeEntityInfo(number, entity_name):
    return NER.getKnowledgeEntityInfo(number, entity_name)


@app.route('/api/ner/deleteKGInfoDetails', methods=['DELETE'])
def deleteKGInfoDetails():
    return NER.deleteKGInfoDetails()


class NER(object):
    '''
    classdocs
    '''

    def __init__(self, params):
        '''
        Constructor
        '''

    @staticmethod
    def nerEnableStatus(regex_status, db_status, spacy_status, customer_id, chosen_team):
        try:
            dataset_id_all = MongoDBPersistence.teams_tbl.find_one({"CustomerID": customer_id, "TeamName": chosen_team},
                                                                   {"DatasetID": 1, "_id": 0})

            dataset_id = dataset_id_all['DatasetID']

            MongoDBPersistence.assign_enable_tbl.update_one({'DatasetID': dataset_id},
                                                            {'$set': {"regex_enabled": regex_status,
                                                                      "db_enabled": db_status,
                                                                      'spacy_enabled': spacy_status}}, upsert=True)
        except Exception as e:
            logging.info('%s: Error: %s' % (RestService.timestamp, str(e)))
            return 'Failure'
        return 'Success'

    @staticmethod
    def alertEnableStatus(sms_status, whatsapp_status, call_status, ms_teams_enabled):
        try:
            MongoDBPersistence.assign_enable_tbl.update_one({}, {
                '$set': {"sms_enabled": sms_status, "whatsapp_enabled": whatsapp_status, 'call_enabled': call_status,
                         "msteams_enabled": ms_teams_enabled}}, upsert=True)
        except Exception as e:
            logging.info('%s: Error: %s' % (RestService.timestamp, str(e)))
            return 'Failure'
        return 'Success'

    @staticmethod
    def TwilioEnableStatus(twilio_enabled):
        try:
            MongoDBPersistence.assign_enable_tbl.update_one({}, {'$set': {"twilio_enabled": twilio_enabled}},
                                                            upsert=True)
        except Exception as e:
            logging.info('%s: Error: %s' % (RestService.timestamp, str(e)))
            return 'Failure'
        return 'Success'

    @staticmethod
    def getAnnotationTags():
        try:

            ner_docs = MongoDBPersistence.annotation_mapping_tbl.find({}, {'_id': 0})
            return json_util.dumps({'response': ner_docs})
        except Exception as e:
            logging.error('In getAnnotationTags : %s' % str(e))
        return json_util.dumps({'response': 'failure'})

    @staticmethod
    def saveNerTags(new_tag):
        try:

            if (new_tag == 'true'):
                new_items = request.get_json()
                l = list(MongoDBPersistence.annotation_mapping_tbl.find({}, {"entity": 1, '_id': 0}))
                existing_list = list(map(lambda d: d['entity'], l))
                insert_new = []
                for item in new_items:
                    if item['entity'] in existing_list:
                        existing_words = MongoDBPersistence.annotation_mapping_tbl.find_one({'entity': item['entity']},
                                                                                            {"description": 1,
                                                                                             '_id': 0})['description']
                        existing_words.extend(item["description"])
                        new_words_list = list(set(existing_words))

                        MongoDBPersistence.annotation_mapping_tbl.update_one({'entity': item['entity']},
                                                                             {"$set": {"description": new_words_list}},
                                                                             upsert=False)
                    else:
                        insert_new.append(item)

                if insert_new:
                    MongoDBPersistence.annotation_mapping_tbl.insert_many(insert_new)

                return 'success'

            else:
                ner_doc = request.get_json()
                MongoDBPersistence.annotation_mapping_tbl.delete_many({})
                MongoDBPersistence.annotation_mapping_tbl.insert(ner_doc)
                return 'success'
        except Exception as e:
            logging.error('In saveNerTags : %s' % str(e))
        return 'failure'

    @staticmethod
    def numberOfTopics():
        annot_mapng_lst = list(MongoDBPersistence.annotation_mapping_tbl.find({}, {'_id': 0}))
        topic_list = []
        for annot_dict in annot_mapng_lst:
            if 'topic' in annot_dict['entity']:
                print(annot_dict['entity'], annot_dict['description'])
                topic_list.append(annot_dict)
        return json_util.dumps({'response': len(topic_list)})

    @staticmethod
    def getTopicTags(num_of_topics):
        try:
            annot_mapng_lst = list(MongoDBPersistence.annotation_mapping_tbl.find({}, {'_id': 0}))
            topic_list = []
            for annot_dict in annot_mapng_lst:
                if 'topic' in annot_dict['entity']:
                    print(annot_dict['entity'], annot_dict['description'])
                    topic_list.append(annot_dict)

            print(topic_list)
            if len(topic_list) >= num_of_topics:
                print('true')
                return json_util.dumps({'response': topic_list[:num_of_topics]})
            else:
                print('false')
                np.random.seed(2018)
                inc_description_list = list(
                    MongoDBPersistence.training_tickets_tbl.find({}, {'_id': 0, 'description': 1}))
                tickets = []

                for item in inc_description_list:
                    line = item['description']
                    tickets.append(line)

                data_text = pd.DataFrame(tickets)
                data_text['index'] = data_text.index
                documents = data_text

                documents.columns = ['description', 'index']

                def preprocess(text):
                    result = []
                    for token in gensim.utils.simple_preprocess(text):
                        if token not in gensim.parsing.preprocessing.STOPWORDS and len(token) > 3:
                            # result.append(lemmatize_stemming(token))
                            result.append(token)

                    return result

                processed_docs = documents['description'].map(preprocess)

                dictionary = gensim.corpora.Dictionary(processed_docs)

                dictionary.filter_extremes(no_below=15, no_above=0.5, keep_n=100000)

                bow_corpus = [dictionary.doc2bow(doc) for doc in processed_docs]
                tfidf = models.TfidfModel(bow_corpus)
                corpus_tfidf = tfidf[bow_corpus]

                lda_model = gensim.models.LdaModel(bow_corpus, num_topics=num_of_topics, id2word=dictionary, passes=2)
                lda_model_tfidf = gensim.models.LdaModel(corpus_tfidf, num_topics=num_of_topics, id2word=dictionary,
                                                         passes=2)

                topic_list = []
                for idx, topic in lda_model_tfidf.print_topics(-1):
                    listwords = re.findall(r"\"[a-zA-Z0-9]+\"", topic)
                    listwords = [i.strip('\"') for i in listwords]
                    topic_doc = {}
                    topic_doc['entity'] = 'topic' + str(idx)
                    topic_doc['description'] = listwords
                    topic_list.append(topic_doc)
                return json_util.dumps({'response': topic_list})
        except Exception as e:
            logging.error('%s' % str(e))
        return ({'response': 'failure'})

    @staticmethod
    def saveTopicTags():
        try:
            annot_mapng_lst = list(MongoDBPersistence.annotation_mapping_tbl.find({}, {'_id': 0}))
            if (annot_mapng_lst):
                new_items = request.get_json()
                l = list(MongoDBPersistence.annotation_mapping_tbl.find({}, {"entity": 1, '_id': 0}))
                existing_list = list(map(lambda d: d['entity'], l))
                insert_new = []
                for item in new_items:
                    if item['entity'] in existing_list:
                        existing_words = MongoDBPersistence.annotation_mapping_tbl.find_one({'entity': item['entity']},
                                                                                            {"description": 1,
                                                                                             '_id': 0})['description']
                        existing_words.extend(item["description"])
                        new_words_list = list(set(existing_words))
                        MongoDBPersistence.annotation_mapping_tbl.update_one({'entity': item['entity']},
                                                                             {"$set": {"description": new_words_list}},
                                                                             upsert=False)
                    else:
                        insert_new.append(item)

                if insert_new:
                    MongoDBPersistence.annotation_mapping_tbl.insert_many(insert_new)
                return 'success'
            else:
                ner_doc = request.get_json()
                MongoDBPersistence.annotation_mapping_tbl.insert(ner_doc)
                return 'success'
        except Exception as e:
            logging.error('In saveTopicTags : %s' % str(e))
        return 'failure'

    @staticmethod
    def exportNerConfigtoCSV():
        try:

            ner_doc = request.get_json()
            csv_data_format = []
            csv_data_format.append(ner_doc[0].keys())
            for flattened_record in ner_doc:
                csv_data_format.append(list(flattened_record.values()))
            si = StringIO()
            cw = csv.writer(si)
            cw.writerows(csv_data_format)
            output = make_response(si.getvalue())
            output.headers["Content-Disposition"] = "attachment; filename=export.csv"
            output.headers["Content-type"] = "text/csv"
            logging.info('%s: s have been exported successfully into a csv.' % RestService.timestamp())
            return output
        except Exception as e:
            logging.error("%s failed in exporting to CSV " % RestService.timestamp())
            return "failure"

    @staticmethod
    def saveKnowledgeInfo():
        try:

            file = request.files['knowledgeInfoDetails']
            mapping_details = request.form.get('mappedHeaders')
            mapping_details = json.loads(mapping_details)
            mapping_dict = {}
            for item in mapping_details:
                mapping_dict[item["iia_column"]] = item["account_column"]
            if not file:
                return "No file"
            elif (not '.csv' in str(file)):
                return "Upload csv file."
            stream = io.StringIO(file.stream.read().decode("latin-1"), newline=None)
            csv_input = csv.reader(stream)
            df_data = []

            for row in csv_input:
                df_data.append(row)
            headers = df_data.pop(0)
            headers = [c for c in headers]

            df = pd.DataFrame(df_data, columns=headers)
            new_df = pd.DataFrame()
            for key, val in mapping_dict.items():
                new_df[key] = df[val]

            json_str = new_df.to_json(orient='records')
            json_data = json.loads(json_str)
            if mapping_dict:
                MongoDBPersistence.knowledge_entity_tbl.update_one({"Mapping": True}, {
                    "$set": {"Mapping": True, "MappingIiaList": list(mapping_dict.keys()),
                             "AccountToIiaColumnMapping": mapping_dict}}, upsert=True)
                MongoDBPersistence.knowledge_entity_tbl.insert_many(json_data)
                return 'success'
            else:
                return 'No Mapping Information'
        except Exception as e:
            logging.error('%s' % str(e))
            return 'failure'

    @staticmethod
    def getKnowledgeInfo():
        try:

            knowledge_info_lst = list(
                MongoDBPersistence.knowledge_entity_tbl.find({'Mapping': {'$exists': False}}, {'_id': 0}))
            return json_util.dumps({'response': knowledge_info_lst})
        except Exception as e:
            logging.error('%s' % str(e))
        return json_util.dumps({'response': 'failure'})

    @staticmethod
    def getKnowledgeEntityInfo(number, entity_name):
        try:

            knowledge_entity_info = MongoDBPersistence.predicted_tickets_tbl.find_one({'number': number},
                                                                                      {'_id': 0, "KgInfo": 1})
            if knowledge_entity_info:
                response = knowledge_entity_info['KgInfo'][0][entity_name]
            else:
                response = 'No Information'
            return json_util.dumps({'response': response})
        except Exception as e:
            logging.error('%s' % str(e))
        return json_util.dumps({'response': 'failure'})

    @staticmethod
    def getKnowledgeInfoColumnNames():
        try:

            print("getKnowledgeInfoColumnNames started")
            file = request.files['knowledgeInfoDetails']
            if not file:
                print("No file")
                return "No file"
            elif (not '.csv' in str(file)):
                print("Upload csv file.")
                logging.info('%s: Upload csv file.' % RestService.timestamp())
                return "Upload csv file."

            stream = io.StringIO(file.stream.read().decode("latin-1"), newline=None)
            csv_input = csv.reader(stream)
            df_data = []

            for row in csv_input:
                df_data.append(row)
            account_column_headers = df_data.pop(0)
            mapping_list = MongoDBPersistence.knowledge_entity_tbl.find_one({"Mapping": True},
                                                                            {"MappingIiaList": 1, '_id': 0})
            if mapping_list:
                iia_column_headers = mapping_list['MappingIiaList']
            else:
                iia_column_headers = ["Server", "Application", "Contact Name", "Platforms", "Service Name"]
                logging.info(
                    "%s 'MappingIiaList' is not defined Taking default as list as  [Server, Application, Contact Name, Platforms, Service Name ]'.." % RestService.timestamp())
            response = {}
            if account_column_headers:
                response['account_column_headers'] = account_column_headers
                response['iia_column_headers'] = iia_column_headers
            else:
                print("No Headers in the file")
                logging.info('%s: No No Headers in the Uploaded file' % RestService.timestamp())
                response['account_column_headers'] = 'No Information'
            return json_util.dumps({'response': response})
        except Exception as e:
            print("Erroe:", e)
            logging.error('%s' % str(e))
        return json_util.dumps({'response': 'failure'})

    @staticmethod
    def deleteKGInfoDetails():
        try:

            MongoDBPersistence.knowledge_entity_tbl.delete_many({})
        except Exception as e:
            logging.error('%s' % str(e))
        return 'failure'
