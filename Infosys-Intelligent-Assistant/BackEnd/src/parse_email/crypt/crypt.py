__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""

import base64
import json
import pickle

import rsa
import getpass

from parse_email.utils.config_helper import get_config
from parse_email.utils.log_helper import get_logger

log = get_logger(__name__)

def encrypt(filename: str):
    """
    :return: None
    """
    config_encrypt = get_config('encrypt')

    publicKey, privateKey = rsa.newkeys(int(config_encrypt['key_bits']))

    username = input("Enter the username")

    password = getpass.getpass(prompt='Enter the Password')

    encMessage = rsa.encrypt(password.encode(),
                             publicKey)

    dict_mongodb = {
        "username": username,
        "passcode": encode_data({
            "password": encMessage,
            "publicKey": publicKey.save_pkcs1(format='DER'),
            "privatekey": privateKey.save_pkcs1(format='DER')})
    }

    json_str = json.dumps(dict_mongodb, indent=1)

    with open(filename, "w") as outfile:
        outfile.write(json_str)

    log.info(f"Updated Details {dict_mongodb}")


def decrypt_credentials(filename: str):
    """

    :return: {username, password}
    """

    log.info('Connecting to Mongo DB')

    with open(filename, 'r') as f:
        config_collection = json.load(f)

    passcode = decode_data(config_collection['passcode'])

    privatekey = rsa.PrivateKey.load_pkcs1(passcode['privatekey'], "DER")

    decMessage = rsa.decrypt(passcode['password'], privatekey).decode()

    return {'username': config_collection['username'], 'password': decMessage}


def encode_data(data):
    pickled = pickle.dumps(data)
    pickled_b64 = base64.b64encode(pickled)
    return pickled_b64.decode('utf-8')


def decode_data(data):
    return pickle.loads(base64.b64decode(data.encode()))
