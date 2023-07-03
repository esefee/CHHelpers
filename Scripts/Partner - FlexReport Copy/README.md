# Partner FlexReport Copy
## Overview  
- Copy one or more FlexReports from MSP tenant to one or more channel customer tenants
- __NOTE__ Only AWS Cost and Usage reports are currently supported.

## Usage
The process to copy one or more FlexReports to one or more Channel Customers is a three step process.  
1. First. Get list of available reports by calling script with --getreports option. Make a note of the Report IDs as you will need them later. 
2. Next. Get list of channel customer tenants by calling script with --getcustomers option.  Make a note of the Customer IDs as you will need them later.
3. Lastly.  Copy report(s) to customer(s) by calling script with --copyreport and providing comma separated list of report ids with --reportids= and a comma separated list of customer ids with the --customerids=  option.

__Example Usage__
python3 flexreport-copy.py --getreports
python3 flexreport-copy.py --getcustomers
python3 flexreport-copy.py --copyreport --reportids=1,2,3 --customerids=a,b,c

 __Note:__ You must edit the config.py file and add the API key from your MSP tenant
 
 ## Example Output
 python3 flexreport-copy.py --copyreport --reportids=b62532a7-6360-4db6-b334-22f21c090198,5ade205e-7477-440a-b7c5-5c5fc453b7bf,448ade4c-af77-435d-8b68-dfccfdac8784 --customerids=42281  
 
Attempting to copy report ID: b62532a7-6360-4db6-b334-22f21c090198 to Channel Customer Tenant ID: 42281  
Success: Report copied into channel customer tenant  
Attempting to copy report ID: 5ade205e-7477-440a-b7c5-5c5fc453b7bf to Channel Customer Tenant ID: 42281  
Success: Report copied into channel customer tenant  
Attempting to copy report ID: 448ade4c-af77-435d-8b68-dfccfdac8784 to Channel Customer Tenant ID: 42281  
Error: A Report already exists with the same name  