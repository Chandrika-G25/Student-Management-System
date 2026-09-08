import os
import ssl
from urllib.parse import urlparse, unquote
import pymysql
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

def parse_db_config():
    """Parse DB configuration from DATABASE_URL / MYSQL_URL or individual DB_* env variables."""
    database_url = os.environ.get("DATABASE_URL") or os.environ.get("MYSQL_URL")
    
    if database_url:
        parsed = urlparse(database_url)
        return {
            "host": parsed.hostname or "127.0.0.1",
            "port": parsed.port or 3306,
            "user": unquote(parsed.username) if parsed.username else "root",
            "password": unquote(parsed.password) if parsed.password else "",
            "database": parsed.path.lstrip("/") if parsed.path else "student_management",
            "ssl": True if "ssl" in database_url.lower() else None
        }

    port_env = os.environ.get("DB_PORT", "3306")
    try:
        port = int(port_env)
    except ValueError:
        port = 3306

    host = os.environ.get("DB_HOST", "127.0.0.1")
    # Auto-enable SSL for common cloud providers (TiDB Cloud, Aiven, etc.)
    auto_ssl = any(cloud in host.lower() for cloud in ["tidbcloud.com", "aivencloud.com", "railway.app"])
    ssl_env = os.environ.get("DB_SSL", "").strip().lower()
    enable_ssl = ssl_env in ("true", "1", "yes", "required") if ssl_env else auto_ssl

    return {
        "host": host,
        "port": port,
        "user": os.environ.get("DB_USER", "root"),
        "password": os.environ.get("DB_PASSWORD", "Chandu@1325"),
        "database": os.environ.get("DB_NAME", "student_management"),
        "ssl": enable_ssl
    }

DB_CONFIG = parse_db_config()

def get_ssl_context():
    """Construct an SSLContext suitable for cloud MySQL (e.g. TiDB, Aiven)."""
    try:
        ctx = ssl.create_default_context()
        # If DB_SSL_VERIFY is explicitly disabled, do not verify server certificate
        if os.environ.get("DB_SSL_VERIFY", "true").lower() in ("false", "0", "no"):
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        return ctx
    except Exception as e:
        print("Warning: Failed to create default SSL context:", e)
        return None

def get_db_connection(include_database=True):
    """
    Establish a connection to the MySQL database.
    If include_database is False, connects to the MySQL server without selecting a DB.
    """
    config = parse_db_config()
    connect_args = {
        "host": config["host"],
        "port": config["port"],
        "user": config["user"],
        "password": config["password"],
        "cursorclass": pymysql.cursors.DictCursor,
        "connect_timeout": 10
    }
    
    if include_database and config["database"]:
        connect_args["database"] = config["database"]

    if config["ssl"]:
        ssl_ctx = get_ssl_context()
        if ssl_ctx:
            connect_args["ssl"] = ssl_ctx

    try:
        connection = pymysql.connect(**connect_args)
        return connection
    except Exception as err:
        print(f"Database Connection Error ({config['host']}:{config['port']}):", err)
        return None