import mysql.connector
from config import DB_CONFIG
import bcrypt

def setup_database():
    try:
        # Connect without database first to create it
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"]
        )
        cursor = conn.cursor()
        
        # Create Database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        print(f"Database {DB_CONFIG['database']} checked/created.")
        
        # Connect to the database
        cursor.execute(f"USE {DB_CONFIG['database']}")
        
        # Create Tables
        tables = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(100) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role ENUM('admin','student') DEFAULT 'student',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS students (
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
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS attendance (
                id INT PRIMARY KEY AUTO_INCREMENT,
                student_id INT,
                attendance_date DATE,
                status ENUM('Present','Absent') NOT NULL,
                FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS marks (
                id INT PRIMARY KEY AUTO_INCREMENT,
                student_id INT,
                exam_name VARCHAR(100),
                subject VARCHAR(100),
                marks_obtained INT,
                total_marks INT DEFAULT 100,
                FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS fees (
                id INT PRIMARY KEY AUTO_INCREMENT,
                student_id INT,
                total_fee DECIMAL(10,2),
                paid_amount DECIMAL(10,2),
                payment_date DATE,
                payment_method VARCHAR(50),
                remarks TEXT,
                FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
            )
            """
        ]
        
        for table in tables:
            cursor.execute(table)
        print("Tables checked/created.")
        
        # Add Admin User if not exists, or verify/repair its password if it does exist
        cursor.execute("SELECT * FROM users WHERE email = %s", ('admin@gmail.com',))
        existing_user = cursor.fetchone()
        hashed_pw = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        if not existing_user:
            cursor.execute(
                "INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
                ('admin', 'admin@gmail.com', hashed_pw, 'admin')
            )
            conn.commit()
            print("Default admin created (admin@gmail.com / admin123)")
        else:
            # users table schema: id, username, email, password, role, created_at
            # since init_db uses a standard cursor (returns tuple), password is index 3
            current_hash = existing_user[3]
            try:
                if not bcrypt.checkpw("admin123".encode('utf-8'), current_hash.encode('utf-8')):
                    cursor.execute(
                        "UPDATE users SET password = %s WHERE email = %s",
                        (hashed_pw, 'admin@gmail.com')
                    )
                    conn.commit()
                    print("Admin password updated to 'admin123' (hash was invalid)")
            except Exception:
                # If checking bcrypt raises an exception due to a corrupted/malformed hash, reset it
                cursor.execute(
                    "UPDATE users SET password = %s WHERE email = %s",
                    (hashed_pw, 'admin@gmail.com')
                )
                conn.commit()
                print("Admin password reset to 'admin123' (old hash format was malformed)")
        
        cursor.close()
        conn.close()
        print("Setup Complete!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

if __name__ == "__main__":
    setup_database()
