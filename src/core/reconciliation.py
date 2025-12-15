"""Revenue reconciliation logic for detecting unsubmitted claims.

This module implements the "Black Hole" detection strategy described in revenue
cycle management best practices:

1. Claims submitted → 277CA rejection (formatting error)
2. Staff misses rejection alert
3. Staff waits for 835 payment
4. 835 never comes (claim was rejected at gate)
5. Revenue lost forever

The reconciliation engine cross-references 277CA rejections with 835 remittances
to identify claims that were rejected and never resubmitted.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set

from ..core.logging_config import get_logger

logger = get_logger(__name__)


class ClaimReconciliationEngine:
    """
    Cross-reference 277CA rejections with 835 payments to identify missing revenue.
    
    This implements the critical revenue integrity workflow:
    - Track all 277CA rejections (front door rejections)
    - Monitor 835 payments for resubmitted claims
    - Alert on claims rejected >30 days ago with no 835 payment
    """

    def __init__(self, lookback_days: int = 60):
        """
        Initialize reconciliation engine.
        
        Args:
            lookback_days: How far back to check for missing resubmissions
        """
        self.lookback_days = lookback_days
        self.rejections_cache: Dict[str, Dict[str, Any]] = {}
        self.payments_cache: Dict[str, Dict[str, Any]] = {}

    def add_277ca_rejections(self, parsed_277ca: Dict[str, Any]) -> None:
        """
        Add 277CA rejections to tracking database.
        
        Args:
            parsed_277ca: Parsed 277CA data with rejections list
        """
        for rejection in parsed_277ca.get("rejections", []):
            # Create composite key for matching (can't rely on claim ID alone)
            match_key = self._create_match_key(rejection)
            
            if match_key:
                self.rejections_cache[match_key] = {
                    "rejection_date": rejection.get("transaction_date"),
                    "patient_id": rejection.get("patient_id"),
                    "patient_name": rejection.get("patient_name"),
                    "date_of_service": rejection.get("date_of_service"),
                    "billed_amount": rejection.get("billed_amount"),
                    "rejection_reason": rejection.get("rejection_reason"),
                    "status_code": rejection.get("status_code"),
                    "trace_number": rejection.get("trace_number"),
                    "found_in_835": False,
                    "resubmission_date": None
                }
                
                logger.info(
                    f"Tracked 277CA rejection: Patient {rejection.get('patient_id')}, "
                    f"Reason: {rejection.get('rejection_reason')}"
                )

    def add_835_payments(self, parsed_835: Dict[str, Any]) -> None:
        """
        Add 835 payments and mark matching rejections as resubmitted.
        
        Args:
            parsed_835: Parsed 835 data with claims list
        """
        for claim in parsed_835.get("claims", []):
            # Create same composite key for matching
            match_key = self._create_match_key(claim)
            
            if match_key:
                # Store payment info
                self.payments_cache[match_key] = {
                    "payment_date": claim.get("payment_date"),
                    "patient_id": claim.get("patient_id"),
                    "paid_amount": claim.get("paid_amount"),
                    "claim_status": claim.get("claim_status")
                }
                
                # Check if this payment matches a previous rejection
                if match_key in self.rejections_cache:
                    self.rejections_cache[match_key]["found_in_835"] = True
                    self.rejections_cache[match_key]["resubmission_date"] = claim.get("payment_date")
                    
                    logger.info(
                        f"✅ Matched 835 payment to 277CA rejection: {match_key} - "
                        "Claim was successfully resubmitted"
                    )

    def find_unsubmitted_claims(
        self, 
        days_threshold: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Identify rejected claims that haven't appeared in 835 after threshold days.
        
        This is the "Black Hole" detection - claims that crashed at the gate
        and were never rebooted (resubmitted).
        
        Args:
            days_threshold: Days since rejection to consider claim "lost"
            
        Returns:
            List of unsubmitted claim alerts
        """
        alerts = []
        current_date = datetime.now()
        threshold_date = current_date - timedelta(days=days_threshold)
        
        for match_key, rejection in self.rejections_cache.items():
            # Skip if already found in 835
            if rejection["found_in_835"]:
                continue
            
            # Parse rejection date
            rejection_date_str = rejection.get("rejection_date")
            if not rejection_date_str:
                continue
            
            try:
                # Handle different date formats (YYYYMMDD or YYYY-MM-DD)
                if "-" in rejection_date_str:
                    rejection_date = datetime.strptime(rejection_date_str, "%Y-%m-%d")
                else:
                    rejection_date = datetime.strptime(rejection_date_str, "%Y%m%d")
            except ValueError:
                logger.warning(f"Invalid date format: {rejection_date_str}")
                continue
            
            # Check if rejection is old enough to be concerning
            if rejection_date < threshold_date:
                days_since_rejection = (current_date - rejection_date).days
                
                alert = {
                    "severity": "HIGH" if days_since_rejection > 45 else "MEDIUM",
                    "match_key": match_key,
                    "patient_id": rejection["patient_id"],
                    "patient_name": rejection["patient_name"],
                    "date_of_service": rejection["date_of_service"],
                    "billed_amount": rejection["billed_amount"],
                    "rejection_date": rejection["rejection_date"],
                    "rejection_reason": rejection["rejection_reason"],
                    "days_since_rejection": days_since_rejection,
                    "estimated_revenue_loss": rejection.get("billed_amount", 0),
                    "action_required": (
                        "Review rejection reason and resubmit corrected claim. "
                        "This claim will NEVER appear in 835 until resubmitted."
                    )
                }
                
                alerts.append(alert)
                
                logger.warning(
                    f"⚠️  UNSUBMITTED CLAIM DETECTED: Patient {alert['patient_id']}, "
                    f"${alert['billed_amount']}, {days_since_rejection} days old"
                )
        
        # Sort by days since rejection (oldest first - highest priority)
        alerts.sort(key=lambda x: x["days_since_rejection"], reverse=True)
        
        return alerts

    def get_reconciliation_summary(self) -> Dict[str, Any]:
        """
        Generate summary statistics for revenue reconciliation.
        
        Returns:
            Summary dict with counts and financial impact
        """
        total_rejections = len(self.rejections_cache)
        resubmitted = sum(
            1 for r in self.rejections_cache.values() if r["found_in_835"]
        )
        unsubmitted = total_rejections - resubmitted
        
        # Calculate potential revenue at risk
        potential_loss = sum(
            float(r.get("billed_amount", 0) or 0)
            for r in self.rejections_cache.values()
            if not r["found_in_835"]
        )
        
        return {
            "total_rejections_tracked": total_rejections,
            "successfully_resubmitted": resubmitted,
            "still_unsubmitted": unsubmitted,
            "resubmission_rate": (
                (resubmitted / total_rejections * 100) if total_rejections > 0 else 0
            ),
            "potential_revenue_at_risk": potential_loss,
            "tracking_period_days": self.lookback_days
        }

    def _create_match_key(self, transaction: Dict[str, Any]) -> Optional[str]:
        """
        Create composite matching key for cross-referencing.
        
        Since rejected claims often don't have Payer Claim Control Numbers yet,
        we must match on Patient + Date of Service + Amount.
        
        Args:
            transaction: 277CA rejection or 835 claim data
            
        Returns:
            Composite key string or None if insufficient data
        """
        patient_id = transaction.get("patient_id")
        date_of_service = transaction.get("date_of_service")
        amount = transaction.get("billed_amount") or transaction.get("charged_amount")
        
        # Need at least patient ID and one other identifier
        if not patient_id:
            return None
        
        # Normalize date format (handle ranges like "20050831-20050906")
        if date_of_service and "-" in str(date_of_service):
            date_parts = str(date_of_service).split("-")
            if len(date_parts) == 2 and len(date_parts[0]) == 8:
                # It's a date range (YYYYMMDD-YYYYMMDD), use start date
                date_of_service = date_parts[0]
        
        # Create composite key
        key_parts = [str(patient_id)]
        
        if date_of_service:
            key_parts.append(str(date_of_service))
        
        if amount:
            # Normalize amount (remove decimals for matching)
            key_parts.append(str(int(float(amount))))
        
        return "|".join(key_parts) if len(key_parts) >= 2 else None


def generate_reconciliation_report(
    rejections_277ca: List[Dict[str, Any]],
    payments_835: List[Dict[str, Any]],
    days_threshold: int = 30
) -> Dict[str, Any]:
    """
    Convenience function to generate full reconciliation report.
    
    Args:
        rejections_277ca: List of parsed 277CA rejection transactions
        payments_835: List of parsed 835 claim transactions
        days_threshold: Days before flagging as unsubmitted
        
    Returns:
        Full reconciliation report with alerts and summary
    """
    engine = ClaimReconciliationEngine()
    
    # Add data (simulating database lookups)
    engine.add_277ca_rejections({"rejections": rejections_277ca})
    engine.add_835_payments({"claims": payments_835})
    
    # Generate alerts and summary
    unsubmitted_alerts = engine.find_unsubmitted_claims(days_threshold)
    summary = engine.get_reconciliation_summary()
    
    report = {
        "report_date": datetime.now().isoformat(),
        "unsubmitted_claims": unsubmitted_alerts,
        "summary": summary,
        "alert_count": len(unsubmitted_alerts),
        "high_severity_count": sum(
            1 for a in unsubmitted_alerts if a["severity"] == "HIGH"
        )
    }
    
    logger.info(
        f"Reconciliation Report: {report['alert_count']} unsubmitted claims, "
        f"${summary['potential_revenue_at_risk']:.2f} at risk"
    )
    
    return report
