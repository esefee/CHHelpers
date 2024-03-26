# This script will create and assign a custom price book to a customer. 
# Update the config file with the path to the custom price book you would like to assign 
# and the client api ID of the customer to whom you would like to assign it.
# Optionally set the Billing Account ID field if you would like to assign the price book to a single account family.
# The script will default to assigning the price book to all billing families under the customer.

import json
import http.client
import ssl
import config

#Functions
def delete_custom_price_book(api_key, price_book_id):
    base_url = 'chapi.cloudhealthtech.com'
    query = f'/v1/price_books/{price_book_id}'
    headers = {'Content-type': 'application/json', 'Authorization': f'Bearer {api_key}'} 
    connection = http.client.HTTPSConnection(base_url, context=ssl._create_unverified_context())
    connection.request('DELETE', url=query, headers=headers)
    response = connection.getresponse()
    connection.close()

    if response.status == 204:
        print(f'price book {price_book_id} was deleted.')
        return
    elif response.status  == 403:
        raise Exception('Error 403, Check that your API Key is correct')
    elif response.status  == 404:
        raise Exception('Error 404, Check that your price_book_id is correct')
    else:
        body = json.loads(response.read().decode())
        print(response.status)
        raise Exception(body)

def main():
    #Work
    delete_custom_price_book(config.api_key, config.price_book_id)

if __name__ == '__main__':
    main()