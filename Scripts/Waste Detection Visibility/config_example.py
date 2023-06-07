# Update your API key and policy id here and rename this file to config.py in order to run the scripts in this Sample API Calls directory.
# the remainder of these variables can be modified but care must be taken in doing so.
api_key = ""
policy_id = "" # this id can be gotten either from the URL of the policy or via the policies API
client_api_id = 0 # leave zero unless you are a partner running this script on behalf of your customer with an API Key from your partner tenant.
per_page = 100 # this is the number of assets to return at a time. the maximum number this can be set to is 100 for most CHAPI calls
max_workers = 10 # this is the maximum numbe of threads to run in parallel per-policy block branch. note that this script will instantiate one parallel branch per policy block
# Max workers can be increased significantly depending on the resources available to this script, however there is no error handling in place (currently) for when the page number is much greater than the number of actual pages and unhandled errors are returned.
tag_key = "cht_waste_detected" #this is the tag key which will be used for tagging assets
backfill_tags = False #set this variable to True if you would like to tag assets for which the last run policy was not in the current month