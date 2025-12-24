#!/usr/bin/env python3
"""
Local test script for the Lambda function
"""

import json
from lambda_function import lambda_handler

# Create a mock event (Lambda URL format)
event = {
    'requestContext': {
        'http': {
            'method': 'GET'
        }
    }
}

# Create a mock context (minimal required attributes)
class MockContext:
    def __init__(self):
        self.function_name = "test-function"
        self.memory_limit_in_mb = 128
        self.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test"
        self.aws_request_id = "test-request-id"

context = MockContext()

# Run the Lambda function
print("Testing Lambda function locally...")
print("=" * 60)

try:
    result = lambda_handler(event, context)
    
    print(f"\nStatus Code: {result['statusCode']}")
    print(f"Headers: {json.dumps(result['headers'], indent=2)}")
    
    body = json.loads(result['body'])
    print(f"\nResponse Body:")
    print(json.dumps(body, indent=2))
    
    if body.get('success'):
        print("\n✓ SUCCESS!")
        print(f"  Silver: ${body.get('silver')}")
        print(f"  Gold: ${body.get('gold')}")
    else:
        print("\n✗ FAILED!")
        print(f"  Error: {body.get('error')}")
        
except Exception as e:
    print(f"\n✗ EXCEPTION: {str(e)}")
    import traceback
    traceback.print_exc()

