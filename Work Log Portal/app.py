from flask import Flask, render_template, request, redirect, session, url_for, send_from_directory, jsonify,flash

from werkzeug.utils import secure_filename
import sqlite3
import os
from datetime import datetime

import sqlite3
conn = sqlite3.connect('your_database_name.db')
cur = conn.cursor()
cur.execute("SELECT * FROM projects")
print(cur.fetchall())


app = Flask(__name__)
app.secret_key = 'secret_key' 
DB_PATH = 'users.db'

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_db_connection():
    conn = sqlite3.connect('worklog.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_assigned_work_table():
    conn = sqlite3.connect('worklog.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS assigned_work (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT,
            project_name TEXT,
            task_description TEXT,
            due_date TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

create_assigned_work_table()

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password)).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['employee_name'] = user['name']
            session['role'] = user['role']

            if user['role'] == 'employee':
                session['employee_id'] = user['id']  

            if user['role'] == 'admin':
                return redirect('/admin')
            else:
                return redirect('/employee')
        else:
            return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')


@app.route('/admin', methods=["GET", "POST"])
def admin():
    conn = get_db_connection()
    cursor = conn.cursor()

    
    employee_id = request.args.get('employee_id')
    project = request.args.get('project')
    status = request.args.get('status')
    date = request.args.get('date')

    
    query = "SELECT * FROM submissions WHERE 1=1"
    params = []

    
    if employee_id:
        query += " AND employee_id = ?"
        params.append(employee_id)
    if project:
        query += " AND project_name = ?"
        params.append(project)
    if status:
        query += " AND status = ?"
        params.append(status)
    if date:
        query += " AND date = ?"
        params.append(date)

    cursor.execute(query, params)
    submissions = cursor.fetchall()
    conn.close()
    filters_applied = any([employee_id, project, status, date])

    return render_template("admin.html", submissions=submissions, show_submissions=filters_applied)

    

@app.route("/admin/assign", methods=["GET", "POST"])
def assign_work():
    if request.method == "POST":
        
        employee_id = request.form['employee_id']
        project_name = request.form['project_name']
        task_description = request.form['description']
        due_date = request.form['due_date']

        conn = get_db_connection()
        conn.execute("""
            INSERT INTO assigned_work (employee_id, project_name, task_description, due_date, status)
            VALUES (?, ?, ?, ?, ?)
        """, (employee_id, project_name, task_description, due_date, 'Pending'))
        conn.commit()
        conn.close()

        flash("Work assigned successfully!", "success")
        return redirect(url_for('admin'))


    
    return "Assignment Form"



@app.route("/admin/submissions")
def admin_submissions():
    
    conn = get_db_connection()
    logs = conn.execute("SELECT * FROM submissions").fetchall()
    conn.close()
    return render_template("admin.html", logs=logs)
  


@app.route('/employee', methods=["GET", "POST"])
def employee():
    conn = get_db_connection()
    employee_id = session['user_id']

    if request.method == 'POST':
        project_name = request.form['project']
        work = request.form['work']
        file = request.files.get('file')  

        filename = None  

        if file and file.filename != '':
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

        conn.execute('''
            INSERT INTO submissions (employee_id, project_name, work_done, file_path, date)
            VALUES (?, ?, ?, ?, ?)
        ''', (employee_id, project_name, work, filename, datetime.now().strftime("%Y-%m-%d")))
        conn.commit()

        flash(" Work submitted successfully!")  
        return redirect('/employee')  


    assigned_projects = conn.execute('''
        SELECT DISTINCT project_name FROM assigned_work
        WHERE employee_id = ?
    ''', (employee_id,)).fetchall()

    conn.close()
    return render_template("employee.html", projects=assigned_projects)



@app.route('/testdb')
def testdb():
    conn = get_db_connection()
    result = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    return str(result)





@app.route('/employee/history')
def employee_history():
    if 'user_id' not in session or session.get('role') != 'employee':
        return redirect(url_for('login'))

    conn = get_db_connection()
    submissions = conn.execute('''
        SELECT date, project_name, work_done, file_path
        FROM submissions
        WHERE employee_id = ?
        ORDER BY date DESC
    ''', (session['user_id'],)).fetchall()
    conn.close()
    
    return render_template('history.html', submissions=submissions)



@app.route('/get_assigned_work')
def get_assigned_work():
    if 'user_id' not in session:
        return jsonify([])

    employee_id = session['user_id']
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT project_name, task_description, due_date, status
        FROM assigned_work
        WHERE employee_id = ?
    """, (employee_id,)).fetchall()
    conn.close()

    data = [dict(row) for row in rows]
    return jsonify(data)




@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')



if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
