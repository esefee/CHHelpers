# Add CloudHealth Tags from CSV
This script will tags AWS accounts in CloudHealth in order to build a perspective.
There are a number of script parameters which can be set in the config.py including API_key, and some performance parameters for controlling parallel execution. The default value of these performance variables are likely fine but are present should modification be required.
The script expects a CSV input, per the template, with columns for the AWS Owner ID, Tag Key, and Tag Value with rows for each account you would like to tag.
It is possible to modify this script to tag a different asset type. Doing so would require changes to the query in the fetch_ch_asset_id function on line 34, and the asset_type on line 165. Further instruction is outside the scope of this README.
