"""
The RequestClient gets and refreshes tokens and also allows for resource requests.
"""

import os
import json
import requests
import base64
from datetime import datetime, timedelta


class RequestClient():
    def __init__(self, server, client_id, client_secret, username, password):
        self.server = server
        self.token_url = os.path.join(self.server, 'token')
        self.client_id = client_id
        self.client_secret = client_secret
        self.authorization_header = {"Authorization": "Basic %s" % base64.b64encode(client_id + ":" + client_secret)}
        self.access_token = None
        self.refresh_token = None
        self.expires_at = None
        self.is_valid_session = False
        self.is_valid_reason = None
        # get new token on init
        self.token_get(username, password)

    #
    #   This method can be manually called but is called when you initialize a RequestClient()
    #   For more details visit: https://devservices.optionshop.com/docs/auth#tokenpostpwd
    #
    def token_get(self, username, password):
        payload = {
            "grant_type": "password",
            "username": username,
            "password": password
        }
        resp = requests.post(self.token_url, data=payload, headers=self.authorization_header)

        if resp.status_code == 200:
            _resp = json.loads(resp.content)
            _resp["status_code"] = 200
            _resp["reason"] = "OK"
            self.access_token = _resp['access_token']
            self.refresh_token = _resp['refresh_token']
            self.expires_at = datetime.utcnow() + timedelta(seconds=_resp['expires_in'])
            self.is_valid_session = True
            self.is_valid_reason = "OK"

            return _resp
        else:
            self.is_valid_session = False
            self.is_valid_reason = json.loads(resp.content)

            return {
                "status_code": resp.status_code,
                "reason": json.loads(resp.content)
            }

    #
    #   This method can be manually called but the request method will auto refresh as needed
    #   For more details visit: https://devservices.optionshop.com/docs/auth#tokenpostrefresh
    #
    def token_refresh(self):
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        }
        resp = requests.post(self.token_url, data=payload, headers=self.authorization_header)

        if resp.status_code == 200:
            _resp = json.loads(resp.content)
            _resp["status_code"] = 200
            _resp["reason"] = "OK"
            self.access_token = _resp['access_token']
            self.refresh_token = _resp['refresh_token']
            self.expires_at = datetime.utcnow() + timedelta(seconds=_resp['expires_in'])
            self.is_valid_session = True
            self.is_valid_reason = "OK"

            return _resp
        else:
            self.is_valid_session = False
            self.is_valid_reason = json.loads(resp.content)

            return {
                "status_code": resp.status_code,
                "reason": json.loads(resp.content)
            }

    #
    #   Resource requests
    #   Fore more details visit:  https://devservices.optionshop.com/docs/overview
    #
    def request(self, request_type, url="events", data=None):

        #   refresh token if necessary
        if datetime.utcnow() >= self.expires_at:
            self.token_refresh()

        header = {
            "Authorization": "Bearer %s" % self.access_token,
            "Content-Type": "application/json"
        }

        request_url = os.path.join(self.server, url)

        if request_type.lower() == "get":
            request_function = requests.get
        elif request_type.lower() == "post":
            request_function = requests.post
        elif request_type.lower() == "put":
            request_function = requests.put
        elif request_type.lower() == "delete":
            request_function = requests.delete

        if data:
            if isinstance(data, dict):
                resp = request_function(request_url, data=json.dumps(data), headers=header)
            else:
                return {
                    "data": None,
                    "status_code": 500,
                    "reason": "'data' parameter must be of type dict."
                }

        else:
            resp = request_function(request_url, headers=header)

        if resp.status_code == 200:
            return {
                "data": json.loads(resp.content),
                "status_code": 200,
                "reason": resp.reason
            }

        else:
            return {
                "data": None,
                "status_code": resp.status_code,
                "reason": resp.reason
            }
