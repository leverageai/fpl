# utils/GCS/bucket.py
from google.cloud.storage import Client
from google.cloud.storage.bucket import Bucket

class Bucket(Bucket):
    def __init__(self, name, user_project=None):
        client = Client()
        super().__init__(client=client, name=name, user_project=user_project)