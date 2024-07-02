__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""
import datetime as dt
import logging.config
import os

import yaml

log_file_folder = 'logs'
config_file_folder = 'config/logging.yaml'


def log_setup(filename: str = 'iia'):
    """
    Initialize a project-level logging object and read in the configuration parameters from an external file.
    You will only need to load this function one time in your main script.
    """
    with open(config_file_folder) as log_file:
        logging_conf = yaml.safe_load(log_file)

    if not os.path.exists(rf'{log_file_folder}/{dt.datetime.now():%Y_%m_%d}'):
        os.makedirs(rf'{log_file_folder}/{dt.datetime.now():%Y_%m_%d}', exist_ok=True)

    logging_conf['handlers']['file']['mode'] = 'a'
    logging_conf['handlers']['file'][
        'filename'] = rf'{log_file_folder}/{dt.datetime.now():%Y_%m_%d}/{dt.datetime.now():%Y%m%d_%H}_{filename}.log'
    logging.config.dictConfig(logging_conf)


def get_logger(name: str):
    """
    Initialize a module-level logging object. This must be loaded in at the start of every module.
    :param name: name of file using the logger, should be provided by using the __name__ variable
    :return: configured logger
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        # Prevent logging from propagating to the root logger
        logger.propagate = 0
        console = logging.StreamHandler()
        logger.addHandler(console)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(lineno)d - %(message)s')
        console.setFormatter(formatter)

    return logger
