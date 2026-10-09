const subjects = [
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

function renderSubjects(){
  subjectsGrid.innerHTML = subjects.map((s,i)=>`
    <article class="subject-card">
      <div class="subject-top"><span class="subject-emoji" style="background:${s.color};color:${s.ink}">${s.icon}</span><span class="grade ${s.grade==="B"?"gold":""}">${s.grade}</span></div>
      <h3>${s.name}</h3><p class="semester">Semester 3</p>
      <div class="subject-metric"><span>Latest marks</span><span class="subject-value">${s.marks}<span style="font-size:10px;font-weight:500;color:#789096"> / ${s.total}</span></span></div>
      <div class="subject-metric"><span>Attendance</span><span class="subject-value">${s.attendance}% <span style="font-size:10px;font-weight:500;color:#789096">(${s.attended}/${s.classes})</span></span></div>
      <div class="progress"><span style="width:${s.attendance}%"></span></div>
      <button class="notes-btn" data-subject="${i}">▤ &nbsp; Notes & Doubts &nbsp; ›</button>
      <button class="text-btn subject-open" data-open="${i}" style="margin-top:11px;width:100%">View subject details →</button>
    </article>`).join("");
  noteSubject.innerHTML = subjects.map(s=>`<option>${s.name}</option>`).join("");
  document.querySelectorAll("[data-subject]").forEach(b=>b.addEventListener("click",()=>openSubject(Number(b.dataset.subject),true)));
  document.querySelectorAll("[data-open]").forEach(b=>b.addEventListener("click",()=>openSubject(Number(b.dataset.open),false)));
}
function addActivity(title,desc){
  activity.unshift({icon:"✦",cls:"note-icon",title,desc,time:"Just now"});
  activity=activity.slice(0,6);renderActivity();
}
function renderActivity(){
  $("activityList").innerHTML=activity.length?activity.slice(0,3).map(a=>`<div class="activity-item"><span class="activity-icon ${a.cls}">${a.icon}</span><div><b>${escapeHtml(a.title)}</b><small>${escapeHtml(a.desc)}</small></div><time>${a.time}</time></div>`).join(""):`<div class="empty-state">No recent activity yet. Start with one small task!</div>`;
}
function escapeHtml(value){return String(value).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));}
function openSubject(index,showNotes){
  const s=subjects[index];selectedSubject=s.name;
  $("subjectTitle").textContent=s.name;
  $("subjectStats").innerHTML=`<div class="detail-stat"><small>Latest marks</small><b>${s.marks}/${s.total}</b></div><div class="detail-stat"><small>Attendance</small><b>${s.attendance}%</b></div><div class="detail-stat"><small>Grade</small><b>${s.grade}</b></div>`;
  $("topicList").innerHTML=s.topics.map(([name,p])=>`<div class="topic-row"><span>${name}</span><div class="progress"><span style="width:${p}%;background:${p<40?"#eab64d":""}"></span></div><small>${p}%</small></div>`).join("");
  renderSubjectNotes(s.name);
  $("subjectDialog").showModal();
  if(showNotes) setTimeout(()=>$("subjectNotes").scrollIntoView({behavior:"smooth",block:"nearest"}),80);
}
function renderSubjectNotes(name){
  const list=notes.filter(n=>n.subject===name);
  $("subjectNotes").innerHTML=list.length?list.map(n=>`<div class="saved-note">${escapeHtml(n.text)}<small>${escapeHtml(n.date)} · ${escapeHtml(n.subject)}</small></div>`).join(""):`<div class="empty-state">No notes yet for this subject. Save your first doubt.</div>`;
}
function openNote(subject=selectedSubject){
  $("noteSubject").value=subject;
  $("noteText").value="";
  $("noteDialog").showModal();
}
function showMessage(title,message,extra=""){
  $("simpleTitle").textContent=title;$("simpleMessage").textContent=message;$("simpleExtra").innerHTML=extra;$("simpleDialog").showModal();
}
function formatTime(seconds){const m=Math.floor(seconds/60).toString().padStart(2,"0");const s=(seconds%60).toString().padStart(2,"0");return `${m}:${s}`;}
function updateTimer(){ $("timerDisplay").textContent=formatTime(remainingSeconds); }
function stopTimer(){if(timerInterval){clearInterval(timerInterval);timerInterval=null;}timerRunning=false;}
function selectTimerMode(minutes){
  stopTimer();timerMinutes=minutes;remainingSeconds=minutes*60;updateTimer();
  document.querySelectorAll(".mode").forEach(b=>b.classList.toggle("active",Number(b.dataset.minutes)===minutes));
  $("timerStart").textContent=minutes===25?"Start focus":"Start break";$("timerStatus").textContent="Ready when you are.";
}
function startTimer(){
  if(timerRunning){stopTimer();$("timerStart").textContent="Resume";$("timerStatus").textContent="Paused. Take a breath.";return;}
  if(remainingSeconds<=0)remainingSeconds=timerMinutes*60;
  timerRunning=true;$("timerStart").textContent="Pause";$("timerStatus").textContent="You're in focus mode. One task at a time.";
  timerInterval=setInterval(()=>{
    remainingSeconds--;updateTimer();
    if(remainingSeconds<=0){
      stopTimer();$("timerStart").textContent="Start again";$("timerStatus").textContent="Session complete. Well done!";
      addActivity("Focus session","Completed a "+timerMinutes+" minute session");
      if("Notification" in window && Notification.permission==="granted")new Notification("UDAAN Focus Timer",{body:"Your session is complete. Take a short break!"});
      showMessage("Session complete! 🎉","You showed up and did the work. Take a short break, then decide your next small step.");
    }
  },1000);
}
function openTimer(){updateTimer();$("timerDialog").showModal();}
function init(){
  renderSubjects();renderActivity();updateTimer();
  $("openTimer").addEventListener("click",openTimer);
  $("startGoal").addEventListener("click",()=>{selectTimerMode(25);openTimer();});
  $("timerStart").addEventListener("click",startTimer);
  $("timerReset").addEventListener("click",()=>{stopTimer();remainingSeconds=timerMinutes*60;updateTimer();$("timerStart").textContent=timerMinutes===25?"Start focus":"Start break";$("timerStatus").textContent="Timer reset. Ready when you are.";});
  document.querySelectorAll(".mode").forEach(b=>b.addEventListener("click",()=>selectTimerMode(Number(b.dataset.minutes))));
  $("subjectAddNote").addEventListener("click",()=>openNote(selectedSubject));
  $("addNote").addEventListener("click",()=>openNote());
  $("saveNote").addEventListener("click",e=>{
    e.preventDefault();const text=$("noteText").value.trim();const subject=$("noteSubject").value;
    if(!text){$("noteText").focus();return;}
    notes.unshift({subject,text,date:"Just now"});selectedSubject=subject;
    $("noteDialog").close();addActivity(subject,"Added a note or doubt");
    if($("subjectDialog").open)renderSubjectNotes(subject);
    showMessage("Note saved","Your note has been saved in this demo for "+subject+".");
  });
  $("askAi").addEventListener("click",()=>showMessage("AI Doubt Solver","The AI tutor will be connected in a later version. For now, save your question under Notes & Doubts so you can revisit it."));
  $("setGoal").addEventListener("click",()=>showMessage("Set today's study goal","Choose a realistic target for today.",'<label for="goalInput">Today I will...</label><input class="goal-input" id="goalInput" value="Solve 3 DSA problems" maxlength="90"/>'));
  $("simpleDone").addEventListener("click",()=>{
    const goal=$("goalInput");if(goal&&goal.value.trim()){const text=goal.value.trim();document.querySelector(".focus-goal h3").textContent=text;document.querySelector(".goal-label").textContent="YOUR DAILY GOAL";$("simpleDialog").close();return;}
    $("simpleDialog").close();
  });
  $("addPractice").addEventListener("click",()=>showMessage("Add coding progress","Platform syncing will be added after we choose the integration. For now, your dashboard displays sample progress."));
  $("practiceBtn").addEventListener("click",()=>showMessage("Keep the streak alive","Open your preferred coding platform and solve one problem. Platform links and automatic progress syncing are planned for the next version."));
  $("notificationBtn").addEventListener("click",()=>showMessage("Notifications","You're all caught up. Focus timer completion notifications can be enabled from your browser."));
  $("profileBtn").addEventListener("click",()=>showMessage("Student profile","Profile settings and real student accounts will be connected when we add the backend."));
  $("logoutBtn").addEventListener("click",()=>showMessage("Demo portal","This is a front-end prototype, so login and logout aren't connected yet."));
  $("clearActivity").addEventListener("click",()=>{activity=[];renderActivity();});
  $("reminderBtn").addEventListener("click",async()=>{
    if(!("Notification" in window)){showMessage("Reminders unavailable","This browser does not support desktop notifications.");return;}
    if(Notification.permission==="granted"){showMessage("Reminders enabled","Your browser can show a notification when a focus session finishes.");return;}
    const permission=await Notification.requestPermission();
    showMessage(permission==="granted"?"Reminders enabled":"Permission not granted",permission==="granted"?"You'll receive a browser notification when a focus session finishes.":"Allow notifications in your browser settings if you'd like timer alerts.");
  });
}
document.addEventListener("DOMContentLoaded",init);
