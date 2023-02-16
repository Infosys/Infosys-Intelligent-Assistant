__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

from parse_email.crypt.crypt import encrypt
from parse_email.utils.log_helper import log_setup, get_logger

log = get_logger(__name__)
# log_setup()
try:
    log.info('Running email credentials')
    encrypt('./config/email_config.json')
except Exception as e:
    log.error(e)
    raise
