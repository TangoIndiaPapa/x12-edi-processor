#!/usr/bin/env python3
"""
Build AWS Lambda deployment package for X12 EDI processor.

This script creates a deployment-ready ZIP file containing:
1. Application source code from src/ directory
2. Python dependencies from lambda/package/ directory

The script was created to avoid PowerShell Compress-Archive caching issues
that caused stale code to be deployed.

Usage:
    python build_zip.py
    
Output:
    lambda_function.zip - Ready for deployment to AWS Lambda
"""
import os
import zipfile
from pathlib import Path

def build_lambda_zip():
    """
    Build Lambda deployment ZIP file.
    
    Creates a fresh ZIP file by:
    1. Removing any existing lambda_function.zip
    2. Adding all source code from src/ with proper structure
    3. Adding all dependencies from package/ to root of ZIP
    4. Excluding Python bytecode files (__pycache__, .pyc)
    
    The resulting structure allows Lambda to import modules correctly:
    - src/handlers/lambda_handler.py (Lambda handler)
    - src/parsers/ (X12 parsers)
    - boto3/, linuxforhealth/, etc. (dependencies at root)
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
        
        # Add Python dependencies from package/ directory
        # These go to the root of the ZIP so Lambda can import them directly
        # Structure: boto3/, linuxforhealth/, aws_lambda_powertools/, etc.
        package_dir = lambda_dir / "package"
        for root, dirs, files in os.walk(package_dir):
            # Skip __pycache__ directories in dependencies too
            dirs[:] = [d for d in dirs if d != '__pycache__']
            
            for file in files:
                # Skip compiled Python files in dependencies
                if file.endswith('.pyc'):
                    continue
                    
                file_path = Path(root) / file
                # Place dependencies at root level of ZIP (no package/ prefix)
                arcname = file_path.relative_to(lambda_dir / "package")
                zf.write(file_path, arcname)
    
    # Report final package size
    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"\nCreated {zip_path.name}: {size_mb:.2f} MB")

if __name__ == "__main__":
    build_lambda_zip()
