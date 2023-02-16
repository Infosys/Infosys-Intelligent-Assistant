__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""
import re
from sklearn.feature_extraction import stop_words

class Adient_IR_Preprocessing:
    def __init__(self):
        pass    
    @staticmethod
    def preprocess(training_tkt_df, caller='train'):
        print("<<<<<<<<<- Account specific code ->>>>>>>>>>>>>")
        print(training_tkt_df.head())
        #if we need to remove stopwords before tfidf
        # with open('stopwords.csv', 'r') as readFile:
        #     reader = csv.reader(readFile)
        #     list1 = list(reader)  
        #     ENGLISH_STOP_WORDS = list1[0]
        #     readFile.close()
        #print(training_tkt_df)        
        stplist=['hi','thanks','thankyou','please','issue','hello','team','infosys','com',
                 'kindly','needfull','look','request','dear','sir','madam',
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
        sig_remarks=['best regard','best regards','best regards,','regards','regards,','thanks,',
                     'thanks!','thank you!','thank you.','thank you:','thank you','thank you,,','thank you,','thanks.','thanks',
                     'thank you in advance','thank you in advance,','thank you in advance.',
                     'thanks in advance','thanks in advance,','thanks in advance!',
                     'thank you & regards','thanks and regards','thanks and regards,',
                     'thank you and best regards','thanks and best regards',
                     'thank you in advance & regards','kind regards,','kind regards',
                     'thank you for your support','yours sincerely','thank you so much',
                     'many thanks in advance','many thanks in advance!','waiting for your kind reply','thank you so much:',
                     'thanks for your support','thank you for your help','thanks & regards',
                     'thanks & regards,','have a nice day','can you help me?',
                     'thank you & kind regards','thank you in advance for your support,',
                     'thank you for your investigation.','please see related invoices:',
                     'thank you very much in advance and best regards,','please help urgently .',
                     'thank you in advanced and best regards.','thank you very much',
                     'thank you very much for your help and support.','thank you and Best Regards,',
                     'thank you very much for your support.','thanks & regards!',
                     'could you please support me.thank','thank you!!','regards.','from:']  
        start_sign = ["thank","thanks",'thanks.',"thanks,","best","regards",'regards,',
                      "from:","kind","yours","your",'please','have','can','could',
                      'waiting','thank!','thanks!','many','regards.','from:']
        list1 = []
        list1str = ""        
        for i in range(0,training_tkt_df.shape[0]):
            input_field = str(training_tkt_df['in_field'][i]).split("--~||~--")
            for field in input_field:               
                corpus = field.lower()
                corpus = corpus.split() 
                modified_flag = False
                tmp_str=""
                r = 0
                for j in range(0,len(corpus)-1):  
                    if corpus[j] in start_sign:
                        r = 0
                        tmp_str = corpus[j]
                    if(len(tmp_str)>=1):
                        r += 1
                        if(tmp_str in sig_remarks):
                            temp_list_2 = corpus[0:j]
                            description_str = ' '.join(temp_list_2)
                            list1str=list1str+' ' +description_str
                            modified_flag = True                
                            break
                        elif(r>6):
                            tmp_str=""
                            continue
                        else:
                            tmp_str += " "+corpus[j+1]
                            if(tmp_str in sig_remarks):
                                temp_list_2 = corpus[0:j]
                                description_str = ' '.join(temp_list_2)
                                list1str=list1str+' ' +description_str
                                modified_flag = True                
                                break
                            continue
                if modified_flag == False:
                    description_str = ' '.join(corpus)
                    list1str=list1str+' ' +description_str
            list1.append(list1str)
            list1str=""
            
            
        list2 = []
        for i in range(0,training_tkt_df.shape[0]):
            usercomment = re.sub(r"\S*@\S*\s?","",list1[i])    
            usercomment = re.sub("[^0-9a-zA-Z]"," ",usercomment)
            usercomment = usercomment.lower()
            usercomment = usercomment.split()
            usercomment = [word for word in usercomment if not word in set(stop_words.ENGLISH_STOP_WORDS)]
            usercomment = [word for word in usercomment if not word in stplist]  
            usercomment = " ".join(sorted(set(usercomment),key=usercomment.index)) 
            usercomment = re.sub(r"\b[a-zA-Z]\b","",usercomment)
            list2.append(usercomment)
        
        
        if (caller != 'predict'):
            list3 = []
            for sentence in list2:
                for word in sentence.split():
                    list3.append(word)  
                    
            from collections import Counter
            clean_words_dict = dict(Counter(list3))            
            
            for key,val in clean_words_dict.items():
                if val < 6:
                    stplist.append(key)     
                    
            list4 = []
            for i in range(0,training_tkt_df.shape[0]):
                temp = list2[i]
                tempsplit = temp.split()
                usercomment = [word for word in tempsplit if not word in stplist] 
                usercomment = " ".join(usercomment)
                list4.append(usercomment)       
                
            training_tkt_df['in_field'] = list4
        else:
            training_tkt_df['in_field'] = list2
        
        training_tkt_df['Additional comments'] = ""
        training_tkt_df['Comments and Work notes'] = ""
        
        return training_tkt_df
    