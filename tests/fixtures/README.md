# X12 Test Fixtures

This directory contains validated X12 EDI test files sourced from the LinuxForHealth X12 library test suite.

## Test Files

### 277 Claims Status Response

**File**: `277_claim_level_status.x12`
- **Source**: [LinuxForHealth X12 Test Resources](https://github.com/LinuxForHealth/x12/tree/main/src/tests/resources/277_005010X212)
- **Version**: 005010X212
- **Description**: Claim-level status response with multiple information sources, receivers, and providers
- **Features**:
  - Information Source (Payer): ABC INSURANCE
  - Information Receiver: XYZ SERVICE
  - Service Providers: HOME HOSPITAL, HOME HOSPITAL PHYSICIANS
  - Multiple claim status scenarios (Paid, Denied, Forwarded)
  - 38 segments total

### 835 Payment/Remittance - Medicare Part A

**File**: `835_medicare_part_a.x12`
- **Source**: [LinuxForHealth X12 Test Resources](https://github.com/LinuxForHealth/x12/tree/main/src/tests/resources/835_005010X221A1)
- **Version**: 005010X221A1
- **Description**: Medicare Part A payment and remittance advice
- **Features**:
  - Payer: INSURANCE COMPANY OF TIMBUCKTU
  - Payee: REGIONAL HOPE HOSPITAL
  - Payment Method: ACH (Automated Clearing House)
  - Provider Adjustment Details (LX, TS3, TS2 segments)
  - Multiple claim payments (CLP segments)
  - 28 segments total

### 835 Payment/Remittance - Managed Care

**File**: `835_managed_care.x12`
- **Source**: [LinuxForHealth X12 Test Resources](https://github.com/LinuxForHealth/x12/tree/main/src/tests/resources/835_005010X221A1)
- **Version**: 005010X221A1
- **Description**: Managed care payment and remittance advice
- **Features**:
  - Payer: RUSHMORE LIFE
  - Payee: ACME MEDICAL CENTER
  - Payment Method: ACH
  - Service-level detail (SVC segments)
  - Multiple claim adjustments (CAS segments)
  - 26 segments total

## Compliance

All test files are production-quality X12 documents that:
- ✅ Pass LinuxForHealth strict validation
- ✅ Conform to HIPAA 5010 specifications
- ✅ Include all required segments and loops
- ✅ Have correct segment counts in SE segments
- ✅ Use valid transaction purpose codes
- ✅ Include proper hierarchical structures (HL segments)

## Usage in Tests

These fixtures are loaded in `tests/conftest.py` and used throughout the test suite:

```python
# 277 Claims Status
def test_parse_277(sample_277_content):
    parser = X12_277_Parser()
    result = parser.parse(sample_277_content)
    assert result is not None

# 835 Medicare Part A
def test_parse_835_medicare(sample_835_medicare):
    parser = X12_835_Parser()
    result = parser.parse(sample_835_medicare)
    assert result is not None

# 835 Managed Care
def test_parse_835_managed_care(sample_835_managed_care):
    parser = X12_835_Parser()
    result = parser.parse(sample_835_managed_care)
    assert result is not None
```

## References

- **X12 277 Specification**: ASC X12N 005010X212 - Health Care Claim Status Notification
- **X12 835 Specification**: ASC X12N 005010X221A1 - Health Care Claim Payment/Advice
- **LinuxForHealth X12**: https://github.com/LinuxForHealth/x12
- **HIPAA 5010**: https://www.cms.gov/medicare/regulations-guidance/hipaa-administrative-simplification

## Segment Structure Overview

### 277 Key Segments
- **ISA/GS/ST**: Envelope and transaction set headers
- **BHT**: Beginning of Hierarchical Transaction (0010*08 = Claims Status Response)
- **HL**: Hierarchical Level (20=Info Source, 21=Info Receiver, 19=Provider, 22=Subscriber)
- **NM1**: Individual or Organizational Name
- **TRN**: Trace Number
- **STC**: Status Information
- **REF**: Reference Identification
- **DTP**: Date or Time Period
- **SVC**: Service Information

### 835 Key Segments
- **BPR**: Financial Information (Payment details)
- **TRN**: Trace Number
- **DTM**: Date/Time Reference
- **N1/N3/N4**: Name and Address
- **LX**: Provider Adjustment
- **CLP**: Claim Payment Information
- **CAS**: Claim Adjustment
- **SVC**: Service Payment Information
- **PLB**: Provider Level Adjustment

## Validation Notes

The LinuxForHealth library performs strict X12 validation including:
- Segment terminator validation (~)
- Element delimiter validation (*)
- Required segment presence
- Correct segment ordering
- Hierarchical level structure validation
- Segment count verification (SE segment)
- Transaction set control number matching

All test files pass this strict validation, ensuring production-quality test coverage.
