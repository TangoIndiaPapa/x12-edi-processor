"""X12 835 Payment/Remittance parser implementation."""

from typing import Any, Dict, List


from ..core.exceptions import X12ParseError
from ..core.logging_config import get_logger
from .base_parser import BaseX12Parser

logger = get_logger(__name__)


class X12_835_Parser(BaseX12Parser):
    """Parser for X12 835 Payment/Remittance (005010X221A1) transactions."""

    def __init__(self):
        """Initialize 835 parser."""
        super().__init__()
        self.transaction_type = "835"
        self.version = "005010X221A1"

    def parse(self, x12_content: str) -> Dict[str, Any]:
        """
        Parse X12 835 Payment/Remittance content.

        Args:
            x12_content: Raw X12 835 EDI content

        Returns:
            Parsed 835 data structure

        Raises:
            X12ParseError: If parsing fails
        """
        try:
            logger.info("Parsing X12 835 Payment/Remittance document")

            # Use LinuxForHealth parser
            models = self.parse_with_linuxforhealth(x12_content)

            if not models:
                raise X12ParseError("No valid 835 transactions found")

            # Extract key information
            result = {"transaction_type": "835", "version": self.version, "transactions": []}

            for model in models:
                transaction = self._extract_835_data(model)
                result["transactions"].append(transaction)

            logger.info(f"Successfully parsed {len(models)} 835 transaction(s)")
            return result

        except Exception as e:
            logger.error(f"Error parsing 835: {str(e)}")
            raise X12ParseError(f"Failed to parse 835 document: {str(e)}")

    def _extract_835_data(self, model: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract specific 835 data from parsed model.

        Args:
            model: Parsed X12 model dictionary

        Returns:
            Structured 835 data
        """
        header = model.get("header", {})

        return {
            "control_number": self._safe_get(header, "st_segment.transaction_set_control_number"),
            "financial_information": self._extract_financial_info(model),
            "payer": self._extract_payer_info(model),
            "payee": self._extract_payee_info(model),
            "claims": self._extract_claim_payments(model),
            "summary": self._extract_payment_summary(model),
            "raw_data": model,
        }

    def _extract_financial_info(self, model: Dict[str, Any]) -> Dict[str, Any]:
        """Extract financial information from BPR segment."""
        header = model.get("header", {})
        bpr_segment = header.get("bpr_segment", {})

        return {
            "transaction_handling_code": bpr_segment.get("transaction_handling_code", ""),
            "total_actual_provider_payment": bpr_segment.get("monetary_amount", 0.0),
            "credit_debit_flag": bpr_segment.get("credit_debit_flag_code", ""),
            "payment_method": bpr_segment.get("payment_method_code", ""),
            "payment_format": bpr_segment.get("payment_format_code", ""),
            "check_or_eft_number": bpr_segment.get("originating_company_supplemental_code", ""),
            "payment_date": bpr_segment.get("effective_date", ""),
        }

    def _extract_payer_info(self, model: Dict[str, Any]) -> Dict[str, str]:
        """Extract payer identification information."""
        loop_1000a = model.get("loop_1000a", {})
        nm1_segment = loop_1000a.get("nm1_segment", {})

        return {
            "name": nm1_segment.get("name_last_or_organization_name", ""),
            "identifier": nm1_segment.get("identification_code", ""),
            "identifier_type": nm1_segment.get("identification_code_qualifier", ""),
            "address": self._extract_address(loop_1000a),
        }

    def _extract_payee_info(self, model: Dict[str, Any]) -> Dict[str, str]:
        """Extract payee identification information."""
        loop_1000b = model.get("loop_1000b", {})
        nm1_segment = loop_1000b.get("nm1_segment", {})

        return {
            "name": nm1_segment.get("name_last_or_organization_name", ""),
            "identifier": nm1_segment.get("identification_code", ""),
            "identifier_type": nm1_segment.get("identification_code_qualifier", ""),
            "address": self._extract_address(loop_1000b),
        }

    def _extract_address(self, loop: Dict[str, Any]) -> Dict[str, str]:
        """Extract address information from N3 and N4 segments."""
        n3_segment = loop.get("n3_segment", {})
        n4_segment = loop.get("n4_segment", {})

        return {
            "street": n3_segment.get("address_information", ""),
            "city": n4_segment.get("city_name", ""),
            "state": n4_segment.get("state_or_province_code", ""),
            "zip": n4_segment.get("postal_code", ""),
        }

    def _extract_claim_payments(self, model: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract claim payment information."""
        claims = []
        loop_2000 = model.get("loop_2000", [])

        if isinstance(loop_2000, dict):
            loop_2000 = [loop_2000]

        for claim_loop in loop_2000:
            clp_segment = claim_loop.get("clp_segment", {})

            claim_data = {
                "claim_identifier": clp_segment.get("claim_submitters_identifier", ""),
                "status_code": clp_segment.get("claim_status_code", ""),
                "total_charge": clp_segment.get("total_claim_charge_amount", 0.0),
                "payment_amount": clp_segment.get("claim_payment_amount", 0.0),
                "patient_responsibility": clp_segment.get("patient_responsibility_amount", 0.0),
                "payer_claim_control_number": clp_segment.get("payer_claim_control_number", ""),
                "service_lines": self._extract_service_lines(claim_loop),
                "adjustments": self._extract_claim_adjustments(claim_loop),
            }

            claims.append(claim_data)

        return claims

    def _extract_service_lines(self, claim_loop: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract service line details."""
        service_lines = []
        loop_2100 = claim_loop.get("loop_2100", [])

        if isinstance(loop_2100, dict):
            loop_2100 = [loop_2100]

        for service_loop in loop_2100:
            svc_segment = service_loop.get("svc_segment", {})

            service_lines.append(
                {
                    "procedure_code": self._safe_get(
                        svc_segment, "composite_medical_procedure.procedure_code"
                    ),
                    "line_item_charge": svc_segment.get("line_item_charge_amount", 0.0),
                    "line_item_payment": svc_segment.get("line_item_provider_payment_amount", 0.0),
                    "units": svc_segment.get("units_of_service_paid_count", 0.0),
                    "adjustments": self._extract_service_adjustments(service_loop),
                }
            )

        return service_lines

    def _extract_claim_adjustments(self, claim_loop: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract claim level adjustments."""
        adjustments = []
        cas_segments = claim_loop.get("cas_segment", [])

        if isinstance(cas_segments, dict):
            cas_segments = [cas_segments]

        for cas in cas_segments:
            adjustments.append(
                {
                    "group_code": cas.get("claim_adjustment_group_code", ""),
                    "reason_code": cas.get("adjustment_reason_code", ""),
                    "amount": cas.get("monetary_amount", 0.0),
                }
            )

        return adjustments

    def _extract_service_adjustments(self, service_loop: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract service line level adjustments."""
        adjustments = []
        cas_segments = service_loop.get("cas_segment", [])

        if isinstance(cas_segments, dict):
            cas_segments = [cas_segments]

        for cas in cas_segments:
            adjustments.append(
                {
                    "group_code": cas.get("claim_adjustment_group_code", ""),
                    "reason_code": cas.get("adjustment_reason_code", ""),
                    "amount": cas.get("monetary_amount", 0.0),
                }
            )

        return adjustments

    def _extract_payment_summary(self, model: Dict[str, Any]) -> Dict[str, Any]:
        """Extract payment summary totals."""
        footer = model.get("footer", {})

        # Calculate totals from claims
        total_claims = 0
        total_charged = 0.0
        total_paid = 0.0

        claims = self._extract_claim_payments(model)
        for claim in claims:
            total_claims += 1
            total_charged += claim.get("total_charge", 0.0)
            total_paid += claim.get("payment_amount", 0.0)

        return {
            "total_claims": total_claims,
            "total_charged_amount": total_charged,
            "total_paid_amount": total_paid,
            "control_number": self._safe_get(footer, "se_segment.transaction_set_control_number"),
        }

    def validate(self, parsed_data: Dict[str, Any]) -> List[str]:
        """
        Validate parsed 835 data.

        Args:
            parsed_data: Parsed 835 data dictionary

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if parsed_data.get("transaction_type") != "835":
            errors.append("Invalid transaction type for 835 parser")

        transactions = parsed_data.get("transactions", [])
        if not transactions:
            errors.append("No transactions found in 835 document")

        for idx, transaction in enumerate(transactions):
            if not transaction.get("control_number"):
                errors.append(f"Transaction {idx}: Missing control number")

            financial_info = transaction.get("financial_information", {})
            if not financial_info.get("total_actual_provider_payment"):
                errors.append(f"Transaction {idx}: Missing payment amount")

            if not transaction.get("payer", {}).get("name"):
                errors.append(f"Transaction {idx}: Missing payer information")

            if not transaction.get("payee", {}).get("name"):
                errors.append(f"Transaction {idx}: Missing payee information")

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
