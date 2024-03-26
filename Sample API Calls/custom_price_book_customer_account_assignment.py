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
def custom_price_book_customer_account_assignment(api_key, price_book_customer_assignment_id):
    base_url = 'chapi.cloudhealthtech.com'
    query = f'/v1/price_book_account_assignments'
    headers = {'Content-type': 'application/json', 'Authorization': f'Bearer {api_key}'} 
    body = json.dumps({"price_book_assignment_id": price_book_customer_assignment_id, "billing_account_owner_id": "ALL"})
    connection = http.client.HTTPSConnection(base_url, context=ssl._create_unverified_context())
    connection.request('POST', query, body, headers)
    response = connection.getresponse()
    body = json.loads(response.read().decode())
    connection.close()
    print()
    print(response.status)
    print()

    if response.status == 200:
        return body
    elif response.status == 201:
        return body
    elif response.status == 204:
        return
    elif response.status  == 403:
        raise Exception('Error 403, Check that your API Key is correct')
    elif response.status  == 404:
        raise Exception('Error 404, Check that your price_book_id is correct')
    else:
        print(response.status)
        raise Exception(body)

def main():
    #Work
    print(custom_price_book_customer_account_assignment(config.api_key, config.price_book_customer_assignment_id))

if __name__ == '__main__':
    main()