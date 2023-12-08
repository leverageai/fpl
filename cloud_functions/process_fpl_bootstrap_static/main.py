import yaml
from datetime import datetime
import functions_framework
import logging
import requests
from typing import Dict
import json
from tempfile import TemporaryFile
from google.cloud import storage

# Setup variables
STATUS_SUCCESS = ('SUCCESS',200)
STATUS_FAILURE = ('FAILURE',500)

# Load configuration variables
with open("fpl_bootstrap_static_config.yaml") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

bucket_name = config["bucket_name"]
source_name = config["source_name"]
source_url = config["source_url"]
source_parameters = config["source_parameters"]
source_api_version = config["source_api_version"]
schema = config["schema"]
output_folder_name = config["output_folder_name"]
trigger_folder = config["trigger_folder"]

@functions_framework.cloud_event
def process_fpl_bootstrap_static(cloud_event):
    """CloudEvent Cloud Function.
    Args:
        cloud_event
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    Note:
        For more information on how Flask integrates with Cloud
        Functions, see the `Writing HTTP functions` page.
        <https://cloud.google.com/functions/docs/writing/http#http_frameworks>
        Access the CloudEvent data payload via cloud_event.data
    """

    # Enforce typing on cloud_event.data
    event_data: Dict = cloud_event.data

    # Extract cloud event id and type
    event_id = cloud_event["id"]
    event_type = cloud_event["type"]

    # Write to logs
    print(f"event_data: {event_data}")
    print(f"event_id: {event_id}")
    print(f"event_type: {event_type}")

    # Return valid response from Cloud Function
    return STATUS_SUCCESS