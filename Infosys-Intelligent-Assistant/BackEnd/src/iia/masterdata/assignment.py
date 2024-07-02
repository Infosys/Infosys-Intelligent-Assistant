__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

from iia.persistence.mongodbpersistence import MongoDBPersistence
from iia.restservice import RestService
from iia.masterdata.assignment_adapter import AssignmentAdapter
from bson import json_util
from datetime import datetime
from flask import request
import json
from iia.utils.log_helper import get_logger, log_setup

logging = get_logger(__name__)
class Assignment():
    def __init__(self, customer_id=None, dataset_id=None, \
                 mapping_assignemnt=None, possible_assignee=None, possible_assignee_for_assignment=None):
        self.customer_id = customer_id
        self.dataset_id = dataset_id
        self.mapping_assignemnt = mapping_assignemnt
        self.possible_assignee = possible_assignee
        self.possible_assignee_for_assignment = possible_assignee_for_assignment

    def assignmentRouting(self):
        try:

            logging.info("Inside Assignment Routing method")
            resourceCount = int(MongoDBPersistence.resource_details_tbl.count())
            applicationCount = int(MongoDBPersistence.applicationDetails_tbl.count())
            mappingTableCount = int(MongoDBPersistence.manual_assignee_tbl.count())
            logging.info("Going to invoke respective Assignment Module")
            logging.debug(f"resourceCount: {resourceCount}")
            logging.debug(f"applicationCount: {applicationCount}")
            logging.debug(f"mappingTableCount: {mappingTableCount}")
            logging.debug(f"self.mapping_assignemnt: {self.mapping_assignemnt}")
            logging.debug(f"self.possible_assignee: {self.possible_assignee}")
            logging.debug(f"self.possible_assignee_for_assignment: {self.possible_assignee_for_assignment}")
            obj = AssignmentAdapter(resourceCount, applicationCount, mappingTableCount, customer_id=self.customer_id, \
                                    dataset_id=self.dataset_id, mapping_assignemnt=self.mapping_assignemnt,
                                    possible_assignee=self.possible_assignee, \
                                    possible_assignee_for_assignment=self.possible_assignee_for_assignment)

            return obj.invokeAssignment()
        except Exception as e:
            logging.error(e, exc_info=True)
            logging.error("Error occurred while assignment routing %s" % (str(e)))
