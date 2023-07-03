import requests
import config

#    Custom Price Book Report (cpb-report.py)
#
#    v1.0  07.03.34
#     - initial release
#
#    NOTE:  This script is provided without any warranty, express or implied. It should be
#            reviewed carefully in it's entirety and executed at your own risk. 
# 
#    Generate a report of all configured Custom Price Books in an MSP tenant
#  
#
#    Usage:  python3 cpb-report.py 
#
#   Please send feedback/questions to jgoyette@vmware.com

def fetch_books(partnerapikey):
    books = dict()
    page = 1
    while page:
        url = 'https://chapi.cloudhealthtech.com/v1/price_books'
        params={'api_key' : {partnerapikey},
            'page' : {page},
            'per_page' : '100'}
        r = requests.get(url, params)
        book_details = (r.json())
        page += 1
        try:
            if book_details['price_books'] == []:
                break
        except KeyError:
            break
        for book in book_details['price_books']:
            id = book['id']
            books[id] = book
    return books


def fetch_customer_assignments(partnerapikey):
    customer_assignments = dict()
    page = 1
    while page:
        url = 'https://chapi.cloudhealthtech.com/v1/price_book_assignments'
        params={'api_key' : {partnerapikey},
            'page' : {page},
            'per_page' : '100'}
        r = requests.get(url, params)
        assignment_details = (r.json())
        page += 1
        try:
            if assignment_details['price_book_assignments'] == []:
                break
        except KeyError:
            break
        for assignment in assignment_details['price_book_assignments']:
            id = assignment['id']
            customer_assignments[id] = assignment
    return customer_assignments

def fetch_account_assignments(partnerapikey):
    account_assignments = dict()
    page = 1
    while page:
        url = 'https://chapi.cloudhealthtech.com/v1/price_book_account_assignments'
        params={'api_key' : {partnerapikey},
            'page' : {page},
            'per_page' : '100'}
        r = requests.get(url, params)
        assignment_details = (r.json())
        page += 1
        try:
            if assignment_details['price_book_account_assignments'] == []:
                break
        except KeyError:
            break
        for assignment in assignment_details['price_book_account_assignments']:
            id = assignment['id']
            account_assignments[id] = assignment
    return account_assignments

def fetch_book_details(partnerapikey, pricebookid):
        url = 'https://chapi.cloudhealthtech.com/v1/price_books/' + str(pricebookid) + '/specification'
        params={'api_key' : {partnerapikey},
            'per_page' : '100'}
        r = requests.get(url, params)
        pricebook_details = (r.json())
        return pricebook_details

def fetch_customers(partnerapikey):
    customers = dict()
    page = 1
    while page:
        url = 'https://chapi.cloudhealthtech.com/v1/customers'
        params={'api_key' : {partnerapikey},
            'page' : {page},
            'per_page' : '100'}
        r = requests.get(url, params)
        customer_details = (r.json())
        page += 1
        try:
            if customer_details['customers'] == []:
                break
        except KeyError:
            break
        for customer in customer_details['customers']:
            id = customer['id']
            customers[id] = customer
    return customers



if __name__ == '__main__':
    apikey = config.api_key

    books = fetch_books(apikey)
    customer_assignments = fetch_customer_assignments(apikey)
    account_assignments = fetch_account_assignments(apikey)
    customers = fetch_customers(apikey)


    print("Custom Price Book Assignments Configured in the MSP Tenant")
    print("----------------------------------------------------------")


    for account_assignment in account_assignments:
        pricebook_assignment_id = account_assignments[account_assignment]['price_book_assignment_id']
        pricebook_id = customer_assignments[pricebook_assignment_id]['price_book_id']
        pricebook_contents = fetch_book_details(apikey, pricebook_id)
        client_api_id = account_assignments[account_assignment]['target_client_api_id']

    
        print("Assignment ID: " + str(account_assignment))
        try:
            customers[client_api_id]
            print("Channel Customer: " + customers[client_api_id]['name'])
        except KeyError as error:
            print("Customer missing from tenant. Cleanup required.")
            continue
        print("Client API ID: " + str(client_api_id))
        print("Billing Account Owner ID(s): " + account_assignments[account_assignment]['billing_account_owner_id'])
        print("Pricebook ID: " + str(pricebook_id))
        print("Pricebook Name: " + books[pricebook_id]['book_name'])
        print("Pricebook Contents:")
        print(pricebook_contents['specification'])
        print()
        print()
        print()
        print()


# Run main function
# main()
