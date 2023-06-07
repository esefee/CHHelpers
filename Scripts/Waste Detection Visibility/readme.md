# Background
- This is one proposed method for determining how much money is being wasted on underutilized assets across services and tracking progress remediating that waste over time.
- This method utilizes CloudHealth Policies for detecting waste and a function which applies CloudHealth tags to the assets in violation. These tags are native to CloudHealth, do not appear in your cloud provider's portal, and do not require special permissions outside CloudHealth. With tags in place, a perspective can be built to report on identified potential waste and how the total cost of these assets changes over time.

# Solution Overview
- There are 4 parts to this solution:
	- CloudHealth Policy
	- CloudHealth Perspective
	- Python script, which can be run locally or deployed to lambda.
	- CloudHealth Interactive/FlexReports

# Steps
## Create Waste Detection Policy
- Waste detection criteria set per-service, and can be filtered to apply to only select perspective groups. Organizations can build policies to detect waste for many services utilizing performance, configuration, and utilization metrics. [See our policy documentation for more details](https://help.cloudhealthtech.com/policies/).

## Create Waste Detection Perspective
- Script included for creating the Perspective via python.
	- Schema included for reference [See documentation for creating a perspective via API](https://apidocs.cloudhealthtech.com/#perspectives_create-perspective-schema)

## Deploy Waste Detection Tagging Function
These instructions will walk you through deploying the function and scheduler via AWS Cloud Formation. Alternatively, there is a version of the script which can be run locally but deploying and scheduling this is out of scope of this guide.

- If you don't have an S3 bucket to store these files in, create one. Note this bucket name.
- Upload the following files to this bucket:
	- waste-detection-asset-tagger.zip
	- Waste-detection-deployment-CF-Template.json
- Copy the URL to the file "Waste-detection-deployment-CF-Template.json"
- Navigate to CloudFormation and create a new Stack from an existing template. Provide the URL from the previous step.
- The template will ask you for 3 pieces of information:
	- The bucket name/path where you uploaded 'waste-detection-asset-tagger.zip'
	- Your CloudHealth API key which you can get from your account settings page (from the silhouette icon in the upper right of the platform)
	- The Policy ID for the waste detection policy created above. You can get this from the URL of the policy or via our Policy API

## Report on Potential Waste
- Potential waste can be tracked in aggregate via Interactive Reports, like the Multi-Cloud report, and Cost History reports.
	- Filter last full and current month.
	- Filter on waste detection tag for last month
	- compare cost of resources detected as wasteful last month to current month. Optionally, use report options to graph change over time.
- More granular insights can be gained via FlexReports, ex:track cost of per-asset over time.
	- Include line item resource ID, month, perspectives you have like (owner, BU, COGs, etc.) and filter on a group in the detected waste perspective to see more detail about who is responsible, and determine who should validate waste detected and remediate as necessary.