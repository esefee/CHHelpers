
import json
import http.client
import ssl
import config

api_key = config.api_key
partner_id = config.partner_id
customer_id = config.customer_id

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

    if 'errors' in response:
        raise ValueError(f"Generate Access Token: {response['errors'][0]['message']}")
    return response['data']['loginAPI']

def generate_customer_access_token(access_token, refresh_token, partner_id, customer_id):
    base_url = 'apps.cloudhealthtech.com'
    headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + access_token
            }
    query = """
            mutation GetToken($cust:CRN, $refreshToken:String!) {
                getAccessToken(input: {
                    customer: $cust
                    justification: "development work",
                    refreshToken: $refreshToken
            }) {
                accessToken
                refreshToken
        }
    }  
            """
    variables = {"refreshToken": refresh_token,
                "cust": f"crn:{partner_id}:tenant/{customer_id}"}

    connection = http.client.HTTPSConnection(base_url, context=ssl._create_unverified_context())
    body = json.dumps({'query': query, 'variables': variables})
    connection.request('POST', "/graphql", body, headers)
    response = json.loads(connection.getresponse().read().decode())
    connection.close()

    if 'errors' in response:
        raise ValueError(f"Generate Access Token: {response['errors'][0]['message']}")
    customer_access_token = response['data']['getAccessToken']['accessToken']
    return(customer_access_token)    

def get_aws_accounts_page(access_token, after_cursor=None):
    base_url = 'apps.cloudhealthtech.com'

    # Construct the after_clause for GraphQL query
    after_clause = f'after: "{after_cursor}"' if after_cursor else ''

    query = f"""
            {{
                awsAccounts (
                    first: 1000,
                    {after_clause}
                ) {{
                    totalCount
                    edges {{
                        node {{
                            id
                            accountId
                            name
                            ownerId
                            payerAccountId
                            payerAccountName
                            accountType
                            tags {{
                                key
                                value
                            }}
                        }}
                    }},
                    pageInfo {{
                        hasNextPage
                        hasPreviousPage
                        startCursor
                        endCursor
                    }}
                }}
            }}
        """

    headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + access_token
            }
    connection = http.client.HTTPSConnection(base_url, context=ssl._create_unverified_context())
    body = json.dumps({'query': query})
    connection.request('POST', "/graphql", body, headers)
    response = json.loads(connection.getresponse().read().decode())
    connection.close()

    if 'errors' in response:
        raise ValueError(f"Query Returned Errors: {response['errors'][0]['message']}")
    return response

def get_all_aws_accounts(api_key, customer_id=None):
    if customer_id:
        tokens = get_tokens(api_key)
        partner_access_token = tokens['accessToken']
        partner_refresh_token = tokens['refreshToken']
        access_token = generate_customer_access_token(partner_access_token, partner_refresh_token, partner_id, customer_id)
    else:    
        tokens = get_tokens(api_key)
        access_token = tokens['accessToken']
    after_cursor = None
    all_accounts = []
    while True:
        result = get_aws_accounts_page(access_token, after_cursor)
        all_accounts.extend(result['data']['awsAccounts']['edges'])

        if result['data']['awsAccounts']['pageInfo']['hasNextPage']:
            after_cursor = result['data']['awsAccounts']['pageInfo']['endCursor']
        else:
            break
    return all_accounts

def main():
    result = get_all_aws_accounts(api_key, customer_id)
    with open('result.json', 'w') as newFile:
        json.dump(result, newFile)

if __name__ == '__main__':
    main()
