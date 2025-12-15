"""Simple test to verify basic imports and functionality."""

import sys
print(f"Python version: {sys.version}")
print(f"Python version info: {sys.version_info}")

# Test basic imports
try:
    import pydantic
    print(f"✓ Pydantic version: {pydantic.VERSION}")
except Exception as e:
    print(f"✗ Pydantic import failed: {e}")

try:
    import boto3
    print(f"✓ boto3 version: {boto3.__version__}")
except Exception as e:
    print(f"✗ boto3 import failed: {e}")

try:
    import linuxforhealth.x12
    print(f"✓ linuxforhealth-x12 imported successfully")
except Exception as e:
    print(f"✗ linuxforhealth-x12 import failed: {e}")

print("\nNote: linuxforhealth-x12 and pydantic v1 are not fully compatible with Python 3.14")
print("Recommended: Use Python 3.10-3.12 for this project")
