# X12 EDI Processing Platform

Enterprise-grade X12 EDI processing system for healthcare claims data (277 & 835).

## Project Overview
- **Language**: Python 3.10+
- **Purpose**: Process X12 277 Claims Status and 835 Payment/Remittance EDI documents
- **Architecture**: AWS Lambda-based serverless processing with multiple input/output options

## Key Features
- Parse X12 277 (Claims Status) and 835 (Payment/Remittance) transactions
- Multiple input sources: Local filesystem, AWS S3, HTTP uploads
- AWS Lambda processing for scalability
- Multiple output destinations: Local, S3, download
- Comprehensive validation and error handling
- Type-safe implementation with Pydantic models

## Project Structure
```
vscworkspace/
├── src/
│   ├── core/          # Configuration, exceptions, logging
│   ├── parsers/       # X12 277 and 835 parsers
│   ├── input/         # Input handlers (local, S3, upload)
│   ├── output/        # Output handlers (local, S3, download)
│   └── handlers/      # AWS Lambda handler
├── tests/             # Comprehensive test suite
├── lambda/            # AWS SAM deployment templates
└── docs/              # Documentation
```

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your AWS credentials and settings
```

### 3. Run Locally
```bash
python main.py
```

### 4. Run Tests
```bash
pytest
```

### 5. Deploy to AWS Lambda
```bash
cd lambda
./build.sh
sam deploy --guided
```

## Usage Examples

### Process Local File
```python
from src.parsers.x12_277_parser import X12_277_Parser
from src.input.local_input import LocalInput

handler = LocalInput("data/sample_277.txt")
content = handler.read()

parser = X12_277_Parser()
result = parser.parse(content)
print(result)
```

### Process from S3
```python
from src.input.s3_input import S3Input

handler = S3Input(bucket="my-bucket", key="input/file.x12")
content = handler.read()
# Process content...
```

## Technology Stack
- **X12 Parsing**: LinuxForHealth X12, copyleftdev/x12-python
- **AWS**: boto3, Lambda, S3
- **Data Validation**: Pydantic
- **Testing**: pytest, moto (AWS mocking)
- **Deployment**: AWS SAM

## References
- X12 277 Specification: 005010X212
- X12 835 Specification: 005010X221A1
- See attached PDF for detailed format specifications

## Next Steps
1. Review README.md for comprehensive documentation
2. Check CONTRIBUTING.md for development guidelines
3. Explore sample data in tests/fixtures/
4. Review lambda/template.yaml for AWS deployment
5. Test with your own X12 files
