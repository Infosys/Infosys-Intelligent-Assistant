__created__ = "May 22, 2020"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

import io
import os
import csv
import re
import importlib
import matplotlib
import pandas as pd
from iia.incident.incidenttraining import IncidentTraining
from iia.masterdata.datasets import DatasetMasterData
from iia.masterdata.customers import CustomerMasterData
import requests
from iia.persistence.mongodbpersistence import MongoDBPersistence
from iia.persistence.mappingpersistence import MappingPersistence
from iia.persistence.csvpersistence import CSVPersistence
from iia.recommendation.recommendationmodel import Recommendation
from iia.restservice import RestService
from iia.utils.utils import Utils
import configparser
import pickle
import matplotlib
import datetime
from bson import json_util
from flask import request, jsonify
import pandas as pd
from textblob import TextBlob
from collections import defaultdict
from collections import Counter
import json
import csv
from flask import make_response
from itertools import islice
from iia.utils.log_helper import get_logger, log_setup
logging = get_logger(__name__)
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import colors
from mpl_toolkits.axes_grid1 import make_axes_locatable
from collections import Counter
from IPython.display import HTML
from PIL import Image
plt.switch_backend('agg')
import random
import re
import string
import nltk
from gensim.models import Word2Vec
from nltk import word_tokenize
from nltk.corpus import stopwords
from sklearn.cluster import MiniBatchKMeans
from sklearn.metrics import silhouette_samples, silhouette_score
from gensim.parsing.preprocessing import remove_stopwords
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
import gensim
import gensim.corpora as corpora
from matplotlib.pyplot import figure
from wordcloud import WordCloud
import seaborn as sns

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

app = RestService.getApp()
fig, ax = plt.subplots(figsize=(20, 12))
bar_fig, bar_ax = plt.subplots(figsize=(40, 30))
line_fig, line_ax = plt.subplots(figsize=(15, 8))
heatmap_fig, heatmap_ax = plt.subplots(figsize=(16, 8))

colors_list = ['#adb0ff', '#ffb3ff', '#90d595', '#e48381', '#aafbff', '#f7bb5f', '#eafb50']


@app.route('/api/getSelctedColumnData/<int:customer_id>/<int:dataset_id>/<string:selected_col>', methods=['GET'])
def getSelctedColumnData(customer_id, dataset_id, selected_col):
    return PMA.getSelctedColumnData(customer_id, dataset_id, selected_col)

@app.route('/api/generatePMALineGraph', methods=['POST'])
def generatePMALineGraph():
    post_data = request.get_json()
    return PMA.generatePMALineGraph(post_data)

@app.route('/api/generatePMAGraph/<int:customer_id>/<int:dataset_id>/<string:year>/<string:month>/<string:selected_field>', methods=['GET'])
def generatePMAGraph(customer_id, dataset_id, year,month, selected_field):
    return PMA.generatePMAGraph(customer_id, dataset_id, year,month, selected_field)

@app.route('/api/uploadClusteringdata/<int:customer_id>/<int:dataset_id>', methods=["POST"])
def db_insert_clustering_tickets(customer_id,dataset_id):
    return PMA.db_insert_clustering_tickets(customer_id,dataset_id)

@app.route('/api/getDatasetDetails1/<int:customer_id>', methods=["GET"])
def getDatasetDetails1(customer_id):
    return PMA.getDatasetDetails1(customer_id)

@app.route('/api/monthlyTrendPMA/<int:customer_id>/<int:dataset_id>/<from_year>/<to_year>',methods=['GET'])  #need to send months from and upto by getting from font end 
def monthlyTrend_PMA(customer_id,dataset_id,from_year,to_year):
    return PMA.monthlyTrend_PMA(customer_id,dataset_id,from_year,to_year)

@app.route('/api/PMAdisplayPieGraph/<int:customer_id>/<int:dataset_id>/<selected_field>/<string:year>/<string:month>',methods=['GET'])
def displayPieGraph_PMA(customer_id,dataset_id,selected_field,year,month):
    return PMA.displayPieGraph_PMA(customer_id,dataset_id,selected_field,year,month)

@app.route('/api/PMAdisplayPieWordCloud/<int:customer_id>/<int:dataset_id>/<selectedfield>/<string:field_value>/<string:unassigned_value>/<int:number_of_words>/<cloud_type>',methods=['GET'])
def displayPieWordCloud_PMA(customer_id, dataset_id, selectedfield,field_value,unassigned_value,number_of_words,cloud_type):
    return PMA.displayPieWordCloud_PMA(customer_id, dataset_id, selectedfield,field_value,unassigned_value,number_of_words,cloud_type)

@app.route('/api/generatePieChart/<int:customer_id>/<int:dataset_id>/<string:selectedDate>', methods=['GET'])
def generatePieChart(customer_id, dataset_id,selectedDate):
    print("pie chart api call start....")
    return PMA.generatePieChart(selectedDate)

@app.route('/api/WeightedMovingAverage', methods=['POST'])
def WeightedMovingAverage():
    return PMA.WeightedMovingAverage()

@app.route('/api/getSelctedYearData/<int:customer_id>/<int:dataset_id>', methods=['GET'])
def getSelctedYearData(customer_id, dataset_id):
    return PMA.getSelctedYearData(customer_id, dataset_id)

@app.route('/api/generateHeatMap/<int:customer_id>/<int:dataset_id>/<string:year>/<string:selected_group>', methods=['GET'])
def generate_heatmap(customer_id, dataset_id, year, selected_group):
    return PMA.generate_heatmap(year, selected_group)

@app.route('/api/generateCluster/<int:customer_id>/<int:dataset_id>/<string:Category>', methods=['GET'])
def generateCluster(customer_id, dataset_id, Category):
    return PMA.generateCluster(customer_id, dataset_id, Category)

@app.route('/api/generateWordCloud/<int:NumberOfCluster>/<string:Type>/<int:Cluster>/<string:Category>', methods=['GET'])
def generateWordCloud(NumberOfCluster,Type,Cluster,Category):
    return PMA.generateWordCloud(NumberOfCluster,Type,Cluster,Category)       

@app.route('/api/getCategorydata/<int:customer_id>/<int:dataset_id>', methods=['GET'])
def getCategorydata(customer_id, dataset_id):
    return PMA.getCategorydata(customer_id, dataset_id)

class LoopingPillowWriter(animation.PillowWriter):
    def finish(self):
        self._frames[0].save(
            self._outfile, save_all=True, append_images=self._frames[1:],
            duration=int(1000 / self.fps), loop=0)

class PMA(object):
    '''
    classdocs
    '''

    def __init__(self, params):
        '''
        Constructor
        '''

    @staticmethod
    def getSelctedYearData(customer_id, dataset_id):
        category_list = list(MongoDBPersistence.cluster_table.find(
            {'CustomerID': customer_id, "DatasetID": dataset_id}))
        pd_data = pd.DataFrame(category_list)
        pd_data['created'] = pd.to_datetime(pd_data.loc[:, 'created'], errors='coerce')
        start_date = (pd_data['created']).min()
 
        end_year = (pd_data['created']).max() + np.timedelta64(1, 'Y')
        year_list = [str(i.strftime("%Y")) for i in pd.date_range(start=start_date, end=end_year, freq='Y')]
        return json_util.dumps(year_list)

    @staticmethod
    def generatePieChart(date): 
        try:    

            print("inside pie chart function...")
            logging.info('inside pie chart function...')

            selected_field = "assignment_group"
            path_check = os.path.join('static/assets/video/pie_Chart'+date+'.jpg')
            print('save_path: ',path_check)

            #-----------Fetchng data from TblClustering---------------------
            PMA_data = list(MongoDBPersistence.cluster_table.find({'CustomerID':1,"DatasetID":1 }))
            new_data = pd.DataFrame(PMA_data)
            new_data['created'] = pd.to_datetime(new_data.loc[:,'created'], errors='coerce')

            filter_year = (new_data['created'] >= str(date)) & (new_data['created'] < str(pd.to_datetime(date) + np.timedelta64(1,'D')) )
            data_for_input_year = new_data[filter_year]

            #---------------Grouping data for the selected date---------------------

            z = pd.DataFrame({'count' : data_for_input_year.groupby(selected_field).size()}).reset_index()

            if len(z) == 0:
                print("empty data set.....")
                return "Empty"
                
            else:
                fig1, ax1 = plt.subplots()

                list1 = list(np.zeros(len(z)))
                list1[0] = 0.2
                explode = tuple(list1)

                print(explode)

                ax1.pie(z['count'], labels = z["assignment_group"],explode = explode, autopct='%1.1f%%', shadow=True, startangle=90)

                ax1.axis('equal')
                
                plt.savefig(path_check, facecolor="#e8e8e8")
            
                return "Success"

        except Exception as ex:
                print('Exception...', ex)

    @staticmethod
    def getSelctedColumnData(customer_id, dataset_id, selected_col):
        category_list = list(MongoDBPersistence.cluster_table.find(
            {'CustomerID': customer_id, "DatasetID": dataset_id}))
        pd_data = pd.DataFrame(category_list)
        assignment_group_names = pd_data[selected_col].unique().tolist()
        print("printing dropdown values.........", assignment_group_names)
        return json_util.dumps(assignment_group_names)

    @staticmethod
    def getCategorydata(customer_id, dataset_id):
        category_list = list(MongoDBPersistence.cluster_table.find(
            {'CustomerID': customer_id, "DatasetID": dataset_id}))
        pd_data = pd.DataFrame(category_list)
        assignment_group_names = pd_data["category1"].tolist()
        print("printing dropdown values.........", assignment_group_names)
        return json_util.dumps(assignment_group_names)

    @staticmethod
    def generatePMAGraph(customer_id, dataset_id, year,month, selected_field):
        print("inside pma Bar graph...")
        logging.info("inside pma Bar graph...")
        PMA_data = list(MongoDBPersistence.cluster_table.find({'CustomerID': customer_id, "DatasetID": dataset_id}))
        pd_data = pd.DataFrame(PMA_data)

        pd_data = pd_data.filter(['created',selected_field])
        pd_data['created'] = pd.to_datetime(pd_data.loc[:, 'created'], errors='coerce')
        
        try:
           
            if year != '' and month=='undefined':
                logging.info('Year_Graph_BAR...')

                #-----Filtering data for selected year-------------------
                pd_data = pd_data.loc[pd_data['created'].dt.year == int(year)]
                pd_data= pd_data[selected_field]
                
                #---Taking top 10 values----
                pd_data = pd_data.value_counts().head(10)
                
                plt.figure(figsize=(15,8))
                try:
                    ax=sns.barplot(y=pd_data.index,x=pd_data.values)
                    ax.bar_label(ax.containers[0])

                    patches = [matplotlib.patches.Patch(color=sns.color_palette()[i], label=t) for i,t in enumerate(t.get_text() for t in ax.get_yticklabels())]
                    plt.legend(handles=patches, loc="lower right")
                except Exception as e:
                    logging.info(f'Exception in Year_Graph_BAR...{str(e)}')
             
                plt.xlabel('No. of tickets',fontsize=15)
                plt.ylabel(selected_field, fontsize=15)
                plt.title(year,fontsize=20)
                plt.tight_layout()
                vocab_path = os.path.join('static/assets/video/PMA_'+str(year)+'_'+month+'_'+selected_field+'.png')
                plt.savefig(vocab_path)

            elif year != '' and month != '':
                logging.info('Month_Graph_BAR...')
                month_number = datetime.datetime.strptime(month[0:3], '%b').month

                #-----Filtering data for selected month-------------------
                pd_data_filtered = pd_data.loc[pd_data['created'].dt.year == int(year)]
                pd_data = pd_data_filtered.loc[pd_data_filtered['created'].dt.month == month_number]
                pd_data= pd_data[selected_field]
                
                #---Taking top 10 values----
                pd_data = pd_data.value_counts().head(10)
                
                plt.figure(figsize=(15,8))
                try:
                    ax=sns.barplot(y=pd_data.index,x=pd_data.values)
                    ax.bar_label(ax.containers[0])

                    patches = [matplotlib.patches.Patch(color=sns.color_palette()[i], label=t) for i,t in enumerate(t.get_text() for t in ax.get_yticklabels())]
                    plt.legend(handles=patches, loc="lower right")
                except Exception as e:
                    logging.info(f'Exception in Month_Graph_BAR...{str(e)}')
                
                plt.xlabel('No. of tickets',fontsize=15)
                plt.ylabel(selected_field, fontsize=15)
                plt.title(month+' '+year,fontsize=20)
                vocab_path = os.path.join('static/assets/video/PMA_'+str(year)+'_'+month+'_'+selected_field+'.png')
                plt.tight_layout()
                plt.savefig(vocab_path)

            print("done....")
            logging.info('done....')

            return "Success"

        except Exception as ex:
            logging.error(str(ex))
            print('Exception...', ex)


    @staticmethod
    def monthlyTrend_PMA(customer_id,dataset_id,from_year,to_year):
        cre_list=[] 
        cre_list=list(MongoDBPersistence.cluster_table.find({"CustomerID": customer_id, "DatasetID":dataset_id},{"created":1,"_id":0}))
        filtered_data=list(filter(None,cre_list))#to remove null values
        
        df=pd.DataFrame()
        date_list=[]
        for i in range(len(filtered_data)):
            
            my_string=filtered_data[i]['created'].split(" ")[0]
            
            date_list.append(my_string)
        print(len(date_list))
        print("date list is ",date_list)

        #--------Counting tickets per month-----------------

        df=pd.DataFrame(date_list,columns =['date'])
        df['Count'] = 1
        df['date'] = pd.to_datetime(df['date'])
        df_new=df.groupby(df['date'].dt.strftime('%Y:%B'))['Count'].sum().sort_values()
        data_dict=df_new.to_dict()
        print("printing data in dictionary format ",data_dict)

        #---------filtering based on from and to years selected ------------------
        print("type of from year and to year is ",type(from_year))
        filtered_dict={k: v for k, v in data_dict.items() if k.startswith((from_year,to_year))}
        resp=json_util.dumps(filtered_dict) 
        return resp

    @staticmethod
    def take(n, iterable):
       
          return dict(islice(iterable, n)) 

    @staticmethod
    def displayPieGraph_PMA(customer_id,dataset_id,selected_field,year,month):
        
        select_field = list(MongoDBPersistence.cluster_table.find({"CustomerID": customer_id, "DatasetID":dataset_id}))

        mydata = pd.DataFrame(select_field)

        mydata['created'] = pd.to_datetime(mydata.loc[:, 'created'], errors='coerce')
        mydata2 = mydata.filter(["created", selected_field])

        if month in ['January','February','March','April','May','June','July','August','September','October','November','December']:
            year = int(year)
            _month = month
            datetime_object = datetime.datetime.strptime(_month, "%B")
            month_number = datetime_object.month
            month = month_number
            filter_year = ((mydata2['created'] >= str(year)) & (mydata2['created'] < str(year + 1)))
            year_data = mydata2[filter_year]
            filter_month = (year_data['created'].dt.month >= month) & (year_data['created'].dt.month < (month + 1))
            month_data = year_data[filter_month]
            z = pd.DataFrame({'count' : month_data.groupby(selected_field).size()})
            
        elif month == 'undefined' or month=='null':
            year = int(year)
            filter_year = (mydata2['created'] >= str(year)) & (mydata2['created'] < str(year + 1))
            data_for_input_year = mydata2[filter_year]
            z = pd.DataFrame({'count' : data_for_input_year.groupby(selected_field).size()})
            
        z1=z.to_dict()
        z2 = list(z1.values())[0]
        new_select_field_dict=dict(sorted(z2.items(), key=lambda kv: kv[1], reverse=True))
        if(len(new_select_field_dict)>15):
            new_select_field_dict=PMA.take(15, new_select_field_dict.items())
        print(new_select_field_dict)

        if(select_field):
            resp = json_util.dumps(new_select_field_dict)
        
        else:
            resp = ''
            
        print("data while displaying Graph",resp)
        return resp

    @staticmethod
    def displayPieWordCloud_PMA(customer_id, dataset_id, selectedfield,field_value,unassigned_value,number_of_words,cloud_type):
        
        if(unassigned_value=="true"):    
            
            with open('data/stopwords.csv', 'r') as readFile:
                reader = csv.reader(readFile)
                list1 = list(reader)  
                ENGLISH_STOP_WORDS = list1[0]
                readFile.close()
            
            input_df = pd.DataFrame()
            input_df = pd.DataFrame(list(MongoDBPersistence.cluster_table.find({'CustomerID': customer_id, "DatasetID": dataset_id,selectedfield:"" },{'_id':0,"description":1})))

            #cleaning corpus
            input_df = IncidentTraining.cleaningInputFields(input_df,'description')
            pd.options.display.max_colwidth = 500
            sentences = list(input_df['description'])
            final_stopwords = ENGLISH_STOP_WORDS 
            clean_sentences = []
            for sentence in sentences:
                
                clean_sentence = sentence.split()
                
                clean_sentence = [word for word in clean_sentence if not word in set(final_stopwords)]
                clean_sentence = " ".join(clean_sentence)
                clean_sentences.append(clean_sentence)
            if cloud_type == 'Unigram':
                clean_words_list = []
                for sentence in clean_sentences:
                    for word in sentence.split():
                        clean_words_list.append(word)
                
                clean_words_dict = dict(Counter(clean_words_list))
                if number_of_words > len(clean_words_dict):
                    number_of_words = len(clean_words_dict)  #also send a default value of number of words from front end
                
                sorted_dict = sorted(clean_words_dict.items(), key=lambda x: x[1])
                words_dict = {}
                for i in range(len(sorted_dict) - 1,len(sorted_dict) - number_of_words -1,-1):
                    words_dict.update({sorted_dict[i][0]:sorted_dict[i][1]})
                
                if words_dict:
                    resp = json_util.dumps(words_dict)
                    
                else:
                    resp = ''
                    

            elif cloud_type == 'Bigram':
                clean_words_list_bigram = []
                for i in range (0,len(clean_sentences) -1):
                    bigram_list = TextBlob(clean_sentences[i]).ngrams(2)
                    for j in range(0,len(bigram_list) - 1):
                        biagram = bigram_list[j][0] + " " + bigram_list[j][1]
                        clean_words_list_bigram.append(biagram)
                clean_word_dict_bigram = dict(Counter(clean_words_list_bigram))
                if number_of_words > len(clean_word_dict_bigram):
                    number_of_words = len(clean_word_dict_bigram)  #also send a default value of number of words from front end
                sorted_dict_bigram = sorted(clean_word_dict_bigram.items(), key=lambda x: x[1])
                words_dict_bigram = {}
                for i in range(len(sorted_dict_bigram) - 1,len(sorted_dict_bigram) - number_of_words -1,-1):
                    words_dict_bigram.update({sorted_dict_bigram[i][0]:sorted_dict_bigram[i][1]} )
                if words_dict_bigram:
                    resp = json_util.dumps(words_dict_bigram)
                    
                else:
                    resp = ''
                    
            return resp
        else:
            with open('data/stopwords.csv', 'r') as readFile:
                reader = csv.reader(readFile)
                list1 = list(reader)  
                
                ENGLISH_STOP_WORDS = list1[0]
                readFile.close()
            
            input_df = pd.DataFrame()
            input_df = pd.DataFrame(list(MongoDBPersistence.cluster_table.find({'CustomerID': customer_id, "DatasetID": dataset_id,selectedfield:field_value },{'_id':0,"description":1})))

            #cleaning corpus
            input_df = IncidentTraining.cleaningInputFields(input_df,'description')
            pd.options.display.max_colwidth = 500
            sentences = list(input_df['description'])
            final_stopwords = ENGLISH_STOP_WORDS #we can add still more stop words
            clean_sentences = []
            for sentence in sentences:
        
                clean_sentence = sentence.split()
                
                clean_sentence = [word for word in clean_sentence if not word in set(final_stopwords)]
                clean_sentence = " ".join(clean_sentence)
                clean_sentences.append(clean_sentence)
            if cloud_type == 'Unigram':
                clean_words_list = []
                for sentence in clean_sentences:
                    for word in sentence.split():
                        clean_words_list.append(word)
                
                clean_words_dict = dict(Counter(clean_words_list))
                if number_of_words > len(clean_words_dict):
                    number_of_words = len(clean_words_dict)  #also send a default value of number of words from front end
                
                sorted_dict = sorted(clean_words_dict.items(), key=lambda x: x[1])
                words_dict = {}
                for i in range(len(sorted_dict) - 1,len(sorted_dict) - number_of_words -1,-1):
                    words_dict.update({sorted_dict[i][0]:sorted_dict[i][1]})
                
                if words_dict:
                    resp = json_util.dumps(words_dict)
                    
                else:
                    resp = ''
                   

            elif cloud_type == 'Bigram':
                clean_words_list_bigram = []
                for i in range (0,len(clean_sentences) -1):
                    bigram_list = TextBlob(clean_sentences[i]).ngrams(2)
                    for j in range(0,len(bigram_list) - 1):
                        biagram = bigram_list[j][0] + " " + bigram_list[j][1]
                        clean_words_list_bigram.append(biagram)
                clean_word_dict_bigram = dict(Counter(clean_words_list_bigram))
                if number_of_words > len(clean_word_dict_bigram):
                    number_of_words = len(clean_word_dict_bigram)  #also send a default value of number of words from front end
                sorted_dict_bigram = sorted(clean_word_dict_bigram.items(), key=lambda x: x[1])
                words_dict_bigram = {}
                for i in range(len(sorted_dict_bigram) - 1,len(sorted_dict_bigram) - number_of_words -1,-1):
                    words_dict_bigram.update({sorted_dict_bigram[i][0]:sorted_dict_bigram[i][1]} )
                if words_dict_bigram:
                    resp = json_util.dumps(words_dict_bigram)
                    
                else:
                    resp = ''
                   
            return resp

    @staticmethod
    def generate_heatmap(input_year, selected_group):
        ()
        print('inside heatmap...')
        logging.info('inside heatmap...')
        print(selected_group, input_year)
        
        fig, ax = plt.subplots(figsize=(20, 12))

        #--------Checking Save Path-------------------------
        
        path_check = os.path.join('static/assets/video/heat_map_'+selected_group+'_'+input_year+'.jpg')
        print('save_path', path_check)

        try:         
            year = input_year

            if selected_group == "All":
                data_by_assignment =  False
            else:
                data_by_assignment =  True

            #------------------Creating and Filtering DATA from TblClustering----------------------------
            db_data = list(MongoDBPersistence.cluster_table.find({'CustomerID': 1, "DatasetID": 1}))
            new_data = pd.DataFrame(db_data)     
            
            new_data['created'] = pd.to_datetime(new_data.loc[:,'created'], errors='coerce')

            if data_by_assignment:
                new_data_fill  = new_data["assignment_group"] == selected_group
                new_data = new_data[new_data_fill]

            df1= pd.DataFrame({'count' : new_data.groupby( new_data.created.dt.date).size()}).reset_index()
            df1.set_index('created', inplace = True)
            df1.index = pd.to_datetime(df1.index)

            # -----------Turn data frame to a dictionary for easy access
            int_year = int(year)
            cal = {year: df1[df1.index.year == int_year]}


            # --------------Define Ticks------------------------
            DAYS = ['Sun', 'Mon', 'Tues', 'Wed', 'Thurs', 'Fri', 'Sat']
            MONTHS = ['Jan', 'Feb', 'Mar', 'Apr',    'May', 'June', 'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']

            fig, ax = plt.subplots(1, 1, figsize = (20,6))
            val = year

            start = pd.to_datetime(f'01/01/{year}')
            end = pd.to_datetime(f'12/31/{year}')

            start_sun = start - np.timedelta64((start.dayofweek + 1) % 7, 'D')

            days = (pd.to_datetime(end) - pd.to_datetime(start)) +  np.timedelta64(1, 'D')
            _week = pd.Timedelta(days).days // 7
            remainder = pd.Timedelta(days).days % 7

            if remainder != 0:
                _week = _week + 1
                
            num_weeks = _week

            heatmap = np.full([7, num_weeks], np.nan)

            ticks = {}
            y = np.arange(8) - 0.5
            x = np.arange(num_weeks + 1) - 0.5

            #------------------Counting tickets per day------------------

            for week in range(num_weeks):
                for day in range(7):
                    date = start_sun + np.timedelta64(7 * week + day, 'D')
                    text = ax.text(week, day, str(date)[8:11],
                                ha="center", va="center", color="w")
                    if date.day == 1:
                        ticks[week] = MONTHS[date.month - 1]
                    if date.dayofyear == 1:
                        ticks[week] += f'\n{date.year}'
                    if start <= date <= end:
                        if date in cal.get(val).index:
                            heatmap[day, week] = cal.get(val).loc[date, 'count']
                        elif date not in cal.get(val).index:
                            heatmap[day, week] = 0
            
            #------------Plotting Heatmap----------------
            
            mesh = ax.pcolormesh(x, y, heatmap, cmap= colors.LinearSegmentedColormap.from_list("", ["green","yellow","red"]), edgecolors='grey')
            print(mesh)
            ax.invert_yaxis()
            
            ax.set_xticks(list(ticks.keys()))
            ax.set_xticklabels(list(ticks.values()))
            ax.set_yticks(np.arange(7))
            ax.set_yticklabels(DAYS)
            ax.set_ylim(6.5, -0.5)
            ax.set_aspect('equal')
            ax.set_title(val, fontsize=15)

            # Hatch for out of bound values in a year
            ax.patch.set(hatch='xx', edgecolor='black')

            # Add color bar at the bottom
            divider = make_axes_locatable(ax)
            cax = divider.append_axes("bottom", size="4%", pad=0.5)

            fig.subplots_adjust(hspace=1)
            plt.colorbar(mesh, cax=cax, orientation = "horizontal")

            heat_map__path = os.path.join('static/assets/video/heat_map_'+selected_group+'_'+year+'.jpg')

            plt.savefig(heat_map__path, facecolor = "#e8e8e8")
            plt.show()

            print('done...')
            logging.info('done...')

            return "Success"

        except Exception as ex:
            print(ex)
            return "error"

    @staticmethod
    def generatePMALineGraph(data):
        
        print("inside line graph ....",data)

        year=data["selected_year"]
        
        if "selected_month" in data.keys():
            month=data["selected_month"]
        else:
            month='undefined'
        
        if month==None:
            month='undefined'
        selected_field = data["selected_field"]
        selected_group = data["selected_groups"]

        pd_data = list(MongoDBPersistence.cluster_table.find({'CustomerID': 1, "DatasetID": 1}))
        pd_data = pd.DataFrame(pd_data)

        pd_data = pd_data.filter(['created',selected_field])

        pd_data['created'] = pd.to_datetime(pd_data.loc[:,'created'], errors='coerce')

        if month=='undefined':
            print('Year_Graph_Line...')
            pd_data_filtered = pd_data.loc[pd_data['created'].dt.year == int(year)]
            period = 'M'
            x_label = str(year)

        else:
            print('Month_Graph_Line')
            month_number = datetime.datetime.strptime(month[0:3], '%b').month
            
            pd_data_filtered = pd_data.loc[pd_data['created'].dt.year == int(year)]
            pd_data_filtered = pd_data_filtered.loc[pd_data_filtered['created'].dt.month == month_number]
            period = 'W'
            x_label = 'Weeks'
        
        line_fig, line_ax = plt.subplots(figsize=(15, 8))

        for slt_grp_lst in selected_group:
            
            pd_data = pd_data_filtered.loc[pd_data_filtered[selected_field]==slt_grp_lst]

            pd_data = pd_data['created'].dt.to_period(period)
            pd_data = pd_data.rename(slt_grp_lst)

            pd_data = pd_data.value_counts()
            pd_data = pd_data.sort_index()
            
            date_list_x = []
            count_list_y = []
            
            if period == 'M':
                pd_data.index = pd_data.index.strftime('%b')
            
                for x in list(pd_data.index.astype(str)):
                    date_list_x.append(x)
                for y in pd_data.values:
                    count_list_y.append(y)
                
                year_dict={'Jan':0,'Feb':0,'Mar':0,'Apr':0,'May':0,'Jun':0,'Jul':0,'Aug':0,'Sep':0,'Oct':0,'Nov':0,'Dec':0}    
                selected_grp_dict = {date_list_x[i]: count_list_y[i] for i in range(len(date_list_x))}
                year_dict.update(selected_grp_dict)
                
                date_list_x = list(year_dict.keys())
                count_list_y = list(year_dict.values())
            
            elif period == 'W':
                for x in list(pd_data.index.astype(str)):
                    date_list_x.append(x)
                for y in pd_data.values:
                    count_list_y.append(y)
                

            line_ax.grid(True, linestyle="-")
            line_ax.plot(date_list_x, count_list_y, label=slt_grp_lst, marker='o')
            plt.xlabel(x_label, fontsize=15)
            plt.ylabel('No. of tickets', fontsize=15)

            for x, y in zip(date_list_x, count_list_y):
                label = str(y)

                line_ax.annotate(label,  # this is the text
                            (x,y),  # this is the point to label
                            textcoords="offset points",  # how to position the text

                            xytext=(0, 10),
                            ha='center')


            line_ax.spines['top'].set_visible(False)
            line_ax.spines['right'].set_visible(False)
            line_ax.spines['bottom'].set_visible(False)
            line_ax.set_facecolor("#e8e8e8")
            line_ax.legend(fontsize='medium', loc='upper right',
                    bbox_to_anchor=(1.12, 1.15))
        plt.gcf()
        
        str_grp_list=''
        for i in selected_group:
            str_grp_list+='_'+ i
        vocab_path = os.path.join('static/assets/video/PMA_Line'+'_'+str(year)+'_'+month+'_'+selected_field+str_grp_list+'.png')
        plt.savefig(vocab_path)
        
        print("done...")
        return "Success"

    @staticmethod
    def WeightedMovingAverage():

        post_data = request.get_json()
        print("inside weighted...", post_data)
        list1 = post_data["selected_value_list"]
        field_value = post_data["selected_field"]
        flag_count = post_data["flag"]

        if flag_count:
            flag = "True"
        else:
            flag = "False"

        length_of_selected_groups = len(list1)

        resp = ''
        try:
            if length_of_selected_groups == 0:
                grup_list = []
                str_grp_list = ''

            elif length_of_selected_groups > 0:  
                grup_list = list1
                str_grp_list = '_'.join(list1)
            path_check = os.path.join('static/assets/video/'+ flag + field_value +"_" +str_grp_list+ '_weighted-moving-average.png')
            print('save_path', path_check)

            training_data = list(MongoDBPersistence.cluster_table.find({'CustomerID': 1, "DatasetID": 1}))
            old_data = pd.DataFrame(training_data)
            new_data = old_data.filter(['created', field_value], axis=1)
            new_data['created'] = pd.to_datetime(new_data.loc[:, 'created'], errors='coerce')
            
            line_fig, line_ax = plt.subplots(figsize=(15, 8))
            
            if(flag_count == True):

                for group in list1:
                    logging.info('inside PMA comp graph...')
                    print('inside PMA comp graph...')
                    new_data2 = PMA.comparitive_graph(new_data, group, field_value)
                    
                    x = new_data2['created']
                    y2 = new_data2['Count']
                    y1 = new_data2['Count_mean']
                    
                    line_ax.grid(True, linestyle="-")
                    line_ax.plot(x, y1, label='count for '+group)
                    line_ax.plot(x, y2, label='count_mean for '+group)
                    plt.ylabel("count_mean + count", fontsize=15)
                    plt.xlabel("no.of days", fontsize=15)
                    plt.title("Weighted Moving Average", fontsize=20)
                    line_ax.legend(fontsize='medium', loc='upper right',
                    bbox_to_anchor=(1.12, 1.15))

                plt.gcf()
                plt.savefig(path_check)

                print('done...')
                return "Success"
            
            else:
                for group in list1:
                    new_data2 = PMA.generate_weighted_graph(field_value, group, new_data)
                    
                    line_ax.grid(True, linestyle="-")
                    line_ax.plot(new_data2['Count_mean'],label='count mean for ' + group)
                    plt.ylabel("count_mean", fontsize=15)
                    plt.xlabel("no.of days", fontsize=15)
                    plt.title("Weighted Moving Average", fontsize=20)
                    line_ax.legend(fontsize='medium', loc='upper right',
                    bbox_to_anchor=(1.12, 1.15))

                plt.gcf()
                plt.savefig(path_check)
                print('done...')
                return "Success"

        except Exception as ex:
            print("exception inside weighted moving avg....", ex)
            return "error"

    @staticmethod
    def generate_weighted_graph(field_value, group, data):
        if(group != 'All'):

            new_data1 = data.loc[(data[field_value] == group)]
            new_data1 = pd.DataFrame({'Count': new_data1.groupby(
                new_data1.created.dt.date).size()}).reset_index()
            rolling_value = 30
            weights = np.arange(1, rolling_value+1)

            new_data1['Count_mean'] = new_data1.Count.rolling(rolling_value).apply(
                lambda x: np.dot(x, weights)/weights.sum(), raw=True)

            return new_data1
        else:
            new_data1 = pd.DataFrame({'Count': data.groupby(data.created.dt.date).size()}).reset_index()
            rolling_value = 30
            weights = np.arange(1, rolling_value+1)
            new_data1['Count_mean'] = new_data1.Count.rolling(rolling_value).apply(
                lambda x: np.dot(x, weights)/weights.sum(), raw=True)
            return new_data1

    @staticmethod
    def comparitive_graph(new_data, group, field_value):
        if(group!='All'):        
            new_data = new_data.loc[(new_data[field_value]==group)]
            first_date = (new_data['created']).min()
            last_date = (new_data['created']).max()
            
            new_data = new_data[(new_data['created'] >= first_date) & (new_data['created'] <= last_date)]
            new_count = pd.DataFrame({'Count': new_data.groupby(new_data.created.dt.date).size()}).reset_index()
            
            rolling_value = 3
            weights = np.arange(1, rolling_value+1)
            
            new_count['Count_mean'] = new_count.Count.rolling(rolling_value).apply(
                                        lambda x: np.dot(x, weights)/weights.sum(), raw=True)
            return new_count
        
        else:
            first_date = (new_data['created']).min()
            last_date = (new_data['created']).max()
            
            new_data = new_data[(new_data['created'] >= first_date) & (new_data['created'] <= last_date)]
            new_count = pd.DataFrame({'Count': new_data.groupby(new_data.created.dt.date).size()}).reset_index()
            rolling_value = 3
            weights = np.arange(1, rolling_value+1)
            
            new_count['Count_mean'] = new_count.Count.rolling(rolling_value).apply(
                                        lambda x: np.dot(x, weights)/weights.sum(), raw=True)
            return new_count

    @staticmethod
    def generateCluster(customer_id, dataset_id, Category):
        try:
            print(f'Category.....{Category}')
            dir_name1 = f'static/assets/video/PMA_tokenized_docs_{Category}.pkl'
            dir_name2 = f'static/assets/video/PMA_vectorized_docs_{Category}.pkl'
            if os.path.exists(dir_name1) and os.path.exists(dir_name2):
                return "Success"
            else:
                try:
                    
                    custom_stopwords = set(stopwords.words("english") + ["news", "new", "top"])
                    
                    df_ = list(MongoDBPersistence.cluster_table.find(
                            {"CustomerID": customer_id, "DatasetID": dataset_id}))
                    
                    df_ = pd.DataFrame(df_)
                    
                    df_["text_desc"] = df_[Category]
                    df_["text_desc"] = df_["text_desc"].fillna("")
                    text_columns = ["text_desc"]
                    print(text_columns, type(text_columns))
                    for col in text_columns:
                            df_[col] = df_[col].astype(str)
                    df = df_.copy()
                    
                    #Calling clean_text function
                    PMA.clean_text.counter = 0
                    nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
                    df["tokens"] = df["text_desc"].apply(lambda x: PMA.clean_text(x, word_tokenize, custom_stopwords,nlp))

                    # Remove duplicated after preprocessing
                    _, idx = np.unique(df["tokens"], return_index=True)
                    df = df.iloc[idx, :]

                    # Remove empty values and keep relevant columns
                    df = df.loc[df.tokens.map(lambda x: len(x) > 0), ["text_desc", "tokens"]]
                    
                    df = df.reset_index(drop=True)
                    print(df)
                    
                    #Word2Vec Model

                    tokenized_docs=df['tokens'].values.tolist()
                    model = Word2Vec(sentences=tokenized_docs, vector_size=100, workers=1)

                    tokenized_docs=df['tokens'].values.tolist()

                    #Calling Vectorize function
                    vectorized_docs = PMA.vectorize(tokenized_docs, model=model)
                    with open(f'static/assets/video/PMA_tokenized_docs_{Category}.pkl', 'wb') as f:
                        pickle.dump(tokenized_docs, f)
                
                
                    with open(f'static/assets/video/PMA_vectorized_docs_{Category}.pkl', 'wb') as f:
                        pickle.dump(vectorized_docs, f)
                
                    return "Success"

        
                except Exception as ex:
                    print("Exception...", ex)
                    return str(ex)

        except Exception as ex:
            print("Exception...", ex)
            return str(ex)
            
     
    @staticmethod
    def generateWordCloud(NumberOfCluster,Type,Cluster,Category):
        with open(f'static/assets/video/PMA_tokenized_docs_{Category}.pkl', 'rb') as f:
            tokenized_docs = pickle.load(f)
    
        with open(f'static/assets/video/PMA_vectorized_docs_{Category}.pkl', 'rb') as f:
            vectorized_docs = pickle.load(f)
        clustering, cluster_labels, pie_dictt = PMA.mbkmeans_clusters(
                        X=vectorized_docs,
                        k=NumberOfCluster,
                        mb=500,
                        print_silhouette_values=True,
                    )


        most_representative_docs = np.argsort(
                        np.linalg.norm(vectorized_docs - clustering.cluster_centers_[Cluster], axis=1))
        clus_list = []

        print(most_representative_docs)
        for d in most_representative_docs[:50]:
        
            clus_list.append(tokenized_docs[d])
        print(clus_list)
        sent_tokens = [' '.join(ele) for ele in clus_list]
        combine_sent_tokens = []
        ress = ' '.join(sent_tokens)
        combine_sent_tokens.append(ress)
        if Type == 'Unigram':
            Type1 = (1,1)
        elif Type == 'Bigram':
            Type1 = (2,2)
        elif Type == 'Trigram':
            Type1 = (3,3)

        vectorizer = TfidfVectorizer(  lowercase=True,
                                        max_features=50,
                                        max_df=1,
                                        min_df=1,
                                        ngram_range = Type1,
                                        stop_words = "english",
                                        use_idf=False)

        vectors = vectorizer.fit_transform(combine_sent_tokens)

        dff=pd.DataFrame(vectors[0].T.todense(), index=vectorizer.get_feature_names(), columns=["TF"])
        dff=dff.sort_values('TF', ascending = False)
        
        dff.reset_index(level=0, inplace=True)
        d={}
        for a, b in dff.values:
            d[a] = b
        wordcloud = WordCloud().generate(str(d))
        Cloud = WordCloud(width=1600, height=800, background_color="aqua", max_words=30).generate_from_frequencies(frequencies=d)
        
        plt.figure(figsize = (20, 10), facecolor = None)
        plt.imshow(Cloud)
        plt.axis("off")
        plt.tight_layout(pad = 0)
        
        vocab_path = os.path.join('static/assets/video/PMA_Cluster_'+str(NumberOfCluster)+'_'+str(Type)+'_'+str(Cluster)+'.png')
        plt.savefig(vocab_path)
        
        return "Success"
    
    #Cleaning, Lemmatizing and Tokenizing Function
    @staticmethod
    def clean_text(text, tokenizer, stopwords, nlp):
        PMA.clean_text.counter += 1
        print(PMA.clean_text.counter)
        print("Cleaning Text. . . .----------------------------------------------------------")
        """Pre-process text and generate tokens

        Args:
            text: Text to tokenize.

        Returns:
            Tokenized text.
        """
        pattern1 = r'requested for'
        pattern2 = r'requested by'
        pattern3 = r'selected application'
        pattern4 = r'type of issue'
        pattern5 = r'description'
        
        
        text = str(text).lower()  # Lowercase words
        text = re.sub(r"\w*\d\w*", "", text)
        
        text = re.sub(r'(\s*\servicenow\s*)',' servicenow ',text)
        text = re.sub(r"\w*\d\w*", "", text)
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub("\s\s+", " ", text)
        text = re.sub(pattern1, '', text)
        text = re.sub(pattern2, '', text)
        text = re.sub(pattern3, '', text)
        text = re.sub(pattern4, '', text)
        text = re.sub(pattern5, '', text)
    
        
        print("Lemme Start======================================================")
        allowed_postags=["NOUN", "ADJ", "VERB", "ADV","PROPN"]
    
        doc = nlp(text)
        lem_str = ''
        for token in doc:
            if token.pos_ in allowed_postags:
                lem_str+=token.lemma_+' '
        print(lem_str)
        print("Lemme Done======================================================")
        
        
        tokens = tokenizer(lem_str)  # Get tokens from text
        tokens = [t for t in tokens if not t in stopwords]  # Remove stopwords
        tokens = ["" if t.isdigit() else t for t in tokens]  # Remove digits
        tokens = [t for t in tokens if len(t) > 1]  # Remove short tokens
        print("Tokens ", '\n',tokens)
        print("Text cleaning done", '\n\n')
        return tokens

    #Creating Vectorized Sentences from vectorized words
    @staticmethod
    def vectorize(list_of_docs, model):
        print("entering into vectorised function")
        """Generate vectors for list of documents using a Word Embedding

        Args:
            list_of_docs: List of documents
            model: Gensim's Word Embedding

        Returns:
            List of document vectors
        """
        features = []

        for tokens in list_of_docs:
            zero_vector = np.zeros(model.vector_size)
            vectors = []
            for token in tokens:
                if token in model.wv:
                    try:
                        vectors.append(model.wv[token])
                    except KeyError:
                        continue
            if vectors:
                vectors = np.asarray(vectors)
                avg_vec = vectors.mean(axis=0)
                features.append(avg_vec)
            else:
                features.append(zero_vector)
        return features

    #Clustering Function   
    @staticmethod
    def mbkmeans_clusters(
        X, 
        k, 
        mb, 
        print_silhouette_values, 
    ):
        """Generate clusters and print Silhouette metrics using MBKmeans

        Args:
            X: Matrix of features.
            k: Number of clusters.
            mb: Size of mini-batches.
            print_silhouette_values: Print silhouette values per cluster.

        Returns:
            Trained clustering model and labels based on X.
        """
        km = MiniBatchKMeans(n_clusters=k, batch_size=mb).fit(X)
        print(f"For n_clusters = {k}")
        print(f"Silhouette coefficient: {silhouette_score(X, km.labels_):0.2f}")
        print(f"Inertia:{km.inertia_}")

        if print_silhouette_values:
            sample_silhouette_values = silhouette_samples(X, km.labels_)
            print(f"Silhouette values:")
            silhouette_values = []
            dictt = {}
            for i in range(k):
                cluster_silhouette_values = sample_silhouette_values[km.labels_ == i]
                silhouette_values.append(
                    (
                        i,
                        cluster_silhouette_values.shape[0],
                        cluster_silhouette_values.mean(),
                        cluster_silhouette_values.min(),
                        cluster_silhouette_values.max(),
                    )
                )
                dictt[i]=[cluster_silhouette_values.shape[0]]

            silhouette_values = sorted(
                silhouette_values, key=lambda tup: tup[2], reverse=True
            )
            for s in silhouette_values:
                print(
                    f"    Cluster {s[0]}: Size:{s[1]} | Avg:{s[2]:.2f} | Min:{s[3]:.2f} | Max: {s[4]:.2f}"
                )
        return km, km.labels_, dictt


    @staticmethod
    def db_insert_clustering_tickets(customer_id,dataset_id):
        print('Inside Insert')

        #----------Removing prev data from ClusteringTbl----------------------
        MongoDBPersistence.cluster_table.remove({})

        new_dataset_flag = 0
        file = request.files['trainingData']
        
        dataset_ = MongoDBPersistence.datasets_tbl.find_one({"CustomerID" : 1, "DatasetID":1})

        if(dataset_):
            #Dataset exist for the team
            
            dataset_id = dataset_["DatasetID"]
            print(dataset_id)
            
        else:
            
            dataset_dict = MongoDBPersistence.datasets_tbl.find_one({"CustomerID" : 1, "DatasetID":1})

            if(dataset_dict):
                last_dataset_id = dataset_dict['DatasetID']
            else:
                last_dataset_id = 0
                logging.info('%s: Adding dataset for very first team.')

            #New dataset id for the customer
            dataset_id = last_dataset_id + 1
            print(dataset_id, "New number..............")
            
            new_dataset_dict = {}
            new_dataset_dict["DatasetID"] = dataset_id
            # new_dataset_dict["DatasetName"] = dataset_name
            new_dataset_dict["CustomerID"] =  customer_id
            new_dataset_flag = 1
        if not file:
            return "No file"
        elif(not '.csv' in str(file)):
            return "Upload csv file."


        #--------------------Reading data from uploaded file-------------------------

        stream = io.StringIO(file.stream.read().decode("latin-1"), newline=None)
        
        stream.seek(0)
        result = stream.read()

        #create list of dictionaries keyed by header row   k.lower()
        csv_dicts = [{k.lower(): v for k, v in row.items()} for row in csv.DictReader(result.splitlines(), \
            skipinitialspace=True)]

        for item in csv_dicts:
            item.update( {"CustomerID":customer_id})
            item.update( {"DatasetID":dataset_id})
            item.update( {"TrainingFlag":0})
            
        #Clease data before inserting into DB
        csv_df = pd.DataFrame(csv_dicts)
        if('number' not in csv_df.columns):
            logging.info('%s: Please rename ticket_id/Incident_id column to "number".'% RestService.timestamp())
            return 'failure'
        
        #remove spaces between the name of column
        csv_df.columns = ['_'.join(col.split(' ')) for col in csv_df.columns]
        #Remove duplicate columns if there any (Based on Incident number)
        csv_df.drop_duplicates(subset ="number", keep = 'first', inplace = True)
        csv_df_cols = csv_df.columns
        
        if(len(set(csv_df_cols))<len(csv_df_cols)):
            # logging.info('%s: Duplicate columns, please rename the duplicate column names..'%timestamp)
            return 'failure'

        training_row = MongoDBPersistence.cluster_table.find_one({'CustomerID':customer_id,'DatasetID':dataset_id},{'_id':0})
        if(training_row):
            prev_uploaded_cols = list(training_row)
            if(not set(csv_df_cols) == set(prev_uploaded_cols)):
                
                return 'failure'
    
        json_str = csv_df.to_json(orient='records')
        json_data = json.loads(json_str)
        try:
            
            #-------------------Inserting New data from file in DB-----------------------
            
            print("successfully deleted the records in tables")
            MongoDBPersistence.cluster_table.insert_many(json_data)
            if(new_dataset_flag):
                
                MongoDBPersistence.datasets_tbl.insert_one(new_dataset_dict)
                
                MongoDBPersistence.teams_tbl.update_one({'CustomerID':customer_id}, {"$set": {"DatasetID":dataset_id}}, upsert=False)

            #--------Deleting pickle files------------
            dir_name = r'static/assets/video/'
            PMA.check_path(dir_name)
            test = os.listdir(dir_name)
            for item in test:
                if item.endswith('.pkl'):
                    os.remove(os.path.join(dir_name,item))


            resp = "success"
        except Exception as e:
            logging.info(f'Error occured...{str(e)}')
            
            resp = 'failure'
        return resp

        
    @staticmethod
    def getDatasetDetails1(customer_id):
        #customer_tbl is a pymongo object to TblCustomer
        train_dict = {}
        
        dataset_dict = MongoDBPersistence.datasets_tbl.find_one({"CustomerID": customer_id},{"DatasetName":1,"_id":0})
        if(dataset_dict):
            train_dict['name'] = dataset_dict["DatasetName"]
            
        else:
            print("dataset details not found")
            
        dataset = pd.DataFrame(list(MongoDBPersistence.cluster_table.find({'CustomerID': customer_id}, {"CustomerID":0, "_id":0, "DatasetID":0, "TrainingFlag":0})))
        tbl_columns = dataset.columns
        row_count = dataset.shape[0]
        train_dict['fields'] = tbl_columns
        train_dict['count'] = row_count
        
        return json_util.dumps(train_dict)


    @staticmethod
    def check_path(mypath):
        try:
            if not os.path.exists(mypath):
                os.mkdir(mypath)
        except Exception as e:
            logging.error(e, exc_info=True)