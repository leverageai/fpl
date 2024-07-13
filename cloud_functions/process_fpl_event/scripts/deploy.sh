#!/bin/bash

# Set project and function variables
PROJECT_ID="leverageai-sandbox"
REGION="australia-southeast1"
FUNCTION_NAME="process_fpl_event"
ENTRY_POINT="process_fpl_event"
TRIGGER_BUCKET="leverageai-sandbox-data"
RUNTIME="python310"
MEMORY="2Gi"
TIME_ZONE="utc"
MAX_INSTANCES="10"
TIMEOUT="540"

# Set timestamp
TIMESTAMP=$(date +%Y%m%d%H%M%S)

# Set temp dir
TMP_DIR=/tmp/$FUNCTION_NAME$TIMESTAMP/

# Set config file path
CONFIG_FILE_NAME="fpl_event_config.yaml"

(
  # Create temp dir
  echo "Creating temp dir... $TMP_DIR" &&
  mkdir $TMP_DIR &&
  echo "DONE" &&

  # Copy files into temp dir
  echo "Copying files..." &&
  cp ./cloud_functions/$FUNCTION_NAME/main.py $TMP_DIR &&
  cp ./cloud_functions/$FUNCTION_NAME/requirements.txt $TMP_DIR &&
  cp ./cloud_functions/$FUNCTION_NAME/$CONFIG_FILE_NAME $TMP_DIR &&
  echo "DONE" &&

  # Change directory
  cd $TMP_DIR &&

  # Deploy the Cloud Function
  echo "Deploying cloud function... $FUNCTION_NAME" &&
  gcloud functions deploy $FUNCTION_NAME \
    --gen2 \
    --project $PROJECT_ID \
    --region $REGION \
    --entry-point $ENTRY_POINT \
    --runtime $RUNTIME \
    --memory $MEMORY \
    --max-instances $MAX_INSTANCES \
    --timeout $TIMEOUT \
    --source . \
    --trigger-bucket $TRIGGER_BUCKET &&
  echo "DONE"
)