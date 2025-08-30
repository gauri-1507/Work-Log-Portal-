import sqlite3
import os


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
db_path = os.path.join(BASE_DIR, 'worklog.db')

conn = sqlite3.connect(db_path)
print("Connected to DB at:", db_path)
cursor = conn.cursor()


cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        department TEXT
    )
''')
print("Users table created.")

cursor.execute('''
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        assigned_to INTEGER,
        due_date TEXT,
        FOREIGN KEY (assigned_to) REFERENCES users(id)
    )
''')
print("Projects table created.")


cursor.execute('''
    CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        project_id INTEGER,
        date TEXT,
        work_update TEXT,
        file_path TEXT,
        completed INTEGER DEFAULT 0,
        FOREIGN KEY (employee_id) REFERENCES users(id),
        FOREIGN KEY (project_id) REFERENCES projects(id)
    )
''')
print("Submissions table created.")


cursor.execute("INSERT OR IGNORE INTO users (name, email, password, role, department) VALUES (?, ?, ?, ?, ?)", 
               ('Admin User', 'admin@example.com', 'admin123', 'admin', 'AdminDept'))

cursor.execute("INSERT OR IGNORE INTO users (name, email, password, role, department) VALUES (?, ?, ?, ?, ?)", 
               ('Employee One', 'emp1@example.com', 'emp123', 'employee', 'Engineering'))

conn.commit()
conn.close()
