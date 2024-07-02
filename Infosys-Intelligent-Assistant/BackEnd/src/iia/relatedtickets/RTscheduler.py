__created__ = "Apr 1, 2022"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

import atexit

from apscheduler.schedulers.background import BackgroundScheduler
from iia.persistence.mongodbpersistence import MongoDBPersistence
from iia.relatedtickets.related_tickets_search import relatedticket
from iia.restservice import RestService

scheduler = BackgroundScheduler()
scheduler.start()

from iia.utils.log_helper import get_logger

logging = get_logger(__name__)
app = RestService.getApp()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.pause())


@app.route("/api/CreateRTJob/<int:customer_id>", methods=['GET'])
def CreateRTJob(customer_id):
    return RelatedTicketScheduler.CreateRTJob(customer_id)


@app.route("/api/StopRTJob/<int:customer_id>/<job_id>", methods=['GET'])
def StopRTJob(customer_id, job_id):
    return RelatedTicketScheduler.StopRTJob(customer_id, job_id)


####### Knowledge Base Scheduler #########
class RelatedTicketScheduler(object):
    def __init__(self):
        pass

    @staticmethod
    def CreateRTJob(customer_id):
        global scheduler
        # by default this job is running once in a week
        cron_settings = {}
        cron_settings["TimeInterval"] = 20  ##60*60*24*7  (seconds in a week)
        try:
            # log_setup()
            logging.info("%s Initializes Job for fetching Related tickets for Customer Id %d" % (
            RestService.timestamp(), customer_id))
            customer_name = MongoDBPersistence.customer_tbl.find_one({"CustomerID": customer_id},
                                                                     {"_id": 0, "CustomerName": 1})
            if (customer_name):
                job_id = 'RT_' + str(customer_name["CustomerName"])
            else:
                logging.info("Customer ID not found in Database ")
                return 'failure'
            job_exits = MongoDBPersistence.customer_tbl.find_one({"CustomerID": customer_id}, {"_id": 0, "job_id": 1})
            if (job_exits):
                logging.info("%s: Job (Job id:%s) has already been scheduled for the customer(CustomerID: %d)" % (
                RestService.timestamp(), job_id, customer_id))
                return "failure"

            ## In args here we only sending the customer id , 
            ## bt as per get knowledge article implemented we need dataset id too
            scheduler.add_job(relatedticket.startProcess, trigger="interval", args=[customer_id], id=job_id,
                              seconds=cron_settings['TimeInterval'])
            
            logging.info('%s: Related ticket Job has been scheduled for the Customer(Customer: %d).. Job id=%s.' % (
                RestService.timestamp(), customer_id, job_id))

        except Exception as e:
            logging.error('%s: Error occurred: %s ' % (RestService.timestamp(), str(e)))
            logging.info('%s: Error while creating new job for the customer(CustomerID: %s)' % (
            RestService.timestamp(), str(customer_id)))  # ,cron_setting["DatasetID"]))
            return 'failure'

        job_setting = {}
        job_setting["TimeInterval"] = cron_settings["TimeInterval"]
        job_setting["job_id"] = job_id
        MongoDBPersistence.customer_tbl.update_one({"CustomerID": customer_id},
                                                   {"$set": {"RTJobSettings": job_setting}}, upsert=False)
        
        return "success"

    @staticmethod
    def StopRTJob(customer_id, job_id):
        try:
            
            try:
                scheduler.remove_job(job_id)
            except Exception as e:
                logging.error(e, exc_info=True)
            
            MongoDBPersistence.customer_tbl.update_one({"CustomerID": customer_id}, {"$unset": {"RTJobSettings": 1}})
            resp = 'success'
        except Exception as e:
            print(str(e))
            resp = 'failure'
        return resp
