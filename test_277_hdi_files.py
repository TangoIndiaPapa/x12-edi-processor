#!/usr/bin/env python3
"""Test HDI 277CA sample files with detailed analysis."""

import json
from src.parsers.x12_277ca_parser import X12_277CA_Parser

def analyze_file_segments(filepath):
    """Read and analyze raw segments in a 277 file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Split by segment terminator
    segments = [s.strip() for s in content.replace('\n', '').split('~') if s.strip()]
    
    print(f"\n{'='*80}")
    print(f"File: {filepath}")
    print(f"{'='*80}")
    print(f"Total segments: {len(segments)}\n")
    
    # Count segment types
    segment_counts = {}
    hl_levels = []
    nm1_qualifiers = []
    stc_categories = []
    
    for seg in segments:
        elements = seg.split('*')
        seg_type = elements[0]
        
        segment_counts[seg_type] = segment_counts.get(seg_type, 0) + 1
        
        if seg_type == 'HL' and len(elements) >= 4:
            hl_levels.append(elements[3])
        elif seg_type == 'NM1' and len(elements) >= 2:
            nm1_qualifiers.append(elements[1])
        elif seg_type == 'STC' and len(elements) >= 2:
            # STC01 format: CategoryCode:StatusCode:EntityCode
            stc_parts = elements[1].split(':')
            if stc_parts:
                stc_categories.append(stc_parts[0])
    
    print("Segment Type Counts:")
    for seg_type in sorted(segment_counts.keys()):
        print(f"  {seg_type}: {segment_counts[seg_type]}")
    
    print(f"\nHL Hierarchy Levels: {set(hl_levels)}")
    print(f"NM1 Entity Qualifiers: {set(nm1_qualifiers)}")
    print(f"STC Status Categories: {set(stc_categories)}")
    
    return segments

def test_with_parser(filepath):
    """Test file with our 277CA parser."""
    print(f"\n{'='*80}")
    print(f"Testing with X12_277CA_Parser: {filepath}")
    print(f"{'='*80}")
    
    parser = X12_277CA_Parser()
    result = parser.parse(filepath)
    
    acks = result.get('acknowledgments', [])
    print(f"\nAcknowledgments found: {len(acks)}")
    
    if acks:
        for i, ack in enumerate(acks, 1):
            print(f"\n  Acknowledgment #{i}:")
            print(f"    Status Category: {ack.get('status_category', 'N/A')}")
            print(f"    Patient ID: {ack.get('patient_id', 'N/A')}")
            print(f"    Billed Amount: ${ack.get('billed_amount', 0)}")
            print(f"    Date of Service: {ack.get('date_of_service', 'N/A')}")
            
            reasons = ack.get('rejection_reasons', [])
            if reasons:
                print(f"    Rejection Reasons: {', '.join(reasons)}")
    else:
        print("\n  ⚠️  No acknowledgments extracted by parser")
        print("  This indicates the file structure doesn't match parser expectations")
    
    return result

def show_sample_segments(filepath, count=20):
    """Show first N segments of the file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    segments = [s.strip() for s in content.replace('\n', '').split('~') if s.strip()]
    
    print(f"\n{'='*80}")
    print(f"Sample Segments (first {count}):")
    print(f"{'='*80}")
    
    for i, seg in enumerate(segments[:count], 1):
        print(f"{i:3}. {seg}")

if __name__ == '__main__':
    files_to_test = [
        'tests/fixtures/hdi_samples/277CA-all-fields.edi',
        'tests/fixtures/hdi_samples/277CA-receiver-rejected.edi',
    ]
    
    print("\n" + "🧪 HDI 277CA Sample Files Analysis" + "\n")
    
    for filepath in files_to_test:
        # Analyze raw segments
        analyze_file_segments(filepath)
        
        # Show sample segments
        show_sample_segments(filepath, 20)
        
        # Test with our parser
        test_with_parser(filepath)
        
        print("\n")
    
    print("="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print("\nKey Observations:")
    print("- HDI files use HL levels: 20 (Payer), 21 (Receiver), 19 (Provider), PT (Patient)")
    print("- Our parser expects simpler structure with NM1*IL (Insured/Patient)")
    print("- HDI uses NM1*QC (Patient), NM1*85 (Provider), NM1*41 (Receiver), NM1*PR (Payer)")
    print("- Status categories: A1-A8 (our parser handles A1, A7)")
    print("\nConclusion: Files are valid 277CA but require parser enhancement to support")
    print("            the multi-level hierarchy structure used by HDI.")
