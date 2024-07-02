__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

import pymongo
import configparser
from pymongo import MongoClient
from iia.utils.config_helper import get_config
from iia.utils.log_helper import get_logger,log_setup
from iia.crypt.crypt import decrypt_credentials
logging = get_logger(__name__)
class MongoDBPersistence(object):

    config = get_config('mongodb')
    logging.info(f"config:{config}")
    hostname = config["hostname"]
    port = int(config["port"])
    database = config['database']

    try:
        if str(config['user_auth']).lower() == 'true':
            file_name = config['config_file_name']
            dict_credentials = decrypt_credentials(file_name)
            client = MongoClient(host=hostname,
                                 port=port,
                                 username=dict_credentials['username'],
                                 password=dict_credentials['password'],
                                 authSource=config['database'],
                                 authMechanism=config['authmechanism']
                                 )
        else:
            client = MongoClient(hostname,port)
    except Exception as e:
        logging.error(e,exc_info=True)
        logging.info("Going with default mongo db connect")
        client = MongoClient(hostname, port)

    db = client[database]

    #Getting all required DB objects-------But for Multithreading we need to think on sharing same objects across all methods
    customer_tbl = db.TblCustomer

    algo_tbl = db.TblAlgorithm
    training_tickets_tbl = db.TblIncidentTraining
    PMAcategory_tbl=db.TblPMAFields
    training_hist_tbl = db.TblTraining
    rt_tickets_tbl = db.TblIncidentRT
    predicted_tickets_tbl = db.TblPredictedData
    teams_tbl = db.TblTeam
    datasets_tbl = db.TblDataset
    users_tbl = db.TblUsers
    configuration_values_tbl= db.TblConfigurationValues
    script_configuration_tbl=db.TblScriptsConfiguration
    resolution_history_tbl=db.TblResolutionHistory
    environments_tbl=db.TblEnvironments
    diagnostic_tbl=db.TblDiagnosticScripts
    tag_training_tbl=db.TblTagTraining
    tag_dataset_tbl=db.TblTagDataset

    sme_mapping_tbl = db.TblSmeMapping

    resource_details_tbl = db.TblResource
    applicationDetails_tbl = db.TblApplication
    roaster_tbl = db.TblRoaster
    tickets_weightage_tbl = db.TblTicketsWeightage
    known_errors_tbl=db.TblKnownErrors
    knowledge_info_tbl=db.TblKnowledgeInfo
    whitelisted_word_tbl=db.TblWhitelistedWordDetails
    itsm_details_tbl=db.TblITSMDetails
    assign_enable_tbl=db.TblAssignmentEnableStatus
    configuration_values_tbl= db.TblConfigurationValues
    mapping_tbl = db.TblITSMFieldMapping
    approved_tickets_tbl = db.TblApprovedTickets
    priority_mapping_tbl = db.TblITSMPriorityMapping
    manual_assignee_tbl = db.TblManualAssignee
    itsm_user_mapping = db.TblITSMUserMapping
    cluster_details_tbl = db.TblCluster
    named_entity_tbl = db.TblNamedEntity
    attachment_tbl = db.TblITSMAttachmentsData
    workflow_tbl = db.TblResolutionWorkflow
    workflow_tickets_tbl = db.TblWorkflowTickets
    pma_fields_tbl = db.TblPMAFields
    related_tickets_tbl = db.TblRelatedTickets
    entity_tags_tbl = db.TblEntityTags
    annotation_mapping_tbl = db.TblDbAnnotation
    knowledge_entity_tbl = db.TblKnowledgeEntity
    ticket_annotation_tbl = db.TblTicketAnnotation
    oneshot_learning_tbl=db.TblOneShotLearning
    image_features_tbl=db.TblImagePrediction
    image_analysis_column_tbl=db.TblImageAnalysisColumns
    image_annotation_tbl=db.TblDbAnnotationImage
    image_analysis_application_flow_tbl=db.TblImageAnalysis_ApplicationFlow
    image_analysis_defaultflow_tbl=db.TblImageAnalysis_defaultFlow
    cluster_table=db.TblClustering
    rpa_configuration_tbl = db.TblRPA_Configuration
    rpa_diag_configuration_tbl=db.TblRPADiagnostic
    itsm_tool_names = db.TblITSMTools
    application_analyst_mapping_tbl= db.TblApplicationAnalystMapping
    roster_mapping_tbl= db.TblRosterMappingDetails
    roster_shifts_tbl = db.TblRosterShifts
    def __init__(self,config):
        #Do Nothing;
        self.config=config
        print("MYSQLPresistence.__init__")
    def readList(self,name):
        #Do Nothing
        print("MYSQLPresistence.readList")
    #Connecting to MongoDB database
    