import json, logging, time
from masheryapi.api.masheryV3 import MasheryV3

class Base:

    def __init__(self, protocol, api_host, logger_name):
        self.masheryV3 = MasheryV3(protocol, api_host)

        # turn off info from http requests library
        logging.getLogger('requests').setLevel(logging.ERROR)
      
        formatter2 = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        l1 = logging.getLogger(logger_name)
        fileHandler1 = logging.FileHandler('mashery_v3.log', mode='a')
        fileHandler1.setLevel(logging.INFO)
        fileHandler1.setFormatter(formatter2)
        l1.addHandler(fileHandler1)
        l1.setLevel(logging.INFO)        
        l1 = logging.getLogger(logger_name)
        self.logger = l1
  
    def fetch(self, access_token, resource, params):
        try:
          result = self.masheryV3.get(access_token, resource, params)
        except ValueError as err:
            if (self.logger != None):
                self.logger.error('ERROR: %s', json.dumps(err.args))
            raise ValueError(err.args)
        return result

    def create(self, access_token, resource, params, item):
        response = self.masheryV3.post(access_token, resource, params, item)
        if (response.status_code == 200):
            return response
        else:
            if (self.logger != None):
                self.logger.error('ERROR: %s', json.dumps(response.json()))
            return response

    def update(self, access_token, resource, params, item):
        response = self.masheryV3.put(access_token, resource, params, item)
        if (response.status_code == 200):
            return response
        else:
            if (self.logger != None):
                self.logger.error('ERROR: %s', json.dumps(response.json()))
            return response


    def delete(self, object_type, item_data):
      result = []
      method = '{"method":"' + object_type + '.delete","id":1,"params":[' + json.dumps(item_data) + ']}'
      try:
          if (self.logger != None):
              self.logger.info('API METHOD: %s', method)

          result = self.masheryV2.post(self.site_id, self.apikey, self.secret, method)
          if (self.logger != None):
              self.logger.info('RESPONSE: %s', json.dumps(result))

          return result
      except ValueError as err:
          if (self.logger != None):
              self.logger.error('ERROR: %s', json.dumps(err.args))
          raise ValueError(err.args)