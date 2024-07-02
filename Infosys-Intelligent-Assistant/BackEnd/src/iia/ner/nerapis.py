__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

import gensim
import numpy as np
from gensim import corpora, models
from iia.persistence.mongodbpersistence import MongoDBPersistence
from iia.restservice import RestService
from bson import json_util
from flask import request
import pandas as pd
import re
from iia.utils.log_helper import get_logger
import re

import gensim
import numpy as np
import pandas as pd
from bson import json_util
from flask import request
from gensim import corpora, models

from iia.persistence.mongodbpersistence import MongoDBPersistence
from iia.restservice import RestService
from iia.utils.log_helper import get_logger

logging = get_logger(__name__)
app = RestService.getApp()

@app.route("/api/nerEnableStatus/<regex_status>/<db_status>/<spacy_status>", methods=["PUT"])
def nerEnableStatus(regex_status, db_status, spacy_status):
    print("nerEnableStatus")
    return NER.nerEnableStatus(regex_status, db_status, spacy_status)


@app.route('/api/ner/saveNerTags', methods=['PUT'])
def saveNerTags():
    return NER.saveNerTags()


@app.route("/api/ner/getAnnotationTags", methods=['GET'])
def getAnnotationTags():
    print("getAnnotationTags")
    return NER.getAnnotationTags()


@app.route("/api/ner/getTopicTags", methods=['GET'])
def getTopicTags():
    print("getTopicTags")
    return NER.getTopicTags()


@app.route("/api/ner/saveTopicTags", methods=['PUT'])
def saveTopicTags():
    return NER.saveTopicTags()


class NER(object):
    '''
    classdocs
    '''

    def __init__(self, params):
        '''
        Constructor
        '''

    @staticmethod
    def nerEnableStatus(regex_status, db_status, spacy_status):
        try:

            MongoDBPersistence.assign_enable_tbl.update_one({}, {
                '$set': {"regex_enabled": regex_status, "db_enabled": db_status, 'spacy_enabled': spacy_status}},
                                                            upsert=True)
        except Exception as e:
            logging.info('%s: Error innerEnableStatus: %s' % (RestService.timestamp, str(e)))
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
    def saveNerTags():
        try:

            ner_doc = request.get_json()
            print('------ner doc-----------', ner_doc)
            MongoDBPersistence.annotation_mapping_tbl.delete_many({})
            MongoDBPersistence.annotation_mapping_tbl.insert(ner_doc)
            return 'success'
        except Exception as e:
            logging.error('In saveNerTags : %s' % str(e))
        return 'failure'

    @staticmethod
    def getTopicTags():

        np.random.seed(2018)
        inc_description_list = list(MongoDBPersistence.training_tickets_tbl.find({}, {'_id': 0, 'description': 1}))
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
                    result.append(token)

            return result

        processed_docs = documents['description'].map(preprocess)
        dictionary = gensim.corpora.Dictionary(processed_docs)
        dictionary.filter_extremes(no_below=15, no_above=0.5, keep_n=100000)
        bow_corpus = [dictionary.doc2bow(doc) for doc in processed_docs]
        tfidf = models.TfidfModel(bow_corpus)
        corpus_tfidf = tfidf[bow_corpus]
        try:

            lda_model = gensim.models.LdaMulticore(bow_corpus, num_topics=10, id2word=dictionary, passes=2, workers=2)
            lda_model_tfidf = gensim.models.LdaMulticore(corpus_tfidf, num_topics=10, id2word=dictionary, passes=2,
                                                         workers=4)
        except Exception as e:
            logging.info('Exception in NER topics')
            print("Exception in NER topics")

        topic_list = {}
        for idx, topic in lda_model_tfidf.print_topics(-1):
            listwords = re.findall(r"\"[a-zA-Z0-9]+\"", topic)
            listwords = [i.strip('\"') for i in listwords]
            topic_list['topic' + str(idx)] = listwords

        return json_util.dumps({'response': topic_list})

    @staticmethod
    def saveTopicTags():
        try:

            ner_doc = request.get_json()
            print('------save TopicTags-----------', ner_doc)
            MongoDBPersistence.annotation_mapping_tbl.delete_many({})
            MongoDBPersistence.annotation_mapping_tbl.insert(ner_doc)
            return 'success'
        except Exception as e:
            logging.error('In saveTopicTags : %s' % str(e))
        return 'failure'
