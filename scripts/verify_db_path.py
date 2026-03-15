"""
Verify which database is being used
"""

import os
import sqlite3

print("=" * 80)
print("🔍 Database Path Verification")
print("=" * 80)

# Check all possible database locations
paths = [
    os.path.join('..', 'database', 'mzansipulse.db'),
    os.path.join('..', 'database', 'mzansipulse_live.db'),
    'mzansipulse.db',
    '../database/mzansipulse.db'
]

for path in paths:
    full_path = os.path.abspath(path)
    exists = os.path.exists(full_path)
    
    print(f"\n📂 {path}")
    print(f"   Full path: {full_path}")
    print(f"   Exists: {'✅ YES' if exists else '❌ NO'}")
    
    if exists:
        try:
            conn = sqlite3.connect(full_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM cash_transactions")
            count = cursor.fetchone()[0]
            print(f"   Transactions: {count}")
            conn.close()
        except Exception as e:
            print(f"   Error: {e}")

print("\n" + "=" * 80)