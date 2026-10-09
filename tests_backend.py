import unittest
import json
from app import app
from database.db import query_one, query_all

class UdaanBackendTestSuite(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()

    # 1. Authentication Tests for all 4 roles
    def test_01_login_all_roles(self):
        roles_to_test = [
            ('student1', 'student123', 'student', '/student'),
            ('teacher_class', 'class123', 'class_teacher', '/class-teacher'),
            ('teacher_priya', 'priya123', 'subject_teacher', '/subject-teacher'),
            ('support_staff', 'support123', 'support', '/support')
        ]
        for user, pwd, role, expected_redirect in roles_to_test:
            res = self.client.post('/api/auth/login', json={
                'username': user,
                'password': pwd,
                'role': role
            })
            self.assertEqual(res.status_code, 200, f"Failed for {user} ({role})")
            data = res.get_json()
            self.assertTrue(data['success'])
            self.assertEqual(data['user']['role'], role)
            self.assertEqual(data['redirect_url'], expected_redirect)

    def test_02_login_invalid_password(self):
        res = self.client.post('/api/auth/login', json={
            'username': 'student1',
            'password': 'wrong_password_xyz',
            'role': 'student'
        })
        self.assertEqual(res.status_code, 401)
        data = res.get_json()
        self.assertFalse(data['success'])

    def test_03_login_role_mismatch(self):
        # student1 exists, but user selects 'class_teacher' role card
        res = self.client.post('/api/auth/login', json={
            'username': 'student1',
            'password': 'student123',
            'role': 'class_teacher'
        })
        self.assertEqual(res.status_code, 403)
        data = res.get_json()
        self.assertFalse(data['success'])
        self.assertIn("Role mismatch", data['message'])

    # 2. Authorization and Route Protection Tests
    def test_04_unauthenticated_access_denied(self):
        unauth_client = self.app.test_client()
        # Pages redirect to login
        for path in ['/student', '/class-teacher', '/subject-teacher', '/support']:
            res = unauth_client.get(path)
            self.assertEqual(res.status_code, 302)
            self.assertIn('/login', res.headers['Location'])

        # APIs return 401
        for api_path in ['/api/student/dashboard', '/api/class-teacher/classes', '/api/subject-teacher/classes']:
            res = unauth_client.get(api_path)
            self.assertEqual(res.status_code, 401)

    def test_05_cross_role_access_denied(self):
        # Login as student
        stu_client = self.app.test_client()
        stu_client.post('/api/auth/login', json={'username': 'student1', 'password': 'student123', 'role': 'student'})

        # Student cannot call class-teacher API
        res = stu_client.get('/api/class-teacher/classes')
        self.assertEqual(res.status_code, 403)

        # Student cannot call subject-teacher marks update
        res = stu_client.post('/api/subject-teacher/marks', json={'marks': 100})
        self.assertEqual(res.status_code, 403)

    # 3. Student Dashboard API
    def test_06_student_dashboard_data(self):
        client = self.app.test_client()
        client.post('/api/auth/login', json={'username': 'student1', 'password': 'student123', 'role': 'student'})

        res = client.get('/api/student/dashboard')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['student_name'], 'Meghana Rao')
        self.assertEqual(data['roll_number'], 'CSE2402')
        self.assertGreater(len(data['subjects']), 0)
        self.assertIn('stats', data)
        self.assertEqual(data['stats']['streak'], 7)

        # Post a student note
        res_note = client.post('/api/student/notes', json={
            'subject': 'Java Programming',
            'text': 'Automated unit test note for Java inheritance'
        })
        self.assertEqual(res_note.status_code, 200)

    # 4. Class Teacher Assignment Enforcement
    def test_07_class_teacher_permissions(self):
        client = self.app.test_client()
        client.post('/api/auth/login', json={'username': 'teacher_class', 'password': 'class123', 'role': 'class_teacher'})

        # Retrieve assigned classes
        res = client.get('/api/class-teacher/classes')
        self.assertEqual(res.status_code, 200)
        classes = res.get_json()
        self.assertTrue(any(c['code'] == 'CSE-A' for c in classes))

        # Authorized class query (CSE-A)
        res_auth = client.get(f"/api/class-teacher/students?class_id={classes[0]['id']}")
        self.assertEqual(res_auth.status_code, 200)
        students = res_auth.get_json()['students']
        self.assertGreater(len(students), 0)

        # Unauthorized class query (CSE-B is not assigned to Dr. Raman!)
        cse_b = query_one("SELECT id FROM classes WHERE code = 'CSE-B'")
        if cse_b:
            res_unauth = client.get(f"/api/class-teacher/students?class_id={cse_b['id']}")
            self.assertEqual(res_unauth.status_code, 403)

        # Save class teacher mentoring note
        res_note = client.post('/api/class-teacher/notes', json={
            'student_id': 'CSE2401',
            'note': 'Test mentoring note from unit test suite'
        })
        self.assertEqual(res_note.status_code, 200)

    # 5. Subject Teacher Dynamic Hierarchy & Early Warning System
    def test_08_subject_teacher_dynamic_selection_and_early_warning(self):
        client = self.app.test_client()
        client.post('/api/auth/login', json={'username': 'teacher_priya', 'password': 'priya123', 'role': 'subject_teacher'})

        # Classes taught by Ms. Priya
        res_cls = client.get('/api/subject-teacher/classes')
        self.assertEqual(res_cls.status_code, 200)
        class_codes = [c['code'] for c in res_cls.get_json()]
        self.assertIn('CSE-A', class_codes)
        self.assertIn('CSE-B', class_codes)
        self.assertIn('ECE-A', class_codes)

        # Subject filtering by class:
        # In CSE-A: teaches DSA and CN
        res_sub_a = client.get('/api/subject-teacher/subjects?class_code=CSE-A')
        subs_a = [s['code'] for s in res_sub_a.get_json()]
        self.assertIn('DSA', subs_a)
        self.assertIn('CN', subs_a)

        # In CSE-B: teaches ONLY DSA
        res_sub_b = client.get('/api/subject-teacher/subjects?class_code=CSE-B')
        subs_b = [s['code'] for s in res_sub_b.get_json()]
        self.assertIn('DSA', subs_b)
        self.assertNotIn('CN', subs_b)

        # In ECE-A: teaches ONLY CN
        res_sub_ece = client.get('/api/subject-teacher/subjects?class_code=ECE-A')
        subs_ece = [s['code'] for s in res_sub_ece.get_json()]
        self.assertIn('CN', subs_ece)
        self.assertNotIn('DSA', subs_ece)

        # Unauthorized request: trying to query CSE-B with CN
        res_unauth = client.get('/api/subject-teacher/students?class_code=CSE-B&subject_code=CN')
        self.assertEqual(res_unauth.status_code, 403)

        # Authorized query: CSE-A + DSA
        res_students = client.get('/api/subject-teacher/students?class_code=CSE-A&subject_code=DSA')
        self.assertEqual(res_students.status_code, 200)
        students_data = res_students.get_json()['students']
        self.assertGreater(len(students_data), 0)

        # Test Early Warning Algorithm verification:
        # Aarav Reddy has marks 51 -> 39 -> 28 (strictly decreasing 3 consecutive)
        aarav = next((s for s in students_data if s['id'] == 'CSE2401'), None)
        self.assertIsNotNone(aarav)
        self.assertTrue(aarav['early_warning'], "Aarav Reddy must be flagged for early warning!")
        self.assertEqual(aarav['trend'], "51.0 → 39.0 → 28.0")

        # First student in list must be early-warning student (sorted to top)
        self.assertTrue(students_data[0]['early_warning'])

    def test_09_subject_teacher_update_marks(self):
        client = self.app.test_client()
        client.post('/api/auth/login', json={'username': 'teacher_priya', 'password': 'priya123', 'role': 'subject_teacher'})

        res_update = client.post('/api/subject-teacher/marks', json={
            'student_id': 'CSE2403',
            'class_code': 'CSE-A',
            'subject_id': 'DSA',
            'marks': 92,
            'attended': 21,
            'total_classes': 22
        })
        self.assertEqual(res_update.status_code, 200)

        # Verify in query
        res_check = client.get('/api/subject-teacher/students?class_code=CSE-A&subject_code=DSA')
        ishaan = next((s for s in res_check.get_json()['students'] if s['id'] == 'CSE2403'), None)
        self.assertEqual(ishaan['marks'], 92)
        self.assertEqual(ishaan['attended'], 21)

    # 6. Support Line Tickets API
    def test_10_support_tickets_flow(self):
        client = self.app.test_client()
        client.post('/api/auth/login', json={'username': 'support_staff', 'password': 'support123', 'role': 'support'})

        # Staff gets all tickets
        res = client.get('/api/support/tickets')
        self.assertEqual(res.status_code, 200)
        tickets = res.get_json()
        self.assertGreaterEqual(len(tickets), 5)

        # Post reply and update status
        tck_id = tickets[0]['id']
        res_rep = client.post('/api/support/reply', json={
            'ticket_id': tck_id,
            'message': 'Counseling session confirmed by support staff via unit test',
            'status': 'in_progress'
        })
        self.assertEqual(res_rep.status_code, 200)

        # Create new ticket
        res_new = client.post('/api/support/tickets', json={
            'studentId': 'CSE2402',
            'category': 'attendance_concern',
            'subjectLine': 'Test ticket created from test suite',
            'description': 'Description from test suite',
            'priority': 'medium'
        })
        self.assertEqual(res_new.status_code, 200)

    # 7. Logout Invalidation
    def test_11_logout_invalidation(self):
        client = self.app.test_client()
        client.post('/api/auth/login', json={'username': 'student1', 'password': 'student123', 'role': 'student'})

        # Check me
        res_me = client.get('/api/auth/me')
        self.assertEqual(res_me.status_code, 200)

        # Logout
        res_logout = client.post('/api/auth/logout')
        self.assertEqual(res_logout.status_code, 200)

        # Check me again -> 401
        res_me_after = client.get('/api/auth/me')
        self.assertEqual(res_me_after.status_code, 401)

    # 8. Multi-role Logout & Session Revocation
    def test_12_logout_all_four_roles(self):
        roles_to_test = [
            ('student1', 'student123', 'student', '/student'),
            ('teacher_class', 'class123', 'class_teacher', '/class-teacher'),
            ('teacher_priya', 'priya123', 'subject_teacher', '/subject-teacher'),
            ('support_staff', 'support123', 'support', '/support')
        ]
        for user, pwd, role, portal_path in roles_to_test:
            client = self.app.test_client()
            res_login = client.post('/api/auth/login', json={'username': user, 'password': pwd, 'role': role})
            self.assertEqual(res_login.status_code, 200)

            # Access protected portal before logout -> 200 OK
            res_portal = client.get(portal_path)
            self.assertEqual(res_portal.status_code, 200)

            # Issue POST /api/auth/logout
            res_logout = client.post('/api/auth/logout')
            self.assertEqual(res_logout.status_code, 200)
            logout_data = res_logout.get_json()
            self.assertTrue(logout_data.get('success'))
            self.assertEqual(logout_data.get('redirect_url'), '/login')

            # Verify session is dead: /api/auth/me returns 401
            res_me = client.get('/api/auth/me')
            self.assertEqual(res_me.status_code, 401)

            # Accessing portal after logout redirects (302) to /login
            res_portal_after = client.get(portal_path)
            self.assertEqual(res_portal_after.status_code, 302)
            self.assertIn('/login', res_portal_after.headers['Location'])

    # 9. Route Aliases & Anti-Back-Button Cache Headers
    def test_13_login_html_alias_and_cache_headers(self):
        client = self.app.test_client()

        # /login.html redirects (302) to /login
        res_alias = client.get('/login.html')
        self.assertEqual(res_alias.status_code, 302)
        self.assertIn('/login', res_alias.headers['Location'])

        # /login renders 200 OK
        res_login_page = client.get('/login')
        self.assertEqual(res_login_page.status_code, 200)

        # GET /logout redirects (302) to /login
        res_get_logout = client.get('/logout')
        self.assertEqual(res_get_logout.status_code, 302)
        self.assertIn('/login', res_get_logout.headers['Location'])

        # Check cache-control headers prevent bfcache restore
        res_check = client.get('/login')
        self.assertIn('no-store', res_check.headers.get('Cache-Control', ''))
        self.assertIn('no-cache', res_check.headers.get('Cache-Control', ''))
        self.assertEqual(res_check.headers.get('Pragma'), 'no-cache')

if __name__ == '__main__':
    unittest.main()
