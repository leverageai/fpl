import yaml
from datetime import datetime
import functions_framework
import logging
import requests
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

# Set variables
source_datetime = datetime.utcnow()
blob_name = f"{output_folder_name}/source_name:{source_name}/source_date:{source_datetime.date().isoformat()}/data001.json"

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

    # Get bucket and blob names from cloud event

    # Process blob data

    # Instantiate output cloud storage bucket and blob
    bucket = Bucket(name=bucket_name)
    blob = Blob(name=blob_name, bucket=bucket)

    # Set metadata for output blob
    metadata = Metadata(
        source_name=source_name,
        source_url=source_url,
        source_datetime=source_datetime.isoformat(),
        response_code=str(response.status_code),
        response_headers=response.headers)

    # Upload data into output blob
    blob.upload_data(data, content_type, metadata)
        
    # Return valid response from Cloud Function
    return STATUS_SUCCESS