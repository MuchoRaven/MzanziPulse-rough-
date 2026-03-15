"""
Verify Transaction Storage
Check if transactions are actually being saved
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join('..', 'database', 'mzansipulse.db')

print("=" * 80)
print("🔍 Verifying Transaction Storage")
print("=" * 80)

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Check total transactions
cursor.execute("SELECT COUNT(*) as count FROM cash_transactions")
total = cursor.fetchone()['count']
print(f"\n📊 Total transactions in database: {total}")

# Check recent transactions
cursor.execute("""
    SELECT 
        ct.cash_transaction_id,
        ct.transaction_type,
        ct.amount_cents,
        ct.source_destination,
        ct.transaction_date,
        ct.recorded_at,
        b.business_name,
        u.first_name || ' ' || u.last_name as owner
    FROM cash_transactions ct
    JOIN cash_wallets cw ON ct.wallet_id = cw.wallet_id
    JOIN businesses b ON cw.business_id = b.business_id
    JOIN users u ON b.user_id = u.user_id
    ORDER BY ct.recorded_at DESC
    LIMIT 10
""")

print("\n📝 Last 10 transactions:")
print("-" * 80)
for row in cursor.fetchall():
    print(f"ID: {row['cash_transaction_id']}")
    print(f"Business: {row['business_name']}")
    print(f"Owner: {row['owner']}")
    print(f"Type: {row['transaction_type']}")
    print(f"Amount: R{row['amount_cents']/100:.2f}")
    print(f"Description: {row['source_destination']}")
    print(f"Date: {row['transaction_date']}")
    print(f"Recorded: {row['recorded_at']}")
    print("-" * 80)

# Check by user
cursor.execute("""
    SELECT 
        u.user_id,
        u.first_name || ' ' || u.last_name as name,
        COUNT(ct.cash_transaction_id) as transaction_count
    FROM users u
    LEFT JOIN businesses b ON u.user_id = b.user_id
    LEFT JOIN cash_wallets cw ON b.business_id = cw.business_id
    LEFT JOIN cash_transactions ct ON cw.wallet_id = ct.wallet_id
    GROUP BY u.user_id
    ORDER BY transaction_count DESC
""")

print("\n👥 Transactions per user:")
for row in cursor.fetchall():
    print(f"   User {row['user_id']} ({row['name']}): {row['transaction_count']} transactions")

conn.close()

print("\n" + "=" * 80)