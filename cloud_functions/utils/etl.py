# Imports the Cloud Logging client library
import google.cloud.logging

# Instantiates a client
client = google.cloud.logging.Client()

# Retrieves a Cloud Logging handler based on the environment
# you're running in and integrates the handler with the
# Python logging module. By default this captures all logs
# at INFO level and higher
client.setup_logging()

import requests
import json
from datetime import datetime
from google.cloud import storage
from google.cloud.storage.blob import Blob
import logging
from dataclasses import dataclass, field, asdict

@dataclass
class BlobMetadata:
    """Class for blob metadata."""
    source_name: str = ""
    source_url: str = ""
    source_parameters: dict = field(default_factory=dict)
    source_api_version: str = ""
    source_datetime: str = ""
    response_code: str = ""
    response_headers: dict = field(default_factory=dict)
    schema: dict = field(default_factory=dict)

def _set_blob_metadata(bucket_name, blob_name, metadata: BlobMetadata):
    """Set a blob's metadata"""
    # bucket_name = 'your-bucket-name'
    # blob_name = 'your-object-name'
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.get_blob(blob_name)
        metageneration_match_precondition = None

        # Optional: set a metageneration-match precondition to avoid potential race
        # conditions and data corruptions. The request to patch is aborted if the
        # object's metageneration does not match your precondition.
        metageneration_match_precondition = blob.metageneration

        blob.metadata = asdict(metadata)
        blob.patch(if_metageneration_match=metageneration_match_precondition)
    except Exception as e:
        logging.error(f"An error occured updating Blob metadata: {e}")
    else:
        logging.debug(f"Updated metadata to gs://{bucket_name}/{blob_name}")

def get_response_from_api(url):
    """Extract data from API"""
    response = requests.get(url)
    try:
        # Raise error if error response code received
        response.raise_for_status()
    except Exception as e:
        logging.error(f"An error occured getting response from api {url}: {e}")
    else:
        logging.debug(f"Response received from api {url}")
    return response

def upload_data_to_gcs_bucket(bucket_name, data, blob_name, content_type='text/plain', metadata=BlobMetadata()):
    """Uploads data to the bucket"""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"
    # The ID of your GCS object
    # blob_name = "storage-object-name"
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_string(data=data, content_type=content_type)
    except Exception as e:
        logging.error(f"An error occured uploading data to Cloud Storage: {e}")
    else:
        logging.debug(f"File uploaded to gs://{bucket_name}/{blob_name}")
    # Set blob metadata
    _set_blob_metadata(bucket_name, blob_name, metadata)

def _test1():
    bucket_name = "leverageai-sandbox-data"
    source_name = "fpl_api_bootstrap_static"
    source_url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    source_datetime = datetime.utcnow()
    destination_dir_name = f"test/source_name:{source_name}/source_date:{source_datetime.date().isoformat()}/"
    try:
        response = get_response_from_api(source_url)
        source_data = response.text
        destination_blob_name = destination_dir_name + "data001.json"
        metadata = BlobMetadata(
            source_name=source_name,
            source_url=source_url,
            source_datetime=source_datetime.isoformat(),
            response_code=str(response.status_code),
            response_headers=response.headers)
        upload_data_to_gcs_bucket(    
            bucket_name=bucket_name, 
            data=source_data, 
            blob_name=destination_blob_name,
            metadata=metadata)
    except Exception as e:
        print(f"Failed with exception: {e}")
    else:
        print("Success")

if __name__=="__main__":
    print("Running tests...")
    _test1()