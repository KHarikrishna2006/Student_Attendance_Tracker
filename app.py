from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
from datetime import date

app = Flask(__name__)
app.secret_key = "secret123"

# Database connection helper
def get_db():
    con = sqlite3.connect("attendance.db")
    con.row_factory = sqlite3.Row
    return con
# Show students with delete option
@app.route("/students")
def students():
    con = sqlite3.connect("attendance.db")
    cur = con.cursor()
    cur.execute("SELECT id, name FROM students")
    students = cur.fetchall()
    con.close()
    return render_template("students.html", students=students)

# Delete student
@app.route("/delete/<int:id>")
def delete_student(id):
    con = sqlite3.connect("attendance.db")
    cur = con.cursor()
    cur.execute("DELETE FROM students WHERE id = ?", (id,))
    con.commit()
    con.close()
    return redirect(url_for("students"))

# ------------------ LOGIN ------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        con = get_db()
        cur = con.cursor()
        cur.execute("SELECT * FROM teachers WHERE username=? AND password=?", (username, password))
        teacher = cur.fetchone()

        if teacher:
            session["teacher"] = teacher["username"]
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

# ------------------ DASHBOARD ------------------
@app.route("/dashboard")
def dashboard():
    if "teacher" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html")

# ------------------ ADD STUDENT ------------------
@app.route("/add_student", methods=["GET", "POST"])
def add_student():
    if "teacher" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form["name"]
        con = get_db()
        cur = con.cursor()
        cur.execute("INSERT INTO students (name) VALUES (?)", (name,))
        con.commit()
        return redirect(url_for("dashboard"))
    return render_template("add_student.html")

# ------------------ MARK ATTENDANCE ------------------
@app.route("/mark_attendance", methods=["GET", "POST"])
def mark_attendance():
    if "teacher" not in session:
        return redirect(url_for("login"))

    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM students")
    students = cur.fetchall()

    if request.method == "POST":
        for student in students:
            status = request.form.get(str(student["id"]))
            cur.execute("INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)",
                        (student["id"], str(date.today()), status))
        con.commit()
        return redirect(url_for("dashboard"))

    # ✅ Pass today's date into template
    return render_template("mark_attendance.html", students=students, today=date.today())

# ------------------ VIEW REPORT ------------------
@app.route("/report")
def report():
    if "teacher" not in session:
        return redirect(url_for("login"))

    con = get_db()
    cur = con.cursor()
    cur.execute("""SELECT students.name, attendance.date, attendance.status
                   FROM attendance
                   JOIN students ON students.id = attendance.student_id
                   ORDER BY attendance.date DESC""")
    records = cur.fetchall()
    return render_template("report.html", records=records)

# ------------------ LOGOUT ------------------
@app.route("/logout")
def logout():
    session.pop("teacher", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
