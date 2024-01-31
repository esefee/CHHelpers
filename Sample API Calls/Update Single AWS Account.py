# this is a template for using CloudHealth rest apis in python. Given an API key and query (everything after 'chapi.cloudhealthtech.com', including the /). This script will save the results to a file called response.json in the current working directory.


import json
import http.client
import ssl
import config

api_key = config.api_key
asset_id = ""

#Functions
def update_aws_account(api_key, query, asset_id, client_api_id=0, org_id = 0):
    base_url = 'chapi.cloudhealthtech.com'
    query = f'/v1/aws_accounts/{asset_id}'
    if client_api_id != 0 and  org_id == 0:
        query = query + f'?client_api_id={client_api_id}'
    elif org_id != 0 and client_api_id == 0:
        query = query + f'?org_id={org_id}'
    elif client_api_id != 0 and  org_id != 0:
        query = query + f'?client_api_id={client_api_id}&client_api_id={client_api_id}'
    headers = {'Content-type': 'application/json', 'Authorization': f'Bearer {api_key}'} 
    connection = http.client.HTTPSConnection(base_url, context=ssl._create_unverified_context())
    connection.request('PUT', url=query, headers=headers)
    response = connection.getresponse()
    body = json.loads(response.read().decode())    
    connection.close()
    if response.status == 200:
        return body
    elif response.status  == 404:
        raise Exception('Error 404, Check that your policy ID is valid')
    elif response.status  == 403:
        raise Exception('Error 403, Check that your API Key is correct')
    else:
        raise Exception(body)

def main():
    #Work
    print(update_aws_account(api_key))

if __name__ == '__main__':
    main()