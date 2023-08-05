__author__ = 'Sinisa'


import json
import requests
from sbg_cli.sbg_docker.auth.error import AuthException


class Authenticator(object):

    def __init__(self, auth_server_url, auth_server_api_version):
        self.auth_server_url = auth_server_url
        self.auth_server_api_version = auth_server_api_version

    def get_session_usrpass(self, username, password):
        url = '{}/{}/session/open'.format(self.auth_server_url, self.auth_server_api_version)
        data = {
            "credentials": {
                "username": username,
                "password": password
            },
            "session": {
                "namespace": "cgccli",
                "scope": []
            }
        }
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json.dumps(data), headers=headers)
        if response.status_code != 200:
            raise AuthException("Failed to open session for user %s" % username)
        return response.json().get('message', {}).get('session_id')

    def get_session_token(self, token):
        url = '{}/{}/session/open/auth'.format(self.auth_server_url, self.auth_server_api_version)
        headers = {'auth-token': token}
        response = requests.post(url=url, headers=headers)
        if response.status_code != 200:
            raise AuthException("Failed to open session with auth token")
        return response.json().get('message', {}).get('session_id')

    def get_username(self, session):
        url = '{}/{}/user'.format(self.auth_server_url, self.auth_server_api_version)
        headers = {'session-id': session, 'Content-Type': 'application/json'}
        response = requests.get(url=url, headers=headers)
        if response.status_code != 200:
            raise AuthException("Failed to get username for session: %s" % session)
        return response.json().get('message').get('username')

    def check_session(self, username, session):
        url = '{}/{}/session/check'.format(self.auth_server_url, self.auth_server_api_version)
        headers = {'session_id': session, 'Content-Type': 'application/json'}
        response = requests.get(url=url, headers=headers)
        if response.status_code != 200:
            try:
                return self.get_username(session) == username
            except AuthException:
                return False
        return True