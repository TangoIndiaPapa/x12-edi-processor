# X12 EDI Processing Platform

Enterprise-grade X12 EDI (Electronic Data Interchange) processing system for healthcare claims data (277 Claims Status & 835 Payment/Remittance). Supports multiple input/output sources including local filesystem, AWS S3, and HTTP uploads, with AWS Lambda for serverless processing.

## Features

- **X12 Format Support**: 277 Claims Status (005010X212) and 835 Payment/Remittance (005010X221A1)
- **Multiple Input Sources**: Local files, AWS S3 buckets, HTTP file uploads
- **AWS Lambda Processing**: Serverless architecture for scalable EDI processing
- **Multiple Output Destinations**: Local filesystem, AWS S3, direct download
- **Data Validation**: Comprehensive X12 segment and transaction validation
- **Error Handling**: Robust error handling with detailed logging
- **Type Safety**: Full type hints and Pydantic models

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Input Sources  │────▶│  AWS Lambda      │────▶│ Output Targets  │
│  - Local Drive  │     │  - Parse X12     │     │  - Local Drive  │
│  - AWS S3       │     │  - Validate      │     │  - AWS S3       │
│  - HTTP Upload  │     │  - Transform     │     │  - Download     │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

## Prerequisites

- **Python 3.10, 3.11, or 3.12** (recommended - see PYTHON_VERSION_NOTE.md for details)
  - Python 3.14+ has compatibility issues with linuxforhealth-x12 library
  - Python 3.11 is recommended for best stability
- AWS Account (for S3 and Lambda features)
- pip (Python package installer)

## Installation

### 1. Clone and Setup Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` with your settings:
```
ENVIRONMENT=development
AWS_REGION=us-east-1
AWS_S3_BUCKET=your-edi-bucket
LOG_LEVEL=INFO
```

### 3. AWS Credentials

Configure AWS credentials:
```bash
aws configure
```

## Project Structure

```
vscworkspace/
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables template
├── .gitignore                       # Git ignore rules
├── pytest.ini                       # Pytest configuration
├── pyproject.toml                   # Project metadata and tool configs
│
├── src/                             # Source code
│   ├── __init__.py
│   ├── core/                        # Core business logic
│   │   ├── __init__.py
│   │   ├── config.py                # Configuration management
│   │   ├── exceptions.py            # Custom exceptions
│   │   └── logging_config.py        # Logging setup
│   │
│   ├── parsers/                     # X12 parsing modules
│   │   ├── __init__.py
│   │   ├── base_parser.py           # Base parser interface
│   │   ├── x12_277_parser.py        # 277 Claims Status parser
│   │   └── x12_835_parser.py        # 835 Payment parser
│   │
│   ├── models/                      # Data models
│   │   ├── __init__.py
│   │   ├── x12_277_models.py        # 277 Pydantic models
│   │   ├── x12_835_models.py        # 835 Pydantic models
│   │   └── common_models.py         # Shared models
│   │
│   ├── input/                       # Input handlers
│   │   ├── __init__.py
│   │   ├── base_input.py            # Base input interface
│   │   ├── local_input.py           # Local file input
│   │   ├── s3_input.py              # AWS S3 input
│   │   └── upload_input.py          # HTTP upload handler
│   │
│   ├── output/                      # Output handlers
│   │   ├── __init__.py
│   │   ├── base_output.py           # Base output interface
│   │   ├── local_output.py          # Local file output
│   │   ├── s3_output.py             # AWS S3 output
│   │   └── download_output.py       # HTTP download handler
│   │
│   ├── processors/                  # Processing logic
│   │   ├── __init__.py
│   │   ├── x12_processor.py         # Main X12 processor
│   │   └── validator.py             # X12 validation
│   │
│   ├── handlers/                    # AWS Lambda handlers
│   │   ├── __init__.py
│   │   └── lambda_handler.py        # Lambda entry point
│   │
│   └── api/                         # FastAPI endpoints (optional)
│       ├── __init__.py
│       ├── app.py                   # FastAPI application
│       └── routes.py                # API routes
│
├── tests/                           # Test suite
│   ├── __init__.py
│   ├── conftest.py                  # Pytest fixtures
│   ├── unit/                        # Unit tests
│   │   ├── test_parsers.py
│   │   ├── test_input_handlers.py
│   │   └── test_output_handlers.py
│   ├── integration/                 # Integration tests
│   │   └── test_lambda_handler.py
│   └── fixtures/                    # Test data
│       ├── sample_277.txt
│       └── sample_835.txt
│
├── lambda/                          # AWS Lambda deployment
│   ├── template.yaml                # SAM/CloudFormation template
│   └── build.sh                     # Build script
│
├── docs/                            # Documentation
│   ├── architecture.md              # Architecture overview
│   ├── x12_formats.md               # X12 format specifications
│   └── deployment.md                # Deployment guide
│
└── scripts/                         # Utility scripts
    ├── deploy_lambda.sh             # Lambda deployment script
    └── sample_data_generator.py     # Generate test data
```

## Usage

### Local Development

```bash
python main.py
```

### Process X12 File (Local)

```python
from src.processors.x12_processor import X12Processor
from src.input.local_input import LocalInput
from src.output.local_output import LocalOutput

processor = X12Processor()
input_handler = LocalInput("data/input/sample_277.txt")
output_handler = LocalOutput("data/output/")

result = processor.process(input_handler, output_handler)
print(result)
```

### Process from S3

```python
from src.input.s3_input import S3Input
from src.output.s3_output import S3Output

input_handler = S3Input(bucket="my-bucket", key="input/file.txt")
output_handler = S3Output(bucket="my-bucket", prefix="output/")

result = processor.process(input_handler, output_handler)
```

### AWS Lambda Invocation

```python
import boto3
import json

lambda_client = boto3.client('lambda')

payload = {
    "input_source": "s3",
    "bucket": "my-bucket",
    "key": "input/sample_277.txt",
    "output_destination": "s3",
    "output_bucket": "my-bucket",
    "output_prefix": "processed/"
}

response = lambda_client.invoke(
    FunctionName='X12Processor',
    InvocationType='RequestResponse',
    Payload=json.dumps(payload)
)

print(json.loads(response['Payload'].read()))
```

## Testing

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=src --cov-report=html
```

### Run Specific Tests

```bash
pytest tests/unit/test_parsers.py -v
```

## Deployment

### Deploy to AWS Lambda

```bash
cd lambda
./build.sh
sam deploy --guided
```

## X12 Format Reference

### 277 Claims Status (005010X212)
- Information Source (Payer)
- Information Receiver (Provider)
- Service Provider
- Claim Status Tracking

### 835 Payment/Remittance (005010X221A1)
- Financial Information
- Payer Identification
- Payee Identification  
- Claim Payment Information
- Service Line Adjustments

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

MIT License - See [LICENSE](LICENSE) file

## Support

For issues and questions, please open a GitHub issue.
