# Scripts Directory

This directory contains utility scripts for building, testing, and managing the X12 EDI processor.

## Build Scripts

- **build_layer.py**: Creates AWS Lambda Layer package with dependencies
- **build_zip.py**: Creates Lambda function deployment package
- **build.sh**: Shell script for building Lambda artifacts

## Utility Scripts

- **main.py**: Main entry point for local testing
- **compare_277_files.py**: Compare and analyze different 277 files

## Usage

### Build Lambda Layer
```bash
python scripts/build_layer.py
```

### Build Lambda Function Package
```bash
python scripts/build_zip.py
```

### Run Local Test
```bash
python scripts/main.py
```
