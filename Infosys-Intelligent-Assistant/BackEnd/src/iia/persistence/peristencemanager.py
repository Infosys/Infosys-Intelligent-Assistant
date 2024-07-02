__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

from iia.persistence.csvpersistence import CSVPersistence
from iia.persistence.sqlpersistence import SQLPersistence
from iia.persistence.mongodbpersistence import MongoDBPersistence

class PeristenceManager(object):
    def __init__(self):
        #Do Nothing;
        print("PeristenceManager.__init__")
    @staticmethod
    def getPeristenceManager():
        #Do Nothing
        global config
        import configparser
        config = configparser.RawConfigParser();
        config.read('config/iia.ini');
        pesistenceType = config.get('Persistence', 'persistenceType');
        global pesistenceManager
        if(pesistenceType=="CSV"):
            pesistenceManager= CSVPersistence(config);
        elif(pesistenceType=="MySQL"):
            pesistenceManager= SQLPersistence(config);
        elif(pesistenceType=="Mongo"):
            pesistenceManager= MongoDBPersistence(config);     
        return pesistenceManager
    @staticmethod
    def getPeristenceManagerByType(pesistenceType):
        #Do Nothing        
        global config
        import configparser
        config = configparser.RawConfigParser();
        config.read('config/iia.ini');
        if(pesistenceType=="CSV"):
            pesistenceManager= CSVPersistence(config);
        elif(pesistenceType=="MySQL"):
            pesistenceManager= SQLPersistence(config);
        elif(pesistenceType=="Mongo"):
            pesistenceManager= MongoDBPersistence(config);     
        return pesistenceManager