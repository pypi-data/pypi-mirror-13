import os
import requests
import base64

# urls
SERVER = 'https://devservices.optionshop.com'
REQUEST_TOKEN_URL = os.path.join(SERVER, 'token')

# client creds
CLIENT_NAME = "Default"
CLIENT_ID = "54cfa6cdf30200ad8de4de09"
CLIENT_SECRET = "f3f6791f-ae0a-4b5f-9603-522bfb051bf1"


class TokenClient():
    def __init__(self, server=SERVER, client_name=CLIENT_NAME, client_id=CLIENT_ID, client_secret=CLIENT_SECRET):
        self.server = server
        self.token_url = os.path.join(SERVER, 'token')
        self.client_name = client_name
        self.client_id = client_id
        self.client_secret = client_secret
        self.authorization_header = {"Authorization": "Basic %s" % base64.b64encode(CLIENT_ID + ":" + CLIENT_SECRET)}
        self.access_token = None
        self.refresh_token = None
        self.expires_in = None

    #
    #	https://devservices.optionshop.com/docs/auth#tokenpostpwd
    #
    def request(self, username, password):
        payload = {
            "grant_type": "password",
            "username": username,
            "password": password
        }
        resp = requests.post(self.token_url, data=payload, headers=self.authorization_header)

        if resp.reason == "OK":
            _resp = eval(resp.content)
            _resp["status_code"] = 200
            _resp["reason"] = "OK"
            self.access_token = _resp['access_token']
            self.refresh_token = _resp['refresh_token']
            self.expires_in = _resp['expires_in']
            return _resp
        else:
            return {"status_code": resp.status_code, "reason": eval(resp.content)}

    #
    #   https://devservices.optionshop.com/docs/auth#tokenpostrefresh
    #
    def refresh(self):
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        }
        resp = requests.post(self.token_url, data=payload, headers=self.authorization_header)

        if resp.reason == "OK":
            _resp = eval(resp.content)
            _resp["status_code"] = 200
            _resp["reason"] = "OK"
            self.access_token = _resp['access_token']
            self.refresh_token = _resp['refresh_token']
            self.expires_in = _resp['expires_in']
            return _resp
        else:
            return {"status_code": resp.status_code, "reason": eval(resp.content)}


    def resource_request(self, url="events", payload=None):
        header = {
            "Authorization": "Bearer %s" % self.access_token,
            "Content-Type": "application/json"
        }
        
        resp = requests.post(os.path.join(self.server, url), payload=None, headers=header)

        return resp