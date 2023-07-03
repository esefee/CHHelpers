from os import access
import requests
import json
import argparse
import re
import random
import sys
import config


#    MSP FlexReport Distribution Script (flexreport-copy.py)
#
#    v1.0  11.22.22
#     - initial release
#
#    NOTE:  This script is provided without any warranty, express or implied. It should be
#            reviewed carefully in it's entirety and executed at your own risk. 
# 
#    Copy one or more FlexReports from MSP tenant to one or more channel customer tenants
#
#    - Three stop process:  
#    - 1. Get list of available reports by calling script with --getreports option
#    - 2. Get list of channel customer tenants by calling script with --getcustomers option
#    - 3. Copy report(s) to customer(s) by calling script with --copyreport and providing
#         comma separated list of report ids with --reportids= and a comma separated list of
#         customer ids with the --customerids=  option.
#  
#
#    Usage:  python3 msp-tenant-cleanup.py --apikey APIKEY --getreports
#            python3 msp-tenant-cleanup.py --apikey APIKEY --getcustomers
#            python3 msp-tenant-cleanup.py --apikey APIKEY --copyreport \
#                --reportids=1,2,3 --customerids=a,b,c
#
#   Please send feedback/questions to jgoyette@vmware.com

# Get Access Token
def get_access_token(partnerapikey):
    url = "https://apps.cloudhealthtech.com/graphql"
    tokenpayload = "{\"query\":\"mutation Login {\\n  loginAPI(apiKey: \\\"" + partnerapikey + "\\\") {\\n    accessToken\\n    refreshToken\\n  }\\n}\\n\",\"operationName\":\"Login\"}"
    headers = {"Content-Type": "application/json"}

    response = requests.request("POST", url, data=tokenpayload, headers=headers)
    tokens = response.json()
    access_token = tokens['data']['loginAPI']['accessToken']
    return access_token

# Get Refresh Token
def get_refresh_token(partnerapikey):
    url = "https://apps.cloudhealthtech.com/graphql"
    tokenpayload = "{\"query\":\"mutation Login {\\n  loginAPI(apiKey: \\\"" + partnerapikey + "\\\") {\\n    accessToken\\n    refreshToken\\n  }\\n}\\n\",\"operationName\":\"Login\"}"
    headers = {"Content-Type": "application/json"}

    response = requests.request("POST", url, data=tokenpayload, headers=headers)
    tokens = response.json()
    refresh_token = tokens['data']['loginAPI']['refreshToken']
    return refresh_token


# Get List of Channel Customers
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


# Get List of All FlexReports in the MSP Tenant
def get_flexreports(access_token):
    url = "https://apps.cloudhealthtech.com/graphql"
    flexreports = dict()
    reportspayload = "{\"query\":\"query queryReport {\\n  flexReports {\\n    id\\n        name\\n        description\\n        createdBy\\n        createdOn\\n        lastUpdatedOn\\n        notification {\\n            sendUserEmail\\n        }\\n        result {\\n            status\\n            contentType\\n            reportUpdatedOn\\n            contents {\\n                preSignedUrl\\n            }\\n        }\\n        query {\\n            sqlStatement\\n            dataset\\n            dataGranularity\\n            needBackLinkingForTags\\n            limit\\n            timeRange {\\n                last\\n                from\\n                to\\n                excludeCurrent\\n            }\\n        }\\n  }\\n}\\n\",\"variables\":{\"dataset\":\"x\"},\"operationName\":\"queryReport\"}"
    auth_header = "Bearer " + access_token
    headers = {
        'Content-Type' : 'application/json',
        'Authorization': auth_header
    }
    response = requests.request("POST", url, data=reportspayload, headers=headers)
    for flexreport in response.json()['data']['flexReports']:
                id = flexreport['id']
                flexreports[id] = flexreport

    return flexreports


# Get MSP Tenant ID
# Note:  Not a clean solution but works
def get_partner_tenant_id(access_token):
    url = "https://apps.cloudhealthtech.com/graphql"
    reportspayload = "{\"query\":\"query queryReport {\\n  flexReports {\\n    id\\n  }\\n}\",\"operationName\":\"queryReport\"}"
    auth_header = "Bearer " + access_token
    headers = {
        'Content-Type' : 'application/json',
        'Authorization': auth_header
    }
    response = requests.request("POST", url, data=reportspayload, headers=headers)
    flexreport_id = response.json()['data']['flexReports'][0]
    partner_tenant_id = flexreport_id["id"].split(":")[1]

    return partner_tenant_id

def copy_report(partner_tenant_id, msp_access_token, msp_refresh_token, report_id, client_api_id):
    print("Attempting to copy report ID: " + report_id + " to Channel Customer Tenant ID: " + client_api_id)
    url = "https://apps.cloudhealthtech.com/graphql"

    # Get Channel Tenant Access Token
    payload = "{\"query\":\"mutation getAccessToken {\\n  getAccessToken(input: {\\n    customer: \\\"crn:" + partner_tenant_id + ":msp_client/" + client_api_id + "\\\",\\n    justification: \\\"MSP Delivered FlexReport\\\",\\n    refreshToken: \\\"" + msp_refresh_token + "\\\"\\n  }) {\\n    accessToken\\n    refreshToken\\n  }\\n}  \",\"operationName\":\"getAccessToken\"}"
    auth_header = "Bearer " + msp_access_token
    headers = {
        'Content-Type': "application/json",
        'Authorization': auth_header
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    channel_tenant_tokens = response.json()
    # print(channel_tenant_tokens)
    channel_tenant_access_token = channel_tenant_tokens["data"]["getAccessToken"]["accessToken"]
    # print("channel tenant access token: " + channel_tenant_access_token)

    # Get MSP Source FlexReport Spec
    payload = "{\"query\":\"query queryReport {\\n  node(id: \\\"crn:" + partner_tenant_id + ":flexreports/" + report_id + "\\\") {\\n    id\\n    ... on FlexReport {\\n        name\\n        description\\n        createdBy\\n        createdOn\\n        lastUpdatedOn\\n        notification {\\n            sendUserEmail\\n        }\\n        result {\\n            status\\n            contentType\\n            reportUpdatedOn\\n            contents {\\n                preSignedUrl\\n            }\\n        }\\n        query {\\n            sqlStatement\\n            dataset\\n            dataGranularity\\n            needBackLinkingForTags\\n            limit\\n            timeRange {\\n                last\\n                from\\n                to\\n                excludeCurrent\\n            }\\n        }\\n    }\\n  }\\n}\",\"operationName\":\"queryReport\"}"
    auth_header = "Bearer " + msp_access_token
    headers = {
        "Content-Type": "application/json",
        "Authorization": auth_header
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    json = response.json()
    report_description = str(json["data"]["node"]["description"])
    report_description = report_description.replace('"', '\\\\\\"')
    report_name = str(json["data"]["node"]["name"])
    report_notification = str(json["data"]["node"]["notification"])
    report_notification = report_notification.replace('\'','')
    report_notification = report_notification.replace('True','true')
    report_notification = report_notification.replace('False','false')
    report_query = json["data"]["node"]["query"]
    report_query_datagranularity = str(json["data"]["node"]["query"]["dataGranularity"])
    report_query_limit = str(json["data"]["node"]["query"]["limit"])
    report_query_needbacklinkingfortags = str(json["data"]["node"]["query"]["needBackLinkingForTags"])
    report_query_needbacklinkingfortags = report_query_needbacklinkingfortags.replace('True','true')
    report_query_needbacklinkingfortags = report_query_needbacklinkingfortags.replace('False','false')
    report_query_sqlstatement = json["data"]["node"]["query"]["sqlStatement"]
    report_query_timerange_last = str(json["data"]["node"]["query"]["timeRange"]["last"])
    report_query_timerange_from = str(json["data"]["node"]["query"]["timeRange"]["from"])
    report_query_timerange_to = str(json["data"]["node"]["query"]["timeRange"]["to"])
    report_query_timerange_excludecurrent = str(json["data"]["node"]["query"]["timeRange"]["excludeCurrent"])

    # Build up the query timerange array
    report_query_timerange = ''
    if report_query_timerange_last != 'None':
        report_query_timerange = report_query_timerange + "last: " +  report_query_timerange_last + ","
    if report_query_timerange_from != 'None':
        report_query_timerange = report_query_timerange + "from: \\\"" +  report_query_timerange_from + "\\\","
    if report_query_timerange_to != 'None':
        report_query_timerange = report_query_timerange + "to: \\\"" +  report_query_timerange_to + "\\\","
    if report_query_timerange_excludecurrent != 'None':
        report_query_timerange_excludecurrent = report_query_timerange_excludecurrent.replace("False", "false")
        report_query_timerange_excludecurrent = report_query_timerange_excludecurrent.replace("True", "true")
        report_query_timerange = report_query_timerange + "excludeCurrent: " +  report_query_timerange_excludecurrent + ","


    # Check to see if description text contains any special characters that are going to cause issues
    if ('\'' in report_description) or ('}' in report_description) or ('{' in report_description) or ('\\' in report_description):
        print("Error: Please check the source report description.  Special characters not supported in description")
        sys.exit()

    # Update the sqlStatement parameter
    report_query_sqlstatement = report_query_sqlstatement.replace("\"", "\\\\\\\"")
    report_query_sqlstatement = "\\\"" + report_query_sqlstatement + "\\\""

    # Copy MSP Flex Report into Channel Customer Tenant
    payload = "{\"query\":\"mutation queryReport {\\n  createFlexReport(input: {\\n    \
        name: \\\"" + report_name +  "\\\",\\n    \
        description: \\\"" + report_description + "\\\",\\n" + \
        "notification: " + report_notification + "   ,\
        query: {\\n      \
            sqlStatement:  " + report_query_sqlstatement + ",\\n      \
            needBackLinkingForTags: " + report_query_needbacklinkingfortags + ",\\n      \
            dataGranularity: " + report_query_datagranularity + ",\\n      \
            limit: " + report_query_limit + ",\\n      \
            timeRange: {" + report_query_timerange + "}\
            \\n    }\\n  }\\n    ) {\\n        id\\n    }\\n}\",\"operationName\":\"queryReport\"}"


    auth_header = "Bearer " + channel_tenant_access_token
    headers = {
        "Content-Type": "application/json",
        "Authorization": auth_header
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    
    # Show result of request
    if "errors" in response.json():
        print("Error: ", end='')
        print(response.json()["errors"][0]["message"])
    else:
        print("Success: Report copied into channel customer tenant")
    


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--getreports", help="Get list of reports",
        action="store_true")
    parser.add_argument("--getcustomers", help="Get list of channel customers",
        action="store_true")
    parser.add_argument("--copyreport", help="Copy report into channel customer tenant",
        action="store_true")
    parser.add_argument("--customerids", help="Comma separated list of customer ids from --getcustomers")
    parser.add_argument("--reportids", help="Comma separated list of report ids from --getreports")
    args = parser.parse_args()

    # Extract the API Key from the local config file
    apikey = config.api_key

    access_token = get_access_token(apikey)
    refresh_token = get_refresh_token(apikey)
    partner_tenant_id = get_partner_tenant_id(access_token)

    if args.getreports:
        print("Getting list of FlexReports")
        flexreports = get_flexreports(access_token)
        print("{:<41} {:<10} {:<50}".format('Report ID', 'Dataset', 'Name'))
        print("{:<41} {:<10} {:<50}".format('--------------------------------------', '---------', '---------------------------------------------------------'))
        for key,flexreport in flexreports.items():
            # Only show AWS reports
            if flexreport['query']['dataset'] == 'AWS_CUR':
                uuid = (re.search(r'(\w|-)+$',flexreport['id']).group())
                print("{:<41} {:<10} {:<50}".format(uuid, flexreport['query']['dataset'], flexreport['name']))

    if args.getcustomers:
        print("Getting list of Channel Customers")
        customers = fetch_customers(apikey)
        print("{:<15} {:<50}".format('Customer ID',' Customer Name'))
        print("{:<15} {:<50}".format("-----------","-----------------------------"))
        for key,customer in customers.items():
            print("{:<15} {:<50}".format(str(customer['id']),customer["name"]))
    
    if args.copyreport:
        if (args.reportids and args.customerids):
            reportid_list = args.reportids.replace(' ','')
            reportid_list = reportid_list.split(',')
            customerid_list = args.customerids.replace(' ','')
            customerid_list = customerid_list.split(',')
            for customerid in customerid_list:
                for reportid in reportid_list:
                    copy_report(partner_tenant_id, access_token, refresh_token, reportid, customerid)
        else:
            print("Error:  Copy command requires both customer ID and report ID arguments")



# Run main function
main()