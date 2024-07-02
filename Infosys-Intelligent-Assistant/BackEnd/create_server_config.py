__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

import toml
import socket
from src.iia.utils.config_helper import get_config
from src.iia.utils.log_helper import log_setup,get_logger
server_fields = get_config('server')

logging = get_logger(__name__)

log_setup()

system_hostname = socket.getfqdn().lower()

server_config = {}
ssl_fields = get_config('ssl')
ssl_flag = str(ssl_fields['ssl']).lower()
del ssl_fields['ssl']
server_config.update({"bind":f"{server_fields['hostname']}:{server_fields['port']}"})
if ssl_flag == 'true':
    server_config.update(ssl_fields)
logging.info(f"system_hostname: {system_hostname}")
logging.info(f"configured hostname: {str(server_fields['hostname']).lower()}")
if system_hostname != str(server_fields['hostname']).lower():
    logging.warning("System hostname and configured hostname differs")

server_config['include_server_header'] = False

output_file_name = "./config/server_config.toml"

with open(output_file_name, "w") as toml_file:
    toml.dump(server_config, toml_file)

