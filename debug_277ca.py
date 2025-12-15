"""Debug 277CA parsing."""

from src.parsers.x12_277ca_parser import X12_277CA_Parser

# Read the test file
with open("tests/fixtures/277ca_rejections.x12", "r") as f:
    x12_content = f.read()

# Parse it
parser = X12_277CA_Parser()

# Test segment parsing
segments = parser._parse_segments(x12_content)
print(f"Total segments found: {len(segments)}\n")

# Show first 20 segments
for i, seg in enumerate(segments[:20]):
    print(f"{i+1}. {seg['id']}: {seg['elements'][:5]}")  # First 5 elements only

# Look for HL segments specifically
hl_segments = [s for s in segments if s['id'] == 'HL']
print(f"\n\nHL segments found: {len(hl_segments)}")
for hl in hl_segments:
    print(f"  HL: {hl['elements']}")

# Look for NM1 segments
nm1_segments = [s for s in segments if s['id'] == 'NM1']
print(f"\n\nNM1 segments found: {len(nm1_segments)}")
for nm1 in nm1_segments[:5]:
    print(f"  NM1: {nm1['elements'][:4]}")

# Look for STC segments
stc_segments = [s for s in segments if s['id'] == 'STC']
print(f"\n\nSTC segments found: {len(stc_segments)}")
for stc in stc_segments:
    print(f"  STC: {stc['elements']}")
