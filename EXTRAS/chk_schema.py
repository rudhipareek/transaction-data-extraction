import sqlite3

# Define the database connection
conn = sqlite3.connect("student_fee_database.db")
cursor = conn.cursor()

# Check existing table schema
cursor.execute("PRAGMA table_info(student_records);")
schema = cursor.fetchall()

for column in schema:
    print(column)

conn.close()
