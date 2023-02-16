__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""
from parse_email.parse_email import process_email
from parse_email.utils.config_helper import get_config
from parse_email.utils.log_helper import get_logger, log_setup
import schedule
import time

config = get_config('email')
process_email()
schedule_seconds = 30
try:
    schedule_seconds = int(config['schedule_seconds'])
except:
    schedule_seconds = 30
schedule.every(schedule_seconds).seconds.do(process_email)

while True:
    # Checks whether a scheduled task
    # is pending to run or not
    schedule.run_pending()
    time.sleep(1)