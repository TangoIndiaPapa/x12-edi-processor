"""Base parser interface for X12 documents."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from linuxforhealth.x12.io import X12ModelReader


class BaseX12Parser(ABC):
    """Abstract base class for X12 parsers."""

    def __init__(self):
        """Initialize the parser."""
        self.transaction_type: str = ""
        self.version: str = ""

    @abstractmethod
    def parse(self, x12_content: str) -> Dict[str, Any]:
        """
        Parse X12 content into structured data.

        Args:
            x12_content: Raw X12 EDI content as string

        Returns:
            Parsed X12 data as dictionary

        Raises:
            X12ParseError: If parsing fails
        """
        pass

    @abstractmethod
    def validate(self, parsed_data: Dict[str, Any]) -> List[str]:
        """
        Validate parsed X12 data.

        Args:
            parsed_data: Parsed X12 data dictionary

        Returns:
            List of validation error messages (empty if valid)
        """
        pass

    def parse_with_linuxforhealth(self, x12_content: str) -> List[Dict[str, Any]]:
        """
        Parse X12 content using LinuxForHealth library.

        Args:
            x12_content: Raw X12 EDI content

        Returns:
            List of parsed transaction models
        """
        models = []
        with X12ModelReader(x12_content) as reader:
            for model in reader.models():
                models.append(model.dict(exclude_none=True))
        return models

    def get_transaction_info(self, x12_content: str) -> Dict[str, str]:
        """
        Extract transaction type and version from X12 content.

        Args:
            x12_content: Raw X12 EDI content

        Returns:
            Dictionary with transaction_code and version
        """
        # Parse ST segment to get transaction type
        lines = x12_content.split("~")
        for line in lines:
            if line.strip().startswith("ST"):
                elements = line.split("*")
                if len(elements) >= 3:
                    return {
                        "transaction_code": elements[1],
                        "version": elements[3] if len(elements) > 3 else "unknown",
                    }
        return {"transaction_code": "unknown", "version": "unknown"}
