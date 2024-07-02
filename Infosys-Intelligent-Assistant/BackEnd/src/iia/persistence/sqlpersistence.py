__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

from sqlalchemy import create_engine

class SQLPersistence(object):
     
    def __init__(self,config):
        #Do Nothing;
        print("SQLPresistence.__init__")
        self.config = config
        self.connectToDB();
    def readList(self,name):
        #Do Nothing
        print("SQLPresistence.readList")
    #Make a connection to the database
    def connectToDB(self):
        print("Connecting To DB");
        
        name = self.config.get('DatabaseSection', 'database.dbname');
        user = self.config.get('DatabaseSection', 'database.user');
        password = self.config.get('DatabaseSection', 'database.password');
        host = self.config.get('DatabaseSection', 'database.host');
        port = self.config.get('DatabaseSection', 'database.port');    
       
        
        print("Connected To DB");
    def closeDBConnection(self):
        print("Closing DB Connection");
        self.cnx.close()
        print("Closed DB Connection");
    def insertCleansedIncidentData(self,data):
       
        data.to_sql(name='incidentdata_cleansed', con=self.engine, schema='ecr', if_exists='append', 
                    index=False, index_label=None, chunksize=None, dtype=None)
        '''
        query = "INSERT INTO ecr.incidentdata_cleansed(number,description) VALUES(%s,%s)"    
        args = (incidentID, description)
        cursor = self.cnx.cursor();
        try:
            cursor.execute(query, args);
            self.cnx.commit()
        except Error as error:
            print(error)
        finally:
            cursor.close()
        '''
    #Read the stop words from CSV file
    def readStopWords(self):
        print("Reading Stop Words From CSV");
        import csv
        #from curses.has_key import python
        with open('./../data/stopwords.csv', 'r') as readFile:
            reader = csv.reader(readFile)
            list1 = list(reader)  
            global ENGLISH_STOP_WORDS
            ENGLISH_STOP_WORDS = list1[0]
            readFile.close()
            len(ENGLISH_STOP_WORDS)
        print("Done Reading Stop Words From CSV");
    #End readStopWordsFromCSV
    #Close DB connection