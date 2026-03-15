"""
Add authentication fields to users table
Adds: password_hash, email, last_login, is_active
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join('..', 'database', 'mzansipulse.db')

print("=" * 80)
print("🔐 Adding Authentication Fields to Users Table")
print("=" * 80)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Check if columns already exist
cursor.execute("PRAGMA table_info(users)")
columns = [col[1] for col in cursor.fetchall()]
print(f"\n📋 Current columns: {columns}")

# Add columns one by one with error handling
columns_to_add = [
    ('email', 'TEXT'),
    ('password_hash', 'TEXT'),
    ('last_login', 'TEXT'),
    ('is_active', 'INTEGER DEFAULT 1'),
    ('created_at_timestamp', 'TEXT')
]

for col_name, col_type in columns_to_add:
    if col_name not in columns:
        try:
            # Add column without UNIQUE constraint first
            cursor.execute(f'ALTER TABLE users ADD COLUMN {col_name} {col_type}')
            print(f"✅ Added column: {col_name}")
        except sqlite3.Error as e:
            print(f"⚠️  Could not add {col_name}: {e}")
    else:
        print(f"ℹ️  Column {col_name} already exists")

conn.commit()

# Now update existing users with email based on phone number
print("\n📝 Updating existing users...")

try:
    cursor.execute('''
        UPDATE users 
        SET email = phone_number || '@mzansipulse.local'
        WHERE email IS NULL
    ''')
    print(f"✅ Updated {cursor.rowcount} users with default email")
except sqlite3.Error as e:
    print(f"⚠️  Could not update emails: {e}")

try:
    cursor.execute('''
        UPDATE users 
        SET password_hash = 'demo_hash_12345'
        WHERE password_hash IS NULL
    ''')
    print(f"✅ Updated {cursor.rowcount} users with default password")
except sqlite3.Error as e:
    print(f"⚠️  Could not update passwords: {e}")

try:
    cursor.execute('''
        UPDATE users 
        SET is_active = 1
        WHERE is_active IS NULL
    ''')
    print(f"✅ Updated {cursor.rowcount} users with active status")
except sqlite3.Error as e:
    print(f"⚠️  Could not update active status: {e}")

try:
    cursor.execute('''
        UPDATE users 
        SET created_at_timestamp = CURRENT_TIMESTAMP
        WHERE created_at_timestamp IS NULL
    ''')
    print(f"✅ Updated {cursor.rowcount} users with timestamp")
except sqlite3.Error as e:
    print(f"⚠️  Could not update timestamps: {e}")

conn.commit()

print("\n" + "=" * 80)
print("✅ Authentication fields migration completed!")
print("=" * 80)

# Verify final schema
cursor.execute("PRAGMA table_info(users)")
print("\n📋 Final users table schema:")
for col in cursor.fetchall():
    print(f"   • {col[1]:25s} {col[2]:15s} {'NOT NULL' if col[3] else ''}")

# Show sample data
print("\n📊 Sample users:")
cursor.execute('''
    SELECT user_id, first_name, last_name, phone_number, email, is_active
    FROM users
    LIMIT 5
''')

for row in cursor.fetchall():
    print(f"   • ID:{row[0]} | {row[1]} {row[2]} | {row[3]} | {row[4]} | Active:{row[5]}")

print("\n" + "=" * 80)
print("🎉 Ready for authentication!")
print("=" * 80)

conn.close()