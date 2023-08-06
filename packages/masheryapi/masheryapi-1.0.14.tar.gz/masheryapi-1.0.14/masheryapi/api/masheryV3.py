import requests, json
from requests.auth import HTTPBasicAuth

class MasheryV3:

    def __init__(self, protocol, api_host):
        self.protocol = protocol
        self.api_host = api_host
        self.token_endpoint = '/v3/token'
        self.resource_endpoint = '/v3/rest'

    def authenticate_with_code(self, apikey, secret, code, area_uuid, redirect_uri):
        payload = {'grant_type': 'authorization_code', 'code' : code, 'redirect_uri': redirect_uri, 'scope' : area_uuid} 
        response = requests.post(self.protocol + '://' + self.api_host + self.token_endpoint, auth=HTTPBasicAuth(apikey, secret), data=payload, verify=False)
        if response.status_code == 200:
            return response.json()
        else:
            raise ValueError(response.json())

    def authenticate(self, apikey, secret, username, password, area_uuid):
        payload = {'grant_type': 'password', 'username' : username, 'password'  : password, 'scope' : area_uuid} 
        response = requests.post(self.protocol + '://' + self.api_host + self.token_endpoint, auth=HTTPBasicAuth(apikey, secret), data=payload, verify=False)
        if response.status_code == 200:
            return response.json()
        else:
            raise ValueError(response.json())

    def get(self, token, resource, params):
        headers = {"Content-type": "application/json", "Authorization": 'Bearer ' + token}
        response = requests.get(self.protocol + '://' + self.api_host + self.resource_endpoint + resource + '?' + params, headers=headers, verify=False)
        return response

    def put(self, token, resource, params, payload):
        headers = {"Content-type": "application/json", "Authorization": 'Bearer ' + token}
        response = requests.put(self.protocol + '://' + self.api_host + self.resource_endpoint + resource + '?' + params, headers=headers, data=json.dumps(payload), verify=False)
        return response

    def post(self, token, resource, params, payload):
        headers = {"Content-type": "application/json", "Authorization": 'Bearer ' + token}
        response = requests.post(self.protocol + '://' + self.api_host + self.resource_endpoint + resource + '?' + params, headers=headers, data=json.dumps(payload), verify=False)
        return response

    def delete(self, token, resource):
        headers = {"Content-type": "application/json", "Authorization": 'Bearer ' + token}
        response = requests.delete(self.protocol + '://' + self.api_host + self.resource_endpoint + resource , headers=headers, verify=False)
        return response.status_code