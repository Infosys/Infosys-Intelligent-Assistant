__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

from pymongo import MongoClient
import os
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from intent.restservice import RestService
from intent.persistence.mongodbpersistence import MongoDBPersistence
#import docx
#import readDocx
import docx2txt
import PyPDF2
import re
import configparser
#import logging
import glob
from intent.utils.log_helper import get_logger, log_setup
logging = get_logger(__name__)
from summarizer import Summarizer,TransformerSummarizer
from transformers import XLNetModel, XLNetTokenizer
from pathlib import Path



#import docx
# path=r'\\ad.infosys.com\storage\PUN\ITP\GDLY\IMPPNZ02\TicketTriaging\Ebin'
#path=r'\\ad.infosys.com\storage\PUN\ITP\GDLY\IMPPNZ02\TicketTriaging\Ebin\requirement.txt'
#path=r'\\ad.infosys.com\storage\PUN\ITP\GDLY\IMPPNZ02\TicketTriaging\Ebin\Sep.pdf'

#from tika import parser


#raw = parser.from_file(r'\\ad.infosys.com\storage\PUN\ITP\GDLY\IMPPNZ02\TicketTriaging\Ebin\Sep.pdf')
#print(raw['content'])
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

''' Opening and reading the files'''

@app.route('/api/getFileServerKnowledgeArticles/<int:customer_id>', methods = ['GET'])
def getFileServerKnowledgeArticles(customer_id):
    return FileServerKnowledgeArticles.getFileServerKnowledgeArticles(customer_id)


class FileServerKnowledgeArticles(object):
    
    def __init__(self):
        pass

    @staticmethod
    def cleanArticle(text):
        #Removing only the HTML tags from the article
        TAG_RE = re.compile(r'<[^>]+>')
        
        REPLACE_BY_SPACE_RE = re.compile('[/(){}\[\]\|@,;]')
        # BAD_SYMBOLS_RE = re.compile('[^0-9a-z #+_]')
        text = TAG_RE.sub('', text)
        text=re.sub(r"http\S+", "", text)
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
    def summarizeArticle_DL(text):
        """ Pre-trained model for summarization """
        logging.info("Summarize Article")
        summary_XLNET = ''.join(xlnet_model(text, min_length=60))
        logging.info(f"summary_XLNET: {summary_XLNET}")
        return summary_XLNET

    @staticmethod
    def insertSummary(summary,key, customer_id, source = "FileServer"):
        print("inserting kb articles")
        try:

            # print(articles_df.shape)
            MongoDBPersistence.knowledge_info_tbl.insert_one({"CustomerID": customer_id, 'Name':key,'Summary':summary, "Source": source})
        except Exception as e:
            logging.info("%s Some Error occured: %s"%(RestService.timestamp(),str(e)))
            # print(e)

    
    
    @staticmethod
    def getFileServerKnowledgeArticles(customer_id):
        # path=r'\\ad.infosys.com\storage\PUN\ITP\GDLY\IMPPNZ02\TicketTriaging\Ebin'
        try:

            config = configparser.ConfigParser()
            config["DEFAULT"]['path'] = "config/"
            config.read(config["DEFAULT"]["path"]+"Intent.ini")
            path = config["ModuleConfig"]["path"]
            # print(type(path))
            print("Path is:", path)
        except:
            logging.error(" %s: Error occured: Hint: 'path' is not defined in 'config/intent.ini' file." %RestService.timestamp())
            # path=r'\\ad.infosys.com\storage\PUN\ITP\GDLY\IMPPNZ02\TicketTriaging\Ebin'
            logging.info("Taking default path " %RestService.timestamp())
        # print("Before Opening files:", path)
        try:
            files = os.listdir(path)
        except:
            logging.info("%s Some error occured in opening directory")
            return "Failure"
        # print("Files:", files)
        if len(files)!=0:
            for i in files:
                if('.txt' in i):
                    with open(path + '\\'+ i,'rb') as f:
                        data=f.read().decode('utf-8')
                    key=i.split('.')[0]
                    present_flag = MongoDBPersistence.knowledge_info_tbl.find_one({"CustomerID": customer_id, 'Name':key})

                    if (present_flag):
                        continue
                    else:
                        data=FileServerKnowledgeArticles.cleanArticle(data)
                        summary = FileServerKnowledgeArticles.summarizeArticle_DL(data)
                        FileServerKnowledgeArticles.insertSummary(summary,key, customer_id)
                
                elif('.docx' in i):
                    data = docx2txt.process(path + '\\'+i)
                    key=i.split('.')[0] 
                    present_flag = MongoDBPersistence.knowledge_info_tbl.find_one({"CustomerID": customer_id, 'Name':key})

                    if (present_flag):
                        continue
                    else:
                        data=FileServerKnowledgeArticles.cleanArticle(data)
                        summary = FileServerKnowledgeArticles.summarizeArticle_DL(data)
                        FileServerKnowledgeArticles.insertSummary(summary,key, customer_id)

            return "Success"

        else:
            return "No files present in the directory"
        
       






