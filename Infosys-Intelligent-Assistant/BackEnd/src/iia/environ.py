__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

from iia.persistence.mappingpersistence import MappingPersistence
from iia.persistence.mongodbpersistence import MongoDBPersistence
from iia.utils.log_helper import get_logger

logging = get_logger(__name__)
customer_id = MongoDBPersistence.customer_tbl.find_one({}, {"CustomerID": 1, "_id": 0})['CustomerID']

# General Variables
field_mapping = MappingPersistence.get_mapping_details(1)
logging.info(f"field_mapping: {field_mapping}")
group_field_name = field_mapping['Group_Field_Name']
ticket_id_field_name = field_mapping['Ticket_ID_Field_Name']
status_field_name = field_mapping['Status_Field_Name']
description_field_name = field_mapping['Description_Field_Name']
sys_created_on_field_name = field_mapping['Sys_Created_On_Field_Name']
closed_at_field_name = field_mapping['Closed_At_Field_Name']

# ITSM related variables
queryBuilder = status_field_name + '=1^OR' + status_field_name + '=2^' + group_field_name + '!=is_empty^'

login_status = {
    "Success": "Logged in",
    "Failure": "No Login Found"
}
