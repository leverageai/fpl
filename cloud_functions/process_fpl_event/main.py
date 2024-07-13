import yaml
from datetime import datetime
import functions_framework
from typing import Dict
import json
import pandas as pd
from google.cloud import storage

# Setup variables
STATUS_SUCCESS = ('SUCCESS',200)
STATUS_FAILURE = ('FAILURE',500)

# Load configuration variables
with open("fpl_event_config.yaml") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

bucket_name = config["bucket_name"]
source_name = config["source_name"]
# source_url = config["source_url"]
source_parameters = config["source_parameters"]
source_api_version = config["source_api_version"]
schema = config["schema"]
output_folder_name = config["output_folder_name"]
trigger_folder = config["trigger_folder"]

def extract_stats_data(output_filepath, data):
    elements_df = pd.DataFrame(data['elements'])
    elements_stats_df = pd.concat(
        objs=[
            elements_df['id'],
            pd.json_normalize(elements_df['stats'])],
        axis=1
    )
    elements_stats_cols = ['id', 'minutes', 'goals_scored', 'assists', 'clean_sheets',
       'goals_conceded', 'own_goals', 'penalties_saved', 'penalties_missed',
       'yellow_cards', 'red_cards', 'saves', 'bonus', 'bps', 'influence',
       'creativity', 'threat', 'ict_index', 'starts', 'expected_goals',
       'expected_assists', 'expected_goal_involvements',
       'expected_goals_conceded', 'total_points', 'in_dreamteam']
    elements_stats_df.to_csv(
        output_filepath,
        columns=elements_stats_cols, 
        index=False
    )
    return


def extract_explain_data(output_filepath, data):
    elements_explain_df = pd.json_normalize(data,'elements')
    elements_explain_df = elements_explain_df.apply(lambda x: x.explode())
    elements_explain_df = pd.concat(
        [
            elements_explain_df['id'],
            pd.json_normalize(elements_explain_df['explain'])
        ],
        axis=1
    )
    elements_explain_df = elements_explain_df.apply(lambda x: x.explode()).reset_index(drop=True)
    elements_explain_df = pd.concat(
        [
            elements_explain_df.loc[:,['id','fixture']],
            pd.json_normalize(elements_explain_df['stats'])
        ], axis=1
    )
    elements_explain_cols = ['id', 'fixture', 'identifier', 'points', 'value']
    elements_explain_df.to_csv(
        output_filepath,
        columns=elements_explain_cols, 
        index=False)
    return


def process_blob(event_bucket_name, event_blob_name):
    """Process blob which triggered event"""
    storage_client = storage.Client()

    # Output bucket
    bucket = storage_client.bucket(bucket_name)

    # Event bucket
    event_bucket = storage_client.get_bucket(event_bucket_name)

    # get bucket data as blob
    event_blob = event_bucket.get_blob(event_blob_name)

    # Get source datetime from event blob metadata
    source_datetime = datetime.fromisoformat(event_blob.metadata["source_datetime"])

    # Extract data from event blob
    data = json.loads(event_blob.download_as_string())
    metadata = event_blob.metadata

    stats_blob_name = f"{output_folder_name}/source_name={source_name}/source_date={source_datetime.date().isoformat()}/data=stats/data01.csv"
    explain_blob_name = f"{output_folder_name}/source_name={source_name}/source_date={source_datetime.date().isoformat()}/data=explain/data01.csv"
    
    stats_temp_file_name = f'{datetime.now().strftime("%Y%m%d%H%M%S")}_stats.csv'
    explain_temp_file_name = f'{datetime.now().strftime("%Y%m%d%H%M%S")}_explain.csv'

    # Transform JSON data into CSV
    extract_stats_data(stats_temp_file_name, data)
    extract_explain_data(explain_temp_file_name, data)

    # Upload data into output blob
    # Optional: set a metageneration-match precondition to avoid potential race
    # conditions and data corruptions. The request to patch is aborted if the
    # object's metageneration does not match your precondition.
    stats_blob = bucket.blob(stats_blob_name)
    explain_blob = bucket.blob(explain_blob_name)

    stats_blob.upload_from_filename(filename=stats_temp_file_name, content_type="text/csv")
    explain_blob.upload_from_filename(filename=explain_temp_file_name, content_type="text/csv")

    metageneration_match_precondition = stats_blob.metageneration
    stats_blob.metadata = metadata
    stats_blob.patch(if_metageneration_match=metageneration_match_precondition)

    metageneration_match_precondition = explain_blob.metageneration
    explain_blob.metadata = metadata
    explain_blob.patch(if_metageneration_match=metageneration_match_precondition)

    # Write to logs
    print(f"blob_name: {stats_blob_name}, {explain_blob_name}")
    print(f"bucket_name: {bucket_name}")
    # print(f"fixtures: {fixtures}")


@functions_framework.cloud_event
def process_fpl_event(cloud_event):
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