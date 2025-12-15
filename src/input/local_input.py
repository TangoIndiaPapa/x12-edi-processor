"""Local filesystem input handler."""

import os
from pathlib import Path

from ..core.config import get_settings
from ..core.exceptions import FileSizeError, InputError
from ..core.logging_config import get_logger
from .base_input import BaseInput

logger = get_logger(__name__)


class LocalInput(BaseInput):
    """Input handler for local filesystem files."""

    def __init__(self, file_path: str, encoding: str = "utf-8"):
        """
        Initialize local file input.

        Args:
            file_path: Path to local X12 file
            encoding: File encoding (default: utf-8)
        """
        super().__init__(file_path)
        self.file_path = Path(file_path)
        self.encoding = encoding
        self.settings = get_settings()

    def validate_source(self) -> bool:
        """
        Validate that file exists and is readable.

        Returns:
            True if file is valid

        Raises:
            InputError: If file doesn't exist or isn't readable
        """
        if not self.file_path.exists():
            raise InputError(f"File not found: {self.file_path}")

        if not self.file_path.is_file():
            raise InputError(f"Path is not a file: {self.file_path}")

        if not os.access(self.file_path, os.R_OK):
            raise InputError(f"File is not readable: {self.file_path}")

        # Check file size
        file_size = self.file_path.stat().st_size
        if file_size > self.settings.max_file_size_bytes:
            raise FileSizeError(
                f"File size ({file_size} bytes) exceeds maximum "
                f"({self.settings.max_file_size_bytes} bytes)"
            )

        logger.info(f"Validated local file: {self.file_path} ({file_size} bytes)")
        return True

    def read(self) -> str:
        """
        Read X12 content from local file.

        Returns:
            File content as string

        Raises:
            InputError: If reading fails
        """
        try:
            self.validate_source()

            logger.info(f"Reading local file: {self.file_path}")
            with open(self.file_path, "r", encoding=self.encoding) as f:
                content = f.read()

            logger.info(f"Successfully read {len(content)} characters from {self.file_path}")
            self._content = content
            return content

        except (OSError, IOError) as e:
            logger.error(f"Error reading file {self.file_path}: {str(e)}")
            raise InputError(f"Failed to read file: {str(e)}")

    def get_metadata(self) -> dict:
        """
        Get file metadata.

        Returns:
            Dictionary with file metadata
        """
        stat = self.file_path.stat()
        return {
            "path": str(self.file_path),
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "encoding": self.encoding,
        }
