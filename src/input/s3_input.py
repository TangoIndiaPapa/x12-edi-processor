"""AWS S3 input handler."""

from typing import Optional
import boto3
from botocore.exceptions import ClientError, BotoCoreError

from ..core.exceptions import InputError, S3Error, FileSizeError
from ..core.config import get_settings
from ..core.logging_config import get_logger
from .base_input import BaseInput

logger = get_logger(__name__)


class S3Input(BaseInput):
    """Input handler for AWS S3 objects."""

    def __init__(self, bucket: str, key: str, region: Optional[str] = None):
        """
        Initialize S3 input.
        
        Args:
            bucket: S3 bucket name
            key: S3 object key
            region: AWS region (uses config if not specified)
        """
        super().__init__(f"s3://{bucket}/{key}")
        self.bucket = bucket
        self.key = key
        self.settings = get_settings()
        self.region = region or self.settings.AWS_REGION
        
        # Initialize S3 client
        self.s3_client = boto3.client('s3', region_name=self.region)

    def validate_source(self) -> bool:
        """
        Validate that S3 object exists and is accessible.
        
        Returns:
            True if object is valid
            
        Raises:
            S3Error: If object doesn't exist or isn't accessible
        """
        try:
            # Get object metadata
            response = self.s3_client.head_object(Bucket=self.bucket, Key=self.key)
            
            # Check file size
            file_size = response['ContentLength']
            if file_size > self.settings.max_file_size_bytes:
                raise FileSizeError(
                    f"S3 object size ({file_size} bytes) exceeds maximum "
                    f"({self.settings.max_file_size_bytes} bytes)"
                )
            
            logger.info(f"Validated S3 object: s3://{self.bucket}/{self.key} ({file_size} bytes)")
            return True
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            if error_code == '404':
                raise S3Error(f"S3 object not found: s3://{self.bucket}/{self.key}")
            elif error_code == '403':
                raise S3Error(f"Access denied to S3 object: s3://{self.bucket}/{self.key}")
            else:
                raise S3Error(f"S3 error ({error_code}): {str(e)}")

    def read(self) -> str:
        """
        Read X12 content from S3 object.
        
        Returns:
            Object content as string
            
        Raises:
            S3Error: If reading fails
        """
        try:
            self.validate_source()
            
            logger.info(f"Reading S3 object: s3://{self.bucket}/{self.key}")
            
            response = self.s3_client.get_object(Bucket=self.bucket, Key=self.key)
            content = response['Body'].read().decode('utf-8')
            
            logger.info(
                f"Successfully read {len(content)} characters from s3://{self.bucket}/{self.key}"
            )
            self._content = content
            return content
            
        except ClientError as e:
            logger.error(f"Error reading S3 object: {str(e)}")
            raise S3Error(f"Failed to read S3 object: {str(e)}")
        except UnicodeDecodeError as e:
            logger.error(f"Error decoding S3 object content: {str(e)}")
            raise InputError(f"Failed to decode S3 object content: {str(e)}")

    def get_metadata(self) -> dict:
        """
        Get S3 object metadata.
        
        Returns:
            Dictionary with object metadata
        """
        try:
            response = self.s3_client.head_object(Bucket=self.bucket, Key=self.key)
            return {
                'bucket': self.bucket,
                'key': self.key,
                'size': response['ContentLength'],
                'last_modified': response['LastModified'].isoformat(),
                'etag': response['ETag'],
                'content_type': response.get('ContentType', 'unknown')
            }
        except ClientError as e:
            logger.error(f"Error getting S3 metadata: {str(e)}")
            return {}

    def copy_to_local(self, local_path: str) -> None:
        """
        Copy S3 object to local file.
        
        Args:
            local_path: Local file path to save to
            
        Raises:
            S3Error: If download fails
        """
        try:
            logger.info(f"Downloading s3://{self.bucket}/{self.key} to {local_path}")
            self.s3_client.download_file(self.bucket, self.key, local_path)
            logger.info(f"Successfully downloaded to {local_path}")
        except ClientError as e:
            logger.error(f"Error downloading S3 object: {str(e)}")
            raise S3Error(f"Failed to download S3 object: {str(e)}")
