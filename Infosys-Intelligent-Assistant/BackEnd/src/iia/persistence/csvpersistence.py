__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

from builtins import print

class CSVPersistence(object,):
    def __init__(self,config):
        #Do Nothing;
        self.config=config
        print("CSVPresistence.__init__")
    def readList(self,name):
        #Do Nothing
        print("CSVPresistence.readList")
    #Read the stop words from CSV file
    def readStopWords(self):
        print("Reading Stop Words From CSV")
        import csv
        #from curses.has_key import python
        with open('./../data/stopwords.csv', 'r') as readFile:
            reader = csv.reader(readFile)
            list1 = list(reader)
            STOP_WORDS = list1[0]
            readFile.close()
            len(STOP_WORDS)
            return STOP_WORDS;            
        
    #End readStopWordsFromCSV
    def readIncidentData(self):
        # Load ticket data
        print("readIncidentData")
        import pandas as pd
        df=pd.read_csv('./../data/Ticket_Dump_v2_half.csv',encoding='latin-1')
             
        print("Done reading IncidentData")
        return df