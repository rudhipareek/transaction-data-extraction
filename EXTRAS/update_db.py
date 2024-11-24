import sqlite3

# Define the database connection
conn = sqlite3.connect("student_fee_database.db")
cursor = conn.cursor()

# Drop any existing tables named 'student_records' or 'fee_status'
cursor.execute("DROP TABLE IF EXISTS student_records;")
cursor.execute("DROP TABLE IF EXISTS fee_status;")

# Create the new table named 'student_records'
cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        urn TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        parent_guardian_name TEXT,
        course_opted TEXT,
        year_of_study INTEGER,
        semester_of_study INTEGER,
        academic_year TEXT,
        other_details TEXT
    );
""")

# Create the new table for fee status
cursor.execute("""
    CREATE TABLE IF NOT EXISTS fee_status (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        urn TEXT NOT NULL,
        name TEXT NOT NULL,
        course_opted TEXT,
        year_of_study INTEGER,
        semester_of_study INTEGER,
        academic_year TEXT,
        total_amount REAL DEFAULT 0,
        amount_paid REAL DEFAULT 0,
        balance REAL DEFAULT 0,
        FOREIGN KEY(urn) REFERENCES student_records(urn)
    );
""")

# Insert sample student data into 'student_records' table
students = [
    ('URN001', 'Rudhi Pareek', 'Nilesh Pareek', 'B.Sc Computer Science', 2, 1, '2023-2024', 'N/A'),
    ('URN002', 'Vaikhari Kanetkar', 'Abhijeet Kanetkar', 'B.A Economics', 3, 2, '2022-2023', 'N/A'),
    ('URN003', 'Sanika Mendhalkar', 'Dilip Mendhalkar', 'B.Tech Mechanical Engineering', 1, 1, '2024-2025', 'N/A'),
    ('URN004', 'Ruchi Purohit', 'Rajesh Purohit', 'M.Sc Chemistry', 1, 1, '2023-2024', 'N/A')
]

# Insert sample data into student_records table if not already present
for student in students:
    cursor.execute("""
        INSERT OR IGNORE INTO student_records (urn, name, parent_guardian_name, course_opted, year_of_study, semester_of_study, academic_year, other_details)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, student)

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database updated with 'student_records' and 'fee_status' tables, and sample data inserted.")
