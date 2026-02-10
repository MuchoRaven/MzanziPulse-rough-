"""
MzansiPulse Transaction Entry System
Uses the parser to clean messages and save to database
"""

import sqlite3
import os
from datetime import datetime
from transaction_parser import MzansiTransactionParser

# Database path
DB_PATH = os.path.join('..', 'database', 'mzansipulse.db')

class TransactionManager:
    """Manages adding transactions to the database"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.parser = MzansiTransactionParser()
    
    def add_transaction(self, business_id: int, message: str, 
                       timestamp: datetime = None) -> dict:
        """
        Parse a message and add it to the database
        
        Args:
            business_id: ID of the business
            message: Raw transaction message
            timestamp: When message was sent (defaults to now)
        
        Returns:
            Dictionary with transaction_id and parsed data
        """
        # Parse the message
        parsed = self.parser.parse(message, timestamp)
        
        # Connect to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert transaction
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
            parsed['data_source'],
            parsed['source_confidence'],
            parsed['is_verified'],
            parsed['flagged_for_review'],
            parsed['flag_reason']
        ))
        
        transaction_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        # Return result
        result = parsed.copy()
        result['transaction_id'] = transaction_id
        result['business_id'] = business_id
        
        return result
    
    def add_batch(self, business_id: int, messages: list) -> list:
        """Add multiple messages at once"""
        results = []
        for msg in messages:
            result = self.add_transaction(business_id, msg)
            results.append(result)
        return results
    
    def get_flagged_transactions(self, business_id: int = None) -> list:
        """Get all transactions that need review"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if business_id:
            cursor.execute('''
                SELECT transaction_id, description, amount, flag_reason
                FROM transactions
                WHERE flagged_for_review = 1 AND business_id = ?
                ORDER BY created_at DESC
            ''', (business_id,))
        else:
            cursor.execute('''
                SELECT transaction_id, description, amount, flag_reason
                FROM transactions
                WHERE flagged_for_review = 1
                ORDER BY created_at DESC
            ''')
        
        results = cursor.fetchall()
        conn.close()
        
        return results


# ============================================================================
# INTERACTIVE DEMO
# ============================================================================

def demo():
    """Interactive demonstration"""
    
    print("=" * 70)
    print("📱 MzansiPulse WhatsApp Transaction Entry - DEMO")
    print("=" * 70)
    
    manager = TransactionManager(DB_PATH)
    
    # Mama Thandi's business ID is 1 (from our test data)
    business_id = 1
    
    print("\n🏪 Business: Mama Thandi's Spaza Shop")
    print("👤 Owner: Thandi Molefe")
    print("\n" + "-" * 70)
    
    # Simulate WhatsApp messages coming in
    whatsapp_messages = [
        "10 bread R150 cash today",
        "airtime mtn R50 paid ewallet",
        "stock makro R2500 yesterday paid cash",
        "milk 5 liters R110",
        "took out R300 for personal use",  # Should be flagged
    ]
    
    print(f"\n📥 Processing {len(whatsapp_messages)} WhatsApp messages...\n")
    
    for i, message in enumerate(whatsapp_messages, 1):
        print(f"MESSAGE {i}: \"{message}\"")
        
        result = manager.add_transaction(business_id, message)
        
        print(f"   ✅ Saved as Transaction #{result['transaction_id']}")
        print(f"   💰 Amount: R{result['amount']}")
        print(f"   📂 Category: {result['category']}")
        print(f"   📊 Confidence: {result['source_confidence']:.0%}")
        
        if result['flagged_for_review']:
            print(f"   ⚠️  FLAGGED: {result['flag_reason']}")
        
        print()
    
    # Show flagged transactions
    print("-" * 70)
    print("\n⚠️  FLAGGED TRANSACTIONS NEEDING REVIEW:")
    print("-" * 70)
    
    flagged = manager.get_flagged_transactions(business_id)
    
    if flagged:
        for trans_id, desc, amount, reason in flagged:
            print(f"\n   Transaction #{trans_id}")
            print(f"   Description: {desc}")
            print(f"   Amount: R{amount}")
            print(f"   Reason: {reason}")
    else:
        print("   None")
    
    # Show transaction count
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM transactions WHERE business_id = ?', (business_id,))
    total = cursor.fetchone()[0]
    conn.close()
    
    print("\n" + "=" * 70)
    print(f"📊 TOTAL TRANSACTIONS IN DATABASE: {total}")
    print("=" * 70)
    print("\n✅ Demo complete! Check DB Browser to see the new transactions.")
    print("=" * 70)


if __name__ == "__main__":
    demo()