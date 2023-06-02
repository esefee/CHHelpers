import json
import http.client
import ssl
import config

api_key = config.api_key

client_api_id = 0 # leave zero unless you are a partner running this script on behalf of your customer with an API Key from your partner tenant.

def main():
    policies = []
    #Functions
    def get_all_policies(api_key):
        page = 1
        while page:
            base_url = 'chapi.cloudhealthtech.com'
            query = f'/v1/policies?page={page}&per_page=30'
            headers = {'Content-type': 'application/json', 'Authorization': 'Bearer %s' % api_key} 
            connection = http.client.HTTPSConnection(base_url, context=ssl._create_unverified_context())
            connection.request('GET', query, headers = headers)
            response = connection.getresponse()
            status = response.status
            body = json.loads(response.read().decode())
            connection.close()
            if status == 200:
                page += 1
                for policy in body['policies']:
                    policies.append(policy)
            elif response.status  == 404:
                raise Exception('Error 404, Check that your policy ID is valid')
            elif response.status  == 403:
                raise Exception('Error 403, Check that your API Key is correct')
            else:
                raise Exception(body)
            if len(body['policies']) < 30:
                return policies
    #Work    
    with open('response.json', 'w') as newFile:
        json.dump(get_all_policies(api_key), newFile)

main()