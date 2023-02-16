__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""
import re
class LTFS_IRSR_Preprocessing:
    def __init__(self):
        pass

    @staticmethod
    def preprocess(training_tkt_df, caller='train'):
        from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
        print("<<<<<<<<<- Account specific code ->>>>>>>>>>>>>")
        REPLACE_BY_SPACE_RE = re.compile('[/(){}\[\]\|@,;]')
        BAD_SYMBOLS_RE = re.compile('[^0-9a-z #+_]')
        stplist=['hi','thanks','thankyou','please','issue','hello','team','infosys','com',
         'kindly','needfull','look','request', 'dear', 'sir', 'madam',
          'what','are','you','having','with','type','having','applications',
          'application','description','affecting','people','how','best','regards','mapping',
          'got','mac','bank','appraisal','reason','rejection','rejected','critical',
          'required','application']
        for index, row in training_tkt_df.iterrows():
            row['in_field'] = re.sub("[^0-9a-zA-Z]", " ", str(row['in_field']))
            row['in_field'] = re.sub(r'[\w\.-]+@[\w\.-]+',' ',str(row['in_field']))
            row['in_field'] = str(row['in_field']).lower() # lowercase text
            row['in_field'] = REPLACE_BY_SPACE_RE.sub(' ', str(row['in_field'])) # replace REPLACE_BY_SPACE_RE symbols by space in text
            row['in_field'] = BAD_SYMBOLS_RE.sub('', str(row['in_field'])) # delete symbols which are in BAD_SYMBOLS_RE from text
            row['in_field'] = ' '.join(word for word in row['in_field'].split() if word not in stplist)          
        
        clean_words = []
        for i in range(0,training_tkt_df.shape[0]):
            usercomment = re.sub(r"\S*@\S*\s?","",training_tkt_df['in_field'][i])
            usercomment = usercomment.lower()
            usercomment = usercomment.split()
            usercomment = [word for word in usercomment if not word in set(ENGLISH_STOP_WORDS)]
            usercomment = " ".join(sorted(set(usercomment),key=usercomment.index))
            clean_words.append(usercomment)
        training_tkt_df['in_field'] = clean_words      
        
        print("frequency of wrods removal")
        
        if (caller != 'predict'):
            list3 = []
            for sentence in clean_words:
                for word in sentence.split():
                    list3.append(word)  
                
            from collections import Counter
            clean_words_dict = dict(Counter(list3))            
        
            for key,val in clean_words_dict.items():
                if val < 10:
                    stplist.append(key)     
                
            list4 = []
            for i in range(0,training_tkt_df.shape[0]):
                temp = clean_words[i]
                tempsplit = temp.split()
                usercomment = [word for word in tempsplit if not word in stplist] 
                usercomment = " ".join(usercomment)
                list4.append(usercomment)       
            
            training_tkt_df['in_field'] = list4
        else:
            training_tkt_df['in_field'] = clean_words
            
        return training_tkt_df
    
    