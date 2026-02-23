/* ============================================================
   StudyAI — Frontend Application Logic
   In a real deployment this talks to Django/Flask + MySQL backend
   Here we simulate all AI logic & data in the browser
   ============================================================ */

// ==================== STATE ====================
let state = {
    user: null,
    subjects: [],
    scores: [],
    notifications: [],
    timetable: [],
    studyHistory: []
};

// ==================== DEMO DATA ====================
const DEMO_SUBJECTS = [
    { id: 1, name: 'Quantum Mechanics', difficulty: 9, examDate: '2025-03-15', color: '#7c6aff', modules: ['Wave-Particle Duality', 'Schrödinger Equation', 'Quantum Entanglement', 'Measurement Problem', 'Fundamentals & History'] },
    { id: 2, name: 'Organic Chemistry', difficulty: 8, examDate: '2025-03-10', color: '#ff6a8e', modules: ['Reaction Mechanisms', 'Stereochemistry', 'Functional Groups', 'NMR Spectroscopy', 'Basic Nomenclature'] },
    { id: 3, name: 'Linear Algebra', difficulty: 7, examDate: '2025-03-20', color: '#00e5b4', modules: ['Eigenvalues & Eigenvectors', 'Matrix Transformations', 'Vector Spaces', 'Systems of Equations', 'Introduction to Vectors'] },
    { id: 4, name: 'Data Structures', difficulty: 6, examDate: '2025-03-25', color: '#ffb84d', modules: ['Graph Algorithms', 'Dynamic Programming', 'Trees & Heaps', 'Sorting Algorithms', 'Arrays & Lists'] },
    { id: 5, name: 'Thermodynamics', difficulty: 7, examDate: '2025-03-18', color: '#ff5050', modules: ['Entropy & Second Law', 'Heat Engines', 'Phase Transitions', 'Gas Laws', 'Zeroth & First Law'] },
    { id: 6, name: 'Statistics', difficulty: 5, examDate: '2025-04-01', color: '#a0ff6a', modules: ['Hypothesis Testing', 'Regression Analysis', 'Probability Distributions', 'Descriptive Stats', 'Data Collection'] }
];

const DEMO_SCORES = [
    { subject: 'Quantum Mechanics', score: 62, type: 'Quiz', date: '2025-01-10', notes: 'Struggled with wave functions' },
    { subject: 'Organic Chemistry', score: 71, type: 'Midterm', date: '2025-01-15', notes: 'Weak on reaction mechanisms' },
    { subject: 'Linear Algebra', score: 85, type: 'Quiz', date: '2025-01-12', notes: '' },
    { subject: 'Data Structures', score: 90, type: 'Quiz', date: '2025-01-18', notes: '' },
    { subject: 'Thermodynamics', score: 68, type: 'Practice', date: '2025-01-20', notes: 'Entropy problems are difficult' },
    { subject: 'Statistics', score: 88, type: 'Quiz', date: '2025-01-22', notes: '' },
    { subject: 'Quantum Mechanics', score: 67, type: 'Practice', date: '2025-01-28', notes: '' },
    { subject: 'Organic Chemistry', score: 76, type: 'Quiz', date: '2025-02-02', notes: '' },
];

const DEMO_NOTIFICATIONS = [
    { id: 1, icon: '⚠️', title: 'Exam Alert: Organic Chemistry', desc: 'Exam in 5 days — increase study intensity!', time: '2 hours ago', unread: true },
    { id: 2, icon: '📊', title: 'Weekly Review Ready', desc: 'Your AI performance report is ready to view', time: '5 hours ago', unread: true },
    { id: 3, icon: '🎯', title: 'Goal Achieved!', desc: 'You hit your weekly study target of 28 hours!', time: '1 day ago', unread: true },
    { id: 4, icon: '💡', title: 'AI Tip', desc: 'Spaced repetition can improve your Quantum Mech score by ~20%', time: '2 days ago', unread: false },
    { id: 5, icon: '📅', title: 'Study Reminder', desc: 'Linear Algebra revision session starts in 1 hour', time: '3 days ago', unread: false },
];

// ==================== AUTH ====================
function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    if (!email || !password) return;

    // Simulate API call: POST /api/auth/login
    const name = email.split('@')[0].replace(/[^a-zA-Z]/g, '') || 'Student';
    const displayName = name.charAt(0).toUpperCase() + name.slice(1);

    loginUser({ email, name: displayName + ' Johnson', firstName: displayName });
}

function handleRegister(e) {
    e.preventDefault();
    const firstName = document.getElementById('regFirstName').value;
    const lastName = document.getElementById('regLastName').value;
    const email = document.getElementById('regEmail').value;
    const university = document.getElementById('regUniversity').value;

    // Simulate API call: POST /api/auth/register
    loginUser({ email, name: `${firstName} ${lastName}`, firstName });
    showToast('Account created successfully! Welcome to StudyAI 🎉');
}

function loginUser(user) {
    state.user = user;
    state.subjects = [...DEMO_SUBJECTS];
    state.scores = [...DEMO_SCORES];
    state.notifications = [...DEMO_NOTIFICATIONS];

    document.getElementById('loginPage').classList.remove('active');
    const app = document.getElementById('appPage');
    app.classList.add('active');
    app.style.display = 'flex';

    // Update UI with user data
    document.getElementById('welcomeName').textContent = user.firstName;
    document.getElementById('userInfo').querySelector('.user-name').textContent = user.name;
    document.getElementById('userInfo').querySelector('.user-email').textContent = user.email;
    document.getElementById('userInfo').querySelector('.user-avatar').textContent = user.firstName[0].toUpperCase();

    initApp();
}

function logout() {
    state = { user: null, subjects: [], scores: [], notifications: [], timetable: [], studyHistory: [] };
    document.getElementById('appPage').classList.remove('active');
    document.getElementById('appPage').style.display = 'none';
    document.getElementById('loginPage').classList.add('active');
    showToast('Logged out successfully');
}

function switchTab(tab) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
    event.target.classList.add('active');
    document.getElementById(tab === 'login' ? 'loginForm' : 'registerForm').classList.add('active');
}

// ==================== NAVIGATION ====================
function showSection(name, navEl) {
    document.querySelectorAll('.content-section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

    document.getElementById(`section-${name}`).classList.add('active');
    if (navEl) navEl.classList.add('active');

    const titles = { dashboard: 'Dashboard', timetable: 'Timetable', subjects: 'Subjects & Syllabus', performance: 'Performance', notifications: 'Notifications', progress: 'Progress' };
    document.getElementById('pageTitle').textContent = titles[name] || name;

    if (window.innerWidth < 768) toggleSidebar();

    // Re-render specific sections
    if (name === 'timetable' && state.timetable.length === 0) generateTimetable();
    if (name === 'performance') renderPerformanceChart();
    if (name === 'progress') renderProgressCharts();
}

function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('open');
}

// ==================== APP INIT ====================
function initApp() {
    renderTodaySchedule();
    renderAITips();
    renderStrengthChart();
    renderSubjectsList();
    renderScoreDropdown();
    renderNotifications();
    renderWeakAreas();
    generateTimetable();
}

// ==================== DASHBOARD ====================
function renderTodaySchedule() {
    const schedule = [
        { time: '08:00 AM', subject: 'Quantum Mechanics', duration: '90 min', color: '#7c6aff' },
        { time: '10:00 AM', subject: 'Organic Chemistry', duration: '75 min', color: '#ff6a8e' },
        { time: '02:00 PM', subject: 'Thermodynamics', duration: '60 min', color: '#ff5050' },
        { time: '04:00 PM', subject: 'Linear Algebra', duration: '45 min', color: '#00e5b4' },
    ];

    const container = document.getElementById('todaySchedule');
    container.innerHTML = schedule.map(s => `
        <div class="schedule-item">
            <span class="schedule-time">${s.time}</span>
            <span class="schedule-dot" style="background:${s.color}"></span>
            <span class="schedule-subject">${s.subject}</span>
            <span class="schedule-duration">${s.duration}</span>
        </div>
    `).join('');
}

function renderAITips() {
    const tips = [
        { icon: '🔥', text: 'Focus on <strong>Quantum Mechanics</strong> today — exam in 15 days and your score is below 70%' },
        { icon: '⚡', text: '<strong>Organic Chemistry</strong> exam is closest. Add 30 min of reaction mechanisms review' },
        { icon: '💡', text: 'You study best between 8–11 AM based on your history. Schedule hardest topics then' },
    ];

    document.getElementById('aiTips').innerHTML = tips.map(t => `
        <div class="ai-tip">
            <span class="ai-tip-icon">${t.icon}</span>
            <div class="ai-tip-text">${t.text}</div>
        </div>
    `).join('');
}

function renderStrengthChart() {
    const ctx = document.getElementById('strengthChart');
    if (!ctx) return;
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: state.subjects.map(s => s.name.split(' ')[0]),
            datasets: [{
                label: 'Current Score %',
                data: [65, 74, 85, 90, 68, 88],
                backgroundColor: state.subjects.map(s => s.color + '40'),
                borderColor: state.subjects.map(s => s.color),
                borderWidth: 2, borderRadius: 8,
            }, {
                label: 'AI Predicted (next 2 weeks)',
                data: [72, 80, 88, 92, 75, 91],
                backgroundColor: 'rgba(255,255,255,0.05)',
                borderColor: 'rgba(255,255,255,0.3)',
                borderWidth: 2, borderRadius: 8,
                borderDash: [5, 5],
            }]
        },
        options: getChartOptions('Score %')
    });
}

// ==================== TIMETABLE ====================
function generateTimetable() {
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
    const hours = parseInt(document.getElementById('studyHoursRange')?.value || 6);
    const container = document.getElementById('weeklyTimetable');
    if (!container) return;

    // AI Scheduling Engine: sort by (difficulty * weight) + exam_proximity_weight
    const sorted = [...state.subjects].sort((a, b) => {
        const daysA = Math.max(1, Math.ceil((new Date(a.examDate) - new Date()) / 86400000));
        const daysB = Math.max(1, Math.ceil((new Date(b.examDate) - new Date()) / 86400000));
        const scoreA = getSubjectAvgScore(a.name);
        const scoreB = getSubjectAvgScore(b.name);
        // Priority = difficulty / avg_score * (1 / days_until_exam)
        const priorityA = (a.difficulty / Math.max(scoreA, 1)) * (100 / daysA);
        const priorityB = (b.difficulty / Math.max(scoreB, 1)) * (100 / daysB);
        return priorityB - priorityA;
    });

    const timeSlots = generateTimeSlots(hours);
    let subjectIndex = 0;

    container.innerHTML = days.map(day => `
        <div class="day-column">
            <div class="day-header">${day.slice(0,3)}</div>
            ${timeSlots.map(slot => {
                const subject = sorted[subjectIndex % sorted.length];
                subjectIndex++;
                const intensity = subject.difficulty > 7 ? 'High' : subject.difficulty > 4 ? 'Med' : 'Low';
                return `
                    <div class="time-block" style="background:${subject.color}18; border-left: 3px solid ${subject.color}">
                        <div class="tb-time">${slot.time}</div>
                        <div class="tb-subject">${subject.name.split(' ')[0]}</div>
                        <div class="tb-duration">${slot.duration} • ${intensity}</div>
                    </div>
                `;
            }).join('')}
        </div>
    `).join('');

    showToast('⚡ AI timetable generated based on difficulty, exam dates & your performance!');
}

function generateTimeSlots(hours) {
    const slots = [];
    let currentHour = 8;
    const durations = hours > 8 ? [90, 60, 90, 60, 90] : [90, 60, 75];
    let remaining = hours * 60;

    for (let dur of durations) {
        if (remaining <= 0) break;
        const actualDur = Math.min(dur, remaining);
        slots.push({ time: formatHour(currentHour), duration: `${actualDur}m` });
        currentHour += actualDur / 60 + 0.25; // 15 min break
        remaining -= actualDur;
    }
    return slots;
}

function formatHour(h) {
    const hour = Math.floor(h);
    const min = Math.round((h - hour) * 60);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const displayH = hour > 12 ? hour - 12 : hour;
    return `${displayH}:${min.toString().padStart(2, '0')} ${ampm}`;
}

function updateHoursDisplay(val) {
    document.getElementById('hoursDisplay').textContent = `${val}h`;
}

// ==================== SUBJECTS ====================
function addSubject(e) {
    e.preventDefault();
    const name = document.getElementById('subjectName').value;
    const difficulty = parseInt(document.getElementById('subjectDifficulty').value);
    const examDate = document.getElementById('subjectExamDate').value;
    const modulesRaw = document.getElementById('subjectModules').value;

    const colors = ['#7c6aff', '#ff6a8e', '#00e5b4', '#ffb84d', '#ff5050', '#a0ff6a', '#6abaff'];
    const color = colors[state.subjects.length % colors.length];

    // AI sorts modules by difficulty (most difficult first)
    const modules = modulesRaw ? sortModulesByDifficulty(modulesRaw.split(',').map(m => m.trim())) : [];

    const subject = { id: Date.now(), name, difficulty, examDate, color, modules };
    state.subjects.push(subject);

    renderSubjectsList();
    renderScoreDropdown();
    e.target.reset();
    showToast(`✅ "${name}" added! AI sorted ${modules.length} modules by difficulty`);
}

function sortModulesByDifficulty(modules) {
    // AI difficulty estimation based on keywords
    const difficultyKeywords = {
        high: ['advanced', 'complex', 'theory', 'proof', 'equation', 'algorithm', 'mechanism', 'quantum', 'differential', 'abstract'],
        med: ['analysis', 'application', 'method', 'technique', 'calculation', 'integration'],
        low: ['introduction', 'basic', 'fundamentals', 'overview', 'history', 'definition', 'types']
    };

    return modules.sort((a, b) => {
        const scoreA = getDifficultyScore(a.toLowerCase(), difficultyKeywords);
        const scoreB = getDifficultyScore(b.toLowerCase(), difficultyKeywords);
        return scoreB - scoreA; // Most difficult first
    });
}

function getDifficultyScore(text, keywords) {
    let score = 5;
    keywords.high.forEach(k => { if (text.includes(k)) score += 3; });
    keywords.med.forEach(k => { if (text.includes(k)) score += 1; });
    keywords.low.forEach(k => { if (text.includes(k)) score -= 2; });
    return score;
}

function renderSubjectsList() {
    const container = document.getElementById('subjectsList');
    if (!container) return;

    if (state.subjects.length === 0) {
        container.innerHTML = '<div class="card" style="text-align:center; color: var(--text-muted)">No subjects yet. Add your first subject!</div>';
        return;
    }

    container.innerHTML = state.subjects.map(s => {
        const daysLeft = Math.ceil((new Date(s.examDate) - new Date()) / 86400000);
        const diffClass = s.difficulty > 7 ? 'diff-high' : s.difficulty > 4 ? 'diff-med' : 'diff-low';
        const diffLabel = s.difficulty > 7 ? 'Hard' : s.difficulty > 4 ? 'Medium' : 'Easy';
        const avgScore = getSubjectAvgScore(s.name);

        return `
        <div class="subject-card">
            <div class="subject-card-header">
                <h4 style="color:${s.color}">${s.name}</h4>
                <span class="difficulty-badge ${diffClass}">${diffLabel} (${s.difficulty}/10)</span>
            </div>
            <div class="subject-meta">
                <span class="subject-exam">📅 Exam: ${daysLeft > 0 ? daysLeft + 'd left' : 'Past'}</span>
                <span>📊 Avg Score: ${avgScore > 0 ? avgScore + '%' : 'No data'}</span>
            </div>
            ${s.modules.length > 0 ? `
            <div class="modules-list">
                <h5>AI-Sorted Modules (Hardest → Easiest)</h5>
                ${s.modules.map((m, i) => `
                    <div class="module-item">
                        <span class="module-rank" style="background:${i < 2 ? 'var(--danger)' : i < 4 ? 'var(--warning)' : 'var(--success)'}">${i + 1}</span>
                        ${m}
                    </div>
                `).join('')}
            </div>
            ` : ''}
        </div>
        `;
    }).join('');
}

// ==================== PERFORMANCE ====================
function renderScoreDropdown() {
    const sel = document.getElementById('scoreSubject');
    if (!sel) return;
    const current = sel.value;
    sel.innerHTML = '<option value="">Select subject...</option>' +
        state.subjects.map(s => `<option value="${s.name}" ${s.name === current ? 'selected' : ''}>${s.name}</option>`).join('');
}

function logScore(e) {
    e.preventDefault();
    const subject = document.getElementById('scoreSubject').value;
    const score = parseInt(document.getElementById('scoreValue').value);
    const type = document.getElementById('scoreType').value;
    const notes = document.getElementById('scoreNotes').value;

    const entry = { subject, score, type, date: new Date().toISOString().split('T')[0], notes };
    state.scores.unshift(entry);

    // AI Analysis
    const avg = getSubjectAvgScore(subject);
    let message = `📊 Score logged! `;
    if (score < 70) message += `AI recommends 2x more focus on ${subject} — below target`;
    else if (score >= 90) message += `Excellent! Maintain this momentum`;
    else message += `Good progress. AI adjusted your timetable for ${subject}`;

    renderPerformanceChart();
    renderWeakAreas();
    e.target.reset();
    showToast(message);
}

function renderPerformanceChart() {
    const ctx = document.getElementById('performanceChart');
    if (!ctx) return;

    // Destroy existing chart
    const existing = Chart.getChart(ctx);
    if (existing) existing.destroy();

    const subjects = [...new Set(state.scores.map(s => s.subject))].slice(0, 5);
    const datasets = subjects.map((subj, i) => {
        const subjectScores = state.scores.filter(s => s.subject === subj).reverse();
        const colors = ['#7c6aff', '#ff6a8e', '#00e5b4', '#ffb84d', '#ff5050'];
        const color = state.subjects.find(s => s.name === subj)?.color || colors[i];
        return {
            label: subj.split(' ')[0],
            data: subjectScores.map(s => s.score),
            borderColor: color, backgroundColor: color + '20',
            tension: 0.4, fill: false, borderWidth: 2, pointRadius: 4
        };
    });

    const maxLen = Math.max(...datasets.map(d => d.data.length));
    const labels = Array.from({ length: maxLen }, (_, i) => `Test ${i + 1}`);

    // Add AI prediction line
    const avgScores = subjects.map(s => getSubjectAvgScore(s));
    const overallAvg = avgScores.reduce((a, b) => a + b, 0) / avgScores.length;

    new Chart(ctx, {
        type: 'line',
        data: { labels: [...labels, 'Predicted'], datasets },
        options: getChartOptions('Score %')
    });
}

function renderWeakAreas() {
    const container = document.getElementById('weakAreas');
    if (!container) return;

    const weakSubjects = state.subjects.map(s => {
        const avg = getSubjectAvgScore(s.name);
        return { ...s, avg: avg || 75 };
    }).sort((a, b) => a.avg - b.avg).slice(0, 4);

    container.innerHTML = weakSubjects.map(s => {
        const borderColor = s.avg < 70 ? 'var(--danger)' : s.avg < 80 ? 'var(--warning)' : 'var(--success)';
        const rec = s.avg < 70 ? 'Critical: Double study time, daily revision' :
                    s.avg < 80 ? 'Needs improvement: Focus on weak modules' : 'Good: Maintain current pace';
        return `
            <div class="weak-area-card" style="border-left-color: ${borderColor}">
                <h4 style="color:${s.color}">${s.name}</h4>
                <div class="progress-bar-wrap">
                    <div class="progress-bar" style="width:${s.avg}%; background:${borderColor}"></div>
                </div>
                <div class="weak-area-note">${s.avg}% avg — ${rec}</div>
            </div>
        `;
    }).join('');
}

// ==================== NOTIFICATIONS ====================
function addReminder() {
    const text = document.getElementById('reminderText').value;
    const time = document.getElementById('reminderTime').value;
    if (!text) { showToast('Please enter a reminder text'); return; }

    const reminder = {
        id: Date.now(), icon: '⏰', title: 'Custom Reminder',
        desc: text, time: time ? new Date(time).toLocaleString() : 'Now', unread: true
    };
    state.notifications.unshift(reminder);
    renderNotifications();
    document.getElementById('reminderText').value = '';
    document.getElementById('reminderTime').value = '';
    showToast('⏰ Reminder set!');
}

function renderNotifications() {
    const container = document.getElementById('notificationsList');
    if (!container) return;

    container.innerHTML = state.notifications.map(n => `
        <div class="notif-item ${n.unread ? 'unread' : ''}" id="notif-${n.id}">
            <div class="notif-icon">${n.icon}</div>
            <div class="notif-content">
                <div class="notif-title">${n.title}</div>
                <div class="notif-desc">${n.desc}</div>
                <div class="notif-time">${n.time}</div>
            </div>
            <button class="notif-dismiss" onclick="dismissNotif(${n.id})">✕</button>
        </div>
    `).join('');

    // Update badge
    const unreadCount = state.notifications.filter(n => n.unread).length;
    const badge = document.querySelector('.nav-item .badge');
    if (badge) badge.textContent = unreadCount;
}

function dismissNotif(id) {
    state.notifications = state.notifications.filter(n => n.id !== id);
    renderNotifications();
}

// ==================== PROGRESS CHARTS ====================
function renderProgressCharts() {
    renderWeeklyHoursChart();
    renderCoverageChart();
    renderTimelineChart();
}

function renderWeeklyHoursChart() {
    const ctx = document.getElementById('weeklyHoursChart');
    if (!ctx) return;
    const existing = Chart.getChart(ctx);
    if (existing) existing.destroy();

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'Hours Studied',
                data: [5.5, 6.5, 4, 7, 6, 3, 2.5],
                backgroundColor: 'rgba(124,106,255,0.4)', borderColor: '#7c6aff',
                borderWidth: 2, borderRadius: 8,
            }, {
                label: 'Target',
                data: [6, 6, 6, 6, 6, 4, 4],
                type: 'line', borderColor: '#ff6a8e', borderDash: [5, 5],
                backgroundColor: 'transparent', borderWidth: 2, pointRadius: 0
            }]
        },
        options: getChartOptions('Hours')
    });
}

function renderCoverageChart() {
    const ctx = document.getElementById('coverageChart');
    if (!ctx) return;
    const existing = Chart.getChart(ctx);
    if (existing) existing.destroy();

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: state.subjects.map(s => s.name.split(' ')[0]),
            datasets: [{
                data: [72, 65, 88, 90, 60, 85],
                backgroundColor: state.subjects.map(s => s.color + '80'),
                borderColor: state.subjects.map(s => s.color),
                borderWidth: 2,
            }]
        },
        options: {
            ...getChartOptions('Coverage %'),
            cutout: '65%',
            plugins: { legend: { position: 'right', labels: { color: '#e8eaf0', font: { family: 'DM Sans' }, padding: 12 } } }
        }
    });
}

function renderTimelineChart() {
    const ctx = document.getElementById('timelineChart');
    if (!ctx) return;
    const existing = Chart.getChart(ctx);
    if (existing) existing.destroy();

    const labels = ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7 (pred)', 'Week 8 (pred)'];
    new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [{
                label: 'Overall Performance',
                data: [65, 68, 70, 74, 72, 78, null, null],
                borderColor: '#7c6aff', backgroundColor: 'rgba(124,106,255,0.1)',
                fill: true, tension: 0.4, borderWidth: 3, pointRadius: 5
            }, {
                label: 'AI Prediction',
                data: [null, null, null, null, null, 78, 83, 87],
                borderColor: '#00e5b4', backgroundColor: 'rgba(0,229,180,0.1)',
                fill: true, tension: 0.4, borderWidth: 2,
                borderDash: [8, 4], pointRadius: 5
            }, {
                label: 'Study Hours (scaled)',
                data: [55, 60, 48, 70, 65, 72, null, null],
                borderColor: '#ffb84d', backgroundColor: 'transparent',
                tension: 0.4, borderWidth: 2, borderDash: [3, 3], pointRadius: 3
            }]
        },
        options: getChartOptions('Score %')
    });
}

// ==================== CHART OPTIONS ====================
function getChartOptions(yLabel) {
    return {
        responsive: true, maintainAspectRatio: false,
        plugins: {
            legend: { labels: { color: '#e8eaf0', font: { family: 'DM Sans' }, padding: 16 } },
            tooltip: {
                backgroundColor: '#1a1d25', borderColor: 'rgba(255,255,255,0.1)',
                borderWidth: 1, titleColor: '#e8eaf0', bodyColor: '#6b7180',
                titleFont: { family: 'Syne', weight: 'bold' }
            }
        },
        scales: {
            x: { ticks: { color: '#6b7180', font: { family: 'DM Sans' } }, grid: { color: 'rgba(255,255,255,0.04)' } },
            y: {
                ticks: { color: '#6b7180', font: { family: 'DM Sans' } },
                grid: { color: 'rgba(255,255,255,0.04)' },
                title: { display: true, text: yLabel, color: '#6b7180' }
            }
        }
    };
}

// ==================== CHATBOT ====================
let chatOpen = false;

function toggleChatbot() {
    chatOpen = !chatOpen;
    const container = document.getElementById('chatbotContainer');
    const fab = document.getElementById('chatFab');
    container.classList.toggle('open', chatOpen);
    fab.textContent = chatOpen ? '✕' : '💬';
}

function sendSuggestion(btn) {
    document.getElementById('chatInput').value = btn.textContent;
    sendChatMessage();
    document.getElementById('chatSuggestions').style.display = 'none';
}

function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const msg = input.value.trim();
    if (!msg) return;

    addChatMessage('user', msg);
    input.value = '';

    // Show typing indicator
    const typingId = 'typing-' + Date.now();
    addTypingIndicator(typingId);

    // Simulate AI response (in real app: POST /api/chat)
    setTimeout(() => {
        removeTypingIndicator(typingId);
        const response = generateAIResponse(msg);
        addChatMessage('bot', response);
    }, 1200 + Math.random() * 800);
}

function addChatMessage(role, text) {
    const container = document.getElementById('chatMessages');
    const div = document.createElement('div');
    div.className = `chat-message ${role}`;
    div.innerHTML = `
        <div class="msg-avatar">${role === 'bot' ? '⚡' : (state.user?.firstName?.[0] || 'U')}</div>
        <div class="msg-bubble">${text}</div>
    `;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function addTypingIndicator(id) {
    const container = document.getElementById('chatMessages');
    const div = document.createElement('div');
    div.id = id; div.className = 'chat-message bot typing-indicator';
    div.innerHTML = `<div class="msg-avatar">⚡</div><div class="msg-bubble"><span></span><span></span><span></span></div>`;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function removeTypingIndicator(id) {
    document.getElementById(id)?.remove();
}

function generateAIResponse(msg) {
    const lower = msg.toLowerCase();

    // Contextual AI responses based on user's data
    const weakSubject = state.subjects.sort((a, b) => getSubjectAvgScore(a.name) - getSubjectAvgScore(b.name))[0];
    const closestExam = state.subjects.filter(s => new Date(s.examDate) > new Date()).sort((a, b) => new Date(a.examDate) - new Date(b.examDate))[0];

    if (lower.includes('study') && lower.includes('effective')) {
        return `Great question! Based on your data, here are your top strategies:<br><br>
        1. 🧠 <strong>Spaced Repetition</strong> — Review material at increasing intervals<br>
        2. ⚡ <strong>Pomodoro Technique</strong> — 25 min focus + 5 min break<br>
        3. 📝 <strong>Active Recall</strong> — Test yourself without looking at notes<br>
        4. 🌙 <strong>Sleep</strong> — Your memory consolidates during REM sleep<br><br>
        Your best hours seem to be <strong>8-11 AM</strong> based on your study history!`;
    }

    if (lower.includes('weak') || lower.includes('struggling')) {
        return `Based on your scores, your weakest subject is <strong>${weakSubject?.name || 'Quantum Mechanics'}</strong> at ${getSubjectAvgScore(weakSubject?.name) || 65}% average.<br><br>
        🎯 <strong>My recommendations:</strong><br>
        • Allocate 2 extra hours/week to this subject<br>
        • Focus on modules: ${weakSubject?.modules?.slice(0, 2).join(', ') || 'core concepts'}<br>
        • Try teaching concepts to someone else (Feynman Technique)<br>
        • Use past papers for practice`;
    }

    if (lower.includes('exam') || lower.includes('deadline')) {
        const days = closestExam ? Math.ceil((new Date(closestExam.examDate) - new Date()) / 86400000) : 10;
        return `Your closest exam is <strong>${closestExam?.name || 'Organic Chemistry'}</strong> in <strong>${days} days</strong>! 📅<br><br>
        📋 <strong>Exam prep strategy:</strong><br>
        • Days ${days}-${Math.max(days-3, 1)}: Complete all modules<br>
        • Last 3 days: Only revision + practice tests<br>
        • Night before: Light review, good sleep<br>
        • Morning: Brief notes review, confidence boost!<br><br>
        Your AI timetable has been optimized for this — check it in the Timetable tab!`;
    }

    if (lower.includes('timetable') || lower.includes('schedule')) {
        return `Your AI-generated timetable prioritizes subjects based on:<br><br>
        📊 <strong>3 Key Factors:</strong><br>
        1. <strong>Difficulty</strong> (hardest first, when you're most alert)<br>
        2. <strong>Exam Proximity</strong> (closer exam = more time allocated)<br>
        3. <strong>Your Performance</strong> (weak subjects get more slots)<br><br>
        Go to the <strong>Timetable</strong> section to view and adjust your schedule. You can set your available hours and days!`;
    }

    if (lower.includes('explain') || lower.includes('concept') || lower.includes('understand')) {
        return `I'd love to help you understand a concept! Please share the specific topic or concept you're struggling with, and I'll break it down with:<br><br>
        • 🔍 Simple explanation<br>
        • 📌 Key points to remember<br>
        • 💡 Real-world analogies<br>
        • 📝 Practice approach<br><br>
        What topic would you like me to explain?`;
    }

    if (lower.includes('motivat') || lower.includes('tired') || lower.includes('burnout')) {
        return `Feeling this way is completely normal! Here's what the science says:<br><br>
        🔋 <strong>Beat Study Fatigue:</strong><br>
        • Take a 20-min power nap (proven to boost memory!)<br>
        • Change your study environment<br>
        • Break large tasks into tiny 5-min wins<br>
        • Remember: You're ${document.getElementById('weekProgress')?.textContent || '73%'} through your weekly goal!<br><br>
        You've got this! 💪 Every expert was once a beginner.`;
    }

    // Default intelligent response
    const responses = [
        `I analyzed your study data and noticed you've been making solid progress! 📈 Your strongest subject is Data Structures at 90%. Keep it up while focusing more on Quantum Mechanics (65%).`,
        `Great question! Based on research, the most effective study method for complex subjects like yours is <strong>interleaved practice</strong> — mixing different topics in one session rather than blocking. This improves long-term retention by ~43%!`,
        `I've looked at your performance trends. Your scores improve significantly on days you study in the morning. Try to front-load your hardest subjects (Quantum Mechanics, Organic Chemistry) in AM sessions for better results!`,
        `Quick tip: For subjects with formulas and equations, write them out by hand 3 times. The motor memory encoding significantly helps recall under exam pressure. 📝`
    ];
    return responses[Math.floor(Math.random() * responses.length)];
}

// ==================== UTILITIES ====================
function getSubjectAvgScore(subjectName) {
    const subjectScores = state.scores.filter(s => s.subject === subjectName);
    if (subjectScores.length === 0) return 0;
    return Math.round(subjectScores.reduce((sum, s) => sum + s.score, 0) / subjectScores.length);
}

function showToast(msg) {
    const toast = document.getElementById('toast');
    toast.textContent = msg;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 3500);
}

// ==================== INIT ====================
document.addEventListener('DOMContentLoaded', () => {
    // Auto-populate form date defaults
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 30);
    const dateInput = document.getElementById('subjectExamDate');
    if (dateInput) dateInput.value = tomorrow.toISOString().split('T')[0];
});
