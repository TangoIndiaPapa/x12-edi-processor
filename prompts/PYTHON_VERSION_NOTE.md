# Python Version Compatibility

## Issue
This project uses `linuxforhealth-x12` version 0.57.0, which depends on Pydantic v1.x. Both of these libraries have compatibility issues with **Python 3.14**:

1. **Pydantic v1**: Shows warning "Core Pydantic V1 functionality isn't compatible with Python 3.14 or greater"
2. **linuxforhealth-x12**: Uses field constraints (`regex`) that are not enforced in Pydantic v1 with Python 3.14

## Error
```
ValueError: On field "x12_character_set" the following field constraints are set but not enforced: regex.
```

## Recommended Solution

### Option 1: Use Python 3.10-3.12 (Recommended)
Download and install Python 3.10, 3.11, or 3.12 from [python.org](https://www.python.org/downloads/).

**Why?**
- Full compatibility with linuxforhealth-x12 and pydantic v1
- All features work as expected
- No warnings or errors

### Option 2: Continue with Python 3.14 (Limited Functionality)
You can continue with Python 3.14, but expect:
- Warning messages from pydantic
- Potential runtime issues with X12 parsing
- Not recommended for production use

## Current Environment
- Python Version: 3.14.2
- Pydantic Version: 1.10.24
- linuxforhealth-x12 Version: 0.57.0

## Next Steps
1. **For Development**: Install Python 3.11 (most stable for this stack)
2. **For Production**: Use Python 3.11 in your AWS Lambda runtime (see `lambda/template.yaml`)
3. Update your virtual environment to use the correct Python version

## Lambda Configuration
The `lambda/template.yaml` is already configured to use Python 3.11:
```yaml
Runtime: python3.11
```

This ensures production deployments use a compatible Python version even if your local development uses 3.14.
