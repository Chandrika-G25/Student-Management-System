-- Create Database
CREATE DATABASE IF NOT EXISTS student_management;

USE student_management;

-- =====================================
-- USERS TABLE
-- =====================================

CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin','student') DEFAULT 'student',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================
-- STUDENTS TABLE
-- =====================================

CREATE TABLE students (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id VARCHAR(20) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15),
    gender ENUM('Male','Female','Other'),
    dob DATE,
    course VARCHAR(100),
    address TEXT,
    photo VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================
-- ATTENDANCE TABLE
-- =====================================

CREATE TABLE attendance (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT,
    attendance_date DATE,
    status ENUM('Present','Absent') NOT NULL,

    FOREIGN KEY(student_id)
    REFERENCES students(id)
    ON DELETE CASCADE
);

-- =====================================
-- MARKS TABLE
-- =====================================

CREATE TABLE marks (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT,
    subject VARCHAR(100),
    marks INT,

    FOREIGN KEY(student_id)
    REFERENCES students(id)
    ON DELETE CASCADE
);

-- =====================================
-- COURSES TABLE
-- =====================================

CREATE TABLE courses (
    id INT PRIMARY KEY AUTO_INCREMENT,
    course_name VARCHAR(100) NOT NULL,
    duration VARCHAR(50),
    fee DECIMAL(10,2)
);

-- =====================================
-- REPORTS TABLE
-- =====================================

CREATE TABLE reports (
    id INT PRIMARY KEY AUTO_INCREMENT,
    report_name VARCHAR(100),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================
-- ADMIN LOGS
-- =====================================

CREATE TABLE admin_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    admin_name VARCHAR(100),
    action_performed TEXT,
    action_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================
-- SAMPLE ADMIN ACCOUNT
-- Password = admin123
-- =====================================

INSERT INTO users
(username,email,password,role)
VALUES
(
'admin',
'admin@gmail.com',
'$2b$12$t7E5LcTPMH./fTZgO/DMc.B40lAWypjmtyrobqpmXrI.L1AdZteYW',
'admin'
);

-- =====================================
-- SAMPLE STUDENTS
-- =====================================

INSERT INTO students
(student_id,full_name,email,phone,gender,dob,course,address)
VALUES
(
'STU001',
'Rahul Kumar',
'rahul@gmail.com',
'9876543210',
'Male',
'2003-05-12',
'B.Tech CSE',
'Hyderabad'
),

(
'STU002',
'Priya Sharma',
'priya@gmail.com',
'9876543211',
'Female',
'2004-01-10',
'B.Tech ECE',
'Bangalore'
);