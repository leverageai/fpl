#!/bin/bash

# Set project and function variables
PROJECT_ID="leverageai-sandbox"
REGION="australia-southeast1"
FUNCTION_NAME="extract_fpl_event"
JOB="extract_fpl_event_daily"
SCHEDULE="0 22 * * *"

(
  # Get Cloud Function URI
  echo "Getting cloud function URI" &&
  URI=$(
    gcloud functions describe $FUNCTION_NAME \
      --gen2 \
      --region=$REGION \
      --format="value(serviceConfig.uri)"
  ) &&

  # Delete existing CRON job
  echo "Find and update existing CRON job... $JOB" &&
  (
    (
      (
        gcloud scheduler jobs describe $JOB \
          --location=$REGION \
          --quiet
      ) &&
      (
        # Updating CRON job
        echo "Updating CRON job... $JOB" &&
        gcloud scheduler jobs update http $JOB \
          --location=$REGION \
          --schedule="$SCHEDULE" \
          --uri=$URI \
          --quiet &&
        echo "DONE" 
      ) 
    ) || 
    (
      # Create CRON job
      echo "CRON job not found, creating CRON job... $JOB" &&
      gcloud scheduler jobs create http $JOB \
        --location=$REGION \
        --schedule="$SCHEDULE" \
        --uri=$URI \
        --quiet &&
      echo "DONE" 
    )
  )
)