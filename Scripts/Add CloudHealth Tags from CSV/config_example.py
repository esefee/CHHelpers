# Update your API key here and rename this file to config.py in order to run the scripts in this Scripts directory
api_key = ""
file_path = '/path/to/csv'
max_workers = 10 # this is the maximum numbe of threads to run in parallel per-policy block branch. note that this script will instantiate one parallel branch per policy block
max_retries = 3
batch_size = 100
delay = 1
client_api_id = 0 # change only if you are a partner running this function on behalf of a customer.