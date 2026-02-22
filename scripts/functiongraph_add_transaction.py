"""
FunctionGraph Function: Add Transaction
Endpoint: POST /transaction
Receives WhatsApp message and records transaction

FLOW:
WhatsApp → API Gateway → This Function → Parse Message → Save to DB → Response
"""

import json
import sqlite3
import os
from datetime import datetime

from obs_helper import OBSDatabaseManager
from transaction_parser import MzansiTransactionParser
from whatsapp_handler import WhatsAppHandler

def handler(event, context):
    """
    Add a new transaction from WhatsApp message
    
    Request Body (JSON):
    {
        "phone_number": "0821234567",
        "message": "10 bread R50 cash today"
    }
    
    Response (JSON):
    {
        "status": "success",
        "message": "✅ Transaction saved! Balance: R7,550",
        "transaction_id": 253,
        "new_balance": 7550.00
    }
    """
    
    print("=" * 80)
    print("📱 Add Transaction Function Started")
    print("=" * 80)
    
    db_path = None
    obs_manager = None
    
    try:
        # ====================================================================
        # STEP 1: Parse Request Body
        # ====================================================================
        
        # Get request body
        body = event.get('body', '{}')
        
        # Body might be a string or dict
        if isinstance(body, str):
            body = json.loads(body)
        
        # Extract required fields
        phone_number = body.get('phone_number')
        message = body.get('message')
        
        # Validate inputs
        if not phone_number:
            return error_response(400, "Missing phone_number in request body")
        
        if not message:
            return error_response(400, "Missing message in request body")
        
        print(f"📱 From: {phone_number}")
        print(f"💬 Message: {message}")
        
        # ====================================================================
        # STEP 2: Download Database
        # ====================================================================
        
        obs_manager = OBSDatabaseManager(
            access_key_id=os.environ.get('OBS_ACCESS_KEY'),
            secret_access_key=os.environ.get('OBS_SECRET_KEY'),
            bucket_name=os.environ.get('OBS_BUCKET_NAME', 'mzansipulse-data')
        )
        
        db_path = obs_manager.download_database()
        
        # ====================================================================
        # STEP 3: Find User by Phone Number
        # ====================================================================
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.user_id, u.first_name, u.preferred_language,
                   b.business_id, w.wallet_id, w.virtual_balance_cents
            FROM users u
            JOIN businesses b ON u.user_id = b.user_id
            JOIN cash_wallets w ON b.business_id = w.business_id
            WHERE u.phone_number = ?
        ''', (phone_number,))
        
        user_data = cursor.fetchone()
        
        if not user_data:
            conn.close()
            return error_response(404, f"User {phone_number} not registered in MzansiPulse")
        
        user_id, first_name, language, business_id, wallet_id, current_balance = user_data
        
        # ====================================================================
        # STEP 4: Parse WhatsApp Message
        # ====================================================================
        
        parser = MzansiTransactionParser()
        parsed = parser.parse(message)
        
        print(f"✅ Parsed: Amount=R{parsed.get('amount')}, Category={parsed.get('category')}")
        
        if not parsed.get('amount'):
            conn.close()
            obs_manager.cleanup(db_path)
            
            # User-friendly response in their language
            if language == 'zu':
                response_msg = "❌ Angizwanga inani. Zama futhi: '10 bread R50 cash'"
            elif language == 'st':
                response_msg = "❌ Ha ke utlwisise palo. Leka hape: '10 bread R50 cash'"
            else:
                response_msg = "❌ Couldn't find amount. Try: '10 bread R50 cash'"
            
            return success_response({
                'status': 'error',
                'message': response_msg,
                'example': '10 bread R50 cash today'
            })
        
        # ====================================================================
        # STEP 5: Save Transaction to Database
        # ====================================================================
        
        amount_cents = int(parsed['amount'] * 100)
        
        # Determine balance change
        if parsed['transaction_type'] == 'SALE':
            trans_type = 'CASH_IN' if parsed['payment_method'] == 'CASH' else 'DIGITAL_IN'
            new_balance = current_balance + amount_cents
        else:  # PURCHASE
            trans_type = 'CASH_OUT'
            new_balance = max(0, current_balance - amount_cents)
        
        # Save to transactions table
        cursor.execute('''
            INSERT INTO transactions (
                business_id, transaction_date, transaction_type,
                amount, category, description, description_cleaned,
                payment_method, data_source, source_confidence,
                is_verified, flagged_for_review, flag_reason
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            business_id,
            parsed['transaction_date'],
            parsed['transaction_type'],
            parsed['amount'],
            parsed['category'],
            parsed['description_original'],
            parsed['description_cleaned'],
            parsed['payment_method'],
            'WHATSAPP',
            parsed['source_confidence'],
            0,
            1 if parsed['flagged_for_review'] else 0,
            parsed.get('flag_reason')
        ))
        
        transaction_id = cursor.lastrowid
        
        # Save to cash_transactions table
        cursor.execute('''
            INSERT INTO cash_transactions (
                wallet_id, transaction_type, amount_cents, payment_method,
                source_destination, balance_before_cents, balance_after_cents,
                transaction_date, transaction_time, recorded_method,
                verified, linked_transaction_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            wallet_id,
            trans_type,
            amount_cents,
            parsed['payment_method'],
            parsed['description_cleaned'],
            current_balance,
            new_balance,
            parsed['transaction_date'],
            datetime.now().strftime('%H:%M:%S'),
            'WHATSAPP',
            1,
            transaction_id
        ))
        
        # Update wallet balance
        cursor.execute('''
            UPDATE cash_wallets
            SET virtual_balance_cents = ?,
                last_updated = ?
            WHERE wallet_id = ?
        ''', (new_balance, datetime.now().isoformat(), wallet_id))
        
        conn.commit()
        conn.close()
        
        # ====================================================================
        # STEP 6: Upload Updated Database
        # ====================================================================
        
        obs_manager.upload_database(db_path)
        obs_manager.cleanup(db_path)
        
        # ====================================================================
        # STEP 7: Build Multilingual Response
        # ====================================================================
        
        direction = "+" if "IN" in trans_type else "-"
        
        if language == 'zu':
            response_msg = f"""✅ Kulondolozwe!
💰 Inani: {direction}R{parsed['amount']:.2f}
📊 Ibhalansi entsha: R{new_balance/100:,.2f}
Qhubeka, {first_name}! 🌟"""
        elif language == 'st':
            response_msg = f"""✅ Ho bolokilwe!
💰 Chelete: {direction}R{parsed['amount']:.2f}
📊 Tefo e ntjha: R{new_balance/100:,.2f}
Tswela pele, {first_name}! 🌟"""
        else:
            response_msg = f"""✅ Transaction Recorded!
💰 Amount: {direction}R{parsed['amount']:.2f}
📂 Category: {parsed['category']}
💰 New Balance: R{new_balance/100:,.2f}
Keep it up, {first_name}! 🌟"""
        
        print("=" * 80)
        print("✅ Add Transaction Function Completed!")
        print("=" * 80)
        
        return success_response({
            'status': 'success',
            'message': response_msg,
            'transaction_id': transaction_id,
            'amount': parsed['amount'],
            'category': parsed['category'],
            'new_balance': new_balance / 100
        })
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        
        if db_path:
            try:
                obs_manager.cleanup(db_path)
            except:
                pass
        
        return error_response(500, str(e))


def success_response(data: dict) -> dict:
    """Helper: Return 200 success response"""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(data)
    }


def error_response(status_code: int, message: str) -> dict:
    """Helper: Return error response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({'error': message})
    }