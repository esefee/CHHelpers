
import json
import http.client
import ssl
import config

api_key = config.api_key

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

def get_all_aws_accounts_missing_tag(api_key, tag_key):
    tokens = get_tokens(api_key)
    access_token = tokens['accessToken']
    after_cursor = None
    filtered_accounts = []
    while True:
        result = get_aws_accounts_page(access_token, after_cursor)

        # Filter out accounts with the cht_customer tag
        for edge in result['data']['awsAccounts']['edges']:
            tags = edge['node']['tags']
            if all(tag['key'] != tag_key for tag in tags):
                filtered_accounts.append(edge)
        if result['data']['awsAccounts']['pageInfo']['hasNextPage']:
            after_cursor = result['data']['awsAccounts']['pageInfo']['endCursor']
        else:
            break
    return filtered_accounts

def main():
    result = get_all_aws_accounts_missing_tag(api_key, 'CHT_Customer')
    with open('result.json', 'w') as newFile:
        json.dump(result, newFile)

if __name__ == '__main__':
    main()
