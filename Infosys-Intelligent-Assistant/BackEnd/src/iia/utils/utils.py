__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

from pathlib import Path
import pandas as pd
import numpy as np
import time 
import os
import csv
from iia.persistence.mongodbpersistence import MongoDBPersistence
from iia.restservice import RestService
import joblib
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression  
from sklearn.cluster import KMeans    
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report
from collections import defaultdict
import re 
from iia.utils.log_helper import get_logger, log_setup
logging = get_logger(__name__)
import warnings
warnings.filterwarnings("ignore") 

with open('data/stopwords.csv', 'r') as readFile:
        reader = csv.reader(readFile)
        list1 = list(reader)  
        ENGLISH_STOP_WORDS = list1[0]
        readFile.close()
def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%r  %2.2f ms' % \
                  (method.__name__, (te - ts) * 1000))
        return result
    return timed
#Naming conventions for: ML model pickes- CustomerName__DatasetName__Algorithm__PredictField__Model.pkl
#Naming conventions for: Vocabulary pickes- CustomerName__DatasetName__inField__PredictField__Vocabulary.pkl
class Utils():
    def _load_data(self, df):
        df_encoded = pd.get_dummies(df,columns = self.additional_fields)
        print("df_encoded:",df_encoded.columns)
        data_for_input = df_encoded.drop([self.pred_field,"category_id"],axis=1)
        data_for_output = df_encoded["category_id"]
        data_for_additional_columns = df_encoded.drop([self.pred_field,"category_id",self.in_field],axis=1)
        List_additional_columns = list(data_for_additional_columns.columns)
        df_file = str(self.cust_name)+'__'+str(self.dataset_name)+'__'+str(self.in_field)+'__'+\
                                                str(self.pred_field) + '__'+'additionalcolumns.pkl'

        joblib.dump(List_additional_columns, 'data/'+df_file)
        X = data_for_input
        Y = data_for_output

        #getting stopwords based on the model
        if(self.training_status == 'InProgress' or self.training_status == 'Retraining'):
            stopwords_list = MongoDBPersistence.datasets_tbl.find_one({"CustomerID": self.customer_id,"DatasetID": self.dataset_id},{"Stopwords":1,"_id":0})
            if stopwords_list:
                stopwords_approved = stopwords_list['Stopwords'][1]['stopword']
                final_stopwords = ENGLISH_STOP_WORDS + stopwords_approved                
                print("Using approved Stopwords only without tuning")
            else:
                final_stopwords = ENGLISH_STOP_WORDS
                print("Using default Stopwords only")
        elif self.training_status == 'Tuning':
            stopwords_list = MongoDBPersistence.datasets_tbl.find_one({"CustomerID": self.customer_id,"DatasetID": self.dataset_id},{"Stopwords":1,"_id":0})
            if stopwords_list:
                stopwords_inprogress = stopwords_list['Stopwords'][0]['stopword']
                stopwords_approved = stopwords_list['Stopwords'][1]['stopword']
                final_stopwords = ENGLISH_STOP_WORDS + stopwords_inprogress + stopwords_approved
                
                print("Using inporgress + approved + default")
                logging.info("Using inporgress + approved + default")
            else:
                final_stopwords = ENGLISH_STOP_WORDS
                print("Using default Stopwords only with tuning") 
                logging.info("Using default Stopwords only with tuning") 
        else:
            logging.error('%s:No status found please provide a training status '%RestService.timestamp())        
        tfidf_vectorizer = TfidfVectorizer(input='content', encoding='utf-8',
                 decode_error='strict', strip_accents=None, lowercase=True, preprocessor=None,
                 tokenizer=None, analyzer='word', stop_words=final_stopwords,
                 token_pattern=r"(?u)\b\w\w+\b",
                 ngram_range=(1, 1), max_df=1.0, min_df=1,
                 max_features=None, vocabulary=None, binary=False, 
                 dtype=np.int64, norm='l2', use_idf=True, smooth_idf=True, sublinear_tf=False)
        X_tfidf = tfidf_vectorizer.fit_transform(X[self.in_field])

        #file for tf-idf vocabulory for important feature extraction
        vocab_file = str(self.cust_name)+'__'+str(self.dataset_name)+'__'+str(self.in_field)+'__'+\
                                                str(self.pred_field) + '__'+'Vocab.pkl'

        joblib.dump(tfidf_vectorizer.vocabulary_, 'data/'+vocab_file)
        
        fileName = str(self.cust_name)+'__'+str(self.dataset_name)+'__'+str(self.in_field)+'__'+str(self.pred_field) + '__'+ self.training_status + '__'+'Vocabulary.pkl'
        joblib.dump(tfidf_vectorizer, 'data/'+fileName)
        transformer = ColumnTransformer([('tfidf', tfidf_vectorizer, self.in_field)],remainder='passthrough')
        print("in_field:",self.in_field)

        X_transform = transformer.fit_transform(X)
        
        fileName = str(self.cust_name)+'__'+str(self.dataset_name)+'__'+str(self.in_field)+'__'+str(self.pred_field) + '__'+ self.training_status + '__'+'transformer.pkl'
        joblib.dump(transformer, 'data/'+fileName)
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X_transform, Y, test_size=0.2, random_state=42)
        self.X_train_tf, self.X_test_tf, self.y_train_tf, self.y_test_tf = train_test_split(X_tfidf, Y, test_size=0.2, random_state=42)
        
    def __init__(self, df,customer_id,dataset_id,pred_field,in_field,training_status,additional_fields):
        self.customer_id = customer_id
        self.dataset_id = dataset_id
        self.additional_fields = additional_fields
        cust_name_dict =  MongoDBPersistence.customer_tbl.find_one({'CustomerID': self.customer_id},{'CustomerName':1, '_id':0})

        if(cust_name_dict):
            self.cust_name = cust_name_dict['CustomerName']
        else:
            logging.info('%s: Customer not found in the record.'%RestService.timestamp())
            #Getting dataset details
        dataset_info_dict =  MongoDBPersistence.datasets_tbl.find_one({'CustomerID': self.customer_id, "DatasetID": self.dataset_id},{'DatasetName':1,'FieldSelections':1, '_id':0})
        if(dataset_info_dict):
            self.dataset_name = dataset_info_dict['DatasetName']
        else:
            logging.info('%s: Dataset not found in the record.'%RestService.timestamp())
        self.training_status = training_status
        self.pred_field = pred_field
        self.in_field = in_field
        self._load_data(df)
    @timeit
    def RFClassifierObjective(self,hyperparameters):
        # Machine learning model
        n_estimator_, max_dept_, criterion_ = hyperparameters
        rf = RandomForestClassifier(n_estimators=int(n_estimator_), max_depth=int(max_dept_), criterion=criterion_)

        # Training 
        rf.fit(self.X_train, self.y_train)

        # Making predictions and evaluating
        y_pred = rf.predict(self.X_test)
        f1_score_ = f1_score(self.y_test, y_pred, average='macro', labels=np.unique(y_pred))
        
        return -(f1_score_)
    
    @timeit
    def SVClassifierObjective(self,hyperparameters):
        # Machine learning model
        c_value_, kernel_ = hyperparameters
        
        svc_ = SVC(C=c_value_, kernel=kernel_)
        # Training 
        svc_.fit(self.X_train, self.y_train)

        # Making predictions and evaluating
        y_pred = svc_.predict(self.X_test)
        f1_score_ = f1_score(self.y_test, y_pred, average='macro', labels=np.unique(y_pred))

        return -(f1_score_)
    
    @timeit
    def MultinomialNBClassifierObjective(self,hyperparameters):
        # Machine learning model
        alpha_, = hyperparameters
        
        mnb = MultinomialNB(alpha=alpha_)
        # Training 
        mnb.fit(self.X_train, self.y_train)

        # Making predictions and evaluating
        y_pred = mnb.predict(self.X_test)
        f1_score_ = f1_score(self.y_test, y_pred, average='macro', labels=np.unique(y_pred))

        return -(f1_score_)
    
    @timeit
    def LogisticRegressionObjective(self,hyperparameters):
        # Machine learning model
        c_value, = hyperparameters
        
        lr = LogisticRegression(C=c_value, random_state=42)
        # Training 
        lr.fit(self.X_train, self.y_train)

        # Making predictions and evaluating
        y_pred = lr.predict(self.X_test)
        f1_score_ = f1_score(self.y_test, y_pred, average='macro', labels=np.unique(y_pred))

        return -(f1_score_)
    
    @timeit
    def XGBClassifierObjective(self,hyperparameters):
        # Machine learning model
        n_estimator_, objective_fn = hyperparameters
        
        xgb = XGBClassifier(n_estimators=int(n_estimator_),objective=objective_fn)
        # Training 
        xgb.fit(self.X_train, self.y_train)

        # Making predictions and evaluating
        y_pred = xgb.predict(self.X_test)
        f1_score_ = f1_score(self.y_test, y_pred, average='macro', labels=np.unique(y_pred))

        return -(f1_score_)

    @timeit
    def classify(self, model):
        # Train final model with all data.. Not throwing away important data that ML model can learn from
        # Train score model with test train splitted data
        model.fit(self.X_train, self.y_train)
        y_pred = model.predict(self.X_test)
        score_dict = {}
        cr = classification_report(self.y_test, y_pred)

        tmp = list()
        for row in cr.split("\n"):
            parsed_row = [x for x in row.split("  ") if len(x) > 0]
            if len(parsed_row) > 0:
                tmp.append(parsed_row)
                
        # -----------------------------Python code change for Python 3.8 version ----------
        microAvgList=[]
        index=0;
        for row in tmp[1:]:
            index=index+1;
            if len(row)==3:
                print(row)
                microAvgList.append("micro avg")
                microAvgList.append(row[1])
                microAvgList.append(row[1])
                microAvgList.append(row[1])
                microAvgList.append(row[2])
                tmp[index] = microAvgList
        #------------------------------------------------------

        # Store in dictionary
        measures = tmp[0]
        print('---------measures--------',measures)
        print('--------tmp[1:]---------',tmp[1:])
        D_class_data = defaultdict(dict)
        for row in tmp[1:]:
            class_label = row[0]
            for j, m in enumerate(measures):
                D_class_data[class_label][m.strip()] = float(row[j + 1].strip())
        metrics_tuples = list(D_class_data.items())[:-1]
        metrics_list = []
        final_metrics_dict = {}
        
        algoName = re.search(r"([A-Za-z0-9_]+)", str(model)).group()

        final_metrics_dict["AlgorithmName"] = algoName
        final_metrics_dict["PredictedField"] = str(self.pred_field)
        
        id_to_labels = MongoDBPersistence.datasets_tbl.find_one({'CustomerID':self.customer_id, "DatasetID": self.dataset_id},{"_id":0,"IdToLabels":1})
        if(id_to_labels):
            
            id_to_labels_dict = id_to_labels["IdToLabels"]
            
            inside_id_to_label = id_to_labels_dict[str(self.pred_field)]
        else:
            logging.info('%s: De-map data not found for %s field.'%(RestService.timestamp(),self.pred_field))
            
        try:
            for tuple_ in metrics_tuples:
                tmp_dict = {}
                if("avg" not in str(tuple_[0]).strip()):
                    tmp_dict["SubCategory"] = inside_id_to_label[str(tuple_[0]).strip()] 
                    metrics_dict = tuple_[1]
                    metrics_dict['f1_score'] = metrics_dict.pop('f1-score')
                    tmp_dict["Metrics"] = metrics_dict
                
                    metrics_list.append(tmp_dict)
        except Exception as e:
            logging.info("Warning ",e)
                
        final_metrics_dict["ClassificationReport"] = metrics_list
        score_dict["CategoryMetrics"] = final_metrics_dict
        vocab_dict={}
        try:
            vocab_path = 'data/' + self.cust_name + "__" + self.dataset_name + '__' + "in_field" + "__" + self.pred_field + "__"+"Vocab.pkl"
            vocab_file = Path(vocab_path)
            if(vocab_file.is_file()):
                vocab = joblib.load(vocab_path)
                
            else:
                logging.info('%s: Vocabulary file not found for %s field.. please train algo, save the choices & try again.'%(RestService.timestamp(),pred_field))
                return "failure"
            tfIdf_vec = vocab
            
            for key,value in enumerate(tfIdf_vec):
                vocab_dict[key] = value
        
        except Exception as e:
            logging.error("error in reading file ",str(e))
            print("error in reading file ",e)
        
        outer_dict_lr={}
        inner_dict_lr={}
        # Create models directory if there is not
        directory = os.path.dirname('models/')
        if not os.path.exists(directory):
            os.makedirs(directory)

        if ("RandomForestClassifier" in str(model)):  #
            try:
                coef_fileName = str(self.cust_name) + '__' + str(
                    self.dataset_name) + '__' + 'RandomForestClassifier' + '__' + str(
                    self.pred_field) + '__'+ 'Coef_.pkl'
                if(os.path.isfile("models/"+coef_fileName)):
                    os.remove("models/"+coef_fileName)
                length_of_vectors = len(vocab_dict)
                model_coefficients = model.feature_importances_[0:length_of_vectors]
                inner_dict_rf={}
                for j in range(len(model_coefficients)):
                    inner_dict_rf[vocab_dict[j]]=model_coefficients[j]
                joblib.dump(inner_dict_rf, 'models/' + coef_fileName)
            except Exception as e:
                print("error in rf",e)

            fileName = str(self.cust_name) + '__' + str(
                self.dataset_name) + '__' + 'RandomForestClassifier' + '__' + str(
                self.pred_field) + '__' + self.training_status + '__' + 'Model.pkl'
        elif ("LogisticRegression" in str(model)):
            
            try:
                coef_fileName = str(self.cust_name) + '__' + str(
                    self.dataset_name) + '__' + 'LogisticRegression' + '__' + str(
                    self.pred_field) + '__'+ 'Coef_.pkl'
                if(os.path.isfile("models/"+coef_fileName)):
                    os.remove("models/"+coef_fileName)
                # IGNORING ONE HOT ENCODING VECTORS FROM COLUMN TRANSFORMER
                length_of_vectors = len(vocab_dict)
                model_coefficients = model.coef_[:,0:length_of_vectors]
                for i in range(len(model.classes_)):
                    for j in range(len(model_coefficients[i])):
                        inner_dict_lr[vocab_dict[j]]=model_coefficients[i][j]
                    outer_dict_lr[model.classes_[i]] = inner_dict_lr
                
                joblib.dump(outer_dict_lr, 'models/' + coef_fileName)
            except Exception as e:
                print("error lr",e)
            fileName = str(self.cust_name) + '__' + str(self.dataset_name) + '__' + 'LogisticRegression' + '__' + str(
                self.pred_field) + '__' + self.training_status + '__' + 'Model.pkl'
        elif ("MultinomialNB" in str(model)):
            try:
                coef_fileName = str(self.cust_name) + '__' + str(
                    self.dataset_name) + '__' + 'MultinomialNB' + '__' + str(
                    self.pred_field) + '__'+ 'Coef_.pkl'
                if(os.path.isfile("models/"+coef_fileName)):
                    os.remove("models/"+coef_fileName)
                # IGNORING ONE HOT ENCODING VECTORS FROM COLUMN TRANSFORMER
                length_of_vectors = len(vocab_dict)
                model_coefficients = model.coef_[:,0:length_of_vectors]
                for i in range(len(model.classes_)):
                    for j in range(len(model_coefficients[i])):
                        inner_dict_lr[vocab_dict[j]]=model_coefficients[i][j]
                    outer_dict_lr[model.classes_[i]] = inner_dict_lr
                
                joblib.dump(outer_dict_lr, 'models/' + coef_fileName)
            except Exception as e:
                print("Error in MNB ",e)

            fileName = str(self.cust_name) + '__' + str(self.dataset_name) + '__' + 'MultinomialNB' + '__' + str(
                self.pred_field) + '__' + self.training_status + '__' + 'Model.pkl'
                
        elif ("SVC" in str(model)):
            try:
                if("kernel='linear'" in str(model)):
                    coef_fileName = str(self.cust_name) + '__' + str(
                        self.dataset_name) + '__' + 'SVC' + '__' + str(
                        self.pred_field) + '__'+ 'Coef_.pkl'
                    if(os.path.isfile("models/"+coef_fileName)):
                        os.remove("models/" + coef_fileName)
                # IGNORING ONE HOT ENCODING VECTORS FROM COLUMN TRANSFORMER
                length_of_vectors = len(vocab_dict)
                model_coefficients = model.coef_[:,0:length_of_vectors]
                
                for i in range(len(model.classes_)):
                    for j in range(len(model_coefficients[i])):
                        inner_dict_lr[vocab_dict[j]]=model_coefficients[i][j]
                    outer_dict_lr[model.classes_[i]] = inner_dict_lr

                for i in range(len(model.classes_)):
                    for j in range(len(model.coef_[i])):
                        inner_dict_lr[vocab_dict[j]]=model.coef_[i][j]
                    outer_dict_lr[model.classes_[i]] = inner_dict_lr
            
                    joblib.dump(outer_dict_lr, 'models/' + coef_fileName)
            except Exception as e:
                logging.error("Error creating vocab file for SVC %s "%(str(e)))
            fileName = str(self.cust_name) + '__' + str(self.dataset_name) + '__' + 'SVC' + '__' + str(
                    self.pred_field) + '__' + self.training_status + '__' + 'Model.pkl'
        elif ("XGBClassifier" in str(model)):
            try:
                coef_fileName = str(self.cust_name) + '__' + str(
                    self.dataset_name) + '__' + 'XGBClassifier' + '__' + str(
                    self.pred_field) + '__'+ 'Coef_.pkl'
                if(os.path.isfile("models/"+coef_fileName)):
                    os.remove("models/" + coef_fileName)
            except Exception as e:
                logging.error("Error creating vocab file for XGBOOST")
            fileName = str(self.cust_name) + '__' + str(self.dataset_name) + '__' + 'XGBClassifier' + '__' + str(
                self.pred_field) + '__' + self.training_status + '__' + 'Model.pkl'

        
        joblib.dump(model, 'models/' + fileName)
        accuracy = accuracy_score(self.y_test, y_pred)
        f1_score_ = f1_score(self.y_test, y_pred, average='macro', labels=np.unique(y_pred))
        precision_score_ = precision_score(self.y_test, y_pred, average='macro', labels=np.unique(y_pred))
        recall_score_ = recall_score(self.y_test, y_pred, average='macro', labels=np.unique(y_pred))
        score_dict["Accuracy"] = accuracy
        score_dict["F1_score"] = f1_score_
        score_dict["Precision"] = precision_score_
        score_dict["Recall"] = recall_score_
        score_dict["Model"] = model
        return score_dict
    @timeit
    def Kmeans(self, output='add'):

        n_clusters = len(np.unique(self.y_train))
        clf = KMeans(n_clusters = n_clusters, random_state=42)
        clf.fit(self.X_train)
        y_labels_train = clf.labels_
        y_labels_test = clf.predict(self.X_test)
        if output == 'add':
            self.X_train['km_clust'] = y_labels_train
            self.X_test['km_clust'] = y_labels_test
        elif output == 'replace':
            self.X_train = y_labels_train[:, np.newaxis]
            self.X_test = y_labels_test[:, np.newaxis]
        else:
            logging.error('output should be either add or replace')
            raise ValueError('output should be either add or replace')
            
        return self