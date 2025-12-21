import os
import requests
from requests.auth import HTTPBasicAuth
import yaml
import glob
import logging
import json

# Set up logging for better visibility
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s")
logger = logging.getLogger(__name__)

# Jira credentials and base URL
JIRA_USER_EMAIL = os.getenv("JIRA_USER_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")

# Authenticate using basic auth
auth_credentials = HTTPBasicAuth(JIRA_USER_EMAIL, JIRA_API_TOKEN)
request_headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def load_yaml_filters():
    filters = []
    # Get all YAML files in the filters directory
    for file in glob.glob("jira-filters/*.yml"):
        with open(file, 'r') as f:
            filter_data = yaml.safe_load(f)
            filters.append(filter_data)
            logger.info(f"Loaded filter: {filter_data['name']} from {file}")
    return filters

def validate_filter(filter_data):
    # Basic validation (you can add more checks for JQL syntax or other fields)
    required_fields = ['id', 'name', 'jql']
    for field in required_fields:
        if field not in filter_data:
            logger.error(f"Filter {filter_data['name']} missing required field: {field}")
            return False
    return True

def update_filter(filter_data):
    url = f"{JIRA_BASE_URL}/rest/api/3/filter/{filter_data['id']}"
    payload = json.dumps({
        "name": filter_data["name"],
        "description": filter_data.get("description", ""),
        "jql": filter_data["jql"]
    })
    
    # Make the PUT request to update the filter
    response = requests.put(url, auth=auth_credentials, headers=request_headers, json=payload)
    
    if response.status_code == 200:
        logger.info(f"Successfully updated filter: {filter_data['name']}")
    else:
        logger.error(f"Failed to update filter {filter_data['name']}. Response: {response.status_code} {response.text}")

if __name__ == "__main__":
    filters = load_yaml_filters()
    for filter_data in filters:
        if validate_filter(filter_data):
            update_filter(filter_data)
