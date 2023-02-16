__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

import re
class Adient_SR_Preprocessing:
    def __init__(self):
        pass

    @staticmethod
    def preprocess(training_tkt_df, caller='train'):
        import re
        print("<<<<<<<<<- Account specific code ->>>>>>>>>>>>>")
        REPLACE_BY_SPACE_RE = re.compile('[/(){}\[\]\|@,;]')
        BAD_SYMBOLS_RE = re.compile('[^0-9a-z #+_]')
        #if we need to remove stopwords before tfidf
        # with open('stopwords.csv', 'r') as readFile:
        #     reader = csv.reader(readFile)
        #     list1 = list(reader)  
        #     ENGLISH_STOP_WORDS = list1[0]
        #     readFile.close()
        #print(training_tkt_df)
        stplist=['hi','thanks','thankyou','please','issue','hello','team','infosys','com',
         'kindly','needfull','look','request', 'dear', 'sir', 'madam',
          'what','are','you','having','with','type','having','applications',
          'application','description','affecting','people','how','best','regards',
          'contact','number','preferred','language','english','chinese',
         'working','hours','monday','tuesday','wednesday','thursday','friday',
         'saturday','sunday','mondays','tuesdays','wednesdays','thursdays','fridays',
         'saturdays','sundays','numbers','part','global id','email','mail','location',
         'pc name','phone','language','customer','states','dear','team','regards',
         'thankyou','thank you','best','spanish','users','article','knowledge',
         'german','iks','serial','model','spain','agullent','skype','slovak','cet',
         'vacation','jan','feb','mar','apr','may','jun','july','aug','sep','oct','nov',
         'dec','adient','used','burscheid','see','attachment','advance','kind','office',
         'accountant','payable','citrix id','morning','evening','am','pm','mon',
         'tue','wed','thu','fri','sat','sun']
        
        for index, row in training_tkt_df.iterrows():
            row['in_field'] = re.sub("[^a-zA-Z]", " ", str(row['in_field']))
            row['in_field'] = re.sub(r'[\w\.-]+@[\w\.-]+',' ',str(row['in_field']))
            row['in_field'] = str(row['in_field']).lower() # lowercase text
            row['in_field'] = REPLACE_BY_SPACE_RE.sub(' ', str(row['in_field'])) # replace REPLACE_BY_SPACE_RE symbols by space in text
            row['in_field'] = BAD_SYMBOLS_RE.sub('', str(row['in_field'])) # delete symbols which are in BAD_SYMBOLS_RE from text
            row['in_field'] = ' '.join(word for word in row['in_field'].split() if word not in stplist)
            
            # row['in_field'] = ' '.join(word for word in row['in_field'].split() if word not in ENGLISH_STOP_WORDS)
        '''import re 
        from sklearn.feature_extraction import stop_words
        stplist=['hi','thanks','thankyou','please','issue','hello','team','infosys','com',
         'kindly','needfull','look','request', 'dear', 'sir', 'madam',
          'what','are','you','having','with','type','having','applications',
          'application','description','affecting','people','how','best','regards']
        clean_words = []
        for i in range(0,training_tkt_df.shape[0]):
            usercomment = re.sub("[^a-zA-Z]"," ",training_tkt_df['in_field'][i])
            usercomment = re.sub(r'[\w\.-]+@[\w\.-]+',' ',usercomment)
            usercomment = usercomment.lower()
            usercomment = usercomment.split()
            usercomment = [word for word in usercomment if not word in set(stop_words.ENGLISH_STOP_WORDS)]
            usercomment = [word for word in usercomment if not word in stplist]
            usercomment = " ".join(sorted(set(usercomment),key=usercomment.index))
            clean_words.append(usercomment)
        training_tkt_df['in_field'] = clean_words'''
        
        return training_tkt_df