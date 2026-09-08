from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)
import bcrypt

from config import get_db_connection

auth_bp = Blueprint("auth", __name__)

# =====================================
# REGISTER USER
# =====================================

@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "student")

    if not username or not email or not password:
        return jsonify({
            "success": False,
            "message": "All fields required"
        }), 400

    connection = get_db_connection()

    if not connection:
        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email=%s",
        (email,)
    )

    existing_user = cursor.fetchone()

    if existing_user:
        return jsonify({
            "success": False,
            "message": "Email already exists"
        }), 400

    hashed_password = bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    )

    cursor.execute(
        """
        INSERT INTO users
        (username,email,password,role)
        VALUES(%s,%s,%s,%s)
        """,
        (
            username,
            email,
            hashed_password.decode('utf-8'),
            role
        )
    )

    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({
        "success": True,
        "message": "User Registered Successfully"
    })


# =====================================
# LOGIN USER
# =====================================

@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    connection = get_db_connection()
    if not connection:
        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = connection.cursor()
    
    try:
        cursor.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        user = cursor.fetchone()

        cursor.close()
        connection.close()
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    if not user:
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    if bcrypt.checkpw(
        password.encode("utf-8"),
        user["password"].encode("utf-8")
    ):

        access_token = create_access_token(
            identity=str(user["id"])
        )

        return jsonify({
            "success": True,
            "token": access_token,
            "role": user["role"],
            "username": user["username"]
        })

    return jsonify({
        "success": False,
        "message": "Invalid Password"
    }), 401


# =====================================
# CURRENT USER
# =====================================

@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    
    connection = get_db_connection()
    if not connection:
        return jsonify({"success": False, "message": "Database error"}), 500
        
    cursor = connection.cursor()
    cursor.execute("SELECT id, username, email, role FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    connection.close()

    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    return jsonify({
        "success": True,
        "user": user
    })


# =====================================
# ADMIN ONLY ROUTE
# =====================================

@auth_bp.route("/admin-dashboard")
@jwt_required()
def admin_dashboard():
    user_id = get_jwt_identity()
    
    connection = get_db_connection()
    if not connection:
        return jsonify({"success": False, "message": "Database error"}), 500
        
    cursor = connection.cursor()
    cursor.execute("SELECT role FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    connection.close()

    if not user or user["role"] != "admin":
        return jsonify({
            "success": False,
            "message": "Access Denied"
        }), 403

    return jsonify({
        "success": True,
        "message": "Welcome Admin"
    })