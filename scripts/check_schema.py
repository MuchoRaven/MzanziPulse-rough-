import sqlite3
import os

DB_PATH = os.path.join('..', 'database', 'mzansipulse.db')

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=" * 80)
print("🔍 Checking cash_transactions schema")
print("=" * 80)

cursor.execute("PRAGMA table_info(cash_transactions)")
columns = cursor.fetchall()

print("\n📋 Columns in cash_transactions table:\n")
for col in columns:
    pk_marker = " ← PRIMARY KEY" if col[5] == 1 else ""
    print(f"   • {col[1]:25s} {col[2]:15s}{pk_marker}")

print("\n" + "=" * 80)

# Check if there are any transactions
cursor.execute("SELECT COUNT(*) FROM cash_transactions")
count = cursor.fetchone()[0]
print(f"📊 Total transactions in database: {count}")

if count > 0:
    # Show first transaction with all columns
    cursor.execute("SELECT * FROM cash_transactions LIMIT 1")
    row = cursor.fetchone()
    column_names = [description[0] for description in cursor.description]
    
    print("\n📄 Sample transaction (first row):\n")
    for col_name, value in zip(column_names, row):
        print(f"   {col_name:25s} = {value}")

conn.close()
print("\n" + "=" * 80)