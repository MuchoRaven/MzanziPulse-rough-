"""
FunctionGraph Function: Get Wallet Balance
Endpoint: GET /balance/{business_id}
Returns current cash wallet balance for a business

FLOW:
User → API Gateway → This Function → OBS (download DB) → Query → Response
"""

import json
import sqlite3
import os

# Import our helper (will be uploaded with the function)
from obs_helper import OBSDatabaseManager

def handler(event, context):
    """
    Main handler function called by FunctionGraph
    
    WHAT IT DOES:
    1. Extracts business_id from request
    2. Downloads database from OBS
    3. Queries wallet balance
    4. Returns balance as JSON
    
    Example Request:
        GET /balance/1
    
    Example Response:
        {
            "business_id": 1,
            "balance": 7500.00,
            "cash": 7450.00,
            "digital": 50.00,
            "credit_owed": 0.00
        }
    """
    
    print("=" * 80)
    print("🏦 Get Balance Function Started")
    print("=" * 80)
    
    try:
        # ====================================================================
        # STEP 1: Parse Request
        # ====================================================================
        
        # FunctionGraph passes business_id in path parameters
        # Example: /balance/1 → pathParameters = {"business_id": "1"}
        
        path_params = event.get('pathParameters', {})
        business_id = path_params.get('business_id')
        
        if not business_id:
            # No business_id provided = bad request
            return {
                'statusCode': 400,  # HTTP 400 = Bad Request
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'error': 'Missing business_id',
                    'message': 'Please provide business_id in URL: /balance/{business_id}'
                })
            }
        
        print(f"📋 Request for business_id: {business_id}")
        
        # ====================================================================
        # STEP 2: Download Database from OBS
        # ====================================================================
        
        # Get credentials from environment variables
        # (We'll set these in FunctionGraph console)
        obs_manager = OBSDatabaseManager(
            access_key_id=os.environ.get('OBS_ACCESS_KEY'),
            secret_access_key=os.environ.get('OBS_SECRET_KEY'),
            bucket_name=os.environ.get('OBS_BUCKET_NAME', 'mzansipulse-data')
        )
        
        # Download database to temporary location
        db_path = obs_manager.download_database()
        
        # ====================================================================
        # STEP 3: Query Database
        # ====================================================================
        
        print(f"🔍 Querying wallet for business_id: {business_id}")
        
        # Connect to SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Query wallet data
        cursor.execute('''
            SELECT 
                w.wallet_id,
                w.virtual_balance_cents,
                w.cash_on_hand_cents,
                w.digital_balance_cents,
                w.credit_given_cents,
                w.last_updated,
                b.business_name,
                u.first_name
            FROM cash_wallets w
            JOIN businesses b ON w.business_id = b.business_id
            JOIN users u ON b.user_id = u.user_id
            WHERE w.business_id = ?
        ''', (business_id,))
        
        result = cursor.fetchone()
        
        conn.close()
        
        # ====================================================================
        # STEP 4: Handle Response
        # ====================================================================
        
        if not result:
            # Business not found
            obs_manager.cleanup(db_path)  # Clean up temp file
            
            return {
                'statusCode': 404,  # HTTP 404 = Not Found
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'error': 'Business not found',
                    'business_id': business_id
                })
            }
        
        # Unpack result
        wallet_id, balance_cents, cash_cents, digital_cents, credit_cents, last_updated, business_name, owner = result
        
        # Convert cents to Rands (divide by 100)
        response_data = {
            'business_id': int(business_id),
            'business_name': business_name,
            'owner': owner,
            'balance': {
                'total': balance_cents / 100,
                'cash': cash_cents / 100,
                'digital': digital_cents / 100,
                'credit_owed_to_you': credit_cents / 100
            },
            'last_updated': last_updated,
            'currency': 'ZAR'
        }
        
        print(f"✅ Balance retrieved: R{balance_cents/100:,.2f}")
        
        # ====================================================================
        # STEP 5: Cleanup & Return
        # ====================================================================
        
        # Clean up temporary database file
        obs_manager.cleanup(db_path)
        
        print("=" * 80)
        print("✅ Get Balance Function Completed Successfully")
        print("=" * 80)
        
        # Return success response
        return {
            'statusCode': 200,  # HTTP 200 = Success
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'  # Allow web browsers to access
            },
            'body': json.dumps(response_data)
        }
    
    except Exception as e:
        # Something went wrong - return error
        print(f"❌ Error: {str(e)}")
        
        # Try to clean up if db_path was created
        try:
            if 'db_path' in locals():
                obs_manager.cleanup(db_path)
        except:
            pass
        
        return {
            'statusCode': 500,  # HTTP 500 = Internal Server Error
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }