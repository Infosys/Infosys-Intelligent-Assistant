__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""
import re
class RB_RB_Preprocessing:
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
          'application','description','affecting','people','how','best','regards']
        for index, row in training_tkt_df.iterrows():
            #row['in_field'] = re.sub("[^a-zA-Z]", " ", str(row['in_field']))
            row['in_field'] = re.sub(r'[\w\.-]+@[\w\.-]+',' ',str(row['in_field']))
            row['in_field'] = str(row['in_field']).lower() # lowercase text
            row['in_field'] = REPLACE_BY_SPACE_RE.sub(' ', str(row['in_field'])) # replace REPLACE_BY_SPACE_RE symbols by space in text
            row['in_field'] = BAD_SYMBOLS_RE.sub('', str(row['in_field'])) # delete symbols which are in BAD_SYMBOLS_RE from text
            row['in_field'] = ' '.join(word for word in row['in_field'].split() if word not in stplist)

        return training_tkt_df