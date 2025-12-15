# Quick Start Guide - X12 EDI Processing Platform

## Overview
This platform processes X12 277 (Claims Status) and 835 (Payment/Remittance) EDI documents using Python with AWS Lambda integration.

## Prerequisites

### Windows: Add pip to PATH

If you get an error like `'pip' is not recognized as an internal or external command`, you need to add Python to your PATH:

**Option 1: Using Environment Variables GUI**
1. Open **System Properties** → **Advanced** → **Environment Variables**
2. Under **User variables** or **System variables**, find **Path**
3. Click **Edit** → **New**
4. Add these paths (adjust Python version as needed):
   ```
   C:\Users\YourUsername\AppData\Local\Programs\Python\Python310\
   C:\Users\YourUsername\AppData\Local\Programs\Python\Python310\Scripts\
   ```
5. Click **OK** on all dialogs
6. **Restart your terminal/PowerShell**

**Option 2: Using PowerShell (Quick)**
```powershell
# Find Python installation
python -c "import sys; print(sys.executable)"

# Add to user PATH (replace with your Python path)
$pythonPath = "C:\Users\YourUsername\AppData\Local\Programs\Python\Python310"
$scriptsPath = "$pythonPath\Scripts"

[Environment]::SetEnvironmentVariable("Path", $env:Path + ";$pythonPath;$scriptsPath", "User")

# Restart PowerShell and verify
pip --version
```

**Option 3: Reinstall Python with PATH**
1. Download Python from [python.org](https://python.org)
2. Run installer
3. ✅ **Check "Add Python to PATH"** during installation
4. Complete installation

## Installation

### 1. Verify Python and pip
```bash
# Check Python installation
python --version

# Check pip installation
pip --version

# If pip still not found, try:
python -m pip --version
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt

# Or if pip not in PATH:
python -m pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings:
# - AWS_REGION=us-east-1
# - AWS_S3_BUCKET=your-bucket-name
# - LOG_LEVEL=INFO
```

### 3. Verify Installation
```bash
python scripts/main.py
```

## Testing Your Setup

### Run Unit Tests
```bash
pytest tests/unit/ -v
```

### Run All Tests
```bash
pytest tests/
```

### Run Integration Tests (requires test files)
```bash
pytest tests/integration/test_simple.py
```

## Project Organization

The project follows Python best practices:

- **`src/`** - All source code (parsers, handlers, core logic)
- **`tests/`** - All tests organized by type:
  - `tests/unit/` - Fast, isolated unit tests
  - `tests/integration/` - Integration tests with real files
  - `tests/fixtures/` - Test data files
  - `tests/debug/` - Debug utilities
- **`scripts/`** - Build and utility scripts:
  - `scripts/main.py` - Local testing entry point
  - `scripts/build_layer.py` - Build Lambda Layer
  - `scripts/build_zip.py` - Build Lambda function
- **`lambda/`** - Lambda deployment artifacts
- **`terraform/`** - Infrastructure as Code

See [prompts/PROJECT_REORGANIZATION.md](prompts/PROJECT_REORGANIZATION.md) for detailed structure documentation.

## Basic Usage

### Parse a Local X12 File

```python
from src.parsers.x12_277_parser import X12_277_Parser
from src.input.local_input import LocalInput

# Read X12 file
input_handler = LocalInput("path/to/your/file.x12")
content = input_handler.read()

# Parse 277 document
parser = X12_277_Parser()
result = parser.parse(content)

# Access parsed data
print(f"Transaction Type: {result['transaction_type']}")
print(f"Version: {result['version']}")
print(f"Number of transactions: {len(result['transactions'])}")

# Validate
errors = parser.validate(result)
if errors:
    print(f"Validation errors: {errors}")
else:
    print("Document is valid!")
```

### Parse 835 Payment Document

```python
from src.parsers.x12_835_parser import X12_835_Parser

parser = X12_835_Parser()
result = parser.parse(content)

# Access payment information
for transaction in result['transactions']:
    financial = transaction['financial_information']
    print(f"Payment Amount: ${financial['total_actual_provider_payment']}")
    print(f"Payment Date: {financial['payment_date']}")
    
    # Access claim details
    for claim in transaction['claims']:
        print(f"Claim ID: {claim['claim_identifier']}")
        print(f"Paid: ${claim['payment_amount']}")
```

### Process from AWS S3

```python
from src.input.s3_input import S3Input

# Read from S3
input_handler = S3Input(
    bucket="my-edi-bucket",
    key="input/claims_277.x12"
)
content = input_handler.read()

# Parse and process...
```

### Handle File Upload

```python
from src.input.upload_input import UploadInput

# From uploaded bytes
file_bytes = uploaded_file.read()  # From HTTP upload
input_handler = UploadInput(
    file_content=file_bytes,
    filename="uploaded_file.x12"
)
content = input_handler.read()
```

## Running Tests

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
# Test parsers only
pytest tests/unit/test_parsers.py -v

# Test input handlers
pytest tests/unit/test_input_handlers.py -v
```

## AWS Lambda Deployment

### 1. Build Lambda Package
```bash
cd lambda
./build.sh
```

### Windows: pip not recognized
```powershell
# Use python -m pip instead
python -m pip install -r requirements.txt

# Or add to PATH (see Prerequisites section above)
```

### Import Errors
```bash
# Ensure you're in the virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
# Or: python -m # - Stack name: x12-edi-processor
# - AWS Region: us-east-1
# - Parameter Environment: development
# - Parameter S3Bucket: your-bucket-name

# Subsequent deployments
sam deploy
```

### 3. Invoke Lambda Function

```python
import boto3
import json

lambda_client = boto3.client('lambda')

# Create event
event = {
    "input_source": "s3",
    "bucket": "my-bucket",
    "key": "input/sample_277.x12",
    "transaction_type": "277",
    "output_destination": "s3",
    "output_bucket": "my-bucket",
    "output_prefix": "processed/"
}

# Invoke Lambda
response = lambda_client.invoke(
    FunctionName='x12-edi-processor-development',
    InvocationType='RequestResponse',
    Payload=json.dumps(event)
)

# Get result
result = json.loads(response['Payload'].read())
print(result)
```

## Sample X12 Data

The `tests/fixtures/` directory contains sample X12 files for testing:
- `sample_277.txt` - Claims Status document
- `sample_835.txt` - Payment/Remittance document

## Troubleshooting

### Import Errors
```bash
# Ensure you're in the virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### AWS Credentials
```bash
# Configure AWS CLI
aws configure

# Test credentials
aws s3 ls
```

### File Size Limits
Default maximum file size is 50MB. To change:
```bash
# In .env file
MAX_FILE_SIZE_MB=100
```

## Next Steps

1. **Review Documentation**: See [README.md](README.md) for comprehensive docs
2. **Explore Code**: Check out the parsers in `src/parsers/`
3. **Run Tests**: Execute `pytest` to ensure everything works
4. **Deploy to AWS**: Follow Lambda deployment steps above
5. **Process Your Data**: Use your own X12 files with the system

## Support

- Issues: Open a GitHub issue
- Documentation: See `docs/` directory
- Contributing: See [CONTRIBUTING.md](CONTRIBUTING.md)

## Key Files

- `main.py` - Application entry point
- `src/handlers/lambda_handler.py` - AWS Lambda handler
- `src/parsers/x12_277_parser.py` - 277 parser implementation
- `src/parsers/x12_835_parser.py` - 835 parser implementation
- `lambda/template.yaml` - AWS SAM deployment template
- `.env.example` - Environment configuration template

---

**Ready to process X12 EDI documents!** 🚀
