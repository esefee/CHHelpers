import logging
import http.client

import logging.handlers

# Set up a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create a file handler with log rotation
file_handler = logging.handlers.RotatingFileHandler('script_log.log', maxBytes=5*1024*1024, backupCount=5)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Optionally, create a console handler to print log messages to the console
console_handler = logging.StreamHandler()
console_formatter = logging.Formatter('%(levelname)s: %(message)s')
console_handler.setFormatter(console_formatter)
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

import json
import ssl
import time
import math
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import config

api_key = config.api_key
max_workers = config.max_workers
max_retries = config.max_retries
delay = config.delay
concurrent_tags = 100

class Customer:
    def __init__(self, name, id):
        self.name = name
        self.id = id

class CustomerList:
    def __init__(self, partnerapikey):
        self.customers = []
        self._fetch_customers(partnerapikey)

    def _fetch_customers(self, partnerapikey):
        page = 1
        while page:
            conn = http.client.HTTPSConnection('chapi.cloudhealthtech.com', context=ssl._create_unverified_context())
            url = f'/v2/customers?api_key={partnerapikey}&page={page}&per_page=100'
            conn.request('GET', url)
            response = conn.getresponse()
            customer_details = json.loads(response.read())
            page += 1
            try:
                if customer_details['customers'] == []:
                    break
            except KeyError:
                break
            for customer in customer_details['customers']:
                c = Customer(customer['name'], customer['id'])
                self.customers.append(c)
            conn.close()

    def __len__(self):
        return len(self.customers)

    def __iter__(self):
        return iter(self.customers)

class Account:
    def __init__(self, customer, uniqueAccountID, assetID):
        self.customer = customer
        self.uniqueAccountID = uniqueAccountID
        self.assetID = assetID

class AccountList:
    def __init__(self, partnerapikey, customer_id):
        self.customer_id = customer_id
        self.accounts = []
        self._fetch_accounts(partnerapikey)

    def _fetch_accounts(self, partnerapikey):
        logger.debug(f"Fetching accounts for customer {self.customer_id}...")
        page = 1
        while page:
            conn = http.client.HTTPSConnection('chapi.cloudhealthtech.com', context=ssl._create_unverified_context())
            url = f'/v1/aws_accounts?api_key={partnerapikey}&page={page}&per_page=100'
            if self.customer_id != 'Partner':
                url += f'&client_api_id={self.customer_id}'
            conn.request('GET', url)
            response = conn.getresponse()
            temp_aws_accounts_details = json.loads(response.read())
            page += 1
            try:
                if temp_aws_accounts_details['aws_accounts'] == []:
                    break
            except KeyError:
                break
            for account in temp_aws_accounts_details['aws_accounts']:
                try:
                    uniqueAccountID = account['owner_id']
                except KeyError:
                    logger.error(f"Error processing account {account['id']} for customer {self.customer_id}: missing owner ID")
                    continue
                a = Account(self.customer_id, uniqueAccountID, account['id'])
                self.accounts.append(a)
            conn.close()
        logger.debug(f"Found {len(self.accounts)} accounts for customer {self.customer_id}.")
            
    def __len__(self):
        return len(self.accounts)

    def __iter__(self):
        return iter(self.accounts)

def fetch_customer_account_mapping(partnerapikey, max_threads=5):
    customer_list = CustomerList(partnerapikey)
    mapping = {}
    total_accounts = 0
    customers_with_accounts = 0
    
    # Locks for thread safety
    total_accounts_lock = threading.Lock()
    customers_with_accounts_lock = threading.Lock()
    mapping_lock = threading.Lock()

    def process_customer(customer):
        nonlocal customers_with_accounts, total_accounts
        logger.debug(f"Processing customer {customer.id}: {customer.name})")
        try:
            account_list = AccountList(partnerapikey, customer.id)
        except Exception as e:
            logger.error(f"Error fetching account list for customer {customer.id}: {e}")
            return

        if account_list:
            with customers_with_accounts_lock:
                customers_with_accounts += 1
            with total_accounts_lock:
                total_accounts += len(account_list)

            # Update mapping
            with mapping_lock:
                for account in account_list:
                    mapping[account.uniqueAccountID] = customer.name
    
    # Using ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [executor.submit(process_customer, customer) for customer in customer_list]

        # Handle results as they come in
        for future in as_completed(futures):
            # This is just to catch exceptions (if any) from futures
            try:
                future.result()
            except Exception as e:
                logger.error(f"Error in processing a customer: {e}")
                
    logger.info(f"\nSummary:\nTotal number of accounts: {total_accounts}")
    logger.info(f"Number of customers with accounts: {customers_with_accounts}")
    
    return mapping

def add_cloudhealth_tag(api_key, asset_list):
    if len(asset_list) == 0:
        raise Exception('No assets provided to tagging function')
    
    base_url = 'chapi.cloudhealthtech.com'
    query = '/v1/custom_tags'
    headers = {'Content-type': 'application/json', 'Authorization': f'Bearer {api_key}'}
    def process_assets(assets):
        data = {"tag_groups": []}
        for asset in assets:
            found = False
            for group in data["tag_groups"]:
                if group["asset_type"] == asset['asset_type'] and group["tags"] == [{"key": asset['tag_key'], "value": asset['tag_value']}]:
                    found = True
                    if asset['asset_id'] not in group["ids"]:
                        group["ids"].append(asset['asset_id'])
            if not found:
                data["tag_groups"].append({
                    "asset_type": asset['asset_type'],
                    "ids": [asset['asset_id']], 
                    "tags": [{"key": asset['tag_key'], "value": asset['tag_value']}]
                })
        body = json.dumps(data)

        # Retry mechanism
        last_error = None  # To store the last error message
        for _ in range(max_retries):
            connection = http.client.HTTPSConnection(base_url, context=ssl._create_unverified_context())
            connection.request('POST', url=query, body=body, headers=headers)
            response = connection.getresponse()

            try:
                raw_response = response.read().decode()
                logger.debug(f"Raw API Response: {raw_response}")
                response_body = json.loads(raw_response)
            except json.decoder.JSONDecodeError as e:
                logger.error(f"Failed to decode JSON from response. Error: {e}")
                logger.error(f"Raw Response: {raw_response}")
                response_body = {}
            connection.close()

            if response.status == 200:
                if response_body['errors'] == []:
                    return response_body['updates']
                try:
                    last_error = response_body['errors']
                    logger.error(f"Error Response from tagging function:", last_error)
                except KeyError:
                    last_error = "There was an error with the request."
            else:
                last_error = f"{response.status}: {response.reason}"
            time.sleep(delay)  # Delay before next retry
        return None


    # Using ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for i in range(0, len(asset_list), concurrent_tags):
            # log batch number
            logger.info(f"Tagging batch {math.ceil((i+1)/concurrent_tags)}")
            # Get the next {concurrent_tags} assets from the list
            assets = asset_list[i:i + concurrent_tags]
            futures.append(executor.submit(process_assets, assets))

        results = []
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                results.append(result)
        return results


partner_accounts = AccountList(api_key, 'Partner')

# Create a set to store all partner accounts
partner_accounts_set = {account.uniqueAccountID for account in partner_accounts}

customer_account_lookup_table = fetch_customer_account_mapping(api_key)

accounts_to_tag = []
for account in partner_accounts:
    try:
        asset = {
            "asset_type": "AwsAccount",
            "asset_id": account.assetID,
            "tag_key": "CHT_Customer",
            "tag_value": customer_account_lookup_table[account.uniqueAccountID]
        }
        accounts_to_tag.append(asset)
        # Remove the account from the partner_accounts_set since it's found in the customer_account_lookup_table
        partner_accounts_set.remove(account.uniqueAccountID)
    except KeyError:
        continue

# Tag accounts that aren't present in any customer tenant with "NULL"
for account_id in partner_accounts_set:
    account = next(account for account in partner_accounts if account.uniqueAccountID == account_id)
    asset = {
        "asset_type": "AwsAccount",
        "asset_id": account.assetID,
        "tag_key": "CHT_Customer",
        "tag_value": None
    }
    accounts_to_tag.append(asset)

logger.info(f"Total number of accounts to tag: {len(accounts_to_tag)}. \nTags will be batched in groups of {concurrent_tags} for a total of {math.ceil(len(accounts_to_tag)/concurrent_tags)} batches")

add_cloudhealth_tag(api_key, accounts_to_tag)
