__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""
import pysnow
from servicenow import ServiceNow
from servicenow import Connection
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
import re
from intent.recommendation.recommendationmodel import Recommendation
from intent.persistence.mongodbpersistence import MongoDBPersistence
from intent.persistence.mappingpersistence import MappingPersistence
#import logging
from bson import json_util
from intent.restservice import RestService
import pandas as pd
from intent.environ import *
from intent.utils.log_helper import get_logger, log_setup
import os
from bs4 import BeautifulSoup
from summarizer import Summarizer,TransformerSummarizer
from transformers import XLNetModel, XLNetTokenizer
from pathlib import Path


logging = get_logger(__name__)
app = RestService.getApp()

xlnet = './models/xlnet/'

if not os.path.exists(xlnet):
    os.makedirs(xlnet)

model_dir = xlnet + "/pytorch_model.bin"
xlnetpath = Path(model_dir)
if xlnetpath.is_file():
    logging.info("%s: KA Summarizer XLNET model presented in model/xlnet directory" %(RestService.timestamp))
    xlnet_model = TransformerSummarizer(transformer_type="XLNet",transformer_model_key=xlnet)
else:
    logging.info("%s: KA Summarizer XLNET not presented" %(RestService.timestamp))
    logging.info("%s: XLNET Pretrained model is downloading" %(RestService.timestamp))
    model = XLNetModel.from_pretrained("xlnet-base-cased")
    model.save_pretrained(xlnet)
    token = XLNetTokenizer.from_pretrained("xlnet-base-cased")
    token.save_pretrained(xlnet)
    logging.info("%s: KA Summarizer XLNET XLNET model downloaded and saved in model/XLNET directory" %(RestService.timestamp))
    xlnet = './models/xlnet/'
    xlnet_model = TransformerSummarizer(transformer_type="XLNet",transformer_model_key=xlnet)

@app.route("/api/getKnowledgeArticle/<int:customer_id>", methods = ['GET'])
def getKnowledgeArticle(customer_id):
    return KnowledgeArticle.getKnowledgeArticle(customer_id)

class KnowledgeArticle(object):
    def __init__(self):
        pass
    #Fetching Knowledge Articles from SNOW
    @staticmethod
    def getKnowledgeArticle(customer_id):

        # field_mapping = MappingPersistence.get_mapping_details(customer_id)
        # group_field_name = field_mapping['Group_Field_Name']
        # ticket_id_field_name = field_mapping['Ticket_ID_Field_Name']
        # status_field_name = field_mapping['Status_Field_Name']
        # description_field_name = field_mapping['Description_Field_Name']
        # TAG_RE = re.compile(r'<[^>]+>')

        try:
            logging.info("%s: Fetching Knowledge articles from Source = SNOW..... "%RestService.timestamp())
            instance = MongoDBPersistence.customer_tbl.find_one({"CustomerID":1}, {'SNOWInstance':1, '_id':0})
            if (instance):
                username = MongoDBPersistence.customer_tbl.find_one({"CustomerID":1}, {'SNOWUserName':1, '_id':0})
                password = MongoDBPersistence.customer_tbl.find_one({"CustomerID":1}, {'SNOWPassword':1, '_id':0})
                KnowledgeArticle.client = pysnow.Client(instance=instance['SNOWInstance'], user=username['SNOWUserName'], password=password['SNOWPassword'])
                KnowledgeArticle.client.parameters.display_value = True
                KnowledgeArticle.client.parameters.exclude_reference_link = True
                KnowledgeArticle.KBTable = KnowledgeArticle.client.resource(api_path='/table/kb_knowledge')
                #fetching all knowledge articles which have workflow state as published
                knowledgearticles = KnowledgeArticle.KBTable.get(query={'workflow_state':'published'})
                # print("Outside IF", knowledgearticles)
                success_flag = 0
                if (knowledgearticles):
                    # print("Inside IF")
                    #cleaning the articles removing the HTML tags from the articles
                    articles_list = []
                    articles_df = pd.DataFrame()
                    for article in knowledgearticles.all():
                        # print("Article Type", type(article))
                        article_dict = {}
                        # print("Inside for loop")
                        if (article['text']):
                            KBNumber = article[ticket_id_field_name]
                            present_flag = MongoDBPersistence.knowledge_info_tbl.find_one({"CustomerID": customer_id, "KBNumber": KBNumber}, {"_id":0, "KBNumber": 1})
                            if (present_flag):
                                # print("Inside if")
                                success_flag = 0
                                continue
                            else:
                                # print("Inside else")
                                article['text'] = KnowledgeArticle.cleanArticle_DL(article['text'])
                                article_dict['KBNumber'] = article[ticket_id_field_name]
                                article_dict['Body'] = article['text']
                                articles_list.append(article_dict)
                                articles_df = pd.DataFrame(articles_list)
                                articles_df['Summary'] = None

                                #Source is SNOW for now
                                # print(articles_df)
                        else:
                            logging.info("%s: There is no body for the respective articles" %(RestService.timestamp))
                            success_flag = 0
                    if (not articles_df.empty):
                        articles_df['Summary'] = articles_df['Body'].apply(KnowledgeArticle.summarizeArticle_DL)
                        KnowledgeArticle.insertSummary(articles_df, customer_id, 'SNOW')
                        success_flag = 1
                else:
                    logging.info("%s: No knowledge Article found" %(RestService.timestamp))
                    success_flag = 0
            else:
                logging.info("%s: There is no ServiceNow instance present" %RestService.timestamp())
                success_flag = 0
        except Exception as e:
            logging.error(e,exc_info=True)
            success_flag = 0

        if (success_flag):
            return "Success"
        else:
            return "Failure"

    @staticmethod
    def cleanArticle(text):
        #Removing only the HTML tags from the article
        TAG_RE = re.compile(r'<[^>]+>')
        
        REPLACE_BY_SPACE_RE = re.compile('[/(){}\[\]\|@,;]')
        # BAD_SYMBOLS_RE = re.compile('[^0-9a-z #+_]')
        text = TAG_RE.sub('', text)
        text = REPLACE_BY_SPACE_RE.sub(' ', text)
        text = re.sub(r'\n', " ", text)
        # text = REPLACE_BY_SPACE_RE.sub(' ', text)
        # text = BAD_SYMBOLS_RE.sub(' ', text)
        return text

    @staticmethod
    def summarizeArticle(text):
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summarizer = LexRankSummarizer()
        summarize_document = summarizer(parser.document, 2)
        summary =''
        for sentence in summarize_document:
            summary += str(sentence)
        return summary

    @staticmethod
    def cleanArticle_DL(KA_Text):
        logging.info("Cleaning Article")
        soup = BeautifulSoup(KA_Text, "lxml")
        text = soup.get_text(separator=' ')
        logging.info(f"text: {text}")
        text = re.sub(r'[^\x00-\x7f]',r' ', text)
        logging.info(f"text: {text}")
        return text
    
    @staticmethod
    def summarizeArticle_DL(text):
        """ Pre-trained model for summarization """
        logging.info("Summarize Article")
        summary_XLNET = ''.join(xlnet_model(text, min_length=60))
        logging.info(f"summary_XLNET: {summary_XLNET}")
        return summary_XLNET

    @staticmethod
    def insertSummary(articles_df, customer_id, source = "SNOW"):
        print("inserting kb articles")
        # log_setup()
        logging.info("inserting kb articles")
        try:
            # print(articles_df.shape)
            for index, row in articles_df.iterrows():
                KBNumber = row['KBNumber']
                summary = row['Summary']
                #CustomerID = 1 , DatasetID = ?
                kb_present = MongoDBPersistence.knowledge_info_tbl.find_one({"CustomerID": customer_id, "KBNumber": KBNumber}, {"_id":0, "KBNumber": 1})
                if (kb_present):
                    continue
                else:
                    MongoDBPersistence.knowledge_info_tbl.insert_one({"KBNumber": KBNumber, "Summary": summary, "Source": source, "CustomerID": customer_id })
                # print(index)
        except Exception as e:
            logging.info("%s Some Error occured in insertSummary: %s"%(RestService.timestamp(),str(e)))
            print(e)

        


