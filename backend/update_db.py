import mysql.connector
from config import DB_CONFIG

def update_marks_table():
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"]
        )
        cursor = conn.cursor()
        
        # Check existing columns
        cursor.execute("SHOW COLUMNS FROM marks")
        columns = [col[0] for col in cursor.fetchall()]
        
        if 'exam_name' not in columns:
            cursor.execute("ALTER TABLE marks ADD COLUMN exam_name VARCHAR(100) AFTER student_id")
            print("Added exam_name column")
            
        if 'marks_obtained' not in columns:
            if 'marks' in columns:
                cursor.execute("ALTER TABLE marks CHANGE marks marks_obtained INT")
                print("Renamed marks to marks_obtained")
            else:
                cursor.execute("ALTER TABLE marks ADD COLUMN marks_obtained INT AFTER subject")
                print("Added marks_obtained column")

        if 'total_marks' not in columns:
            cursor.execute("ALTER TABLE marks ADD COLUMN total_marks INT DEFAULT 100 AFTER marks_obtained")
            print("Added total_marks column")

        conn.commit()
        cursor.close()
        conn.close()
        print("Marks table updated successfully.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

if __name__ == "__main__":
    update_marks_table()
