__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""
import time
import atexit
from iia.restservice import RestService
from iia.persistence.mongodbpersistence import MongoDBPersistence
from iia.training.retraining import Retrain
from bson import json_util
from flask import request
from iia.utils.log_helper import get_logger, log_setup
logging = get_logger(__name__)
from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler()
scheduler.start()
app = RestService.getApp()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.pause())

@app.route("/api/CreateJob/<int:customer_id>", methods=['POST'])
def CreateJob(customer_id):
    return JobScheduler.CreateJob(customer_id)


@app.route("/api/StopJob/<int:customer_id>/<int:dataset_id>/<job_id>", methods=['GET'])
def StopJob(customer_id,dataset_id,job_id):
    return JobScheduler.StopJob(customer_id,dataset_id,job_id)


@app.route("/api/GetJobs/<int:customer_id>", methods=['GET'])
def GetJobs(customer_id):
    return JobScheduler.GetJobs(customer_id)


@app.route("/api/GetJob/<job_id>", methods=['GET'])
def GetJob(job_id):
    return JobScheduler.GetJob(job_id)

@app.route("/api/getJobSettings/<int:customerID>/<int:datasetID>", methods = ['GET'])
def getJobSettings(customerID, datasetID):
    return JobScheduler.getJobSettings(customerID, datasetID)

@app.route("/api/getJobID/<int:customerID>/<int:datasetID>", methods = ['GET'])
def getJobID(customerID, datasetID):
    return JobScheduler.getJobID(customerID, datasetID)

class JobScheduler(object):
    '''
    classdocs
    '''

    def __init__(self, params):
        '''
        Constructor
        '''

    @staticmethod
    def CreateJob(customer_id):
        global scheduler
        settings = request.get_json() 
        print(settings)
        logging.info(f"settings: {settings}")
        for cron_setting in settings:
            try:
                print("cron_setting %s" % cron_setting)
                logging.info(f"cron_setting: {cron_setting}")
                # Create job
                dataset_id = cron_setting["DatasetID"]
                logging.info('%s: Scheduling new job for the dataset(DatasetID: %d).' % (RestService.timestamp(), dataset_id))
                job_id = str(customer_id) + str(dataset_id)
                print("job_id %s" % job_id)
                job_exists = MongoDBPersistence.datasets_tbl.find_one({"CustomerID": customer_id, "DatasetID": dataset_id},{"_id":0, "job_id":1})
                if(job_exists):
                    logging.info('%s: Job (Job id:%s) has already been scheduled for the dataset(DatasetID: %d).' % (RestService.timestamp(), job_id, dataset_id))
                    continue

                scheduler.add_job(Retrain.retrain, trigger="interval", args=[customer_id, dataset_id], id=job_id,
                                  seconds=cron_setting['TimeInterval'],next_run_time=cron_setting['retrain_date'])
                
                logging.info('%s: Job has been scheduled for the dataset(DatasetID: %d).. Job id=%s.' % (
                RestService.timestamp(), dataset_id, job_id))
            except Exception as e:
                logging.error('%s: Error occurred: %s ' % (RestService.timestamp(), str(e)))
                logging.info('%s: Error while creating new job for the dataset(DatasetID: ).' % (
                    RestService.timestamp())) 
                return 'failure'
            # Push settings into database
            JobSettings = {}
            JobSettings['TimeInterval'] = cron_setting['TimeInterval']
            JobSettings['MinUntrained'] = cron_setting['MinUntrained']

            MongoDBPersistence.datasets_tbl.update_one({"CustomerID": customer_id, "DatasetID": dataset_id},
                                    {"$set": {"JobSettings": JobSettings}}, upsert=False)
            MongoDBPersistence.datasets_tbl.update_one({"CustomerID": customer_id, "DatasetID": dataset_id}, {"$set": {"job_id": job_id}},
                                    upsert=False)
            logging.info(
                '%s: Job schedule settings for the dataset(DatasetID: %d) has been stored in TblDataset successfully.' % (
                RestService.timestamp(), dataset_id))
        return 'success'

    @staticmethod 
    def StopJob(customer_id,dataset_id, job_id):
        try:
            try:
                scheduler.remove_job(job_id)
            except Exception as e:
                logging.error(e, exc_info=True)
            #unset job_id field from from TblDataset
            MongoDBPersistence.datasets_tbl.update_one({"CustomerID": customer_id, 'DatasetID':dataset_id}, {"$unset": {"job_id": 1}})
            MongoDBPersistence.datasets_tbl.update_one({"CustomerID": customer_id, 'DatasetID':dataset_id}, {"$unset": {"JobSettings": 1}})
            resp = 'success'
        except Exception as e:
            print(str(e))
            resp = 'failure'
        return resp

    @staticmethod
    def GetJobs(customer_id):
        print(scheduler.get_jobs())
        jobs = []
        if (len(scheduler.get_jobs()) == 0):
            resp = json_util.dumps(["failure"])
        else:
            jobs = list(MongoDBPersistence.datasets_tbl.find({'CustomerID': customer_id, 'job_id': {"$exists" : True}}, {'JobSettings': 1, "_id": 0, "job_id": 1}))
            resp = json_util.dumps(jobs)
        return resp

    @staticmethod
    def GetJob(job_id):
        print(scheduler.get_job(job_id))
        return str(scheduler.get_job(job_id))

    @staticmethod
    def getJobID(customer_id,dataset_id):
        job_id = MongoDBPersistence.datasets_tbl.find_one({'CustomerID':customer_id,'DatasetID':dataset_id},{"_id":0,"job_id":1})
        if(job_id):
            return job_id['job_id']
        else:
            logging.info("Job not found.")
            return 'empty'

    @staticmethod
    def getJobSettings(customerID, datasetID):
        settings = MongoDBPersistence.datasets_tbl.find_one({"DatasetID":datasetID, "CustomerID": customerID}
                                        ,{"JobSettings":1, "_id": 0})
        if (settings):
            resp = "success"
        else:
            resp = "failure"
        return resp