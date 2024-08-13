import yaml
from datetime import datetime, timezone
import functions_framework
from typing import Dict
import json
import pandas as pd
from google.cloud import storage

# Setup variables
STATUS_SUCCESS = ('SUCCESS',200)
STATUS_FAILURE = ('FAILURE',500)

# Load configuration variables
with open("fantasyfootballhub_predictions_config.yaml") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

bucket_name = config["bucket_name"]
source_name = config["source_name"]
# source_url = config["source_url"]
source_parameters = config["source_parameters"]
source_api_version = config["source_api_version"]
schema = config["schema"]
output_folder_name = config["output_folder_name"]
trigger_folder = config["trigger_folder"]

def extract_data(output_filepath, data):
    # Load JSON data into dataframe
    raw_df = pd.DataFrame(data)

    # Format output dataframe
    output_df = pd.concat(
        [
            raw_df.loc[:,['web_name', 'code', 'now_cost', 'status', 'position_id',
        'chance_next_round', 'season_prediction', 'season_prediction_avg',
        'search_term', 'position', 'club', 'range_prediction',
        'range_goals', 'range_assists', 'range_cs', 'range_returns',
        'range_value', 'fpl_id']],
            pd.json_normalize(raw_df['team']).rename(columns={"code_name":"team_code_name","code":"team_code"}),
            pd.json_normalize(raw_df['player']).loc[:,['id','hub_owned','elite_owned','elite_weight']].rename(columns={"id":"player_id","hub_owned":"player_hub_owned","elite_owned":"player_elite_owned","elite_weight":"player_elite_weight"}),
            pd.json_normalize(raw_df['this_gameweek']).loc[:,['xmins','any_cs','any_goal','any_assist','any_return']].rename(columns={"xmins":"this_gameweek_xmins","any_cs":"this_gameweek_any_cs","any_goal":"this_gameweek_any_goal","any_assist":"this_gameweek_any_assist","any_return":"this_gameweek_any_return"})
        ],
        axis=1
    )

    # Load dataframe to CSV
    output_df.to_csv(
        output_filepath,
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

    # get metadata
    event_blob.reload()
    event_blob_metadata = event_blob.metadata
    source_datetime = datetime.now(timezone.utc)
    current_datetime_string = source_datetime.strftime("%Y%m%d%H%M%S")
    
    # Extract data from event blob
    data = json.loads(event_blob.download_as_string())


    blob_name = f"{output_folder_name}/source_name={source_name}/source_date={source_datetime.date().isoformat()}/{current_datetime_string}.csv"
    
    temp_file_name = f'{current_datetime_string}.csv'

    # Transform JSON data into CSV
    extract_data(temp_file_name, data)

    # Upload data into output blob
    # Optional: set a metageneration-match precondition to avoid potential race
    # conditions and data corruptions. The request to patch is aborted if the
    # object's metageneration does not match your precondition.
    blob = bucket.blob(blob_name)

    blob.upload_from_filename(filename=temp_file_name, content_type="text/csv")

    metageneration_match_precondition = blob.metageneration
    blob.metadata = event_blob_metadata
    blob.patch(if_metageneration_match=metageneration_match_precondition)

    # Write to logs
    print(f"blob_name: {blob_name}")
    print(f"bucket_name: {bucket_name}")


@functions_framework.cloud_event
def process_fantasyfootballhub_predictions(cloud_event):
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