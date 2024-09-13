import sqlite3

# Define the database connection
conn = sqlite3.connect("student_fee_database.db")
cursor = conn.cursor()

# Create a table for student records if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY,
        name TEXT,
        fee_status TEXT,
        parent_guardian_name TEXT  -- Column to store parent/guardian name
    );
""")

# Create a table for transaction data if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY,
        student_id INTEGER,
        transaction_date TEXT,
        transaction_amount REAL,
        transaction_id TEXT,
        payment_method TEXT,
        sender TEXT  -- This already stores the sender information
    );
""")

conn.commit()
conn.close()
