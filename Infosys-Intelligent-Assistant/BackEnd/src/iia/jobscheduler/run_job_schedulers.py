__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""
from iia.persistence.mongodbpersistence import MongoDBPersistence
from iia.recommendation.knowledgearticles import KnowledgeArticle
from iia.relatedtickets.related_tickets_search import relatedticket
import atexit
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.start()
atexit.register(lambda: scheduler.pause())

class SchedulerJobs(object):
    '''
    classdocs
    '''

    def __init__(self, params):
        '''
        Constructor
        '''
    @staticmethod
    def run_jobs():
        cron_settings = list(MongoDBPersistence.customer_tbl.find({},{"RTJobSettings":1,
                                                                 "KBJobSettings":1,
                                                                 "CustomerID":1,
                                                                 "_id":0}))

        if cron_settings:
            for cron_setting in cron_settings:
                if cron_setting.get("RTJobSettings"):
                    print(cron_setting['RTJobSettings'])
                    scheduler.add_job(relatedticket.startProcess, trigger="interval",
                                      id=cron_setting['RTJobSettings']['job_id'],
                                      seconds=cron_setting['RTJobSettings']['TimeInterval'])
                if cron_setting.get("KBJobSettings"):
                    print(cron_setting['KBJobSettings'])
                    KnowledgeArticle.getKnowledgeArticle(cron_setting['CustomerID'])
                    scheduler.add_job(KnowledgeArticle.getKnowledgeArticle, trigger="interval",
                                      args=[cron_setting['CustomerID']],
                                     id=cron_setting['KBJobSettings']['job_id'],
                                     seconds=cron_setting['KBJobSettings']['TimeInterval'])

            print(scheduler.get_jobs())


SchedulerJobs.run_jobs()