__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""
import time
import atexit
from iia.restservice import RestService
from iia.persistence.mongodbpersistence import MongoDBPersistence
from iia.recommendation.knowledgearticles import KnowledgeArticle
from bson import json_util
from flask import request
from iia.utils.config_helper import get_config
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.start()
from iia.utils.log_helper import get_logger, log_setup
logging = get_logger(__name__)
app = RestService.getApp()

atexit.register(lambda: scheduler.pause())

@app.route("/api/CreateKBJob/<int:customer_id>",methods=['GET'])
def CreateKBJob(customer_id):
    return KnowledgeBaseScheduler.CreateKBJob(customer_id)

@app.route("/api/StopKBJob/<int:customer_id>/<job_id>", methods=['GET'])
def StopKBJob(customer_id, job_id):
    return KnowledgeBaseScheduler.StopKBJob(customer_id,job_id)

####### Knowledge Base Scheduler #########
class KnowledgeBaseScheduler(object):
    def __init__(self):
        pass
    
    @staticmethod
    def CreateKBJob(customer_id):
        global scheduler
        #by default this job is running once in a week 
        cron_settings={}

        time_interval = 60*60*24*7

        try:
            time_interval = get_config('KnowledgeArticle')['TimeInterval']
        except Exception as e:
            time_interval = 60*60*24*7

        cron_settings["TimeInterval"] = time_interval #60*60*24*7   ##60*60*24*7  (seconds in a week)
        try:

            logging.info("%s Initializes Job for fetching KB Articles for Customer Id %d"% (RestService.timestamp(), customer_id))
            customer_name = MongoDBPersistence.customer_tbl.find_one({"CustomerID":customer_id},{"_id":0,"CustomerName":1})
            if(customer_name):
                job_id = 'KB_'+str(customer_name["CustomerName"])
            else:
                logging.info("Customer ID not found in Database ")
                return 'failure'
            job_exits = MongoDBPersistence.customer_tbl.find_one({"CustomerID":customer_id},{"_id":0,"job_id":1})
            if(job_exits):
                logging.info("%s: Job (Job id:%s) has already been scheduled for the customer(CustomerID: %d)" % (RestService.timestamp(), job_id, customer_id))
                return "failure"

            ## In args here we only sending the customer id , 
            ## bt as per get knowledge article implemented we need dataset id too
            KnowledgeArticle.getKnowledgeArticle(customer_id)
            scheduler.add_job(KnowledgeArticle.getKnowledgeArticle,trigger="interval",args=[customer_id], id=job_id,
                                    seconds=cron_settings['TimeInterval'])
            logging.info('%s: KB Job has been scheduled for the Customer(Customer: %d).. Job id=%s.' % (
                    RestService.timestamp(), customer_id, job_id))
        
        except Exception as e:
            logging.error('%s: Error occurred: %s ' % (RestService.timestamp(), str(e)))
            logging.info('%s: Error while creating new job for the customer(CustomerID: %s)' % (RestService.timestamp(), str(customer_id)))  # ,cron_setting["DatasetID"]))
            return 'failure'
        
        job_setting={}
        job_setting["TimeInterval"] = cron_settings["TimeInterval"]
        job_setting["job_id"] = job_id

        MongoDBPersistence.customer_tbl.update_one({"CustomerID": customer_id},
                                    {"$set": {"KBJobSettings": job_setting}}, upsert=False)

        return "success"

        ##make entries in the database for the job per customer .
        

    @staticmethod 
    def StopKBJob(customer_id, job_id):
        try:
            ()
            scheduler.remove_job(job_id)
           
            MongoDBPersistence.customer_tbl.update_one({"CustomerID": customer_id}, {"$unset": {"KBJobSettings": 1}})
            resp = 'success'
        except Exception as e:
            print(str(e))
            resp = 'failure'
        return resp