import json
import re
import sys
from datetime import datetime
from collections import Counter

# Try to import dependencies, provide helpful error if missing
try:
    import requests
except ImportError:
    print("ERROR: requests module not found. Install it: pip install requests")
    sys.exit(1)

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: beautifulsoup4 module not found. Install it: pip install beautifulsoup4")
    sys.exit(1)

def lambda_handler(event, context):
    """
    AWS Lambda function to scrape silver and gold spot prices from APMEX widget.
    Returns JSON with silver and gold prices.
    """
    
    # Handle OPTIONS request for CORS preflight
    if event.get('requestContext', {}).get('http', {}).get('method') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
            },
            'body': ''
        }
    
    # APMEX widget URL
    widget_url = 'https://widgets.apmex.com/widget/spotprice/?w=280&h=180&mtls=GS&arf=False&rint=5&srf=False&tId=1&wId=1'
    
    try:
        print(f"Fetching from: {widget_url}")
        # Fetch the widget page
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        response = requests.get(widget_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        html = response.text
        print(f"Received HTML, length: {len(html)}")
        
        # Parse HTML
        soup = BeautifulSoup(html, 'html.parser')
        print("HTML parsed successfully")
        
        silver_price = 0
        gold_price = 0
        
        # Primary strategy: Look for the spotprice table with class 'spotprice'
        spotprice_table = soup.find('table', class_='spotprice')
        if spotprice_table:
            print("Found spotprice table")
            # Get all rows in the table
            rows = spotprice_table.find_all('tr')
            print(f"Found {len(rows)} rows in table")
            
            for row in rows:
                # Get all cells in the row
                cells = row.find_all(['td', 'th'])
                row_text = row.get_text().lower()
                
                # Look for silver or gold indicators in the row
                if 'silver' in row_text or 'ag' in row_text:
                    # Extract price from this row - look for Bid or Ask price
                    for cell in cells:
                        cell_text = cell.get_text().strip()
                        # Look for price pattern with optional commas: $1,234.56 or $12.34
                        price_match = re.search(r'\$?([\d,]+\.\d{2})', cell_text)
                        if price_match:
                            # Remove commas and convert to float
                            price_str = price_match.group(1).replace(',', '')
                            price = float(price_str)
                            if 10 < price < 200:  # Reasonable silver range
                                silver_price = price
                                print(f"Found silver price in table: {silver_price}")
                                break
                
                if 'gold' in row_text or 'au' in row_text:
                    # Extract price from this row - look for Bid or Ask price
                    for cell in cells:
                        cell_text = cell.get_text().strip()
                        # Look for price pattern with optional commas: $1,234.56 or $12,345.67
                        price_match = re.search(r'\$?([\d,]+\.\d{2})', cell_text)
                        if price_match:
                            # Remove commas and convert to float
                            price_str = price_match.group(1).replace(',', '')
                            price = float(price_str)
                            if 1000 < price < 10000:  # Reasonable gold range
                                gold_price = price
                                print(f"Found gold price in table: {gold_price}")
                                break
            
            # Alternative: If table structure is different, try finding by column headers
            if not silver_price or not gold_price:
                headers = spotprice_table.find_all(['th', 'td'])
                header_texts = [h.get_text().lower() for h in headers]
                
                # Find indices of silver and gold columns
                silver_idx = None
                gold_idx = None
                
                for i, header_text in enumerate(header_texts):
                    if ('silver' in header_text or 'ag' in header_text) and silver_idx is None:
                        silver_idx = i
                    if ('gold' in header_text or 'au' in header_text) and gold_idx is None:
                        gold_idx = i
                
                # If we found column indices, get prices from data rows
                if silver_idx is not None or gold_idx is not None:
                    data_rows = spotprice_table.find_all('tr')[1:]  # Skip header row
                    for row in data_rows:
                        cells = row.find_all(['td', 'th'])
                        if silver_idx is not None and len(cells) > silver_idx:
                            cell_text = cells[silver_idx].get_text().strip()
                            price_match = re.search(r'\$?([\d,]+\.\d{2})', cell_text)
                            if price_match:
                                price_str = price_match.group(1).replace(',', '')
                                price = float(price_str)
                                if 10 < price < 200 and not silver_price:
                                    silver_price = price
                                    print(f"Found silver price from column {silver_idx}: {silver_price}")
                        
                        if gold_idx is not None and len(cells) > gold_idx:
                            cell_text = cells[gold_idx].get_text().strip()
                            price_match = re.search(r'\$?([\d,]+\.\d{2})', cell_text)
                            if price_match:
                                price_str = price_match.group(1).replace(',', '')
                                price = float(price_str)
                                if 1000 < price < 10000 and not gold_price:
                                    gold_price = price
                                    print(f"Found gold price from column {gold_idx}: {gold_price}")
        
        # Fallback: If table not found or prices not extracted, try generic parsing
        if not silver_price or not gold_price:
            print("Table parsing incomplete, trying fallback strategies...")
            
            # Look for any table with spot price data
            all_tables = soup.find_all('table')
            for table in all_tables:
                table_text = table.get_text().lower()
                if 'spot' in table_text or 'price' in table_text:
                    # Try to extract prices from this table
                    cells_with_prices = table.find_all(text=re.compile(r'\d+\.\d{2}'))
                    for price_text in cells_with_prices:
                        price_match = re.search(r'(\d+\.\d{2})', price_text)
                        if price_match:
                            price = float(price_match.group(1))
                            # Check context around the price
                            parent = price_text.parent
                            if parent:
                                parent_text = parent.get_text().lower()
                                if ('silver' in parent_text or 'ag' in parent_text) and 10 < price < 200 and not silver_price:
                                    silver_price = price
                                    print(f"Found silver price in fallback: {silver_price}")
                                elif ('gold' in parent_text or 'au' in parent_text) and 1000 < price < 10000 and not gold_price:
                                    gold_price = price
                                    print(f"Found gold price in fallback: {gold_price}")
        
        print(f"Final parsed prices - Silver: {silver_price}, Gold: {gold_price}")
        
        # Validate we got both prices
        if silver_price <= 0 or gold_price <= 0:
            # Log HTML snippet for debugging
            html_snippet = html[:5000] if len(html) > 5000 else html
            print(f"HTML snippet (first 5000 chars): {html_snippet}")
            # Also log the text content
            text_content = soup.get_text()
            text_snippet = text_content[:2000] if len(text_content) > 2000 else text_content
            print(f"Text content (first 2000 chars): {text_snippet}")
            raise ValueError(f"Failed to parse prices. Silver: {silver_price}, Gold: {gold_price}")
        
        # Validate price ranges are reasonable (expanded ranges)
        if not (10 < silver_price < 200):
            raise ValueError(f"Silver price out of reasonable range: {silver_price}")
        if not (1000 < gold_price < 10000):
            raise ValueError(f"Gold price out of reasonable range: {gold_price}")
        
        result = {
            'success': True,
            'silver': round(silver_price, 2),
            'gold': round(gold_price, 2),
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'source': 'APMEX Widget'
        }
        
        print(f"Returning success: {result}")
        
        # Return JSON response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',  # Allow CORS from any origin
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
            },
            'body': json.dumps(result)
        }
        
    except requests.RequestException as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps({
                'success': False,
                'error': f'Failed to fetch APMEX data: {str(e)}'
            })
        }
    except (ValueError, AttributeError) as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps({
                'success': False,
                'error': f'Failed to parse prices: {str(e)}'
            })
        }
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Unexpected error: {str(e)}")
        print(f"Traceback: {error_trace}")
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps({
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'type': type(e).__name__
            })
        }

