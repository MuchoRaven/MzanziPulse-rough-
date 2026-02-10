"""
MzansiPulse Database Creation Script
Purpose: Creates SQLite database with all tables for the competition
Author: [Kamohelo Mototo]
Date: February 2025
"""

import sqlite3
import os
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

# Database will be created in the database/ folder
DB_PATH = os.path.join('..', 'database', 'mzansipulse.db')

print("=" * 70)
print("🇿🇦 MzansiPulse Database Setup")
print("=" * 70)

# ============================================================================
# CREATE DATABASE CONNECTION
# ============================================================================

print("\n📁 Creating database at:", DB_PATH)

# Create connection
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("✅ Database file created successfully!")

# ============================================================================
# TABLE 1: USERS
# ============================================================================

print("\n🔨 Creating table: users")

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone_number TEXT UNIQUE NOT NULL,
        id_number_hash TEXT,
        first_name TEXT,
        last_name TEXT,
        preferred_language TEXT DEFAULT 'en',
        
        -- POPIA Consent Management
        consent_data_processing INTEGER DEFAULT 0,
        consent_credit_check INTEGER DEFAULT 0,
        consent_timestamp TEXT,
        
        -- Account Status
        kyc_status TEXT DEFAULT 'PENDING',
        account_created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        last_active TEXT,
        
        -- Offline sync
        offline_sync_enabled INTEGER DEFAULT 1,
        last_sync_timestamp TEXT
    )
''')

print("✅ Table 'users' created")

# ============================================================================
# TABLE 2: BUSINESSES
# ============================================================================

print("🔨 Creating table: businesses")

cursor.execute('''
    CREATE TABLE IF NOT EXISTS businesses (
        business_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        
        -- Business Identity
        business_name TEXT NOT NULL,
        trading_name TEXT,
        business_type TEXT,
        
        -- Location
        province TEXT,
        township TEXT,
        street_address TEXT,
        gps_latitude REAL,
        gps_longitude REAL,
        
        -- Registration
        cipc_registered INTEGER DEFAULT 0,
        cipc_registration_number TEXT,
        tax_number TEXT,
        vat_registered INTEGER DEFAULT 0,
        
        -- Operations
        operating_since TEXT,
        employee_count INTEGER DEFAULT 1,
        monthly_revenue_range TEXT,
        
        -- Verification
        verification_status TEXT DEFAULT 'UNVERIFIED',
        
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
''')

print("✅ Table 'businesses' created")

# ============================================================================
# TABLE 3: TRANSACTIONS (THE HEART OF THE SYSTEM)
# ============================================================================

print("🔨 Creating table: transactions")

cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        business_id INTEGER NOT NULL,
        
        -- Transaction Core
        transaction_date TEXT NOT NULL,
        transaction_time TEXT,
        transaction_type TEXT,
        
        -- Financial Data
        amount REAL NOT NULL,
        currency TEXT DEFAULT 'ZAR',
        payment_method TEXT DEFAULT 'CASH',
        
        -- Details
        category TEXT,
        description TEXT,
        description_cleaned TEXT,
        supplier_name TEXT,
        
        -- Source Tracking
        data_source TEXT DEFAULT 'MANUAL_ENTRY',
        source_confidence REAL DEFAULT 0.5,
        original_image_url TEXT,
        
        -- Data Quality
        is_verified INTEGER DEFAULT 0,
        flagged_for_review INTEGER DEFAULT 0,
        flag_reason TEXT,
        
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        synced_from_device INTEGER DEFAULT 0,
        
        FOREIGN KEY (business_id) REFERENCES businesses(business_id)
    )
''')

print("✅ Table 'transactions' created")

# ============================================================================
# TABLE 4: CREDIT_LOGS (EMPOWER SCORE)
# ============================================================================

print("🔨 Creating table: credit_logs")

cursor.execute('''
    CREATE TABLE IF NOT EXISTS credit_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        business_id INTEGER NOT NULL,
        
        -- Score Snapshot
        score_date TEXT NOT NULL,
        empower_score INTEGER,
        score_tier TEXT,
        
        -- Feature Contributions
        consistency_score REAL,
        growth_score REAL,
        diversity_score REAL,
        financial_discipline_score REAL,
        
        -- Model Metadata
        model_version TEXT,
        confidence_interval REAL,
        
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        
        FOREIGN KEY (business_id) REFERENCES businesses(business_id)
    )
''')

print("✅ Table 'credit_logs' created")

# ============================================================================
# TABLE 5: GRANT_OPPORTUNITIES
# ============================================================================

print("🔨 Creating table: grant_opportunities")

cursor.execute('''
    CREATE TABLE IF NOT EXISTS grant_opportunities (
        grant_id INTEGER PRIMARY KEY AUTOINCREMENT,
        
        grant_name TEXT NOT NULL,
        provider TEXT,
        grant_type TEXT,
        
        -- Stored as JSON text in SQLite
        eligibility_criteria TEXT,
        
        amount_range TEXT,
        application_url TEXT,
        application_deadline TEXT,
        
        is_active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
''')

print("✅ Table 'grant_opportunities' created")

# ============================================================================
# TABLE 6: GRANT_MATCHES
# ============================================================================

print("🔨 Creating table: grant_matches")

cursor.execute('''
    CREATE TABLE IF NOT EXISTS grant_matches (
        match_id INTEGER PRIMARY KEY AUTOINCREMENT,
        business_id INTEGER NOT NULL,
        grant_id INTEGER NOT NULL,
        
        match_score REAL,
        match_reasons TEXT,
        
        application_status TEXT DEFAULT 'RECOMMENDED',
        applied_date TEXT,
        outcome_date TEXT,
        
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        
        FOREIGN KEY (business_id) REFERENCES businesses(business_id),
        FOREIGN KEY (grant_id) REFERENCES grant_opportunities(grant_id)
    )
''')

print("✅ Table 'grant_matches' created")

# ============================================================================
# TABLE 7: AUDIT_TRAIL (POPIA Compliance)
# ============================================================================

print("🔨 Creating table: audit_trail")

cursor.execute('''
    CREATE TABLE IF NOT EXISTS audit_trail (
        audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
        
        user_id INTEGER,
        action_type TEXT,
        entity_type TEXT,
        entity_id INTEGER,
        
        ip_address TEXT,
        user_agent TEXT,
        action_details TEXT,
        
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
''')

print("✅ Table 'audit_trail' created")

# ============================================================================
# CREATE INDEXES FOR PERFORMANCE
# ============================================================================

print("\n🚀 Creating indexes for fast queries...")

cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone_number)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_business_user ON businesses(user_id)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_transaction_business ON transactions(business_id)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_transaction_date ON transactions(transaction_date)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_credit_business ON credit_logs(business_id)')

print("✅ Indexes created")

# ============================================================================
# COMMIT AND CLOSE
# ============================================================================

conn.commit()
print("\n💾 All changes committed to database")

# ============================================================================
# VERIFY TABLES WERE CREATED
# ============================================================================

print("\n📊 Verifying database structure...")

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print(f"\n✅ Total tables created: {len(tables)}")
print("\nTable List:")
for i, table in enumerate(tables, 1):
    print(f"   {i}. {table[0]}")

conn.close()

print("\n" + "=" * 70)
print("🎉 DATABASE SETUP COMPLETE!")
print("=" * 70)
print(f"\n📁 Database location: {os.path.abspath(DB_PATH)}")
print("📏 Database size:", os.path.getsize(os.path.abspath(DB_PATH)), "bytes")
print("\n✅ Ready for data insertion!")
print("=" * 70)