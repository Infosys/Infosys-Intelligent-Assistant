__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

from iia.persistence.mongodbpersistence import MongoDBPersistence
from iia.utils.log_helper import get_logger

logging = get_logger(__name__)

class MappingPersistence(object):

    def __init__(self):
        pass

    @staticmethod
    def get_mapping_details(customer_id):
        itsm_details = MongoDBPersistence.itsm_details_tbl.find_one({}, {"_id":0, "ITSMToolName":1})
        logging.info(f"itsm_details: {itsm_details}")
        itsm_tool_name = itsm_details['ITSMToolName']
        field_mapping = MongoDBPersistence.mapping_tbl.find_one({"CustomerID":customer_id, "Source_ITSM_Name": itsm_tool_name}, {"_id":0})
        logging.info(f"field_mapping: {field_mapping}")
        return field_mapping