"""
MzansiPulse Test Data Insertion
Creates realistic test data for a Soweto spaza shop
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random

DB_PATH = os.path.join('..', 'database', 'mzansipulse.db')

print("=" * 70)
print("📝 Inserting Test Data into MzansiPulse")
print("=" * 70)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ============================================================================
# INSERT USER (Spaza Shop Owner)
# ============================================================================

print("\n👤 Creating user: Mama Thandi Molefe")

cursor.execute('''
    INSERT INTO users (
        phone_number, first_name, last_name, preferred_language,
        consent_data_processing, consent_credit_check, kyc_status
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
''', ('0821234567', 'Thandi', 'Molefe', 'Zulu', 1, 1, 'VERIFIED'))

user_id = cursor.lastrowid
print(f"✅ User created with ID: {user_id}")

# ============================================================================
# INSERT BUSINESS (Spaza Shop)
# ============================================================================

print("🏪 Creating business: Mama Thandi's Spaza")

cursor.execute('''
    INSERT INTO businesses (
        user_id, business_name, trading_name, business_type,
        province, township, street_address,
        operating_since, employee_count, monthly_revenue_range,
        verification_status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', (
    user_id,
    "Mama Thandi's Spaza Shop",
    "Thandi's Corner Store",
    "SPAZA_SHOP",
    "Gauteng",
    "Soweto - Orlando East",
    "1234 Vilakazi Street",
    "2020-01-15",
    2,
    "R5K-20K",
    "VERIFIED"
))

business_id = cursor.lastrowid
print(f"✅ Business created with ID: {business_id}")

# ============================================================================
# INSERT TRANSACTIONS (30 days of realistic sales)
# ============================================================================

print("\n💰 Creating 30 days of transaction history...")

# Categories and typical prices in a spaza shop
transaction_templates = [
    ("GROCERIES", "Bread sales", 15.00, 25.00),
    ("GROCERIES", "Milk sales", 18.00, 22.00),
    ("GROCERIES", "Sugar 2kg", 35.00, 45.00),
    ("GROCERIES", "Maize meal sales", 50.00, 80.00),
    ("AIRTIME", "Airtime voucher", 10.00, 100.00),
    ("AIRTIME", "Data bundle", 30.00, 150.00),
    ("GROCERIES", "Cooking oil", 40.00, 60.00),
    ("GROCERIES", "Rice sales", 50.00, 90.00),
    ("ELECTRICITY", "Prepaid electricity", 50.00, 200.00),
    ("STOCK_PURCHASE", "Wholesaler stock purchase", 500.00, 2000.00),
]

# Generate transactions for last 30 days
transaction_count = 0
today = datetime.now()

for day_offset in range(30, 0, -1):
    transaction_date = (today - timedelta(days=day_offset)).strftime('%Y-%m-%d')
    
    # 5-10 transactions per day
    daily_transactions = random.randint(5, 10)
    
    for _ in range(daily_transactions):
        # Pick random transaction type
        category, desc, min_price, max_price = random.choice(transaction_templates)
        
        # Random amount within range
        amount = round(random.uniform(min_price, max_price), 2)
        
        # Payment method (spaza shops are mostly cash)
        payment_method = random.choices(
            ['CASH', 'EWALLET', 'CREDIT'],
            weights=[0.7, 0.2, 0.1]  # 70% cash, 20% ewallet, 10% credit
        )[0]
        
        # Transaction type
        if category == "STOCK_PURCHASE":
            trans_type = "PURCHASE"
        else:
            trans_type = "SALE"
        
        cursor.execute('''
            INSERT INTO transactions (
                business_id, transaction_date, transaction_type,
                amount, category, description, description_cleaned,
                payment_method, data_source, is_verified
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            business_id,
            transaction_date,
            trans_type,
            amount,
            category,
            desc,
            desc,  # In real system, this would be cleaned version
            payment_method,
            'MANUAL_ENTRY',
            1
        ))
        
        transaction_count += 1

print(f"✅ Created {transaction_count} transactions")

# ============================================================================
# INSERT GRANT OPPORTUNITIES (Real SA Grants)
# ============================================================================

print("\n🎁 Adding South African grant opportunities...")

grants = [
    (
        "NYDA Business Grant",
        "National Youth Development Agency",
        "SEED_FUNDING",
        '{"min_age": 18, "max_age": 35, "min_score": 400}',
        "R10,000 - R100,000",
        "https://www.nyda.gov.za/Programmes/Pages/Business-Development-and-Support.aspx",
        "2025-12-31"
    ),
    (
        "SEFA Khula Micro Finance",
        "Small Enterprise Finance Agency",
        "LOAN",
        '{"min_score": 500, "operating_months": 12}',
        "R5,000 - R3,000,000",
        "https://www.sefa.org.za/",
        "2025-12-31"
    ),
    (
        "Township Entrepreneur Fund",
        "Standard Bank",
        "SEED_FUNDING",
        '{"location": "township", "min_score": 450}',
        "R20,000 - R150,000",
        "https://www.standardbank.co.za/southafrica/business",
        "2025-06-30"
    ),
]

for grant_data in grants:
    cursor.execute('''
        INSERT INTO grant_opportunities (
            grant_name, provider, grant_type, eligibility_criteria,
            amount_range, application_url, application_deadline
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', grant_data)

print(f"✅ Added {len(grants)} grant opportunities")

# ============================================================================
# INSERT INITIAL CREDIT SCORE
# ============================================================================

print("\n📊 Calculating initial EmpowerScore...")

# Calculate based on transaction history
cursor.execute('''
    SELECT 
        COUNT(*) as transaction_count,
        AVG(amount) as avg_transaction,
        SUM(CASE WHEN transaction_type = 'SALE' THEN amount ELSE 0 END) as total_sales
    FROM transactions
    WHERE business_id = ?
''', (business_id,))

stats = cursor.fetchone()
transaction_count, avg_transaction, total_sales = stats

# Simple scoring algorithm
consistency_score = min(100, (transaction_count / 300) * 100)  # More transactions = better
growth_score = 65  # Placeholder
diversity_score = 70  # Placeholder
discipline_score = 75  # Placeholder

empower_score = int(
    (consistency_score * 0.3) +
    (growth_score * 0.25) +
    (diversity_score * 0.25) +
    (discipline_score * 0.2)
)

# Determine tier
if empower_score >= 601:
    tier = "PRIME"
elif empower_score >= 301:
    tier = "BUILDER"
else:
    tier = "STARTER"

cursor.execute('''
    INSERT INTO credit_logs (
        business_id, score_date, empower_score, score_tier,
        consistency_score, growth_score, diversity_score, financial_discipline_score,
        model_version
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
''', (
    business_id,
    datetime.now().strftime('%Y-%m-%d'),
    empower_score,
    tier,
    consistency_score,
    growth_score,
    diversity_score,
    discipline_score,
    "v1.0_baseline"
))

print(f"✅ EmpowerScore calculated: {empower_score} ({tier})")

# ============================================================================
# COMMIT AND SUMMARY
# ============================================================================

conn.commit()

print("\n" + "=" * 70)
print("📊 DATABASE SUMMARY")
print("=" * 70)

# Count records in each table
tables = ['users', 'businesses', 'transactions', 'grant_opportunities', 'credit_logs']

for table in tables:
    cursor.execute(f'SELECT COUNT(*) FROM {table}')
    count = cursor.fetchone()[0]
    print(f"   {table:.<30} {count:>5} records")

print("=" * 70)

# Business summary
print("\n💼 BUSINESS SNAPSHOT: Mama Thandi's Spaza")
print("-" * 70)
print(f"   Total Sales (30 days):        R{total_sales:,.2f}")
print(f"   Average Transaction:          R{avg_transaction:,.2f}")
print(f"   Transaction Count:            {transaction_count}")
print(f"   EmpowerScore:                 {empower_score}/1000")
print(f"   Tier:                         {tier}")
print("-" * 70)

conn.close()

print("\n✅ Test data insertion complete!")
print("🎉 Your database is now ready for development!\n")