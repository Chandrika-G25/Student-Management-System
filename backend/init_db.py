import pymysql
import bcrypt
from config import DB_CONFIG, get_db_connection

def setup_database():
    """
    Initialize tables and default admin account.
    Returns (True, message) on success, or (False, error_message) on failure.
    """
    conn = None
    try:
        # Step 1: Try connecting directly to the specified database
        conn = get_db_connection(include_database=True)

        # If connecting with DB name fails (e.g., database doesn't exist yet on local server),
        # try connecting without selecting a DB and create it.
        if not conn:
            print(f"Connecting to MySQL server to create '{DB_CONFIG['database']}'...")
            root_conn = get_db_connection(include_database=False)
            if not root_conn:
                return False, "Could not connect to MySQL server. Check your credentials."
            
            with root_conn.cursor() as cur:
                cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}`")
            root_conn.commit()
            root_conn.close()

            # Now connect to the newly created database
            conn = get_db_connection(include_database=True)
            if not conn:
                return False, f"Database created, but failed to connect to '{DB_CONFIG['database']}'."

        cursor = conn.cursor()
        
        # Step 2: Define table schemas
        tables = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(100) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role ENUM('admin','student') DEFAULT 'student',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
            """
            CREATE TABLE IF NOT EXISTS attendance (
                id INT PRIMARY KEY AUTO_INCREMENT,
                student_id INT,
                attendance_date DATE,
                status ENUM('Present','Absent') NOT NULL,
                FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        ]

        for table in tables:
            cursor.execute(table)
        print("Database tables verified/created successfully.")

        # Step 3: Verify or create default Admin user
        cursor.execute("SELECT * FROM users WHERE email = %s", ('admin@gmail.com',))
        existing_user = cursor.fetchone()
        hashed_pw = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        if not existing_user:
            cursor.execute(
                "INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
                ('admin', 'admin@gmail.com', hashed_pw, 'admin')
            )
            conn.commit()
            print("Default admin created: admin@gmail.com / admin123")
        else:
            # Check if existing hash is valid or needs update
            current_hash = existing_user.get("password") if isinstance(existing_user, dict) else existing_user[3]
            try:
                if not bcrypt.checkpw("admin123".encode('utf-8'), current_hash.encode('utf-8')):
                    cursor.execute(
                        "UPDATE users SET password = %s WHERE email = %s",
                        (hashed_pw, 'admin@gmail.com')
                    )
                    conn.commit()
                    print("Admin password updated to 'admin123'")
            except Exception:
                cursor.execute(
                    "UPDATE users SET password = %s WHERE email = %s",
                    (hashed_pw, 'admin@gmail.com')
                )
                conn.commit()
                print("Admin password repaired to 'admin123'")

        cursor.close()
        conn.close()
        return True, "Database initialization completed successfully!"

    except Exception as err:
        print(f"Database Setup Error: {err}")
        if conn:
            try:
                conn.close()
            except Exception:
                pass
        return False, str(err)

if __name__ == "__main__":
    success, msg = setup_database()
    print(msg)

