# X12 EDI Processing Platform

Enterprise-grade X12 EDI (Electronic Data Interchange) processing system for healthcare claims data (277 Claims Status & 835 Payment/Remittance). Supports multiple input/output sources including local filesystem, AWS S3, and HTTP uploads, with AWS Lambda for serverless processing.

## 🆕 Recent Updates (v1.1.0+)

- ✅ **100% PEP8 Compliance** - Zero code style violations
- ✅ **277CA Parser** - Full support for Claim Acknowledgment with rejection tracking
- ✅ **Claim Reconciliation Engine** - Revenue integrity analysis and tracking
- ✅ **Lambda Layers** - Optimized deployment (20 KB code + 20.7 MB dependencies)
- ✅ **Project Reorganization** - Python best practices directory structure
- ✅ **Security Hardening** - Removed sensitive data from version control
- ✅ **HDI Sample Files** - Healthcare Data Insight test files integrated
- ✅ **Pylint Score: 9.04/10** - High code quality metrics

See [prompts/PROJECT_REORGANIZATION.md](prompts/PROJECT_REORGANIZATION.md) and [prompts/PYTHON_BEST_PRACTICES_REVIEW.md](prompts/PYTHON_BEST_PRACTICES_REVIEW.md) for details.

## Features

- **X12 Format Support**: 
  - 277 Claims Status (005010X212)
  - 277CA Claim Acknowledgment (with rejection tracking)
  - 835 Payment/Remittance (005010X221A1)
- **Claim Reconciliation Engine**: Track claim status changes, identify revenue leakage
- **Multiple Input Sources**: Local files, AWS S3 buckets, HTTP file uploads
- **AWS Lambda Processing**: Serverless architecture with optimized Lambda Layers
- **Multiple Output Destinations**: Local filesystem, AWS S3, direct download
- **Data Validation**: Comprehensive X12 segment and transaction validation
- **Error Handling**: Robust error handling with detailed logging
- **Type Safety**: Full type hints and Pydantic models
- **Code Quality**: PEP8 compliant, Black formatted, 9.04/10 Pylint score

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
x12-edi-processor/
├── requirements.txt                 # Python dependencies
├── requirements-dev.txt             # Development dependencies
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
│   │   ├── logging_config.py        # Logging setup
│   │   └── reconciliation.py        # Claim reconciliation engine
│   │
│   ├── parsers/                     # X12 parsing modules
│   │   ├── __init__.py
│   │   ├── base_parser.py           # Base parser interface
│   │   ├── x12_277_parser.py        # 277 Claims Status parser
│   │   ├── x12_277ca_parser.py      # 277CA Claim Acknowledgment parser
│   │   └── x12_835_parser.py        # 835 Payment/Remittance parser
│   │
│   ├── input/                       # Input handlers
│   │   ├── __init__.py
│   │   ├── base_input.py            # Base input interface
│   │   ├── local_input.py           # Local file input
│   │   ├── s3_input.py              # AWS S3 input
│   │   └── upload_input.py          # HTTP upload handler
│   │
│   └── handlers/                    # AWS Lambda handlers
│       ├── __init__.py
│       └── lambda_handler.py        # Lambda entry point
│
├── tests/                           # Test suite
│   ├── __init__.py
│   ├── conftest.py                  # Pytest fixtures and configuration
│   ├── README.md                    # Test organization guide
│   ├── unit/                        # Unit tests
│   │   ├── test_parsers.py          # Parser unit tests
│   │   └── test_input_handlers.py   # Input handler tests
│   ├── integration/                 # Integration tests
│   │   ├── test_277ca.py            # 277CA integration tests
│   │   ├── test_hdi_samples.py      # HDI sample file tests
│   │   ├── test_277_hdi_files.py    # 277 file analysis tests
│   │   ├── test_manual.py           # Manual verification tests
│   │   └── test_simple.py           # Simple functionality tests
│   ├── debug/                       # Debug utilities (not pytest tests)
│   │   ├── debug_parser.py          # Parser debugging
│   │   └── debug_277ca.py           # 277CA debugging
│   └── fixtures/                    # Test data files
│       ├── 277ca_rejections.x12     # Sample 277CA files
│       ├── 277_claim_level_status.x12
│       ├── 835_managed_care.x12     # Sample 835 files
│       └── hdi_samples/             # Healthcare Data Insight samples
│
├── scripts/                         # Build and utility scripts
│   ├── __init__.py
│   ├── README.md                    # Scripts documentation
│   ├── main.py                      # Local testing entry point
│   ├── build_layer.py               # Build AWS Lambda Layer
│   ├── build_zip.py                 # Build Lambda function package
│   ├── build.sh                     # Shell build script
│   └── compare_277_files.py         # File comparison utility
│
├── lambda/                          # AWS Lambda deployment
│   ├── template.yaml                # SAM/CloudFormation template
│   ├── lambda_function.zip          # Deployment package (20 KB)
│   ├── lambda_layer.zip             # Dependencies layer (20.7 MB)
│   └── backup_lambda_handler.py     # Previous handler backup
│
└── terraform/                       # Infrastructure as Code
    ├── main.tf                      # Main Terraform config
    ├── variables.tf                 # Variable definitions
    ├── outputs.tf                   # Output definitions
    ├── terraform.tfvars.example     # Example variables
    └── README.md                    # Terraform documentation
```

## Usage

### Local Development

```bash
python scripts/main.py
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
pytest tests/
```

### Run Unit Tests Only

```bash
pytest tests/unit/ -v
```

### Run Integration Tests

```bash
pytest tests/integration/ -v
```

### Run with Coverage

```bash
pytest --cov=src --cov-report=html
```

### Run Specific Test File

```bash
pytest tests/unit/test_parsers.py -v
```

See [tests/README.md](tests/README.md) for detailed testing documentation.

## Deployment

### Build Lambda Layer and Function

```bash
# Build Lambda Layer (dependencies)
python scripts/build_layer.py

# Build Lambda Function (code)
python scripts/build_zip.py

# Or use shell script
bash scripts/build.sh
```

### Deploy with Terraform

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

### Deploy with AWS SAM (alternative)

```bash
cd lambda
sam deploy --guided
```

See [prompts/LAMBDA_LAYER_IMPLEMENTATION.md](prompts/LAMBDA_LAYER_IMPLEMENTATION.md) for Lambda Layers architecture details.

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

## Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Quick start guide and basic usage
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Development guidelines and standards
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and changes
- **[tests/README.md](tests/README.md)** - Testing guide and organization
- **[scripts/README.md](scripts/README.md)** - Build scripts documentation
- **[terraform/README.md](terraform/README.md)** - Infrastructure as Code guide

### Internal Documentation (prompts/)

- **[prompts/PROJECT_REORGANIZATION.md](prompts/PROJECT_REORGANIZATION.md)** - Project structure details
- **[prompts/PYTHON_BEST_PRACTICES_REVIEW.md](prompts/PYTHON_BEST_PRACTICES_REVIEW.md)** - Code quality review
- **[prompts/LAMBDA_LAYER_IMPLEMENTATION.md](prompts/LAMBDA_LAYER_IMPLEMENTATION.md)** - Lambda Layers architecture
- **[prompts/README.md](prompts/README.md)** - Internal documentation index

## Version History

- **v1.1.0** - PEP8 compliance, code quality improvements
- **v1.0.0** - 277CA parser and claim reconciliation engine
- **v0.9.0** - Initial release with 277/835 parsers

## License

MIT License - See [LICENSE](LICENSE) file

## Support

For issues and questions, please open a GitHub issue.
