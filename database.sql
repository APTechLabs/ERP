DROP DATABASE IF EXISTS student_erp;
CREATE DATABASE student_erp;
USE student_erp;

-- Users table (Main identity store)
CREATE TABLE users (
    user_id VARCHAR(9) PRIMARY KEY,       -- APxxxxxxx
    password VARCHAR(255) NOT NULL,       -- hashed password
    role ENUM('student','admin') NOT NULL DEFAULT 'student'
);

-- Student details
CREATE TABLE students (
    user_id VARCHAR(9) PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    dob DATE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15),
    address TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Fees
CREATE TABLE fees (
    fee_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(9) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    paid DECIMAL(10,2) DEFAULT 0,
    due_date DATE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Hostel
CREATE TABLE hostel (
    hostel_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(9) NOT NULL,
    room_no VARCHAR(10),
    join_date DATE,
    leave_date DATE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Exams (Schedule + Results together)
CREATE TABLE exams (
    exam_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(9) NOT NULL,
    subject VARCHAR(50) NOT NULL,
    exam_date DATE,
    time TIME,
    marks INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Notices (visible to all students)
CREATE TABLE notices (
    notice_id INT AUTO_INCREMENT PRIMARY KEY,
    message TEXT NOT NULL,
    date DATE DEFAULT (CURRENT_DATE)
);

-- Attendance
CREATE TABLE attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(9) NOT NULL,
    date DATE NOT NULL,
    status ENUM('present','absent') NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Leave Notes
CREATE TABLE leave_notes (
    note_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(9) NOT NULL,
    text TEXT NOT NULL,
    date DATE DEFAULT (CURRENT_DATE),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
