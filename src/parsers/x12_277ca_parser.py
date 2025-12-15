"""X12 277CA Claim Acknowledgment parser implementation.

The 277CA is the "front door" rejection report - it identifies claims that were
rejected BEFORE adjudication due to formatting errors, invalid IDs, etc.

This is CRITICAL for revenue cycle management because rejected claims will NEVER
appear in the 835 remittance. Cross-referencing 277CA rejections with 835 payments
identifies the "black hole" of unsubmitted claims.
"""

from typing import Any, Dict, List

from linuxforhealth.x12.io import X12ModelReader

from ..core.exceptions import X12ParseError, X12ValidationError
from ..core.logging_config import get_logger
from .base_parser import BaseX12Parser

logger = get_logger(__name__)


class X12_277CA_Parser(BaseX12Parser):
    """
    Parser for X12 277CA Claim Acknowledgment (005010X214) transactions.
    
    The 277CA is distinct from 277CS (Claim Status):
    - 277CA: Pre-adjudication acknowledgment/rejection (formatting errors)
    - 277CS: Post-submission status response (claims in process)
    
    Key Status Codes:
    - Category A7: Rejected at gateway (most critical for revenue tracking)
    - Category A1: Accepted for processing
    - Category A6: Rejected - resubmission allowed
    """

    def __init__(self):
        """Initialize 277CA parser."""
        super().__init__()
        self.transaction_type = "277CA"
        self.version = "005010X214"

    def parse(self, x12_content: str) -> Dict[str, Any]:
        """
        Parse X12 277CA Claim Acknowledgment content.
        
        Note: LinuxForHealth library doesn't support 005010X214 (277CA), so we use
        manual segment parsing. The 277CA structure is simpler than 277CS since
        it's pre-adjudication acknowledgment.
        
        Args:
            x12_content: Raw X12 277CA EDI content
            
        Returns:
            Parsed 277CA data structure with rejection/acceptance status
            
        Raises:
            X12ParseError: If parsing fails
        """
        try:
            logger.info("Parsing X12 277CA Claim Acknowledgment document (manual parsing)")
            
            # Manual segment parsing for 277CA
            # LinuxForHealth doesn't support 005010X214, so we parse segments directly
            segments = self._parse_segments(x12_content)
            
            # Extract key information
            result = {
                "transaction_type": "277CA",
                "version": self.version,
                "acknowledgments": [],
                "rejections": [],
                "acceptances": []
            }
            
            # Process segments hierarchically
            current_transaction = None
            
            for segment in segments:
                segment_id = segment["id"]
                elements = segment["elements"]
                
                # HL segments define hierarchy - Level 22 (Information Source Detail) = individual claim
                if segment_id == "HL" and len(elements) >= 3:
                    # Elements: [HL_ID, Parent_HL_ID, Level_Code, Hier_Child_Code]
                    level_code = elements[2]
                    
                    if level_code == "22":  # Information Source Detail = Claim level
                        # Save previous transaction
                        if current_transaction and current_transaction.get("trace_number"):
                            result["acknowledgments"].append(current_transaction)
                        # Start new transaction
                        current_transaction = self._init_transaction()
                
                # Process segment data into current transaction
                if current_transaction:
                    if segment_id == "NM1":
                        self._process_nm1(segment, current_transaction)
                    elif segment_id == "TRN":
                        self._process_trn(segment, current_transaction)
                    elif segment_id == "STC":
                        self._process_stc(segment, current_transaction)
                    elif segment_id == "REF":
                        self._process_ref(segment, current_transaction)
                    elif segment_id == "DTP":
                        self._process_dtp(segment, current_transaction)
                    elif segment_id == "MSG":
                        self._process_msg(segment, current_transaction)
            
            # Add last transaction
            if current_transaction and current_transaction.get("trace_number"):
                result["acknowledgments"].append(current_transaction)
            
            # Categorize by status for easy revenue tracking
            for ack in result["acknowledgments"]:
                if ack.get("status_category") == "A7":  # Rejected
                    result["rejections"].append(ack)
                elif ack.get("status_category") == "A1":  # Accepted
                    result["acceptances"].append(ack)
            
            # Add summary statistics for monitoring
            result["summary"] = {
                "total_claims": len(result["acknowledgments"]),
                "rejected_count": len(result["rejections"]),
                "accepted_count": len(result["acceptances"]),
                "rejection_rate": (
                    len(result["rejections"]) / len(result["acknowledgments"]) * 100
                    if result["acknowledgments"] else 0
                )
            }
            
            logger.info(
                f"Parsed 277CA with {result['summary']['total_claims']} claims, "
                f"{result['summary']['rejected_count']} rejections"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse 277CA: {str(e)}")
            raise X12ParseError(f"277CA parsing failed: {str(e)}") from e

    def _extract_transaction_data(self, model: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract relevant data from a 277CA transaction model.
        
        Focus on data needed for cross-referencing with 835:
        - Patient identifier
        - Date of service
        - Total billed amount
        - Rejection reason
        
        Args:
            model: Parsed X12 model from LinuxForHealth
            
        Returns:
            Structured transaction data
        """
        transaction = {
            "claim_id": None,
            "patient_id": None,
            "patient_name": None,
            "date_of_service": None,
            "billed_amount": None,
            "status_category": None,
            "status_code": None,
            "rejection_reason": None,
            "provider_npi": None,
            "payer_claim_control_number": None
        }
        
        # Extract hierarchical level data
        for segment in model.get("segments", []):
            segment_id = segment.get("id", "")
            
            # BHT - Beginning of Hierarchical Transaction
            if segment_id == "BHT":
                transaction["transaction_date"] = segment.get("date")
            
            # NM1 - Name segments for Patient (IL), Provider (1P), Payer (PR)
            elif segment_id == "NM1":
                entity_type = segment.get("entity_identifier_code")
                if entity_type == "IL":  # Insured/Patient
                    transaction["patient_name"] = self._format_name(segment)
                    transaction["patient_id"] = segment.get("identification_code")
                elif entity_type == "1P":  # Provider
                    transaction["provider_name"] = segment.get("name")
                    transaction["provider_npi"] = segment.get("identification_code")
                elif entity_type == "PR":  # Payer
                    transaction["payer_name"] = segment.get("name")
            
            # TRN - Trace Number (critical for matching)
            elif segment_id == "TRN":
                transaction["trace_number"] = segment.get("trace_number")
            
            # STC - Status Information (THE MOST CRITICAL SEGMENT)
            elif segment_id == "STC":
                # Status Category Code (A1=Accepted, A7=Rejected, etc.)
                status_info = segment.get("status_information", {})
                transaction["status_category"] = status_info.get("category_code")
                transaction["status_code"] = status_info.get("status_code")
                transaction["rejection_reason"] = status_info.get("status_reason")
                
                # Financial amounts if provided
                transaction["billed_amount"] = segment.get("total_claim_charge_amount")
            
            # REF - Reference Identification
            elif segment_id == "REF":
                ref_qualifier = segment.get("reference_identification_qualifier")
                ref_value = segment.get("reference_identification")
                
                if ref_qualifier == "1K":  # Payer Claim Control Number
                    transaction["payer_claim_control_number"] = ref_value
                elif ref_qualifier == "D9":  # Patient Account Number
                    transaction["claim_id"] = ref_value
            
            # DTP - Date/Time Period (Date of Service)
            elif segment_id == "DTP":
                date_qualifier = segment.get("date_time_qualifier")
                if date_qualifier == "472":  # Service Period
                    transaction["date_of_service"] = segment.get("date_time_period")
        
        return transaction

    def _parse_segments(self, x12_content: str) -> List[Dict[str, Any]]:
        """
        Parse X12 content into segments.
        
        Args:
            x12_content: Raw X12 content
            
        Returns:
            List of segment dictionaries
        """
        segments = []
        lines = x12_content.replace('\n', '').split('~')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            elements = line.split('*')
            if elements:
                segments.append({
                    "id": elements[0],
                    "elements": elements[1:] if len(elements) > 1 else []
                })
        
        return segments

    def _init_transaction(self) -> Dict[str, Any]:
        """Initialize empty transaction dictionary."""
        return {
            "claim_id": None,
            "patient_id": None,
            "patient_name": None,
            "date_of_service": None,
            "billed_amount": None,
            "status_category": None,
            "status_code": None,
            "rejection_reason": None,
            "provider_npi": None,
            "payer_claim_control_number": None,
            "trace_number": None
        }

    def _process_nm1(self, segment: Dict[str, Any], transaction: Dict[str, Any]) -> None:
        """Process NM1 (Name) segment."""
        elements = segment["elements"]
        if len(elements) < 2:
            return
        
        entity_code = elements[0]  # Entity identifier code
        
        if entity_code == "IL":  # Insured/Patient
            if len(elements) >= 3:
                transaction["patient_name"] = f"{elements[2]} {elements[1]}" if len(elements) >= 3 else elements[1]
            if len(elements) >= 9:
                transaction["patient_id"] = elements[8]
        elif entity_code == "1P":  # Provider
            if len(elements) >= 9:
                transaction["provider_npi"] = elements[8]

    def _process_trn(self, segment: Dict[str, Any], transaction: Dict[str, Any]) -> None:
        """Process TRN (Trace Number) segment."""
        elements = segment["elements"]
        if len(elements) >= 2:
            transaction["trace_number"] = elements[1]

    def _process_stc(self, segment: Dict[str, Any], transaction: Dict[str, Any]) -> None:
        """Process STC (Status Information) segment - THE CRITICAL SEGMENT."""
        elements = segment["elements"]
        if len(elements) < 1:
            return
        
        # First element is Status Information composite
        # Format: CATEGORY:CODE (e.g., "A7:42" = Rejected, reason 42)
        status_info = elements[0]
        if ':' in status_info:
            parts = status_info.split(':')
            transaction["status_category"] = parts[0]
            transaction["status_code"] = parts[1] if len(parts) > 1 else None
        
        # STC segment format: STC*Status*Date*ActionCode*TotalClaimChargeAmount
        # Element 4 (index 3) = Total Claim Charge Amount (not index 2!)
        if len(elements) >= 4 and elements[3]:
            try:
                transaction["billed_amount"] = float(elements[3])
            except (ValueError, TypeError):
                pass

    def _process_ref(self, segment: Dict[str, Any], transaction: Dict[str, Any]) -> None:
        """Process REF (Reference) segment."""
        elements = segment["elements"]
        if len(elements) < 2:
            return
        
        ref_qualifier = elements[0]
        ref_value = elements[1]
        
        if ref_qualifier == "D9":  # Patient Account Number / Claim ID
            transaction["claim_id"] = ref_value
        elif ref_qualifier == "EA":  # Member ID (alternative patient identifier)
            if not transaction.get("patient_id"):
                transaction["patient_id"] = ref_value

    def _process_dtp(self, segment: Dict[str, Any], transaction: Dict[str, Any]) -> None:
        """Process DTP (Date/Time Period) segment."""
        elements = segment["elements"]
        if len(elements) < 3:
            return
        
        date_qualifier = elements[0]
        if date_qualifier == "472":  # Service Period
            transaction["date_of_service"] = elements[2]

    def _process_msg(self, segment: Dict[str, Any], transaction: Dict[str, Any]) -> None:
        """Process MSG (Message Text) segment - contains rejection reason text."""
        elements = segment["elements"]
        if elements:
            # MSG contains human-readable rejection reason
            transaction["rejection_reason"] = elements[0]

    def _format_name(self, nm1_segment: Dict[str, Any]) -> str:
        """
        Format patient name from NM1 segment.
        
        Args:
            nm1_segment: NM1 segment data
            
        Returns:
            Formatted name string
        """
        last_name = nm1_segment.get("last_name", "")
        first_name = nm1_segment.get("first_name", "")
        middle_name = nm1_segment.get("middle_name", "")
        
        name_parts = [p for p in [first_name, middle_name, last_name] if p]
        return " ".join(name_parts)

    def validate(self, parsed_data: Dict[str, Any]) -> List[str]:
        """
        Validate parsed 277CA data.
        
        Critical validations for revenue tracking:
        - All rejections have a reason code
        - Required identifiers present for cross-referencing
        
        Args:
            parsed_data: Parsed 277CA data
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate each acknowledgment
        for ack in parsed_data.get("acknowledgments", []):
            # Check required fields for cross-referencing
            if not ack.get("patient_id") and not ack.get("trace_number"):
                errors.append(
                    "Missing patient identifier and trace number - "
                    "cannot cross-reference with 835"
                )
            
            # Rejections must have a reason
            if ack.get("status_category") == "A7" and not ack.get("rejection_reason"):
                errors.append(
                    f"Rejection for patient {ack.get('patient_id')} "
                    "missing rejection reason"
                )
        
        return errors
