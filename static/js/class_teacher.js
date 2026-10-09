// UDAAN Class Teacher Portal Client

document.addEventListener('DOMContentLoaded', () => {
  const classSelect = document.getElementById('classSelect');
  const searchInput = document.getElementById('searchInput');
  const filterSelect = document.getElementById('filterSelect');
  const studentRows = document.getElementById('studentRows');
  const studentDialog = document.getElementById('studentDialog');
  const modalDetail = document.getElementById('modalDetail');
  const logoutBtn = document.getElementById('logoutBtn');

  // KPI elements
  const totalCountEl = document.getElementById('totalCount');
  const avgAttendanceEl = document.getElementById('avgAttendance');
  const goodCountEl = document.getElementById('goodCount');
  const lowCountEl = document.getElementById('lowCount');

  // Check authentication session
  const sessionData = localStorage.getItem('udaan_session');
  if (sessionData) {
    try {
      const user = JSON.parse(sessionData);
      if (user.role && user.role !== 'class_teacher') {
        // Warning: unauthorized role access
        console.warn('Role mismatch: current user is not class_teacher');
      }
      if (user.name) {
        const nameEl = document.querySelector('.teacher-name');
        if (nameEl) nameEl.textContent = user.name;
        const profileEl = document.querySelector('.teacher-profile b');
        if (profileEl) profileEl.textContent = user.name;
      }
    } catch (e) {}
  }

  // Demo Fallback Data for Class Teacher
  const demoClasses = [
    { id: '1', code: 'CSE-A', name: 'B.Tech CSE · 2nd Year · Section A', studentCount: 6 }
  ];

  const demoStudents = [
    {
      id: 'CSE2401', name: 'Aarav Reddy', class: 'CSE-A', attendance: 62, avgMarks: 45, status: 'low',
      phone: '9876501201',
      subjects: [
        { name: 'Data Structures & Algorithms', teacher: 'Ms. Priya', marks: '28 / 100', attendance: '62%' },
        { name: 'Java Programming', teacher: 'Prof. Sharma', marks: '52 / 100', attendance: '65%' },
        { name: 'Mathematics', teacher: 'Dr. Bose', marks: '55 / 100', attendance: '60%' }
      ],
      note: 'Attendance is below 75% threshold. Needs regular follow-up.'
    },
    {
      id: 'CSE2403', name: 'Ishaan Varma', class: 'CSE-A', attendance: 82, avgMarks: 68, status: 'average',
      phone: '9876501203',
      subjects: [
        { name: 'Data Structures & Algorithms', teacher: 'Ms. Priya', marks: '48 / 100', attendance: '82%' },
        { name: 'Java Programming', teacher: 'Prof. Sharma', marks: '74 / 100', attendance: '80%' },
        { name: 'Mathematics', teacher: 'Dr. Bose', marks: '82 / 100', attendance: '85%' }
      ],
      note: 'Good steady progress in all subjects.'
    },
    {
      id: 'CSE2405', name: 'Vikram Singh', class: 'CSE-A', attendance: 91, avgMarks: 84, status: 'good',
      phone: '9876501205',
      subjects: [
        { name: 'Data Structures & Algorithms', teacher: 'Ms. Priya', marks: '72 / 100', attendance: '91%' },
        { name: 'Java Programming', teacher: 'Prof. Sharma', marks: '88 / 100', attendance: '90%' },
        { name: 'Mathematics', teacher: 'Dr. Bose', marks: '92 / 100', attendance: '92%' }
      ],
      note: 'High performer. Participating in college hackathons.'
    },
    {
      id: 'CSE2415', name: 'Rohit Naidu', class: 'CSE-A', attendance: 68, avgMarks: 49, status: 'low',
      phone: '9876501215',
      subjects: [
        { name: 'Data Structures & Algorithms', teacher: 'Ms. Priya', marks: '39 / 100', attendance: '68%' },
        { name: 'Java Programming', teacher: 'Prof. Sharma', marks: '54 / 100', attendance: '70%' },
        { name: 'Mathematics', teacher: 'Dr. Bose', marks: '54 / 100', attendance: '65%' }
      ],
      note: 'Struggling in DSA theory and lab.'
    },
    {
      id: 'CSE2417', name: 'Karthik Dev', class: 'CSE-A', attendance: 79, avgMarks: 65, status: 'average',
      phone: '9876501217',
      subjects: [
        { name: 'Data Structures & Algorithms', teacher: 'Ms. Priya', marks: '56 / 100', attendance: '79%' },
        { name: 'Java Programming', teacher: 'Prof. Sharma', marks: '70 / 100', attendance: '78%' },
        { name: 'Mathematics', teacher: 'Dr. Bose', marks: '68 / 100', attendance: '80%' }
      ],
      note: 'Consistent attendance.'
    },
    {
      id: 'CSE2419', name: 'Aditya Paul', class: 'CSE-A', attendance: 96, avgMarks: 91, status: 'good',
      phone: '9876501219',
      subjects: [
        { name: 'Data Structures & Algorithms', teacher: 'Ms. Priya', marks: '88 / 100', attendance: '96%' },
        { name: 'Java Programming', teacher: 'Prof. Sharma', marks: '92 / 100', attendance: '95%' },
        { name: 'Mathematics', teacher: 'Dr. Bose', marks: '94 / 100', attendance: '98%' }
      ],
      note: 'Top rank candidate in class.'
    }
  ];

  let currentStudents = [...demoStudents];

  async function loadAssignedClasses() {
    try {
      const res = await fetch('/api/class-teacher/classes');
      if (res.ok) {
        const classes = await res.json();
        if (classes.length > 0) {
          classSelect.innerHTML = classes.map(c => `<option value="${c.id}">${escapeHtml(c.name || c.code)}</option>`).join('');
          loadClassStudents(classes[0].id);
          return;
        }
      }
    } catch (e) {}

    // Fallback demo classes
    classSelect.innerHTML = demoClasses.map(c => `<option value="${c.id}">${escapeHtml(c.name)}</option>`).join('');
    loadClassStudents(demoClasses[0].id);
  }

  async function loadClassStudents(classId) {
    try {
      const res = await fetch(`/api/class-teacher/students?class_id=${classId}`);
      if (res.ok) {
        const data = await res.json();
        if (data.students && data.students.length > 0) {
          currentStudents = data.students;
          render();
          return;
        }
      }
    } catch (e) {}

    currentStudents = [...demoStudents];
    render();
  }

  function getFilteredStudents() {
    const q = searchInput.value.trim().toLowerCase();
    const filter = filterSelect.value;

    return currentStudents.filter(s => {
      const matchesSearch = !q || s.name.toLowerCase().includes(q) || s.id.toLowerCase().includes(q);
      let matchesFilter = true;

      if (filter === 'good') matchesFilter = s.status === 'good';
      else if (filter === 'average') matchesFilter = s.status === 'average';
      else if (filter === 'low') matchesFilter = s.status === 'low';
      else if (filter === 'low_attendance') matchesFilter = s.attendance < 75;

      return matchesSearch && matchesFilter;
    });
  }

  function renderKPIs() {
    totalCountEl.textContent = currentStudents.length;
    const avgAtt = currentStudents.length ? Math.round(currentStudents.reduce((acc, s) => acc + s.attendance, 0) / currentStudents.length) : 0;
    avgAttendanceEl.textContent = `${avgAtt}%`;
    goodCountEl.textContent = currentStudents.filter(s => s.status === 'good').length;
    lowCountEl.textContent = currentStudents.filter(s => s.status === 'low' || s.attendance < 75).length;
  }

  function render() {
    renderKPIs();
    const students = getFilteredStudents();

    if (!students.length) {
      studentRows.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:32px;color:var(--muted)">No students match the selected filter.</td></tr>';
      return;
    }

    studentRows.innerHTML = students.map(s => {
      const initials = s.name.split(' ').map(n => n[0]).slice(0, 2).join('');
      const statusLabel = s.status === 'low' ? 'Needs Support' : s.status === 'average' ? 'Making Progress' : 'Good Standing';
      const statusClass = `status-${s.status}`;
      const isLowAttendance = s.attendance < 75;

      return `
        <tr data-id="${s.id}">
          <td>
            <div class="student-col">
              <span class="student-avatar">${escapeHtml(initials)}</span>
              <div class="student-meta">
                <b>${escapeHtml(s.name)}</b>
                <small>${escapeHtml(s.id)}</small>
              </div>
            </div>
          </td>
          <td>
            <div class="attendance-progress">
              <div class="progress-bar">
                <div class="progress-fill ${isLowAttendance ? 'danger' : ''}" style="width: ${s.attendance}%"></div>
              </div>
              <strong style="color: ${isLowAttendance ? 'var(--red)' : 'var(--ink)'}">${s.attendance}%</strong>
              ${isLowAttendance ? '<small style="color:var(--red);font-weight:700;">⚠ Low</small>' : ''}
            </div>
          </td>
          <td>
            <strong>${s.avgMarks}%</strong>
          </td>
          <td>
            <span class="status-badge ${statusClass}">${statusLabel}</span>
          </td>
          <td style="color:var(--muted);font-size:12px;">
            ${escapeHtml(s.note || 'None')}
          </td>
          <td>
            <button class="btn-view" data-view="${s.id}">View Record ↗</button>
          </td>
        </tr>
      `;
    }).join('');

    // Attach row view click listeners
    document.querySelectorAll('[data-view]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        openStudentDetail(btn.dataset.view);
      });
    });

    document.querySelectorAll('tbody tr').forEach(row => {
      row.addEventListener('click', () => {
        if (row.dataset.id) openStudentDetail(row.dataset.id);
      });
    });
  }

  function openStudentDetail(studentId) {
    const s = currentStudents.find(x => x.id === studentId);
    if (!s) return;

    const initials = s.name.split(' ').map(n => n[0]).slice(0, 2).join('');

    modalDetail.innerHTML = `
      <div class="modal-header">
        <span class="student-avatar" style="width:48px;height:48px;font-size:18px;">${escapeHtml(initials)}</span>
        <div>
          <h2>${escapeHtml(s.name)}</h2>
          <p>${escapeHtml(s.id)} &bull; ${escapeHtml(s.class)} &bull; Overall Attendance: <strong>${s.attendance}%</strong></p>
        </div>
      </div>

      <div class="notice-box">
        <span>ℹ️</span>
        <div>
          <strong>Class Teacher Viewing Permission:</strong> You have read-only access to academic marks across all enrolled subjects. Marks can only be entered or modified by authorized Subject Teachers.
        </div>
      </div>

      <h3 style="font-size:14px;font-weight:800;margin:16px 0 8px;">Academic Record Across Subjects</h3>
      <table class="subject-marks-table">
        <thead>
          <tr>
            <th>SUBJECT</th>
            <th>FACULTY</th>
            <th>LATEST SCORE</th>
            <th>ATTENDANCE</th>
          </tr>
        </thead>
        <tbody>
          ${(s.subjects || []).map(sub => `
            <tr>
              <td><b>${escapeHtml(sub.name)}</b></td>
              <td>${escapeHtml(sub.teacher || 'Assigned Faculty')}</td>
              <td><strong>${escapeHtml(sub.marks)}</strong></td>
              <td>${escapeHtml(sub.attendance)}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>

      <div class="followup-box">
        <label for="mentoringNote">Class Teacher Mentoring & Follow-up Note</label>
        <textarea id="mentoringNote" rows="3" placeholder="Enter academic counseling, mentoring notes, or parent communication records for this student...">${escapeHtml(s.note || '')}</textarea>
        <button type="button" class="btn-save-note" id="saveNoteBtn">Save Follow-up Note</button>
      </div>
    `;

    studentDialog.showModal();

    const saveNoteBtn = document.getElementById('saveNoteBtn');
    if (saveNoteBtn) {
      saveNoteBtn.addEventListener('click', async () => {
        const newNote = document.getElementById('mentoringNote').value.trim();
        s.note = newNote;

        try {
          await fetch('/api/class-teacher/notes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ student_id: s.id, note: newNote })
          });
        } catch (e) {}

        render();
        saveNoteBtn.textContent = 'Saved ✓';
        setTimeout(() => { saveNoteBtn.textContent = 'Save Follow-up Note'; }, 1500);
      });
    }
  }

  // Event Listeners
  classSelect.addEventListener('change', () => loadClassStudents(classSelect.value));
  searchInput.addEventListener('input', render);
  filterSelect.addEventListener('change', render);

  const closeDialogBtn = document.getElementById('closeDialog');
  if (closeDialogBtn) closeDialogBtn.addEventListener('click', () => studentDialog.close());
  studentDialog.addEventListener('click', (e) => {
    if (e.target === studentDialog) studentDialog.close();
  });

  if (logoutBtn) {
    logoutBtn.addEventListener('click', async (e) => {
      if (e) e.preventDefault();
      try {
        await fetch('/api/auth/logout', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'same-origin'
        });
      } catch (err) {
        console.error('Logout error:', err);
      }
      localStorage.removeItem('udaan_session');
      sessionStorage.clear();
      window.location.replace('/login');
    });
  }

  window.addEventListener('pageshow', function (event) {
    if (event.persisted) {
      fetch('/api/auth/me', { credentials: 'same-origin' })
        .then(res => {
          if (!res.ok) window.location.replace('/login');
        })
        .catch(() => window.location.replace('/login'));
    }
  });

  function escapeHtml(str) {
    return String(str).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  }

  loadAssignedClasses();
});
