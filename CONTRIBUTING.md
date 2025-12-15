# Contributing to X12 EDI Processing Platform

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd x12-edi-processor
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

## Code Standards

### Python Style
- Follow PEP 8 guidelines
- Use type hints for all functions
- Maximum line length: 100 characters
- Use Black for code formatting
- Use isort for import sorting

### Testing
- Write unit tests for all new features in `tests/unit/`
- Add integration tests in `tests/integration/` for end-to-end scenarios
- Maintain or improve code coverage (target: >80%)
- Run tests before submitting PR

```bash
# Run all tests
pytest tests/

# Run unit tests only
pytest tests/unit/ -v

# Run with coverage
pytest --cov=src --cov-report=html
```

See [tests/README.md](tests/README.md) for detailed testing guidelines.

### Documentation
- Add docstrings to all public functions/classes
- Update README.md for significant changes
- Add type hints and clear parameter descriptions

## Pull Request Process

1. Create a feature branch
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit
   ```bash
   git add .
   git commit -m "Description of changes"
   ```

3. Run tests and linters
   ```bash
   # Run tests
   pytest tests/
   
   # Format code
   black src/ tests/
   
   # Sort imports
   isort src/ tests/
   
   # Run linters
   flake8 src/ tests/
   pylint src/
   ```

4. Push and create PR
   ```bash
   git push origin feature/your-feature-name
   ```

## Project Structure Guidelines

- **src/core**: Core configuration, logging, exceptions, and utilities
- **src/parsers**: X12 format parsers (277, 277CA, 835)
- **src/input**: Input handlers (local, S3, upload)
- **src/handlers**: AWS Lambda handlers
- **tests/unit**: Fast, isolated unit tests
- **tests/integration**: Integration tests with real X12 files
- **tests/fixtures**: Test data files (X12 samples)
- **tests/debug**: Debug utilities (not run by pytest)
- **scripts**: Build scripts and utilities
- **lambda**: Lambda deployment artifacts only
- **terraform**: Infrastructure as Code

### File Placement Rules

1. **Source Code** → `src/<module>/`
2. **Unit Tests** → `tests/unit/test_<module>.py`
3. **Integration Tests** → `tests/integration/test_<feature>.py`
4. **Test Data** → `tests/fixtures/`
5. **Build Scripts** → `scripts/`
6. **Debug Tools** → `tests/debug/` (not run automatically)

## Code Quality Standards

### Current Status
- ✅ PEP8 Compliance: 100% (0 violations)
- ✅ Pylint Score: 9.04/10
- ✅ Black Formatted: All files
- ✅ Import Sorting: isort configured
- ✅ Line Length: 100 characters max

### Pre-commit Checklist
- [ ] Code formatted with Black
- [ ] Imports sorted with isort
- [ ] No flake8 violations
- [ ] Tests pass locally
- [ ] Coverage maintained or improved
- [ ] Docstrings added/updated
- [ ] Type hints included
- **src/parsers**: X12 parsing implementations
- **src/input**: Input source handlers
- **src/output**: Output destination handlers
- **src/handlers**: AWS Lambda handlers
- **tests**: Test suite

## Questions or Issues?

Open an issue on GitHub for:
- Bug reports
- Feature requests
- Questions about usage

Thank you for contributing!
