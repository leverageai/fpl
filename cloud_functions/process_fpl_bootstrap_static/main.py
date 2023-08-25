import yaml
from datetime import datetime
import functions_framework
import logging
import requests
from typing import Dict
import json
from tempfile import TemporaryFile
from utils.GCS.blob import Metadata, Blob
from utils.GCS.bucket import Bucket

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

def process_blob(blob) -> dict:
    """Process blob which triggered event"""

    # Store objects in local variable
    objects = {}

    # Extract data
    data = json.loads(blob.download_as_string())
    
    # Object keys
    object_keys = {
        "events"
        ,"game settings"
        ,"phases"
        ,"teams"
        ,"elements"
        ,"element_stats"
        ,"element_types"
        ,"total players"
    }

    # Extract objects
    objects.update({key: data[key] for key in data.keys() & object_keys})

    return objects

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

    # Instantiate blob which triggered cloud event
    event_bucket = Bucket(name=event_data["bucket"])
    event_blob = Blob(name=event_data["name"], bucket=event_bucket)

    # Get source datetime from event blob metadata
    source_datetime = datetime.fromisoformat(event_blob.metadata["source_datetime"])

    # Process blob
    objects = process_blob(blob=event_blob)

    # Loop through each object in data
    for key, object in objects.items():

        # Upload object to cloud storage
        blob_name = f"{output_folder_name}/source_name={source_name}/object={key}/source_date={source_datetime.date().isoformat()}/data.jsonl"

        # Instantiate output cloud storage objects
        output_bucket = Bucket(name=bucket_name)
        output_blob = Blob(name=blob_name, bucket=output_bucket)

        # Set metadata for output blob
        output_metadata = event_blob.metadata

        # Convert object into JSONL (https://www.kaggle.com/code/nestoranaranjo/convert-json-to-jsonl-with-python-for-bigquery?scriptVersionId=85393799&cellId=9)
        with TemporaryFile('w+b') as jsonl_output:

            # Loop through every element in object and write to temporary JSONL file
            for element in object:
                json.dump(element, jsonl_output)
                jsonl_output.write('\n')

            # Upload data into output blob
            output_blob.upload_file(filename=jsonl_output, content_type="application/jsonl", metadata=output_metadata)
        
    # Return valid response from Cloud Function
    return STATUS_SUCCESS