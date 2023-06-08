import json
import http.client
import ssl
import config
from time import sleep


#Variables
api_key = config.api_key

# Functions
def get_tokens(api_key):
    base_url = 'apps.cloudhealthtech.com'
    headers = {'Content-type': 'application/json'} 
    query = """
            mutation Login($apiKey: String!) {
            loginAPI(apiKey: $apiKey) {
            accessToken
            refreshToken
            }
            }
            """
    variables = {"apiKey": api_key}
    connection = http.client.HTTPSConnection(base_url, context=ssl._create_unverified_context())
    body = json.dumps({'query': query, 'variables': variables})
    connection.request('POST', "/graphql", body, headers)
    response = json.loads(connection.getresponse().read().decode())
    connection.close()
    try:
        if response['errors']: 
            raise Exception("get_tokens Returned Errors: ", response)
    except KeyError:
        return response['data']['loginAPI']


# Create FlexReport
def create_savings_flexreport(access_token):
    base_url = 'apps.cloudhealthtech.com'
    headers = {'Content-type': 'application/json'} 
    query = """
        mutation queryReport($reportInput: FlexReportInput!) {
        createFlexReport(input: $reportInput) {
                id
                name
                createdBy
                createdOn
                lastUpdatedOn
                notification {
                    sendUserEmail
                }
                result {
                    status
                    contentType
                    reportUpdatedOn
                    contents {
                        preSignedUrl
                    }
                }
                query {
                    sqlStatement
                    dataGranularity
                    needBackLinkingForTags
                    limit
                    timeRange {
                        last
                        from
                        to
                    }
                }
            }
        }
        """
    variables = { "reportInput": {"name": "Test Savings from RI and SP","notification": {"sendUserEmail": False},
                    "query": {"sqlStatement": "WITH \"cxtemp_spsavings\" AS (SELECT timeInterval_Month AS Month, SUM(lineItem_UnblendedCost) AS SUM_lineItem_UnblendedCost, CONCAT(lineItem_ProductCode, ' SP') AS LineItem_ProductCode, SUM(savingsPlan_SavingsPlanEffectiveCost) AS SavingsPlanEffectiveCost, CAST((SUM(lineItem_UnblendedCost) - SUM(savingsPlan_SavingsPlanEffectiveCost)) AS DECIMAL(18, 2)) AS Savings FROM AWS_CUR WHERE (savingsPlan_SavingsPlanARN IS NOT NULL) AND (lineItem_LineItemDescription NOT LIKE '%SavingsPlanNegation%') GROUP BY timeInterval_Month, lineItem_ProductCode), \"cxtemp_risavings\" AS (SELECT timeInterval_Month AS Month, CAST((SUM(pricing_publicOnDemandCost) - SUM(Reservation_EffectiveCost)) AS DECIMAL(18, 2)) AS Savings, CONCAT(LineItem_ProductCode, ' RI') AS LineItem_ProductCode FROM AWS_CUR WHERE (reservation_ReservationARN IS NOT NULL) GROUP BY timeInterval_Month, LineItem_ProductCode)SELECT cxtemp_spsavings.Month, cxtemp_spsavings.LineItem_ProductCode, cxtemp_spsavings.Savings FROM cxtemp_spsavings Where Savings IS NOT NULL UNION SELECT cxtemp_risavings.Month, cxtemp_risavings.LineItem_ProductCode, cxtemp_risavings.Savings FROM cxtemp_risavings WHERE Savings IS NOT NULL ORDER BY Month ASC",
                    "needBackLinkingForTags": True,
                    "dataGranularity": "MONTHLY",
                    "timeRange": {
                    "last": 12,
                    "excludeCurrent": True
                    },
                    "limit": -1}}}
    connection = http.client.HTTPSConnection(base_url, context=ssl._create_unverified_context())
    headers =   {
                    "Content-Type":"application/json",
                    "Authorization": "Bearer " + access_token
                }
    body = json.dumps({'query': query, 'variables': variables})
    connection.request('POST', "/graphql", body, headers)
    response = json.loads(connection.getresponse().read().decode())
    connection.close()
    try:
        if response['errors']: 
            raise Exception("create_savings_flexreport Returned: ", response)
    except KeyError:
        return response



#List all FlexReports and their data
def get_all_flexreports(access_token):
    base_url = 'apps.cloudhealthtech.com'
    headers = {'Content-type': 'application/json'} 
    query = """
        query queryReport($dataset: String) {
        flexReports(dataset: $dataset) {
            id
                name
                description
                createdBy
                createdOn
                lastUpdatedOn
                notification {
                    sendUserEmail
                }
                result {
                    status
                    contentType
                    reportUpdatedOn
                    contents {
                        preSignedUrl
                    }
                }
                query {
                    sqlStatement
                    dataset
                    dataGranularity
                    needBackLinkingForTags
                    limit
                    timeRange {
                        last
                        from
                        to
                        excludeCurrent
                    }
                }
        }
        }
        """
    connection = http.client.HTTPSConnection(base_url, context=ssl._create_unverified_context())
    headers =   {
                    "Content-Type":"application/json",
                    "Authorization": "Bearer " + access_token
                }
    body = json.dumps({'query': query})
    connection.request('POST', "/graphql", body, headers)
    response = json.loads(connection.getresponse().read().decode())
    connection.close()
    try:
        if response['errors']: 
            raise Exception("get_all_flexreports Returned: ", response)
    except KeyError:
        return response


# Refresh a FlexReport
def execute_flexreport(access_token, flexreport_crn):
    base_url = 'apps.cloudhealthtech.com'
    headers = {'Content-type': 'application/json'} 
    query = """
            mutation executeFlexReport($report_crn: ID!) {
            triggerFlexReportExecution(id:$report_crn)
            }
            """
    variables = { "report_crn": flexreport_crn}
    connection = http.client.HTTPSConnection(base_url, context=ssl._create_unverified_context())
    headers =   {
                    "Content-Type":"application/json",
                    "Authorization": "Bearer " + access_token
                }
    body = json.dumps({'query': query, 'variables': variables})
    connection.request('POST', "/graphql", body, headers)
    response = json.loads(connection.getresponse().read().decode())
    connection.close()
    try:
        if response['errors']: 
            raise Exception("execute_flexreport Returned: ", response)
    except KeyError:
        return response

# Return the report URL for a given FlexReport
def get_flexreport_csv(access_token, flexreport_crn):
    base_url = 'apps.cloudhealthtech.com'
    query = """
            query queryReport($report_crn: ID!) {
                node(id:$report_crn) {
                    id
                    ... on FlexReport {
                            name
                            description
                            createdBy
                            createdOn
                            lastUpdatedOn
                            notification {
                                sendUserEmail
                            }
                        result {
                            status
                            contentType
                            reportUpdatedOn
                            contents {
                                preSignedUrl
                            }
                        }
                        query {
                            sqlStatement
                            dataset
                            dataGranularity
                            needBackLinkingForTags
                            limit
                            timeRange {
                                last
                                from
                                to
                                excludeCurrent
                            }
                        }
                    }
            }
            }
            """
    headers =   {
                    "Content-Type":"application/json",
                    "Authorization": "Bearer " + access_token
                }
    variables = { "report_crn": flexreport_crn}
    body = json.dumps({'query': query, 'variables': variables})
    connection = http.client.HTTPSConnection(base_url, context=ssl._create_unverified_context())
    connection.request('POST', "/graphql", body, headers)
    response = json.loads(connection.getresponse().read().decode())
    connection.close()
    try:
        return response['data']['node']['result']['contents'][0]['preSignedUrl']
    except KeyError:
        return response['errors']    
    except IndexError:
        return response['data']['node']['result']['status']

# Delete a particular FlexReport
def delete_flexreport(access_token, flexreport_crn):
    base_url = 'apps.cloudhealthtech.com'
    query = """
            mutation queryReport($report_crn: ID!) {
            delete(id:$report_crn)
            }
            """
    headers =   {
                    "Content-Type":"application/json",
                    "Authorization": "Bearer " + access_token
                }
    
    variables = { "report_crn": flexreport_crn}
    connection = http.client.HTTPSConnection(base_url, context=ssl._create_unverified_context())
    headers =   {
                    "Content-Type":"application/json",
                    "Authorization": "Bearer " + access_token
                }
    body = json.dumps({'query': query, 'variables': variables})
    connection.request('POST', "/graphql", body, headers)
    response = json.loads(connection.getresponse().read().decode())
    connection.close()
    try:
        if response['errors']: 
            raise Exception("Delete FLexReport Returned Errors: ", response)
    except KeyError:
        return response['data']

# Recursive call of get csv, will return URL when report is ready.
def return_report_when_ready(access_token, flexreport_crn):
    report_csv = get_flexreport_csv(access_token, flexreport_crn)
    if report_csv == 'RUNNING' or report_csv == 'QUEUED':
        sleep(1)
        return return_report_when_ready(access_token, flexreport_crn)
    else:
        return report_csv

# Grab the file at the specified URL, name it, and save it in the current working directory
def fetch_and_rename(url, name_of_file):
    host = url.split("//")[1].split("/")[0]
    path = "/" + "/".join(url.split("//")[1].split("/")[1:])
    connection = http.client.HTTPSConnection(host)
    connection.request("GET", path)
    response = connection.getresponse()
    file_content = response.read()
    connection.close()
    open(name_of_file, 'wb').write(file_content)
    return name_of_file

# These next two lines are if you would like to run through the below for all customers instead of the truncated list 

try:
    access_token = get_tokens(api_key)['accessToken']
except Exception as e:
    print(f"There was an error generating your access token: {e}")
try:
    new_FlexReport = create_savings_flexreport(access_token)
    report_crn = new_FlexReport['data']['createFlexReport']['id']
except Exception as e:
    print(f"There was an error creating your FlexReport: {e}")
print("Waiting for report to complete")
url = return_report_when_ready(access_token, report_crn)
print("report completed, file URL is ", url)
file_name = "RI+SP Savings Report.csv"
print(fetch_and_rename(url, file_name), " saved to current directory")
print(f"Deleting FlexReport {file_name}")
print(delete_flexreport(access_token, report_crn))