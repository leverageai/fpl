import yaml
from datetime import datetime
import functions_framework
import logging
import requests
import json
from google.cloud.storage import Client

# Setup variables
STATUS_SUCCESS = ('SUCCESS',200)
STATUS_FAILURE = ('FAILURE',500)

# Load configuration variables
with open("fpl_event_config.yaml") as f:
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

@functions_framework.http
def extract_fpl_event(request):
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

    # loop through all event ids
    event_ids = source_parameters['event_ids']
    
    for event_id in event_ids:
        url = source_url.format(event_id=event_id)
        blob_name = f"{output_folder_name}/source_name:{source_name}/event_id:{event_id}/source_date:{source_datetime.date().isoformat()}/data001.json"
        # Get response from API
        response = requests.get(url=url)
        
        # Raise error if error response code received
        try:
            response.raise_for_status()
        except Exception as e:
            logging.error(f"An error occured getting response from api {url}: {e}")
            return STATUS_FAILURE

        # Extract response content
        source_data = response.text
        source_response_code = response.status_code
        source_content_type = response.headers['content-type'] if 'content-type' in response.headers.keys() else None

        # Check valid response
        try:
            assert(source_response_code==200)
        except AssertionError:
            logging.error(f"Invalid source response code: {source_response_code}")
            return STATUS_FAILURE
        
        try:
            assert(source_content_type=='application/json')
        except AssertionError:
            logging.error(f"Invalid source content type: {source_content_type}")
            return STATUS_FAILURE

        # Instantiate cloud storage objects
        storage_client = Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        # Upload blob and update metadata
        # Optional: set a metageneration-match precondition to avoid potential race
        # conditions and data corruptions. The request to patch is aborted if the
        # object's metageneration does not match your precondition.
        blob.upload_from_string(data=source_data, content_type=source_content_type)
        metageneration_match_precondition = blob.metageneration
        blob.metadata = {
            "source_name": source_name,
            "source_url": url,
            "source_parameters": json.dumps({"event_id": event_id}),
            "source_api_version": "",
            "source_datetime": source_datetime.isoformat(),
            "response_code": str(response.status_code),
            "response_headers": json.dumps(dict(response.headers)),
            "schema": {}
        }
        blob.patch(if_metageneration_match=metageneration_match_precondition)
        
    # Return valid response from Cloud Function
    return STATUS_SUCCESS