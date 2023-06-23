# enhancements: make perspective multicloud (Azure, GCP, etc)

import json
import http.client
import ssl
import config
from random import randint

api_key = config.api_key
org_id = 0 # leave zero to create the perspective in the TLOU or whichever OU your accaount is in.

def main():
    #Functions
    #Create a perspective
    def create_perspective(api_key, org_id = 0):
            ref_id = randint(100, 9999)
            base_url = 'chapi.cloudhealthtech.com'
            query = "/v1/perspective_schemas"
            if org_id == 0:
                query = query
            elif org_id:
                query = query + f'?org_id={org_id}'    
            headers = {'Content-type': 'application/json', 'Authorization': f'Bearer {api_key}' }
            body = ({
                "schema": {
                    "name": "Customers",
                    "rules": [
                        {
                            "type": "categorize",
                            "asset": "AwsAccount",
                            "ref_id": f"{ref_id}",
                            "name": "Customers",
                            "tag_field": [
                                "CHT_Customer"
                            ]
                        }
                    ],
                    "constants": [
                        {
                            "type": "Static Group",
                            "list": [
                                {
                                    "ref_id": f"{ref_id+1}",
                                    "name": "Other",
                                    "is_other": "true"
                                }
                            ]
                        }
                    ],
                    "include_in_reports": "true"
                }
            })
            connection = http.client.HTTPSConnection(base_url, context=ssl._create_unverified_context())
            connection.request('POST', query, body=json.dumps(body), headers = headers)
            response = connection.getresponse()
            status = response.status
            payload = json.loads(response.read().decode())
            connection.close()
            if status == 404:
                raise Exception('Error 404, Check your query')
            elif status == 403:
                raise Exception(f'Error 403, Check your API Key. {payload}, {query}')
            else:
                return [status, payload]
    #Work
    print("Creating Customer Perspective...")
    print(create_perspective(api_key))
main()