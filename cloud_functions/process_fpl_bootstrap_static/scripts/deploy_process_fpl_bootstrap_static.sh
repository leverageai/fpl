#!/bin/bash

# Set project and function variables
PROJECT_ID="leverageai-sandbox"
REGION="australia-southeast1"
FUNCTION_NAME="process_fpl_bootstrap_static"
ENTRY_POINT="process_fpl_bootstrap_static"
RUNTIME="python311"
MEMORY="128Mi"
TIME_ZONE="utc"
VERBOSITY="warning"

# Set timestamp
TIMESTAMP=$(date +%Y%m%d%H%M%S)

# Set temp dir
TMP_DIR=/tmp/$FUNCTION_NAME$TIMESTAMP/

# Set config file path
CONFIG_FILE_NAME="fpl_bootstrap_static_config.yaml"

(
  # Create temp dir
  echo "Creating temp dir... $TMP_DIR" &&
  mkdir $TMP_DIR &&
  echo "DONE" &&

  # Copy files into temp dir
  echo "Copying files..." &&
  cp ./cloud_functions/$FUNCTION_NAME/main.py $TMP_DIR &&
  cp ./cloud_functions/$FUNCTION_NAME/requirements.txt $TMP_DIR &&
  cp -r ./cloud_functions/utils/ $TMP_DIR &&
  cp ./cloud_functions/$FUNCTION_NAME/config/$CONFIG_FILE_NAME $TMP_DIR &&
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
    --source . \
    --trigger-http \
    --allow-unauthenticated \
    --verbosity $VERBOSITY \
    --quiet &&
  echo "DONE"
)