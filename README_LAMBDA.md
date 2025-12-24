# AWS Lambda Function for APMEX Price Scraping

This Lambda function scrapes silver and gold spot prices from the APMEX widget and returns them as JSON.

## Setup Instructions

### 1. Create Lambda Function

1. Go to AWS Lambda Console
2. Create a new function
3. Choose "Author from scratch"
4. Runtime: Python 3.11 or 3.12
5. Architecture: x86_64

### 2. Install Dependencies

Since Lambda doesn't include `requests` and `beautifulsoup4` by default, you need to package them:

**Option A: Using Lambda Layers (Easier)**
- Search for public layers that include requests and beautifulsoup4
- Or create your own layer (see below)

**Option B: Package Dependencies (Recommended)**

1. Create a directory structure:
```bash
mkdir lambda-package
cd lambda-package
```

2. Install dependencies:
```bash
pip install -r requirements.txt -t .
```

3. Copy your lambda function:
```bash
cp lambda_function.py .
```

4. Create a zip file:
```bash
zip -r lambda-function.zip .
```

5. Upload the zip to Lambda:
   - In Lambda console, go to your function
   - Upload the zip file

### 3. Configure Lambda

1. **Handler**: `lambda_function.lambda_handler`
2. **Timeout**: Set to at least 10 seconds (recommended: 30 seconds)
3. **Memory**: 128 MB should be sufficient
4. **Environment variables**: None required

### 4. Set up API Gateway (Optional but Recommended)

To call this from your frontend:

1. Create a new API Gateway REST API
2. Create a new resource and method (GET)
3. Enable CORS
4. Connect it to your Lambda function
5. Deploy the API
6. Copy the API endpoint URL

### 5. Update Frontend

Update your `index.html` to call the Lambda endpoint instead of trying to scrape directly:

```javascript
async function fetchPricesFromAPMEX() {
    const lambdaUrl = 'YOUR_API_GATEWAY_ENDPOINT_URL';
    
    const response = await fetch(lambdaUrl);
    if (!response.ok) {
        throw new Error(`Lambda error: ${response.status}`);
    }
    
    const data = await response.json();
    
    if (!data.success) {
        throw new Error(data.error);
    }
    
    return {
        silverPrice: data.silver,
        goldPrice: data.gold
    };
}
```

## Testing

You can test the Lambda function directly in the AWS Console:

1. Go to your Lambda function
2. Click "Test"
3. Create a test event (empty JSON `{}` is fine)
4. Run the test

## Response Format

Success response:
```json
{
    "success": true,
    "silver": 24.50,
    "gold": 2050.75,
    "timestamp": "2024-01-15T12:00:00Z",
    "source": "APMEX Widget"
}
```

Error response:
```json
{
    "success": false,
    "error": "Error message here"
}
```

## Notes

- The function includes CORS headers so it can be called from your frontend
- The function validates price ranges to ensure reasonable values
- If APMEX changes their HTML structure, you may need to update the parsing logic
- Consider adding CloudWatch alarms for monitoring

