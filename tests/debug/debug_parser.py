#!/usr/bin/env python3
"""Debug why our 277CA parser isn't finding acknowledgments."""

from src.parsers.x12_277ca_parser import X12_277CA_Parser

# Read our test file
with open('tests/fixtures/277ca_rejections.x12', 'r') as f:
    content = f.read()

# Parse
parser = X12_277CA_Parser()

# Get segments
segments = parser._parse_segments(content)

print(f"Total segments parsed: {len(segments)}\n")

# Show HL segments
hl_segments = [s for s in segments if s['id'] == 'HL']
print(f"HL segments found: {len(hl_segments)}")
for hl in hl_segments:
    print(f"  {hl}")

# Show NM1 segments
nm1_segments = [s for s in segments if s['id'] == 'NM1']
print(f"\nNM1 segments found: {len(nm1_segments)}")
for nm1 in nm1_segments:
    print(f"  {nm1}")

# Show STC segments
stc_segments = [s for s in segments if s['id'] == 'STC']
print(f"\nSTC segments found: {len(stc_segments)}")
for stc in stc_segments:
    print(f"  {stc}")

# Now actually parse
print("\n" + "="*80)
print("Parsing result:")
print("="*80)
result = parser.parse(content)
print(f"\nAcknowledgments: {len(result['acknowledgments'])}")
print(f"Rejections: {len(result['rejections'])}")
print(f"Acceptances: {len(result['acceptances'])}")

if result['acknowledgments']:
    print("\nAcknowledgment details:")
    import json
    print(json.dumps(result['acknowledgments'], indent=2))
