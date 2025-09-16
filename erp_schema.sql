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
    amount DECIMAL(10,2) NOT NULL,
    status ENUM('paid','unpaid') DEFAULT 'unpaid',
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

-- Exams
CREATE TABLE exams (
    exam_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(9) NOT NULL,
    subject VARCHAR(50) NOT NULL,
    marks INT,
    exam_date DATE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
