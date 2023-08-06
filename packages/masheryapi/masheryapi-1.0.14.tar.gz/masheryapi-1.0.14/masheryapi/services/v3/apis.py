import json

class Apis:

    def iodoc_from_swagger(self, public_domain, external_api_definition):
        iodoc = {}
        iodoc['name'] = external_api_definition['info']['title']
        iodoc['title'] = external_api_definition['info']['title']
        iodoc['version'] = external_api_definition['info']['version']
        iodoc['description'] = external_api_definition['info']['description']
        iodoc['protocol'] = 'rest'
        iodoc['basePath'] = external_api_definition['schemes'][0] + '://' + external_api_definition['basePath'] + external_api_definition['basePath'] 

        iodoc['resources'] = {}
        for path in external_api_definition['paths']:
            iodoc['resources'][path] = {'methods': {}}
            for http_method in external_api_definition['paths'][path]:
                method = external_api_definition['paths'][path][http_method]
                iodoc['resources'][path]['methods'][method['operationId']] = {'path': path, 'httpMethod': http_method.upper(), 'description': method['description'], 'parameters': {}}
                for parameter in method['parameters']:
                    #'type': parameter['type']  , 'description': parameter['description']
                    iodoc_parameter = {'required': parameter['required'], 'location': parameter['in']}
                    iodoc['resources'][path]['methods'][method['operationId']]['parameters'][parameter['name']] = iodoc_parameter

        return iodoc


    def load_swagger_json(self, external_api_definition):
        try:
            external_api_definition_object = json.loads(external_api_definition)
        except ValueError as err:
            raise ValueError("External source is invalid JSON or invalid Swagger.") 

        if 'info' not in external_api_definition_object:
            raise ValueError("External source is invalid JSON or invalid Swagger.") 
        return external_api_definition_object

    def from_swagger(self, public_domain, external_api_definition):
        try:
            external_api_definition_object = self.load_swagger_json(external_api_definition)
        except ValueError as err:
            return err

        api = {}

        api['name'] = external_api_definition_object['info']['title']
        api['version'] = external_api_definition_object['info']['version']
        api['description'] = external_api_definition_object['info']['description']

        api['endpoints'] = []

        for path in external_api_definition_object['paths']:
            endpoint = {}
            endpoint['name'] = path.replace('/', ' ').replace('{', ' ').replace('}', ' ').strip()
            endpoint['requestPathAlias'] = external_api_definition_object['basePath'] + path
            endpoint['targetRequestPath'] = external_api_definition_object['basePath'] + path

            if external_api_definition_object['schemes'][0] == 'https':
                endpoint['inboundSslRequired'] = True
            else:
                endpoint['inboundSslRequired'] = False

            if 'securityDefinitions' in external_api_definition_object:
                if 'api_key' in external_api_definition_object['securityDefinitions']:
                    endpoint['requestAuthenticationType'] = 'api_key'
                    endpoint['apiKeyValueLocationKey'] = external_api_definition_object['securityDefinitions']['api_key']['name']
                    endpoint['apiKeyValueLocations'] = ['request-header']

            endpoint['publicDomains'] = [{'address': public_domain}]
            endpoint['systemDomains'] = [{'address': external_api_definition_object['host']}]

            endpoint['supportedHttpMethods'] = []
            for http_method in external_api_definition_object['paths'][path]:
                endpoint['supportedHttpMethods'].append(http_method)

            api['endpoints'].append(endpoint)

        return api

    def from_raml(self, external_api_definition):		
        api = {}

        return api

    def to_swagger(self, api_definition):
        external_api_definition = {}

        return external_api_definition

    def to_raml(self, api_definition):        
        external_api_definition = {}

        return external_api_definition
