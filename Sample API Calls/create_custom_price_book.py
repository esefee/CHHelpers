# This script will create and assign a custom price book to a customer. 
# Update the config file with the path to the custom price book you would like to assign 
# and the client api ID of the customer to whom you would like to assign it.
# Optionally set the Billing Account ID field if you would like to assign the price book to a single account family.
# The script will default to assigning the price book to all billing families under the customer.

import json
import http.client
import ssl
import config
from pprint import pprint

#Functions
def list_custom_price_book(api_key):
    base_url = 'chapi.cloudhealthtech.com'
    query = f'/v1/price_books'
    headers = {'Content-type': 'application/json', 'Authorization': f'Bearer {api_key}'} 
    # Open and read the file contents
    with open(config.price_book_path, 'r') as file:
        file_contents = file.read()
    # Assuming the file content is already in JSON format
    body = file_contents  # If the API expects a JSON string, make sure the file contains valid JSON
    connection = http.client.HTTPSConnection(base_url, context=ssl._create_unverified_context())
    connection.request('POST', query, body, headers)
    response = connection.getresponse()
    body = json.loads(response.read().decode())
    connection.close()
    if response.status == 201:
        return body
    elif response.status  == 403:
        raise Exception('Error 403, Check that your API Key is correct')
    elif response.status  == 422:
        raise Exception('Error 422, Check you are creating the correct Price Book')
    else:
        print(response.status)
        raise Exception(body)

def main():
    #Work
    pprint(list_custom_price_book(config.api_key))

if __name__ == '__main__':
    main()