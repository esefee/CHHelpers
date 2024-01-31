import http.client
import json
import csv
import ssl
import config
import logging
import time
import math
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set to DEBUG for detailed logging
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class AWSAccounts:
    """
    Represents an AWS account with properties for owner ID, tag key, tag value, and CloudHealth asset ID.
    """
    def __init__(self, owner_id, tag_key, tag_value):
        self.owner_id = owner_id
        self.tag_key = tag_key
        self.tag_value = tag_value
        self.ch_asset_id = None

    def fetch_ch_asset_id(self, api_key, client_api_id=0):
        """
        Fetches the CloudHealth asset ID for the account using the CloudHealth API.
        """
        base_url = 'chapi.cloudhealthtech.com'
        query = f'/api/search.json?api_version=2&name=AwsAccount&query=owner_id=\'{self.owner_id}\'&fields=owner_id'
        if client_api_id:
            query += f'&client_api_id={client_api_id}'
        headers = {'Content-type': 'application/json', 'Authorization': f'Bearer {api_key}'}

        try:
            connection = http.client.HTTPSConnection(base_url, context=ssl.create_default_context())
            logger.debug(f"Requesting CloudHealth API: {query}")
            connection.request('GET', query, headers=headers)
            response = connection.getresponse()

            if response.status == 200:
                response_data = response.read().decode()
                logger.debug(f"Response from CloudHealth API: {response_data}")
                self.ch_asset_id = json.loads(response_data)[0]['id']
            else:
                logger.error(f"HTTP error {response.status}: {response.reason}")
                self.ch_asset_id = None
        except http.client.HTTPException as http_err:
            logger.error(f"HTTP error occurred: {http_err}")
            self.ch_asset_id = None
        except json.JSONDecodeError as json_err:
            logger.error(f"JSON decoding error: {json_err}")
            self.ch_asset_id = None
        finally:
            connection.close()

def read_csv_to_objects(file_path, api_key, client_api_id=0, max_workers=10):
    """
    Reads a CSV file and converts each row into an AWSAccounts object.
    Uses ThreadPoolExecutor with max_workers for parallel processing.
    """
    records = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                logger.debug(f"Processing row: {row}")
                aws_account = AWSAccounts(row['owner_id'], row['tag_key'], row['tag_value'])
                aws_account.fetch_ch_asset_id(api_key, client_api_id)
                records.append(aws_account)
    except FileNotFoundError as fnf_err:
        logger.error(f"File not found error: {fnf_err}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
    return records


def add_cloudhealth_tag(api_key, asset_list):
    if len(asset_list) == 0:
        raise Exception('No assets provided to tagging function')

    base_url = 'chapi.cloudhealthtech.com'
    query = '/v1/custom_tags'
    headers = {'Content-type': 'application/json', 'Authorization': f'Bearer {api_key}'}

    def process_assets(assets, batch_number=None):
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

        last_error = None
        for _ in range(config.max_retries):
            try:
                connection = http.client.HTTPSConnection(base_url, context=ssl._create_unverified_context())
                connection.request('POST', url=query, body=body, headers=headers)
                logger.debug(f"Batch {batch_number}: Request Body: {body}")
                response = connection.getresponse()

                if response.status == 200:
                    raw_response = response.read().decode()
                    if batch_number:
                        logger.debug(f"Batch {batch_number}: Raw API Response: {raw_response}")
                    else:
                        logger.debug(f"Raw API Response: {raw_response}")
                    response_body = json.loads(raw_response)

                    if response_body.get('errors', []) == []:
                        return response_body.get('updates', None)
                    else:
                        last_error = response_body.get('errors', "Unknown error")
                        logger.error(f"Error Response from tagging function: {last_error}")
                else:
                    last_error = f"{response.status}: {response.reason}"
                    logger.error(f"HTTP error in batch {batch_number}: {last_error}")
            except http.client.HTTPException as http_err:
                last_error = str(http_err)
                logger.error(f"HTTP error occurred in batch {batch_number}: {http_err}")
            except json.decoder.JSONDecodeError as json_err:
                last_error = str(json_err)
                logger.error(f"Failed to decode JSON from response in batch {batch_number}. Error: {json_err}")
            finally:
                connection.close()

            time.sleep(config.delay)  # Delay before next retry

        return None

    with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
        futures = []
        for i in range(0, len(asset_list), config.batch_size):
            batch_number = math.ceil((i + 1) / config.batch_size)
            logger.info(f"Tagging batch {batch_number}")
            assets = asset_list[i:i + config.batch_size]
            futures.append(executor.submit(process_assets, assets, batch_number))

        results = []
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                results.append(result)

        return results

# Script execution
try:
    aws_accounts = read_csv_to_objects(config.file_path, config.api_key, config.client_api_id, config.max_workers)
    asset_list = [
        {
            'asset_type': 'AwsAccount',
            'asset_id': account.ch_asset_id,
            'tag_key': account.tag_key,
            'tag_value': account.tag_value
        } for account in aws_accounts if account.ch_asset_id
    ]

    response = add_cloudhealth_tag(config.api_key, asset_list)
    logger.info(f"Tagging response: {response}")
except Exception as e:
    logger.error(f"Script execution error: {e}")
