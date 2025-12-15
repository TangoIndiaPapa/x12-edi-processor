#!/usr/bin/env python3
"""
Build AWS Lambda deployment package for X12 EDI processor.

**BEST PRACTICE**: This now builds a CODE-ONLY package for use with Lambda Layers.
Dependencies are deployed separately as a Lambda Layer, which provides:
- Faster deployments when only code changes (~1-2MB vs ~20MB)
- Separation of concerns (code vs dependencies)
- Ability to share dependencies across multiple Lambda functions
- Reduced deployment time and costs

This script creates a deployment-ready ZIP file containing ONLY:
- Application source code from src/ directory

Dependencies are handled by the Lambda Layer (see build_layer.py).

Usage:
    python build_zip.py
    
Output:
    lambda_function.zip - Code-only package for AWS Lambda (~1-2MB)
"""
import os
import zipfile
from pathlib import Path

def build_lambda_zip():
    """
    Build Lambda deployment ZIP file with CODE ONLY.
    
    **BEST PRACTICE**: Dependencies are deployed as a Lambda Layer separately.
    This creates a much smaller deployment package (~1-2MB) containing only:
    - Application source code from src/
    
    The resulting structure allows Lambda to import modules correctly:
    - src/handlers/lambda_handler.py (Lambda handler)
    - src/parsers/ (X12 parsers)
    - src/core/ (configuration and utilities)
    - src/input/ (input handlers)
    
    Dependencies (boto3, linuxforhealth, aws_lambda_powertools, etc.) are
    provided by the Lambda Layer and do not need to be in this package.
    """
    # Determine paths relative to this script
    lambda_dir = Path(__file__).parent
    project_dir = lambda_dir.parent
    zip_path = lambda_dir / "lambda_function.zip"
    
    # Remove old ZIP to ensure fresh build (avoid stale code issues)
    if zip_path.exists():
        zip_path.unlink()
    
    # Create ZIP with compression for smaller deployment package
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Add application source code from src/ directory
        # Structure: src/handlers/, src/parsers/, src/core/, src/input/
        src_dir = project_dir / "src"
        for root, dirs, files in os.walk(src_dir):
            # Skip __pycache__ directories to avoid bytecode files
            # Modified in-place to prevent os.walk from descending into them
            dirs[:] = [d for d in dirs if d != '__pycache__']
            
            for file in files:
                # Skip compiled Python files (.pyc)
                if file.endswith('.pyc'):
                    continue
                    
                file_path = Path(root) / file
                # Preserve src/ directory structure in ZIP
                arcname = file_path.relative_to(project_dir)
                zf.write(file_path, arcname)
                print(f"Added: {arcname}")
    
    # Report final package size
    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"\nCreated {zip_path.name}: {size_mb:.2f} MB (code only)")
    print(f"\nNote: This package requires the Lambda Layer with dependencies.")
    print(f"Build layer with: python build_layer.py")

if __name__ == "__main__":
    build_lambda_zip()
