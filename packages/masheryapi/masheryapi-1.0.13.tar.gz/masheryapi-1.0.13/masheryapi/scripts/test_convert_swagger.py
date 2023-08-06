# -*- coding: utf-8 -*-
import sys
from apis import Apis

def main(argv):
    api_service = Apis()

    with open('/Volumes/CaseSensitiveHD/petstore1.json') as data_file: 
        external_api_definition_content = data_file.read()

    api_definition = api_service.from_swagger('api.demo3.com', external_api_definition_content)
    print api_definition

    with open('/Volumes/CaseSensitiveHD/petstore2.json') as data_file: 
        external_api_definition_content = data_file.read()

    api_definition = api_service.from_swagger('api.demo3.com', external_api_definition_content)
    print api_definition

if __name__ == "__main__":
    main(sys.argv[1:])