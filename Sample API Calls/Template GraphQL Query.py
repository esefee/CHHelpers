# this is a template for running graphQL queries against CloudHealth. Given an API key, it will generate an access token which is then passed to the graphql_query function. Results are saved in a file in the current working directory as response.json
# the query section, noted below, needs to be completed in order for this function to work.

import json
import http.client
import ssl
import config

api_key = config.api_key

def main():
    #Functions
    #This function takes an API key and returns graphql access and refresh tokens
    def get_tokens(api_key):
        base_url = 'apps.cloudhealthtech.com'
        headers = {'Content-type': 'application/json'} 
        query = """
                mutation Login($apiKey: String!) {
                loginAPI(apiKey: $apiKey) {
                accessToken
                refreshToken
                }
                }
                """
        variables = {"apiKey": api_key}
        connection = http.client.HTTPSConnection(base_url, context=ssl._create_unverified_context())
        body = json.dumps({'query': query, 'variables': variables})
        connection.request('POST', "/graphql", body, headers)
        response = json.loads(connection.getresponse().read().decode())
        connection.close()
        try:
            if response['errors']: 
                print("Generate Access Token: ", response['errors'][0]['message'])
        except KeyError:       
            tokens = response['data']['loginAPI']
            return(tokens)
    
    #Query Tag Management API
    def graphql_query(access_token):
        base_url = 'apps.cloudhealthtech.com'
        headers = {'Content-type': 'application/json'} 
        #Put the query here
        query = """
            
                """
        connection = http.client.HTTPSConnection(base_url, context=ssl._create_unverified_context())
        headers =   {
                        "Content-Type":"application/json",
                        "Authorization": "Bearer " + access_token
                    }
        body = json.dumps({'query': query})
        connection.request('POST', "/graphql", body, headers)
        response = json.loads(connection.getresponse().read().decode())
        connection.close()
        try:
            if response['errors']: 
                print("Query Returned Errors: ", response)
                return "error"            
        except KeyError:
            return response

    #Work
    result = graphql_query(get_tokens(api_key)['accessToken'])
    #The below line will save the result to a json file in your working directory
    #'''
    with open('result.json', 'w') as newFile:
        json.dump(result, newFile)
    #'''
    #if you would prefer to print the result to the console, remove the # from ''' in lines 68 and 71 and uncomment the below line
    #print(result['data'])
main()