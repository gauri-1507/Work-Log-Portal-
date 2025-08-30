import sqlite3

# Connect to (or create) a new SQLite database file
conn = sqlite3.connect('worklog.db')
cursor = conn.cursor()

# Drop the old submissions table if it exists
cursor.execute("DROP TABLE IF EXISTS submissions")

# Create a fresh submissions table with project_name column included
cursor.execute('''
CREATE TABLE submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    work TEXT NOT NULL,
    date TEXT NOT NULL,
    project_name TEXT
)
''')

conn.commit()
conn.close()

print("✅ New table created successfully with project_name column.")
