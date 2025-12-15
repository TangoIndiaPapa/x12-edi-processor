#!/usr/bin/env python3
"""Test HDI sample files with our parsers."""

import json
from src.parsers.x12_277ca_parser import X12_277CA_Parser
from src.parsers.x12_835_parser import X12_835_Parser

def test_277ca_all_fields():
    """Test 277CA comprehensive sample."""
    print("\n" + "="*80)
    print("Testing: 277CA-all-fields.edi")
    print("="*80)
    
    parser = X12_277CA_Parser()
    result = parser.parse('tests/fixtures/hdi_samples/277CA-all-fields.edi')
    
    acks = result.get('acknowledgments', [])
    print(f"\n✅ Found {len(acks)} acknowledgments")
    
    for i, ack in enumerate(acks, 1):
        status = ack.get('status_category', 'Unknown')
        patient_id = ack.get('patient_id', 'N/A')
        amount = ack.get('billed_amount', 0)
        print(f"\n  Acknowledgment #{i}:")
        print(f"    Status: {status}")
        print(f"    Patient ID: {patient_id}")
        print(f"    Billed Amount: ${amount}")
        
        reasons = ack.get('rejection_reasons', [])
        if reasons:
            print(f"    Rejection Reasons: {', '.join(reasons)}")
    
    return result

def test_277ca_receiver_rejected():
    """Test 277CA receiver-level rejection."""
    print("\n" + "="*80)
    print("Testing: 277CA-receiver-rejected.edi")
    print("="*80)
    
    parser = X12_277CA_Parser()
    result = parser.parse('tests/fixtures/hdi_samples/277CA-receiver-rejected.edi')
    
    acks = result.get('acknowledgments', [])
    print(f"\n✅ Found {len(acks)} acknowledgments")
    
    for i, ack in enumerate(acks, 1):
        status = ack.get('status_category', 'Unknown')
        print(f"\n  Acknowledgment #{i}:")
        print(f"    Status: {status}")
        print(f"    Details: {json.dumps(ack, indent=6)}")
    
    return result

def test_835_all_fields():
    """Test 835 comprehensive sample."""
    print("\n" + "="*80)
    print("Testing: 835-all-fields.dat")
    print("="*80)
    
    parser = X12_835_Parser()
    result = parser.parse('tests/fixtures/hdi_samples/835-all-fields.dat')
    
    payments = result.get('payments', [])
    print(f"\n✅ Found {len(payments)} payments")
    
    for i, payment in enumerate(payments[:3], 1):  # Show first 3
        claim_id = payment.get('claim_id', 'N/A')
        patient_id = payment.get('patient_id', 'N/A')
        paid_amount = payment.get('paid_amount', 0)
        print(f"\n  Payment #{i}:")
        print(f"    Claim ID: {claim_id}")
        print(f"    Patient ID: {patient_id}")
        print(f"    Paid Amount: ${paid_amount}")
    
    if len(payments) > 3:
        print(f"\n  ... and {len(payments) - 3} more payments")
    
    return result

def test_835_provider_adjustment():
    """Test 835 provider adjustment sample."""
    print("\n" + "="*80)
    print("Testing: 835-provider-adjustment.dat")
    print("="*80)
    
    parser = X12_835_Parser()
    result = parser.parse('tests/fixtures/hdi_samples/835-provider-adjustment.dat')
    
    payments = result.get('payments', [])
    print(f"\n✅ Found {len(payments)} payments")
    
    summary = result.get('summary', {})
    print(f"\n  Summary:")
    print(f"    Total Paid: ${summary.get('total_paid', 0)}")
    print(f"    Transaction Date: {summary.get('transaction_date', 'N/A')}")
    
    return result

if __name__ == '__main__':
    print("\n" + "🧪 Testing HDI Sample Files" + "\n")
    
    try:
        # Test 277CA files
        test_277ca_all_fields()
        test_277ca_receiver_rejected()
        
        # Test 835 files
        test_835_all_fields()
        test_835_provider_adjustment()
        
        print("\n" + "="*80)
        print("✅ All HDI sample files tested successfully!")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error testing HDI samples: {e}")
        import traceback
        traceback.print_exc()
