__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""
# -*- coding: utf-8 -*-

import re
from sklearn.feature_extraction import stop_words

class  Microsoft_Infra_Preprocessing:
    def __init__(self):
        pass    
    @staticmethod
    def preprocess(training_tkt_df, caller='train'):
        print(training_tkt_df.head())
        print("<<<<<<<<<- Account specific code ->>>>>>>>>>>>>")
        #if we need to remove stopwords before tfidf
        # with open('stopwords.csv', 'r') as readFile:
        #     reader = csv.reader(readFile)
        #     list1 = list(reader)  
        #     ENGLISH_STOP_WORDS = list1[0]
        #     readFile.close()
        #print(training_tkt_df)              
        
        stplist=['hi','thanks','thankyou','please','issue','hello','team','microsoft','com','kindly','needfull','look','request', 
         'dear','sir','madam','regards','kind','usd','payops','description','good','day','lingering',
         'adjustment','adjustments','jpy','jpyexplain','ems','boyanazure','suspendedcancel','instate ea','caid','target']
            #'thank','customer']
            #'thank','http','customer','partner','cust','problem','statement','needing','assistance','aaaaaaa']

        
        
        
        list1 = []
        print(training_tkt_df.head())
        list1str = ""        
        for i in range(0,training_tkt_df.shape[0]):
            input_field = str(training_tkt_df['in_field'][i]).split("--~||~--")
            for field in input_field:
                corpus = field.lower()
                temp_list = corpus.split() 
                modified_flag = False
                for j in range(0,len(temp_list)-1):
                    if temp_list[j] == '2.'or temp_list[j] == 'log' :
                        temp_list_2 = temp_list[0:j-1]
                        description_str = ' '.join(temp_list_2)
                        list1str = list1str +' '+ description_str
                        modified_flag = True
                        break
                if modified_flag == False:
                    description_str = ' '.join(temp_list)
                    list1str=list1str+' ' +description_str
            list1.append(list1str)
            list1str=""
            
            
        list2 = []
        print(training_tkt_df.head())
        for i in range(0,training_tkt_df.shape[0]):
            usercomment = re.sub(r"\S*@\S*\s?","",list1[i])    
            usercomment = re.sub("[^a-zA-Z]"," ",usercomment)
            usercomment = re.sub(r'[^\x00-\x7F]+'," ",usercomment)
            usercomment = usercomment.lower()
            usercomment = usercomment.split()
            usercomment = [word for word in usercomment if not word in set(stop_words.ENGLISH_STOP_WORDS)]
            usercomment = [word for word in usercomment if not word in stplist]  
            usercomment = " ".join(sorted(set(usercomment),key=usercomment.index)) 
            usercomment = re.sub(r"\b[a-zA-Z]\b","",usercomment)
            usercomment = re.sub("\\b\\w{1,2}\\b","",usercomment)
            list2.append(usercomment)
        
        
        if (caller != 'predict'):
            list3 = []
            print(training_tkt_df.head())
            for sentence in list2:
                for word in sentence.split():
                    list3.append(word)  
                    
            from collections import Counter
            clean_words_dict = dict(Counter(list3))            
            
            for key,val in clean_words_dict.items():
                if val < 6:
                    stplist.append(key)     
                    
            list4 = []
            print(training_tkt_df.head())
            for i in range(0,training_tkt_df.shape[0]):
                temp = list2[i]
                tempsplit = temp.split()
                usercomment = [word for word in tempsplit if not word in stplist] 
                usercomment = " ".join(usercomment)
                list4.append(usercomment)       
                
            training_tkt_df['in_field'] = list4
        else:
            training_tkt_df['in_field'] = list2
        
        return training_tkt_df
