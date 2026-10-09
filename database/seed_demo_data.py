import argparse
import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from werkzeug.security import generate_password_hash
from database.db import get_db, execute, query_one, get_active_engine, init_sqlite_schema

def seed(reset=False):
    conn = get_db()
    engine = get_active_engine()
    print(f"[*] Initializing and seeding database using engine: {engine.upper()}")

    if engine == 'sqlite':
        init_sqlite_schema(conn)
    conn.close()

    existing = query_one("SELECT COUNT(*) AS cnt FROM users")
    if existing and existing['cnt'] and not reset:
        raise RuntimeError(
            "The database already contains users. Seeding will not delete data by default. "
            "Use --reset only on a disposable demo database."
        )

    # Destructive reset is opt-in and only for disposable demo databases.
    tables = [
        'ticket_replies', 'support_tickets', 'class_teacher_notes', 'student_notes',
        'student_topic_progress', 'topics', 'attendance', 'marks', 'assessments',
        'teacher_subject_assignments', 'class_teacher_assignments', 'teachers',
        'students', 'subjects', 'classes', 'users'
    ]
    if reset:
        for tbl in tables:
            execute(f"DELETE FROM {tbl};")

    print("[*] Inserting safe demo users with hashed passwords...")
    # Demo Users
    users_data = [
        # Students
        ('student1', 'student123', 'Meghana Rao', 'student', 'meghana@udaan.edu'),
        ('student_aarav', 'student123', 'Aarav Reddy', 'student', 'aarav@udaan.edu'),
        ('student_rohit', 'student123', 'Rohit Naidu', 'student', 'rohit@udaan.edu'),
        ('student_ishaan', 'student123', 'Ishaan Varma', 'student', 'ishaan@udaan.edu'),
        ('student_karthik', 'student123', 'Karthik Dev', 'student', 'karthik@udaan.edu'),
        ('student_vikram', 'student123', 'Vikram Singh', 'student', 'vikram@udaan.edu'),
        ('student_aditya', 'student123', 'Aditya Paul', 'student', 'aditya@udaan.edu'),
        ('student_saanvi', 'student123', 'Saanvi Kumar', 'student', 'saanvi@udaan.edu'),
        ('student_nitya', 'student123', 'Nitya Rao', 'student', 'nitya@udaan.edu'),
        ('student_mira', 'student123', 'Mira Joshi', 'student', 'mira@udaan.edu'),
        ('student_tarun', 'student123', 'Tarun Verma', 'student', 'tarun@udaan.edu'),
        
        # Class Teacher
        ('teacher_class', 'class123', 'Dr. Raman', 'class_teacher', 'raman@udaan.edu'),
        
        # Subject Teacher
        ('teacher_priya', 'priya123', 'Ms. Priya', 'subject_teacher', 'priya@udaan.edu'),
        
        # Support Staff
        ('support_staff', 'support123', 'Alex Patel', 'support', 'alex.support@udaan.edu')
    ]

    user_ids = {}
    for u, p, name, role, email in users_data:
        p_hash = generate_password_hash(p)
        uid = execute(
            "INSERT INTO users (username, password_hash, full_name, role, email) VALUES (%s, %s, %s, %s, %s)",
            (u, p_hash, name, role, email)
        )
        user_ids[u] = uid

    # 2. Classes
    print("[*] Inserting classes...")
    classes_data = [
        ('CSE-A', 'B.Tech CSE · 2nd Year · Section A', 2, 'A'),
        ('CSE-B', 'B.Tech CSE · 2nd Year · Section B', 2, 'B'),
        ('CSE-C', 'B.Tech CSE · 2nd Year · Section C', 2, 'C'),
        ('ECE-A', 'B.Tech ECE · 2nd Year · Section A', 2, 'A')
    ]
    class_ids = {}
    for code, name, year, sec in classes_data:
        cid = execute(
            "INSERT INTO classes (code, name, year_level, section) VALUES (%s, %s, %s, %s)",
            (code, name, year, sec)
        )
        class_ids[code] = cid

    # 3. Teachers
    print("[*] Inserting teacher profiles...")
    # Dr. Raman (Class Teacher)
    t_raman_id = execute(
        "INSERT INTO teachers (user_id, employee_id, department, phone) VALUES (%s, %s, %s, %s)",
        (user_ids['teacher_class'], 'EMP-CT-201', 'Computer Science', '9876543201')
    )
    # Ms. Priya (Subject Teacher)
    t_priya_id = execute(
        "INSERT INTO teachers (user_id, employee_id, department, phone) VALUES (%s, %s, %s, %s)",
        (user_ids['teacher_priya'], 'EMP-ST-101', 'Computer Science', '9876543101')
    )

    # 4. Class Teacher Assignment
    # Dr. Raman is class teacher of CSE-A
    execute(
        "INSERT INTO class_teacher_assignments (teacher_id, class_id, academic_year) VALUES (%s, %s, %s)",
        (t_raman_id, class_ids['CSE-A'], '2025-2026')
    )

    # 5. Subjects
    print("[*] Inserting subjects...")
    subjects_data = [
        ('DSA', 'Data Structures & Algorithms', '⌘', '#e7f2ff', '#3e87e7'),
        ('JAVA', 'Java Programming', '♨', '#fff0e8', '#dc783d'),
        ('MATH', 'Mathematics', '▦', '#fff2d9', '#c88817'),
        ('CN', 'Computer Networks', '⌘', '#eeeaff', '#6d61d9')
    ]
    subject_ids = {}
    for code, name, icon, color, ink in subjects_data:
        sid = execute(
            "INSERT INTO subjects (code, name, icon, color, ink) VALUES (%s, %s, %s, %s, %s)",
            (code, name, icon, color, ink)
        )
        subject_ids[code] = sid

    # 6. Subject Teacher Assignments (Ms. Priya teaches across multiple classes)
    print("[*] Inserting subject teacher class/subject assignments...")
    # Ms. Priya teaches:
    # - CSE-A: DSA and CN
    # - CSE-B: DSA
    # - ECE-A: CN
    execute("INSERT INTO teacher_subject_assignments (teacher_id, class_id, subject_id) VALUES (%s, %s, %s)",
            (t_priya_id, class_ids['CSE-A'], subject_ids['DSA']))
    execute("INSERT INTO teacher_subject_assignments (teacher_id, class_id, subject_id) VALUES (%s, %s, %s)",
            (t_priya_id, class_ids['CSE-A'], subject_ids['CN']))
    execute("INSERT INTO teacher_subject_assignments (teacher_id, class_id, subject_id) VALUES (%s, %s, %s)",
            (t_priya_id, class_ids['CSE-B'], subject_ids['DSA']))
    execute("INSERT INTO teacher_subject_assignments (teacher_id, class_id, subject_id) VALUES (%s, %s, %s)",
            (t_priya_id, class_ids['ECE-A'], subject_ids['CN']))

    # 7. Students
    print("[*] Inserting students...")
    students_data = [
        # CSE-A
        ('student1', 'CSE2402', 'CSE-A', '9876501202', 7),
        ('student_aarav', 'CSE2401', 'CSE-A', '9876501201', 5),
        ('student_rohit', 'CSE2415', 'CSE-A', '9876501215', 3),
        ('student_ishaan', 'CSE2403', 'CSE-A', '9876501203', 6),
        ('student_karthik', 'CSE2417', 'CSE-A', '9876501217', 4),
        ('student_vikram', 'CSE2405', 'CSE-A', '9876501205', 9),
        ('student_aditya', 'CSE2419', 'CSE-A', '9876501219', 11),
        # CSE-B
        ('student_saanvi', 'CSE2408', 'CSE-B', '9876501208', 4),
        ('student_nitya', 'CSE2410', 'CSE-B', '9876501210', 8),
        ('student_mira', 'CSE2412', 'CSE-B', '9876501212', 12),
        # ECE-A
        ('student_tarun', 'ECE2401', 'ECE-A', '9876501250', 5)
    ]

    student_ids = {}
    for ukey, roll, clscode, phone, streak in students_data:
        sid = execute(
            "INSERT INTO students (user_id, roll_number, class_id, phone, streak_days) VALUES (%s, %s, %s, %s, %s)",
            (user_ids[ukey], roll, class_ids[clscode], phone, streak)
        )
        student_ids[ukey] = sid

    # 8. Assessments
    print("[*] Inserting assessments...")
    # Assessments for CSE-A DSA
    a_dsa1 = execute("INSERT INTO assessments (class_id, subject_id, name, max_marks, sequence_order, assessment_date) VALUES (%s, %s, %s, %s, %s, %s)",
                     (class_ids['CSE-A'], subject_ids['DSA'], 'Quiz 1', 100, 1, '2026-08-15'))
    a_dsa2 = execute("INSERT INTO assessments (class_id, subject_id, name, max_marks, sequence_order, assessment_date) VALUES (%s, %s, %s, %s, %s, %s)",
                     (class_ids['CSE-A'], subject_ids['DSA'], 'Mid-Term 1', 100, 2, '2026-09-10'))
    a_dsa3 = execute("INSERT INTO assessments (class_id, subject_id, name, max_marks, sequence_order, assessment_date) VALUES (%s, %s, %s, %s, %s, %s)",
                     (class_ids['CSE-A'], subject_ids['DSA'], 'Unit Test 2', 100, 3, '2026-10-01'))

    # Assessments for CSE-A CN
    a_cn1 = execute("INSERT INTO assessments (class_id, subject_id, name, max_marks, sequence_order, assessment_date) VALUES (%s, %s, %s, %s, %s, %s)",
                    (class_ids['CSE-A'], subject_ids['CN'], 'Quiz 1', 100, 1, '2026-08-20'))
    a_cn2 = execute("INSERT INTO assessments (class_id, subject_id, name, max_marks, sequence_order, assessment_date) VALUES (%s, %s, %s, %s, %s, %s)",
                    (class_ids['CSE-A'], subject_ids['CN'], 'Mid-Term 1', 100, 2, '2026-09-15'))
    a_cn3 = execute("INSERT INTO assessments (class_id, subject_id, name, max_marks, sequence_order, assessment_date) VALUES (%s, %s, %s, %s, %s, %s)",
                    (class_ids['CSE-A'], subject_ids['CN'], 'Unit Test 2', 100, 3, '2026-10-05'))

    # Assessments for CSE-A JAVA
    a_java1 = execute("INSERT INTO assessments (class_id, subject_id, name, max_marks, sequence_order, assessment_date) VALUES (%s, %s, %s, %s, %s, %s)",
                      (class_ids['CSE-A'], subject_ids['JAVA'], 'Unit Test 1', 100, 1, '2026-09-12'))
    # Assessments for CSE-A MATH
    a_math1 = execute("INSERT INTO assessments (class_id, subject_id, name, max_marks, sequence_order, assessment_date) VALUES (%s, %s, %s, %s, %s, %s)",
                      (class_ids['CSE-A'], subject_ids['MATH'], 'Unit Test 1', 100, 1, '2026-09-18'))

    # Assessments for CSE-B DSA
    a_b_dsa1 = execute("INSERT INTO assessments (class_id, subject_id, name, max_marks, sequence_order, assessment_date) VALUES (%s, %s, %s, %s, %s, %s)",
                       (class_ids['CSE-B'], subject_ids['DSA'], 'Quiz 1', 100, 1, '2026-08-16'))
    a_b_dsa2 = execute("INSERT INTO assessments (class_id, subject_id, name, max_marks, sequence_order, assessment_date) VALUES (%s, %s, %s, %s, %s, %s)",
                       (class_ids['CSE-B'], subject_ids['DSA'], 'Mid-Term 1', 100, 2, '2026-09-12'))
    a_b_dsa3 = execute("INSERT INTO assessments (class_id, subject_id, name, max_marks, sequence_order, assessment_date) VALUES (%s, %s, %s, %s, %s, %s)",
                       (class_ids['CSE-B'], subject_ids['DSA'], 'Unit Test 2', 100, 3, '2026-10-02'))

    # Assessments for ECE-A CN
    a_ece_cn1 = execute("INSERT INTO assessments (class_id, subject_id, name, max_marks, sequence_order, assessment_date) VALUES (%s, %s, %s, %s, %s, %s)",
                        (class_ids['ECE-A'], subject_ids['CN'], 'Quiz 1', 100, 1, '2026-08-22'))
    a_ece_cn2 = execute("INSERT INTO assessments (class_id, subject_id, name, max_marks, sequence_order, assessment_date) VALUES (%s, %s, %s, %s, %s, %s)",
                        (class_ids['ECE-A'], subject_ids['CN'], 'Mid-Term 1', 100, 2, '2026-09-18'))
    a_ece_cn3 = execute("INSERT INTO assessments (class_id, subject_id, name, max_marks, sequence_order, assessment_date) VALUES (%s, %s, %s, %s, %s, %s)",
                        (class_ids['ECE-A'], subject_ids['CN'], 'Unit Test 2', 100, 3, '2026-10-06'))

    # 9. Marks - Including strictly decreasing scores for the Early-Warning rule!
    print("[*] Inserting assessment marks (including 3-consecutive decline early-warning records)...")
    # Aarav Reddy: 51 -> 39 -> 28 (Strictly Decreasing across 3 consecutive tests -> Early Warning!)
    execute("INSERT INTO marks (assessment_id, student_id, marks_obtained) VALUES (%s, %s, %s)", (a_dsa1, student_ids['student_aarav'], 51.0))
    execute("INSERT INTO marks (assessment_id, student_id, marks_obtained) VALUES (%s, %s, %s)", (a_dsa2, student_ids['student_aarav'], 39.0))
    execute("INSERT INTO marks (assessment_id, student_id, marks_obtained) VALUES (%s, %s, %s)", (a_dsa3, student_ids['student_aarav'], 28.0))

    # Rohit Naidu: 55 -> 48 -> 39 (Strictly Decreasing -> Early Warning!)
    execute("INSERT INTO marks (assessment_id, student_id, marks_obtained) VALUES (%s, %s, %s)", (a_dsa1, student_ids['student_rohit'], 55.0))
    execute("INSERT INTO marks (assessment_id, student_id, marks_obtained) VALUES (%s, %s, %s)", (a_dsa2, student_ids['student_rohit'], 48.0))
    execute("INSERT INTO marks (assessment_id, student_id, marks_obtained) VALUES (%s, %s, %s)", (a_dsa3, student_ids['student_rohit'], 39.0))

    # Karthik Dev: 64 -> 60 -> 56 (Strictly Decreasing -> Early Warning!)
    execute("INSERT INTO marks (assessment_id, student_id, marks_obtained) VALUES (%s, %s, %s)", (a_dsa1, student_ids['student_karthik'], 64.0))
    execute("INSERT INTO marks (assessment_id, student_id, marks_obtained) VALUES (%s, %s, %s)", (a_dsa2, student_ids['student_karthik'], 60.0))
    execute("INSERT INTO marks (assessment_id, student_id, marks_obtained) VALUES (%s, %s, %s)", (a_dsa3, student_ids['student_karthik'], 56.0))

    # Ishaan Varma: 43 -> 52 -> 48 (Not 3-consecutive decrease)
    execute("INSERT INTO marks (assessment_id, student_id, marks_obtained) VALUES (%s, %s, %s)", (a_dsa1, student_ids['student_ishaan'], 43.0))
    execute("INSERT INTO marks (assessment_id, student_id, marks_obtained) VALUES (%s, %s, %s)", (a_dsa2, student_ids['student_ishaan'], 52.0))
    execute("INSERT INTO marks (assessment_id, student_id, marks_obtained) VALUES (%s, %s, %s)", (a_dsa3, student_ids['student_ishaan'], 48.0))

    # Vikram Singh: 68 -> 70 -> 72 (Increasing)
    execute("INSERT INTO marks (assessment_id, student_id, marks_obtained) VALUES (%s, %s, %s)", (a_dsa1, student_ids['student_vikram'], 68.0))
    execute("INSERT INTO marks (assessment_id, student_id, marks_obtained) VALUES (%s, %s, %s)", (a_dsa2, student_ids['student_vikram'], 70.0))
    execute("INSERT INTO marks (assessment_id, student_id, marks_obtained) VALUES (%s, %s, %s)", (a_dsa3, student_ids['student_vikram'], 72.0))

    # Aditya Paul: 82 -> 85 -> 88 (High performer)
    execute("INSERT INTO marks (assessment_id, student_id, marks_obtained) VALUES (%s, %s, %s)", (a_dsa1, student_ids['student_aditya'], 82.0))
    execute("INSERT INTO marks (assessment_id, student_id, marks_obtained) VALUES (%s, %s, %s)", (a_dsa2, student_ids['student_aditya'], 85.0))
    execute("INSERT INTO marks (assessment_id, student_id, marks_obtained) VALUES (%s, %s, %s)", (a_dsa3, student_ids['student_aditya'], 88.0))

    # Meghana Rao:
    execute("INSERT INTO marks (assessment_id, student_id, marks_obtained) VALUES (%s, %s, %s)", (a_dsa3, student_ids['student1'], 65.0))
    execute("INSERT INTO marks (assessment_id, student_id, marks_obtained) VALUES (%s, %s, %s)", (a_java1, student_ids['student1'], 78.0))
    execute("INSERT INTO marks (assessment_id, student_id, marks_obtained) VALUES (%s, %s, %s)", (a_math1, student_ids['student1'], 72.0))
    execute("INSERT INTO marks (assessment_id, student_id, marks_obtained) VALUES (%s, %s, %s)", (a_cn3, student_ids['student1'], 68.0))

    # CSE-B Saanvi Kumar: 58 -> 46 -> 34 (Early Warning in CSE-B DSA!)
    execute("INSERT INTO marks (assessment_id, student_id, marks_obtained) VALUES (%s, %s, %s)", (a_b_dsa1, student_ids['student_saanvi'], 58.0))
    execute("INSERT INTO marks (assessment_id, student_id, marks_obtained) VALUES (%s, %s, %s)", (a_b_dsa2, student_ids['student_saanvi'], 46.0))
    execute("INSERT INTO marks (assessment_id, student_id, marks_obtained) VALUES (%s, %s, %s)", (a_b_dsa3, student_ids['student_saanvi'], 34.0))

    # CSE-B Nitya Rao: 48 -> 51 -> 52
    execute("INSERT INTO marks (assessment_id, student_id, marks_obtained) VALUES (%s, %s, %s)", (a_b_dsa1, student_ids['student_nitya'], 48.0))
    execute("INSERT INTO marks (assessment_id, student_id, marks_obtained) VALUES (%s, %s, %s)", (a_b_dsa2, student_ids['student_nitya'], 51.0))
    execute("INSERT INTO marks (assessment_id, student_id, marks_obtained) VALUES (%s, %s, %s)", (a_b_dsa3, student_ids['student_nitya'], 52.0))

    # CSE-B Mira Joshi: 76 -> 79 -> 81
    execute("INSERT INTO marks (assessment_id, student_id, marks_obtained) VALUES (%s, %s, %s)", (a_b_dsa1, student_ids['student_mira'], 76.0))
    execute("INSERT INTO marks (assessment_id, student_id, marks_obtained) VALUES (%s, %s, %s)", (a_b_dsa2, student_ids['student_mira'], 79.0))
    execute("INSERT INTO marks (assessment_id, student_id, marks_obtained) VALUES (%s, %s, %s)", (a_b_dsa3, student_ids['student_mira'], 81.0))

    # ECE-A Tarun Verma in CN: 65 -> 60 -> 55 (Early Warning in ECE-A CN!)
    execute("INSERT INTO marks (assessment_id, student_id, marks_obtained) VALUES (%s, %s, %s)", (a_ece_cn1, student_ids['student_tarun'], 65.0))
    execute("INSERT INTO marks (assessment_id, student_id, marks_obtained) VALUES (%s, %s, %s)", (a_ece_cn2, student_ids['student_tarun'], 60.0))
    execute("INSERT INTO marks (assessment_id, student_id, marks_obtained) VALUES (%s, %s, %s)", (a_ece_cn3, student_ids['student_tarun'], 55.0))

    # 10. Attendance
    print("[*] Inserting subject attendance...")
    # Meghana
    execute("INSERT INTO attendance (student_id, subject_id, attended_classes, total_classes) VALUES (%s, %s, %s, %s)", (student_ids['student1'], subject_ids['JAVA'], 17, 20))
    execute("INSERT INTO attendance (student_id, subject_id, attended_classes, total_classes) VALUES (%s, %s, %s, %s)", (student_ids['student1'], subject_ids['DSA'], 16, 20))
    execute("INSERT INTO attendance (student_id, subject_id, attended_classes, total_classes) VALUES (%s, %s, %s, %s)", (student_ids['student1'], subject_ids['MATH'], 18, 20))
    execute("INSERT INTO attendance (student_id, subject_id, attended_classes, total_classes) VALUES (%s, %s, %s, %s)", (student_ids['student1'], subject_ids['CN'], 15, 20))

    # Aarav (low attendance: 13 / 21 = 62%)
    execute("INSERT INTO attendance (student_id, subject_id, attended_classes, total_classes) VALUES (%s, %s, %s, %s)", (student_ids['student_aarav'], subject_ids['DSA'], 13, 21))
    execute("INSERT INTO attendance (student_id, subject_id, attended_classes, total_classes) VALUES (%s, %s, %s, %s)", (student_ids['student_aarav'], subject_ids['JAVA'], 14, 21))
    execute("INSERT INTO attendance (student_id, subject_id, attended_classes, total_classes) VALUES (%s, %s, %s, %s)", (student_ids['student_aarav'], subject_ids['MATH'], 13, 21))

    # Rohit (low attendance: 15 / 22 = 68%)
    execute("INSERT INTO attendance (student_id, subject_id, attended_classes, total_classes) VALUES (%s, %s, %s, %s)", (student_ids['student_rohit'], subject_ids['DSA'], 15, 22))
    # Ishaan
    execute("INSERT INTO attendance (student_id, subject_id, attended_classes, total_classes) VALUES (%s, %s, %s, %s)", (student_ids['student_ishaan'], subject_ids['DSA'], 18, 22))
    # Vikram
    execute("INSERT INTO attendance (student_id, subject_id, attended_classes, total_classes) VALUES (%s, %s, %s, %s)", (student_ids['student_vikram'], subject_ids['DSA'], 21, 23))
    # Aditya
    execute("INSERT INTO attendance (student_id, subject_id, attended_classes, total_classes) VALUES (%s, %s, %s, %s)", (student_ids['student_aditya'], subject_ids['DSA'], 23, 24))
    # Saanvi (CSE-B)
    execute("INSERT INTO attendance (student_id, subject_id, attended_classes, total_classes) VALUES (%s, %s, %s, %s)", (student_ids['student_saanvi'], subject_ids['DSA'], 15, 21))

    # 11. Topics & Topic Progress
    print("[*] Inserting topic milestones...")
    dsa_topics = [
        ('Arrays', 1), ('Linked Lists', 2), ('Stacks & Queues', 3), ('Trees', 4), ('Graphs', 5)
    ]
    java_topics = [
        ('Introduction to Java', 1), ('OOP Concepts', 2), ('Inheritance & Polymorphism', 3), ('Exception Handling', 4), ('File Handling', 5)
    ]
    dsa_top_ids = []
    for name, ord_idx in dsa_topics:
        tid = execute("INSERT INTO topics (subject_id, name, order_index) VALUES (%s, %s, %s)", (subject_ids['DSA'], name, ord_idx))
        dsa_top_ids.append(tid)

    java_top_ids = []
    for name, ord_idx in java_topics:
        tid = execute("INSERT INTO topics (subject_id, name, order_index) VALUES (%s, %s, %s)", (subject_ids['JAVA'], name, ord_idx))
        java_top_ids.append(tid)

    # Progress for Meghana
    execute("INSERT INTO student_topic_progress (student_id, topic_id, completion_pct) VALUES (%s, %s, %s)", (student_ids['student1'], java_top_ids[0], 100))
    execute("INSERT INTO student_topic_progress (student_id, topic_id, completion_pct) VALUES (%s, %s, %s)", (student_ids['student1'], java_top_ids[1], 85))
    execute("INSERT INTO student_topic_progress (student_id, topic_id, completion_pct) VALUES (%s, %s, %s)", (student_ids['student1'], java_top_ids[2], 60))
    execute("INSERT INTO student_topic_progress (student_id, topic_id, completion_pct) VALUES (%s, %s, %s)", (student_ids['student1'], java_top_ids[3], 0))
    execute("INSERT INTO student_topic_progress (student_id, topic_id, completion_pct) VALUES (%s, %s, %s)", (student_ids['student1'], java_top_ids[4], 0))

    execute("INSERT INTO student_topic_progress (student_id, topic_id, completion_pct) VALUES (%s, %s, %s)", (student_ids['student1'], dsa_top_ids[0], 90))
    execute("INSERT INTO student_topic_progress (student_id, topic_id, completion_pct) VALUES (%s, %s, %s)", (student_ids['student1'], dsa_top_ids[1], 55))
    execute("INSERT INTO student_topic_progress (student_id, topic_id, completion_pct) VALUES (%s, %s, %s)", (student_ids['student1'], dsa_top_ids[2], 35))
    execute("INSERT INTO student_topic_progress (student_id, topic_id, completion_pct) VALUES (%s, %s, %s)", (student_ids['student1'], dsa_top_ids[3], 20))
    execute("INSERT INTO student_topic_progress (student_id, topic_id, completion_pct) VALUES (%s, %s, %s)", (student_ids['student1'], dsa_top_ids[4], 0))

    # Progress for Aarav
    execute("INSERT INTO student_topic_progress (student_id, topic_id, completion_pct) VALUES (%s, %s, %s)", (student_ids['student_aarav'], dsa_top_ids[0], 35))
    execute("INSERT INTO student_topic_progress (student_id, topic_id, completion_pct) VALUES (%s, %s, %s)", (student_ids['student_aarav'], dsa_top_ids[1], 42))
    execute("INSERT INTO student_topic_progress (student_id, topic_id, completion_pct) VALUES (%s, %s, %s)", (student_ids['student_aarav'], dsa_top_ids[2], 30))

    # 12. Student Notes & Doubts
    print("[*] Inserting student notes & doubts...")
    execute("INSERT INTO student_notes (student_id, subject_id, note_text) VALUES (%s, %s, %s)",
            (student_ids['student1'], subject_ids['JAVA'], 'Why do we use super() in Java constructors?'))
    execute("INSERT INTO student_notes (student_id, subject_id, note_text) VALUES (%s, %s, %s)",
            (student_ids['student1'], subject_ids['DSA'], 'Revise the difference between stack and queue.'))

    # 13. Class Teacher Mentoring Notes
    print("[*] Inserting class teacher mentoring follow-up notes...")
    execute("INSERT INTO class_teacher_notes (teacher_id, student_id, note_text) VALUES (%s, %s, %s)",
            (t_raman_id, student_ids['student_aarav'], 'Attendance is below 75% threshold. Spoke with student regarding morning commute issues; counseling scheduled.'))
    execute("INSERT INTO class_teacher_notes (teacher_id, student_id, note_text) VALUES (%s, %s, %s)",
            (t_raman_id, student_ids['student_rohit'], 'Struggling with DSA theory. Advised to attend remedial tutorial sessions on Thursdays.'))

    # 14. Support Tickets & Replies
    print("[*] Inserting support tickets & conversation threads...")
    tck1 = execute(
        """INSERT INTO support_tickets 
        (ticket_number, student_id, category, subject_line, description, priority, status, assigned_to_user_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        ('TCK-101', student_ids['student_aarav'], 'academic_difficulty',
         'Need extra tutoring in Linked Lists & Pointer algorithms',
         'I scored 28 in the recent Unit Test. I am struggling to understand double pointer manipulation in Java and would appreciate mentoring support.',
         'high', 'open', user_ids['support_staff'])
    )
    execute(
        "INSERT INTO ticket_replies (ticket_id, user_id, author_name, role, message) VALUES (%s, %s, %s, %s, %s)",
        (tck1, user_ids['student_aarav'], 'Aarav Reddy (Student)', 'student',
         'I scored 28 in the recent Unit Test. I am struggling to understand double pointer manipulation in Java and would appreciate mentoring support.')
    )

    tck2 = execute(
        """INSERT INTO support_tickets 
        (ticket_number, student_id, category, subject_line, description, priority, status, assigned_to_user_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        ('TCK-102', student_ids['student1'], 'technical_issue',
         'LeetCode streak progress sync delay',
         'My DSA streak count shows 7 days on LeetCode but did not update on my student portal dashboard yesterday.',
         'medium', 'in_progress', user_ids['support_staff'])
    )
    execute(
        "INSERT INTO ticket_replies (ticket_id, user_id, author_name, role, message) VALUES (%s, %s, %s, %s, %s)",
        (tck2, user_ids['student1'], 'Meghana Rao (Student)', 'student',
         'My DSA streak count shows 7 days on LeetCode but did not update on my student portal dashboard yesterday.')
    )
    execute(
        "INSERT INTO ticket_replies (ticket_id, user_id, author_name, role, message) VALUES (%s, %s, %s, %s, %s)",
        (tck2, user_ids['support_staff'], 'Alex Patel (Support Staff)', 'support',
         'Hello Meghana, we are currently refreshing the batch synchronization token. Please allow up to 2 hours for cache refresh.')
    )

    tck3 = execute(
        """INSERT INTO support_tickets 
        (ticket_number, student_id, category, subject_line, description, priority, status, assigned_to_user_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        ('TCK-103', student_ids['student_rohit'], 'attendance_concern',
         'Medical leave attendance adjustment for DSA Lab',
         'I submitted my hospital medical certificate to the department office for 3 days of absence last week. Attendance still shows 68%.',
         'high', 'open', None)
    )
    execute(
        "INSERT INTO ticket_replies (ticket_id, user_id, author_name, role, message) VALUES (%s, %s, %s, %s, %s)",
        (tck3, user_ids['student_rohit'], 'Rohit Naidu (Student)', 'student',
         'I submitted my hospital medical certificate to the department office for 3 days of absence last week. Attendance still shows 68%.')
    )

    tck4 = execute(
        """INSERT INTO support_tickets 
        (ticket_number, student_id, category, subject_line, description, priority, status, assigned_to_user_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        ('TCK-104', student_ids['student_saanvi'], 'personal_support',
         'Request for confidential academic counseling session',
         'Feeling overwhelmed preparing for upcoming semester examinations and coding interviews. Would like to speak with a student counselor.',
         'medium', 'in_progress', user_ids['support_staff'])
    )
    execute(
        "INSERT INTO ticket_replies (ticket_id, user_id, author_name, role, message) VALUES (%s, %s, %s, %s, %s)",
        (tck4, user_ids['student_saanvi'], 'Saanvi Kumar (Student)', 'student',
         'Feeling overwhelmed preparing for upcoming semester examinations and coding interviews. Would like to speak with a student counselor.')
    )
    execute(
        "INSERT INTO ticket_replies (ticket_id, user_id, author_name, role, message) VALUES (%s, %s, %s, %s, %s)",
        (tck4, user_ids['support_staff'], 'Alex Patel (Support Staff)', 'support',
         'Hi Saanvi, we have scheduled a peaceful 1-on-1 counseling appointment for Friday at 3:00 PM in Room 104. We are here to support you.')
    )

    tck5 = execute(
        """INSERT INTO support_tickets 
        (ticket_number, student_id, category, subject_line, description, priority, status, assigned_to_user_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        ('TCK-105', student_ids['student_ishaan'], 'other',
         'Hostel WiFi connectivity in study rooms',
         'Slow internet connection preventing access to online practice compilers in Block C.',
         'low', 'resolved', user_ids['support_staff'])
    )
    execute(
        "INSERT INTO ticket_replies (ticket_id, user_id, author_name, role, message) VALUES (%s, %s, %s, %s, %s)",
        (tck5, user_ids['student_ishaan'], 'Ishaan Varma (Student)', 'student',
         'Slow internet connection preventing access to online practice compilers in Block C.')
    )
    execute(
        "INSERT INTO ticket_replies (ticket_id, user_id, author_name, role, message) VALUES (%s, %s, %s, %s, %s)",
        (tck5, user_ids['support_staff'], 'Alex Patel (Support Staff)', 'support',
         'Replaced access point router in Block C 2nd floor. Speeds verified above 100 Mbps.')
    )

    print("[OK] Database seeded successfully with complete multi-role academic records!")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Seed disposable UDAAN demo data.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete existing records before seeding. Use only with a disposable demo database."
    )
    args = parser.parse_args()
    seed(reset=args.reset)
