import yaml
from datetime import datetime
import functions_framework
import logging
import requests
from typing import Dict
import json
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

def extract_elements_l1(data) -> dict:
    """Extract level 1 elements"""
    elements_l1 = {}
    
    # Level 1 element keys
    element_l1_keys = {
        "events",
        "game settings",
        "phases",
        "teams",
        "elements",
        "element_stats",
        "element_types",
        "total_players"
    }

    # Extract level 1 elements
    elements_l1.update({key: data[key] for key in data.keys() & element_l1_keys})

    return elements_l1


def process_blob(event_bucket_name, event_blob_name):
    """Process blob which triggered event"""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    # get bucket with name
    event_bucket = storage_client.get_bucket(event_bucket_name)

    # get bucket data as blob
    event_blob = event_bucket.get_blob(event_blob_name)

    # Get source datetime from event blob metadata
    source_datetime = datetime.fromisoformat(event_blob.metadata["source_datetime"])

    # Extract data from event blob
    data = json.loads(event_blob.download_as_string())

    # Extract level 1 elements
    elements_l1 = extract_elements_l1(data)

    # Loop through each element in level 1 elements
    for key, element_l1 in elements_l1.items():
        blob_name = f"{output_folder_name}/source_name={source_name}/element={key}/source_date={source_datetime.date().isoformat()}/data.jsonl"
        metadata = event_blob.metadata
        temp_file_name = f'{datetime.now().strftime("%Y%m%d%H%M%S")}.jsonl'

        # Convert elements into JSONL (https://www.kaggle.com/code/nestoranaranjo/convert-json-to-jsonl-with-python-for-bigquery?scriptVersionId=85393799&cellId=9)
        with open(temp_file_name, 'w') as jsonl_output:
            # Loop through every element in object and write to temporary JSONL file
            if type(element_l1) not in (dict, list):
                json.dump(element_l1, jsonl_output)
                jsonl_output.write('\n')
            else:
                for element in element_l1:
                    json.dump(element, jsonl_output)
                    jsonl_output.write('\n')

        # Upload data into output blob
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(filename=temp_file_name, content_type="application/jsonl")
        blob.metadata = metadata
        
        # Write to logs
        print(f"element: {key}")

    # Write to logs
    print(f"blob_name: {blob_name}")
    print(f"bucket_name: {bucket_name}")


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

    # Check if event type is correct
    try:
        assert event_type=="google.cloud.storage.object.v1.finalized"
    except AssertionError:
        # Log error
        return STATUS_FAILURE
    
    # Check object is from trigger folder
    try:
        assert trigger_folder in event_data["name"]
    except AssertionError:
        # Log error
        return STATUS_FAILURE

    # Get blob which triggered cloud event
    event_bucket_name = event_data["bucket"]
    event_blob_name = event_data["name"]

    # Write to logs
    print(f"event_bucket_name: {event_bucket_name}")
    print(f"event_blob_name: {event_blob_name}")

    # Process blob
    process_blob(event_bucket_name=event_bucket_name, event_blob_name=event_blob_name)

    # Return valid response from Cloud Function
    return STATUS_SUCCESS