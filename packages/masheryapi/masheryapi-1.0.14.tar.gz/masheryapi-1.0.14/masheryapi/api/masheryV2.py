import requests, hashlib, time, logging

class MasheryV2:

    def __init__(self, protocol, api_host):
        self.protocol = protocol
        self.api_host = api_host

    def get(self, site_id, apikey, secret, resource, params):
        resourceEndpoint = '/v2/rest'
        url = str(self.protocol) + '://' + str(self.api_host) + resourceEndpoint + '/' + str(site_id) + resource + '?apikey=' + apikey + '&sig=' + self.hash(apikey, secret) + params
        response = requests.get(url)
        if (response.status_code == 200):
            return response.json()
        else:
            return None

    def post(self, site_id, apikey, secret, payload):
        resourceEndpoint = '/v2/json-rpc'
        headers = {"Content-type": "application/json"}
        url = str(self.protocol) + '://' + str(self.api_host) + resourceEndpoint + '/' + str(site_id) + '?apikey=' + apikey + '&sig=' + self.hash(apikey, secret)
        response = requests.post(url, headers=headers, data=payload)
        responseJson = response.json()

        if (response.status_code == 200):
          return responseJson
        else:
          raise ValueError(responseJson['error']) 

    def hash(self, apikey, secret):
        authHash = hashlib.md5();
        temp = str.encode(str(apikey) + str(secret) + repr(int(time.time())))
        authHash.update(temp)
        return authHash.hexdigest()