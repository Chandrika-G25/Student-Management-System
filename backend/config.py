import pymysql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "127.0.0.1"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", "chandu123"),
    "database": os.environ.get("DB_NAME", "student_management")
}

def get_db_connection():
    try:
        connection = pymysql.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection

    except Exception as err:
        print("Database Connection Error:", err)
        return None