__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

import os
os.environ['PYTHONPATH'] = 'src'
from intent.crypt.crypt import encrypt
from intent.utils.log_helper import log_setup, get_logger

log = get_logger(__name__)
log_setup()
try:
    log.info('Running mongodb credentials')
    file_name = input("Enter Json File name: ").replace('.json','')
    encrypt(f'./config/{file_name}.json')
except Exception as e:
    log.error(e)
    raise
