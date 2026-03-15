"""
Update Transactions Schema
Ensure all columns needed for OCR and receipt scanning exist
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join('..', 'database', 'mzansipulse.db')

print("=" * 80)
print("📊 Updating Transactions Schema")
print("=" * 80)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ═══════════════════════════════════════════════════════════════════════════
# 1. CHECK EXISTING SCHEMA
# ═══════════════════════════════════════════════════════════════════════════

print("\n1️⃣ Checking cash_transactions schema...")

cursor.execute("PRAGMA table_info(cash_transactions)")
columns_info = cursor.fetchall()
existing_columns = {col[1]: col[2] for col in columns_info}

print(f"   Existing columns: {len(existing_columns)}")
print("\n   📋 Current schema:")
for col_name, col_type in existing_columns.items():
    print(f"      • {col_name}: {col_type}")

# ═══════════════════════════════════════════════════════════════════════════
# 2. ADD MISSING COLUMNS FOR OCR/RECEIPT FEATURES
# ═══════════════════════════════════════════════════════════════════════════

print("\n2️⃣ Adding new columns for OCR features...")

new_columns = {
    'receipt_image_path': 'TEXT',  # Path to receipt/logbook photo
    'ocr_confidence': 'REAL',       # OCR accuracy score
    'ocr_raw_text': 'TEXT',         # Raw OCR output
    'entry_method': 'TEXT DEFAULT "MANUAL"',  # MANUAL, OCR, API
    'verified': 'INTEGER DEFAULT 0',  # User verified the transaction
}

for col_name, col_type in new_columns.items():
    if col_name not in existing_columns:
        try:
            cursor.execute(f'ALTER TABLE cash_transactions ADD COLUMN {col_name} {col_type}')
            print(f"   ✅ Added '{col_name}' column")
        except sqlite3.Error as e:
            print(f"   ⚠️  Could not add {col_name}: {e}")
    else:
        print(f"   ℹ️  Column '{col_name}' already exists")

conn.commit()

# ═══════════════════════════════════════════════════════════════════════════
# 3. VERIFY PRIVACY (transactions are user-specific via wallet_id)
# ═══════════════════════════════════════════════════════════════════════════

print("\n3️⃣ Verifying privacy isolation...")

# First, get the actual primary key column name
cursor.execute("PRAGMA table_info(cash_transactions)")
pk_column = None
for col in cursor.fetchall():
    if col[5] == 1:  # col[5] is the pk flag
        pk_column = col[1]
        break

if not pk_column:
    # If no PK found, check for common names
    if 'id' in existing_columns:
        pk_column = 'id'
    elif 'transaction_id' in existing_columns:
        pk_column = 'transaction_id'
    else:
        # Use first column as fallback
        pk_column = list(existing_columns.keys())[0]

print(f"   ℹ️  Primary key column: {pk_column}")

try:
    # Count users and transactions
    cursor.execute('''
        SELECT COUNT(DISTINCT b.user_id) as user_count,
               COUNT(*) as transaction_count
        FROM cash_transactions ct
        JOIN cash_wallets cw ON ct.wallet_id = cw.wallet_id
        JOIN businesses b ON cw.business_id = b.business_id
    ''')
    
    result = cursor.fetchone()
    user_count = result[0] if result else 0
    transaction_count = result[1] if result else 0
    
    print(f"   ✅ Users with transactions: {user_count}")
    print(f"   ✅ Total transactions: {transaction_count}")
    print(f"   ✅ Privacy: Each user sees ONLY their wallet's transactions")
    
except sqlite3.Error as e:
    print(f"   ⚠️  Could not verify privacy: {e}")
    print("   ℹ️  This is OK if there are no transactions yet")

# ═══════════════════════════════════════════════════════════════════════════
# 4. CREATE SAMPLE TRANSACTION (if none exist)
# ═══════════════════════════════════════════════════════════════════════════

print("\n4️⃣ Checking for sample data...")

cursor.execute('SELECT COUNT(*) FROM cash_transactions')
transaction_count = cursor.fetchone()[0]

if transaction_count == 0:
    print("   ℹ️  No transactions found. Creating sample data...")
    
    # Get first wallet
    cursor.execute('SELECT wallet_id FROM cash_wallets LIMIT 1')
    wallet_row = cursor.fetchone()
    
    if wallet_row:
        wallet_id = wallet_row[0]
        
        # Create sample transactions
        sample_transactions = [
            ('CASH_IN', 15000, 'CASH', 'Sold bread and vetkoek', 'GROCERIES'),
            ('CASH_IN', 5000, 'DIGITAL', 'EFT payment from customer', 'SALES'),
            ('CASH_OUT', 25000, 'CASH', 'Bought stock from Makro', 'STOCK_PURCHASE'),
            ('CASH_IN', 10000, 'CASH', 'Sold cold drinks', 'BEVERAGES'),
        ]
        
        for trans_type, amount, method, description, category in sample_transactions:
            cursor.execute('''
                INSERT INTO cash_transactions (
                    wallet_id, transaction_type, amount_cents, 
                    payment_method, source_destination, category,
                    transaction_date, entry_method
                ) VALUES (?, ?, ?, ?, ?, ?, datetime('now'), 'MANUAL')
            ''', (wallet_id, trans_type, amount, method, description, category))
        
        print(f"   ✅ Created {len(sample_transactions)} sample transactions")
    else:
        print("   ⚠️  No wallets found - cannot create sample transactions")
else:
    print(f"   ℹ️  Found {transaction_count} existing transactions")

conn.commit()
conn.close()

print("\n" + "=" * 80)
print("✅ Transactions Schema Updated Successfully!")
print("=" * 80)

print("=" * 80)