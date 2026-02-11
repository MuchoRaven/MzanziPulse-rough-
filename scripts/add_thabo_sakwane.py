"""
Add Thabo Sakwane - Self-Employed Tailor from Qwaqwa
Demonstrates MzansiPulse for different business type and language (Sesotho)
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random

DB_PATH = os.path.join('..', 'database', 'mzansipulse.db')

print("=" * 80)
print("👔 Adding Thabo Sakwane - Qwaqwa Street Tailor")
print("=" * 80)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ============================================================================
# INSERT USER: Thabo Sakwane
# ============================================================================

print("\n👤 Creating user: Thabo Sakwane (Sesotho speaker)")

cursor.execute('''
    INSERT INTO users (
        phone_number, first_name, last_name, preferred_language,
        consent_data_processing, consent_credit_check, consent_timestamp,
        kyc_status, account_created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
''', (
    '0837654321',
    'Thabo',
    'Sakwane',
    'st',  # Sesotho language code
    1,
    1,
    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'VERIFIED',
    (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d %H:%M:%S')  # Joined 3 months ago
))

user_id = cursor.lastrowid
print(f"✅ User created with ID: {user_id}")
print(f"   Phone: 0837654321")
print(f"   Language: Sesotho (st)")
print(f"   Account age: 90 days")

# ============================================================================
# INSERT BUSINESS: Street Tailor
# ============================================================================

print("\n🪡 Creating business: Thabo's Tailoring Services")

cursor.execute('''
    INSERT INTO businesses (
        user_id, business_name, trading_name, business_type,
        province, township, street_address,
        gps_latitude, gps_longitude,
        cipc_registered, tax_number, vat_registered,
        operating_since, employee_count, monthly_revenue_range,
        verification_status, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', (
    user_id,
    "Thabo Sakwane Tailoring",
    "Thabo's Quick Fix",
    "TAILOR_SHOP",
    "Free State",
    "Qwaqwa - Phuthaditjhaba",
    "Corner Mampoi & Kestell Street, Phuthaditjhaba",
    -28.5245,  # Qwaqwa coordinates
    28.8147,
    0,  # Not CIPC registered (informal)
    None,
    0,  # No VAT registration
    "2022-06-01",  # Operating for ~2.5 years
    1,  # Solo entrepreneur
    "R5K-20K",
    "VERIFIED",
    (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d %H:%M:%S')
))

business_id = cursor.lastrowid
print(f"✅ Business created with ID: {business_id}")
print(f"   Type: Street Tailor (self-employed)")
print(f"   Location: Qwaqwa, Free State")
print(f"   Operating since: June 2022 (2.5 years)")
print(f"   Revenue range: R5,000 - R10,000/month")

# ============================================================================
# INSERT TRANSACTIONS: 60 Days of Tailoring Work
# ============================================================================

print("\n💰 Creating 60 days of tailoring transactions...")

# Tailor-specific transaction templates
# Street tailors do: alterations, repairs, custom sewing
transaction_templates = [
    # (category, description, min_price, max_price, transaction_type)
    ("ALTERATIONS", "trouser hemming", 40, 80, "SALE"),
    ("ALTERATIONS", "dress alteration", 80, 150, "SALE"),
    ("ALTERATIONS", "jacket sleeves shortening", 60, 100, "SALE"),
    ("ALTERATIONS", "school uniform alteration", 50, 90, "SALE"),
    ("REPAIRS", "zip replacement", 35, 60, "SALE"),
    ("REPAIRS", "button repair", 20, 40, "SALE"),
    ("REPAIRS", "torn seam repair", 30, 70, "SALE"),
    ("CUSTOM_SEWING", "custom shirt", 200, 400, "SALE"),
    ("CUSTOM_SEWING", "traditional Basotho blanket coat", 500, 800, "SALE"),
    ("CUSTOM_SEWING", "church dress", 300, 600, "SALE"),
    ("CUSTOM_SEWING", "wedding outfit", 800, 1500, "SALE"),
    ("STOCK_PURCHASE", "fabric from textile shop", 200, 800, "PURCHASE"),
    ("STOCK_PURCHASE", "thread spools bulk", 150, 300, "PURCHASE"),
    ("STOCK_PURCHASE", "zips and buttons", 100, 250, "PURCHASE"),
    ("EQUIPMENT", "sewing machine maintenance", 150, 400, "EXPENSE"),
]

# Generate transactions for last 60 days (more history than Thandi)
transaction_count = 0
today = datetime.now()

for day_offset in range(60, 0, -1):
    transaction_date = (today - timedelta(days=day_offset)).strftime('%Y-%m-%d')
    
    # Street tailors work 5-6 days/week
    # Skip some days (Sundays and random slow days)
    if random.random() < 0.15:  # 15% chance of no business
        continue
    
    # 3-7 jobs per working day (less than spaza shop transactions)
    daily_jobs = random.randint(3, 7)
    
    for _ in range(daily_jobs):
        # Pick random job type
        category, desc, min_price, max_price, trans_type = random.choice(transaction_templates)
        
        # Random amount within range
        amount = round(random.uniform(min_price, max_price), 2)
        
        # Payment method (tailors get more cash than spaza shops)
        payment_method = random.choices(
            ['CASH', 'EWALLET', 'CARD'],
            weights=[0.80, 0.15, 0.05]  # 80% cash, 15% ewallet, 5% card
        )[0]
        
        # Sesotho-flavored descriptions (code-switching)
        sesotho_phrases = [
            "mokgotsi o ile a lefa",  # customer paid
            "mosadi o rekile",  # woman bought
            "monna a rekile",  # man bought
            "moruti a tlile",  # pastor came
            "baithuti ba sekolong",  # school students
            "mosebetsi wa letsatsi",  # day's work
        ]
        
        # Sometimes add Sesotho phrase to description
        if random.random() < 0.3 and trans_type == "SALE":
            sesotho_touch = random.choice(sesotho_phrases)
            description = f"{desc} {sesotho_touch}"
        else:
            description = desc
        
        cursor.execute('''
            INSERT INTO transactions (
                business_id, transaction_date, transaction_time, transaction_type,
                amount, category, description, description_cleaned,
                payment_method, data_source, source_confidence,
                is_verified, flagged_for_review
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            business_id,
            transaction_date,
            f"{random.randint(8, 18):02d}:{random.randint(0, 59):02d}:00",  # 8am-6pm working hours
            trans_type,
            amount,
            category,
            description,
            desc,  # Cleaned version
            payment_method,
            'MANUAL_ENTRY',
            0.85,  # Slightly lower confidence (street business, less structured)
            1,
            0
        ))
        
        transaction_count += 1

print(f"✅ Created {transaction_count} transactions over 60 days")

# ============================================================================
# CALCULATE MONTHLY REVENUE SUMMARY
# ============================================================================

cursor.execute('''
    SELECT 
        COUNT(*) as total_transactions,
        SUM(CASE WHEN transaction_type = 'SALE' THEN amount ELSE 0 END) as total_revenue,
        SUM(CASE WHEN transaction_type = 'PURCHASE' THEN amount ELSE 0 END) as total_expenses,
        AVG(CASE WHEN transaction_type = 'SALE' THEN amount ELSE NULL END) as avg_sale,
        COUNT(DISTINCT transaction_date) as days_worked
    FROM transactions
    WHERE business_id = ?
    AND transaction_date >= date('now', '-30 days')
''', (business_id,))

stats = cursor.fetchone()
total_trans, revenue, expenses, avg_sale, days_worked = stats

net_income = revenue - expenses

print(f"\n📊 BUSINESS PERFORMANCE (Last 30 Days)")
print("-" * 80)
print(f"   Total Jobs Completed:     {total_trans}")
print(f"   Days Worked:              {days_worked}/30")
print(f"   Total Revenue:            R{revenue:,.2f}")
print(f"   Total Expenses:           R{expenses:,.2f}")
print(f"   Net Income:               R{net_income:,.2f}")
print(f"   Average Job Value:        R{avg_sale:,.2f}")

# ============================================================================
# CALCULATE EMPOWERSCORE (Using Our Algorithm)
# ============================================================================

print("\n🧠 Calculating EmpowerScore...")

# Get all transactions for scoring
cursor.execute('''
    SELECT 
        transaction_id, transaction_date, transaction_type,
        amount, category, payment_method, flagged_for_review, supplier_name
    FROM transactions
    WHERE business_id = ?
    AND transaction_date >= date('now', '-30 days')
    ORDER BY transaction_date ASC
''', (business_id,))

transactions = cursor.fetchall()

# CONSISTENCY SCORE (30%)
unique_dates = set(t[1] for t in transactions)
days_with_transactions = len(unique_dates)
consistency_score = min((days_with_transactions / 30) * 100, 100.0)

# GROWTH SCORE (25%)
mid_point = len(transactions) // 2
first_half = transactions[:mid_point]
second_half = transactions[mid_point:]

first_revenue = sum(t[3] for t in first_half if t[2] == 'SALE')
second_revenue = sum(t[3] for t in second_half if t[2] == 'SALE')

if first_revenue > 0:
    growth_pct = ((second_revenue - first_revenue) / first_revenue) * 100
    growth_score = 50 + growth_pct if -50 <= growth_pct <= 50 else (0 if growth_pct < -50 else 100)
else:
    growth_score = 50.0

# DIVERSITY SCORE (25%)
categories = set(t[4] for t in transactions if t[4])
category_count = len(categories)
category_score = min(category_count * 10, 50)

# Tailors have fewer suppliers than spaza shops, adjust scoring
suppliers = set(t[7] for t in transactions if t[2] == 'PURCHASE' and t[7])
supplier_count = len(suppliers)
if supplier_count == 0:
    supplier_score = 30  # Neutral for service businesses
elif supplier_count == 1:
    supplier_score = 20
elif supplier_count == 2:
    supplier_score = 35
else:
    supplier_score = 50

diversity_score = category_score + supplier_score

# DISCIPLINE SCORE (20%)
flagged_count = sum(1 for t in transactions if t[6])
flagged_pct = (flagged_count / len(transactions)) * 100 if len(transactions) > 0 else 0

if flagged_pct == 0:
    discipline_score = 100.0
elif flagged_pct >= 30:
    discipline_score = 0.0
else:
    discipline_score = 100 - (flagged_pct * 3.33)

# FINAL SCORE
weighted_score = (
    consistency_score * 0.30 +
    growth_score * 0.25 +
    diversity_score * 0.25 +
    discipline_score * 0.20
)

empower_score = int(weighted_score * 10)

# Determine tier
if empower_score >= 601:
    tier = "PRIME"
elif empower_score >= 301:
    tier = "BUILDER"
else:
    tier = "STARTER"

print(f"\n🎯 EMPOWERSCORE CALCULATED")
print("-" * 80)
print(f"   Consistency Score:    {consistency_score:.1f}/100")
print(f"   Growth Score:         {growth_score:.1f}/100")
print(f"   Diversity Score:      {diversity_score:.1f}/100")
print(f"   Discipline Score:     {discipline_score:.1f}/100")
print("-" * 80)
print(f"   FINAL SCORE:          {empower_score}/1000")
print(f"   TIER:                 {tier}")

# ============================================================================
# SAVE CREDIT LOG
# ============================================================================

cursor.execute('''
    INSERT INTO credit_logs (
        business_id, score_date, empower_score, score_tier,
        consistency_score, growth_score, diversity_score,
        financial_discipline_score, model_version, confidence_interval
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', (
    business_id,
    datetime.now().strftime('%Y-%m-%d'),
    empower_score,
    tier,
    consistency_score,
    growth_score,
    diversity_score,
    discipline_score,
    'v1.0_production',
    0.88  # High confidence (60 days of data)
))

credit_log_id = cursor.lastrowid
print(f"\n✅ Credit log saved (ID: {credit_log_id})")

# ============================================================================
# FIND GRANT MATCHES
# ============================================================================

print("\n🎁 Finding eligible grants for Thabo...")

cursor.execute('''
    SELECT grant_id, grant_name, provider, amount_range
    FROM grant_opportunities
    WHERE is_active = 1
''')

grants = cursor.fetchall()
matches_saved = 0

for grant in grants:
    grant_id, name, provider, amount = grant
    
    # Simple eligibility: score > 400 for most grants
    if empower_score >= 400:
        # Calculate match score based on business type
        match_score = 0.75  # Base for tailors
        
        if "Youth" in provider or "NYDA" in provider:
            match_score = 0.85  # Young entrepreneur bonus
        
        cursor.execute('''
            INSERT INTO grant_matches (
                business_id, grant_id, match_score, match_reasons,
                application_status
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            business_id,
            grant_id,
            match_score,
            '["EmpowerScore meets requirement", "Service business (tailor)", "Free State location"]',
            'RECOMMENDED'
        ))
        matches_saved += 1
        print(f"   ✅ Matched: {name} ({amount})")

# ============================================================================
# COMMIT AND SUMMARY
# ============================================================================

conn.commit()

print("\n" + "=" * 80)
print("📊 THABO SAKWANE - SUMMARY")
print("=" * 80)

print(f"\n👤 PERSONAL INFO")
print(f"   Name:                 Thabo Sakwane")
print(f"   Phone:                0837654321")
print(f"   Language:             Sesotho")
print(f"   Location:             Qwaqwa, Free State")

print(f"\n🪡 BUSINESS INFO")
print(f"   Business Type:        Street Tailor (Self-Employed)")
print(f"   Trading As:           Thabo's Quick Fix")
print(f"   Operating Since:      June 2022 (2.5 years)")
print(f"   Days Worked (30d):    {days_worked}/30")

print(f"\n💰 FINANCIALS (30 Days)")
print(f"   Revenue:              R{revenue:,.2f}")
print(f"   Expenses:             R{expenses:,.2f}")
print(f"   Net Income:           R{net_income:,.2f}")
print(f"   Avg Job Value:        R{avg_sale:,.2f}")

print(f"\n📈 CREDIT PROFILE")
print(f"   EmpowerScore:         {empower_score}/1000")
print(f"   Tier:                 {tier}")
print(f"   Transaction Count:    {transaction_count} (60 days)")
print(f"   Eligible Grants:      {matches_saved}")

print("\n" + "=" * 80)

# ============================================================================
# DATABASE COMPARISON
# ============================================================================

print("\n🔍 DATABASE TOTALS (All Businesses)")
print("=" * 80)

cursor.execute('SELECT COUNT(*) FROM users')
total_users = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM businesses')
total_businesses = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM transactions')
total_transactions = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM credit_logs')
total_scores = cursor.fetchone()[0]

print(f"   Total Users:          {total_users}")
print(f"   Total Businesses:     {total_businesses}")
print(f"   Total Transactions:   {total_transactions}")
print(f"   Total Credit Logs:    {total_scores}")

print("\n" + "=" * 80)
print("✅ Thabo Sakwane successfully added to MzansiPulse!")
print("=" * 80)
print("\n💡 View in DB Browser:")
print("   • users table → user_id =", user_id)
print("   • businesses table → business_id =", business_id)
print("   • transactions table → filter by business_id =", business_id)
print("   • credit_logs table → latest entry")
print("=" * 80)

conn.close()