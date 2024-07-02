__copyright__ = """Copyright 2022 Infosys Ltd.
Use of this source code is governed by MIT license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT."""
import json
from bson import json_util
from flask import redirect, session, request
from requests_oauthlib import OAuth2Session
import requests
from iia.restservice import RestService
from iia.utils.log_helper import log_setup, get_logger

app = RestService.getApp()
app.secret_key="iia-secret-key"


log = get_logger(__name__)

sso_file_path = 'config/sso_config.json'
class SSOAuthentication(object):

    def __init__(self):
        pass

    @staticmethod
    def login():

        with open(sso_file_path) as f:
            client_secrets = json.load(f)

        authenticate = OAuth2Session(client_secrets['client_id'], redirect_uri=client_secrets['redirect_uris'],
                                     scope=client_secrets['scope'])
        authorization_url, state = authenticate.authorization_url(client_secrets['auth_uri'])
        # State is used to prevent CSRF, keep this for later.
        session['oauth_state'] = state
        log.debug(f'authentication request {authorization_url}')
        log.info(f'posting authentication request to server')
        resp = [{"Status": "redirect", "redirect_url": f"{authorization_url}", "State": f"{state}"}]
        return json_util.dumps(resp)

    @staticmethod
    def auth(forms:dict):
        try:
            with open(sso_file_path) as f:
                client_secrets = json.load(f)
            log.info(f"client_secrets: {client_secrets}")
            log.info(f"forms: {forms}")
            request_url = client_secrets['redirect_uris'] + f"?state={forms['state']}&code={forms['code']}"
            authentication = OAuth2Session(client_secrets['client_id'],
                                           redirect_uri=client_secrets['redirect_uris'],
                                           scope=client_secrets['scope'])
            token = authentication.fetch_token(client_secrets['token_uri'],
                                               client_secret=client_secrets['client_secret'],
                                               authorization_response=request_url)
            userinfo = authentication.get(client_secrets['userinfo']).json()
            log.debug(f'userinfo {userinfo}')
            log.info('redirected to homepage after successful login')
            resp = [{"Status": "Success", "State": f"{forms['state']}",
                     "UserId": f"{userinfo['email']}"}]
            return json_util.dumps(resp)
        except Exception as e:
            log.exception(e)
            resp = [{"Status": "Failure", "Access": "None"}]
            return json_util.dumps(resp)

    @staticmethod
    def logout():
        log.info('Logout')
        with open(sso_file_path) as f:
            client_secrets = json.load(f)
        try:
            if session.get('Auth_Status'):
                session.pop('Auth_Status')
        except Exception as e:
            pass

        return client_secrets['signoff']