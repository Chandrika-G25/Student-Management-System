import sys
import os
import json
import unittest

# Add project directories to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from app import app
from config import get_db_connection

class TestStudentManagementSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()
        cls.client.testing = True

    def test_01_health_and_static_routes(self):
        """Test health check and frontend static page delivery"""
        # Test /health
        res = self.client.get('/health')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get('status'), 'healthy')
        self.assertTrue(data.get('database_connected'))

        # Test static files
        res_index = self.client.get('/')
        self.assertEqual(res_index.status_code, 200)
        self.assertIn(b'<!DOCTYPE html>', res_index.data)

        for page in ['dashboard.html', 'attendance.html', 'marks.html', 'fees.html', 'reports.html', 'style.css']:
            res_page = self.client.get(f'/{page}')
            self.assertEqual(res_page.status_code, 200, f"Failed to load {page}")

    def test_02_authentication_flow(self):
        """Test login, registration, invalid credentials, and profile endpoints"""
        # Test Invalid Login
        res_fail = self.client.post('/login', json={
            'email': 'admin@gmail.com',
            'password': 'wrong_password'
        })
        self.assertEqual(res_fail.status_code, 401)
        self.assertFalse(res_fail.get_json().get('success'))

        # Test Valid Admin Login
        res_login = self.client.post('/login', json={
            'email': 'admin@gmail.com',
            'password': 'admin123'
        })
        self.assertEqual(res_login.status_code, 200)
        data = res_login.get_json()
        self.assertTrue(data.get('success'))
        self.assertIn('token', data)
        self.assertEqual(data.get('role'), 'admin')
        TestStudentManagementSystem.token = data['token']
        TestStudentManagementSystem.headers = {
            'Authorization': f"Bearer {data['token']}",
            'Content-Type': 'application/json'
        }

        # Test Protected Profile Endpoint
        res_profile = self.client.get('/profile', headers=self.headers)
        self.assertEqual(res_profile.status_code, 200)
        user_data = res_profile.get_json()
        self.assertTrue(user_data.get('success'))
        self.assertEqual(user_data['user']['email'], 'admin@gmail.com')

        # Test Admin Dashboard Check
        res_admin = self.client.get('/admin-dashboard', headers=self.headers)
        self.assertEqual(res_admin.status_code, 200)

        # Test Registering a new student user
        res_reg = self.client.post('/register', json={
            'username': 'test_student_user',
            'email': 'test_student@example.com',
            'password': 'password123',
            'role': 'student'
        })
        # Could be 200 or 400 if already created in previous run
        self.assertIn(res_reg.status_code, [200, 400])

    def test_03_student_management_crud(self):
        """Test adding, retrieving, updating, searching, and deleting a student"""
        # 1. Add Student
        student_payload = {
            "student_id": "TEST_STU_001",
            "full_name": "Antigravity Test Student",
            "email": "antigravity.test@example.com",
            "phone": "9876543210",
            "gender": "Male",
            "dob": "2002-05-15",
            "course": "Computer Science",
            "address": "123 Innovation Boulevard"
        }
        res_add = self.client.post('/students', json=student_payload, headers=self.headers)
        self.assertIn(res_add.status_code, [200, 500]) # 500 if duplicate, handled below

        # 2. Get Students
        res_list = self.client.get('/students', headers=self.headers)
        self.assertEqual(res_list.status_code, 200)
        students = res_list.get_json()
        self.assertIsInstance(students, list)

        # Find our test student
        test_student = next((s for s in students if s['student_id'] == "TEST_STU_001"), None)
        self.assertIsNotNone(test_student, "Created student should be found in list")
        TestStudentManagementSystem.student_db_id = test_student['id']

        # 3. Update Student
        update_payload = {
            "full_name": "Antigravity Test Student (Updated)",
            "email": "antigravity.test@example.com",
            "phone": "9876543219",
            "course": "Data Science",
            "address": "456 Tech Park Way"
        }
        res_update = self.client.put(f"/students/{test_student['id']}", json=update_payload, headers=self.headers)
        self.assertEqual(res_update.status_code, 200)
        self.assertTrue(res_update.get_json().get('success'))

        # 4. Search Student
        res_search = self.client.get("/search/Antigravity", headers=self.headers)
        self.assertEqual(res_search.status_code, 200)
        search_results = res_search.get_json()
        self.assertTrue(len(search_results) > 0)
        self.assertEqual(search_results[0]['student_id'], "TEST_STU_001")

    def test_04_attendance_management(self):
        """Test marking attendance and retrieving records"""
        payload = {
            "student_id": self.student_db_id,
            "attendance_date": "2026-09-08",
            "status": "Present"
        }
        res_att = self.client.post('/attendance', json=payload, headers=self.headers)
        self.assertEqual(res_att.status_code, 200)
        self.assertTrue(res_att.get_json().get('success'))

        # Retrieve attendance
        res_list = self.client.get('/attendance', headers=self.headers)
        self.assertEqual(res_list.status_code, 200)
        records = res_list.get_json()
        self.assertIsInstance(records, list)
        found = any(r.get('roll_no') == "TEST_STU_001" or r.get('student_id') == self.student_db_id for r in records)
        self.assertTrue(found, "Marked attendance record should be present")


    def test_05_marks_management(self):
        """Test recording exam scores and retrieving marks"""
        payload = {
            "student_id": self.student_db_id,
            "exam_name": "Mid-Term",
            "subject": "Cloud Computing",
            "marks_obtained": 95,
            "total_marks": 100
        }
        res_marks = self.client.post('/marks', json=payload, headers=self.headers)
        self.assertEqual(res_marks.status_code, 200)
        self.assertTrue(res_marks.get_json().get('success'))

        # Retrieve marks
        res_list = self.client.get('/marks', headers=self.headers)
        self.assertEqual(res_list.status_code, 200)
        records = res_list.get_json()
        self.assertIsInstance(records, list)
        found = any(r['subject'] == "Cloud Computing" for r in records)
        self.assertTrue(found, "Added marks record should be present")

    def test_06_fees_management(self):
        """Test recording tuition fee payment and retrieving payment history"""
        payload = {
            "student_id": self.student_db_id,
            "total_fee": 1500.00,
            "paid_amount": 1000.00,
            "payment_date": "2026-09-08",
            "payment_method": "Credit Card",
            "remarks": "Term 1 Advance"
        }
        res_fees = self.client.post('/fees', json=payload, headers=self.headers)
        self.assertEqual(res_fees.status_code, 200)
        self.assertTrue(res_fees.get_json().get('success'))

        # Retrieve fees
        res_list = self.client.get('/fees', headers=self.headers)
        self.assertEqual(res_list.status_code, 200)
        records = res_list.get_json()
        self.assertIsInstance(records, list)
        found = any(float(r['paid_amount']) == 1000.00 for r in records)
        self.assertTrue(found, "Recorded fee payment should be present")

    def test_07_dashboard_stats(self):
        """Test dashboard summary counters"""
        res = self.client.get('/dashboard/stats', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        stats = res.get_json()
        self.assertIn('students', stats)
        self.assertIn('attendance', stats)
        self.assertIn('marks', stats)
        self.assertGreaterEqual(stats['students'], 1)
        self.assertGreaterEqual(stats['attendance'], 1)
        self.assertGreaterEqual(stats['marks'], 1)

    def test_08_cleanup(self):
        """Clean up test student created during test run"""
        if hasattr(self, 'student_db_id'):
            res_del = self.client.delete(f"/students/{self.student_db_id}", headers=self.headers)
            self.assertEqual(res_del.status_code, 200)
            self.assertTrue(res_del.get_json().get('success'))

if __name__ == '__main__':
    unittest.main(verbosity=2)
