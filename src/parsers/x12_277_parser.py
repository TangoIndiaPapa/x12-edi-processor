"""X12 277 Claims Status parser implementation."""

from typing import Any, Dict, List

from ..core.exceptions import X12ParseError
from ..core.logging_config import get_logger
from .base_parser import BaseX12Parser

logger = get_logger(__name__)


class X12_277_Parser(BaseX12Parser):
    """Parser for X12 277 Claims Status (005010X212) transactions."""

    def __init__(self):
        """Initialize 277 parser."""
        super().__init__()
        self.transaction_type = "277"
        self.version = "005010X212"

    def parse(self, x12_content: str) -> Dict[str, Any]:
        """
        Parse X12 277 Claims Status content.

        Args:
            x12_content: Raw X12 277 EDI content

        Returns:
            Parsed 277 data structure

        Raises:
            X12ParseError: If parsing fails
        """
        try:
            logger.info("Parsing X12 277 Claims Status document")

            # Use LinuxForHealth parser
            models = self.parse_with_linuxforhealth(x12_content)

            if not models:
                raise X12ParseError("No valid 277 transactions found")

            # Extract key information
            result = {"transaction_type": "277", "version": self.version, "transactions": []}

            for model in models:
                transaction = self._extract_277_data(model)
                result["transactions"].append(transaction)

            logger.info(f"Successfully parsed {len(models)} 277 transaction(s)")
            return result

        except Exception as e:
            logger.error(f"Error parsing 277: {str(e)}")
            raise X12ParseError(f"Failed to parse 277 document: {str(e)}")

    def _extract_277_data(self, model: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract specific 277 data from parsed model.

        Args:
            model: Parsed X12 model dictionary

        Returns:
            Structured 277 data
        """
        header = model.get("header", {})

        return {
            "control_number": self._safe_get(header, "st_segment.transaction_set_control_number"),
            "information_source": self._extract_information_source(model),
            "information_receiver": self._extract_information_receiver(model),
            "service_providers": self._extract_service_providers(model),
            "claim_status": self._extract_claim_status(model),
            "raw_data": model,
        }

    def _extract_information_source(self, model: Dict[str, Any]) -> Dict[str, str]:
        """Extract information source (payer) details."""
        # Navigate to Loop 2000A (Information Source)
        loop_2000a = model.get("loop_2000a", [])

        # Handle both list and dict structures
        if isinstance(loop_2000a, list) and loop_2000a:
            loop_2000a = loop_2000a[0]

        if isinstance(loop_2000a, dict):
            loop_2100a = loop_2000a.get("loop_2100a", {})
            if isinstance(loop_2100a, list) and loop_2100a:
                loop_2100a = loop_2100a[0]
            nm1_segment = loop_2100a.get("nm1_segment", {}) if isinstance(loop_2100a, dict) else {}
        else:
            nm1_segment = {}

        return {
            "name": nm1_segment.get("name_last_or_organization_name", ""),
            "identifier": nm1_segment.get("identification_code", ""),
            "identifier_type": nm1_segment.get("identification_code_qualifier", ""),
        }

    def _extract_information_receiver(self, model: Dict[str, Any]) -> Dict[str, str]:
        """Extract information receiver (provider) details."""
        loop_2000b = model.get("loop_2000b", [])

        # Handle both list and dict structures
        if isinstance(loop_2000b, list) and loop_2000b:
            loop_2000b = loop_2000b[0]

        if isinstance(loop_2000b, dict):
            loop_2100b = loop_2000b.get("loop_2100b", {})
            if isinstance(loop_2100b, list) and loop_2100b:
                loop_2100b = loop_2100b[0]
            nm1_segment = loop_2100b.get("nm1_segment", {}) if isinstance(loop_2100b, dict) else {}
        else:
            nm1_segment = {}

        return {
            "name": nm1_segment.get("name_last_or_organization_name", ""),
            "identifier": nm1_segment.get("identification_code", ""),
            "identifier_type": nm1_segment.get("identification_code_qualifier", ""),
        }

    def _extract_service_providers(self, model: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract service provider information."""
        providers = []
        loop_2000c = model.get("loop_2000c", [])

        if isinstance(loop_2000c, dict):
            loop_2000c = [loop_2000c]

        for provider in loop_2000c:
            loop_2100c = provider.get("loop_2100c", {})
            if isinstance(loop_2100c, list) and loop_2100c:
                loop_2100c = loop_2100c[0]

            nm1_segment = loop_2100c.get("nm1_segment", {}) if isinstance(loop_2100c, dict) else {}

            providers.append(
                {
                    "name": nm1_segment.get("name_last_or_organization_name", ""),
                    "identifier": nm1_segment.get("identification_code", ""),
                    "claims": self._extract_claims(provider),
                }
            )

        return providers

    def _extract_claims(self, provider_loop: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract claim status information."""
        claims = []
        loop_2200c = provider_loop.get("loop_2200c", [])

        if isinstance(loop_2200c, dict):
            loop_2200c = [loop_2200c]

        for claim in loop_2200c:
            trn_segment = claim.get("loop_2200c", {}).get("trn_segment", {})
            stc_segments = claim.get("stc_segment", [])

            if isinstance(stc_segments, dict):
                stc_segments = [stc_segments]

            claims.append(
                {
                    "claim_identifier": trn_segment.get("trace_number", ""),
                    "status_codes": [
                        {
                            "category": stc.get("health_care_claim_status_category_code", ""),
                            "code": stc.get("status_code", ""),
                            "effective_date": stc.get("status_effective_date", ""),
                        }
                        for stc in stc_segments
                    ],
                }
            )

        return claims

    def _extract_claim_status(self, model: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract overall claim status information."""
        statuses = []
        # Implementation depends on specific 277 structure
        return statuses

    def validate(self, parsed_data: Dict[str, Any]) -> List[str]:
        """
        Validate parsed 277 data.

        Args:
            parsed_data: Parsed 277 data dictionary

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if parsed_data.get("transaction_type") != "277":
            errors.append("Invalid transaction type for 277 parser")

        transactions = parsed_data.get("transactions", [])
        if not transactions:
            errors.append("No transactions found in 277 document")

        for idx, transaction in enumerate(transactions):
            if not transaction.get("control_number"):
                errors.append(f"Transaction {idx}: Missing control number")

            if not transaction.get("information_source", {}).get("name"):
                errors.append(f"Transaction {idx}: Missing information source")

        return errors

    @staticmethod
    def _safe_get(dictionary: Dict, key_path: str, default: Any = "") -> Any:
        """Safely get nested dictionary value using dot notation."""
        keys = key_path.split(".")
        value = dictionary
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key, default)
            else:
                return default
        return value if value is not None else default
