@app.route('/admin')
def admin_dashboard():
    if 'role' in session and session['role'] == 'admin':
        conn = get_db_connection()
        submissions = conn.execute("SELECT * FROM submissions").fetchall()
        conn.close()
        return render_template("admin.html", submissions=submissions)
    
    submissions = conn.execute("SELECT * FROM submissions").fetchall()
    retu