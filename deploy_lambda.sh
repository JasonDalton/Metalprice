#!/bin/bash
# Script to package Lambda function with dependencies

echo "Creating Lambda deployment package..."

# Create a clean directory
rm -rf lambda-package
mkdir lambda-package
cd lambda-package

# Install dependencies
echo "Installing dependencies..."
pip install -r ../requirements.txt -t . --upgrade

# Copy the Lambda function
echo "Copying Lambda function..."
cp ../lambda_function.py .

# Create zip file
echo "Creating zip file..."
zip -r ../lambda-function.zip . -x "*.pyc" "__pycache__/*" "*.dist-info/*"

cd ..
echo "Done! Upload lambda-function.zip to AWS Lambda"
echo ""
echo "To upload:"
echo "1. Go to AWS Lambda Console"
echo "2. Select your function"
echo "3. Upload lambda-function.zip"

