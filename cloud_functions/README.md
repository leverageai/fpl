# Local deployment
1. Create and activate python virtual environment.
```bash
mkdir .envs/
python -m venv .envs/py-env
source .envs/py-env/bin/activate
```
2. Install python dependencies.
```bash
pip install -r requirements.txt
```
3. Deploy function locally.
```bash
functions-framework --target extract_fpl_fixtures --debug
```
4. (Optional) Simulate a cloud event from another terminal.
```bash
curl -m 610 -X POST localhost:8080 \
-H "Authorization: bearer $(gcloud auth print-identity-token)" \
-H "Content-Type: application/json" \
-H "ce-id: 1234567890" \
-H "ce-specversion: 1.0" \
-H "ce-type: google.cloud.storage.object.v1.finalized" \
-H "ce-time: 2020-08-08T00:11:44.895529672Z" \
-H "ce-source: //storage.googleapis.com/projects/_/buckets/leverageai-sandbox-data" \
-d '{
  "name": "raw/source_name:fpl_api_fixtures/source_date:2024-02-09/data001.json",
  "bucket": "leverageai-sandbox-data",
  "contentType": "application/json",
  "metageneration": "1",
  "timeCreated": "2020-04-23T07:38:57.230Z",
  "updated": "2020-04-23T07:38:57.230Z"
}'
```

# GCP deployment
1. Run deployment script from root directory of github repo.
```bash
./cloud_functions/extract_fpl_fixtures/scripts/deploy.sh
```

# Resources
- [GitHub: functions-framework-python](https://github.com/GoogleCloudPlatform/functions-framework-python)