// UDAAN Student Portal Client

let subjects = [
  {name:"Java Programming", icon:"♨", color:"#fff0e8", ink:"#dc783d", marks:78, total:100, grade:"B+", attendance:85, attended:17, classes:20, topics:[["Introduction to Java",100],["OOP Concepts",85],["Inheritance & Polymorphism",60],["Exception Handling",0],["File Handling",0]]},
  {name:"Data Structures & Algorithms", icon:"⌘", color:"#e7f2ff", ink:"#3e87e7", marks:65, total:100, grade:"B", attendance:80, attended:16, classes:20, topics:[["Arrays",90],["Linked Lists",55],["Stacks & Queues",35],["Trees",20],["Graphs",0]]},
  {name:"Mathematics", icon:"▦", color:"#fff2d9", ink:"#c88817", marks:72, total:100, grade:"A-", attendance:90, attended:18, classes:20, topics:[["Matrices",100],["Differentiation",75],["Integration",55],["Probability",20]]},
  {name:"Computer Networks", icon:"⌘", color:"#eeeaff", ink:"#6d61d9", marks:68, total:100, grade:"B", attendance:75, attended:15, classes:20, topics:[["Network Models",90],["Data Link Layer",60],["Routing",40],["Security",10]]}
];

let notes = [
  {subject:"Java Programming", text:"Why do we use super() in Java?", date:"Today"},
  {subject:"Data Structures & Algorithms", text:"Revise the difference between stack and queue.", date:"Yesterday"}
];

let activity = [
  {icon:"J", cls:"java-icon", title:"Java Programming", desc:"Reviewed inheritance notes", time:"Today"},
  {icon:"⌘", cls:"dsa-icon", title:"DSA Practice", desc:"Solved a two-sum problem", time:"Today"},
  {icon:"▤", cls:"note-icon", title:"Study session", desc:"Focus session completed", time:"Yesterday"}
];

const $ = (id) => document.getElementById(id);
const subjectsGrid = $("subjectsGrid");
const noteSubject = $("noteSubject");
let selectedSubject = subjects[0].name;
let timerMinutes = 25;
let remainingSeconds = timerMinutes * 60;
let timerInterval = null;
let timerRunning = false;

// Check user session
function checkAuth() {
  const sessionData = localStorage.getItem('udaan_session');
  if (sessionData) {
    try {
      const user = JSON.parse(sessionData);
      if (user.name) {
        const nameEl = document.querySelector('.topbar h1 .name');
        if (nameEl) nameEl.textContent = user.name;
        const profileEl = document.querySelector('#profileBtn span:nth-child(2)');
        if (profileEl) profileEl.textContent = user.name;
        const avatarEl = document.querySelector('#profileBtn .avatar');
        if (avatarEl) avatarEl.textContent = user.name[0].toUpperCase();
      }
    } catch (e) {}
  }
}

async function loadStudentData() {
  try {
    const res = await fetch('/api/student/dashboard');
    if (res.ok) {
      const data = await res.json();
      if (data.student_name) {
        const nameEl = document.querySelector('.topbar h1 .name');
        if (nameEl) nameEl.textContent = data.student_name;
      }
      if (data.subjects && data.subjects.length > 0) {
        subjects = data.subjects;
      }
      if (data.notes) {
        notes = data.notes;
      }
      if (data.stats) {
        if (data.stats.streak) {
          const streakEl = document.querySelector('.streak-card h2');
          if (streakEl) streakEl.innerHTML = `${data.stats.streak} days <span class="tiny-tag">🔥</span>`;
        }
        if (data.stats.attendance_pct !== undefined) {
          const attEl = document.querySelector('.attendance-card h2');
          if (attEl) attEl.textContent = `${data.stats.attendance_pct}%`;
          const attSub = document.querySelector('.attendance-card .muted');
          if (attSub) attSub.textContent = `${data.stats.attended_classes} of ${data.stats.total_classes} classes attended`;
          const attBar = document.querySelector('.attendance-card .progress span');
          if (attBar) attBar.style.width = `${data.stats.attendance_pct}%`;
        }
      }
      renderSubjects();
    }
  } catch (e) {
    // Backend offline / static mode: fallback data already in place
  }
}

function renderSubjects() {
  if (!subjectsGrid) return;
  subjectsGrid.innerHTML = subjects.map((s, i) => `
    <article class="subject-card">
      <div class="subject-top">
        <span class="subject-emoji" style="background:${s.color || '#f5f3ff'};color:${s.ink || '#7c3aed'}">${s.icon || '▤'}</span>
        <span class="grade ${s.grade === 'B' ? 'gold' : ''}">${s.grade || 'A'}</span>
      </div>
      <h3>${escapeHtml(s.name)}</h3>
      <p class="semester">Semester 3</p>
      <div class="subject-metric">
        <span>Latest marks</span>
        <span class="subject-value">${s.marks}<span style="font-size:10px;font-weight:500;color:#64748b"> / ${s.total || 100}</span></span>
      </div>
      <div class="subject-metric">
        <span>Attendance</span>
        <span class="subject-value">${s.attendance}% <span style="font-size:10px;font-weight:500;color:#64748b">(${s.attended || 0}/${s.classes || 0})</span></span>
      </div>
      <div class="progress"><span style="width:${s.attendance}%"></span></div>
      <button class="notes-btn" data-subject="${i}">▤ &nbsp; Notes & Doubts &nbsp; ›</button>
      <button class="text-btn subject-open" data-open="${i}" style="margin-top:11px;width:100%">View subject details →</button>
    </article>`).join("");

  if (noteSubject) {
    noteSubject.innerHTML = subjects.map(s => `<option value="${escapeHtml(s.name)}">${escapeHtml(s.name)}</option>`).join("");
  }

  document.querySelectorAll("[data-subject]").forEach(b => b.addEventListener("click", () => openSubject(Number(b.dataset.subject), true)));
  document.querySelectorAll("[data-open]").forEach(b => b.addEventListener("click", () => openSubject(Number(b.dataset.open), false)));
}

function addActivity(title, desc) {
  activity.unshift({ icon: "✦", cls: "note-icon", title, desc, time: "Just now" });
  activity = activity.slice(0, 6);
  renderActivity();
}

function renderActivity() {
  const list = $("activityList");
  if (!list) return;
  list.innerHTML = activity.length
    ? activity.slice(0, 3).map(a => `
      <div class="activity-item">
        <span class="activity-icon ${a.cls}">${a.icon}</span>
        <div><b>${escapeHtml(a.title)}</b><small>${escapeHtml(a.desc)}</small></div>
        <time>${a.time}</time>
      </div>`).join("")
    : `<div class="empty-state">No recent activity yet. Start with one small task!</div>`;
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function openSubject(index, showNotes) {
  const s = subjects[index];
  if (!s) return;
  selectedSubject = s.name;
  $("subjectTitle").textContent = s.name;
  $("subjectStats").innerHTML = `
    <div class="detail-stat"><small>Latest marks</small><b>${s.marks}/${s.total || 100}</b></div>
    <div class="detail-stat"><small>Attendance</small><b>${s.attendance}%</b></div>
    <div class="detail-stat"><small>Grade</small><b>${s.grade || 'A'}</b></div>`;

  const topics = s.topics || [];
  $("topicList").innerHTML = topics.map(([name, p]) => `
    <div class="topic-row">
      <span>${escapeHtml(name)}</span>
      <div class="progress"><span style="width:${p}%;background:${p < 40 ? "#eab64d" : ""}"></span></div>
      <small>${p}%</small>
    </div>`).join("");

  renderSubjectNotes(s.name);
  $("subjectDialog").showModal();
  if (showNotes) setTimeout(() => $("subjectNotes").scrollIntoView({ behavior: "smooth", block: "nearest" }), 80);
}

function renderSubjectNotes(name) {
  const list = notes.filter(n => n.subject === name);
  $("subjectNotes").innerHTML = list.length
    ? list.map(n => `<div class="saved-note">${escapeHtml(n.text)}<small>${escapeHtml(n.date || 'Saved')} · ${escapeHtml(n.subject)}</small></div>`).join("")
    : `<div class="empty-state">No notes yet for this subject. Save your first doubt.</div>`;
}

function openNote(subject = selectedSubject) {
  if ($("noteSubject")) $("noteSubject").value = subject;
  if ($("noteText")) $("noteText").value = "";
  $("noteDialog").showModal();
}

function showMessage(title, message, extra = "") {
  $("simpleTitle").textContent = title;
  $("simpleMessage").textContent = message;
  $("simpleExtra").innerHTML = extra;
  $("simpleDialog").showModal();
}

function formatTime(seconds) {
  const m = Math.floor(seconds / 60).toString().padStart(2, "0");
  const s = (seconds % 60).toString().padStart(2, "0");
  return `${m}:${s}`;
}

function updateTimer() {
  if ($("timerDisplay")) $("timerDisplay").textContent = formatTime(remainingSeconds);
}

function stopTimer() {
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
  timerRunning = false;
}

function selectTimerMode(minutes) {
  stopTimer();
  timerMinutes = minutes;
  remainingSeconds = minutes * 60;
  updateTimer();
  document.querySelectorAll(".mode").forEach(b => b.classList.toggle("active", Number(b.dataset.minutes) === minutes));
  $("timerStart").textContent = minutes === 25 ? "Start focus" : "Start break";
  $("timerStatus").textContent = "Ready when you are.";
}

function startTimer() {
  if (timerRunning) {
    stopTimer();
    $("timerStart").textContent = "Resume";
    $("timerStatus").textContent = "Paused. Take a breath.";
    return;
  }
  if (remainingSeconds <= 0) remainingSeconds = timerMinutes * 60;
  timerRunning = true;
  $("timerStart").textContent = "Pause";
  $("timerStatus").textContent = "You're in focus mode. One task at a time.";
  timerInterval = setInterval(() => {
    remainingSeconds--;
    updateTimer();
    if (remainingSeconds <= 0) {
      stopTimer();
      $("timerStart").textContent = "Start again";
      $("timerStatus").textContent = "Session complete. Well done!";
      addActivity("Focus session", "Completed a " + timerMinutes + " minute session");
      if ("Notification" in window && Notification.permission === "granted") {
        new Notification("UDAAN Focus Timer", { body: "Your session is complete. Take a short break!" });
      }
      showMessage("Session complete! 🎉", "You showed up and did the work. Take a short break, then decide your next small step.");
    }
  }, 1000);
}

function openTimer() {
  updateTimer();
  $("timerDialog").showModal();
}

async function handleLogout(e) {
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

function init() {
  checkAuth();
  renderSubjects();
  renderActivity();
  updateTimer();
  loadStudentData();

  if ($("openTimer")) $("openTimer").addEventListener("click", openTimer);
  if ($("startGoal")) $("startGoal").addEventListener("click", () => { selectTimerMode(25); openTimer(); });
  if ($("timerStart")) $("timerStart").addEventListener("click", startTimer);
  if ($("timerReset")) $("timerReset").addEventListener("click", () => {
    stopTimer();
    remainingSeconds = timerMinutes * 60;
    updateTimer();
    $("timerStart").textContent = timerMinutes === 25 ? "Start focus" : "Start break";
    $("timerStatus").textContent = "Timer reset. Ready when you are.";
  });

  document.querySelectorAll(".mode").forEach(b => b.addEventListener("click", () => selectTimerMode(Number(b.dataset.minutes))));
  if ($("subjectAddNote")) $("subjectAddNote").addEventListener("click", () => openNote(selectedSubject));
  if ($("addNote")) $("addNote").addEventListener("click", () => openNote());

  if ($("saveNote")) {
    $("saveNote").addEventListener("click", async (e) => {
      e.preventDefault();
      const text = $("noteText").value.trim();
      const subject = $("noteSubject").value;
      if (!text) {
        $("noteText").focus();
        return;
      }

      // Try saving to backend
      try {
        await fetch('/api/student/notes', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ subject, text })
        });
      } catch (err) {}

      notes.unshift({ subject, text, date: "Just now" });
      selectedSubject = subject;
      $("noteDialog").close();
      addActivity(subject, "Added a note or doubt");
      if ($("subjectDialog").open) renderSubjectNotes(subject);
      showMessage("Note saved", `Your note has been saved for ${subject}.`);
    });
  }

  // AI Doubt Solver: explicit, honest messaging
  if ($("askAi")) {
    $("askAi").addEventListener("click", () => {
      showMessage(
        "AI Doubt Solver",
        "The automated AI tutor is currently awaiting API credentials configuration. To make sure you don't lose your doubt, please save it under 'Notes & Doubts' below so your faculty or peers can review it.",
        '<button class="primary-btn full-btn" id="openNoteFromAi" style="margin-top:12px;">Add as Note / Doubt →</button>'
      );
      setTimeout(() => {
        const btn = document.getElementById('openNoteFromAi');
        if (btn) btn.addEventListener('click', () => {
          $("simpleDialog").close();
          openNote();
        });
      }, 50);
    });
  }

  if ($("setGoal")) {
    $("setGoal").addEventListener("click", () => showMessage(
      "Set today's study goal",
      "Choose a realistic target for today.",
      '<label for="goalInput">Today I will...</label><input class="goal-input" id="goalInput" value="Solve 3 DSA problems" maxlength="90"/>'
    ));
  }

  if ($("simpleDone")) {
    $("simpleDone").addEventListener("click", () => {
      const goal = $("goalInput");
      if (goal && goal.value.trim()) {
        const text = goal.value.trim();
        const goalHeading = document.querySelector(".focus-goal h3");
        const goalLabel = document.querySelector(".goal-label");
        if (goalHeading) goalHeading.textContent = text;
        if (goalLabel) goalLabel.textContent = "YOUR DAILY GOAL";
      }
      $("simpleDialog").close();
    });
  }

  if ($("addPractice")) $("addPractice").addEventListener("click", () => showMessage("Add coding progress", "External platform syncing will connect to your profile. Currently displaying your tracked DSA progress."));
  if ($("practiceBtn")) $("practiceBtn").addEventListener("click", () => showMessage("Keep the streak alive", "Solve your next problem on LeetCode or Striver's sheet to keep your 7-day streak going strong!"));
  if ($("notificationBtn")) $("notificationBtn").addEventListener("click", () => showMessage("Notifications", "You're all caught up! Browser notifications will trigger when your focus timer finishes."));
  if ($("profileBtn")) $("profileBtn").addEventListener("click", () => showMessage("Student Profile", "Connected as Student. You can view your enrolled subjects, attendance, and study records."));

  // Connected Logout
  if ($("logoutBtn")) $("logoutBtn").addEventListener("click", handleLogout);

  if ($("clearActivity")) $("clearActivity").addEventListener("click", () => { activity = []; renderActivity(); });

  if ($("reminderBtn")) {
    $("reminderBtn").addEventListener("click", async () => {
      if (!("Notification" in window)) {
        showMessage("Reminders unavailable", "This browser does not support desktop notifications.");
        return;
      }
      if (Notification.permission === "granted") {
        showMessage("Reminders enabled", "Your browser will display a notification whenever a study session finishes.");
        return;
      }
      const permission = await Notification.requestPermission();
      showMessage(
        permission === "granted" ? "Reminders enabled" : "Permission not granted",
        permission === "granted"
          ? "You will now receive a desktop notification when your focus session finishes."
          : "Allow notifications in your browser settings if you would like timer alerts."
      );
    });
  }
}

document.addEventListener("DOMContentLoaded", init);
