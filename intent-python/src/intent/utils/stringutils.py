__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

import re
from pandas.io.sql import read_sql_table
from intent.persistence.peristencemanager import PeristenceManager
from intent.persistence.sqlpersistence import SQLPersistence
class StringUtils(object):
    cleanUpCount = 0
    def __init__(self):
        #Do Nothing;
        print("PeristenceManager.__init__")
    
    # =============================================================================
    # #Cleaning data before feeding it to algorithms while predicting
    # def remove_html_tags(text):
    #     """Remove html tags from a string"""
    #     import re
    #     clean = re.compile('<.*?>')
    #     return re.sub(clean, '', text)
    # =============================================================================
    #Cleaning data before feeding it to algorithms while predicting
    # def get_clean_text(text):
    #     html_less = re.sub(re.compile('<.*?>'), '', text)
    #     number_less = re.sub(re.compile('[0-9]'), '', html_less)
    #     clean_text = re.sub(re.compile('[^ a-zA-Z_]'), '', number_less)
    #     return clean_text

    # @staticmethod
    # def remove_html_tags(text):      
    #     StringUtils.cleanUpCount=StringUtils.cleanUpCount+1
    #     if(StringUtils.cleanUpCount%1000 == 0):
    #         print('remove_html_tags - Cleaned '+str(StringUtils.cleanUpCount)+' records')  
    # #     updated=text;
    #     '''
    #     from html.parser import HTMLParser
    #     html_parser = HTMLParser()
    #     updated = html_parser.unescape(updated)
    #     '''
        
        # clean = re.compile('<img.*\\.\\.\\.')        
        # updated= re.sub(clean, ' ', updated)
        # clean = re.compile('<img.*/>')        
        # updated= re.sub(clean, ' ', updated)
        # clean = re.compile('<a.*</a>')
        # updated= re.sub(clean, ' ', updated)
        # clean = re.compile('href=".*"')
        # updated= re.sub(clean, ' ', updated)    
        # clean = re.compile('https://.*[\u00ff ]')
        # updated= re.sub(clean, ' ', updated)         
        # clean = re.compile('<.*?>')
        # updated= re.sub(clean, ' ', updated)
        # clean = re.compile(' .*\\.jpg')
        # updated= re.sub(clean, ' ', updated)        
        # clean = re.compile('\n')
        # updated= re.sub(clean, ' ', updated)
        # #if(text!=updated):
        # #print("Original = "+text)            
        # #print("Updated = "+updated)
        # return updated
       
#     @staticmethod
#     def remove_special_char(text):
#         #Remove special char from a string
#         #print("remove_special_char");
#         StringUtils.cleanUpCount=StringUtils.cleanUpCount+1
#         if(StringUtils.cleanUpCount%1000 == 0):
#             print('remove_special_char - Cleaned '+str(StringUtils.cleanUpCount)+' records')  
#         import re
#         updated=text;
#         clean = re.compile('<')
#         updated = re.sub(clean, ' ', updated)
#         clean = re.compile('\u00ff')
#         updated = re.sub(clean, ' ', updated)     
#         clean = re.compile('&#39;')
#         updated = re.sub(clean, '\'', updated)
#         clean = re.compile('&#64;')
#         updated = re.sub(clean, '@', updated)
#         clean = re.compile('&#34;')
#         updated = re.sub(clean, '"', updated)
#         clean = re.compile('&#43;')
#         updated = re.sub(clean, '+', updated)
#         clean = re.compile('_+')
#         updated = re.sub(clean, '_', updated)
#         clean = re.compile(' +')
#         updated = re.sub(clean, ' ', updated)
#         clean = re.compile('&amp;')
#         updated = re.sub(clean, '&', updated)        
#         clean = re.compile('&lt;')
#         updated = re.sub(clean, '<', updated)
#         clean = re.compile('&gt;')
#         updated = re.sub(clean, '>', updated)
#                 
#         #print("remove_special_char - Original = "+text)            
#         #print("remove_special_char - Updated = "+updated)   
#         #clean1 = re.compile('&\\#....?;')
#         return updated; #re.sub(clean, '', intm)
# 
#     
#     @staticmethod
#     def nltk2wn_tag(nltk_tag):
#         import nltk
#         from nltk.stem import WordNetLemmatizer
#         from nltk.corpus import wordnet
#         lemmatizer = WordNetLemmatizer()
#         if nltk_tag.startswith('J'):
#             return wordnet.ADJ
#         elif nltk_tag.startswith('V'):
#             return wordnet.VERB
#         elif nltk_tag.startswith('N'):
#             return wordnet.NOUN
#         elif nltk_tag.startswith('R'):
#             return wordnet.ADV
#         else:
#             return None
#     @staticmethod
#     def lemmatize_sentence(sentence):
#         StringUtils.cleanUpCount=StringUtils.cleanUpCount+1
#         if(StringUtils.cleanUpCount%1000 == 0):
#             print('lemmatize_sentence - Cleaned '+str(StringUtils.cleanUpCount)+' records')  
#         import nltk
#         from nltk.stem import WordNetLemmatizer
#         from nltk.corpus import wordnet
#         lemmatizer = WordNetLemmatizer()
#         nltk_tagged = nltk.pos_tag(nltk.word_tokenize(sentence))  
#         wn_tagged = map(lambda x: (x[0], StringUtils.nltk2wn_tag(x[1])), nltk_tagged)
#         res_words = []
#         for word, tag in wn_tagged:
#             if tag is None:            
#                 res_words.append(word)
#             else:
#                 res_words.append(lemmatizer.lemmatize(word, tag))
#         return " ".join(res_words)
#     @staticmethod
#     def remove_stop_words(sentence,custom_stop_words):
#         StringUtils.cleanUpCount=StringUtils.cleanUpCount+1
#         if(StringUtils.cleanUpCount%1000 == 0):
#             print('remove_stop_words - Cleaned '+str(StringUtils.cleanUpCount)+' records')  
#         from nltk.corpus import stopwords
#         from nltk.tokenize import word_tokenize
#         stop_words = set(stopwords.words('english'))
#         stop_words.update(custom_stop_words)
#         #print(stopwords)
#         word_tokens = word_tokenize(sentence)
#         #print(word_tokens)
#         filtered_sentence = ' '.join([w for w in word_tokens if not w in stop_words])
#         #print("remove_stop_words - Original = "+sentence)            
#         #print("remove_stop_words - Updated = "+filtered_sentence)  
#         return filtered_sentence
#     pm = PeristenceManager.getPeristenceManager();        
#     columns=['phrase', 'updated_phrase']
#     wordstandardization = read_sql_table('wordstandardization', pm.engine, 'ecr', None, True, True, columns, None)    
#     @staticmethod
#     def cleanComplexPhrases(text):        
#         updated=text;
#         StringUtils.cleanUpCount=StringUtils.cleanUpCount+1
#         if(StringUtils.cleanUpCount%1000 == 0):
#             print('cleanComplexPhrases - Cleaned '+str(StringUtils.cleanUpCount)+' records')
#         for i in range(len(StringUtils.wordstandardization)):
#             import re
#             ph = StringUtils.wordstandardization.loc[i]['phrase']
#             ph_upd=StringUtils.wordstandardization.loc[i]['updated_phrase'];
#             clean = re.compile('\b?'+ph+'\b?')
#             updated = re.sub(clean,  ph_upd ,updated)
#             #print(ph, ph_upd)
#             #print(updated)
#         return updated;
if __name__ == '__main__':
    str = StringUtils.cleanComplexPhrases('Description: Issue: Application Name: Error Messages: Workstation ID: Contact Name: Contact #: Physical Address: Microsoft Powerpoint - Application Issue Name : NTID : Tel : Email : Location : Is it a BP machine? What build is the machine? (e.g. Voyager) Error Message(s): Problem Determination: Product name: Microsoft Access Incident Type: User Service Restoration Customer Name: Michelle McArthur Customer Region: EMEA Customer Phone Number: To Be Advised Customer Site: Unknown Site - GB Ticketowner Support Company: IBM Ticketowner Support Organization: GOI - Service Desk Ticketowner Support Group: IBM Service Desk');
    print(str)