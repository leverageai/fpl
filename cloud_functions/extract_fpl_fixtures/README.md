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

# GCP deployment
1. Run deployment script from root directory of github repo.
```bash
./cloud_functions/extract_fpl_fixtures/scripts/deploy.sh
```

# Resources
- [GitHub: functions-framework-python](https://github.com/GoogleCloudPlatform/functions-framework-python)