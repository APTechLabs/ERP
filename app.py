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
            # If admin has no password set yet
            if user_id == "aditya" and (user["password"] is None or user["password"] == ""):
                hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
                cursor.execute("UPDATE users SET password=%s WHERE user_id=%s", (hashed_pw, "aditya"))
                db.commit()
                session["user_id"] = "aditya"
                session["role"] = "admin"
                return redirect("/admin_dashboard")

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

# Student dashboard
@app.route("/student_dashboard")
def student_dashboard():
    if "user_id" in session and session["role"]=="student":
        user_id = session["user_id"]
        cursor.execute("SELECT * FROM students WHERE user_id=%s", (user_id,))
        student = cursor.fetchone()
        # You can also fetch fees, hostel, exams info here
        return render_template("student_dashboard.html", student=student)
    return redirect("/login")

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

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__=="__main__":
    app.run(debug=True)
