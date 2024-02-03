# utils/GCS/blob.py
from google.cloud.storage.blob import Blob
from dataclasses import dataclass, field, asdict

@dataclass
class Metadata:
    """Class for blob metadata."""
    source_name: str = ""
    source_url: str = ""
    source_parameters: dict = field(default_factory=dict)
    source_api_version: str = ""
    source_datetime: str = ""
    response_code: str = ""
    response_headers: dict = field(default_factory=dict)
    schema: dict = field(default_factory=dict)


class Blob(Blob):
    def __init__(
            self,
            name,
            bucket,
            chunk_size=None,
            encryption_key=None,
            kms_key_name=None,
            generation=None):
        super().__init__(
            name=name, 
            bucket=bucket, 
            chunk_size=chunk_size,
            encryption_key=encryption_key,
            kms_key_name=kms_key_name,
            generation=generation)


    def _set_metadata(self, metadata: Metadata):
        """Set Blob metadata"""

        # Optional: set a metageneration-match precondition to avoid potential race
        # conditions and data corruptions. The request to patch is aborted if the
        # object's metageneration does not match your precondition.
        metageneration_match_precondition = self.metageneration
        self.metadata = asdict(metadata)
        self.patch(if_metageneration_match=metageneration_match_precondition)
    

    def upload_data(self, data, content_type="text/plain", metadata=Metadata()):
        """Upload data to storage bucket"""
        self.upload_from_string(data=data, content_type=content_type)
        self._set_metadata(metadata=metadata)


    def upload_file(self, filename, content_type="text/plain", metadata=Metadata()):
        """Upload data to storage bucket from file"""
        self.upload_from_filename(filename=filename, content_type=content_type)
        self._set_metadata(metadata=metadata)


    def download_data(self):
        """Download data and metadata from storage bucket"""
        data = self.download_as_text()
        return data