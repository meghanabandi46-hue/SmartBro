import os
import re
import secrets
from functools import wraps
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash

from config import Config
from database.db import query_all, query_one, execute, get_active_engine

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config.from_object(Config)

# ---------------------------------------------------------------------
# Role-Based Authentication & Authorization Decorators
# ---------------------------------------------------------------------

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'success': False, 'message': 'Authentication required. Please sign in.'}), 401
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({'success': False, 'message': 'Authentication required. Please sign in.'}), 401
                return redirect(url_for('login_page'))
            
            user_role = session.get('role')
            if user_role not in allowed_roles:
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({
                        'success': False,
                        'message': f"Access forbidden. Your account role is '{user_role}'. Required: {list(allowed_roles)}"
                    }), 403
                # Redirect to user's authorized role dashboard
                if user_role == 'student':
                    return redirect(url_for('student_portal'))
                elif user_role == 'class_teacher':
                    return redirect(url_for('class_teacher_portal'))
                elif user_role == 'subject_teacher':
                    return redirect(url_for('subject_teacher_portal'))
                elif user_role == 'support':
                    return redirect(url_for('support_portal'))
                return redirect(url_for('login_page'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ---------------------------------------------------------------------
# HTML Page Routes (Role-Protected Dashboards)
# ---------------------------------------------------------------------

@app.route('/')
def home():
    if 'user_id' in session:
        role = session.get('role')
        if role == 'student':
            return redirect(url_for('student_portal'))
        elif role == 'class_teacher':
            return redirect(url_for('class_teacher_portal'))
        elif role == 'subject_teacher':
            return redirect(url_for('subject_teacher_portal'))
        elif role == 'support':
            return redirect(url_for('support_portal'))
    return redirect(url_for('login_page'))

@app.route('/login')
def login_page():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    if request.is_json:
        return jsonify({'success': True, 'message': 'Logged out successfully.'})
    return redirect(url_for('login_page'))

@app.route('/student')
@role_required('student')
def student_portal():
    return render_template('index.html')

@app.route('/class-teacher')
@role_required('class_teacher')
def class_teacher_portal():
    return render_template('class_teacher.html')

@app.route('/subject-teacher')
@role_required('subject_teacher')
def subject_teacher_portal():
    return render_template('subject_teacher.html')

@app.route('/support')
@role_required('support', 'student')
def support_portal():
    return render_template('support.html')

@app.after_request
def add_no_cache_headers(response):
    """Ensure browsers do not cache protected dashboards so Back button cannot bypass logout."""
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Legacy and direct .html route aliases to prevent 404s
@app.route('/login.html')
def alias_login_html():
    return redirect(url_for('login_page'))

@app.route('/index.html')
def alias_index_html():
    return redirect(url_for('student_portal'))

@app.route('/class_teacher.html')
def alias_class_teacher_html():
    return redirect(url_for('class_teacher_portal'))

@app.route('/subject_teacher.html')
def alias_subject_teacher_html():
    return redirect(url_for('subject_teacher_portal'))

@app.route('/support.html')
def alias_support_html():
    return redirect(url_for('support_portal'))

# Authentication API
# ---------------------------------------------------------------------

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')
    selected_role = data.get('role', '').strip()

    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password are required.'}), 400
    if not selected_role:
        return jsonify({'success': False, 'message': 'Please select your role from the role cards.'}), 400

    user = query_one(
        "SELECT * FROM users WHERE username = %s OR email = %s",
        (username, username)
    )

    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({'success': False, 'message': 'Invalid username or password.'}), 401

    # Server-Side Role Enforcement: Prevent cross-role impersonation
    if user['role'] != selected_role:
        role_labels = {
            'student': 'Student',
            'class_teacher': 'Class Teacher',
            'subject_teacher': 'Subject Teacher',
            'support': 'Support Line'
        }
        actual_name = role_labels.get(user['role'], user['role'])
        chosen_name = role_labels.get(selected_role, selected_role)
        return jsonify({
            'success': False,
            'message': f"Role mismatch: This account belongs to role '{actual_name}', but you selected '{chosen_name}'. Please select the matching role card."
        }), 403

    # Establish secure session
    session.clear()
    session['user_id'] = user['id']
    session['username'] = user['username']
    session['role'] = user['role']
    session['name'] = user['full_name']

    redirect_urls = {
        'student': '/student',
        'class_teacher': '/class-teacher',
        'subject_teacher': '/subject-teacher',
        'support': '/support'
    }

    return jsonify({
        'success': True,
        'message': f"Welcome back, {user['full_name']}!",
        'user': {
            'id': user['id'],
            'username': user['username'],
            'name': user['full_name'],
            'role': user['role']
        },
        'redirect_url': redirect_urls.get(user['role'], '/')
    })

@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({
        'success': True,
        'message': 'Session ended.',
        'redirect_url': '/login'
    })

@app.route('/api/auth/me', methods=['GET'])
def api_me():
    if 'user_id' not in session:
        return jsonify({'authenticated': False}), 401
    return jsonify({
        'authenticated': True,
        'user': {
            'id': session['user_id'],
            'username': session.get('username'),
            'name': session.get('name'),
            'role': session.get('role')
        }
    })

# ---------------------------------------------------------------------
# Student Portal API
# ---------------------------------------------------------------------

@app.route('/api/student/dashboard', methods=['GET'])
@role_required('student')
def api_student_dashboard():
    user_id = session['user_id']
    student = query_one(
        """SELECT s.id as student_id, s.roll_number, s.streak_days, 
                  u.full_name, c.code as class_code, c.name as class_name 
           FROM students s 
           JOIN users u ON s.user_id = u.id 
           JOIN classes c ON s.class_id = c.id 
           WHERE s.user_id = %s""",
        (user_id,)
    )

    if not student:
        return jsonify({'error': 'Student record not found'}), 404

    # Enrolled attendance and subjects
    att_rows = query_all(
        """SELECT a.attended_classes, a.total_classes, 
                  sub.id as subject_id, sub.code, sub.name, sub.icon, sub.color, sub.ink 
           FROM attendance a 
           JOIN subjects sub ON a.subject_id = sub.id 
           WHERE a.student_id = %s""",
        (student['student_id'],)
    )

    total_attended = sum(r['attended_classes'] for r in att_rows)
    total_classes = sum(r['total_classes'] for r in att_rows)
    overall_att_pct = round((total_attended / total_classes * 100), 1) if total_classes > 0 else 0

    subjects_data = []
    for r in att_rows:
        sub_att_pct = round((r['attended_classes'] / r['total_classes'] * 100), 1) if r['total_classes'] > 0 else 0

        # Latest marks
        mark_row = query_one(
            """SELECT m.marks_obtained, a.max_marks 
               FROM marks m 
               JOIN assessments a ON m.assessment_id = a.id 
               WHERE m.student_id = %s AND a.subject_id = %s 
               ORDER BY a.sequence_order DESC LIMIT 1""",
            (student['student_id'], r['subject_id'])
        )
        marks_val = float(mark_row['marks_obtained']) if mark_row else 0
        total_val = mark_row['max_marks'] if mark_row else 100

        # Academic grade calculation
        pct = (marks_val / total_val * 100) if total_val > 0 else 0
        grade = 'A' if pct >= 80 else 'B+' if pct >= 70 else 'B' if pct >= 55 else 'C'

        # Topic progress
        topics = query_all(
            """SELECT t.name, COALESCE(p.completion_pct, 0) as pct 
               FROM topics t 
               LEFT JOIN student_topic_progress p ON t.id = p.topic_id AND p.student_id = %s 
               WHERE t.subject_id = %s 
               ORDER BY t.order_index ASC""",
            (student['student_id'], r['subject_id'])
        )

        subjects_data.append({
            'name': r['name'],
            'icon': r['icon'],
            'color': r['color'],
            'ink': r['ink'],
            'marks': marks_val,
            'total': total_val,
            'grade': grade,
            'attendance': round(sub_att_pct),
            'attended': r['attended_classes'],
            'classes': r['total_classes'],
            'topics': [[t['name'], t['pct']] for t in topics]
        })

    # Student notes
    notes = query_all(
        """SELECT n.id, n.note_text as text, n.created_at, sub.name as subject 
           FROM student_notes n 
           JOIN subjects sub ON n.subject_id = sub.id 
           WHERE n.student_id = %s 
           ORDER BY n.created_at DESC""",
        (student['student_id'],)
    )

    return jsonify({
        'student_name': student['full_name'],
        'roll_number': student['roll_number'],
        'class': student['class_code'],
        'stats': {
            'streak': student['streak_days'],
            'attended_classes': total_attended,
            'total_classes': total_classes,
            'attendance_pct': overall_att_pct
        },
        'subjects': subjects_data,
        'notes': [{'subject': n['subject'], 'text': n['text'], 'date': str(n['created_at'])[:10]} for n in notes]
    })

@app.route('/api/student/notes', methods=['POST'])
@role_required('student')
def api_student_save_note():
    user_id = session['user_id']
    student = query_one("SELECT id FROM students WHERE user_id = %s", (user_id,))
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    data = request.get_json() or {}
    subject_name = data.get('subject', '').strip()
    text = data.get('text', '').strip()

    if not subject_name or not text:
        return jsonify({'error': 'Subject and note content are required.'}), 400

    subject = query_one("SELECT id FROM subjects WHERE name = %s OR code = %s", (subject_name, subject_name))
    if not subject:
        return jsonify({'error': 'Subject not found'}), 404

    execute(
        "INSERT INTO student_notes (student_id, subject_id, note_text) VALUES (%s, %s, %s)",
        (student['id'], subject['id'], text)
    )
    return jsonify({'success': True, 'message': 'Note saved successfully.'})

# ---------------------------------------------------------------------
# Class Teacher Portal API
# ---------------------------------------------------------------------

@app.route('/api/class-teacher/classes', methods=['GET'])
@role_required('class_teacher')
def api_class_teacher_classes():
    teacher = query_one("SELECT id FROM teachers WHERE user_id = %s", (session['user_id'],))
    if not teacher:
        return jsonify([]), 200

    classes = query_all(
        """SELECT c.id, c.code, c.name, c.section 
           FROM class_teacher_assignments cta 
           JOIN classes c ON cta.class_id = c.id 
           WHERE cta.teacher_id = %s""",
        (teacher['id'],)
    )
    return jsonify(classes)

@app.route('/api/class-teacher/students', methods=['GET'])
@role_required('class_teacher')
def api_class_teacher_students():
    teacher = query_one("SELECT id FROM teachers WHERE user_id = %s", (session['user_id'],))
    if not teacher:
        return jsonify({'error': 'Teacher record not found'}), 404

    class_id_param = request.args.get('class_id')
    if not class_id_param:
        return jsonify({'error': 'class_id parameter is required.'}), 400

    # SERVER-SIDE AUTHORIZATION: Verify class teacher assignment
    auth_check = query_one(
        """SELECT c.id, c.code, c.name 
           FROM class_teacher_assignments cta 
           JOIN classes c ON cta.class_id = c.id 
           WHERE cta.teacher_id = %s AND (c.id = %s OR c.code = %s)""",
        (teacher['id'], class_id_param, class_id_param)
    )
    if not auth_check:
        return jsonify({'error': 'Access Denied: You are not the assigned Class Teacher for this class.'}), 403

    target_class_id = auth_check['id']
    students = query_all(
        """SELECT s.id, s.roll_number, u.full_name as name, s.phone, c.code as class_code 
           FROM students s 
           JOIN users u ON s.user_id = u.id 
           JOIN classes c ON s.class_id = c.id 
           WHERE s.class_id = %s 
           ORDER BY u.full_name ASC""",
        (target_class_id,)
    )

    results = []
    for s in students:
        # Calculate attendance across all subjects
        att_rows = query_all(
            "SELECT attended_classes, total_classes FROM attendance WHERE student_id = %s",
            (s['id'],)
        )
        total_att = sum(r['attended_classes'] for r in att_rows)
        total_cls = sum(r['total_classes'] for r in att_rows)
        overall_att = round((total_att / total_cls * 100)) if total_cls > 0 else 0

        # Calculate average marks across all subjects
        marks_rows = query_all(
            "SELECT marks_obtained FROM marks WHERE student_id = %s",
            (s['id'],)
        )
        avg_marks = round(sum(float(m['marks_obtained']) for m in marks_rows) / len(marks_rows)) if marks_rows else 0

        status = 'low' if (avg_marks < 50 or overall_att < 75) else 'average' if avg_marks < 70 else 'good'

        # Fetch subject-wise academic details (View-Only for Class Teacher)
        sub_records = query_all(
            """SELECT sub.name, COALESCE(att.attended_classes, 0) as attended, 
                      COALESCE(att.total_classes, 0) as total, 
                      COALESCE(u_tch.full_name, 'Assigned Faculty') as teacher_name 
               FROM subjects sub 
               LEFT JOIN attendance att ON sub.id = att.subject_id AND att.student_id = %s 
               LEFT JOIN teacher_subject_assignments tsa ON sub.id = tsa.subject_id AND tsa.class_id = %s 
               LEFT JOIN teachers tch ON tsa.teacher_id = tch.id 
               LEFT JOIN users u_tch ON tch.user_id = u_tch.id 
               GROUP BY sub.id""",
            (s['id'], target_class_id)
        )

        subjects_summary = []
        for sr in sub_records:
            sub_att_str = f"{round((sr['attended'] / sr['total'] * 100))}%" if sr['total'] > 0 else "N/A"
            # Get latest mark for this subject
            last_m = query_one(
                """SELECT m.marks_obtained, a.max_marks 
                   FROM marks m 
                   JOIN assessments a ON m.assessment_id = a.id 
                   JOIN subjects sub ON a.subject_id = sub.id 
                   WHERE m.student_id = %s AND sub.name = %s 
                   ORDER BY a.sequence_order DESC LIMIT 1""",
                (s['id'], sr['name'])
            )
            mark_str = f"{last_m['marks_obtained']} / {last_m['max_marks']}" if last_m else "Not recorded"
            subjects_summary.append({
                'name': sr['name'],
                'teacher': sr['teacher_name'],
                'marks': mark_str,
                'attendance': sub_att_str
            })

        # Fetch follow-up mentoring note from class teacher
        note_row = query_one(
            "SELECT note_text FROM class_teacher_notes WHERE teacher_id = %s AND student_id = %s",
            (teacher['id'], s['id'])
        )

        results.append({
            'id': s['roll_number'],
            'student_db_id': s['id'],
            'name': s['name'],
            'class': s['class_code'],
            'attendance': overall_att,
            'avgMarks': avg_marks,
            'status': status,
            'phone': s['phone'] or 'N/A',
            'note': note_row['note_text'] if note_row else 'None',
            'subjects': subjects_summary
        })

    return jsonify({'class': auth_check['name'], 'students': results})

@app.route('/api/class-teacher/notes', methods=['POST'])
@role_required('class_teacher')
def api_class_teacher_save_note():
    teacher = query_one("SELECT id FROM teachers WHERE user_id = %s", (session['user_id'],))
    if not teacher:
        return jsonify({'error': 'Teacher not found'}), 404

    data = request.get_json() or {}
    roll_number = data.get('student_id', '').strip()
    note_text = data.get('note', '').strip()

    student = query_one("SELECT id, class_id FROM students WHERE roll_number = %s OR id = %s", (roll_number, roll_number))
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    # SERVER-SIDE AUTHORIZATION: Verify class teacher assignment
    auth_check = query_one(
        "SELECT 1 FROM class_teacher_assignments WHERE teacher_id = %s AND class_id = %s",
        (teacher['id'], student['class_id'])
    )
    if not auth_check:
        return jsonify({'error': 'Access Denied: You are not authorized to mentor students in this class.'}), 403

    existing = query_one(
        "SELECT id FROM class_teacher_notes WHERE teacher_id = %s AND student_id = %s",
        (teacher['id'], student['id'])
    )
    if existing:
        execute(
            "UPDATE class_teacher_notes SET note_text = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
            (note_text, existing['id'])
        )
    else:
        execute(
            "INSERT INTO class_teacher_notes (teacher_id, student_id, note_text) VALUES (%s, %s, %s)",
            (teacher['id'], student['id'], note_text)
        )

    return jsonify({'success': True, 'message': 'Mentoring note saved.'})

# ---------------------------------------------------------------------
# Subject Teacher Portal API (Class & Subject Selection)
# ---------------------------------------------------------------------

@app.route('/api/subject-teacher/classes', methods=['GET'])
@role_required('subject_teacher')
def api_subject_teacher_classes():
    teacher = query_one("SELECT id FROM teachers WHERE user_id = %s", (session['user_id'],))
    if not teacher:
        return jsonify([]), 200

    classes = query_all(
        """SELECT DISTINCT c.id, c.code, c.name 
           FROM teacher_subject_assignments tsa 
           JOIN classes c ON tsa.class_id = c.id 
           WHERE tsa.teacher_id = %s 
           ORDER BY c.code ASC""",
        (teacher['id'],)
    )
    return jsonify(classes)

@app.route('/api/subject-teacher/subjects', methods=['GET'])
@role_required('subject_teacher')
def api_subject_teacher_subjects():
    teacher = query_one("SELECT id FROM teachers WHERE user_id = %s", (session['user_id'],))
    if not teacher:
        return jsonify([]), 200

    class_code = request.args.get('class_code') or request.args.get('class_id')
    if not class_code:
        return jsonify({'error': 'class_code is required'}), 400

    subjects = query_all(
        """SELECT DISTINCT s.id, s.code, s.name 
           FROM teacher_subject_assignments tsa 
           JOIN subjects s ON tsa.subject_id = s.id 
           JOIN classes c ON tsa.class_id = c.id 
           WHERE tsa.teacher_id = %s AND (c.code = %s OR c.id = %s) 
           ORDER BY s.name ASC""",
        (teacher['id'], class_code, class_code)
    )
    return jsonify(subjects)

@app.route('/api/subject-teacher/students', methods=['GET'])
@role_required('subject_teacher')
def api_subject_teacher_students():
    teacher = query_one("SELECT id FROM teachers WHERE user_id = %s", (session['user_id'],))
    if not teacher:
        return jsonify({'error': 'Teacher record not found'}), 404

    class_code = request.args.get('class_code')
    subject_code = request.args.get('subject_code')

    if not class_code or not subject_code:
        return jsonify({'error': 'Both class_code and subject_code are required.'}), 400

    # SERVER-SIDE AUTHORIZATION: Teacher must be assigned to this Class AND Subject
    auth_check = query_one(
        """SELECT c.id as class_id, c.code as class_code, s.id as subject_id, s.name as subject_name 
           FROM teacher_subject_assignments tsa 
           JOIN classes c ON tsa.class_id = c.id 
           JOIN subjects s ON tsa.subject_id = s.id 
           WHERE tsa.teacher_id = %s 
             AND (c.code = %s OR c.id = %s) 
             AND (s.code = %s OR s.id = %s)""",
        (teacher['id'], class_code, class_code, subject_code, subject_code)
    )

    if not auth_check:
        return jsonify({
            'error': f"Access Denied: You are not authorized to teach subject '{subject_code}' in class '{class_code}'."
        }), 403

    class_id = auth_check['class_id']
    subject_id = auth_check['subject_id']

    # Chronological assessments for this class and subject
    assessments = query_all(
        """SELECT id, name, max_marks, sequence_order 
           FROM assessments 
           WHERE class_id = %s AND subject_id = %s 
           ORDER BY sequence_order ASC""",
        (class_id, subject_id)
    )

    # Students enrolled in this class
    students = query_all(
        """SELECT s.id as student_db_id, s.roll_number as id, u.full_name as name, 
                  s.phone, c.code as class 
           FROM students s 
           JOIN users u ON s.user_id = u.id 
           JOIN classes c ON s.class_id = c.id 
           WHERE s.class_id = %s 
           ORDER BY u.full_name ASC""",
        (class_id,)
    )

    results = []
    for s in students:
        # Subject attendance
        att = query_one(
            "SELECT attended_classes, total_classes FROM attendance WHERE student_id = %s AND subject_id = %s",
            (s['student_db_id'], subject_id)
        )
        attended = att['attended_classes'] if att else 0
        total_cls = att['total_classes'] if att else 0
        att_pct = round((attended / total_cls * 100)) if total_cls > 0 else 0

        # Assessment marks in chronological order
        student_assessments = []
        valid_scores = []
        for a in assessments:
            m = query_one(
                "SELECT marks_obtained FROM marks WHERE assessment_id = %s AND student_id = %s",
                (a['id'], s['student_db_id'])
            )
            score = float(m['marks_obtained']) if m else None
            student_assessments.append([a['name'], score, a['max_marks']])
            if score is not None:
                valid_scores.append(score)

        # Latest mark
        latest_marks = valid_scores[-1] if valid_scores else 0
        max_marks = 100

        # CHRONOLOGICAL 3-CONSECUTIVE ASSESSMENT EARLY WARNING RULE
        # Evaluates strictly decreasing marks across 3 consecutive assessments in chronological order.
        # Missing assessments are ignored, NOT treated as 0.
        early_warning = False
        trend_str = ""
        if len(valid_scores) >= 3:
            if valid_scores[-3] > valid_scores[-2] and valid_scores[-2] > valid_scores[-1]:
                early_warning = True
                trend_str = f"{valid_scores[-3]} → {valid_scores[-2]} → {valid_scores[-1]}"

        # Topics
        topics = query_all(
            """SELECT t.name, COALESCE(p.completion_pct, 0) as pct 
               FROM topics t 
               LEFT JOIN student_topic_progress p ON t.id = p.topic_id AND p.student_id = %s 
               WHERE t.subject_id = %s 
               ORDER BY t.order_index ASC""",
            (s['student_db_id'], subject_id)
        )

        results.append({
            'student_db_id': s['student_db_id'],
            'id': s['id'],
            'name': s['name'],
            'class': s['class'],
            'marks': latest_marks,
            'max': max_marks,
            'attendance': att_pct,
            'attended': attended,
            'classes': total_cls,
            'early_warning': early_warning,
            'trend': trend_str,
            'assessments': student_assessments,
            'topics': [[t['name'], t['pct']] for t in topics],
            'phone': s['phone'] or 'N/A'
        })

    # Sort students: Early warning first, then low marks (<40)
    results.sort(key=lambda x: (
        not x['early_warning'],
        0 if x['marks'] < 40 else 1 if x['marks'] < 70 else 2,
        x['marks'],
        x['name']
    ))

    return jsonify({
        'class': auth_check['class_code'],
        'subject': auth_check['subject_name'],
        'students': results
    })

@app.route('/api/subject-teacher/marks', methods=['POST'])
@role_required('subject_teacher')
def api_subject_teacher_save_marks():
    teacher = query_one("SELECT id FROM teachers WHERE user_id = %s", (session['user_id'],))
    if not teacher:
        return jsonify({'error': 'Teacher not found'}), 404

    data = request.get_json() or {}
    roll_number = data.get('student_id', '').strip()
    class_code = data.get('class_code', '').strip()
    subject_code = data.get('subject_id', '').strip()
    marks_val = data.get('marks')
    attended_val = data.get('attended')
    total_classes_val = data.get('total_classes')

    # SERVER-SIDE AUTHORIZATION: Verify teacher assignment
    auth_check = query_one(
        """SELECT c.id as class_id, s.id as subject_id 
           FROM teacher_subject_assignments tsa 
           JOIN classes c ON tsa.class_id = c.id 
           JOIN subjects s ON tsa.subject_id = s.id 
           WHERE tsa.teacher_id = %s 
             AND (c.code = %s OR c.id = %s) 
             AND (s.code = %s OR s.id = %s)""",
        (teacher['id'], class_code, class_code, subject_code, subject_code)
    )
    if not auth_check:
        return jsonify({'error': 'Access Denied: You are not authorized to modify marks for this subject and class.'}), 403

    # The target student must belong to the exact class authorized above.
    student = query_one(
        "SELECT id FROM students WHERE roll_number = %s AND class_id = %s",
        (roll_number, auth_check['class_id'])
    )
    if not student:
        return jsonify({'error': 'Student not found in the authorized class.'}), 404

    # Validate numeric values before writing academic records.
    try:
        if marks_val is not None:
            marks_val = float(marks_val)
            if not (marks_val >= 0):
                raise ValueError
        if attended_val is not None:
            attended_val = int(attended_val)
        if total_classes_val is not None:
            total_classes_val = int(total_classes_val)
    except (TypeError, ValueError, OverflowError):
        return jsonify({'error': 'Marks must be a non-negative number and attendance must use whole numbers.'}), 400

    if (attended_val is not None or total_classes_val is not None):
        if attended_val is None or total_classes_val is None:
            return jsonify({'error': 'Provide both attended and total classes.'}), 400
        if total_classes_val < 0 or attended_val < 0 or attended_val > total_classes_val:
            return jsonify({'error': 'Attendance must satisfy 0 <= attended <= total classes.'}), 400

    # Update or insert attendance
    if attended_val is not None and total_classes_val is not None:
        att = query_one(
            "SELECT id FROM attendance WHERE student_id = %s AND subject_id = %s",
            (student['id'], auth_check['subject_id'])
        )
        if att:
            execute(
                "UPDATE attendance SET attended_classes = %s, total_classes = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
                (attended_val, total_classes_val, att['id'])
            )
        else:
            execute(
                "INSERT INTO attendance (student_id, subject_id, attended_classes, total_classes) VALUES (%s, %s, %s, %s)",
                (student['id'], auth_check['subject_id'], attended_val, total_classes_val)
            )

    # Update latest assessment marks
    if marks_val is not None:
        last_assess = query_one(
            """SELECT id FROM assessments 
               WHERE class_id = %s AND subject_id = %s 
               ORDER BY sequence_order DESC LIMIT 1""",
            (auth_check['class_id'], auth_check['subject_id'])
        )
        if not last_assess:
            return jsonify({'error': 'No assessment is configured for this class and subject.'}), 400
        assessment = query_one("SELECT max_marks FROM assessments WHERE id = %s", (last_assess['id'],))
        if marks_val > float(assessment['max_marks']):
            return jsonify({'error': f"Marks cannot exceed the assessment maximum of {assessment['max_marks']}."}), 400
        if last_assess:
            existing_mark = query_one(
                "SELECT id FROM marks WHERE assessment_id = %s AND student_id = %s",
                (last_assess['id'], student['id'])
            )
            if existing_mark:
                execute(
                    "UPDATE marks SET marks_obtained = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
                    (marks_val, existing_mark['id'])
                )
            else:
                execute(
                    "INSERT INTO marks (assessment_id, student_id, marks_obtained) VALUES (%s, %s, %s)",
                    (last_assess['id'], student['id'], marks_val)
                )

    return jsonify({'success': True, 'message': f"Marks and attendance recorded successfully in {get_active_engine().upper()} database."})

# ---------------------------------------------------------------------
# Support Line Portal API
# ---------------------------------------------------------------------

@app.route('/api/support/tickets', methods=['GET', 'POST'])
@role_required('support', 'student')
def api_support_tickets():
    user_id = session['user_id']
    role = session['role']

    if request.method == 'GET':
        if role == 'support':
            # Support staff sees all tickets
            tickets = query_all(
                """SELECT t.id, t.ticket_number, t.category, t.subject_line, t.description, 
                          t.priority, t.status, t.created_at, 
                          u_stu.full_name as student_name, s.roll_number as student_id 
                   FROM support_tickets t 
                   JOIN students s ON t.student_id = s.id 
                   JOIN users u_stu ON s.user_id = u_stu.id 
                   ORDER BY t.created_at DESC"""
            )
        else:
            # Student sees only their own tickets
            tickets = query_all(
                """SELECT t.id, t.ticket_number, t.category, t.subject_line, t.description, 
                          t.priority, t.status, t.created_at, 
                          u_stu.full_name as student_name, s.roll_number as student_id 
                   FROM support_tickets t 
                   JOIN students s ON t.student_id = s.id 
                   JOIN users u_stu ON s.user_id = u_stu.id 
                   WHERE s.user_id = %s 
                   ORDER BY t.created_at DESC""",
                (user_id,)
            )

        cat_labels = {
            'academic_difficulty': 'Academic Difficulty',
            'technical_issue': 'Technical Issue',
            'attendance_concern': 'Attendance Concern',
            'personal_support': 'Personal Support Request',
            'other': 'Other'
        }

        output = []
        for t in tickets:
            replies = query_all(
                """SELECT author_name as author, role, message, created_at as time 
                   FROM ticket_replies 
                   WHERE ticket_id = %s 
                   ORDER BY created_at ASC""",
                (t['id'],)
            )
            output.append({
                'id': t['ticket_number'],
                'studentName': t['student_name'],
                'studentId': t['student_id'],
                'category': t['category'],
                'categoryLabel': cat_labels.get(t['category'], 'General'),
                'subjectLine': t['subject_line'],
                'description': t['description'],
                'priority': t['priority'],
                'status': t['status'],
                'createdDate': str(t['created_at'])[:16],
                'replies': [{
                    'author': r['author'],
                    'role': r['role'],
                    'message': r['message'],
                    'time': str(r['time'])[:16]
                } for r in replies]
            })
        return jsonify(output)

    # POST: Create new ticket
    data = request.get_json() or {}
    student_id_val = data.get('studentId', '').strip()
    category = data.get('category', 'other')
    subject_line = data.get('subjectLine', '').strip()
    description = data.get('description', '').strip()
    priority = data.get('priority', 'medium')

    allowed_categories = {'academic_difficulty', 'technical_issue', 'attendance_concern', 'personal_support', 'other'}
    allowed_priorities = {'low', 'medium', 'high'}
    if not subject_line or not description:
        return jsonify({'error': 'Subject line and description are required.'}), 400
    if len(subject_line) > 200 or len(description) > 5000:
        return jsonify({'error': 'Subject line must be <= 200 characters and description <= 5000 characters.'}), 400
    if category not in allowed_categories or priority not in allowed_priorities:
        return jsonify({'error': 'Invalid ticket category or priority.'}), 400

    # Students can create tickets only for themselves; support must specify a real student.
    if role == 'student':
        student = query_one("SELECT id, roll_number FROM students WHERE user_id = %s", (user_id,))
    else:
        if not student_id_val:
            return jsonify({'error': 'A valid student roll number is required.'}), 400
        student = query_one("SELECT id, roll_number FROM students WHERE roll_number = %s", (student_id_val,))
    if not student:
        return jsonify({'error': 'Student not found.'}), 404

    # Random suffix avoids count-based collisions after deletions or concurrent requests.
    new_tck_num = f"TCK-{secrets.token_hex(4).upper()}"

    tck_id = execute(
        """INSERT INTO support_tickets 
           (ticket_number, student_id, category, subject_line, description, priority, status) 
           VALUES (%s, %s, %s, %s, %s, %s, 'open')""",
        (new_tck_num, student['id'], category, subject_line, description, priority)
    )

    execute(
        "INSERT INTO ticket_replies (ticket_id, user_id, author_name, role, message) VALUES (%s, %s, %s, %s, %s)",
        (tck_id, user_id, session.get('name', 'Student'), session.get('role', 'student'), description)
    )

    return jsonify({'success': True, 'ticket_id': new_tck_num})

@app.route('/api/support/reply', methods=['POST'])
@role_required('support', 'student')
def api_support_reply():
    data = request.get_json() or {}
    tck_num = data.get('ticket_id')
    message = data.get('message', '').strip()
    new_status = data.get('status')

    if not tck_num or not message:
        return jsonify({'error': 'Ticket ID and message are required.'}), 400

    if len(message) > 5000:
        return jsonify({'error': 'Reply must be 5000 characters or fewer.'}), 400

    if session.get('role') == 'student':
        ticket = query_one(
            """SELECT t.id FROM support_tickets t
               JOIN students s ON t.student_id = s.id
               WHERE t.ticket_number = %s AND s.user_id = %s""",
            (tck_num, session['user_id'])
        )
    else:
        ticket = query_one("SELECT id FROM support_tickets WHERE ticket_number = %s", (tck_num,))
    if not ticket:
        # Do not disclose whether another student's ticket exists.
        return jsonify({'error': 'Ticket not found or access denied.'}), 404

    if session.get('role') == 'student' and new_status:
        return jsonify({'error': 'Students cannot change ticket status.'}), 403
    if session.get('role') == 'support' and new_status and new_status not in {'open', 'in_progress', 'resolved', 'closed'}:
        return jsonify({'error': 'Invalid ticket status.'}), 400

    author_name = f"{session.get('name')} ({session.get('role').replace('_', ' ').title()})"
    execute(
        "INSERT INTO ticket_replies (ticket_id, user_id, author_name, role, message) VALUES (%s, %s, %s, %s, %s)",
        (ticket['id'], session['user_id'], author_name, session['role'], message)
    )

    if new_status and session.get('role') == 'support':
        execute(
            "UPDATE support_tickets SET status = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
            (new_status, ticket['id'])
        )

    return jsonify({'success': True, 'message': 'Reply submitted.'})

# ---------------------------------------------------------------------
# Application Entry Point
# ---------------------------------------------------------------------

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = bool(int(os.getenv('FLASK_DEBUG', '0')))
    print(f"\n==================================================================")
    print(f" UDAAN Academic Portal Server Running on http://127.0.0.1:{port}")
    print(f" Active Database Engine: {get_active_engine().upper()}")
    print(f"==================================================================\n")
    app.run(host='127.0.0.1', port=port, debug=debug)
