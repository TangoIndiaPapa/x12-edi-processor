"""Base input handler interface.

Defines the abstract interface for all input sources (local files, S3, uploads).
All input handlers must inherit from BaseInput and implement required methods.

Callees:
    - abc.ABC: Abstract base class functionality

Implementations:
    - src.input.local_input.LocalInput: Local filesystem input
    - src.input.s3_input.S3Input: AWS S3 input
    - src.input.upload_input.UploadInput: HTTP upload input
    - src.input.upload_input.StreamingUploadInput: Streaming upload input

Usage Pattern:
    with InputHandler(source) as handler:
        content = handler.read()
        size = handler.get_size()
"""

from abc import ABC, abstractmethod
from typing import Optional


class BaseInput(ABC):
    """Abstract base class for input sources.

    Provides common functionality and interface contract for all input handlers.
    Subclasses must implement read() and validate_source() methods.

    Supports context manager protocol for resource cleanup.

    Attributes:
        source (str): Input source identifier (path, S3 key, filename)
        _content (Optional[str]): Cached content for size calculations

    Subclasses:
        - LocalInput: Reads from local filesystem
        - S3Input: Reads from AWS S3
        - UploadInput: Processes HTTP uploads
        - StreamingUploadInput: Handles streaming uploads
    """

    def __init__(self, source: str):
        """
        Initialize input handler.

        Args:
            source: Input source identifier (path, S3 key, etc.)
        """
        self.source = source
        self._content: Optional[str] = None

    @abstractmethod
    def read(self) -> str:
        """
        Read content from input source.

        Returns:
            Raw X12 content as string

        Raises:
            InputError: If reading fails
        """
        pass

    @abstractmethod
    def validate_source(self) -> bool:
        """
        Validate that the input source exists and is accessible.

        Returns:
            True if source is valid, False otherwise
        """
        pass

    def get_size(self) -> int:
        """
        Get size of input content in bytes.

        Returns:
            Size in bytes
        """
        if self._content is None:
            self._content = self.read()
        return len(self._content.encode("utf-8"))

    def __enter__(self) -> "BaseInput":
        """Context manager entry.

        Returns:
            BaseInput: Self for use in with statement

        Example:
            >>> with LocalInput("file.x12") as handler:
            ...     content = handler.read()
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit.

        Clears cached content to free memory.

        Args:
            exc_type: Exception type if raised
            exc_val: Exception value if raised
            exc_tb: Exception traceback if raised

        Note:
            Does not suppress exceptions (returns None)
        """
        self._content = None
