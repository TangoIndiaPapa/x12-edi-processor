#!/bin/bash

# AWS SAM build and deployment script for X12 EDI Processor Lambda

set -e

echo "Building X12 EDI Processor Lambda function..."

# Navigate to lambda directory
cd "$(dirname "$0")"

# Build with SAM
echo "Running SAM build..."
sam build

echo "Build complete!"
echo ""
echo "To deploy, run:"
echo "  sam deploy --guided"
echo ""
echo "For subsequent deployments:"
echo "  sam deploy"
