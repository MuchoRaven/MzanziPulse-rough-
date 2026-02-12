"""
WhatsApp Message Handler
Simulates receiving transaction messages via WhatsApp
"""

import sqlite3
import os
from datetime import datetime
from transaction_parser import MzansiTransactionParser

DB_PATH = os.path.join('..', 'database', 'mzansipulse.db')

class WhatsAppHandler:
    """
    Handles incoming WhatsApp messages and updates cash wallet
    """
    
    def __init__(self):
        self.parser = MzansiTransactionParser()
    
    def process_message(self, phone_number: str, message: str) -> dict:
        """
        Process incoming WhatsApp message
        
        Args:
            phone_number: User's phone (e.g., "0821234567")
            message: Transaction message (e.g., "10 bread R50 cash")
        
        Returns:
            Response dict with confirmation
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Find user and wallet
        cursor.execute('''
            SELECT u.user_id, u.first_name, b.business_id, w.wallet_id,
                   w.virtual_balance_cents
            FROM users u
            JOIN businesses b ON u.user_id = b.user_id
            JOIN cash_wallets w ON b.business_id = w.business_id
            WHERE u.phone_number = ?
        ''', (phone_number,))
        
        user_data = cursor.fetchone()
        
        if not user_data:
            conn.close()
            return {
                'status': 'error',
                'message': 'User not found. Register first!'
            }
        
        user_id, first_name, business_id, wallet_id, current_balance = user_data
        
        # Parse the message
        parsed = self.parser.parse(message)
        
        if not parsed['amount']:
            conn.close()
            return {
                'status': 'error',
                'message': f"❌ Couldn't understand amount. Please try again.\nExample: '20 bread R50 cash'"
            }
        
        # Determine transaction type and update balance
        amount_cents = int(parsed['amount'] * 100)
        
        # Determine if money coming in or going out
        if parsed['transaction_type'] == 'SALE':
            trans_type = 'CASH_IN' if parsed['payment_method'] == 'CASH' else 'DIGITAL_IN'
            new_balance = current_balance + amount_cents
        elif parsed['transaction_type'] == 'PURCHASE':
            trans_type = 'CASH_OUT'
            new_balance = current_balance - amount_cents
        else:
            trans_type = 'CASH_IN'  # Default
            new_balance = current_balance + amount_cents
        
        # Save to cash_transactions
        cursor.execute('''
            INSERT INTO cash_transactions (
                wallet_id, transaction_type, amount_cents, payment_method,
                source_destination, balance_before_cents, balance_after_cents,
                transaction_date, transaction_time, recorded_method, verified
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            1
        ))
        
        # Update wallet balance
        if trans_type in ['CASH_IN', 'CASH_OUT']:
            cursor.execute('''
                UPDATE cash_wallets
                SET virtual_balance_cents = ?,
                    cash_on_hand_cents = ?,
                    last_updated = ?
                WHERE wallet_id = ?
            ''', (new_balance, new_balance, datetime.now().isoformat(), wallet_id))
        else:  # DIGITAL_IN
            cursor.execute('''
                UPDATE cash_wallets
                SET virtual_balance_cents = ?,
                    digital_balance_cents = digital_balance_cents + ?,
                    last_updated = ?
                WHERE wallet_id = ?
            ''', (new_balance, amount_cents, datetime.now().isoformat(), wallet_id))
        
        conn.commit()
        conn.close()
        
        # Build response message
        emoji = "💵" if trans_type in ['CASH_IN', 'CASH_OUT'] else "💳"
        direction = "+" if "IN" in trans_type else "-"
        
        response = f"""✅ Transaction Recorded!

{emoji} Amount: {direction}R{parsed['amount']:.2f}
📂 Category: {parsed['category']}
💰 New Balance: R{new_balance/100:,.2f}

Keep it up, {first_name}! 🌟"""
        
        return {
            'status': 'success',
            'message': response,
            'balance': new_balance / 100,
            'transaction_type': trans_type
        }


# ============================================================================
# DEMO: Simulate WhatsApp Conversations
# ============================================================================

def demo_whatsapp_integration():
    """
    Simulate WhatsApp message exchange
    """
    print("=" * 80)
    print("📱 WhatsApp Integration - DEMO")
    print("=" * 80)
    
    handler = WhatsAppHandler()
    
    # ========================================================================
    # SCENARIO 1: Mama Thandi logs a sale
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("SCENARIO 1: Mama Thandi logs cash sale via WhatsApp")
    print("=" * 80)
    
    print("\n📱 WhatsApp Message:")
    print("   From: 0821234567 (Mama Thandi)")
    print("   Message: '15 bread R75 cash'")
    
    result = handler.process_message('0821234567', '15 bread R75 cash')
    
    print("\n🤖 MzansiPulse Response:")
    print("─" * 80)
    print(result['message'])
    print("─" * 80)
    
    # ========================================================================
    # SCENARIO 2: Thabo logs eWallet payment
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("SCENARIO 2: Thabo receives eWallet payment")
    print("=" * 80)
    
    print("\n📱 WhatsApp Message:")
    print("   From: 0837654321 (Thabo)")
    print("   Message: 'trouser hemming R60 ewallet capitec'")
    
    result = handler.process_message('0837654321', 'trouser hemming R60 ewallet capitec')
    
    print("\n🤖 MzansiPulse Response:")
    print("─" * 80)
    print(result['message'])
    print("─" * 80)
    
    # ========================================================================
    # SCENARIO 3: Stock purchase
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("SCENARIO 3: Mama Thandi buys stock")
    print("=" * 80)
    
    print("\n📱 WhatsApp Message:")
    print("   From: 0821234567 (Mama Thandi)")
    print("   Message: 'stock from makro R500 cash izolo'")
    
    result = handler.process_message('0821234567', 'stock from makro R500 cash izolo')
    
    print("\n🤖 MzansiPulse Response:")
    print("─" * 80)
    print(result['message'])
    print("─" * 80)
    
    # ========================================================================
    # SCENARIO 4: Error handling - unclear message
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("SCENARIO 4: Unclear message (error handling)")
    print("=" * 80)
    
    print("\n📱 WhatsApp Message:")
    print("   From: 0821234567 (Mama Thandi)")
    print("   Message: 'sold some stuff'")
    
    result = handler.process_message('0821234567', 'sold some stuff')
    
    print("\n🤖 MzansiPulse Response:")
    print("─" * 80)
    print(result['message'])
    print("─" * 80)
    
    print("\n" + "=" * 80)
    print("✅ WhatsApp Integration Demo Complete!")
    print("=" * 80)
    print("\n💡 In production, this would:")
    print("   • Connect to WhatsApp Business API")
    print("   • Process messages in real-time")
    print("   • Send responses automatically")
    print("   • Handle multiple users simultaneously")
    print("=" * 80)

if __name__ == "__main__":
    demo_whatsapp_integration()