#!/usr/bin/env python3
"""
Build AWS Lambda Layer for Python dependencies.

Lambda Layers are a best practice for separating application code from dependencies.
This provides:
- Faster deployments when only code changes (no need to re-upload dependencies)
- Smaller deployment packages (code-only ZIP is much smaller)
- Ability to share dependencies across multiple Lambda functions
- Better organization and separation of concerns
- Reduced deployment time from ~20MB to ~1-2MB for code changes

Layer Structure:
python/
  boto3/
  botocore/
  linuxforhealth/
  aws_lambda_powertools/
  ... (all other dependencies)

Usage:
    python build_layer.py
    
Output:
    lambda_layer.zip - Ready for deployment as Lambda Layer
"""
import os
import zipfile
from pathlib import Path


def build_lambda_layer():
    """
    Build Lambda Layer ZIP file containing all Python dependencies.
    
    Creates a ZIP with the required directory structure for Lambda Layers:
    - python/ directory at root (required by Lambda)
    - All dependencies placed inside python/
    
    Lambda automatically adds python/ to the Python path, making all
    dependencies importable.
    """
    lambda_dir = Path(__file__).parent
    zip_path = lambda_dir / "lambda_layer.zip"
    package_dir = lambda_dir / "package"
    
    # Verify package directory exists
    if not package_dir.exists():
        raise FileNotFoundError(
            f"Package directory not found: {package_dir}\n"
            "Run: pip install -r requirements.txt -t lambda/package"
        )
    
    # Remove old layer ZIP to ensure fresh build
    if zip_path.exists():
        zip_path.unlink()
    
    # Create Layer ZIP with required python/ directory structure
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Add all dependencies inside python/ directory
        # This is the required structure for Lambda Layers
        for root, dirs, files in os.walk(package_dir):
            # Skip __pycache__ directories to reduce layer size
            dirs[:] = [d for d in dirs if d != '__pycache__']
            
            for file in files:
                # Skip compiled Python files
                if file.endswith('.pyc'):
                    continue
                    
                file_path = Path(root) / file
                # Place inside python/ directory as required by Lambda
                arcname = Path('python') / file_path.relative_to(package_dir)
                zf.write(file_path, arcname)
    
    # Report final layer size
    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"\nCreated Lambda Layer: {zip_path.name}")
    print(f"Size: {size_mb:.2f} MB")
    print(f"\nDeploy with:")
    print(f"  aws lambda publish-layer-version \\")
    print(f"    --layer-name x12-edi-processor-dependencies \\")
    print(f"    --zip-file fileb://{zip_path.name} \\")
    print(f"    --compatible-runtimes python3.12")


if __name__ == "__main__":
    build_lambda_layer()
