// UDAAN Subject Teacher Portal Client

document.addEventListener('DOMContentLoaded', () => {
  // Demo Teacher Assignments Hierarchy
  const teacherAssignments = {
    'CSE-A': [
      { id: 'DSA', name: 'Data Structures & Algorithms' },
      { id: 'CN', name: 'Computer Networks' }
    ],
    'CSE-B': [
      { id: 'DSA', name: 'Data Structures & Algorithms' }
    ],
    'ECE-A': [
      { id: 'CN', name: 'Computer Networks' }
    ]
  };

  // Student database partitioned by Class and Subject
  let studentDatabase = {
    'CSE-A': {
      'DSA': [
        {
          id: 'CSE2401', name: 'Aarav Reddy', class: 'CSE-A', marks: 28, max: 100,
          attendance: 62, attended: 13, classes: 21,
          trend: [51, 39, 28], // Decreasing: 51 -> 39 -> 28
          topics: [['Arrays', 35], ['Linked Lists', 42], ['Stacks & Queues', 30]],
          assessments: [['Quiz 1', 51, 100], ['Mid-Term 1', 39, 100], ['Unit Test 2', 28, 100]],
          note: 'Needs help with core concepts. Consider a short one-to-one revision session.',
          phone: '9876501201'
        },
        {
          id: 'CSE2415', name: 'Rohit Naidu', class: 'CSE-A', marks: 39, max: 100,
          attendance: 68, attended: 15, classes: 22,
          trend: [55, 48, 39], // Decreasing: 55 -> 48 -> 39
          topics: [['Arrays', 55], ['Linked Lists', 40], ['Stacks & Queues', 47]],
          assessments: [['Quiz 1', 55, 100], ['Mid-Term 1', 48, 100], ['Unit Test 2', 39, 100]],
          note: 'Marks are low and attendance needs follow-up.',
          phone: '9876501215'
        },
        {
          id: 'CSE2403', name: 'Ishaan Varma', class: 'CSE-A', marks: 48, max: 100,
          attendance: 82, attended: 18, classes: 22,
          trend: [43, 52, 48], // Not 3-consecutive decrease
          topics: [['Arrays', 60], ['Linked Lists', 55], ['Stacks & Queues', 58]],
          assessments: [['Quiz 1', 43, 100], ['Mid-Term 1', 52, 100], ['Unit Test 2', 48, 100]],
          note: 'Making progress. Encourage regular problem-solving practice.',
          phone: '9876501203'
        },
        {
          id: 'CSE2417', name: 'Karthik Dev', class: 'CSE-A', marks: 56, max: 100,
          attendance: 79, attended: 19, classes: 24,
          trend: [64, 60, 56], // Decreasing: 64 -> 60 -> 56
          topics: [['Arrays', 68], ['Linked Lists', 60], ['Stacks & Queues', 62]],
          assessments: [['Quiz 1', 64, 100], ['Mid-Term 1', 60, 100], ['Unit Test 2', 56, 100]],
          note: 'Can improve with more practice on linked lists.',
          phone: '9876501217'
        },
        {
          id: 'CSE2405', name: 'Vikram Singh', class: 'CSE-A', marks: 72, max: 100,
          attendance: 91, attended: 21, classes: 23,
          trend: [68, 70, 72],
          topics: [['Arrays', 82], ['Linked Lists', 72], ['Stacks & Queues', 78]],
          assessments: [['Quiz 1', 68, 100], ['Mid-Term 1', 70, 100], ['Unit Test 2', 72, 100]],
          note: 'Performing well. Offer extension problems for deeper learning.',
          phone: '9876501205'
        },
        {
          id: 'CSE2419', name: 'Aditya Paul', class: 'CSE-A', marks: 88, max: 100,
          attendance: 96, attended: 23, classes: 24,
          trend: [82, 85, 88],
          topics: [['Arrays', 92], ['Linked Lists', 88], ['Stacks & Queues', 90]],
          assessments: [['Quiz 1', 82, 100], ['Mid-Term 1', 85, 100], ['Unit Test 2', 88, 100]],
          note: 'Excellent progress. Peer mentor candidate.',
          phone: '9876501219'
        }
      ],
      'CN': [
        {
          id: 'CSE2401', name: 'Aarav Reddy', class: 'CSE-A', marks: 61, max: 100,
          attendance: 78, attended: 14, classes: 18,
          trend: [58, 60, 61],
          topics: [['Network Models', 65], ['Data Link Layer', 60], ['Routing', 55]],
          assessments: [['Quiz 1', 58, 100], ['Mid-Term 1', 60, 100], ['Unit Test 2', 61, 100]],
          note: 'Good conceptual grasp in networks.',
          phone: '9876501201'
        },
        {
          id: 'CSE2403', name: 'Ishaan Varma', class: 'CSE-A', marks: 75, max: 100,
          attendance: 85, attended: 17, classes: 20,
          trend: [70, 72, 75],
          topics: [['Network Models', 80], ['Data Link Layer', 75], ['Routing', 70]],
          assessments: [['Quiz 1', 70, 100], ['Mid-Term 1', 72, 100], ['Unit Test 2', 75, 100]],
          note: 'Attentive and active in lab experiments.',
          phone: '9876501203'
        }
      ]
    },
    'CSE-B': {
      'DSA': [
        {
          id: 'CSE2408', name: 'Saanvi Kumar', class: 'CSE-B', marks: 34, max: 100,
          attendance: 71, attended: 15, classes: 21,
          trend: [58, 46, 34], // Decreasing
          topics: [['Arrays', 45], ['Linked Lists', 38], ['Stacks & Queues', 52]],
          assessments: [['Quiz 1', 58, 100], ['Mid-Term 1', 46, 100], ['Unit Test 2', 34, 100]],
          note: 'Review linked-list fundamentals.',
          phone: '9876501208'
        },
        {
          id: 'CSE2410', name: 'Nitya Rao', class: 'CSE-B', marks: 52, max: 100,
          attendance: 85, attended: 18, classes: 21,
          trend: [48, 51, 52],
          topics: [['Arrays', 65], ['Linked Lists', 60], ['Stacks & Queues', 58]],
          assessments: [['Quiz 1', 48, 100], ['Mid-Term 1', 51, 100], ['Unit Test 2', 52, 100]],
          note: 'Steady progress.',
          phone: '9876501210'
        },
        {
          id: 'CSE2412', name: 'Mira Joshi', class: 'CSE-B', marks: 81, max: 100,
          attendance: 94, attended: 20, classes: 21,
          trend: [76, 79, 81],
          topics: [['Arrays', 90], ['Linked Lists', 82], ['Stacks & Queues', 85]],
          assessments: [['Quiz 1', 76, 100], ['Mid-Term 1', 79, 100], ['Unit Test 2', 81, 100]],
          note: 'Strong understanding across current topics.',
          phone: '9876501212'
        }
      ]
    },
    'ECE-A': {
      'CN': [
        {
          id: 'ECE2401', name: 'Tarun Verma', class: 'ECE-A', marks: 55, max: 100,
          attendance: 80, attended: 16, classes: 20,
          trend: [65, 60, 55], // Decreasing
          topics: [['Network Models', 60], ['Data Link Layer', 55], ['Routing', 50]],
          assessments: [['Quiz 1', 65, 100], ['Mid-Term 1', 60, 100], ['Unit Test 2', 55, 100]],
          note: 'Requires practice on subnetting calculations.',
          phone: '9876501250'
        }
      ]
    }
  };

  // DOM Elements
  const classSelect = document.getElementById('classSelect');
  const subjectSelect = document.getElementById('subjectSelect');
  const subjectTitleEl = document.getElementById('subjectTitle');
  const searchInput = document.getElementById('searchInput');
  const statusFilter = document.getElementById('statusFilter');
  const rows = document.getElementById('studentRows');
  const dialog = document.getElementById('studentDialog');
  const studentDetail = document.getElementById('studentDetail');
  const logoutBtn = document.getElementById('logoutBtn');

  // KPI elements
  const totalCountEl = document.getElementById('totalCount');
  const lowCountEl = document.getElementById('lowCount');
  const averageCountEl = document.getElementById('averageCount');
  const goodCountEl = document.getElementById('goodCount');

  // Check auth session
  const sessionData = localStorage.getItem('udaan_session');
  if (sessionData) {
    try {
      const user = JSON.parse(sessionData);
      if (user.name) {
        const topH1 = document.querySelector('.topbar h1 span');
        if (topH1) topH1.textContent = user.name;
        const profB = document.querySelector('.teacher-profile b');
        if (profB) profB.textContent = user.name;
      }
    } catch (e) {}
  }

  // Performance classification: <40 Low, <70 Average, >=70 Good
  const band = s => s.marks < 40 ? 'low' : s.marks < 70 ? 'average' : 'good';
  const label = s => ({ low: 'Needs support', average: 'Making progress', good: 'Doing well' }[band(s)]);

  // Chronological 3-consecutive decrease early-warning rule:
  // Strictly decreasing across 3 consecutive valid assessment scores in chronological order.
  // Missing assessment scores are ignored, NOT treated as 0.
  function hasEarlyWarning(s) {
    if (!s || !Array.isArray(s.assessments) || s.assessments.length < 3) return false;
    // Extract non-null scores
    const validScores = s.assessments
      .map(a => typeof a[1] === 'number' ? a[1] : parseFloat(a[1]))
      .filter(score => !isNaN(score) && score !== null);

    if (validScores.length < 3) return false;

    // Check last 3 consecutive assessments in order
    const n = validScores.length;
    return validScores[n - 3] > validScores[n - 2] && validScores[n - 2] > validScores[n - 1];
  }

  function getEarlyWarningTrend(s) {
    if (!s || !Array.isArray(s.assessments)) return '';
    const validScores = s.assessments
      .map(a => typeof a[1] === 'number' ? a[1] : parseFloat(a[1]))
      .filter(score => !isNaN(score) && score !== null);
    if (validScores.length < 3) return '';
    const n = validScores.length;
    return `${validScores[n - 3]} → ${validScores[n - 2]} → ${validScores[n - 1]}`;
  }

  function esc(s) {
    return String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  }

  // Initialize Class Selector
  async function initClasses() {
    try {
      const res = await fetch('/api/subject-teacher/classes');
      if (res.ok) {
        const serverClasses = await res.json();
        if (serverClasses && serverClasses.length > 0) {
          classSelect.innerHTML = serverClasses.map(c => `<option value="${c.code}">${c.name || c.code}</option>`).join('');
          loadSubjectsForClass(serverClasses[0].code);
          return;
        }
      }
    } catch (e) {}

    // Fallback demo classes assigned to this teacher
    const classes = Object.keys(teacherAssignments);
    classSelect.innerHTML = classes.map(c => `<option value="${c}">${c === 'CSE-A' ? 'B.Tech CSE · 2nd Year · Section A' : c === 'CSE-B' ? 'B.Tech CSE · 2nd Year · Section B' : 'B.Tech ECE · 2nd Year · Section A'}</option>`).join('');
    loadSubjectsForClass(classes[0]);
  }

  // Load authorized subjects when class changes
  async function loadSubjectsForClass(classCode) {
    const subjects = teacherAssignments[classCode] || [];

    if (!subjects.length) {
      subjectSelect.innerHTML = '<option value="">No authorized subjects</option>';
      subjectTitleEl.textContent = 'No Subjects Assigned';
      renderEmpty('You do not have any authorized subjects assigned in this class.');
      return;
    }

    subjectSelect.innerHTML = subjects.map(s => `<option value="${s.id}">${escapeHtml(s.name)}</option>`).join('');
    subjectSelect.selectedIndex = 0;
    updateSelectedSubject();
  }

  function updateSelectedSubject() {
    const classCode = classSelect.value;
    const subjectId = subjectSelect.value;
    const subjects = teacherAssignments[classCode] || [];
    const subj = subjects.find(s => s.id === subjectId);

    if (subj) {
      subjectTitleEl.textContent = subj.name;
    }

    render();
  }

  function getCurrentStudents() {
    const classCode = classSelect.value;
    const subjectId = subjectSelect.value;
    if (!classCode || !subjectId) return [];

    const classData = studentDatabase[classCode];
    if (!classData) return [];

    return classData[subjectId] || [];
  }

  function getVisibleStudents() {
    const students = getCurrentStudents();
    const q = searchInput.value.trim().toLowerCase();
    const status = statusFilter.value;

    return students.filter(s => {
      const matchesSearch = !q || s.name.toLowerCase().includes(q) || s.id.toLowerCase().includes(q);
      const isWarn = hasEarlyWarning(s);
      const matchesStatus = status === 'all'
        || (status === 'warning' ? isWarn : band(s) === status);

      return matchesSearch && matchesStatus;
    }).sort((a, b) => {
      // Priority sorting: Early warning first, then Low band, then lowest marks
      return (Number(hasEarlyWarning(b)) - Number(hasEarlyWarning(a)))
        || ({ low: 0, average: 1, good: 2 }[band(a)] - { low: 0, average: 1, good: 2 }[band(b)])
        || (a.marks - b.marks)
        || a.name.localeCompare(b.name);
    });
  }

  function renderKPIs(students) {
    totalCountEl.textContent = students.length;
    lowCountEl.textContent = students.filter(s => band(s) === 'low' || hasEarlyWarning(s)).length;
    averageCountEl.textContent = students.filter(s => band(s) === 'average').length;
    goodCountEl.textContent = students.filter(s => band(s) === 'good').length;
  }

  function renderEmpty(message) {
    totalCountEl.textContent = '0';
    lowCountEl.textContent = '0';
    averageCountEl.textContent = '0';
    goodCountEl.textContent = '0';
    rows.innerHTML = `<tr><td colspan="6" class="empty-row">${esc(message)}</td></tr>`;
  }

  function render() {
    const allStudents = getCurrentStudents();
    if (!allStudents.length) {
      renderEmpty('No student records found for this class and subject combination.');
      return;
    }

    renderKPIs(allStudents);
    const visible = getVisibleStudents();

    if (!visible.length) {
      rows.innerHTML = '<tr><td colspan="6" class="empty-row">No students match these search and status filters.</td></tr>';
      return;
    }

    rows.innerHTML = visible.map(s => {
      const isWarning = hasEarlyWarning(s);
      const initials = s.name.split(' ').map(n => n[0]).slice(0, 2).join('');
      const topicPct = s.topics && s.topics.length
        ? Math.round(s.topics.reduce((acc, t) => acc + t[1], 0) / s.topics.length)
        : 0;

      return `
        <tr class="status-${band(s)}" data-id="${s.id}" tabindex="0" aria-label="View ${esc(s.name)} details">
          <td data-label="STUDENT">
            <div class="student-cell">
              <span class="student-avatar">${esc(initials)}</span>
              <span>
                <b class="student-name">${esc(s.name)}</b>
                <small class="student-id">
                  ${esc(s.id)}
                  ${isWarning ? '<span class="warning-text"> · ⚠ Early Warning</span>' : ''}
                </small>
              </span>
            </div>
          </td>
          <td data-label="CLASS">${esc(s.class)}</td>
          <td data-label="LAST MARKS">
            <span class="mark">${s.marks}<small> / ${s.max}</small></span>
          </td>
          <td data-label="SUBJECT ATTENDANCE">
            <span class="attendance ${s.attendance < 75 ? 'low-attendance' : ''}">
              <span class="attendance-track"><span style="width:${s.attendance}%"></span></span>
              <em>${s.attendance}%</em>
            </span>
          </td>
          <td data-label="STATUS">
            <span class="status-pill ${band(s)}">${label(s)}</span>
            ${isWarning ? '<small class="warning-chip">3-Assessment Decline</small>' : ''}
          </td>
          <td data-label="DETAILS">
            <button class="open-link" data-open="${s.id}">View details ↗</button>
          </td>
        </tr>
      `;
    }).join('');
  }

  function showDetail(id) {
    const students = getCurrentStudents();
    const s = students.find(x => x.id === id);
    if (!s) return;

    const cls = band(s);
    const isWarning = hasEarlyWarning(s);
    const initials = s.name.split(' ').map(n => n[0]).slice(0, 2).join('');
    const trendStr = getEarlyWarningTrend(s);
    const subjectName = subjectTitleEl.textContent;

    studentDetail.innerHTML = `
      <div class="detail-head">
        <span class="detail-avatar">${esc(initials)}</span>
        <div>
          <h2>${esc(s.name)}</h2>
          <p>${esc(s.id)} · ${esc(s.class)} · ${esc(subjectName)}</p>
        </div>
      </div>

      <div class="detail-band">
        <div>
          <small>Latest assessment score</small>
          <strong style="color:var(--${cls === 'low' ? 'red' : cls === 'average' ? 'yellow' : 'green'})">
            ${s.marks} / ${s.max}
          </strong>
        </div>
        <span class="status-pill ${cls}">${label(s)}</span>
      </div>

      <div class="detail-grid">
        <div class="detail-metric">
          <small>Subject attendance</small>
          <b>${s.attendance}% (${s.attended}/${s.classes} classes)</b>
        </div>
        <div class="detail-metric">
          <small>Topics covered</small>
          <b>${s.topics ? s.topics.length : 0} topics</b>
        </div>
        <div class="detail-metric">
          <small>Assessments recorded</small>
          <b>${s.assessments ? s.assessments.length : 0} tests</b>
        </div>
      </div>

      ${isWarning ? `
        <div class="early-warning-box">
          <b>⚠ Early Warning · Continuous Score Drop Detected</b>
          <p>
            This student's scores have decreased across three consecutive assessments in this subject (<strong>${esc(trendStr)}</strong>).
            Intervention recommended: Review recent difficult topics with the student and provide guided problem practice.
          </p>
        </div>
      ` : ''}

      <h3 class="detail-section-title">Assessment History (Chronological)</h3>
      ${(s.assessments || []).map(a => `
        <div class="assessment-row">
          <span>${esc(a[0])}</span>
          <b>${a[1]} / ${a[2] || 100}</b>
        </div>
      `).join('')}

      <h3 class="detail-section-title">Topic Completion Progress</h3>
      ${(s.topics || []).map(t => `
        <div class="topic-row">
          <span>${esc(t[0])}</span>
          <span style="font-weight:700;color:var(--primary)">${t[1]}%</span>
        </div>
      `).join('')}

      <h3 class="detail-section-title">Faculty Follow-up Notes</h3>
      <p class="detail-note">${esc(s.note || 'No notes entered yet.')}</p>

      <!-- Edit Marks & Attendance Form -->
      <div class="edit-form">
        <h4 style="font-size:13px;font-weight:800;margin-bottom:12px;color:var(--primary);">
          ✏️ Enter / Update Marks & Attendance
        </h4>
        <div class="form-row">
          <div class="form-group">
            <label for="updateAssessment">Select Assessment</label>
            <select id="updateAssessment">
              ${(s.assessments || []).map((a, i) => `<option value="${i}">${esc(a[0])}</option>`).join('')}
              <option value="new">+ Add New Unit Test</option>
            </select>
          </div>
          <div class="form-group">
            <label for="updateMarks">Marks Obtained (out of 100)</label>
            <input type="number" id="updateMarks" min="0" max="100" value="${s.marks}">
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label for="updateAttended">Classes Attended</label>
            <input type="number" id="updateAttended" min="0" value="${s.attended}">
          </div>
          <div class="form-group">
            <label for="updateTotalClasses">Total Classes Held</label>
            <input type="number" id="updateTotalClasses" min="1" value="${s.classes}">
          </div>
        </div>
        <button type="button" class="action-btn primary" id="saveMarksBtn" style="margin-top:6px;">
          Save Marks & Attendance to Database
        </button>
        <span id="saveStatus" style="font-size:11px;margin-left:10px;font-weight:700;color:var(--green);"></span>
      </div>

      <div class="detail-actions">
        <a class="action-btn" href="tel:${s.phone}">Contact Student</a>
        <button class="action-btn" id="copyStudent">Copy Student ID</button>
      </div>
      <p class="detail-note">Institutional Phone: ${esc(s.phone)} · Contact info is restricted to authorized faculty members.</p>
    `;

    dialog.showModal();

    // Copy Student ID button handler
    const copyBtn = document.getElementById('copyStudent');
    if (copyBtn) {
      copyBtn.addEventListener('click', () => {
        navigator.clipboard?.writeText(s.id);
        copyBtn.textContent = 'Copied: ' + s.id;
        setTimeout(() => { copyBtn.textContent = 'Copy Student ID'; }, 1500);
      });
    }

    // Save Marks and Attendance handler
    const saveMarksBtn = document.getElementById('saveMarksBtn');
    if (saveMarksBtn) {
      saveMarksBtn.addEventListener('click', async () => {
        const marksVal = parseInt(document.getElementById('updateMarks').value, 10);
        const attendedVal = parseInt(document.getElementById('updateAttended').value, 10);
        const totalClassesVal = parseInt(document.getElementById('updateTotalClasses').value, 10);
        const assessIdx = document.getElementById('updateAssessment').value;
        const statusSpan = document.getElementById('saveStatus');

        if (isNaN(marksVal) || marksVal < 0 || marksVal > 100) {
          alert('Please enter a valid mark score between 0 and 100.');
          return;
        }
        if (isNaN(attendedVal) || isNaN(totalClassesVal) || attendedVal < 0 || totalClassesVal <= 0 || attendedVal > totalClassesVal) {
          alert('Please enter valid attendance figures (attended classes cannot exceed total classes).');
          return;
        }

        saveMarksBtn.disabled = true;
        saveMarksBtn.textContent = 'Saving...';

        // Update local object
        s.marks = marksVal;
        s.attended = attendedVal;
        s.classes = totalClassesVal;
        s.attendance = Math.round((attendedVal / totalClassesVal) * 100);

        if (assessIdx === 'new') {
          s.assessments.push([`Unit Test ${s.assessments.length + 1}`, marksVal, 100]);
          s.trend.push(marksVal);
        } else {
          s.assessments[parseInt(assessIdx, 10)][1] = marksVal;
          s.trend[parseInt(assessIdx, 10)] = marksVal;
        }

        // Try saving to backend API
        try {
          await fetch('/api/subject-teacher/marks', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              student_id: s.id,
              class_code: classSelect.value,
              subject_id: subjectSelect.value,
              marks: marksVal,
              attended: attendedVal,
              total_classes: totalClassesVal
            })
          });
        } catch (err) {}

        render();
        saveMarksBtn.disabled = false;
        saveMarksBtn.textContent = 'Save Marks & Attendance to Database';
        statusSpan.textContent = '✓ Saved successfully!';
        setTimeout(() => { showDetail(s.id); }, 700);
      });
    }
  }

  // Row and Dialog click events
  rows.addEventListener('click', e => {
    const row = e.target.closest('tr[data-id]');
    if (row) showDetail(row.dataset.id);
  });

  const closeDialogBtn = document.getElementById('closeDialog');
  if (closeDialogBtn) closeDialogBtn.addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', e => {
    if (e.target === dialog) dialog.close();
  });

  // Selectors and Filter change events
  classSelect.addEventListener('change', () => loadSubjectsForClass(classSelect.value));
  subjectSelect.addEventListener('change', updateSelectedSubject);
  searchInput.addEventListener('input', render);
  statusFilter.addEventListener('change', render);

  // Logout handler
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

  initClasses();
});
