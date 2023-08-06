import json, logging, time
from masheryapi.api.masheryV3  import MasheryV3
from masheryapi.api.masheryV2 import MasheryV2

class Auth:

    def __init__(self, protocol, api_host, area_id, area_uuid, apikey, secret, logger_name):
        self.masheryV3 = MasheryV3(protocol, api_host)
        self.masheryV2 = MasheryV2(protocol, api_host)
        self.area_id = area_id
        self.area_uuid = area_uuid
        self.apikey = apikey
        self.secret = secret
        self.access_tokens = {}
        self.authorization_codes = {}

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


    def access_token_to_list(self, access_token, authorization_code, scope, redirect_uri):
        self.access_tokens[authorization_code + scope + redirect_uri] = access_token

    def authorization_code_to_list(self, authorization_code, api_id, client_id, redirect_uri, scope, user_context):
        self.authorization_codes[api_id + client_id + redirect_uri + scope + user_context] = authorization_code

    def access_token_from_list(self, authorization_code, scope, redirect_uri):
        try:
            return self.access_tokens[authorization_code + scope + redirect_uri]
        except KeyError as err:
            return None

    def authorization_code_from_list(self, api_id, client_id, redirect_uri, scope, user_context):
        try:
            return self.authorization_codes[api_id + client_id + redirect_uri + scope + user_context]
        except KeyError as err:
            return None

    def authorize(self, api_id, client_id, redirect_uri, scope, user_context):
        payload = { 'jsonrpc':'2.0', 'method':'oauth2.createAuthorizationCode', 'params': {'service_key':api_id, 'client': { 'client_id': client_id }, 'uri':{ 'redirect_uri': redirect_uri }, 'scope': scope, 'user_context': user_context, 'response_type':'code' }, 'id':1}
        try:
            code_request_time = time.time()
            authorization_code = self.masheryV2.post(self.area_id, self.apikey, self.secret, json.dumps(payload))
            
            if authorization_code != None:
                authorization_code_object = {}
                authorization_code_object['request_time'] = code_request_time
                authorization_code_object['code'] = authorization_code['result']['code']
                self.authorization_code_to_list(authorization_code_object, api_id, client_id, redirect_uri, scope, user_context)
        except ValueError as err:
            if (self.logger != None):
                self.logger.error('ERROR: %s', json.dumps(err.args))
            raise ValueError(err.args)

    def get_authorization_code(self, api_id, client_id, redirect_uri, scope, user_context):
        authorization_code = self.authorization_code_from_list(api_id, client_id, redirect_uri, scope, user_context)
        if authorization_code == None or authorization_code['request_time'] - time.time() > 60:
            self.authorize(api_id, client_id, redirect_uri, scope, user_context)
            authorization_code = self.authorization_code_from_list(api_id, client_id, redirect_uri, scope, user_context)
            if authorization_code == None:
                return None
            else:
               return authorization_code['code']
        return authorization_code['code']

    def authenticate(self, username, password, area_uuid ):
        try:
            token_request_time = time.time()
            access_token = self.masheryV3.authenticate(self.apikey, self.secret, username, password, area_uuid )
            if access_token != None:
                access_token_object = {}
                access_token_object['request_time'] = token_request_time
                access_token_object['token'] = access_token
                self.access_token_to_list(access_token_object, username, area_uuid, 'token')
        except ValueError as err:
            if (self.logger != None):
                self.logger.error('ERROR: %s', json.dumps(err.args))
            raise ValueError(err.args)

    def authenticate_with_code(self, authorization_code, scope, redirect_uri):
        try:
            token_request_time = time.time()
            access_token = self.masheryV3.authenticate_with_code(self.apikey, self.secret, authorization_code, scope, redirect_uri)
            if access_token != None:
                access_token_object = {}
                access_token_object['request_time'] = token_request_time
                access_token_object['token'] = access_token
                self.access_token_to_list(access_token_object, authorization_code, scope, redirect_uri)
        except ValueError as err:
            if (self.logger != None):
                self.logger.error('ERROR: %s', json.dumps(err.args))
            raise ValueError(err.args)

    def get_access_token(self, username, password, area_uuid):
        access_token = self.access_token_from_list(username, area_uuid, 'token')

        if access_token == None or access_token['request_time'] - time.time() > 15:
            self.authenticate(username, password, area_uuid)
            access_token = self.access_token_from_list(username, area_uuid, 'token')
            if access_token == None:
                return None
            else:
                return access_token['token']
        return access_token['token']

    def get_access_token_with_code(self, authorization_code, scope, redirect_uri ):
        access_token = self.access_token_from_list(authorization_code, scope, redirect_uri)

        if access_token == None or access_token['request_time'] - time.time() > 15:
            self.authenticate_with_code(authorization_code, scope, redirect_uri)
            access_token = self.access_token_from_list(authorization_code, scope, redirect_uri)
            if access_token == None:
                return None
            else:
                return access_token['token']
        return access_token['token']