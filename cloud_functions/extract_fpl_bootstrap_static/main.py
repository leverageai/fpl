# Imports the Cloud Logging client library
import google.cloud.logging

# Instantiates a client
client = google.cloud.logging.Client()

# Retrieves a Cloud Logging handler based on the environment
# you're running in and integrates the handler with the
# Python logging module. By default this captures all logs
# at INFO level and higher
client.setup_logging()

import yaml
from datetime import datetime
import functions_framework
import logging
from utils.ingest import upload_data_to_gcs_bucket, get_response_from_api

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

@functions_framework.http
def extract_fpl_bootstrap_static(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    Note:
        For more information on how Flask integrates with Cloud
        Functions, see the `Writing HTTP functions` page.
        <https://cloud.google.com/functions/docs/writing/http#http_frameworks>
    """
    # Get response from API
    logging.info("Getting response from API....")
    logging.info(f"URL: {source_url}")
    response = get_response_from_api(source_url)
    source_response_code = response.status_code
    source_content_type = response.headers['content-type'] if 'content-type' in response.headers.keys() else None
    logging.info(f"Response code: {source_response_code}")
    logging.info(f"Content type: {source_content_type}")
    # Check valid response
    if source_response_code==200 and source_content_type=='application/json':
        # Extract data from response
        source_data = response.text
        # Set Blob metadata
        metadata = BlobMetadata(
            source_name=source_name,
            source_url=source_url,
            source_datetime=source_datetime.isoformat(),
            response_code=str(response.status_code),
            response_headers=response.headers)
        # Upload data to Cloud Storage
        logging.info("Uploading data to GCS...")
        logging.info(f"Bucket: {bucket_name}")
        logging.info(f"Blob: {blob_name}")
        logging.info(f"Metadata: {metadata}")
        upload_data_to_gcs_bucket(    
            bucket_name=bucket_name, 
            data=source_data, 
            blob_name=blob_name,
            metadata=metadata)
    # Return valid response from Cloud Function
    return 'OK'