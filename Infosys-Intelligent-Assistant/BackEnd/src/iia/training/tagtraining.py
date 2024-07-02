__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

import csv
import datetime
import io
import itertools
import json
import os
import pickle
import re
import traceback

import joblib
import numpy as np
import pandas as pd
from bson import json_util
from flask import request
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

from iia.persistence.mappingpersistence import MappingPersistence
from iia.persistence.mongodbpersistence import MongoDBPersistence
from iia.restservice import RestService
from iia.utils.log_helper import get_logger

logging = get_logger(__name__)
()
app = RestService.getApp()


@app.route('/api/uploadTagsTrainingData/<int:customer_id>/<dataset_name>/<team_name>', methods=["POST"])
def db_insert_tags_training_tickets(customer_id, dataset_name, team_name):
    return TagsTraining.db_insert_tags_training_tickets(customer_id, dataset_name, team_name)


@app.route('/api/tagTrain/<int:customer_id>/<int:dataset_id>', methods=["POST"])
def tagTrain(customer_id, dataset_id):
    print("Execution started. In tagTrain function..")
    return TagsTraining.tagTrain(customer_id, dataset_id)


@app.route("/api/Tags/<incident_no>/<int:customer_id>/<int:dataset_id>", methods=["GET"])
def Tags(incident_no, customer_id, dataset_id):
    return TagsTraining.Tags(incident_no, customer_id, dataset_id)


@app.route("/api/getTagBasedField/<int:customer_id>/<int:dataset_id>")
def getTagBasedField(customer_id, dataset_id):
    return TagsTraining.getTagBasedField(customer_id, dataset_id)


@app.route("/api/loadCluster", methods=["GET"])
def loadCluster():
    return TagsTraining.loadCluster()


@app.route("/api/saveClusterDetails/<int:customer_id>/<int:dataset_id>", methods=["POST"])
def saveClusterDetails(customer_id, dataset_id):
    return TagsTraining.saveClusterDetails(customer_id, dataset_id)


class TagsTraining(object):
    '''
    classdocs
    '''

    def __init__(self, params):
        '''
        Constructor
        '''

    @staticmethod
    def compute_parameters(predicted_features, support):
        # TEST DATASET
        D = predicted_features

        n_transactions = len(D)

        # Compute candidate 1-itemset
        C1 = {}
        for element in D:
            for word in element:
                if word not in C1.keys():
                    C1[word] = 1
                else:
                    count = C1[word]
                    C1[word] = count + 1

        # Compute frequent 1-itemset
        L1 = []
        for key in C1:
            if (100 * C1[key] / n_transactions) >= support:
                list = []
                list.append(key)
                L1.append(list)

        return D, L1

    """has_infrequent_subsets function to determine if pruning is required to remove unfruitful candidates (c) using the Apriori property, with prior knowledge of frequent (k-1)-itemset (Lk_1)"""

    @staticmethod
    def has_infrequent_subset(c, Lk_1, k):
        list = []
        list = TagsTraining.findsubsets(c, k)
        for item in list:
            s = []
            for l in item:
                s.append(l)
            s.sort()
            if s not in Lk_1:
                return True
        return False

    """apriori_gen function to compute candidate k-itemset, (Ck) , using frequent (k-1)-itemset, (Lk_1)"""

    @staticmethod
    def apriori_gen(Lk_1, k):
        length = k
        Ck = []
        for list1 in Lk_1:
            for list2 in Lk_1:
                count = 0
                c = []
                if list1 != list2:
                    while count < length - 1:
                        if list1[count] != list2[count]:
                            break
                        else:
                            count += 1
                    else:
                        if list1[length - 1] < list2[length - 1]:
                            for item in list1:
                                c.append(item)
                            c.append(list2[length - 1])
                            if not TagsTraining.has_infrequent_subset(c, Lk_1, k):
                                Ck.append(c)
                                c = []
        return Ck

    """function to compute 'm' element subsets of a set S"""

    @staticmethod
    def findsubsets(S, m):
        return set(itertools.combinations(S, m))

    """frequent_itemsets function to compute all frequent itemsets"""

    @staticmethod
    def frequent_itemsets(D, L1, support):
        k = 2
        Lk_1 = []
        Lk = []
        L = []
        count = 0
        transactions = 0
        for item in L1:
            Lk_1.append(item)
        while Lk_1 != []:
            Ck = []
            Lk = []
            Ck = TagsTraining.apriori_gen(Lk_1, k - 1)
            for c in Ck:
                count = 0
                transactions = 0
                s = set(c)
                for T in D:
                    transactions += 1
                    t = set(T)
                    if s.issubset(t) == True:
                        count += 1
                if (100 * count / transactions) >= support:
                    c.sort()
                    Lk.append(c)
            Lk_1 = []
            for l in Lk:
                Lk_1.append(l)
            if Lk != []:
                L.append(Lk)

        return L

    """generate_association_rules function to mine and print all the association rules with given support and confidence value"""

    @staticmethod
    def generate_association_rules(D, confidence, L1, support):
        rule_list = []
        support_list = []
        confidence_list = []
        element1_list = []
        element2_list = []

        s = []
        r = []
        length = 0
        count = 1
        inc1 = 0
        inc2 = 0
        num = 1
        m = []
        L = TagsTraining.frequent_itemsets(D, L1, support)
        for list in L:
            for l in list:
                length = len(l)
                count = 1
                while count < length:
                    s = []
                    r = TagsTraining.findsubsets(l, count)
                    count += 1
                    for item in r:
                        inc1 = 0
                        inc2 = 0
                        s = []
                        m = []
                        for i in item:
                            s.append(i)
                        for T in D:
                            if set(s).issubset(set(T)) == True:
                                inc1 += 1
                            if set(l).issubset(set(T)) == True:
                                inc2 += 1
                        if 100 * inc2 / inc1 >= confidence:
                            for index in l:
                                if index not in s:
                                    m.append(index)
                            # print("Rule#  %d : %s ==> %s %d \t %d" %(num, s, m, 100*inc2/len(D), 100*inc2/inc1))
                            rule_list.append("{0} ==> {1}".format(s, m))
                            support_list.append(100 * inc2 / len(D))
                            confidence_list.append(100 * inc2 / inc1)
                            element1_list.append(str(s).strip()[2:-2])
                            element2_list.append(str(m).strip()[2:-2])
                            num += 1

        return rule_list, support_list, confidence_list, element1_list, element2_list

    @staticmethod
    def db_insert_tags_training_tickets(customer_id, dataset_name, team_name):

        try:

            field_mapping = MappingPersistence.get_mapping_details(customer_id)
            ticket_id_field_name = field_mapping['Ticket_ID_Field_Name']
           
            new_dataset_flag = 0
            file = request.files['trainingData']
            dataset_ = MongoDBPersistence.teams_tbl.find_one({"CustomerID": customer_id, "TeamName": team_name},
                                                             {"TagsDatasetID": 1, "_id": 0})
            if (dataset_):
                dataset_dict = {}
                # Dataset exist for the team
                logging.info('%s: Getting old tag dataset details.' % RestService.timestamp())
                dataset_id = dataset_["TagsDatasetID"]
            else:
                # Newly adding the dataset
                logging.info('%s: Adding new tag dataset.' % RestService.timestamp())
                # getting max dataset id for the customer, so that new dataset id = old + 1
                dataset_dict = MongoDBPersistence.tag_dataset_tbl.find_one(
                    {"CustomerID": customer_id, "TagsDatasetID": {"$exists": True}}, {'_id': 0, "TagsDatasetID": 1},
                    sort=[("TagsDatasetID", -1)])
                if (dataset_dict):
                    last_dataset_id = dataset_dict['TagsDatasetID']
                else:
                    last_dataset_id = 0
                    logging.info('%s: Adding tag dataset for very first team.' % RestService.timestamp())

                # New dataset id for the customer
                dataset_id = last_dataset_id + 1

                new_dataset_dict = {}
                new_dataset_dict["TagsDatasetID"] = dataset_id
                new_dataset_dict["TagsDatasetName"] = dataset_name
                new_dataset_dict["CustomerID"] = customer_id
                new_dataset_flag = 1
            if not file:
                return "No file"
            elif (not '.csv' in str(file)):
                return "Upload csv file."
            stream = io.StringIO(file.stream.read().decode("latin-1"), newline=None)
            csv_input = csv.reader(stream)
            df_data = []

            for row in csv_input:
                df_data.append(row)
            headers = df_data.pop(0)
            headers = [c.lower() for c in headers]

            df = pd.DataFrame(df_data, columns=headers)
            list_columns = list(df.columns)
            df['CustomerID'] = customer_id
            df['TagsDatasetID'] = dataset_id
            df['TagsTrainingFlag'] = 0

            list_columns = ["_".join(re.sub("[^a-zA-Z]", " ", col).strip().split(" ")) for col in list_columns]

            if (ticket_id_field_name not in df.columns):
                logging.info('%s: Please rename ticket_id/Incident_id column to "number".' % RestService.timestamp())
                return 'failure'

            # remove special chars between the name of column
            df.columns = ["_".join(re.sub("[^a-zA-Z]", " ", col).strip().split(" ")) for col in df.columns]

            # Remove duplicate columns if there any (Based on Incident number)
            df.drop_duplicates(subset=ticket_id_field_name, keep='first', inplace=True)
            csv_df_cols = df.columns

            if (len(set(csv_df_cols)) < len(csv_df_cols)):
                logging.info(
                    '%s: Duplicate columns, please rename the duplicate column names..' % RestService.timestamp())
                return 'failure'

            current_row_count = df.shape[0]
            prev_ticket_count = MongoDBPersistence.tag_dataset_tbl.find_one(
                {"CustomerID": customer_id, "TagsDatasetID": dataset_id}, {"TicketCount": 1, "_id": 0})
            if (prev_ticket_count):
                prev_ticket_count = prev_ticket_count['TicketCount']
                row_count = current_row_count + prev_ticket_count
            else:
                row_count = current_row_count

            json_str = df.to_json(orient='records')
            json_data = json.loads(json_str)

            logging.info('%s: Trying to insert records into TblTagTraining...' % RestService.timestamp())
            MongoDBPersistence.tag_training_tbl.insert_many(json_data)
            if (new_dataset_flag):
                new_dataset_dict["TicketCount"] = row_count
                new_dataset_dict["ColumnNames"] = list_columns
                logging.info('%s: Trying to insert new dataset into TblTagDataset...' % RestService.timestamp())
                MongoDBPersistence.tag_dataset_tbl.insert_one(new_dataset_dict)
                logging.info('%s: Trying to update TblTeams with tag Dataset details...' % RestService.timestamp())
                MongoDBPersistence.teams_tbl.update_one({'CustomerID': customer_id, "TeamName": team_name}, \
                                                        {"$set": {"TagsDatasetID": dataset_id}}, upsert=False)
            else:
                dataset_dict["TicketCount"] = row_count
                dataset_dict["ColumnNames"] = list_columns
                MongoDBPersistence.tag_dataset_tbl.update_one({'CustomerID': customer_id, "TagsDatasetID": dataset_id}, \
                                                              {"$set": {"TicketCount": dataset_dict["TicketCount"],
                                                                        "ColumnNames": dataset_dict["ColumnNames"]}},
                                                              upsert=False)
            logging.info('%s: Records inserted successfully.' % RestService.timestamp())
            resp = "success"
        except Exception as e:
            logging.error('%s: Error occurred: %s ' % (RestService.timestamp(), str(e)))
            logging.error(
                '%s: Possible error: Data format in csv not matching with database constarints.(unique key & not null)' % RestService.timestamp())
            resp = 'failure'
        return resp

    @staticmethod
    def cleaningInputFields(df, in_field):
        print("Inside line break method")
        for index, row in df.iterrows():
            row[in_field] = re.sub(r'\n', " ", row[in_field])
            row[in_field] = re.sub("[^A-Za-z0-9]+", " ", row[in_field])
            df[in_field][index] = row[in_field].lower()
        return df

    @staticmethod
    def get_data():
        print("In get data function. Below are the column names")
        try:
            ()
            row_list = list(MongoDBPersistence.tag_training_tbl.find({}, {"_id": 0}))
            print("column list")
            print(row_list[0].keys())
            print("number of rows", len(row_list))
            if len(row_list) > 0:
                df = pd.DataFrame(columns=list(row_list[0].keys()))
            else:
                print("No training data found into the table")

            print("dataframe shape ", df.shape)
            count = 0
            for row in row_list:
                print("processing ", count)
                count += 1
                df = df.append(row, ignore_index=True)
            print("dataframe shape ", df.shape)

            return df
        except Exception as e:
            logging.error('%s: Error occurred: %s ' % (RestService.timestamp(), str(e)))
            print(traceback.format_exc())
            newDF = pd.DataFrame()
            return newDF

    @staticmethod
    def cleanHtml(sentence):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, ' ', str(sentence))
        return cleantext

    # function to clean the word of any punctuation or special characters
    @staticmethod
    def cleanPunc(sentence):
        cleaned = re.sub(r'[?|!|\'|"|#]', r'', sentence)
        cleaned = re.sub(r'[.|,|)|(|\|/]', r' ', cleaned)
        cleaned = cleaned.strip()
        cleaned = cleaned.replace("\n", " ")
        return cleaned

    @staticmethod
    def keepAlpha(sentence):
        alpha_sent = ""
        for word in sentence.split():
            alpha_word = re.sub('[^a-z A-Z]+', ' ', word)
            alpha_sent += alpha_word
            alpha_sent += " "
        alpha_sent = alpha_sent.strip()
        return alpha_sent

    @staticmethod
    def clean_text(text):
        text = text.lower()
        text = TagsTraining.cleanHtml(text)
        text = TagsTraining.cleanPunc(text)
        text = TagsTraining.keepAlpha(text)

        return text

    @staticmethod
    def remove_stopwords(sentence):
        stop_words = set(stopwords.words('english'))
        stop_free = " ".join([i for i in sentence.split() if i not in stop_words])
        return stop_free

    @staticmethod
    def lemmatize_text(sentence):
        lemma = WordNetLemmatizer()
        lemmatized = " ".join(lemma.lemmatize(word) for word in sentence.split())
        return lemmatized

    @staticmethod
    def get_vectorized_representation(text):
        with open("models/tagging/tfidf_vector_clustering_ShortDescription_3Fields.pkl", "rb") as f:
            vectorizer = TfidfVectorizer(stop_words='english',
                                         vocabulary=pickle.load(f))
        vectorized_text = vectorizer.fit_transform(text)
        terms = vectorizer.get_feature_names()

        return terms, vectorized_text

    @staticmethod
    def load_and_predict(vectorized_text):
        print("In load and predict method. dev log")
        model_loaded = joblib.load("models/tagging/model_clustering_3Fields.sav")
        print("Model has been loaded. dev log")
        predictions = model_loaded.predict(vectorized_text)
        print("Prediction has been done.")

        return model_loaded, predictions

    
    @staticmethod
    def CustomTags(desc, customer_id, dataset_id):
        try:
            desc = re.sub('([^\s\w]|_)+', ' ', desc).split()
            with open('data/stopwords.csv', 'r') as readFile:
                reader = csv.reader(readFile)
                list1 = list(reader)
                stopwords_english = list1[0]
                readFile.close()
            if stopwords_english is None:
                stopwords_english = []

            desc_lwr = [w.lower() for w in desc]
            stopwords_english = [w.lower() for w in stopwords_english]
            desc_list = list(set(desc_lwr) - set(stopwords_english))
            print(desc_list)
            cluster_list = []
            details = \
            MongoDBPersistence.cluster_details_tbl.find_one({'customer_id': customer_id, 'dataset_id': dataset_id, },
                                                            {'_id': 0, 'cluster_details': 1})['cluster_details']
            for clus in details:
                print(type(clus))
                if ('customValues' in clus):
                    for value in clus['customValues']:
                        if value.lower() in desc_list:
                            cluster_list.append(clus['clusterName'])

            print(cluster_list)
            return cluster_list
        except Exception as e:
            print(str(e))
            return []

    @staticmethod
    def get_predicted_features(total_terms, cluster_coordinates, test_features):
        temp_df = pd.DataFrame(columns=total_terms)
        for row_num in range(cluster_coordinates.shape[0]):
            temp_df.loc[row_num] = cluster_coordinates[row_num]

        # creating temporary array
        tarray = np.array(test_features)
        test_start_index = temp_df.shape[0]
        for row_num in range(tarray.shape[0]):
            temp_df.loc[test_start_index + row_num] = tarray[row_num]

        single_prediction_result = temp_df.loc[14]
        results_list = single_prediction_result.sort_values(ascending=False)[:5]

        return results_list

    @staticmethod
    def get_association(predicted_tags):
        with open("models/tagging/association_rules_with_resolution.pkl", "rb") as f:
            rule_df = pickle.load(f)
        filtered_rule_df = rule_df.loc[
            rule_df['element1'].isin(predicted_tags) | rule_df['element2'].isin(predicted_tags)]
        sorted_rule_df = filtered_rule_df.sort_values(by=['Confidence'], ascending=False)
        unique_tags = []
        adjacant_confidence_scores = []
        for i, row in sorted_rule_df.iterrows():
            if 'close_notes' in row['element1'] and row['element1'] not in unique_tags:
                unique_tags.append(row['element1'])
                adjacant_confidence_scores.append(row['Confidence'])
        final_list = {}
        for tag, score in zip(unique_tags, adjacant_confidence_scores):
            final_list[tag] = score
            print(tag, score)

        return list(final_list.keys())

    @staticmethod
    def Tags(incident_no, customer_id, dataset_id):

        try:
            rt_doc = MongoDBPersistence.rt_tickets_tbl.find_one(
                {'CustomerID': customer_id, 'DatasetID': dataset_id, 'number': incident_no},
                {'_id': 0, 'description': 1, 'subcategory': 1, 'category': 1})
            all_clms = MongoDBPersistence.datasets_tbl.find_one({'CustomerID': customer_id, 'DatasetID': dataset_id},
                                                                {'_id': 0, 'ColumnNames': 1})['ColumnNames']
            short_description = rt_doc['description']
            category = rt_doc['category']
            sub_category = rt_doc['subcategory']
            text = TagsTraining.clean_text(short_description)

            # get vectorized representation of the data
            terms, vectorized_text = TagsTraining.get_vectorized_representation([text])

            one_hot_columns, features = TagsTraining.get_combined_text_and_categorical_features(vectorized_text,
                                                                                                [category,
                                                                                                 sub_category])

            # load the model and make predictions
            model_loaded, predicted_cluster = TagsTraining.load_and_predict(features)
            print("Predicted cluster:", predicted_cluster)

            # get features from the text example which contributed into predicting the cluster(top 5 only for now)
            predicted_tags = TagsTraining.get_predicted_features(terms + one_hot_columns, model_loaded.cluster_centers_,
                                                                 features)
            predicted_tags = list(dict(predicted_tags).keys())[:5]
            print("Predicted tags from the predicted cluster:", predicted_tags)
            split_count = 0
            if ('close_notes' in all_clms):
                associated_resolution = TagsTraining.get_association(predicted_tags)
                print("Association results:", associated_resolution)
                split_count = 2
            else:
                print("Association is not performed.")
                associated_resolution = predicted_tags
                split_count = 1

            predicted_tags_cleaned = []

            for i in associated_resolution:
                if len(i.split("_")) > split_count:
                    predicted_tags_cleaned.append("".join(i.split("_")[split_count:]))
                else:
                    predicted_tags_cleaned.append(i)

            # take only top 5
            print("Predicted tags count:", len(predicted_tags_cleaned))
            if len(predicted_tags_cleaned) > 0:
                predicted_tags_cleaned = predicted_tags_cleaned[:5]
            return json_util.dumps(predicted_tags_cleaned)
        except Exception as e:
            print(str(e))
            return str(e)


    @staticmethod
    def get_combined_text_and_categorical_features(vectorized_text, test_categorical_values):
        # load all the one-hot-encoded columns
        with open("models/tagging/one_hot_columns_3Fields.pkl", "rb") as f:
            one_hot_columns = pickle.load(f)

        # start preparing 1/0 row for the test row
        one_hot_val_arr = np.zeros(len(one_hot_columns))

        ##split at first _ occurence
        index = 0
        for col in one_hot_columns:
            for val in test_categorical_values:
                if val == col[col.find("_") + 1:]:
                    one_hot_val_arr[index] = 1
                    break

            index += 1

        print("1/0 row has been prepared for the test example")

        # make temporary dataframe
        one_hot_df = pd.DataFrame(columns=one_hot_columns)

        start_index = one_hot_df.shape[0]
        one_hot_df.loc[start_index] = one_hot_val_arr
        dense_vectorized_text = pd.DataFrame(vectorized_text.todense())
        test_features = pd.concat([dense_vectorized_text, one_hot_df], axis=1)

        print("One hot columns and test features has been returned.")
        return one_hot_columns, test_features


    def get_predicted_features(total_terms, cluster_coordinates, test_features):
        temp_df = pd.DataFrame(columns=total_terms)
        for row_num in range(cluster_coordinates.shape[0]):
            temp_df.loc[row_num] = cluster_coordinates[row_num]
            
        #creating temporary array
        tarray = np.array(test_features)
        test_start_index = temp_df.shape[0]
        for row_num in range(tarray.shape[0]):
            temp_df.loc[test_start_index + row_num] = tarray[row_num]
            
        single_prediction_result = temp_df.loc[14]
        results_list = single_prediction_result.sort_values(ascending=False)[:5]
        
        return results_list

        print("In tagTrain method in the class..")
        
        try:
            data = request.get_json()
            training_start_date=datetime.datetime.now()
            tag_column=data['TagColName']
            tag_based_column=data['TagBasedCol']
            customer_name = MongoDBPersistence.customer_tbl.find_one({'CustomerID':customer_id},{'CustomerName':1, '_id':0})['CustomerName']
            dataset_name = MongoDBPersistence.tag_dataset_tbl.find_one({'CustomerID':customer_id,"TagsDatasetID" : dataset_id},{'TagsDatasetName':1, '_id':0})['TagsDatasetName']
            for filename in os.listdir("models/tagging"):
                file_list = filename.split('__')
                if(customer_name in file_list):
                    if(dataset_name in file_list):
                        if('tags' in file_list):
                            os.remove("models/tagging/"+filename)
                            
            df = TagsTraining.get_data(tag_column,tag_based_column)
            print("Data has been populated...")
            #df = pd.read_csv('HersheyDump_tagged.csv', usecols=['Tags', 'Short Description'], encoding = "ISO-8859-1")
            if df.empty:
                return 'csv has some issues.Check the logs'
            #drop null values
            df = df.dropna(how='any',axis=0) 
            
            #get the tags count for each row
            df['tag_count'] = df[tag_column].apply(lambda x: len(str(x).split(';')))
            
            #count the unique tags and put them into a list
            unique_tags_cleaned = []
            for tag in df[tag_column]:
                for t in str(tag).split(";"):
                    unique_tags_cleaned.append(t)
            
            #print("Maximum number of tags in a single example:", max(df['tag_count']))
            #print("Total number of unique tags:", len(list(set(unique_tags_cleaned))))
            
            tag_col_name_list = []
            
            #add separate columns for every tag
            for tag in range(max(df['tag_count'])):
                df['tag'+str(tag+1)] = np.nan
                tag_col_name_list.append('tag'+str(tag+1))
            
            #edit every NaN values with thier respective tags in each row
            for index, row in df.iterrows():
                tags_list = row[tag_column].split(';')
                for i in range(len(tags_list)):
                    col_name = ['tag'+str(i+1)]
                    df.loc[index, col_name] = tags_list[i]
            
            #remove unnecessary columns
            df_processed = df.drop([tag_column, 'tag_count'], axis=1)
            
            # start preparing the columns according to the multi-label-classification problem
            df_processed = pd.get_dummies(df_processed, columns=tag_col_name_list, prefix=None)
            
            total_tags_list = list(df_processed.columns)
            
            temp = [] 
            tags_to_remove = []
            for tag in total_tags_list:
                if tag not in temp or tag == "":
                    temp.append(tag)
                else:
                    tags_to_remove.append(tag)
            
            #remove duplicate columns from the dataframe
            df_processed = df_processed.drop(tags_to_remove, axis=1)
            
            pickle.dump(df_processed.columns, open('models/tagging/'+customer_name+'__'+dataset_name+'__'+'total__tags__file.pkl', 'wb'))
            print("All the tags has been saved in the models/tagging folder with the name "+customer_name+'__'+dataset_name+'__'+"total__tags__file.pkl")
            
            #df = pd.read_csv("processed_data.csv")
            rowSums = df_processed.iloc[:,2:].sum(axis=1)
            clean_comments_count = (rowSums==0).sum(axis=0)
            
            print("Total number of tickets = ",len(df_processed))
            print("Number of tickets with no tags = ",clean_comments_count)
            print("Number of tickets with tags =",(len(df_processed)-clean_comments_count))
            
            df1 = df_processed[rowSums != 0]
            
            df1[tag_based_column] = df1[tag_based_column].str.lower()
            df1[tag_based_column] = df1[tag_based_column].apply(TagsTraining.cleanHtml)
            df1[tag_based_column] = df1[tag_based_column].apply(TagsTraining.cleanPunc)
            df1[tag_based_column] = df1[tag_based_column].apply(TagsTraining.keepAlpha)

            train, test = train_test_split(df1, random_state=42, test_size=0.05, shuffle=True)
            
            train_text = train[tag_based_column]
            test_text = test[tag_based_column]
            
            vectorizer = TfidfVectorizer(strip_accents='unicode', analyzer='word', ngram_range=(1,3), norm='l2')
            vectorizer.fit(train_text)
            vectorizer.fit(test_text)
            
            pickle.dump(vectorizer.vocabulary_, open('models/tagging/'+customer_name+'__'+dataset_name+'__'+"tfidf__tags__vector.pkl","wb"))
            
            print("The vocabulary has been saved with the name: "+customer_name+'__'+dataset_name+'__'+"tfidf__tags__vector.pkl in the models/tagging directory.")
            
            x_train = vectorizer.transform(train_text)
            y_train = train.drop(labels = [tag_based_column], axis=1)
            
            x_test = vectorizer.transform(test_text)
            y_test = test.drop(labels = [tag_based_column], axis=1)
            
            classifier_lblPwr = LabelPowerset(RandomForestClassifier(n_estimators=10))
            
            # train
            classifier_lblPwr.fit(x_train, y_train)
            
            # predict
            predictions = classifier_lblPwr.predict(x_test)
            
            # accuracy
            print("Accuracy = ",accuracy_score(y_test,predictions))
            
            joblib.dump(classifier_lblPwr, 'models/tagging/'+customer_name+'__'+dataset_name+'__'+'model__tags__tagging.sav')
            print("Model is saved in the models/tagging folder. File name is "+customer_name+'__'+dataset_name+'__'+"model__tags__tagging.sav")
            
            MongoDBPersistence.tag_training_tbl.update_many({'CustomerID': customer_id, "TagsDatasetID": dataset_id},{"$set": {"TagsTrainingFlag": 1}})
            training_end_date =datetime.datetime.now()
            training_stats = {}
            training_stats['TrainingCompletedFlag'] = 'Completed'
            training_stats['TrainingStartedBy'] = os.getlogin()
            training_stats['TrainingStartDate'] = training_start_date
            training_stats['TrainingEndDate'] = training_end_date
            training_stats['CompletedStatus'] = 100
            tag_based_field=[]
            tag_based_field.append(tag_based_column)
            MongoDBPersistence.tag_dataset_tbl.update_one({'CustomerID':customer_id,"TagsDatasetID" : dataset_id},{'$set':{'TagsTrainingStatus':training_stats,'TagBasedField':tag_based_field}},upsert=True)
            return 'Success'
        
        except Exception as e:
            logging.error('%s: Error: %s'%(RestService.timestamp,str(e)))
            print(traceback.format_exc())
            return 'Failure'
