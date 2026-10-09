// UDAAN Support Line Portal Client

document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const ticketRows = document.getElementById('ticketRows');
  const searchInput = document.getElementById('searchInput');
  const statusFilter = document.getElementById('statusFilter');
  const categoryFilter = document.getElementById('categoryFilter');
  const btnNewTicket = document.getElementById('btnNewTicket');

  // KPI elements
  const totalTicketsEl = document.getElementById('totalTickets');
  const openTicketsEl = document.getElementById('openTickets');
  const inProgressTicketsEl = document.getElementById('inProgressTickets');
  const resolvedTicketsEl = document.getElementById('resolvedTickets');

  // Dialogs
  const ticketDetailDialog = document.getElementById('ticketDetailDialog');
  const ticketDetailContent = document.getElementById('ticketDetailContent');
  const newTicketDialog = document.getElementById('newTicketDialog');
  const newTicketForm = document.getElementById('newTicketForm');
  const logoutBtn = document.getElementById('logoutBtn');

  // The server session is authoritative; browser storage is not authentication.
  let currentUser = { name: 'Support Staff', role: 'support' };
  fetch('/api/auth/me', { credentials: 'same-origin' })
    .then(async res => {
      if (!res.ok) {
        window.location.replace('/login');
        return;
      }
      const data = await res.json();
      currentUser = data.user || currentUser;
      const staffNameEl = document.querySelector('.staff-name');
      if (staffNameEl) staffNameEl.textContent = currentUser.name || 'Support Staff';
      const profNameEl = document.querySelector('.staff-profile b');
      if (profNameEl) profNameEl.textContent = currentUser.name || 'Support Staff';
    })
    .catch(() => window.location.replace('/login'));

  // Demo Tickets Database
  let tickets = [
    {
      id: 'TCK-101',
      studentName: 'Aarav Reddy',
      studentId: 'CSE2401',
      category: 'academic_difficulty',
      categoryLabel: 'Academic Difficulty',
      subjectLine: 'Need extra tutoring in Linked Lists & Pointer algorithms',
      description: 'I scored 28 in the recent Unit Test. I am struggling to understand double pointer manipulation in C/Java and would like mentoring support.',
      priority: 'high',
      status: 'open',
      assignedTo: 'Alex Patel',
      createdDate: 'Today, 10:15 AM',
      replies: [
        {
          author: 'Aarav Reddy (Student)',
          role: 'student',
          time: 'Today, 10:15 AM',
          message: 'I scored 28 in the recent Unit Test. I am struggling to understand double pointer manipulation in C/Java and would like mentoring support.'
        }
      ]
    },
    {
      id: 'TCK-102',
      studentName: 'Meghana Rao',
      studentId: 'CSE2402',
      category: 'technical_issue',
      categoryLabel: 'Technical Issue',
      subjectLine: 'LeetCode streak progress sync delay',
      description: 'My DSA streak count shows 7 days on LeetCode but did not update on my student portal dashboard yesterday.',
      priority: 'medium',
      status: 'in_progress',
      assignedTo: 'Alex Patel',
      createdDate: 'Yesterday, 03:40 PM',
      replies: [
        {
          author: 'Meghana Rao (Student)',
          role: 'student',
          time: 'Yesterday, 03:40 PM',
          message: 'My DSA streak count shows 7 days on LeetCode but did not update on my student portal dashboard yesterday.'
        },
        {
          author: 'Alex Patel (Support Staff)',
          role: 'staff',
          time: 'Yesterday, 05:10 PM',
          message: 'Hello Meghana, we are currently refreshing the batch synchronization token. Please allow up to 2 hours.'
        }
      ]
    },
    {
      id: 'TCK-103',
      studentName: 'Rohit Naidu',
      studentId: 'CSE2415',
      category: 'attendance_concern',
      categoryLabel: 'Attendance Concern',
      subjectLine: 'Medical leave attendance adjustment for DSA Lab',
      description: 'I submitted my hospital medical certificate to the department office for 3 days of absence last week. Attendance still shows 68%.',
      priority: 'high',
      status: 'open',
      assignedTo: 'Unassigned',
      createdDate: 'Yesterday, 11:20 AM',
      replies: [
        {
          author: 'Rohit Naidu (Student)',
          role: 'student',
          time: 'Yesterday, 11:20 AM',
          message: 'I submitted my hospital medical certificate to the department office for 3 days of absence last week. Attendance still shows 68%.'
        }
      ]
    },
    {
      id: 'TCK-104',
      studentName: 'Saanvi Kumar',
      studentId: 'CSE2408',
      category: 'personal_support',
      categoryLabel: 'Personal Support Request',
      subjectLine: 'Request for confidential academic counseling session',
      description: 'Feeling overwhelmed preparing for upcoming semester examinations and coding interviews. Would like to speak with a student counselor.',
      priority: 'medium',
      status: 'in_progress',
      assignedTo: 'Dr. Anita (Counselor)',
      createdDate: '2 days ago',
      replies: [
        {
          author: 'Saanvi Kumar (Student)',
          role: 'student',
          time: '2 days ago',
          message: 'Feeling overwhelmed preparing for upcoming semester examinations and coding interviews. Would like to speak with a student counselor.'
        },
        {
          author: 'Dr. Anita (Counselor)',
          role: 'staff',
          time: 'Yesterday, 09:30 AM',
          message: 'Hi Saanvi, we have scheduled a peaceful 1-on-1 counseling appointment for Friday at 3:00 PM in Room 104. We are here to support you.'
        }
      ]
    },
    {
      id: 'TCK-105',
      studentName: 'Divya Sharma',
      studentId: 'CSE2422',
      category: 'other',
      categoryLabel: 'Other',
      subjectLine: 'Hostel WiFi connectivity in study rooms',
      description: 'Slow internet connection preventing access to online practice compilers in Block C.',
      priority: 'low',
      status: 'resolved',
      assignedTo: 'IT Helpdesk',
      createdDate: '3 days ago',
      replies: [
        {
          author: 'Divya Sharma (Student)',
          role: 'student',
          time: '3 days ago',
          message: 'Slow internet connection preventing access to online practice compilers in Block C.'
        },
        {
          author: 'IT Helpdesk',
          role: 'staff',
          time: '2 days ago',
          message: 'Replaced access point router in Block C 2nd floor. Speeds verified above 100 Mbps.'
        }
      ]
    }
  ];

  async function loadTickets() {
    try {
      const res = await fetch('/api/support/tickets');
      if (res.ok) {
        const data = await res.json();
        if (data && data.length > 0) {
          tickets = data;
          render();
          return;
        }
      }
    } catch (e) {
      console.error('Unable to load tickets:', e);
    }

    // Do not display fabricated sample tickets when the backend is unavailable.
    tickets = [];
    render();
  }

  function getFilteredTickets() {
    const q = searchInput.value.trim().toLowerCase();
    const stat = statusFilter.value;
    const cat = categoryFilter.value;

    return tickets.filter(t => {
      const matchesSearch = !q || t.subjectLine.toLowerCase().includes(q)
        || t.studentName.toLowerCase().includes(q)
        || t.id.toLowerCase().includes(q);

      const matchesStatus = stat === 'all' || t.status === stat;
      const matchesCategory = cat === 'all' || t.category === cat;

      return matchesSearch && matchesStatus && matchesCategory;
    });
  }

  function renderKPIs() {
    totalTicketsEl.textContent = tickets.length;
    openTicketsEl.textContent = tickets.filter(t => t.status === 'open').length;
    inProgressTicketsEl.textContent = tickets.filter(t => t.status === 'in_progress').length;
    resolvedTicketsEl.textContent = tickets.filter(t => t.status === 'resolved' || t.status === 'closed').length;
  }

  function render() {
    renderKPIs();
    const filtered = getFilteredTickets();

    if (!filtered.length) {
      ticketRows.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:32px;color:var(--muted)">No tickets match the selected filters.</td></tr>';
      return;
    }

    ticketRows.innerHTML = filtered.map(t => {
      const statusMap = {
        'open': { label: 'Open', cls: 'status-open' },
        'in_progress': { label: 'In Progress', cls: 'status-inprogress' },
        'resolved': { label: 'Resolved', cls: 'status-resolved' },
        'closed': { label: 'Closed', cls: 'status-closed' }
      };

      const priorityMap = {
        'high': { label: '🔴 Urgent', cls: 'priority-high' },
        'medium': { label: '🟡 Medium', cls: 'priority-medium' },
        'low': { label: '⚪ Low', cls: 'priority-low' }
      };

      const statInfo = statusMap[t.status] || { label: t.status, cls: '' };
      const prioInfo = priorityMap[t.priority] || { label: t.priority, cls: '' };

      return `
        <tr data-id="${t.id}">
          <td><strong>${escapeHtml(t.id)}</strong></td>
          <td>
            <b>${escapeHtml(t.studentName)}</b><br>
            <small style="color:var(--muted)">${escapeHtml(t.studentId)}</small>
          </td>
          <td>
            <span class="category-tag">${escapeHtml(t.categoryLabel)}</span>
          </td>
          <td style="max-width:240px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
            <b>${escapeHtml(t.subjectLine)}</b>
          </td>
          <td>
            <span class="priority-chip ${prioInfo.cls}">${prioInfo.label}</span>
          </td>
          <td>
            <span class="status-badge ${statInfo.cls}">${statInfo.label}</span>
          </td>
          <td>
            <button class="open-link" data-open="${t.id}" style="border:none;cursor:pointer;">View & Reply ↗</button>
          </td>
        </tr>
      `;
    }).join('');

    // Attach row open handlers
    document.querySelectorAll('[data-open]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        openTicketDetail(btn.dataset.open);
      });
    });

    document.querySelectorAll('tbody tr').forEach(row => {
      row.addEventListener('click', () => {
        if (row.dataset.id) openTicketDetail(row.dataset.id);
      });
    });
  }

  function openTicketDetail(ticketId) {
    const t = tickets.find(x => x.id === ticketId);
    if (!t) return;

    ticketDetailContent.innerHTML = `
      <div class="modal-header">
        <div>
          <span class="category-tag" style="margin-bottom:8px;">${escapeHtml(t.categoryLabel)}</span>
          <h2 style="font-size:20px;margin-top:6px;">${escapeHtml(t.subjectLine)}</h2>
          <p style="color:var(--muted);font-size:12px;">Ticket ${escapeHtml(t.id)} &bull; Submitted by <strong>${escapeHtml(t.studentName)}</strong> (${escapeHtml(t.studentId)}) &bull; ${escapeHtml(t.createdDate)}</p>
        </div>
      </div>

      <div style="padding:14px;background:#f8fafc;border-radius:12px;border:1px solid var(--line);margin-bottom:16px;">
        <p style="font-size:13px;line-height:1.6;margin:0;">${escapeHtml(t.description)}</p>
      </div>

      <h3 style="font-size:14px;font-weight:800;margin:18px 0 8px;">Support Conversation History</h3>
      <div class="thread-container" id="threadList">
        ${(t.replies || []).map(r => `
          <div class="thread-message ${r.role === 'staff' ? 'staff' : ''}">
            <div class="thread-meta">
              <strong>${escapeHtml(r.author)}</strong>
              <span>${escapeHtml(r.time)}</span>
            </div>
            <div>${escapeHtml(r.message)}</div>
          </div>
        `).join('')}
      </div>

      <div class="reply-form">
        <label for="replyText" style="font-size:12px;font-weight:700;display:block;margin-bottom:6px;">Post Support Response & Action Plan</label>
        <textarea id="replyText" rows="3" placeholder="Type instructions, guidance, or counseling feedback for the student..."></textarea>
        
        <div class="reply-actions">
          <div style="display:flex;align-items:center;gap:8px;">
            <label for="updateStatusSelect" style="font-size:12px;font-weight:700;margin:0;">Status:</label>
            <select id="updateStatusSelect" style="border:1.5px solid var(--line);border-radius:8px;padding:6px 10px;font:inherit;font-size:12px;">
              <option value="open" ${t.status === 'open' ? 'selected' : ''}>Open</option>
              <option value="in_progress" ${t.status === 'in_progress' ? 'selected' : ''}>In Progress</option>
              <option value="resolved" ${t.status === 'resolved' ? 'selected' : ''}>Resolved</option>
              <option value="closed" ${t.status === 'closed' ? 'selected' : ''}>Closed</option>
            </select>
          </div>
          <button type="button" class="btn-new-ticket" id="submitReplyBtn" style="padding:8px 16px;font-size:12px;">
            Send Response
          </button>
        </div>
      </div>
    `;

    ticketDetailDialog.showModal();

    const submitReplyBtn = document.getElementById('submitReplyBtn');
    if (submitReplyBtn) {
      submitReplyBtn.addEventListener('click', async () => {
        const replyText = document.getElementById('replyText').value.trim();
        const newStatus = document.getElementById('updateStatusSelect').value;

        if (!replyText) {
          alert('Please enter a response message before submitting.');
          return;
        }

        const replyObj = {
          author: `${currentUser.name} (Support Staff)`,
          role: 'staff',
          time: 'Just now',
          message: replyText
        };

        t.replies.push(replyObj);
        t.status = newStatus;
        t.assignedTo = currentUser.name;

        try {
          await fetch('/api/support/reply', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              ticket_id: t.id,
              message: replyText,
              status: newStatus
            })
          });
        } catch (e) {}

        render();
        openTicketDetail(t.id);
      });
    }
  }

  // Create New Ticket
  if (btnNewTicket) {
    btnNewTicket.addEventListener('click', () => {
      newTicketDialog.showModal();
    });
  }

  if (newTicketForm) {
    newTicketForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      const studentName = document.getElementById('newStudentName').value.trim();
      const studentId = document.getElementById('newStudentId').value.trim();
      const category = document.getElementById('newCategory').value;
      const priority = document.getElementById('newPriority').value;
      const subjectLine = document.getElementById('newSubjectLine').value.trim();
      const description = document.getElementById('newDescription').value.trim();

      const categoryLabels = {
        'academic_difficulty': 'Academic Difficulty',
        'technical_issue': 'Technical Issue',
        'attendance_concern': 'Attendance Concern',
        'personal_support': 'Personal Support Request',
        'other': 'Other'
      };

      const submitButton = newTicketForm.querySelector('[type="submit"]');
      if (submitButton) submitButton.disabled = true;
      try {
        const response = await fetch('/api/support/tickets', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'same-origin',
          body: JSON.stringify({
            studentId,
            category,
            priority,
            subjectLine,
            description
          })
        });
        const result = await response.json();
        if (!response.ok || !result.success) {
          throw new Error(result.error || result.message || 'Unable to create ticket.');
        }
        newTicketForm.reset();
        newTicketDialog.close();
        await loadTickets();
        openTicketDetail(result.ticket_id);
      } catch (err) {
        alert(err.message || 'Unable to create ticket. Please try again.');
      } finally {
        if (submitButton) submitButton.disabled = false;
      }
    });
  }

  // Close modals
  document.querySelectorAll('.modal-close').forEach(btn => {
    btn.addEventListener('click', () => {
      ticketDetailDialog.close();
      newTicketDialog.close();
    });
  });

  ticketDetailDialog.addEventListener('click', e => {
    if (e.target === ticketDetailDialog) ticketDetailDialog.close();
  });
  newTicketDialog.addEventListener('click', e => {
    if (e.target === newTicketDialog) newTicketDialog.close();
  });

  // Filter events
  searchInput.addEventListener('input', render);
  statusFilter.addEventListener('change', render);
  categoryFilter.addEventListener('change', render);

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

  loadTickets();
});
