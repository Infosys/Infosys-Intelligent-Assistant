__created__ = "Mar 19, 2019"
__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""


class StringUtils(object):
    cleanUpCount = 0

    def __init__(self):
        # Do Nothing;
        print("PeristenceManager.__init__")

if __name__ == '__main__':
    str = StringUtils.cleanComplexPhrases(
        'Description: Issue: Application Name: Error Messages: Workstation ID: Contact Name: Contact #: Physical Address:');
    print(str)
