# enhancements: make perspective multicloud (Azure, GCP, etc)

import json
import http.client
import ssl
import config

api_key = config.api_key
client_api_id = 0 # leave zero unless you are a partner running this script on behalf of your customer with an API Key from your partner tenant.
org_id = 0 # leave zero to create the perspective in the TLOU or whichever OU your accaount is in.

def main():
    #Functions
    #Create a perspective
    def create_perspective(api_key, client_api_id = 0, org_id = 0):
            base_url = 'chapi.cloudhealthtech.com'
            query = "/v1/perspective_schemas"
            if client_api_id == 0 & org_id == 0:
                query = query
            elif client_api_id & org_id == 0:
                query = query + f'?client_api_id={client_api_id}'
            elif org_id & client_api_id == 0:
                query = query + f'?org_id={org_id}'
            elif client_api_id & org_id:
                query = query + f'?client_api_id={client_api_id}&org_id={org_id}'
            headers = {'Content-type': 'application/json', 'Authorization': f'Bearer {api_key}' }
            body = ({
                "schema": {
                    "name": "Detected Waste",
                    "rules": [
                        {
                            "type": "categorize",
                            "asset": "AwsTaggableAsset",
                            "ref_id": "1924145686101",
                            "name": "Waste detected by Month",
                            "tag_field": [
                                "cht_waste_detected"
                            ]
                        },
                        {
                            "type": "categorize",
                            "asset": "AzureTaggableAsset",
                            "ref_id": "1924145686107",
                            "name": "Waste detected by Month",
                            "tag_field": [
                                "cht_waste_detected"
                            ]
                        }
                    ],
                    "merges": [
                        {
                            "type": "Dynamic Group Block",
                            "to": "1924145686101",
                            "from": [
                                "1924145686107"
                            ]
                        }
                    ],
                    "constants": [
                        {
                            "type": "Dynamic Group Block",
                            "list": [
                                {
                                    "ref_id": "1924145686101",
                                    "name": "Waste detected by Month"
                                },
                                {
                                    "ref_id": "1924145686107",
                                    "name": "Waste detected by Month",
                                    "fwd_to": "1924145686101"
                                }
                            ]
                        },
                        {
                            "type": "Static Group",
                            "list": [
                                {
                                    "ref_id": "1924166595367",
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
    print("Creating Detected Waste Perspective")
    print(create_perspective(api_key))
main()