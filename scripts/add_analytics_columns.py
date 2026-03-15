"""
Add Analytics Columns to Database
Adds category and other missing columns for Business Intelligence
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join('..', 'database', 'mzansipulse.db')

print("=" * 80)
print("📊 Adding Analytics Columns to Database")
print("=" * 80)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ═══════════════════════════════════════════════════════════════════════════
# 1. ADD CATEGORY COLUMN TO CASH_TRANSACTIONS
# ═══════════════════════════════════════════════════════════════════════════

print("\n1️⃣ Checking cash_transactions table...")

cursor.execute("PRAGMA table_info(cash_transactions)")
columns = [col[1] for col in cursor.fetchall()]

if 'category' not in columns:
    try:
        cursor.execute('ALTER TABLE cash_transactions ADD COLUMN category TEXT')
        print("   ✅ Added 'category' column to cash_transactions")
    except sqlite3.Error as e:
        print(f"   ⚠️  Could not add category: {e}")
else:
    print("   ℹ️  Column 'category' already exists")

# ═══════════════════════════════════════════════════════════════════════════
# 2. ADD MISSING COLUMNS TO CASH_WALLETS (if needed)
# ═══════════════════════════════════════════════════════════════════════════

print("\n2️⃣ Checking cash_wallets table...")

cursor.execute("PRAGMA table_info(cash_wallets)")
wallet_columns = [col[1] for col in cursor.fetchall()]

wallet_new_columns = {
    'digital_balance_cents': 'INTEGER DEFAULT 0',
    'total_cash_sales_cents': 'INTEGER DEFAULT 0',
    'total_digital_sales_cents': 'INTEGER DEFAULT 0',
    'total_expenses_cents': 'INTEGER DEFAULT 0',
    'reconciliation_count': 'INTEGER DEFAULT 0',
    'accuracy_percentage': 'REAL DEFAULT 100.0',
    'last_reconciliation_date': 'TEXT'
}

for col_name, col_type in wallet_new_columns.items():
    if col_name not in wallet_columns:
        try:
            cursor.execute(f'ALTER TABLE cash_wallets ADD COLUMN {col_name} {col_type}')
            print(f"   ✅ Added '{col_name}' to cash_wallets")
        except sqlite3.Error as e:
            print(f"   ⚠️  Could not add {col_name}: {e}")
    else:
        print(f"   ℹ️  Column '{col_name}' already exists")

conn.commit()

# ═══════════════════════════════════════════════════════════════════════════
# 3. POPULATE CATEGORY BASED ON SOURCE_DESTINATION (Intelligent Categorization)
# ═══════════════════════════════════════════════════════════════════════════

print("\n3️⃣ Populating categories from transaction descriptions...")

# Category mapping based on keywords
category_mapping = [
    # Groceries & Food
    (['bread', 'milk', 'egg', 'sugar', 'flour', 'rice', 'maize', 'mealie', 'pap'], 'GROCERIES'),
    (['chicken', 'meat', 'beef', 'pork', 'fish', 'polony', 'wors'], 'GROCERIES'),
    
    # Airtime & Mobile
    (['airtime', 'data', 'mtn', 'vodacom', 'cell c', 'telkom'], 'AIRTIME'),
    
    # Beverages
    (['coke', 'fanta', 'sprite', 'juice', 'drink', 'soda', 'cool drink'], 'BEVERAGES'),
    (['beer', 'wine', 'alcohol'], 'BEVERAGES'),
    
    # Toiletries & Personal Care
    (['soap', 'shampoo', 'toothpaste', 'lotion', 'vaseline', 'dettol'], 'TOILETRIES'),
    
    # Household
    (['candle', 'matches', 'paraffin', 'cleaning'], 'HOUSEHOLD'),
    
    # Snacks & Treats
    (['chips', 'sweets', 'chocolate', 'biscuit', 'cookie', 'simba'], 'SNACKS'),
    
    # Stock Purchase
    (['makro', 'wholesaler', 'cash and carry', 'massmart', 'stock'], 'STOCK_PURCHASE'),
    
    # Utilities
    (['electricity', 'prepaid', 'eskom'], 'UTILITIES'),
    
    # Cash Book (Credit)
    (['book', 'credit', 'owe', 'debt'], 'CREDIT'),
    
    # Other Sales
    (['sale', 'sold', 'customer'], 'SALES'),
]

# Update categories based on source_destination text
categorized_count = 0
for keywords, category in category_mapping:
    for keyword in keywords:
        cursor.execute('''
            UPDATE cash_transactions 
            SET category = ?
            WHERE category IS NULL 
            AND LOWER(source_destination) LIKE ?
        ''', (category, f'%{keyword}%'))
        categorized_count += cursor.rowcount

print(f"   ✅ Categorized {categorized_count} transactions")

# Set default category for uncategorized transactions
cursor.execute('''
    UPDATE cash_transactions 
    SET category = 'OTHER'
    WHERE category IS NULL OR category = ''
''')

print(f"   ✅ Set default category for {cursor.rowcount} remaining transactions")

conn.commit()

# ═══════════════════════════════════════════════════════════════════════════
# 4. UPDATE WALLET TOTALS (Calculate from transactions)
# ═══════════════════════════════════════════════════════════════════════════

print("\n4️⃣ Calculating wallet totals from transactions...")

cursor.execute('SELECT wallet_id FROM cash_wallets')
wallets = cursor.fetchall()

for wallet_row in wallets:
    wallet_id = wallet_row[0]
    
    # Calculate total cash sales
    cursor.execute('''
        SELECT SUM(amount_cents) 
        FROM cash_transactions 
        WHERE wallet_id = ? 
        AND transaction_type = 'CASH_IN'
    ''', (wallet_id,))
    total_cash_sales = cursor.fetchone()[0] or 0
    
    # Calculate total digital sales
    cursor.execute('''
        SELECT SUM(amount_cents) 
        FROM cash_transactions 
        WHERE wallet_id = ? 
        AND transaction_type = 'DIGITAL_IN'
    ''', (wallet_id,))
    total_digital_sales = cursor.fetchone()[0] or 0
    
    # Calculate total expenses
    cursor.execute('''
        SELECT SUM(amount_cents) 
        FROM cash_transactions 
        WHERE wallet_id = ? 
        AND transaction_type = 'CASH_OUT'
    ''', (wallet_id,))
    total_expenses = cursor.fetchone()[0] or 0
    
    # Update wallet
    cursor.execute('''
        UPDATE cash_wallets 
        SET total_cash_sales_cents = ?,
            total_digital_sales_cents = ?,
            total_expenses_cents = ?
        WHERE wallet_id = ?
    ''', (total_cash_sales, total_digital_sales, total_expenses, wallet_id))
    
    print(f"   ✅ Updated wallet {wallet_id}: Cash Sales R{total_cash_sales/100:.2f}, Digital R{total_digital_sales/100:.2f}, Expenses R{total_expenses/100:.2f}")

conn.commit()

# ═══════════════════════════════════════════════════════════════════════════
# 5. VERIFY CHANGES
# ═══════════════════════════════════════════════════════════════════════════

print("\n5️⃣ Verification:")

# Check categories
cursor.execute('''
    SELECT category, COUNT(*) as count
    FROM cash_transactions
    GROUP BY category
    ORDER BY count DESC
    LIMIT 10
''')

print("\n   📊 Transaction Categories:")
for row in cursor.fetchall():
    print(f"      • {row[0]}: {row[1]} transactions")

# Check wallet totals
cursor.execute('''
    SELECT 
        w.wallet_id,
        w.total_cash_sales_cents,
        w.total_digital_sales_cents,
        w.total_expenses_cents,
        b.business_name
    FROM cash_wallets w
    LEFT JOIN businesses b ON w.business_id = b.business_id
''')

print("\n   💰 Wallet Totals:")
for row in cursor.fetchall():
    wallet_id, cash_sales, digital_sales, expenses, business_name = row
    print(f"      • {business_name or 'Wallet ' + str(wallet_id)}:")
    print(f"        - Cash Sales: R{(cash_sales or 0)/100:.2f}")
    print(f"        - Digital Sales: R{(digital_sales or 0)/100:.2f}")
    print(f"        - Expenses: R{(expenses or 0)/100:.2f}")

conn.close()

print("\n" + "=" * 80)
print("✅ Database Analytics Columns Added Successfully!")
print("=" * 80)
print("\n💡 Next steps:")
print("   1. Run: python business_intelligence.py")
print("   2. Should now work without errors!")
print("=" * 80)