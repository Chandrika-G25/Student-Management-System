import mysql.connector
import os
from config import DB_CONFIG

def migrate():
    print(f"Connecting to database at {DB_CONFIG['host']}...")
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"]
        )
        cursor = conn.cursor()

        # Read the SQL file
        sql_path = os.path.join(os.path.dirname(__file__), "database.sql")
        with open(sql_path, 'r') as f:
            sql_commands = f.read().split(';')

        print("Executing migrations...")
        for command in sql_commands:
            if command.strip():
                try:
                    cursor.execute(command)
                except mysql.connector.Error as e:
                    print(f"Skipping command due to error: {e}")

        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Migration completed successfully!")

    except mysql.connector.Error as err:
        print(f"❌ Connection Error: {err}")
        print("\nTIP: If you are connecting to Railway, make sure your .env file or environment variables are set correctly.")

if __name__ == "__main__":
    migrate()
