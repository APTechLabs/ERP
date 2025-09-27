from flask import Flask, render_template, request, redirect, session
import mysql.connector
import random
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = "supersecretkey"
bcrypt = Bcrypt(app)

# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="erpuser",
    password="erppassword",
    database="student_erp"
)

cursor = db.cursor(dictionary=True)

# Generate unique AP ID
def generate_user_id():
    while True:
        user_id = "AP" + str(random.randint(1000000, 9999999))
        cursor.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
        if not cursor.fetchone():
            return user_id

# ----------------- Routes -----------------

@app.route("/")
def home():
    return redirect("/login")

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_id = request.form["user_id"]
        password = request.form["password"].encode('utf-8')

        cursor.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
        user = cursor.fetchone()

        if user:
            # Normal login check
            if bcrypt.check_password_hash(user["password"], password):
                session["user_id"] = user_id
                session["role"] = user["role"]
                if user["role"] == "student":
                    return redirect("/student_dashboard")
                else:
                    return redirect("/admin_dashboard")
        return "Invalid ID or password"
    return render_template("login.html")


# Register new student
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        full_name = request.form["full_name"]
        dob = request.form["dob"]
        email = request.form["email"]
        phone = request.form["phone"]
        address = request.form["address"]
        password = request.form["password"].encode('utf-8')
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        user_id = generate_user_id()

        # Insert into users
        cursor.execute("INSERT INTO users (user_id, password, role) VALUES (%s,%s,'student')",
                       (user_id, hashed_pw))
        # Insert into students
        cursor.execute("""INSERT INTO students (user_id, full_name, dob, email, phone, address)
                          VALUES (%s,%s,%s,%s,%s,%s)""",
                       (user_id, full_name, dob, email, phone, address))
        db.commit()
        return f"Registered successfully! Your unique ID is: {user_id}"
    return render_template("register.html")

# Admin dashboard
@app.route("/admin_dashboard")
def admin_dashboard():
    if "user_id" not in session or session["role"] != "admin":
        return redirect("/login")

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT user_id, full_name, email, phone FROM students")
    students = cursor.fetchall()
    cursor.close()

    return render_template("admin_dashboard.html", students=students)

# Edit student
@app.route("/edit_student/<user_id>", methods=["GET", "POST"])
def edit_student(user_id):
    if "user_id" not in session or session["role"] != "admin":
        return redirect("/login")

    # GET → fetch student and show pre-filled form
    if request.method == "GET":
        cursor.execute("SELECT * FROM students WHERE user_id=%s", (user_id,))
        student = cursor.fetchone()
        if not student:
            return "Student not found"
        return render_template("register.html", student=student)

    # POST → update student info
    if request.method == "POST":
        full_name = request.form["full_name"]
        dob = request.form["dob"]
        email = request.form["email"]
        phone = request.form["phone"]
        address = request.form["address"]

        cursor.execute("""
            UPDATE students
            SET full_name=%s, dob=%s, email=%s, phone=%s, address=%s
            WHERE user_id=%s
        """, (full_name, dob, email, phone, address, user_id))
        db.commit()

        return redirect("/admin_dashboard")

# Delete student
@app.route("/delete_student/<user_id>", methods=["GET"])
def delete_student(user_id):
    if "user_id" not in session or session["role"] != "admin":
        return redirect("/login")

    # Remove from both tables
    cursor.execute("DELETE FROM students WHERE user_id=%s", (user_id,))
    cursor.execute("DELETE FROM users WHERE user_id=%s", (user_id,))
    db.commit()

    return redirect("/admin_dashboard")

@app.route("/student_dashboard")
def student_dashboard():
    if "user_id" in session and session["role"] == "student":
        user_id = session["user_id"]

        # Student info
        cursor.execute("SELECT * FROM students WHERE user_id=%s", (user_id,))
        student = cursor.fetchone()

        # Fees
        cursor.execute("SELECT * FROM fees WHERE user_id=%s", (user_id,))
        fees = cursor.fetchall()

        # Exams (schedule + results)
        cursor.execute("SELECT * FROM exams WHERE user_id=%s", (user_id,))
        exams = cursor.fetchall()

        # Notices (global, visible to all students)
        cursor.execute("SELECT * FROM notices ORDER BY date DESC")
        notices = cursor.fetchall()

        # Attendance
        cursor.execute("SELECT * FROM attendance WHERE user_id=%s", (user_id,))
        attendance_records = cursor.fetchall()

        present = sum(1 for a in attendance_records if a['status'].lower() == 'present')
        absent = sum(1 for a in attendance_records if a['status'].lower() == 'absent')

        attendance = {
            "present": present,
            "absent": absent
        }


        # Leave notes
        cursor.execute("SELECT * FROM leave_notes WHERE user_id=%s", (user_id,))
        leaves = cursor.fetchall()

        return render_template("student_dashboard.html",
                               student=student,
                               fees=fees,
                               exams=exams,
                               notices=notices,
                               attendance=attendance,
                               leaves=leaves)
    return redirect("/login")


    total_days = present + absent
    attendance_percentage = round((present / total_days * 100), 2) if total_days > 0 else 0
    attendance = {
        "present": present,
        "absent": absent,
        "percentage": attendance_percentage
    }

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__=="__main__":
    app.run(debug=True)
