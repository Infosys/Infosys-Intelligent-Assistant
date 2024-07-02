__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""
from gensim.models.keyedvectors import KeyedVectors
import configparser
import csv
import json
import re
from collections import Counter
from math import log
from operator import itemgetter
import nltk
import numpy as np
import pandas as pd
import urllib3
from bson import json_util
from flask import request
from gensim.models import Word2Vec
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
from iia.restservice import RestService
from iia.utils.log_helper import get_logger
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from nltk.tokenize import word_tokenize


logging = get_logger(__name__)

stopword_path = './data/stopwords.csv'
PATH_TO_FREQUENCIES_FILE = './data/frequencies.tsv'

with open(stopword_path, 'r') as fh:
    stopwords = fh.read().split(",")

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

class KAreleatedsearch:

    def __init__(self):
        pass

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
    def create_doc2vec_model(descriptions, use_stop_list=False):
        
        """
        Arguments:

        Input:
        descriptions <List>: A list of descriptions 
        Output:
        model <object>: A Doc2Vec model trained on desciptions

        """
        print("inside create_doc2vec_model")
        documents = [TaggedDocument(words=word_tokenize(_d.lower()), tags=[str(i)]) for i, _d in enumerate(descriptions)]
        model = Doc2Vec(dm=0, min_count=1, vector_size=100, workers=1, window =3, hs = 0, alpha= 0.03,min_alpha=0.0025)
        model.build_vocab(documents)
        return model
   
    @staticmethod
    def similarity_measures(real_time_descr, descriptions, model,search_alogorithm, use_stop_list=False, freqs={}, a=0.001):
        """
        Arguments

        Input:
        incident_number <str>: Real Time ticket incident number to which related tickets needs to be found
        percentage_match <float>: The match percentage required

        Output:
        related_tickets <list>: List of incident number of related tickets

        """
        print("Similarity check")
        logging.info("Similarity check")
        embeddings = []
        trained_embeddings = []
        total_freq = sum(freqs.values())
        ticket_descr = real_time_descr
        ticket_descr = Sentence(ticket_descr)
        print(ticket_descr.normalized_sentence)

        tokens1 = ticket_descr.tokens_without_stop if use_stop_list else ticket_descr.tokens

        if(search_alogorithm=="word2Vec"):
            tokens1 = [token for token in tokens1 if token in model.wv.key_to_index]
        else:
            tokens1 = [token for token in tokens1 if token in model.wv.key_to_index]

        weights1 = [a / (a + freqs.get(token, 0) / total_freq) for token in tokens1]
        embedding1 = np.average([model.wv[token] for token in tokens1], axis=0, weights=weights1)
        if(search_alogorithm=="word2Vec"):
            for sentence in descriptions:
                print("word2vec Embedding Calculation")
                tokens2 = sentence.tokens_without_stop if use_stop_list else sentence.tokens
                tokens2 = [token for token in tokens2 if token in model.wv.key_to_index]
                if len(tokens2) != 0:
                    weights2 = [a / (a + freqs.get(token, 0) / total_freq) for token in tokens2]
                    embedding2 = np.average([model.wv[token] for token in tokens2], axis=0, weights=weights2)
                else:
                    weights2 = [1]
                    embedding2 = -embedding1
                trained_embeddings.append(embedding2)
            trained_embeddings.append(embedding1)
        else:
            for sentence in descriptions:
                print("Doc2vec Embedding Calculation")
                tokens2 = sentence.tokens_without_stop if use_stop_list else sentence.tokens
                tokens2 = [token for token in tokens2 if token in model.wv.key_to_index]
                if len(tokens2) != 0:
                    weights2 = [a / (a + freqs.get(token, 0) / total_freq) for token in tokens2]
                    embedding2 = np.average([model.wv[token] for token in tokens2], axis=0, weights=weights2)
                else:
                    weights2 = [1]
                    embedding2 = -embedding1
                trained_embeddings.append(embedding2)
            trained_embeddings.append(embedding1)
        trained_embeddings = KAreleatedsearch.remove_first_principal_component(np.array(trained_embeddings))
        sims1 = [cosine_similarity(trained_embeddings[int(len(trained_embeddings)-1)].reshape(1, -1),
                                trained_embeddings[idx].reshape(1, -1))[0][0]
                for idx in range(int(len(trained_embeddings)))]
        sims1 = sims1[:-1]
        
        return sims1