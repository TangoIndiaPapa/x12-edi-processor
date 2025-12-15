# Contributing to X12 EDI Processing Platform

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd vscworkspace
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
- Write unit tests for all new features
- Maintain or improve code coverage
- Run tests before submitting PR

```bash
pytest tests/
```

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
   pytest
   black src/
   isort src/
   ```

4. Push and create PR
   ```bash
   git push origin feature/your-feature-name
   ```

## Project Structure Guidelines

- **src/core**: Core configuration and utilities
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
