"""
Cash-Based Virtual Wallet System
For informal entrepreneurs who operate primarily in CASH
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join('..', 'database', 'mzansipulse.db')

print("=" * 80)
print("💵 Creating CASH-BASED Virtual Wallet System")
print("=" * 80)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ============================================================================
# TABLE 1: CASH_WALLETS (Virtual cash tracking)
# ============================================================================

print("\n🏦 Creating table: cash_wallets")

cursor.execute('''
    CREATE TABLE IF NOT EXISTS cash_wallets (
        wallet_id INTEGER PRIMARY KEY AUTOINCREMENT,
        business_id INTEGER NOT NULL UNIQUE,
        
        -- Virtual Balance (mirrors physical cash on hand)
        virtual_balance_cents INTEGER DEFAULT 0,  -- What app THINKS they have
        last_declared_balance_cents INTEGER,      -- What USER said they have
        last_reconciliation_date TEXT,            -- When they last counted
        
        -- Balance breakdown
        cash_on_hand_cents INTEGER DEFAULT 0,       -- Physical cash
        digital_balance_cents INTEGER DEFAULT 0,    -- In phone (eWallet/bank)
        credit_given_cents INTEGER DEFAULT 0,       -- Money customers owe them
        
        -- Tracking
        total_cash_sales_cents INTEGER DEFAULT 0,
        total_digital_sales_cents INTEGER DEFAULT 0,
        total_credit_sales_cents INTEGER DEFAULT 0,
        total_expenses_cents INTEGER DEFAULT 0,
        
        -- Reconciliation accuracy (trust score!)
        reconciliation_count INTEGER DEFAULT 0,
        accurate_reconciliations INTEGER DEFAULT 0,
        accuracy_percentage REAL DEFAULT 100.0,
        
        -- Status
        wallet_status TEXT DEFAULT 'ACTIVE',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        last_updated TEXT,
        
        FOREIGN KEY (business_id) REFERENCES businesses(business_id)
    )
''')

print("✅ Table 'cash_wallets' created")

# ============================================================================
# TABLE 2: CASH_TRANSACTIONS (Every cash movement)
# ============================================================================

print("🔨 Creating table: cash_transactions")

cursor.execute('''
    CREATE TABLE IF NOT EXISTS cash_transactions (
        cash_transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        wallet_id INTEGER NOT NULL,
        linked_transaction_id INTEGER,  -- Links to main transactions table
        
        -- Transaction details
        transaction_type TEXT NOT NULL,  -- CASH_IN, CASH_OUT, DIGITAL_IN, CREDIT_GIVEN, CREDIT_COLLECTED
        amount_cents INTEGER NOT NULL,
        
        -- Payment method
        payment_method TEXT,  -- CASH, EWALLET, BANK_TRANSFER, WHATSAPP_PAY, CREDIT
        payment_proof TEXT,   -- SMS screenshot, WhatsApp confirmation, etc.
        
        -- Cash source/destination
        source_destination TEXT,  -- "Customer cash payment", "Makro stock purchase", etc.
        
        -- Balance snapshot (before and after)
        balance_before_cents INTEGER,
        balance_after_cents INTEGER,
        
        -- Verification
        receipt_photo_url TEXT,
        verified INTEGER DEFAULT 0,
        verification_method TEXT,
        
        -- Metadata
        transaction_date TEXT NOT NULL,
        transaction_time TEXT,
        recorded_at TEXT DEFAULT CURRENT_TIMESTAMP,
        recorded_method TEXT,  -- WHATSAPP, MANUAL_ENTRY, SMS_FORWARD, VOICE_NOTE
        
        FOREIGN KEY (wallet_id) REFERENCES cash_wallets(wallet_id),
        FOREIGN KEY (linked_transaction_id) REFERENCES transactions(transaction_id)
    )
''')

print("✅ Table 'cash_transactions' created")

# ============================================================================
# TABLE 3: RECONCILIATIONS (Weekly cash counting)
# ============================================================================

print("🔨 Creating table: reconciliations")

cursor.execute('''
    CREATE TABLE IF NOT EXISTS reconciliations (
        reconciliation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        wallet_id INTEGER NOT NULL,
        
        -- What the numbers say
        system_balance_cents INTEGER,      -- What app calculated
        declared_balance_cents INTEGER,    -- What user counted physically
        difference_cents INTEGER,          -- The gap
        
        -- Analysis
        difference_percentage REAL,
        is_accurate INTEGER,  -- Within 5% tolerance?
        
        -- Resolution
        discrepancy_reason TEXT,  -- "Forgot to log 3 sales", "Personal withdrawal not logged", etc.
        correction_made INTEGER DEFAULT 0,
        correction_details TEXT,
        
        -- Trust impact
        impacts_score INTEGER DEFAULT 1,  -- Does this affect EmpowerScore?
        
        -- Metadata
        reconciliation_date TEXT NOT NULL,
        reconciliation_method TEXT,  -- USER_COUNT, BANK_STATEMENT_CHECK, PHOTO_VERIFICATION
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        
        FOREIGN KEY (wallet_id) REFERENCES cash_wallets(wallet_id)
    )
''')

print("✅ Table 'reconciliations' created")

# ============================================================================
# TABLE 4: CREDIT_LEDGER (Customer "book" debts)
# ============================================================================

print("🔨 Creating table: credit_ledger")

cursor.execute('''
    CREATE TABLE IF NOT EXISTS credit_ledger (
        credit_entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
        wallet_id INTEGER NOT NULL,
        
        -- Customer info
        customer_name TEXT,
        customer_phone TEXT,
        
        -- Credit details
        amount_owed_cents INTEGER NOT NULL,
        amount_paid_cents INTEGER DEFAULT 0,
        balance_cents INTEGER,  -- Outstanding
        
        -- Transaction link
        original_sale_transaction_id INTEGER,
        
        -- Status
        status TEXT DEFAULT 'OUTSTANDING',  -- OUTSTANDING, PARTIALLY_PAID, FULLY_PAID, WRITTEN_OFF
        
        -- Dates
        credit_given_date TEXT NOT NULL,
        due_date TEXT,
        paid_date TEXT,
        
        -- Notes
        notes TEXT,
        
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        
        FOREIGN KEY (wallet_id) REFERENCES cash_wallets(wallet_id),
        FOREIGN KEY (original_sale_transaction_id) REFERENCES transactions(transaction_id)
    )
''')

print("✅ Table 'credit_ledger' created")

# ============================================================================
# TABLE 5: PAYMENT_PROOFS (SMS, WhatsApp confirmations)
# ============================================================================

print("🔨 Creating table: payment_proofs")

cursor.execute('''
    CREATE TABLE IF NOT EXISTS payment_proofs (
        proof_id INTEGER PRIMARY KEY AUTOINCREMENT,
        cash_transaction_id INTEGER,
        
        -- Proof details
        proof_type TEXT,  -- SMS_SCREENSHOT, WHATSAPP_CONFIRMATION, BANK_NOTIFICATION, RECEIPT_PHOTO
        file_url TEXT,    -- OBS storage link
        
        -- Extracted data (OCR/AI parsed)
        sender_number TEXT,
        amount_cents INTEGER,
        reference_number TEXT,
        payment_date TEXT,
        
        -- Verification
        verified INTEGER DEFAULT 0,
        ocr_confidence REAL,
        
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        
        FOREIGN KEY (cash_transaction_id) REFERENCES cash_transactions(cash_transaction_id)
    )
''')

print("✅ Table 'payment_proofs' created")

# ============================================================================
# CREATE CASH WALLETS FOR EXISTING BUSINESSES
# ============================================================================

print("\n💼 Creating cash wallets for existing businesses...")

cursor.execute('SELECT business_id, business_name FROM businesses')
businesses = cursor.fetchall()

for business_id, business_name in businesses:
    cursor.execute('''
        INSERT INTO cash_wallets (
            business_id, 
            virtual_balance_cents,
            cash_on_hand_cents,
            wallet_status
        ) VALUES (?, 0, 0, 'ACTIVE')
    ''', (business_id,))
    
    wallet_id = cursor.lastrowid
    print(f"   ✅ Cash wallet created for: {business_name} (Wallet ID: {wallet_id})")

# ============================================================================
# CREATE INDEXES
# ============================================================================

print("\n🚀 Creating indexes...")

cursor.execute('CREATE INDEX IF NOT EXISTS idx_cash_wallet_business ON cash_wallets(business_id)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_cash_trans_wallet ON cash_transactions(wallet_id)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_reconciliations_wallet ON reconciliations(wallet_id)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_credit_ledger_wallet ON credit_ledger(wallet_id)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_credit_ledger_status ON credit_ledger(status)')

print("✅ Indexes created")

conn.commit()

print("\n" + "=" * 80)
print("🎉 CASH-BASED WALLET SYSTEM CREATED!")
print("=" * 80)
print("\nDESIGNED FOR INFORMAL ECONOMY:")
print("  ✅ Tracks physical cash (not a bank account)")
print("  ✅ Records eWallet/WhatsApp Pay receipts")
print("  ✅ Manages customer credit (book debts)")
print("  ✅ Weekly reconciliation (trust building)")
print("  ✅ SMS/WhatsApp proof storage")
print("\nTHIS IS WHAT TOWNSHIP BUSINESSES ACTUALLY NEED! 🇿🇦")
print("=" * 80)

conn.close()