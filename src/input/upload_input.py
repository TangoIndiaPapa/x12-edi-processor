"""HTTP upload input handler."""

from typing import BinaryIO

from ..core.config import get_settings
from ..core.exceptions import FileSizeError, InputError
from ..core.logging_config import get_logger
from .base_input import BaseInput

logger = get_logger(__name__)


class UploadInput(BaseInput):
    """Input handler for HTTP file uploads."""

    def __init__(self, file_content: bytes, filename: str, encoding: str = "utf-8"):
        """
        Initialize upload input.

        Args:
            file_content: Uploaded file content as bytes
            filename: Original filename
            encoding: Content encoding (default: utf-8)
        """
        super().__init__(filename)
        self.file_content = file_content
        self.filename = filename
        self.encoding = encoding
        self.settings = get_settings()

    def validate_source(self) -> bool:
        """
        Validate uploaded content.

        Returns:
            True if content is valid

        Raises:
            InputError: If validation fails
        """
        if not self.file_content:
            raise InputError("Upload content is empty")

        # Check file size
        file_size = len(self.file_content)
        if file_size > self.settings.max_file_size_bytes:
            raise FileSizeError(
                f"Upload size ({file_size} bytes) exceeds maximum "
                f"({self.settings.max_file_size_bytes} bytes)"
            )

        logger.info(f"Validated upload: {self.filename} ({file_size} bytes)")
        return True

    def read(self) -> str:
        """
        Read content from uploaded file.

        Returns:
            Content as string

        Raises:
            InputError: If reading fails
        """
        try:
            self.validate_source()

            logger.info(f"Reading upload: {self.filename}")
            content = self.file_content.decode(self.encoding)

            logger.info(f"Successfully read {len(content)} characters from upload")
            self._content = content
            return content

        except UnicodeDecodeError as e:
            logger.error(f"Error decoding upload content: {str(e)}")
            raise InputError(f"Failed to decode upload content: {str(e)}")

    def get_metadata(self) -> dict:
        """
        Get upload metadata.

        Returns:
            Dictionary with upload metadata
        """
        return {
            "filename": self.filename,
            "size": len(self.file_content),
            "encoding": self.encoding,
        }

    def save_to_file(self, file_path: str) -> None:
        """
        Save uploaded content to local file.

        Args:
            file_path: Path to save file to

        Raises:
            InputError: If save fails
        """
        try:
            logger.info(f"Saving upload to {file_path}")
            with open(file_path, "wb") as f:
                f.write(self.file_content)
            logger.info(f"Successfully saved upload to {file_path}")
        except (OSError, IOError) as e:
            logger.error(f"Error saving upload: {str(e)}")
            raise InputError(f"Failed to save upload: {str(e)}")


class StreamingUploadInput(BaseInput):
    """Input handler for streaming HTTP file uploads."""

    def __init__(self, file_stream: BinaryIO, filename: str, encoding: str = "utf-8"):
        """
        Initialize streaming upload input.

        Args:
            file_stream: File stream (e.g., from FastAPI UploadFile)
            filename: Original filename
            encoding: Content encoding (default: utf-8)
        """
        super().__init__(filename)
        self.file_stream = file_stream
        self.filename = filename
        self.encoding = encoding
        self.settings = get_settings()

    def validate_source(self) -> bool:
        """
        Validate file stream.

        Returns:
            True if stream is valid
        """
        if self.file_stream is None:
            raise InputError("File stream is None")

        logger.info(f"Validated streaming upload: {self.filename}")
        return True

    def read(self) -> str:
        """
        Read content from file stream.

        Returns:
            Content as string

        Raises:
            InputError: If reading fails
        """
        try:
            self.validate_source()

            logger.info(f"Reading streaming upload: {self.filename}")

            # Read stream content
            content_bytes = self.file_stream.read()

            # Check size
            if len(content_bytes) > self.settings.max_file_size_bytes:
                raise FileSizeError(
                    f"Stream size exceeds maximum ({self.settings.max_file_size_bytes} bytes)"
                )

            content = content_bytes.decode(self.encoding)

            logger.info(f"Successfully read {len(content)} characters from stream")
            self._content = content
            return content

        except UnicodeDecodeError as e:
            logger.error(f"Error decoding stream content: {str(e)}")
            raise InputError(f"Failed to decode stream content: {str(e)}")
        except Exception as e:
            logger.error(f"Error reading stream: {str(e)}")
            raise InputError(f"Failed to read stream: {str(e)}")

    def get_metadata(self) -> dict:
        """
        Get stream metadata.

        Returns:
            Dictionary with stream metadata
        """
        return {"filename": self.filename, "encoding": self.encoding, "type": "streaming"}
