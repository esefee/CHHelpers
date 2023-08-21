# Update your API key here and rename this file to config.py in order to run the scripts in this Sample API Calls directory
api_key = ""
org_id = 0 # leave zero to create the perspective in the TLOU or whichever OU your accaount is in.
max_workers = 10
max_retries = 1
delay = .1
concurrent_tags = 100 # leave at 100 if your total accounts/max_workers is greater than 100. otherwise you may be able to increase performance if you have fewer accounts or increase number of max workers.