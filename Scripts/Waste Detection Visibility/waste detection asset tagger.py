import datetime
import json
import http.client
import ssl
from pprint import pprint
from concurrent.futures import ThreadPoolExecutor, as_completed
import config


api_key = config.api_key # this key can be gotten from the user account settings page

#Variables
policy_id = config.policy_id # this id can be gotten either from the URL of the policy or via the policies API
client_api_id = config.client_api_id
per_page = config.per_page
max_workers = config.max_workers
tag_key = config.tag_key
backfill_tags = config.backfill_tags
month_year = datetime.datetime.now().strftime("%Y-%m") #variable which looks up the current year and month and returns YYYY-MM

#Functions
def ch_get_rest(api_key, query):
    base_url = 'chapi.cloudhealthtech.com'
    print(query)
    headers = {'Content-type': 'application/json', 'Authorization': f'Bearer {api_key}'} 
    connection = http.client.HTTPSConnection(base_url, context=ssl._create_unverified_context())
    connection.request('GET', query, headers = headers)
    response = connection.getresponse()
    body = json.loads(response.read().decode())
    if response.status == 200:
        return body
    elif response.status  == 404:
        raise Exception('Error 404, Check that your policy ID is valid')
    elif response.status  == 403:
        raise Exception('Error 403, Check that your API Key is correct')
    else:
        raise Exception(body)

def get_policy_blocks(api_key, policy_id):
    query = f'/v1/policies/{policy_id}/policy_blocks/'
    if client_api_id:
        query = query + f'?client_api_id={client_api_id}'
    response = ch_get_rest(api_key, query)
    policy_blocks = []
    for policy_block in response['policy_blocks']:
        policy_blocks.append(policy_block['id'])
    return policy_blocks

def most_recent_violation_lookup(block_id):
    query = f'/v1/policies/{policy_id}/policy_blocks/{block_id}/violations/'
    if client_api_id:
        query = query + f'?client_api_id={client_api_id}'
    response = ch_get_rest(api_key, query)
    try:
        alert_id = response['policy_violations'][0]['alerts'][0]['alert_id']
        tag_value = response['policy_violations'][0]['alerts'][0]['evaluation_time'][:7]
        if backfill_tags == True or tag_value == month_year:
            return {'alert_id': alert_id, 'tag_value': tag_value}
        else:
            return None
    except IndexError or TypeError:
        raise Exception('No violations received by most recent violation lookup function')

def get_assets_in_violation(block_id, violation_id, page):
    base_url = 'chapi.cloudhealthtech.com'
    query = f'/v1/policies/{policy_id}/policy_blocks/{block_id}/violations/{violation_id}?page={page}&per_page={per_page}'
    headers = {'Content-type': 'application/json', 'Authorization': 'Bearer %s' % api_key}
    connection = http.client.HTTPSConnection(base_url, context=ssl._create_unverified_context())
    connection.request('GET', query, headers=headers)
    response = connection.getresponse()
    status = response.status
    body = json.loads(response.read().decode())
    connection.close()

    if status == 200:
        #print(type(body))
        return body
    elif status == 404:
        raise Exception('Error 404, Check that your policy ID is valid')
    elif status == 403:
        raise Exception('Error 403, Check that your API Key is correct')
    else:
        raise Exception(body)

def resource_type_translation_for_tagging(resource_type):
    if resource_type == []:
        raise Exception('No resource type provided to translation function')
    resource_dict={
        'aws_ec2_instance': 'AwsInstance',
        'aws_ec2_image': 'AwsImage',
        'aws_ec2_volume': 'AwsVolume',
        'aws_s3_bucket': 'AwsS3Bucket',
        'aws_ec2_snapshot': 'AwsSnapshot',
        'aws_ec2_reservation': 'AwsInstanceReservation',
        'aws_ec2_reservation_mod': 'AwsInstanceReservationModification',
        'aws_encryption_key': 'AwsKmsCmk',
        'aws_sage_maker_endpoint': 'AwsSageMakerEndpoint',
        'aws_sagemaker_notebook_instance': 'AwsSagemakerNotebookInstance',
        'aws_rds_instance': 'AwsRdsInstance',
        'aws_rds_security_group': 'AwsRdsSecurityGroup',
        'aws_lambda_function': 'AwsLambdaFunction',
        'aws_rds_subnet_group': 'AwsRdsSubnetGroup',
        'aws_rds_snapshot': 'AwsRdsSnapshot',
        'aws_load_balancer': 'AwsLoadBalancer',
        'aws_security_group': 'AwsSecurityGroup',
        'aws_ec2_spot_request': 'AwsSpotRequest',
        'aws_emr_cluster': 'AwsEmrCluster',
        'aws_vpc': 'AwsVpc',
        'aws_vpc_subnet': 'AwsVpcSubnet',
        'aws_cloudtrail_trail': 'AwsCloudtrailTrail',
        'aws_workspace': 'AwsWorkspace',
        'aws_auto_scaling_group': 'AwsAutoScalingGroup',
        'aws_kinesis_firehose': 'AwsKinesisFirehose',
        'aws_kinesis_stream': 'AwsKinesisStream',
        'aws_cache_cluster': 'AwsCacheCluster',
        'aws_elasticache_reserved_node': 'AwsElasticacheReservedNode',
        'aws_cloud_formation_stack': 'AwsCloudFormationStack',
        'aws_elastic_file_system': 'AwsElasticFileSystem',
        'aws_elasticsearch_domain': 'AwsElasticsearchDomain',
        'aws_rds_instance_reservation': 'AwsRdsInstanceReservation',
        'aws_redshift_cluster': 'AwsRedshiftCluster',
        'aws_redshift_reserved_node': 'AwsRedshiftReservedNode',
        'aws_dms_replication_instance': 'AwsDmsReplicationInstance',
        'aws_nat_gateway': 'AwsNatGateway',
        'aws_workspace_bundle': 'AwsWorkspaceBundle',
        'aws_sagemaker_training_job': 'AwsSagemakerTrainingJob',
        'aws_cost_management_savings_plan': 'AwsCostManagementSavingsPlan',
        'aws_elasticsearch_reserved_instance': 'AwsElasticsearchReservedInstance',
        'aws_ec2_application_load_balancer': 'AwsEc2ApplicationLoadBalancer',
        'aws_ec2_network_load_balancer': 'AwsEc2NetworkLoadBalancer',
        'chef_node': 'ChefNode',
        'aws_route53_hosted_zone': 'AwsRoute53HostedZone',
        'dynamo_db_table': 'AwsDynamoDbTable',
        'aws_elastic_ip': 'AwsElasticIp',
        'aws_account': 'AwsAccount',
        'aws_iam_server_certificate': 'AwsIamServerCertificate',
        'aws_iam_group': 'AwsGroup',
        'aws_iam_role': 'AwsIamRole',
        'aws_iam_policy': 'AwsIamPolicy',
        'aws_user': 'AwsUser',
        'azure_vm': 'AzureVm',
        'azure_managed_disk': 'AzureManagedDisk',
        'azure_ip_address': 'AzureIpAddress',
        'azure_resource_group': 'AzureResourceGroup',
        'azure_sql_server_firewall_rules': 'AzureSqlServerFirewallRule',
        'azure_sql_server': 'AzureSqlServer',
        'azure_sql_server_vulnerability_assessment': 'AzureSqlServerVulnerabilityAssessment',
        'azure_active_directory_user': 'AzureActiveDirectoryUser',
        'azure_storage': 'AzureStorage',
        'azure_batch_account': 'AzureBatchAccount',
        'azure_snapshot': 'AzureSnapshot',
        'azure_vm_scale_set': 'AzureVmScaleSet',
        'azure_redis_cache': 'AzureRedisCache',
        'azure_search_service': 'AzureSearchService',
        'azure_sql_database': 'AzureSqlDatabase',
        'azure_sql_warehouse': 'AzureSqlDataWarehouse',
        'azure_hd_insight_cluster': 'AzureHdInsightCluster',
        'azure_log_analytics': 'AzureLogAnalyticsWorkspace',
        'azure_cdn_profile': 'AzureCdnProfile',
        'azure_ex_route': 'AzureExpressRouteCircuit',
        'azure_network_interface': 'AzureNetworkInterface',
        'azure_virtual_network_gateway': 'AzureVirtualNetworkGateway',
        'azure_virtual_network': 'AzureVirtualNetwork',
        'azure_service_bus': 'AzureServiceBusNamespace',
        'azure_recovery_service_vault': 'AzureRecoveryServicesVault',
        'azure_storsimple_dm': 'AzureStorSimpleDeviceManager',
        'azure_app_service_plan': 'AzureAppServicePlan',
        'azure_app_service': 'AzureAppService',
        'azure_document_db': 'AzureDocumentDb',
        'azure_key_vault': 'AzureKeyVault',
        'azure_key_vault_key': 'AzureKeyVaultKey',
        'azure_key_vault_secret': 'AzureKeyVaultSecret',
        'azure_application_gateway': 'AzureApplicationGateway',
        'azure_app_service_environment': 'AzureAppServiceEnvironment',
        'azure_reservation_order': 'AzureReservationOrder',
        'azure_reservation': 'AzureReservation',
        'azure_log_profile': 'AzureLogProfile',
        'azure_subscription': 'AzureSubscription',
        'azure_activity_log_alert': 'AzureActivityLogAlert',
        'azure_kubernetes_service': 'AzureKubernetesService',
        'azure_sql_managed_instance': 'AzureSqlManagedInstance',
        'azure_postgresql_server': 'AzurePostgresqlServer',
        'azure_billing_account': 'AzureBillingAccount',
        'azure_billing_profile': 'AzureBillingProfile',
        'azure_invoice_section': 'AzureInvoiceSection',
        'azure_app_insight': 'AzureAppInsight',
        'azure_enrollment': 'AzureEnrollment',
        'azure_service_principal': 'AzureServicePrincipal',
        'azure_storage_blob_container': 'AzureStorageBlobContainer',
        'azure_active_directory_role_definition': 'AzureActiveDirectoryRoleDefinition',
        'azure_sql_server_auditing': 'AzureSqlServerAuditing',
        'azure_sql_server_threat_detection': 'AzureSqlServerThreatDetection',
        'azure_sql_database_threat_detection': 'AzureSqlDatabaseThreatDetection',
        'azure_sql_database_auditing': 'AzureSqlDatabaseAuditing',
        'azure_subscription_security_policy': 'AzureSubscriptionSecurityPolicy',
        'azure_security_group': 'AzureSecurityGroup',
        'azure_iot_hub': 'AzureIotHub',
        'azure_event_hub_namespace': 'AzureEventHubNamespace',
        'azure_event_hub': 'AzureEventHub',
        'azure_databricks_workspace': 'AzureDatabricksWorkspace',
        'azure_postgresql_server_firewall_rules': 'AzurePostgresqlServerFirewallRule',
        'azure_mysql_servers': 'AzureMysqlServer',
        'gcp_compute_instance': 'GcpComputeInstance',
        'gcp_dataproc_cluster': 'GcpDataprocCluster',
        'gcp_compute_disk': 'GcpComputeDisk',
        'gcp_compute_snapshot': 'GcpComputeSnapshot',
        'gcp_compute_static_ip': 'GcpComputeIP'
    }
    try:
        return resource_dict[resource_type]
    except KeyError:
        return resource_type

def add_cloudhealth_tag(assets, asset_type, tag_value):
    if len(assets) == 0:
        raise Exception('No assets provided to tagging function')

    base_url = 'chapi.cloudhealthtech.com'
    query = '/v1/custom_tags'
    headers = {'Content-type': 'application/json', 'Authorization': f'Bearer {api_key}'}

    data = {"tag_groups": []}
    for asset in assets:
        found = False
        for group in data["tag_groups"]:
            if group["asset_type"] ==  asset_type and group["tags"] == [{"key": tag_key, "value": tag_value}]:
                found = True
                if asset['Asset ID'] not in group["ids"]:
                    group["ids"].append(asset['Asset ID'])
        if not found:
            data["tag_groups"].append({
                "asset_type": asset_type,
                "ids": [asset['Asset ID']],
                "tags": [{"key": tag_key, "value": tag_value}]
            })
    body = json.dumps(data)
    connection = http.client.HTTPSConnection(base_url, context=ssl._create_unverified_context())
    connection.request('POST', url=query, body=body, headers=headers)
    response = json.loads(connection.getresponse().read().decode())
    connection.close()
    return response

def main():
    # This section calls the policy and gets each block
    # each block is then called to get the most recent violation and the associated assets.
    # a dictionary is created for each asset with the relevant information for tagging and added to a list called 'assets_to_tag'
    # this list is then passed to the tagging function which will tag up to 100 assets at a time.
    policy_blocks = get_policy_blocks(api_key, policy_id)
    #spawn a thread for each policy block.
        #spawn a thread for each page of block violations
            # for each page, get assets and tag assets.

    #this is the function that handles the inner loop of threads
    def get_and_tag_assets(block_id, violation_id, tag_value, page):
        assets_in_violation = get_assets_in_violation(block_id, violation_id, page)
        if assets_in_violation == None:
            return None
        #pprint(assets_in_violation)
        resource_type = assets_in_violation['resource_type']
        asset_type = resource_type_translation_for_tagging(resource_type)
        try:
            affected_resources = assets_in_violation['affected_resources']
        except:
            return None
        pprint(add_cloudhealth_tag(affected_resources, asset_type, tag_value))
        return assets_in_violation

    # this is the function that handles the outer loop of threads.
    def policies_in_parallel(block_id):
        last_violation = most_recent_violation_lookup(block_id)
        violation_id = last_violation['alert_id']
        tag_value = last_violation['tag_value']
        page = 1

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            active_branches = max_workers
            while active_branches > 0:
                futures = [executor.submit(get_and_tag_assets, block_id, violation_id, tag_value, page + i) for i in range(max_workers)]
                active_branches = 0

                for future in as_completed(futures):
                    try:
                        response = future.result()
                        #pprint(response)
                        if response is not None:
                            active_branches += 1
                    except Exception as e:
                        print(f"Error from get and tag assets: {e}")

                page += max_workers

    with ThreadPoolExecutor(max_workers) as executor:
            futures = [executor.submit(policies_in_parallel, block_id) for block_id in policy_blocks]

            for future in as_completed(futures):
                try:
                    response = future.result()
                except Exception as e:
                    print(f"Error from policis in parallel: {e}")
main()