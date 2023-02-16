__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

import unittest
from intent.utils.stringutils import StringUtils
#from com.infosys.impact.utils.StringUtils import StringUtils


class TestStringUtils(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testName(self):
        str = StringUtils.cleanComplexPhrases('Description: Issue: Application Name: Error Messages: Workstation ID: Contact Name: Contact #: Physical Address: Microsoft Powerpoint - Application Issue Name : NTID : Tel : Email : Location : Is it a BP machine? What build is the machine? (e.g. Voyager) Error Message(s): Problem Determination: Product name: Microsoft Access Incident Type: User Service Restoration Customer Name: Michelle McArthur Customer Region: EMEA Customer Phone Number: To Be Advised Customer Site: Unknown Site - GB Ticketowner Support Company: IBM Ticketowner Support Organization: GOI - Service Desk Ticketowner Support Group: IBM Service Desk');
        print("test");
        #assert(False)
        pass
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main() 