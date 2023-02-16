__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

from intent.persistence.mongodbpersistence import MongoDBPersistence
from intent.persistence.mappingpersistence import MappingPersistence
from intent.restservice import RestService
#from intent.utils.stringutils import StringUtils
from intent.masterdata.resources import ResourceMasterData

from pathlib import Path
import joblib
from bson import json_util

#import logging

import pandas as pd

import importlib

from intent.incident.incidenttraining import IncidentTraining
import os
from flask import session
from intent.utils.log_helper import get_logger, log_setup
logging = get_logger(__name__)



class RB_RBTeam_Predict(object):
    '''
    classdocs
    '''

    def __init__(self, params):
        '''
        Constructor
        '''
        
    #@app.route('/predict/<int:customer_id>', methods=['GET'])
    @staticmethod
    def predict(customer_id):
        # log_setup()
        logging.info("Inside RB customized prediction File for customer %s"%(customer_id))
        field_mapping = MappingPersistence.get_mapping_details(customer_id)
        group_field_name = field_mapping['Group_Field_Name']
        ticket_id_field_name = field_mapping['Ticket_ID_Field_Name']
        status_field_name = field_mapping['Status_Field_Name']
        description_field_name = field_mapping['Description_Field_Name']
        result = {}
        logging.info('%s: Deleting the old records from TblPredictedData.'%(RestService.timestamp()))
        # user = os.getlogin()
        if (session.get('user')):
            logging.info("%s Catching User Session"%RestService.timestamp())
            user = session['user']
            logging.info("%s Session catched user as  %s"%(RestService.timestamp(), user))
        else:
            logging.info("%s You are not logged in please login" %RestService.timestamp())
            return "No Login Found"
        
        #print("User Yamini")
        login_user = MongoDBPersistence.users_tbl.find_one({"UserID": user}, {"_id": 0})
        if(login_user):
            user_role = login_user['Role']
            if (user_role == 'Admin'):

                MongoDBPersistence.predicted_tickets_tbl.delete_many({'CustomerID':customer_id})
                
                garbage_tickets = []
                ############## RB specific ########
                #print("rb predict working")
                rt_tickets =  list(MongoDBPersistence.rt_tickets_tbl.find({'CustomerID':customer_id, "$or": [{status_field_name:'New'},{status_field_name:'Assigned'}], 'user_status':'Not Approved'},{'_id':0}))
                #print("zrt tickets", rt_tickets)
                if(not rt_tickets):
                    logging.info('%s: There is nothing uploaded for prediction. Upload tickets data first & then try again.'%RestService.timestamp())
                    return "failure"
                #Current logic: predicting tickets one by one from TblIncidentRT
                #Other logic: Picking up all realtime tickets dataset by dataset from TblIncidentRT: Faster in some case
                
                pred_assignment_grp_lst=[]
                final_predictions_lst=[]
                dataset_id = rt_tickets[0]['DatasetID']
                white_lst_collection=list(MongoDBPersistence.whitelisted_word_tbl.find({'CustomerID':customer_id,'DatasetID':dataset_id}))
                #--Automatic approval of incident tickets based on threshold value--
                tickets_to_be_approved=[]
                logging.info('%s: fetching details from "assign_enable_tbl"'%RestService.timestamp())
                t_value_doc=MongoDBPersistence.assign_enable_tbl.find_one({})
                t_value_keys=list(t_value_doc.keys())
                logging.info('%s: assigning default value 0 for "t_value" and "False" for "t_value_enabled"'%RestService.timestamp())
                t_value=0         
                t_value_enabled=False
                if(t_value_doc and "t_value_enabled" in t_value_keys):
                    if(t_value_doc['t_value_enabled']=='true' and 'threshold_value' in t_value_keys):
                        logging.info('assigning value for "t_value" and for "t_value_enabled" from database!')
                        t_value=t_value_doc["threshold_value"]
                        t_value_enabled=True
                    else:
                        logging.info('%s: Either "t_value_enabled" is false or no "threshold_value" field in database'%RestService.timestamp())
                else:
                    logging.info('%s: Either "t_value_doc" not exist or no field "t_value_enabled" in database'%RestService.timestamp())
                
                if(t_value_doc and 'assignment_enabled' in list(t_value_doc.keys())):
                    assignment_enabled=True if t_value_doc['assignment_enabled']=='true' else False
                else:
                    logging.info('%s: Either "t_value_doc" not exist or no field "assignment_enabled" in database'%RestService.timestamp())
                    logging.info('assigning default value "True" for "assignment_enabled"')
                    assignment_enabled=True
                
                for ticket in rt_tickets:
                    all_ok_flag = 0
                    try:
                        dataset_id = ticket['DatasetID']
                        #print('dataset id is ' + str(dataset_id))
                    except Exception as e:
                        logging.error('%s: Error: %s'%(RestService.timestamp(),str(e)))
                        garbage_tickets.append(ticket[ticket_id_field_name])
                        logging.info('%s: Dataset id not found for the ticket Number: %s'%(RestService.timestamp(),ticket[ticket_id_field_name]))
                        continue
                    final_predictions = {}
                    final_predictions[ticket_id_field_name] = ticket[ticket_id_field_name]
            
                    #Fetch Customer choices
                    cust_name = MongoDBPersistence.customer_tbl.find_one({'CustomerID':customer_id},{'CustomerName':1, '_id':0})['CustomerName']
                    dataset_info_dict =  MongoDBPersistence.datasets_tbl.find_one({'CustomerID':customer_id, "DatasetID":dataset_id},{'DatasetName':1,'FieldSelections':1, '_id':0})
                    if(dataset_info_dict):
                        dataset_name = dataset_info_dict['DatasetName']
                    else:
                        logging.info('%s: Customer name not found in the record.'%RestService.timestamp())
                        return "failure"
                    fieldselection_list = dataset_info_dict['FieldSelections']
                    #print('field selection list is ' + str(fieldselection_list))
                    pred_fields_choices_list = []
                    #Pick up Approved customer choices 
                    for pred_fields in fieldselection_list:
                        if(pred_fields['FieldsStatus']=='Approved'):
                            pred_fields_choices_list = pred_fields['PredictedFields']
                            #print('predicted fields are ' + str(pred_fields_choices_list))
            
                    pred_field_list = []
                    for pre_field in pred_fields_choices_list:
                        pred_field_list.append(pre_field['PredictedFieldName'])
            
                    conf_score = []
                    #--Automatic approval of incident tickets based on threshold value--
                    t_value_confidence_flag=0  
                    total_fields_to_be_perdicted=len(pred_field_list)
                    for pred_field in pred_field_list:
                        pred_field_confidance = {}
                            #Based on each prediction field, get all corelated fields appended in a single field(Say in_field)
                            #Use feature selection algorithms to select best fields from training dataset
                        input_field_list = []
                        for input_field in pred_fields_choices_list:
                            if(input_field['PredictedFieldName'] == pred_field):
                                input_field_list = input_field['InputFields']
                                #print('input field list is ' + str(input_field_list))
                                algoName = input_field['AlgorithmName']
                        if(len(input_field_list)==0):
                            logging.info('%s: No input fields choosen for %s.'%(RestService.timestamp(),pred_field))
                            continue
                        #Concatinating input fields together into in_field
                        input_df = pd.DataFrame()   
                        input_df = pd.DataFrame([{input_field_list[0]:ticket[input_field_list[0]]}])
                        final_predictions[input_field_list[0]] = ticket[input_field_list[0]]
                        for input_field_ in input_field_list[1:]:
                            final_predictions[input_field_] = ticket[input_field_]
                            input_df[input_field_] = pd.DataFrame([{input_field_:ticket[input_field_]}])
                        
                        #input_df['in_field'] = input_df[input_field_list].astype(str).sum(axis=1)
                        input_df['in_field'] = ''
                        for field in input_field_list:
                            input_df['in_field'] += input_df[field] + ' --~||~-- '
                        input_df1 = pd.DataFrame()
                        input_df1['in_field'] = input_df['in_field']
                        
                        logging.info(input_df1.iloc[0]['in_field'])
                        in_field = 'in_field'
                        #Skips those tickets where there is no description field
                        input_df1 = input_df1[pd.notnull(input_df1[in_field])]

                        #Custom preprocessing call
                        customer_name = MongoDBPersistence.customer_tbl.find_one({'CustomerID':customer_id},{'CustomerName':1, '_id':0})['CustomerName']
                        class_name = customer_name + "_"+ "".join(dataset_name.split()) +"_Preprocessing"
                        module_name = "intent.custompreprocessing." + class_name
                        try:
                            module = importlib.import_module(module_name)
                            class_ = getattr(module, class_name)
                            input_df1 = class_.preprocess(input_df1, "predict")
                        except Exception as e:
                            logging.error('%s: Error occurred: %s ' % (RestService.timestamp(), str(e)))
                            logging.info("Error can be ignored if there is no customized pre-processing module uploaded. Going for basic cleaning of corpus ")
                            ## No custom preprocessing file present , so going for some basic cleaning
                            training_tkt_df = IncidentTraining.cleaningInputFields(input_df1,in_field)

                        input_df_list = input_df1['in_field'].tolist()
                        descr_df = [str(x) for x in input_df_list]

                        #   ----White Listed Word Logic---
                        found_white_lst_wrd=False
                        input_descr=descr_df[0]

                        try:
                            for white_lst_doc in white_lst_collection:# --loop 1--
                                if(white_lst_doc['PredictedField']==pred_field and white_lst_doc['WhiteListed_Words'] != []):#   --condition 1--
                                    for field_doc in white_lst_doc['WhiteListed_Words']:# --loop 2--
                                        for word in field_doc['Value']:# --loop 3--
                                            # word = word.lower()
                                            # wht_lst_wrd = '\\b'+word+'\\t'
                                            # wrd_exst_state = re.search(wht_lst_wrd,input_descr)
                                            if(word.lower() in input_descr):#   --condition 2--
                                                predicted_label=field_doc['Field_Name']
                                                logging.info('%s: found a match from white listed words collection'%RestService.timestamp())
                                                if(pred_field=='assignment_group'):#   --condition 3--
                                                    pred_assignment_grp_lst.append(predicted_label)
                                                    final_predictions['possible_assignees'] = ResourceMasterData.find_possibleassignees(predicted_label)
                                                #--condition 3--
                                                pred_field_confidance[pred_field] = predicted_label
                                                pred_field_confidance['ConfidenceScore'] = 1
                                                conf_score.append(pred_field_confidance)
                                                found_white_lst_wrd=True
                                                #--Automatic approval of incident tickets based on threshold value--
                                                t_value_confidence_flag=t_value_confidence_flag+1 
                                                logging.info('%s: successfully updated conf_score doc with white listed words details '%RestService.timestamp())
                                                break
                                            #--condition 2--
                                        # --loop 2--
                                        if(found_white_lst_wrd):
                                            break
                                    #--loop 3--
                                #--condition 1--
                                if found_white_lst_wrd:
                                    break
                            #--loop 1--
                        except Exception as e:
                            logging.error('%s: Exception: %s'%(RestService.timestamp(),str(e)))
                        if(found_white_lst_wrd):
                            all_ok_flag = 1
                            logging.info('%s: match found!, continueing the loop with next predicted field'%RestService.timestamp())
                            continue
                        #   ------------------------------
                        
                        pred_output_result = []
            
                        vocab_path = 'data/' + cust_name + "__" + dataset_name + '__' + in_field + "__" + pred_field + "__" + "Approved" + "__" +"Vocabulary.pkl"
                        model_path = 'models/' + cust_name + "__" + dataset_name + '__' + algoName + "__" + pred_field + "__" + "Approved" + "__" +"Model.pkl"
                        vocab_file = Path(vocab_path)
                        model_file = Path(model_path)
                        if(vocab_file.is_file()):
                            tfidf = joblib.load(vocab_path)
                        else:
                            logging.info('%s: Vocabulary file not found for %s field.. please train algo, save the choices & try again.'%(RestService.timestamp(),pred_field))
                            continue
            
                        if(model_file.is_file()):
                            fittedModel = joblib.load(model_file)
                        else:
                            logging.info('%s: ML Model file not found for %s field.. please train algo, save the choices & try again.'%(RestService.timestamp(),pred_field))
                            continue
                        pred_output_result = fittedModel.predict(tfidf.transform(descr_df).toarray())
                        id_to_labels = MongoDBPersistence.datasets_tbl.find_one({'CustomerID':customer_id, "DatasetID": dataset_id},{"_id":0,"IdToLabels":1})
                        if(id_to_labels):
                            id_to_labels_dict = id_to_labels["IdToLabels"]
                            inside_id_to_label = id_to_labels_dict[str(pred_field)]
                        else:
                            logging.info('%s: De-map data not found for %s field.'%(RestService.timestamp(),pred_field))

                        predicted_label = inside_id_to_label[str(pred_output_result[0])]
                        #predicted_label= str(pred_output_result[0])
                        
                        # assign_grp = str(pred_output_result[0])
                        pred_field_confidance[pred_field] = predicted_label
                        
                        confidence_score = float("{0:.2f}".format(max(fittedModel.predict_proba(tfidf.transform(descr_df).toarray())[0])))
                        pred_field_confidance['ConfidenceScore'] = confidence_score
                        conf_score.append(pred_field_confidance)
                        #--Automatic approval of incident tickets based on threshold value--
                        if(t_value_enabled and float(t_value) <= confidence_score):
                            t_value_confidence_flag=t_value_confidence_flag+1 
                        
                        #if pred_field is assignment group.. pass it to get_assignee, to recieve assignee details back.
                        #if(pred_field=='assignment_group' and assignment_ini.lower() == "yes" and assignment_enabled):
                        if(pred_field== group_field_name and assignment_enabled):
                            pred_assignment_grp_lst.append(predicted_label)
                            #                   assignees = ResourceMasterData.find_assigneesForAssignmentGroups(pred_output_result)
                            #                   final_predictions['predicted_assigned_to'] = assignees[0]
                            final_predictions['possible_assignees'] = ResourceMasterData.find_possibleassignees(predicted_label)
                    
                        all_ok_flag = 1
                        
                    if(all_ok_flag):
                        final_predictions['predicted_fields'] = conf_score
                        final_predictions['CustomerID'] = customer_id
                        final_predictions['DatasetID'] = dataset_id

                        final_predictions_lst.append(final_predictions)
                    #--Automatic approval of incident tickets based on threshold value--    
                    if(t_value_enabled and total_fields_to_be_perdicted==t_value_confidence_flag):
                        temp_doc={}
                        temp_doc[ticket_id_field_name]=ticket[ticket_id_field_name]
                        for doc in conf_score:
                            
                            key=list(doc.keys())[0]
                            predicted_value=doc[key]
                            temp_doc[key]=predicted_value
                        
                        tickets_to_be_approved.append(temp_doc)          
                            
                #--calling assignment logic from new location--
                if(pred_assignment_grp_lst):
                    assignees = ResourceMasterData.find_assigneesForAssignmentGroups(pred_assignment_grp_lst)
                    logging.info('%s: values in pred assignment grp lst and %s: values in tickets to be approved'%(str(len(pred_assignment_grp_lst)),str(len(tickets_to_be_approved))))
                    sub_index=0
                    total_approve_tickets=len(tickets_to_be_approved)
                    if(len(pred_assignment_grp_lst)==len(final_predictions_lst)):
                        logging.info('%s: no. of assignment groups predicted and no. of tickets predicted are equal. Proceeding to allocation of resource'%RestService.timestamp())
                        for index in range(0,len(pred_assignment_grp_lst)):
                            assignee=assignees[index]
                            final_predictions_lst[index]['predicted_assigned_to']=assignee
                            #--Automatic approval of incident tickets based on threshold value-- 
                            if(sub_index<total_approve_tickets and t_value_enabled and tickets_to_be_approved[sub_index][ticket_id_field_name]==final_predictions_lst[index][ticket_id_field_name]):
                                tickets_to_be_approved[sub_index]['predicted_assigned_to']=assignee
                                sub_index=sub_index+1
                    else:
                        logging.info('%s: no. of assignment groups predicted and no. of tickets predicted are different! cannot assign resource'%RestService.timestamp())
                else:
                    logging.info("In application settings assignment_module is not enabled ...")
                
                #--Automatic approval of incident tickets based on threshold value-- 
                if(t_value_enabled and tickets_to_be_approved):
                    Predict.automaticTicketApproval(customer_id, dataset_id, tickets_to_be_approved)
                    #        data=json_util.dumps(tickets_to_be_approved)
                    #        resp=requests.put('http://127.0.0.1:5001/updatePredictedDetails/1/1', json=data)
                    #        print(resp)
                if(all_ok_flag):
                        try:
                            logging.info('%s: Trying to insert newly predicted record into TblPredictedData.'%RestService.timestamp())
                            MongoDBPersistence.predicted_tickets_tbl.insert_many(final_predictions_lst)
                            logging.info('%s: Record inserted successfully.'%RestService.timestamp())
                        except Exception as e:
                            logging.error('%s: Error occurred: %s '%(RestService.timestamp(),str(e)))
                if(len(garbage_tickets)>0):
                    result['DatasetID'] = -1
                    #resp = 'warning'
                    logging.info("%d tickets cannot be predicted.. dataset info missing"%len(garbage_tickets))
                else:
                    result['DatasetID'] = dataset_id
                    #resp = 'success'
                return json_util.dumps(result)
            else:


                # logic for different team users
                team_id = login_user['TeamID']
                user_dataset_id = MongoDBPersistence.teams_tbl.find_one({"TeamID": int(team_id)},{"_id":0, "DatasetID":1})
                MongoDBPersistence.predicted_tickets_tbl.delete_many({'CustomerID':customer_id, "DatasetID": user_dataset_id['DatasetID']})
                
                garbage_tickets = []
                ####### RB specific #######
                
                rt_tickets =  list(MongoDBPersistence.rt_tickets_tbl.find({'CustomerID':customer_id, "$or": [{status_field_name:'New'},{status_field_name:'Assigned'}], 'user_status':'Not Approved'},{'_id':0}))
                
                #print(rt_tickets)
                if(not rt_tickets):
                    logging.info('%s: There is nothing uploaded for prediction. Upload tickets data first & then try again.'%RestService.timestamp())
                    return "failure"
                #Current logic: predicting tickets one by one from TblIncidentRT
                #Other logic: Picking up all realtime tickets dataset by dataset from TblIncidentRT: Faster in some case
                
                pred_assignment_grp_lst=[]
                final_predictions_lst=[]
                dataset_id = rt_tickets[0]['DatasetID']
                white_lst_collection=list(MongoDBPersistence.whitelisted_word_tbl.find({'CustomerID':customer_id,'DatasetID':dataset_id}))
                #--Automatic approval of incident tickets based on threshold value--
                tickets_to_be_approved=[]
                logging.info('%s: fetching details from "assign_enable_tbl"'%RestService.timestamp())
                t_value_doc=MongoDBPersistence.assign_enable_tbl.find_one({})
                t_value_keys=list(t_value_doc.keys())
                logging.info('%s: assigning default value 0 for "t_value" and "False" for "t_value_enabled"'%RestService.timestamp())
                t_value=0         
                t_value_enabled=False
                if(t_value_doc and "t_value_enabled" in t_value_keys):
                    if(t_value_doc['t_value_enabled']=='true' and 'threshold_value' in t_value_keys):
                        logging.info('assigning value for "t_value" and for "t_value_enabled" from database!')
                        t_value=t_value_doc["threshold_value"]
                        t_value_enabled=True
                    else:
                        logging.info('%s: Either "t_value_enabled" is false or no "threshold_value" field in database'%RestService.timestamp())
                else:
                    logging.info('%s: Either "t_value_doc" not exist or no field "t_value_enabled" in database'%RestService.timestamp())
                
                if(t_value_doc and 'assignment_enabled' in list(t_value_doc.keys())):
                    assignment_enabled=True if t_value_doc['assignment_enabled']=='true' else False
                else:
                    logging.info('%s: Either "t_value_doc" not exist or no field "assignment_enabled" in database'%RestService.timestamp())
                    logging.info('assigning default value "True" for "assignment_enabled"')
                    assignment_enabled=True
                
                for ticket in rt_tickets:
                    all_ok_flag = 0
                    try:
                        dataset_id = ticket['DatasetID']
                        #print('dataset id is ' + str(dataset_id))
                    except Exception as e:
                        logging.error('%s: Error: %s'%(RestService.timestamp(),str(e)))
                        garbage_tickets.append(ticket[ticket_id_field_name])
                        logging.info('%s: Dataset id not found for the ticket Number: %s'%(RestService.timestamp(),ticket[ticket_id_field_name]))
                        continue
                    final_predictions = {}
                    final_predictions[ticket_id_field_name] = ticket[ticket_id_field_name]
            
                    #Fetch Customer choices
                    cust_name = MongoDBPersistence.customer_tbl.find_one({'CustomerID':customer_id},{'CustomerName':1, '_id':0})['CustomerName']
                    dataset_info_dict =  MongoDBPersistence.datasets_tbl.find_one({'CustomerID':customer_id, "DatasetID":dataset_id},{'DatasetName':1,'FieldSelections':1, '_id':0})
                    if(dataset_info_dict):
                        dataset_name = dataset_info_dict['DatasetName']
                    else:
                        logging.info('%s: Customer name not found in the record.'%RestService.timestamp())
                        return "failure"
                    fieldselection_list = dataset_info_dict['FieldSelections']
                    #print('field selection list is ' + str(fieldselection_list))
                    pred_fields_choices_list = []
                    #Pick up Approved customer choices 
                    for pred_fields in fieldselection_list:
                        if(pred_fields['FieldsStatus']=='Approved'):
                            pred_fields_choices_list = pred_fields['PredictedFields']
                            #print('predicted fields are ' + str(pred_fields_choices_list))
            
                    pred_field_list = []
                    for pre_field in pred_fields_choices_list:
                        pred_field_list.append(pre_field['PredictedFieldName'])
            
                    conf_score = []
                    #--Automatic approval of incident tickets based on threshold value--
                    t_value_confidence_flag=0  
                    total_fields_to_be_perdicted=len(pred_field_list)
                    for pred_field in pred_field_list:
                        pred_field_confidance = {}
                            #Based on each prediction field, get all corelated fields appended in a single field(Say in_field)
                            #Use feature selection algorithms to select best fields from training dataset
                        input_field_list = []
                        for input_field in pred_fields_choices_list:
                            if(input_field['PredictedFieldName'] == pred_field):
                                input_field_list = input_field['InputFields']
                                #print('input field list is ' + str(input_field_list))
                                algoName = input_field['AlgorithmName']
                        if(len(input_field_list)==0):
                            logging.info('%s: No input fields choosen for %s.'%(RestService.timestamp(),pred_field))
                            continue
                        #Concatinating input fields together into in_field
                        input_df = pd.DataFrame()   
                        input_df = pd.DataFrame([{input_field_list[0]:ticket[input_field_list[0]]}])
                        final_predictions[input_field_list[0]] = ticket[input_field_list[0]]
                        for input_field_ in input_field_list[1:]:
                            final_predictions[input_field_] = ticket[input_field_]
                            input_df[input_field_] = pd.DataFrame([{input_field_:ticket[input_field_]}])
                        
                        #input_df['in_field'] = input_df[input_field_list].astype(str).sum(axis=1)
                        input_df['in_field'] = ''
                        for field in input_field_list:
                            input_df['in_field'] += input_df[field] + ' --~||~-- '
                        input_df1 = pd.DataFrame()
                        input_df1['in_field'] = input_df['in_field']
                        
                        logging.info(input_df1.iloc[0]['in_field'])
                        in_field = 'in_field'
                        #Skips those tickets where there is no description field
                        input_df1 = input_df1[pd.notnull(input_df1[in_field])]
            
                        # for index,row in input_df1.iterrows():
                        #     row[in_field] = re.sub("[^_a-zA-Z]", " ", row[in_field])
                        #     # row[in_field] = row[in_field].lower()
                        #     input_df1[in_field][index] = row[in_field].lower()
                        
                        #Custom preprocessing call
                        customer_name = MongoDBPersistence.customer_tbl.find_one({'CustomerID':customer_id},{'CustomerName':1, '_id':0})['CustomerName']
                        class_name = customer_name + "_"+ "".join(dataset_name.split()) +"_Preprocessing"
                        module_name = "intent.custompreprocessing." + class_name
                        try:
                            module = importlib.import_module(module_name)
                            class_ = getattr(module, class_name)
                            input_df1 = class_.preprocess(input_df1, "predict")
                        except Exception as e:
                            logging.error('%s: Error occurred: %s ' % (RestService.timestamp(), str(e)))
                            logging.info("Error can be ignored if there is no customized pre-processing module uploaded. Going for basic cleaning of corpus ")
                            ## No custom preprocessing file present , so going for some basic cleaning
                            training_tkt_df = IncidentTraining.cleaningInputFields(input_df1,in_field)

                        input_df_list = input_df1['in_field'].tolist()
                        descr_df = [str(x) for x in input_df_list]
                        #   ----White Listed Word Logic---
                        found_white_lst_wrd=False
                        input_descr=descr_df[0]

                        try:
                            for white_lst_doc in white_lst_collection:# --loop 1--
                                if(white_lst_doc['PredictedField']==pred_field and white_lst_doc['WhiteListed_Words'] != []):#   --condition 1--
                                    for field_doc in white_lst_doc['WhiteListed_Words']:# --loop 2--
                                        for word in field_doc['Value']:# --loop 3--
                                            # word = word.lower()
                                            # wht_lst_wrd = '\\b'+word+'\\t'
                                            # wrd_exst_state = re.search(wht_lst_wrd,input_descr)
                                            if(word.lower() in input_descr):#   --condition 2--
                                                predicted_label=field_doc['Field_Name']
                                                logging.info('%s: found a match from white listed words collection'%RestService.timestamp())
                                                if(pred_field=='assignment_group'):#   --condition 3--
                                                    pred_assignment_grp_lst.append(predicted_label)
                                                    final_predictions['possible_assignees'] = ResourceMasterData.find_possibleassignees(predicted_label)
                                                #--condition 3--
                                                pred_field_confidance[pred_field] = predicted_label
                                                pred_field_confidance['ConfidenceScore'] = 1
                                                conf_score.append(pred_field_confidance)
                                                found_white_lst_wrd=True
                                                #--Automatic approval of incident tickets based on threshold value--
                                                t_value_confidence_flag=t_value_confidence_flag+1 
                                                logging.info('%s: successfully updated conf_score doc with white listed words details '%RestService.timestamp())
                                                break
                                            #--condition 2--
                                        # --loop 2--
                                        if(found_white_lst_wrd):
                                            break
                                    #--loop 3--
                                #--condition 1--
                                if found_white_lst_wrd:
                                    break
                            #--loop 1--
                        except Exception as e:
                            logging.error('%s: Exception: %s'%(RestService.timestamp(),str(e)))
                        if(found_white_lst_wrd):
                            all_ok_flag = 1
                            logging.info('%s: match found!, continueing the loop with next predicted field'%RestService.timestamp())
                            continue
                        #   ------------------------------
                        
                        pred_output_result = []
            
                        vocab_path = 'data/' + cust_name + "__" + dataset_name + '__' + in_field + "__" + pred_field + "__" + "Approved" + "__" +"Vocabulary.pkl"
                        model_path = 'models/' + cust_name + "__" + dataset_name + '__' + algoName + "__" + pred_field + "__" + "Approved" + "__" +"Model.pkl"
                        vocab_file = Path(vocab_path)
                        model_file = Path(model_path)
                        if(vocab_file.is_file()):
                            tfidf = joblib.load(vocab_path)
                        else:
                            logging.info('%s: Vocabulary file not found for %s field.. please train algo, save the choices & try again.'%(RestService.timestamp(),pred_field))
                            continue
            
                        if(model_file.is_file()):
                            fittedModel = joblib.load(model_file)
                        else:
                            logging.info('%s: ML Model file not found for %s field.. please train algo, save the choices & try again.'%(RestService.timestamp(),pred_field))
                            continue
                        pred_output_result = fittedModel.predict(tfidf.transform(descr_df).toarray())
                        id_to_labels = MongoDBPersistence.datasets_tbl.find_one({'CustomerID':customer_id, "DatasetID": dataset_id},{"_id":0,"IdToLabels":1})
                        if(id_to_labels):
                            id_to_labels_dict = id_to_labels["IdToLabels"]
                            inside_id_to_label = id_to_labels_dict[str(pred_field)]
                        else:
                            logging.info('%s: De-map data not found for %s field.'%(RestService.timestamp(),pred_field))

                        predicted_label = inside_id_to_label[str(pred_output_result[0])]
                        #predicted_label= str(pred_output_result[0])
                        
                        # assign_grp = str(pred_output_result[0])
                        pred_field_confidance[pred_field] = predicted_label
                        
                        confidence_score = float("{0:.2f}".format(max(fittedModel.predict_proba(tfidf.transform(descr_df).toarray())[0])))
                        pred_field_confidance['ConfidenceScore'] = confidence_score
                        conf_score.append(pred_field_confidance)
                        #--Automatic approval of incident tickets based on threshold value--
                        if(t_value_enabled and float(t_value) <= confidence_score):
                            t_value_confidence_flag=t_value_confidence_flag+1 
       
                        if(pred_field== group_field_name and assignment_enabled):
                            pred_assignment_grp_lst.append(predicted_label)
                            #                   assignees = ResourceMasterData.find_assigneesForAssignmentGroups(pred_output_result)
                            #                   final_predictions['predicted_assigned_to'] = assignees[0]
                            final_predictions['possible_assignees'] = ResourceMasterData.find_possibleassignees(predicted_label)
                    
                        all_ok_flag = 1
                        
                    if(all_ok_flag):
                        final_predictions['predicted_fields'] = conf_score
                        final_predictions['CustomerID'] = customer_id
                        final_predictions['DatasetID'] = dataset_id
                        
                        final_predictions_lst.append(final_predictions)
                #--Automatic approval of incident tickets based on threshold value--    
                    if(t_value_enabled and total_fields_to_be_perdicted==t_value_confidence_flag):
                        temp_doc={}
                        temp_doc[ticket_id_field_name]=ticket[ticket_id_field_name]
                        for doc in conf_score:
                            
                            key=list(doc.keys())[0]
                            predicted_value=doc[key]
                            temp_doc[key]=predicted_value
                        
                        tickets_to_be_approved.append(temp_doc)          
                            
                #--calling assignment logic from new location--
                if(pred_assignment_grp_lst):
                    assignees = ResourceMasterData.find_assigneesForAssignmentGroups(pred_assignment_grp_lst)
                    logging.info('%s: values in pred assignment grp lst and %s: values in tickets to be approved'%(str(len(pred_assignment_grp_lst)),str(len(tickets_to_be_approved))))
                    sub_index=0
                    total_approve_tickets=len(tickets_to_be_approved)
                    if(len(pred_assignment_grp_lst)==len(final_predictions_lst)):
                        logging.info('%s: no. of assignment groups predicted and no. of tickets predicted are equal. Proceeding to allocation of resource'%RestService.timestamp())
                        for index in range(0,len(pred_assignment_grp_lst)):
                            assignee=assignees[index]
                            final_predictions_lst[index]['predicted_assigned_to']=assignee
                            #--Automatic approval of incident tickets based on threshold value-- 
                            if(sub_index<total_approve_tickets and t_value_enabled and tickets_to_be_approved[sub_index][ticket_id_field_name]==final_predictions_lst[index][ticket_id_field_name]):
                                tickets_to_be_approved[sub_index]['predicted_assigned_to']=assignee
                                sub_index=sub_index+1
                    else:
                        logging.info('%s: no. of assignment groups predicted and no. of tickets predicted are different! cannot assign resource'%RestService.timestamp())
                else:
                    logging.info("In application settings assignment_module is not enabled ...")
                
                #--Automatic approval of incident tickets based on threshold value-- 
                if(t_value_enabled and tickets_to_be_approved):
                    Predict.automaticTicketApproval(customer_id, dataset_id, tickets_to_be_approved)
                    #        data=json_util.dumps(tickets_to_be_approved)
                    #        resp=requests.put('http://127.0.0.1:5001/updatePredictedDetails/1/1', json=data)
                    #        print(resp)
                if(all_ok_flag):
                        try:
                            logging.info('%s: Trying to insert newly predicted record into TblPredictedData.'%RestService.timestamp())
                            MongoDBPersistence.predicted_tickets_tbl.insert_many(final_predictions_lst)
                            logging.info('%s: Record inserted successfully.'%RestService.timestamp())
                        except Exception as e:
                            logging.error('%s: Error occurred: %s '%(RestService.timestamp(),str(e)))
                if(len(garbage_tickets)>0):
                    result['DatasetID'] = -1
                    #resp = 'warning'
                    logging.info("%d tickets cannot be predicted.. dataset info missing"%len(garbage_tickets))
                else:
                    result['DatasetID'] = dataset_id
                    #resp = 'success'
                return json_util.dumps(result)
        else:
            logging.info("%s User is not authenticated"%RestService.timestamp())
            return "failure"
    
        
    
    
    