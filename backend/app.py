
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required
from config import get_db_connection
from auth import auth_bp

app = Flask(__name__, 
            static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend")), 
            static_url_path="")
app.config["JWT_SECRET_KEY"] = "student_management_secret_key_change_me"

CORS(app)
jwt = JWTManager(app)

app.register_blueprint(auth_bp)

# ---------------- DEBUG ROUTES ----------------

@app.route("/test-db")
def test_db():
    conn = get_db_connection()
    if conn:
        conn.close()
        return jsonify({"status": "Online", "database": "Connected", "path": os.getcwd()})
    return jsonify({"status": "Online", "database": "Connection Failed", "path": os.getcwd()}), 500

# ---------------- STATIC FILES ----------------

@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "login.html")

@app.route("/<path:path>")
def serve_static(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return jsonify({"error": "Not Found"}), 404

# ---------------- STUDENTS ----------------

@app.route("/students", methods=["GET"])
@jwt_required()
def get_students():
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Database connection error"}), 500
    
    cur = conn.cursor()
    cur.execute("SELECT * FROM students ORDER BY id DESC")
    data = cur.fetchall()
    cur.close()
    conn.close()
    
    # Format date and datetime objects for JSON serialization
    for row in data:
        if row.get('dob') and hasattr(row['dob'], 'strftime'):
            row['dob'] = row['dob'].strftime('%Y-%m-%d')
        if row.get('created_at') and hasattr(row['created_at'], 'strftime'):
            row['created_at'] = row['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            
    return jsonify(data)

@app.route("/students", methods=["POST"])
@jwt_required()
def add_student():
    data = request.get_json()

    if not data or "student_id" not in data or "full_name" not in data:
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Database connection error"}), 500
        
    cur = conn.cursor()

    sql = """
    INSERT INTO students
    (student_id, full_name, email, phone, gender, dob, course, address)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """

    values = (
        data["student_id"],
        data["full_name"],
        data["email"],
        data.get("phone"),
        data.get("gender"),
        data.get("dob"),
        data.get("course"),
        data.get("address")
    )

    try:
        cur.execute(sql, values)
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True, "message": "Student added"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/students/<int:id>", methods=["PUT"])
@jwt_required()
def update_student(id):
    data = request.get_json()

    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Database connection error"}), 500
        
    cur = conn.cursor()

    try:
        cur.execute("""
        UPDATE students
        SET full_name=%s,email=%s,phone=%s,course=%s,address=%s
        WHERE id=%s
        """, (
            data.get("full_name"),
            data.get("email"),
            data.get("phone"),
            data.get("course"),
            data.get("address"),
            id
        ))

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True, "message": "Student updated"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/students/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_student(id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Database connection error"}), 500
        
    cur = conn.cursor()

    try:
        cur.execute("DELETE FROM students WHERE id=%s", (id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True, "message": "Student deleted"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ---------------- ATTENDANCE ----------------

@app.route("/attendance", methods=["POST"])
@jwt_required()
def mark_attendance():
    data = request.get_json()

    if not data or "student_id" not in data or "status" not in data or "attendance_date" not in data:
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Database connection error"}), 500

    cur = conn.cursor()

    try:
        # Check if student exists (by internal ID)
        cur.execute("SELECT id FROM students WHERE id = %s", (data["student_id"],))
        if not cur.fetchone():
            return jsonify({"success": False, "message": "Student not found"}), 404

        cur.execute("""
        INSERT INTO attendance
        (student_id, attendance_date, status)
        VALUES (%s,%s,%s)
        """, (
            data["student_id"],
            data["attendance_date"],
            data["status"]
        ))

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True, "message": "Attendance marked successfully"})
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/attendance", methods=["GET"])
@jwt_required()
def get_attendance():
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Database connection error"}), 500
        
    try:
        cur = conn.cursor()
        cur.execute("""
        SELECT a.id, s.student_id as roll_no, s.full_name, a.attendance_date, a.status
        FROM attendance a
        JOIN students s ON a.student_id=s.id
        ORDER BY a.attendance_date DESC, a.id DESC
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        # Format date for JSON if needed (though Flask usually handles it)
        for row in rows:
            if hasattr(row['attendance_date'], 'strftime'):
                row['attendance_date'] = row['attendance_date'].strftime('%Y-%m-%d')
                
        return jsonify(rows)
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({"success": False, "message": str(e)}), 500


# ---------------- MARKS ----------------

@app.route("/marks", methods=["POST"])
@jwt_required()
def add_marks():
    data = request.get_json()
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Database connection error"}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO marks(student_id, exam_name, subject, marks_obtained, total_marks)
        VALUES(%s,%s,%s,%s,%s)
        """, (
            data["student_id"],
            data["exam_name"],
            data["subject"],
            data["marks_obtained"],
            data.get("total_marks", 100)
        ))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True, "message": "Marks added successfully"})
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/marks", methods=["GET"])
@jwt_required()
def get_marks():
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Database connection error"}), 500
        
    try:
        cur = conn.cursor()
        cur.execute("""
        SELECT m.*, s.full_name, s.student_id as roll_no
        FROM marks m
        JOIN students s ON m.student_id=s.id
        ORDER BY m.id DESC
        """)
        data = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(data)
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({"success": False, "message": str(e)}), 500


# ---------------- FEES ----------------

@app.route("/fees", methods=["POST"])
@jwt_required()
def record_payment():
    data = request.get_json()
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Database error"}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO fees(student_id, total_fee, paid_amount, payment_date, payment_method, remarks)
        VALUES(%s,%s,%s,%s,%s,%s)
        """, (
            data["student_id"],
            data["total_fee"],
            data["paid_amount"],
            data["payment_date"],
            data["payment_method"],
            data.get("remarks", "")
        ))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True, "message": "Payment recorded successfully"})
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/fees", methods=["GET"])
@jwt_required()
def get_fees():
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Database error"}), 500
        
    try:
        cur = conn.cursor()
        cur.execute("""
        SELECT f.*, s.full_name, s.student_id as roll_no
        FROM fees f
        JOIN students s ON f.student_id=s.id
        ORDER BY f.payment_date DESC
        """)
        data = cur.fetchall()
        cur.close()
        conn.close()
        
        # Format dates for JSON
        for row in data:
            if hasattr(row['payment_date'], 'strftime'):
                row['payment_date'] = row['payment_date'].strftime('%Y-%m-%d')
                
        return jsonify(data)
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({"success": False, "message": str(e)}), 500


# ---------------- DASHBOARD ----------------

@app.route("/dashboard/stats", methods=["GET"])
@jwt_required()
def dashboard_stats():
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Database error"}), 500
        
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) total FROM students")
        students = cur.fetchone()["total"]

        cur.execute("SELECT COUNT(*) total FROM attendance")
        attendance = cur.fetchone()["total"]

        cur.execute("SELECT COUNT(*) total FROM marks")
        marks = cur.fetchone()["total"]

        cur.close()
        conn.close()

        return jsonify({
            "students": students,
            "attendance": attendance,
            "marks": marks
        })
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/search/<name>", methods=["GET"])
@jwt_required()
def search_student(name):
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Database error"}), 500
        
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM students WHERE full_name LIKE %s OR student_id LIKE %s",
            (f"%{name}%", f"%{name}%")
        )
        data = cur.fetchall()
        cur.close()
        conn.close()
        
        # Format date and datetime objects for JSON serialization
        for row in data:
            if row.get('dob') and hasattr(row['dob'], 'strftime'):
                row['dob'] = row['dob'].strftime('%Y-%m-%d')
            if row.get('created_at') and hasattr(row['created_at'], 'strftime'):
                row['created_at'] = row['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                
        return jsonify(data)
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({"success": False, "message": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
