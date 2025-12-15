# Test Organization

This directory contains all tests for the X12 EDI processor, organized by type.

## Directory Structure

```
tests/
├── __init__.py
├── conftest.py              # Pytest configuration and fixtures
├── fixtures/                # Test data files
│   ├── 277ca_rejections.x12
│   ├── 277_claim_level_status.x12
│   ├── 835_managed_care.x12
│   └── hdi_samples/        # Healthcare Data Insight sample files
├── unit/                    # Unit tests for individual components
│   ├── test_parsers.py
│   └── test_input_handlers.py
├── integration/             # Integration tests with real files
│   ├── test_277ca.py       # 277CA parser integration tests
│   ├── test_hdi_samples.py # HDI sample file tests
│   ├── test_manual.py      # Manual verification tests
│   └── test_simple.py      # Simple import/functionality tests
└── debug/                   # Debug utilities (not run by pytest)
    ├── debug_parser.py     # Debug parser logic
    └── debug_277ca.py      # Debug 277CA parsing

```

## Running Tests

### All Unit Tests
```bash
pytest tests/unit/
```

### All Integration Tests
```bash
pytest tests/integration/
```

### Specific Test File
```bash
pytest tests/unit/test_parsers.py -v
```

### With Coverage
```bash
pytest --cov=src --cov-report=html
```

## Test Categories

- **Unit Tests** (`tests/unit/`): Fast, isolated tests for individual functions/classes
- **Integration Tests** (`tests/integration/`): Tests with real X12 files and multiple components
- **Debug Scripts** (`tests/debug/`): Helper scripts for troubleshooting (not pytest tests)

## Fixtures

Test data files are stored in `tests/fixtures/`:
- Standard X12 EDI files for common scenarios
- HDI (Healthcare Data Insight) sample files
- Edge cases and error conditions
