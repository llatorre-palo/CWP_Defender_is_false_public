import requests
import json
import csv
import pandas as pd

### Prisma Cloud Professional Services
### Created on November 13, 2023
### Created by llatorre@paloaltonetworks.com
### Version: 2023.12.14.A

"""
This script is used to automatically export all workload instances without a defender installed on CWP:

To use the script, you need to define:
PCAccessKey
PCSecretKey
CSPMApi = # set api based on tenant (api3, api2, api)
CWPurl

serviceType
Possible values: [
	aws-ecr,
	aws-lambda,
	aws-ec2,
	aws-eks,
	aws-ecs,
	aws-s3,
	aws-config,
	aws-cloud-trail,
	aws-kms,
	aws-cloud-watch,
	aws-sns,
	aws-security-hub,
	aws-secrets-manager,
	aws-parameter-store,
	azure-acr,
	azure-functions,
	azure-aks,
	azure-aci,
	azure-vm,
	gcp-gcr,
	gcp-gcf,
	gcp-gke,
	gcp-vm,
	gcp-artifact,
	oci-instance]
"""

### How to create a service account on Prisma Cloud
### https://docs.prismacloud.io/en/classic/cspm-admin-guide/manage-prisma-cloud-administrators/add-service-account-prisma-cloud

### Set-up your Env
### Create and Manage Access Keys --> https://docs.prismacloud.io/en/classic/cspm-admin-guide/manage-prisma-cloud-administrators/create-access-keys
PCAccessKey="<YOUR-ACCESS-KEY>"
PCSecretKey="<YOUR-SECRET-KEY>" 
### Prisma Cloud API URLs --> https://pan.dev/prisma-cloud/api/cspm/api-urls/
### set api based on tenant (api3, api2, api)
CSPMApi = "<YOUR-API-TENANT>" 
CWPurl="<YOUR-CWP-PATH-CONSOLE>" 

### Retrieve a token from the CSPM Login alt text endpoint with your CSPM user credentials
### https://pan.dev/prisma-cloud/api/cwpp/access-api-saas/#accessing-the-api-using-prisma-cloud-login-token

login_url = f"https://{CSPMApi}.prismacloud.io/login"

login_payload = json.dumps({
  "password": PCSecretKey,
  "username": PCAccessKey
})
login_headers = {
  'Content-Type': 'application/json'
}

auth_token = requests.request("POST", login_url, headers=login_headers, data=login_payload)
token = auth_token.json()["token"]

### response = requests.request("POST", login_url, headers=login_headers, data=login_payload)
### print(response.text)

### Use the token to call any Compute API

### Get Discovered Cloud Entities
### https://pan.dev/prisma-cloud/api/cwpp/get-cloud-discovery-entities/

cwp_url = f"https://{CWPurl}/api/v31.02/cloud/discovery/entities?offset=0&serviceType=aws-eks,azure-aks,gcp-gke&defended=false"

cwp_payload = {}
cwp_headers = {
  'x-redlock-auth': token,
  'Content-Type': 'application/json'
}

response = requests.request("GET", cwp_url, headers=cwp_headers, data=cwp_payload)

### For troubleshooting
###print(response.text)
###data = response.json()

### Create a new CSV file
       
responsejson = json.loads(response.text)

with open('Without_defenders.csv', 'w', newline='') as csvfile:
###fieldnames = ['name', 'status', 'defended',  'provider', 'serviceType', 'nodesCount','version','runningTasksCount', 'dvim_aks','lastModified', 'activeServicesCount', 'createdAt', 'resourceGroup', 'accountID', 'region', 'timestamp', 'collections', 'arn', 'endpoints']
    fieldnames = ['name', 'status', 'defended',  'provider', 'serviceType', 'nodesCount','version','runningTasksCount', 'region']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')

    writer.writeheader()
    for row in responsejson:
        writer.writerow(row)

csv_to_pdf = pd.read_csv("Without_defenders.csv")
csv_to_pdf.to_excel("Without_defenders.xlsx", sheet_name="Defender_Is_Required", index=False)
