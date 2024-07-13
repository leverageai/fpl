#!/bin/bash

# Set project and function variables
PROJECT_ID="leverageai-sandbox"
REGION="australia-southeast1"
FUNCTION_NAME="extract_fpl_event"
ENTRY_POINT="extract_fpl_event"
RUNTIME="python310"
MEMORY="128Mi"
JOB="extract_fpl_event_daily"
SCHEDULE="0 22 * * *"
TIME_ZONE="utc"
VERBOSITY="warning"

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
    --source . \
    --trigger-http \
    --allow-unauthenticated \
    --verbosity $VERBOSITY \
    --quiet &&
  echo "DONE" &&

  # Get Cloud Function URI
  URI=$(
    gcloud functions describe $FUNCTION_NAME \
      --gen2 \
      --region=$REGION \
      --verbosity=$VERBOSITY \
      --format="value(serviceConfig.uri)"
  ) &&

  # Delete existing CRON job
  echo "Find and delete existing CRON job... $JOB" &&
  (
    (
      gcloud scheduler jobs delete $JOB \
        --location=$REGION \
        --verbosity=$VERBOSITY \
        --quiet && 
      echo "DONE"
    ) || 
    (
      (
        gcloud scheduler jobs describe $JOB \
          --location=$REGION \
          --verbosity=$VERBOSITY \
          --quiet && 
        echo "DONE: FOUND NOT DELETED"
      ) || 
      echo "DONE: NOT FOUND"
    )
  ) &&
  
  # Create CRON job
  echo "Creating CRON job... $JOB" &&
  gcloud scheduler jobs create http $JOB \
    --location=$REGION \
    --schedule="$SCHEDULE" \
    --uri=$URI \
    --verbosity=$VERBOSITY \
    --quiet &&
  echo "DONE" 
)