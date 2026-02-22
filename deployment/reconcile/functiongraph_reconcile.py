"""
FunctionGraph Function: Weekly Reconciliation
Endpoint: POST /reconcile
Handles Friday cash counting
"""

import json
import sqlite3
import os
from datetime import datetime

from obs_helper import OBSDatabaseManager

def handler(event, context):
    """
    Perform weekly cash reconciliation
    
    Request Body:
    {
        "wallet_id": 1,
        "declared_balance": 7500.00,
        "reason": "Personal withdrawal R300 forgot to log"
    }
    
    Response:
    {
        "status": "success",
        "difference": -300.00,
        "accuracy": "96.2%",
        "message": "Thank you for being honest!"
    }
    """
    
    print("=" * 80)
    print("📊 Reconciliation Function Started")
    print("=" * 80)
    
    db_path = None
    obs_manager = None
    
    try:
        # Parse request
        body = event.get('body', '{}')
        if isinstance(body, str):
            body = json.loads(body)
        
        wallet_id = body.get('wallet_id')
        declared_balance = body.get('declared_balance')
        reason = body.get('reason', '')
        
        if not wallet_id or declared_balance is None:
            return error_response(400, "Missing wallet_id or declared_balance")
        
        declared_cents = int(float(declared_balance) * 100)
        
        # Download database
        obs_manager = OBSDatabaseManager(
            access_key_id=os.environ.get('OBS_ACCESS_KEY'),
            secret_access_key=os.environ.get('OBS_SECRET_KEY'),
            bucket_name=os.environ.get('OBS_BUCKET_NAME', 'mzansipulse-data')
        )
        db_path = obs_manager.download_database()
        
        # Get system balance
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT virtual_balance_cents, reconciliation_count,
                   accurate_reconciliations
            FROM cash_wallets
            WHERE wallet_id = ?
        ''', (wallet_id,))
        
        wallet_data = cursor.fetchone()
        
        if not wallet_data:
            conn.close()
            return error_response(404, "Wallet not found")
        
        system_balance, recon_count, accurate_count = wallet_data
        
        # Calculate difference
        difference = declared_cents - system_balance
        difference_pct = abs((difference / system_balance) * 100) if system_balance > 0 else 0
        is_accurate = difference_pct <= 5.0  # 5% tolerance
        
        # Update stats
        new_count = recon_count + 1
        new_accurate = accurate_count + (1 if is_accurate else 0)
        new_accuracy_pct = (new_accurate / new_count) * 100
        
        # Save reconciliation
        cursor.execute('''
            INSERT INTO reconciliations (
                wallet_id, system_balance_cents, declared_balance_cents,
                difference_cents, difference_percentage, is_accurate,
                discrepancy_reason, reconciliation_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            wallet_id, system_balance, declared_cents,
            difference, difference_pct, 1 if is_accurate else 0,
            reason, datetime.now().strftime('%Y-%m-%d')
        ))
        
        # Update wallet
        cursor.execute('''
            UPDATE cash_wallets
            SET virtual_balance_cents = ?,
                last_reconciliation_date = ?,
                reconciliation_count = ?,
                accurate_reconciliations = ?,
                accuracy_percentage = ?
            WHERE wallet_id = ?
        ''', (
            declared_cents,
            datetime.now().strftime('%Y-%m-%d'),
            new_count,
            new_accurate,
            new_accuracy_pct,
            wallet_id
        ))
        
        conn.commit()
        conn.close()
        
        # Upload updated database
        obs_manager.upload_database(db_path)
        obs_manager.cleanup(db_path)
        
        # Build response message
        if is_accurate:
            message = f"🎉 Great job! Your records are {100-difference_pct:.1f}% accurate!"
        elif difference < 0:
            message = f"🤔 You have R{abs(difference)/100:.2f} LESS than expected. Personal withdrawal?"
        else:
            message = f"🤔 You have R{difference/100:.2f} MORE than expected. Unlogged sales?"
        
        print(f"✅ Reconciliation complete. Accuracy: {new_accuracy_pct:.1f}%")
        print("=" * 80)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'status': 'success',
                'system_balance': system_balance / 100,
                'declared_balance': declared_cents / 100,
                'difference': difference / 100,
                'accuracy_percentage': round(difference_pct, 2),
                'overall_accuracy': round(new_accuracy_pct, 2),
                'is_accurate': is_accurate,
                'message': message,
                'reconciliation_count': new_count
            })
        }
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        if db_path:
            try:
                obs_manager.cleanup(db_path)
            except:
                pass
        return error_response(500, str(e))


def error_response(status_code: int, message: str) -> dict:
    return {
        'statusCode': status_code,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'error': message})
    }