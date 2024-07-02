__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""
from configparser import ConfigParser
from iia.utils.log_helper import log_setup, get_logger

log = get_logger(__name__)

config_file_path = 'config/iia.ini'


def get_config(key: str=None) -> dict:
    try:
        log.debug(f"key: {key}")
        log.debug(config_file_path)
        config_file = ConfigParser()
        config_file.read(config_file_path)
        config = config_file.__dict__['_sections'].copy()
        log.debug(config)
        if key is not None:
            return config[key]
        else:
            return config
    except Exception as e:
        log.error(e)
        print("Error :",(e))
        return {}