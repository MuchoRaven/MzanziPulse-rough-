"""
Add Sample Cash Transactions for Thandi & Thabo
Simulates realistic cash-based informal economy transactions
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random

DB_PATH = os.path.join('..', 'database', 'mzansipulse.db')

print("=" * 80)
print("💰 Adding Sample Cash Transactions")
print("=" * 80)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ============================================================================
# GET WALLET IDs
# ============================================================================

cursor.execute('''
    SELECT w.wallet_id, b.business_id, b.business_name, u.first_name
    FROM cash_wallets w
    JOIN businesses b ON w.business_id = b.business_id
    JOIN users u ON b.user_id = u.user_id
    ORDER BY b.business_id
''')

wallets = cursor.fetchall()

if not wallets:
    print("❌ No wallets found! Run add_cash_wallet_system.py first")
    exit()

print(f"\n✅ Found {len(wallets)} wallets")
for wallet_id, business_id, business_name, owner in wallets:
    print(f"   • {owner}'s {business_name} (Wallet ID: {wallet_id})")

# ============================================================================
# MAMA THANDI (SPAZA SHOP) - 7 DAYS OF TRANSACTIONS
# ============================================================================

print("\n" + "=" * 80)
print("🏪 MAMA THANDI'S SPAZA SHOP - Cash Flow Simulation")
print("=" * 80)

thandi_wallet_id = wallets[0][0]
thandi_business_id = wallets[0][1]

# Starting balance: R5,000 cash on hand
starting_balance = 500000  # cents

print(f"\n📅 MONDAY - Week Start")
print(f"   💰 Starting cash: R{starting_balance/100:,.2f}")

current_balance = starting_balance

# Update wallet starting balance
cursor.execute('''
    UPDATE cash_wallets
    SET virtual_balance_cents = ?,
        cash_on_hand_cents = ?,
        last_updated = ?
    WHERE wallet_id = ?
''', (starting_balance, starting_balance, datetime.now().isoformat(), thandi_wallet_id))

# ============================================================================
# MONDAY: Stock Purchase + Sales
# ============================================================================

transactions_thandi = []

# MONDAY 9AM: Stock purchase at Makro (CASH OUT)
day_offset = 7
transaction_date = (datetime.now() - timedelta(days=day_offset)).strftime('%Y-%m-%d')

stock_amount = 250000  # R2,500
current_balance -= stock_amount

trans = {
    'wallet_id': thandi_wallet_id,
    'transaction_type': 'CASH_OUT',
    'amount_cents': stock_amount,
    'payment_method': 'CASH',
    'source_destination': 'Makro Wholesale - Stock purchase',
    'balance_before_cents': current_balance + stock_amount,
    'balance_after_cents': current_balance,
    'transaction_date': transaction_date,
    'transaction_time': '09:15:00',
    'recorded_method': 'WHATSAPP',
    'receipt_photo_url': 'obs://receipts/thandi_makro_001.jpg',
    'verified': 1,
    'verification_method': 'OCR_VERIFIED'
}
transactions_thandi.append(trans)

print(f"\n   09:15 - Stock Purchase (Makro)")
print(f"   💸 Out: R{stock_amount/100:,.2f}")
print(f"   💰 Balance: R{current_balance/100:,.2f}")

# MONDAY: 15 cash sales throughout the day
for i in range(15):
    sale_amount = random.randint(2000, 15000)  # R20 to R150
    current_balance += sale_amount
    
    hour = random.randint(10, 18)
    minute = random.randint(0, 59)
    
    trans = {
        'wallet_id': thandi_wallet_id,
        'transaction_type': 'CASH_IN',
        'amount_cents': sale_amount,
        'payment_method': 'CASH',
        'source_destination': 'Customer cash payment - groceries',
        'balance_before_cents': current_balance - sale_amount,
        'balance_after_cents': current_balance,
        'transaction_date': transaction_date,
        'transaction_time': f'{hour:02d}:{minute:02d}:00',
        'recorded_method': 'WHATSAPP',
        'verified': 1
    }
    transactions_thandi.append(trans)

print(f"   10:00-18:00 - 15 Cash Sales")
print(f"   💵 In: R{sum(t['amount_cents'] for t in transactions_thandi[1:])/100:,.2f}")
print(f"   💰 Balance: R{current_balance/100:,.2f}")

# ============================================================================
# TUESDAY: Normal sales + eWallet payment
# ============================================================================

day_offset = 6
transaction_date = (datetime.now() - timedelta(days=day_offset)).strftime('%Y-%m-%d')

print(f"\n📅 TUESDAY")

# 12 cash sales
for i in range(12):
    sale_amount = random.randint(2000, 12000)
    current_balance += sale_amount
    
    hour = random.randint(8, 18)
    minute = random.randint(0, 59)
    
    trans = {
        'wallet_id': thandi_wallet_id,
        'transaction_type': 'CASH_IN',
        'amount_cents': sale_amount,
        'payment_method': 'CASH',
        'source_destination': 'Customer cash payment',
        'balance_before_cents': current_balance - sale_amount,
        'balance_after_cents': current_balance,
        'transaction_date': transaction_date,
        'transaction_time': f'{hour:02d}:{minute:02d}:00',
        'recorded_method': 'WHATSAPP',
        'verified': 1
    }
    transactions_thandi.append(trans)

# 1 eWallet payment (Capitec)
ewallet_amount = 5000  # R50
current_balance += ewallet_amount

trans = {
    'wallet_id': thandi_wallet_id,
    'transaction_type': 'DIGITAL_IN',
    'amount_cents': ewallet_amount,
    'payment_method': 'EWALLET',
    'source_destination': 'Capitec eWallet - Customer 0829876543',
    'balance_before_cents': current_balance - ewallet_amount,
    'balance_after_cents': current_balance,
    'transaction_date': transaction_date,
    'transaction_time': '14:30:00',
    'recorded_method': 'SMS_FORWARD',
    'payment_proof': 'obs://proofs/thandi_capitec_sms_001.jpg',
    'verified': 1,
    'verification_method': 'SMS_VERIFIED'
}
transactions_thandi.append(trans)

print(f"   Cash Sales: 12 transactions")
print(f"   💳 eWallet: R{ewallet_amount/100:.2f}")
print(f"   💰 Balance: R{current_balance/100:,.2f}")

# ============================================================================
# WEDNESDAY: Sales + Credit ("Book")
# ============================================================================

day_offset = 5
transaction_date = (datetime.now() - timedelta(days=day_offset)).strftime('%Y-%m-%d')

print(f"\n📅 WEDNESDAY")

# 10 cash sales
for i in range(10):
    sale_amount = random.randint(3000, 10000)
    current_balance += sale_amount
    
    hour = random.randint(8, 17)
    minute = random.randint(0, 59)
    
    trans = {
        'wallet_id': thandi_wallet_id,
        'transaction_type': 'CASH_IN',
        'amount_cents': sale_amount,
        'payment_method': 'CASH',
        'source_destination': 'Customer cash payment',
        'balance_before_cents': current_balance - sale_amount,
        'balance_after_cents': current_balance,
        'transaction_date': transaction_date,
        'transaction_time': f'{hour:02d}:{minute:02d}:00',
        'recorded_method': 'WHATSAPP',
        'verified': 1
    }
    transactions_thandi.append(trans)

# Credit sale (doesn't affect cash balance yet)
credit_amount = 10000  # R100

trans = {
    'wallet_id': thandi_wallet_id,
    'transaction_type': 'CREDIT_GIVEN',
    'amount_cents': credit_amount,
    'payment_method': 'CREDIT',
    'source_destination': 'Sipho - Book credit (Due Friday)',
    'balance_before_cents': current_balance,
    'balance_after_cents': current_balance,  # No cash change yet
    'transaction_date': transaction_date,
    'transaction_time': '16:45:00',
    'recorded_method': 'WHATSAPP',
    'verified': 1
}
transactions_thandi.append(trans)

# Add to credit ledger
cursor.execute('''
    INSERT INTO credit_ledger (
        wallet_id, customer_name, customer_phone,
        amount_owed_cents, balance_cents,
        status, credit_given_date, due_date
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', (
    thandi_wallet_id,
    'Sipho Dlamini',
    '0827654321',
    credit_amount,
    credit_amount,
    'OUTSTANDING',
    transaction_date,
    (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')  # Due Friday
))

print(f"   Cash Sales: 10 transactions")
print(f"   📓 Credit Given: R{credit_amount/100:.2f} (Sipho - Due Friday)")
print(f"   💰 Balance: R{current_balance/100:,.2f}")

# ============================================================================
# THURSDAY: Normal sales + Personal withdrawal (should flag!)
# ============================================================================

day_offset = 4
transaction_date = (datetime.now() - timedelta(days=day_offset)).strftime('%Y-%m-%d')

print(f"\n📅 THURSDAY")

# 13 cash sales
for i in range(13):
    sale_amount = random.randint(2500, 11000)
    current_balance += sale_amount
    
    hour = random.randint(8, 18)
    minute = random.randint(0, 59)
    
    trans = {
        'wallet_id': thandi_wallet_id,
        'transaction_type': 'CASH_IN',
        'amount_cents': sale_amount,
        'payment_method': 'CASH',
        'source_destination': 'Customer cash payment',
        'balance_before_cents': current_balance - sale_amount,
        'balance_after_cents': current_balance,
        'transaction_date': transaction_date,
        'transaction_time': f'{hour:02d}:{minute:02d}:00',
        'recorded_method': 'WHATSAPP',
        'verified': 1
    }
    transactions_thandi.append(trans)

# Personal withdrawal (NOT LOGGED INITIALLY - will cause reconciliation discrepancy!)
# We'll log it during reconciliation

print(f"   Cash Sales: 13 transactions")
print(f"   💰 Balance: R{current_balance/100:,.2f}")
print(f"   ⚠️  [Personal withdrawal R300 NOT logged - will be caught in reconciliation]")

actual_balance = current_balance - 30000  # R300 taken out

# ============================================================================
# FRIDAY: Sales + Credit collection
# ============================================================================

day_offset = 3
transaction_date = (datetime.now() - timedelta(days=day_offset)).strftime('%Y-%m-%d')

print(f"\n📅 FRIDAY")

# 11 cash sales
for i in range(11):
    sale_amount = random.randint(3000, 12000)
    current_balance += sale_amount
    
    hour = random.randint(8, 17)
    minute = random.randint(0, 59)
    
    trans = {
        'wallet_id': thandi_wallet_id,
        'transaction_type': 'CASH_IN',
        'amount_cents': sale_amount,
        'payment_method': 'CASH',
        'source_destination': 'Customer cash payment',
        'balance_before_cents': current_balance - sale_amount,
        'balance_after_cents': current_balance,
        'transaction_date': transaction_date,
        'transaction_time': f'{hour:02d}:{minute:02d}:00',
        'recorded_method': 'WHATSAPP',
        'verified': 1
    }
    transactions_thandi.append(trans)

# Sipho pays his debt
current_balance += credit_amount

trans = {
    'wallet_id': thandi_wallet_id,
    'transaction_type': 'CREDIT_COLLECTED',
    'amount_cents': credit_amount,
    'payment_method': 'CASH',
    'source_destination': 'Sipho paid book debt',
    'balance_before_cents': current_balance - credit_amount,
    'balance_after_cents': current_balance,
    'transaction_date': transaction_date,
    'transaction_time': '17:00:00',
    'recorded_method': 'WHATSAPP',
    'verified': 1
}
transactions_thandi.append(trans)

# Update credit ledger
cursor.execute('''
    UPDATE credit_ledger
    SET amount_paid_cents = amount_owed_cents,
        balance_cents = 0,
        status = 'FULLY_PAID',
        paid_date = ?
    WHERE wallet_id = ? AND customer_name = 'Sipho Dlamini'
''', (transaction_date, thandi_wallet_id))

print(f"   Cash Sales: 11 transactions")
print(f"   💵 Credit Collected: R{credit_amount/100:.2f} (Sipho paid!)")
print(f"   💰 System Balance: R{current_balance/100:,.2f}")
print(f"   💰 ACTUAL Balance: R{actual_balance/100:,.2f} (R300 less due to unlogged withdrawal)")

# ============================================================================
# INSERT ALL THANDI'S TRANSACTIONS
# ============================================================================

print(f"\n💾 Saving Mama Thandi's transactions...")

for trans in transactions_thandi:
    cursor.execute('''
        INSERT INTO cash_transactions (
            wallet_id, transaction_type, amount_cents, payment_method,
            source_destination, balance_before_cents, balance_after_cents,
            transaction_date, transaction_time, recorded_method,
            receipt_photo_url, verified, verification_method, payment_proof
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        trans['wallet_id'],
        trans['transaction_type'],
        trans['amount_cents'],
        trans['payment_method'],
        trans['source_destination'],
        trans['balance_before_cents'],
        trans['balance_after_cents'],
        trans['transaction_date'],
        trans['transaction_time'],
        trans['recorded_method'],
        trans.get('receipt_photo_url'),
        trans['verified'],
        trans.get('verification_method'),
        trans.get('payment_proof')
    ))

# Update wallet totals
total_cash_in = sum(t['amount_cents'] for t in transactions_thandi if t['transaction_type'] in ['CASH_IN', 'CREDIT_COLLECTED'])
total_cash_out = sum(t['amount_cents'] for t in transactions_thandi if t['transaction_type'] == 'CASH_OUT')
total_digital_in = sum(t['amount_cents'] for t in transactions_thandi if t['transaction_type'] == 'DIGITAL_IN')

cursor.execute('''
    UPDATE cash_wallets
    SET virtual_balance_cents = ?,
        cash_on_hand_cents = ?,
        digital_balance_cents = ?,
        total_cash_sales_cents = ?,
        total_digital_sales_cents = ?,
        total_expenses_cents = ?,
        last_updated = ?
    WHERE wallet_id = ?
''', (
    current_balance,
    current_balance - 5000,  # Minus the R50 in phone
    5000,
    total_cash_in,
    total_digital_in,
    total_cash_out,
    datetime.now().isoformat(),
    thandi_wallet_id
))

print(f"✅ {len(transactions_thandi)} transactions saved")

# ============================================================================
# THABO SAKWANE (TAILOR) - 7 DAYS OF TRANSACTIONS
# ============================================================================

print("\n" + "=" * 80)
print("🪡 THABO'S TAILORING - Cash Flow Simulation")
print("=" * 80)

thabo_wallet_id = wallets[1][0]
thabo_business_id = wallets[1][1]

# Starting balance: R3,000 cash on hand
starting_balance = 300000  # cents

print(f"\n📅 MONDAY - Week Start")
print(f"   💰 Starting cash: R{starting_balance/100:,.2f}")

current_balance = starting_balance

cursor.execute('''
    UPDATE cash_wallets
    SET virtual_balance_cents = ?,
        cash_on_hand_cents = ?,
        last_updated = ?
    WHERE wallet_id = ?
''', (starting_balance, starting_balance, datetime.now().isoformat(), thabo_wallet_id))

transactions_thabo = []

# ============================================================================
# WEEK OF TAILORING WORK
# ============================================================================

# Thabo works 6 days (Monday-Saturday), 4-6 jobs per day
for day in range(7, 1, -1):  # 7 days ago to 2 days ago
    transaction_date = (datetime.now() - timedelta(days=day)).strftime('%Y-%m-%d')
    
    if day == 2:  # Sunday - rest day
        continue
    
    daily_jobs = random.randint(4, 6)
    
    for job in range(daily_jobs):
        # Tailor jobs: R40-R150 mostly cash
        job_amount = random.randint(4000, 15000)
        
        # 85% cash, 15% eWallet
        payment_method = 'CASH' if random.random() < 0.85 else 'EWALLET'
        trans_type = 'CASH_IN' if payment_method == 'CASH' else 'DIGITAL_IN'
        
        current_balance += job_amount
        
        hour = random.randint(9, 17)
        minute = random.randint(0, 59)
        
        # Sesotho-flavored descriptions
        descriptions = [
            'Trouser hemming - mokgotsi o lefile',
            'Dress alteration - mosadi',
            'Zip replacement - customer paid',
            'School uniform repair',
            'Button repair - cash',
            'Custom shirt - measured and paid'
        ]
        
        trans = {
            'wallet_id': thabo_wallet_id,
            'transaction_type': trans_type,
            'amount_cents': job_amount,
            'payment_method': payment_method,
            'source_destination': random.choice(descriptions),
            'balance_before_cents': current_balance - job_amount,
            'balance_after_cents': current_balance,
            'transaction_date': transaction_date,
            'transaction_time': f'{hour:02d}:{minute:02d}:00',
            'recorded_method': 'WHATSAPP',
            'verified': 1
        }
        transactions_thabo.append(trans)

# Fabric purchase on Wednesday
day_offset = 5
transaction_date = (datetime.now() - timedelta(days=day_offset)).strftime('%Y-%m-%d')

fabric_amount = 80000  # R800
current_balance -= fabric_amount

trans = {
    'wallet_id': thabo_wallet_id,
    'transaction_type': 'CASH_OUT',
    'amount_cents': fabric_amount,
    'payment_method': 'CASH',
    'source_destination': 'Textile Warehouse - Fabric stock',
    'balance_before_cents': current_balance + fabric_amount,
    'balance_after_cents': current_balance,
    'transaction_date': transaction_date,
    'transaction_time': '11:30:00',
    'recorded_method': 'WHATSAPP',
    'receipt_photo_url': 'obs://receipts/thabo_textile_001.jpg',
    'verified': 1,
    'verification_method': 'OCR_VERIFIED'
}
transactions_thabo.append(trans)

print(f"\n💾 Saving Thabo's transactions...")

for trans in transactions_thabo:
    cursor.execute('''
        INSERT INTO cash_transactions (
            wallet_id, transaction_type, amount_cents, payment_method,
            source_destination, balance_before_cents, balance_after_cents,
            transaction_date, transaction_time, recorded_method,
            receipt_photo_url, verified, verification_method
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        trans['wallet_id'],
        trans['transaction_type'],
        trans['amount_cents'],
        trans['payment_method'],
        trans['source_destination'],
        trans['balance_before_cents'],
        trans['balance_after_cents'],
        trans['transaction_date'],
        trans['transaction_time'],
        trans['recorded_method'],
        trans.get('receipt_photo_url'),
        trans['verified'],
        trans.get('verification_method')
    ))

# Update Thabo's wallet totals
total_cash_in = sum(t['amount_cents'] for t in transactions_thabo if t['transaction_type'] == 'CASH_IN')
total_digital_in = sum(t['amount_cents'] for t in transactions_thabo if t['transaction_type'] == 'DIGITAL_IN')
total_cash_out = sum(t['amount_cents'] for t in transactions_thabo if t['transaction_type'] == 'CASH_OUT')

cursor.execute('''
    UPDATE cash_wallets
    SET virtual_balance_cents = ?,
        cash_on_hand_cents = ?,
        digital_balance_cents = ?,
        total_cash_sales_cents = ?,
        total_digital_sales_cents = ?,
        total_expenses_cents = ?,
        last_updated = ?
    WHERE wallet_id = ?
''', (
    current_balance,
    current_balance - sum(t['amount_cents'] for t in transactions_thabo if t['transaction_type'] == 'DIGITAL_IN'),
    sum(t['amount_cents'] for t in transactions_thabo if t['transaction_type'] == 'DIGITAL_IN'),
    total_cash_in,
    total_digital_in,
    total_cash_out,
    datetime.now().isoformat(),
    thabo_wallet_id
))

print(f"✅ {len(transactions_thabo)} transactions saved")

# ============================================================================
# SUMMARY
# ============================================================================

conn.commit()

print("\n" + "=" * 80)
print("📊 CASH WALLET SUMMARY")
print("=" * 80)

cursor.execute('''
    SELECT 
        b.business_name,
        u.first_name,
        w.virtual_balance_cents,
        w.cash_on_hand_cents,
        w.digital_balance_cents,
        w.total_cash_sales_cents,
        w.total_expenses_cents,
        (SELECT COUNT(*) FROM cash_transactions WHERE wallet_id = w.wallet_id) as transaction_count
    FROM cash_wallets w
    JOIN businesses b ON w.business_id = b.business_id
    JOIN users u ON b.user_id = u.user_id
''')

for row in cursor.fetchall():
    name, owner, balance, cash, digital, sales, expenses, count = row
    print(f"\n👤 {owner}'s {name}")
    print(f"   💰 Total Balance: R{balance/100:,.2f}")
    print(f"   💵 Cash: R{cash/100:,.2f}")
    print(f"   💳 Digital: R{digital/100:,.2f}")
    print(f"   📈 Sales: R{sales/100:,.2f}")
    print(f"   📉 Expenses: R{expenses/100:,.2f}")
    print(f"   📊 Transactions: {count}")

print("\n" + "=" * 80)
print("✅ SAMPLE CASH TRANSACTIONS CREATED!")
print("=" * 80)
print("\nNEXT: View in DB Browser → cash_transactions table")
print("=" * 80)

conn.close()