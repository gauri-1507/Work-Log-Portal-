import sqlite3

conn = sqlite3.connect("worklog.db")
cursor = conn.cursor()

# Drop the old table if it exists
cursor.execute("DROP TABLE IF EXISTS submissions")

# Create the new table with the correct columns
cursor.execute("""
    CREATE TABLE submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        project_name TEXT,
        work_done TEXT,
        file_path TEXT,
        date TEXT
    )
""")

conn.commit()
conn.close()

print("✅ submissions table dropped and recreated successfully.")
