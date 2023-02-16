__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""
import re
class BPX_IRSR_Preprocessing:
    def __init__(self):
        pass

    @staticmethod
    def preprocess(training_tkt_df, caller='train'):
        from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
        print("<<<<<<<<<- Account specific code ->>>>>>>>>>>>>")
        #applications
        stplist=['hi','thanks','thankyou','please','issue','hello','team','infosys','com',
         'kindly','needfull','look','request','dear','sir','madam',
          'what','are','you','having','with','type','having',
          'application','description','affecting','people','how','best','regards','see',
          'attached','screenshot','png','jpg','jpeg','from','to','january',
          'february','march','april','may','june','july','august','september',
          'october','november','december','sunday','monday','tuesday','wednesday',
          'thursday','friday','saturday','sunday','cc','bcc','jan','feb','mar','apr','jun',
          'jul','aug','sep','oct','nov','dec','mon','tue','wed','thu','fri','sat',
          'sun','am','pm','example','template','com','mail','email','mobile','plz',
          'bpx','subject','re','forward','fwd','fw','pre',
          'task','close','raised','ticket','need',
          'short','andre','vizina','feel','free','description',
          'closed','actions','ignore','mind']

        
        wordre = ('This email and any attachments are intended only for the addressee s listed above and may contain confidential proprietary and or privileged information If you are not an intended recipient please immediately advise the sender by return email delete this email and any attachments and destroy any copies of same Any unauthorized review use copying disclosure or distribution of this email and any attachments is prohibited')
        wordre = wordre.lower()
        clean_words = []
        training_tkt_df['in_field'] = training_tkt_df['in_field'].str.lower()
        #print("Initial Cleaning")
        for i in range(0,training_tkt_df.shape[0]):
            usercomment = str(training_tkt_df['in_field'][i])
            for count in range(len(usercomment)-1):                
                if (usercomment.find('src=',count,len(usercomment)) == count):
                    count1 = usercomment.find('--~||~--',count,len(usercomment))
                    usercomment = usercomment.replace(usercomment[count:count1-1],'')
                    count = count1
            count = 0
            
            clean_words.append(usercomment)
        
        training_tkt_df['in_field'] = clean_words
        
        clean_words = []
        #print("Mail header removal")
        for i in range(0,training_tkt_df.shape[0]):
            usercomment = str(training_tkt_df['in_field'][i])
            for count in range(len(usercomment)-1):
                if (usercomment.find('from:',count,len(usercomment)) == count):
                    count1 = usercomment.find('subject',count,len(usercomment))
                    usercomment = usercomment.replace(usercomment[count:count1-1],'')
                    count = count1
                                   
            clean_words.append(usercomment)

        training_tkt_df['in_field'] = clean_words
            
        
        list2 = []
        #print("HTML tags removal")
        for index, row in training_tkt_df.iterrows():
            #row['in_field'] = re.sub(r'^https?:\/\/.*[\r\n]*', '', str(row['in_field']), flags=re.MULTILINE)
            row['in_field'] = re.sub(r'<.*?>',r' ',str(row['in_field']))
            #row['in_field'] = re.sub("[^0-9a-zA-Z]", "", str(row['in_field']))
            #row['in_field'] = re.sub(r'[\w\.-]+@[\w\.-]+','',str(row['in_field']))
            row['in_field'] = str(row['in_field']).replace(wordre,'')
            
            list2.append(row['in_field'])
            
 
        training_tkt_df['in_field'] = list2      
        
        list3 = []
        #print("Final cleaning")
        for i in range(0,training_tkt_df.shape[0]):
            usercomment = re.sub(r"\S*@\S*\s?","",list2[i])    
            usercomment = re.sub("[^0-9a-zA-Z]"," ",usercomment)
            usercomment = usercomment.lower()
            usercomment = usercomment.split()
            usercomment = [word for word in usercomment if not word in set(ENGLISH_STOP_WORDS)]
            usercomment = [word for word in usercomment if not word in stplist]  
            usercomment = " ".join(usercomment)
            usercomment = re.sub(r"\b[a-zA-Z]\b","",usercomment)
            list3.append(usercomment)   
            
        training_tkt_df['in_field'] = list3   
        print("done")
        return training_tkt_df