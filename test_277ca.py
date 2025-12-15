"""Quick test of 277CA parser functionality."""

from src.parsers.x12_277ca_parser import X12_277CA_Parser

# Read the test file
with open("tests/fixtures/277ca_rejections.x12", "r") as f:
    x12_content = f.read()

# Parse it
parser = X12_277CA_Parser()
try:
    result = parser.parse(x12_content)
    
    print("✅ 277CA Parsing Successful!")
    print(f"\nSummary:")
    print(f"  Total acknowledgments: {result['summary']['total_claims']}")
    print(f"  Rejections: {result['summary']['rejected_count']}")
    print(f"  Acceptances: {result['summary']['accepted_count']}")
    print(f"  Rejection rate: {result['summary']['rejection_rate']:.1f}%")
    
    print(f"\n📋 Rejections:")
    for rejection in result['rejections']:
        print(f"  • Patient: {rejection.get('patient_name', 'N/A')}")
        print(f"    Amount: ${rejection.get('billed_amount', 0)}")
        print(f"    Reason: {rejection.get('rejection_reason', 'N/A')}")
        print()
    
    print(f"✅ Acceptances:")
    for acceptance in result['acceptances']:
        print(f"  • Patient: {acceptance.get('patient_name', 'N/A')}")
        print(f"    Amount: ${acceptance.get('billed_amount', 0)}")
        print()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
