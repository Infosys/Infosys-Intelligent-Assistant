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
from iia.recommendation.recommendationmodel import Recommendation
from iia.persistence.mongodbpersistence import MongoDBPersistence
from iia.persistence.mappingpersistence import MappingPersistence

from bson import json_util
from iia.restservice import RestService
import pandas as pd
from iia.environ import *
from iia.utils.log_helper import get_logger, log_setup
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
                
                knowledgearticles = KnowledgeArticle.KBTable.get(query={'workflow_state':'published'})
                
                success_flag = 0
                if (knowledgearticles):
                    
                    articles_list = []
                    articles_df = pd.DataFrame()
                    for article in knowledgearticles.all():
                        
                        article_dict = {}
                        
                        if (article['text']):
                            KBNumber = article[ticket_id_field_name]
                            present_flag = MongoDBPersistence.knowledge_info_tbl.find_one({"CustomerID": customer_id, "KBNumber": KBNumber}, {"_id":0, "KBNumber": 1})
                            if (present_flag):
                                
                                success_flag = 0
                                continue
                            else:
                                
                                article['text'] = KnowledgeArticle.cleanArticle_DL(article['text'])
                                article_dict['KBNumber'] = article[ticket_id_field_name]
                                article_dict['Body'] = article['text']
                                articles_list.append(article_dict)
                                articles_df = pd.DataFrame(articles_list)
                                articles_df['Summary'] = None

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
        
        TAG_RE = re.compile(r'<[^>]+>')
        
        REPLACE_BY_SPACE_RE = re.compile('[/(){}\[\]\|@,;]')
        
        text = TAG_RE.sub('', text)
        text = REPLACE_BY_SPACE_RE.sub(' ', text)
        text = re.sub(r'\n', " ", text)
        
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

        logging.info("inserting kb articles")
        try:
            
            for index, row in articles_df.iterrows():
                KBNumber = row['KBNumber']
                summary = row['Summary']
               
                kb_present = MongoDBPersistence.knowledge_info_tbl.find_one({"CustomerID": customer_id, "KBNumber": KBNumber}, {"_id":0, "KBNumber": 1})
                if (kb_present):
                    continue
                else:
                    MongoDBPersistence.knowledge_info_tbl.insert_one({"KBNumber": KBNumber, "Summary": summary, "Source": source, "CustomerID": customer_id })
                
        except Exception as e:
            logging.info("%s Some Error occured in insertSummary: %s"%(RestService.timestamp(),str(e)))
            print(e)