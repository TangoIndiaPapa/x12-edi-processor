# Changelog

All notable changes to the X12 EDI Processing Platform will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Documentation updated to reflect reorganized project structure
- All file paths updated from root to `scripts/` and `tests/` directories

## [1.1.0] - 2025-12-15

### Added
- 277CA Claim Acknowledgment parser with rejection tracking
- Claim Reconciliation Engine for revenue integrity analysis
- Lambda Layers architecture (20 KB code + 20.7 MB dependencies)
- Healthcare Data Insight (HDI) sample test files integration
- Comprehensive project documentation ([PROJECT_REORGANIZATION.md](PROJECT_REORGANIZATION.md))
- Test organization documentation ([tests/README.md](tests/README.md))
- Build scripts documentation ([scripts/README.md](scripts/README.md))

### Changed
- **Project Reorganization**: Python best practices directory structure
  - Moved all test files to `tests/unit/` and `tests/integration/`
  - Moved debug utilities to `tests/debug/`
  - Moved build scripts to `scripts/` directory
  - Created proper `__init__.py` files for all directories
- **Code Quality Improvements**:
  - Achieved 100% PEP8 compliance (0 violations)
  - Improved Pylint score to 9.04/10
  - Formatted all code with Black (100-char line limit)
  - Sorted all imports with isort
  - Removed 11 unused imports
  - Fixed 347 whitespace violations

### Security
- Removed sensitive AWS account ID from git-tracked files
- Added `LAMBDA_LAYER_IMPLEMENTATION.md` to `.gitignore`
- Verified no credentials or API keys in repository

### Fixed
- Line ending consistency issues (CRLF/LF)
- Import organization and formatting
- Test fixture paths and organization

## [1.0.0] - 2025-12-10

### Added
- 277CA parser with manual segment parsing for claim acknowledgments
- Claim Reconciliation Engine (`src/core/reconciliation.py`)
  - Track claim status changes over time
  - Identify claims stuck in specific states
  - Calculate rejection rates and revenue impact
  - Support for 277/277CA/835 integration
- Comprehensive 277CA test suite with HDI sample files

### Changed
- Enhanced parser architecture to support 277CA format
- Improved segment parsing logic for complex hierarchies

## [0.9.0] - 2025-12-01

### Added
- Initial release with X12 277 and 835 parsers
- AWS Lambda handler with S3 input/output
- Terraform infrastructure as code
- Local and S3 input handlers
- Comprehensive error handling and logging
- Type hints and Pydantic models
- Unit and integration test suite

### Infrastructure
- AWS Lambda deployment with CloudWatch logging
- S3 bucket for input/output files
- X-Ray tracing integration
- SQS for async processing
- Terraform configuration for AWS resources

## Version History Summary

| Version | Date | Key Features |
|---------|------|-------------|
| **v1.1.0** | 2025-12-15 | PEP8 compliance, 277CA parser, Reconciliation engine, Lambda Layers |
| **v1.0.0** | 2025-12-10 | 277CA parser, Claim reconciliation |
| **v0.9.0** | 2025-12-01 | Initial release: 277/835 parsers, AWS Lambda |

## Migration Guide

### From v1.0.0 to v1.1.0

#### File Paths Changed
```bash
# Old paths
python main.py
python lambda/build_layer.py
test_277ca.py

# New paths
python scripts/main.py
python scripts/build_layer.py
pytest tests/integration/test_277ca.py
```

#### Test Commands Updated
```bash
# Old
pytest

# New - Run all tests
pytest tests/

# New - Run specific test types
pytest tests/unit/        # Unit tests only
pytest tests/integration/ # Integration tests only
```

#### Import Paths (unchanged)
```python
# All imports remain the same
from src.parsers.x12_277ca_parser import X12_277CA_Parser
from src.core.reconciliation import ClaimReconciliationEngine
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing to this project.

## Links

- [GitHub Repository](https://github.com/TangoIndiaPapa/x12-edi-processor)
- [Documentation](README.md)
- [Quick Start Guide](QUICKSTART.md)
- [Project Structure](PROJECT_REORGANIZATION.md)
- [Python Best Practices Review](PYTHON_BEST_PRACTICES_REVIEW.md)
