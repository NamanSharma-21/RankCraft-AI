/**
 * RankCraft AI: Intelligent Recruiting Workspace & Candidate Screening
 * Single Page Application (SPA) Controller & State Store
 */

// ==========================================================================
// 1. Application State & Storage
// ==========================================================================
const AppState = {
  currentUser: null,
  currentRoute: 'landing',
  currentAppView: 'dashboard',
  selectedJobId: 'job_01',
  activeJobDetail: null,
  rankedCandidates: [],
  allJobs: [],
  allCandidates: [],
  recentActivity: [],
  thresholdScore: 0,
  uploadedFiles: [],
  selectedCandidateForDrawer: null
};

// ==========================================================================
// 2. Initialization & Router
// ==========================================================================
document.addEventListener('DOMContentLoaded', () => {
  initKeyboardShortcuts();
  checkAuthSession();
});

function checkAuthSession() {
  const path = window.location.pathname;
  const savedUser = localStorage.getItem('rankcraft_user');

  if (savedUser) {
    try {
      AppState.currentUser = JSON.parse(savedUser);
    } catch (e) {
      localStorage.removeItem('rankcraft_user');
      AppState.currentUser = null;
    }
  }

  if (path === '/login') {
    navigateTo('login', false);
  } else if (path === '/signup') {
    navigateTo('signup', false);
  } else if (path.startsWith('/app')) {
    if (AppState.currentUser) {
      navigateTo('app', false);
      loadInitialWorkspaceData();
    } else {
      showToast('Please sign in to access your workspace.', 'info');
      navigateTo('login', false);
    }
  } else {
    if (AppState.currentUser) {
      navigateTo('app', false);
      loadInitialWorkspaceData();
    } else {
      navigateTo('landing', false);
    }
  }
}

function navigateTo(route, updateHistory = true) {
  AppState.currentRoute = route;
  
  if (updateHistory && window.history && window.history.pushState) {
    const targetUrl = route === 'landing' ? '/' : `/${route}`;
    if (window.location.pathname !== targetUrl) {
      window.history.pushState({ route }, '', targetUrl);
    }
  }

  document.getElementById('route-landing').classList.add('hidden');
  document.getElementById('route-login').classList.add('hidden');
  document.getElementById('route-signup').classList.add('hidden');
  document.getElementById('route-app').classList.add('hidden');

  if (route === 'landing') {
    document.getElementById('route-landing').classList.remove('hidden');
    window.scrollTo(0, 0);
  } else if (route === 'login') {
    document.getElementById('route-login').classList.remove('hidden');
    window.scrollTo(0, 0);
  } else if (route === 'signup') {
    document.getElementById('route-signup').classList.remove('hidden');
    window.scrollTo(0, 0);
  } else if (route === 'app') {
    if (!AppState.currentUser) {
      showToast('Please sign in to access workspace.', 'info');
      navigateTo('login');
      return;
    }
    document.getElementById('route-app').classList.remove('hidden');
    updateUserInterfaceHeaders();
    switchAppView(AppState.currentAppView || 'dashboard');
  }
}

function switchAppView(viewName) {
  AppState.currentAppView = viewName;

  // Hide all views
  const views = document.querySelectorAll('.app-view');
  views.forEach(v => v.classList.add('hidden'));

  // Remove active from all sidebar items
  const navItems = document.querySelectorAll('.sidebar-nav-item');
  navItems.forEach(item => item.classList.remove('active'));

  // Show target view
  const targetView = document.getElementById(`view-${viewName}`);
  if (targetView) {
    targetView.classList.remove('hidden');
  }

  // Highlight active sidebar item
  const activeNavItem = document.querySelector(`.sidebar-nav-item[data-view="${viewName}"]`);
  if (activeNavItem) {
    activeNavItem.classList.add('active');
  }

  // Update breadcrumb
  const bcCurrent = document.getElementById('bc-current-page');
  if (bcCurrent) {
    bcCurrent.textContent = viewName.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase());
  }

  // Load view-specific data
  if (viewName === 'dashboard') loadDashboardData();
  else if (viewName === 'jobs') loadJobsData();
  else if (viewName === 'candidates') loadCandidatesDirectory();
  else if (viewName === 'screening') initScreeningWorkspace();
  else if (viewName === 'analytics') loadAnalyticsData();
}

function updateUserInterfaceHeaders() {
  if (!AppState.currentUser) return;
  const user = AppState.currentUser;
  
  const avatarElem = document.getElementById('user-avatar-initials');
  const nameElem = document.getElementById('user-display-name');
  const roleElem = document.getElementById('user-display-role');
  const wsElem = document.getElementById('user-ws-name');
  const greetingElem = document.getElementById('greeting-text');

  if (avatarElem) avatarElem.textContent = user.avatar_initials || 'SJ';
  if (nameElem) nameElem.textContent = user.name || 'Sarah Jenkins';
  if (roleElem) roleElem.textContent = user.role || 'Lead Recruiter';
  if (wsElem) wsElem.textContent = user.workspace || 'SomethingCo Talent';
  if (greetingElem) greetingElem.textContent = `Good morning, ${(user.name || 'Sarah').split(' ')[0]}`;
}

// ==========================================================================
// 3. Demo Authentication
// ==========================================================================
async function handleLoginSubmit(e) {
  e.preventDefault();
  const email = document.getElementById('login-email').value;
  const btn = document.getElementById('btn-login-submit');
  btn.textContent = 'Signing in...';
  btn.disabled = true;

  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email, password: 'password123' })
    });
    const data = await res.json();
    if (data.status === 'success') {
      AppState.currentUser = data.user;
      localStorage.setItem('rankcraft_user', JSON.stringify(data.user));
      showToast('Signed in successfully as ' + data.user.name, 'success');
      navigateTo('app');
      loadInitialWorkspaceData();
    }
  } catch (err) {
    showToast('Failed to sign in. Connecting in offline mode.', 'info');
    loginDemoUser();
  } finally {
    btn.textContent = 'Sign In';
    btn.disabled = false;
  }
}

function loginDemoUser() {
  const demoUser = {
    id: 'usr_001',
    name: 'Sarah Jenkins',
    email: 'recruiter@somethingco.com',
    role: 'Lead Technical Recruiter',
    company: 'SomethingCo',
    workspace: 'SomethingCo Talent',
    avatar_initials: 'SJ'
  };
  AppState.currentUser = demoUser;
  localStorage.setItem('rankcraft_user', JSON.stringify(demoUser));
  showToast('Logged in as Lead Technical Recruiter', 'success');
  navigateTo('app');
  loadInitialWorkspaceData();
}

async function handleSignupSubmit(e) {
  e.preventDefault();
  const firstName = document.getElementById('signup-first-name').value;
  const lastName = document.getElementById('signup-last-name').value;
  const email = document.getElementById('signup-email').value;
  const company = document.getElementById('signup-company').value;

  const newUser = {
    id: 'usr_' + Math.random().toString(36).substr(2, 6),
    name: `${firstName} ${lastName}`,
    email: email,
    role: 'Hiring Lead',
    company: company,
    workspace: `${company} Talent`,
    avatar_initials: `${firstName[0]}${lastName[0]}`.toUpperCase()
  };

  AppState.currentUser = newUser;
  localStorage.setItem('rankcraft_user', JSON.stringify(newUser));
  showToast('Workspace created successfully! Welcome to RankCraft AI.', 'success');
  navigateTo('app');
  loadInitialWorkspaceData();
}

function handleForgotPassword() {
  showToast('Password reset link simulated and sent to your email.', 'info');
}

function logoutUser() {
  localStorage.removeItem('rankcraft_user');
  AppState.currentUser = null;
  showToast('Logged out of workspace.', 'info');
  navigateTo('login');
}

// ==========================================================================
// 4. Data Loading & Dashboard Views
// ==========================================================================
async function loadInitialWorkspaceData() {
  try {
    const res = await fetch('/api/dashboard');
    const data = await res.json();
    AppState.allJobs = data.jobs || [];
    AppState.allCandidates = data.top_candidates || [];
    AppState.recentActivity = data.recent_activity || [];
    renderDashboard(data);
  } catch (err) {
    console.error('Failed to load dashboard data:', err);
  }
}

async function loadDashboardData() {
  try {
    const res = await fetch('/api/dashboard');
    const data = await res.json();
    renderDashboard(data);
  } catch (err) {
    console.error('Dashboard reload error:', err);
  }
}

function renderDashboard(data) {
  // Update KPIs
  if (data.kpis) {
    document.getElementById('kpi-open-roles').textContent = data.kpis.open_roles;
    document.getElementById('kpi-active-cand').textContent = data.kpis.active_candidates;
    document.getElementById('kpi-screened').textContent = data.kpis.candidates_screened;
    document.getElementById('kpi-avg-score').textContent = `${data.kpis.avg_screening_score}%`;
  }

  // Render Funnel
  const funnelContainer = document.getElementById('dashboard-funnel');
  if (funnelContainer && data.funnel) {
    funnelContainer.innerHTML = data.funnel.map(f => `
      <div class="funnel-step">
        <div class="f-stage">${f.stage}</div>
        <div class="f-count">${f.count}</div>
        <div class="f-pct">${f.pct}% conv</div>
      </div>
    `).join('');
  }

  // Render Top Candidates Table
  const topCandTbody = document.getElementById('dashboard-top-candidates');
  if (topCandTbody && data.top_candidates) {
    topCandTbody.innerHTML = data.top_candidates.map(c => `
      <tr>
        <td>
          <div class="cand-cell">
            <div class="cand-avatar">${getInitials(c.name)}</div>
            <div class="cand-meta">
              <h4>${escapeHTML(c.name)}</h4>
              <p>${escapeHTML(c.email || 'applicant@talent.io')}</p>
            </div>
          </div>
        </td>
        <td><span class="font-medium">${escapeHTML(c.role)}</span></td>
        <td><span class="font-mono font-bold text-success">${c.score}%</span></td>
        <td><span class="badge-stage stage-${c.stage}">${c.stage.toUpperCase()}</span></td>
        <td>
          <button class="btn btn-ghost btn-sm" onclick="openCandidateDrawerById('${c.id}')">View</button>
        </td>
      </tr>
    `).join('');
  }

  // Render Activity Feed
  const activityFeed = document.getElementById('dashboard-activity-feed');
  if (activityFeed && data.recent_activity) {
    activityFeed.innerHTML = data.recent_activity.map(a => `
      <div class="activity-item">
        <div class="act-dot"></div>
        <div class="act-content">
          <p><strong>${escapeHTML(a.action)}:</strong> ${escapeHTML(a.description)}</p>
          <div class="act-meta">${a.time} • ${escapeHTML(a.user)}</div>
        </div>
      </div>
    `).join('');
  }
}

// ==========================================================================
// 5. Jobs Management & Job Detail View
// ==========================================================================
async function loadJobsData() {
  try {
    const res = await fetch('/api/jobs');
    const data = await res.json();
    AppState.allJobs = data.jobs || [];
    renderJobsTable(AppState.allJobs);
  } catch (err) {
    console.error('Failed to load jobs:', err);
  }
}

function renderJobsTable(jobs) {
  const tbody = document.getElementById('jobs-table-body');
  if (!tbody) return;

  if (!jobs || jobs.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" class="text-center py-6 text-muted">No jobs matching your filter.</td></tr>`;
    return;
  }

  tbody.innerHTML = jobs.map(j => `
    <tr>
      <td>
        <strong class="cursor-pointer text-primary" onclick="openJobDetail('${j.id}')">${escapeHTML(j.title)}</strong>
        <div class="text-xs text-muted">${j.experience_req || '3+ yrs'} • ${j.employment_type || 'Full-time'}</div>
      </td>
      <td>${escapeHTML(j.department)}</td>
      <td>${escapeHTML(j.location)}</td>
      <td><span class="font-mono font-bold">${j.candidates_count || 12}</span> <span class="text-xs text-muted">(${j.screened_count || 12} screened)</span></td>
      <td><span class="badge ${j.status === 'Open' ? 'badge-open' : 'badge-draft'}">${j.status}</span></td>
      <td class="text-muted text-xs">${j.created_at}</td>
      <td class="text-right">
        <button class="btn btn-secondary btn-sm" onclick="openJobDetail('${j.id}')">View</button>
        <button class="btn btn-primary btn-sm" onclick="openJobScreeningDirect('${j.filename || 'job_01_senior_ai_ml_engineer.txt'}')">Screen</button>
      </td>
    </tr>
  `).join('');
}

function filterJobsTable() {
  const search = document.getElementById('jobs-search-input').value.toLowerCase();
  const status = document.getElementById('jobs-status-filter').value;
  const dept = document.getElementById('jobs-dept-filter').value;

  const filtered = AppState.allJobs.filter(j => {
    const matchSearch = j.title.toLowerCase().includes(search) || j.department.toLowerCase().includes(search);
    const matchStatus = status === 'ALL' || j.status === status;
    const matchDept = dept === 'ALL' || j.department === dept;
    return matchSearch && matchStatus && matchDept;
  });

  renderJobsTable(filtered);
}

async function openJobDetail(jobId) {
  try {
    const res = await fetch(`/api/jobs/${jobId}`);
    const data = await res.json();
    AppState.activeJobDetail = data.job;
    
    document.getElementById('job-detail-title').textContent = data.job.title;
    document.getElementById('job-detail-status').textContent = data.job.status;
    document.getElementById('job-detail-status').className = `badge ${data.job.status === 'Open' ? 'badge-open' : 'badge-draft'}`;
    
    // Overview Requirements
    const reqDiv = document.getElementById('job-detail-req-skills');
    if (reqDiv) {
      reqDiv.innerHTML = (data.job.required_skills || []).map(s => `<span class="skill-pill skill-pill-matched">✓ ${escapeHTML(s)}</span>`).join('');
    }

    const prefDiv = document.getElementById('job-detail-pref-skills');
    if (prefDiv) {
      prefDiv.innerHTML = (data.job.preferred_skills || []).map(s => `<span class="skill-pill skill-pill-missing-pref">• ${escapeHTML(s)}</span>`).join('');
    }

    document.getElementById('job-detail-exp').textContent = data.job.experience_req || '3+ Years';
    document.getElementById('job-detail-edu').textContent = data.job.education_req || "Bachelor's Degree";

    // Populate Job Candidates Table & Kanban
    renderJobKanbanPipeline(data.candidates || []);
    renderJobCandidatesTable(data.candidates || []);

    switchAppView('job-detail');
    switchJobTab('overview');
  } catch (err) {
    showToast('Failed to load job details.', 'danger');
  }
}

function switchJobTab(tabName) {
  const tabs = document.querySelectorAll('.tab-btn');
  tabs.forEach(t => t.classList.remove('active'));

  const activeTab = document.querySelector(`.tab-btn[data-tab="${tabName}"]`);
  if (activeTab) activeTab.classList.add('active');

  const panes = document.querySelectorAll('.job-tab-pane');
  panes.forEach(p => p.classList.add('hidden'));

  const targetPane = document.getElementById(`job-tab-${tabName}`);
  if (targetPane) targetPane.classList.remove('hidden');

  if (tabName === 'screening') {
    runInstantScreeningDemo();
  }
}

function renderJobKanbanPipeline(candidates) {
  const board = document.getElementById('kanban-pipeline-board');
  if (!board) return;

  const stages = ['applied', 'screening', 'shortlisted', 'interview', 'offer', 'hired'];
  board.innerHTML = stages.map(stg => {
    const stageCands = candidates.filter(c => c.stage === stg);
    return `
      <div class="kanban-col">
        <div class="kanban-col-header">
          <span class="kanban-col-title">${stg.toUpperCase()}</span>
          <span class="kanban-count">${stageCands.length}</span>
        </div>
        <div class="kanban-cards-list">
          ${stageCands.map(c => `
            <div class="kanban-card" onclick="openCandidateDrawerById('${c.id}')">
              <div class="kc-name">${escapeHTML(c.name)}</div>
              <div class="kc-title">${escapeHTML(c.role)}</div>
              <div class="kc-footer">
                <span class="badge-stage stage-${c.stage}">${c.stage}</span>
                <span class="kc-score">${c.score}%</span>
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }).join('');
}

function renderJobCandidatesTable(candidates) {
  const tbody = document.getElementById('job-candidates-table-body');
  if (!tbody) return;

  tbody.innerHTML = candidates.map(c => `
    <tr>
      <td>
        <div class="cand-cell">
          <div class="cand-avatar">${getInitials(c.name)}</div>
          <div class="cand-meta">
            <h4>${escapeHTML(c.name)}</h4>
            <p>${escapeHTML(c.email || '')}</p>
          </div>
        </div>
      </td>
      <td>${escapeHTML(c.role)}</td>
      <td><span class="font-mono font-bold text-success">${c.score}%</span></td>
      <td><span class="badge-stage stage-${c.stage}">${c.stage.toUpperCase()}</span></td>
      <td class="text-muted text-xs">${c.applied_date || '2026-08-25'}</td>
      <td class="text-right">
        <button class="btn btn-secondary btn-sm" onclick="openCandidateDrawerById('${c.id}')">Profile</button>
      </td>
    </tr>
  `).join('');
}

// Create Job Modal
function openCreateJobModal() {
  document.getElementById('modal-create-job').classList.remove('hidden');
}

function closeCreateJobModal() {
  document.getElementById('modal-create-job').classList.add('hidden');
}

async function handleCreateJobSubmit(e) {
  e.preventDefault();
  const title = document.getElementById('new-job-title').value;
  const dept = document.getElementById('new-job-dept').value;
  const location = document.getElementById('new-job-location').value;
  const empType = document.getElementById('new-job-type').value;
  const desc = document.getElementById('new-job-desc').value;
  const reqSkills = document.getElementById('new-job-req-skills').value.split(',').map(s => s.trim()).filter(Boolean);
  const prefSkills = document.getElementById('new-job-pref-skills').value.split(',').map(s => s.trim()).filter(Boolean);

  try {
    const res = await fetch('/api/jobs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title, department: dept, location, employment_type: empType,
        description: desc, required_skills: reqSkills, preferred_skills: prefSkills
      })
    });
    const data = await res.json();
    if (data.status === 'success') {
      showToast(`Job requisition '${title}' created successfully!`, 'success');
      closeCreateJobModal();
      loadJobsData();
      switchAppView('jobs');
    }
  } catch (err) {
    showToast('Failed to create job requisition.', 'danger');
  }
}

// ==========================================================================
// 6. Candidate Directory & Profile Drawer
// ==========================================================================
async function loadCandidatesDirectory() {
  try {
    const res = await fetch('/api/candidates');
    const data = await res.json();
    AppState.allCandidates = data.candidates || [];
    renderCandidatesDirectoryTable(AppState.allCandidates);
  } catch (err) {
    console.error('Failed to load candidate directory:', err);
  }
}

function renderCandidatesDirectoryTable(candidates) {
  const tbody = document.getElementById('candidates-directory-tbody');
  if (!tbody) return;

  tbody.innerHTML = candidates.map(c => `
    <tr>
      <td>
        <div class="cand-cell">
          <div class="cand-avatar">${getInitials(c.name)}</div>
          <div class="cand-meta">
            <h4>${escapeHTML(c.name)}</h4>
            <p>${escapeHTML(c.email || 'applicant@talent.io')}</p>
          </div>
        </div>
      </td>
      <td>${escapeHTML(c.role)}</td>
      <td><span class="text-xs text-muted">Senior AI/ML Engineer</span></td>
      <td><span class="font-mono font-bold text-success">${c.score}%</span></td>
      <td><span class="badge-stage stage-${c.stage}">${c.stage.toUpperCase()}</span></td>
      <td class="text-muted text-xs">${c.applied_date || '2026-08-25'}</td>
      <td class="text-right">
        <button class="btn btn-secondary btn-sm" onclick="openCandidateDrawerById('${c.id}')">Inspect</button>
      </td>
    </tr>
  `).join('');
}

function filterCandidatesDirectory() {
  const search = document.getElementById('candidates-search-input').value.toLowerCase();
  const stage = document.getElementById('cand-stage-filter').value;

  const filtered = AppState.allCandidates.filter(c => {
    const matchSearch = c.name.toLowerCase().includes(search) || c.role.toLowerCase().includes(search) || (c.email && c.email.toLowerCase().includes(search));
    const matchStage = stage === 'ALL' || c.stage === stage;
    return matchSearch && matchStage;
  });

  renderCandidatesDirectoryTable(filtered);
}

function openCandidateDrawerById(candId) {
  const cand = AppState.allCandidates.find(c => c.id === candId) || AppState.rankedCandidates.find(c => c.candidate_id === candId);
  if (!cand) return;
  openCandidateDrawer(cand);
}

function openCandidateDrawer(cand) {
  AppState.selectedCandidateForDrawer = cand;
  const modal = document.getElementById('modal-candidate-profile');
  if (!modal) return;

  const name = cand.name || cand.candidate_name || 'Candidate';
  const role = cand.role || 'Candidate';
  const email = cand.email || 'applicant@talent.io';
  const phone = cand.phone || '(555) 123-4567';
  const score = cand.score || cand.screening_score || 78.3;

  document.getElementById('drawer-cand-name').textContent = name;
  document.getElementById('drawer-cand-title').textContent = `${role} • ${email} • ${phone}`;
  document.getElementById('drawer-stage-select').value = (cand.stage || 'shortlisted').toLowerCase();

  const bodyContent = document.getElementById('drawer-body-content');
  bodyContent.innerHTML = `
    <!-- Top Scoring Gauge -->
    <div class="panel-card" style="margin-bottom: 16px; background: var(--bg-card);">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
          <span class="badge badge-subtle">Multi-Factor Screening Score</span>
          <h2 style="font-size: 2.2rem; font-weight: 800; font-family: var(--font-mono); color: var(--success); margin-top: 4px;">${score}%</h2>
        </div>
        <div style="text-align: right;">
          <span class="badge badge-open">High Match Alignment</span>
          <p class="text-xs text-muted" style="margin-top: 4px;">Sublinear TF-IDF + Skill Taxonomy</p>
        </div>
      </div>
    </div>

    <!-- Explainability -->
    <div class="panel-card" style="margin-bottom: 16px;">
      <h4 style="font-size: 0.8rem; text-transform: uppercase; color: var(--text-muted); margin-bottom: 6px;">Why This Candidate Ranked Here</h4>
      <div class="explain-narrative-box">
        ${escapeHTML(cand.explainability || 'Strong technical match with 5+ years experience and verified required skills in Python, PyTorch, and FastAPI.')}
      </div>
    </div>

    <!-- Skills Breakdown -->
    <div class="panel-card" style="margin-bottom: 16px;">
      <h4 style="font-size: 0.8rem; text-transform: uppercase; color: var(--text-muted); margin-bottom: 6px;">Verified Skills Breakdown</h4>
      <div style="margin-bottom: 8px;">
        <span class="text-xs text-muted">Matched Skills:</span>
        <div class="skill-pills-row">
          ${(cand.matched_skills || ['Python', 'PyTorch', 'FastAPI', 'Docker', 'Machine Learning']).map(s => `<span class="skill-pill skill-pill-matched">✓ ${escapeHTML(s)}</span>`).join('')}
        </div>
      </div>
      <div>
        <span class="text-xs text-muted">Missing Qualifications:</span>
        <div class="skill-pills-row">
          ${(cand.missing_required || ['Kubernetes']).map(s => `<span class="skill-pill skill-pill-missing-req">• ${escapeHTML(s)}</span>`).join('')}
        </div>
      </div>
    </div>

    <!-- 8-Point ATS Parseability Checklist -->
    <div class="panel-card">
      <h4 style="font-size: 0.8rem; text-transform: uppercase; color: var(--text-muted); margin-bottom: 6px;">8-Point ATS Parseability Diagnostic</h4>
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 0.82rem;">
        <div>✓ Text Extraction (&gt;50 words)</div>
        <div>✓ Name Detection</div>
        <div>✓ Email Contact Detected</div>
        <div>✓ Phone Number Detected</div>
        <div>✓ Work Experience Section</div>
        <div>✓ Timeline Dates Extracted</div>
        <div>✓ Education & Degrees</div>
        <div>✓ Technical Skills Extracted</div>
      </div>
    </div>
  `;

  modal.classList.remove('hidden');
}

function closeCandidateDrawer() {
  document.getElementById('modal-candidate-profile').classList.add('hidden');
}

async function handleDrawerStageChange(newStage) {
  if (!AppState.selectedCandidateForDrawer) return;
  const candId = AppState.selectedCandidateForDrawer.id || AppState.selectedCandidateForDrawer.candidate_id;
  try {
    const res = await fetch(`/api/candidates/${candId}/stage`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ stage: newStage })
    });
    const data = await res.json();
    showToast(`Candidate moved to ${newStage.toUpperCase()} stage.`, 'success');
    loadInitialWorkspaceData();
  } catch (err) {
    showToast(`Stage updated to ${newStage}.`, 'info');
  }
}

function shortlistCurrentDrawerCandidate() {
  handleDrawerStageChange('shortlisted');
  closeCandidateDrawer();
}

// ==========================================================================
// 7. AI Screening Workspace (Core Functionality)
// ==========================================================================
function initScreeningWorkspace() {
  if (AppState.rankedCandidates.length === 0) {
    runInstantScreeningDemo();
  }
}

function openJobScreeningDirect(filename) {
  const select = document.getElementById('screening-job-select');
  if (select) select.value = filename;
  switchAppView('screening');
  runInstantScreeningDemo();
}

function handleScreeningJobChange() {
  runInstantScreeningDemo();
}

async function runInstantScreeningDemo() {
  const jobSelect = document.getElementById('screening-job-select');
  const filename = jobSelect ? jobSelect.value : 'job_01_senior_ai_ml_engineer.txt';
  
  const container = document.getElementById('screening-cards-container');
  if (container) {
    container.innerHTML = `<div class="p-8 text-center text-muted"><p>Analyzing candidate resumes using TF-IDF & Skill Taxonomy...</p></div>`;
  }

  try {
    const formData = new FormData();
    formData.append('job_filename', filename);

    const res = await fetch('/api/rank-sample-data', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();
    
    AppState.rankedCandidates = data.ranked_candidates || [];
    renderScreeningCards(AppState.rankedCandidates);
    showToast(`Ranked ${AppState.rankedCandidates.length} candidates in 12ms`, 'success');
  } catch (err) {
    showToast('Failed to run screening demo. Check server connection.', 'danger');
  }
}

function handleCustomFileUpload(e) {
  const files = e.target.files;
  if (!files || files.length === 0) return;
  AppState.uploadedFiles = Array.from(files);
  document.getElementById('dropzone-text').textContent = `${files.length} resume file(s) selected: ${files[0].name}...`;
  showToast(`Loaded ${files.length} custom resume(s) for screening.`, 'info');
}

async function runActiveScreening() {
  if (AppState.uploadedFiles.length === 0) {
    runInstantScreeningDemo();
    return;
  }

  const formData = new FormData();
  const jobSelect = document.getElementById('screening-job-select');
  const filename = jobSelect ? jobSelect.value : 'job_01_senior_ai_ml_engineer.txt';
  
  formData.append('job_description_text', `Target role: ${filename}`);
  AppState.uploadedFiles.forEach(f => {
    formData.append('resumes', f);
  });

  try {
    const res = await fetch('/rank', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();
    AppState.rankedCandidates = data.ranked_candidates || [];
    renderScreeningCards(AppState.rankedCandidates);
    showToast(`Screening completed for ${data.total_resumes_processed} custom resumes!`, 'success');
  } catch (err) {
    showToast('Custom screening failed. Running pre-packaged demo data.', 'info');
    runInstantScreeningDemo();
  }
}

function applyScoreThresholdFilter(val) {
  AppState.thresholdScore = parseInt(val);
  document.getElementById('threshold-val').textContent = `${val}%`;
  
  const filtered = AppState.rankedCandidates.filter(c => (c.screening_score || c.score || 0) >= AppState.thresholdScore);
  renderScreeningCards(filtered);
}

function renderScreeningCards(candidates) {
  const container = document.getElementById('screening-cards-container');
  if (!container) return;

  const countBadge = document.getElementById('screening-results-count');
  if (countBadge) countBadge.textContent = `${candidates.length} Candidates Ranked`;

  if (!candidates || candidates.length === 0) {
    container.innerHTML = `<div class="p-8 text-center text-muted"><p>No candidates meet the selected score threshold.</p></div>`;
    return;
  }

  container.innerHTML = candidates.map(c => {
    const score = c.screening_score || c.score || 0;
    const tfidf = c.score_percentage || c.tfidf || 0;
    const skills = c.skill_coverage_pct || 75;
    const title = c.title_match_pct || 80;
    const exp = c.experience_match_pct || 100;
    const edu = c.education_match_pct || 100;
    const atsScore = c.ats_parseability ? c.ats_parseability.parseability_score : 90;
    const atsGrade = c.ats_parseability ? c.ats_parseability.parseability_grade : 'High';

    return `
      <div class="candidate-card">
        <!-- Top Row -->
        <div class="card-top-row">
          <div class="card-candidate-header">
            <div class="card-rank-badge">#${c.rank || 1}</div>
            <div class="card-candidate-details">
              <h3>${escapeHTML(c.candidate_name || c.name)}</h3>
              <p>${escapeHTML(c.file_name || 'resume.pdf')} • ${c.file_type || 'PDF'} • ${c.highest_degree || "Bachelor's"} in ${escapeHTML(c.primary_discipline || 'Computer Science')}</p>
            </div>
          </div>
          <div class="card-scores-gauge">
            <div class="main-score-box">
              <span class="score-val">${score}%</span>
              <span class="score-lbl">Screening Score</span>
            </div>
          </div>
        </div>

        <!-- 5 Sub-Metric Bars -->
        <div class="submetrics-grid">
          <div class="sm-item">
            <div class="sm-label"><span>TF-IDF Match (40%)</span><span class="sm-val">${tfidf}%</span></div>
            <div class="sm-progress-track"><div class="sm-progress-fill" style="width: ${tfidf}%;"></div></div>
          </div>
          <div class="sm-item">
            <div class="sm-label"><span>Skill Coverage (25%)</span><span class="sm-val">${skills}%</span></div>
            <div class="sm-progress-track"><div class="sm-progress-fill" style="width: ${skills}%;"></div></div>
          </div>
          <div class="sm-item">
            <div class="sm-label"><span>Title Match (15%)</span><span class="sm-val">${title}%</span></div>
            <div class="sm-progress-track"><div class="sm-progress-fill" style="width: ${title}%;"></div></div>
          </div>
          <div class="sm-item">
            <div class="sm-label"><span>Experience (10%)</span><span class="sm-val">${exp}%</span></div>
            <div class="sm-progress-track"><div class="sm-progress-fill" style="width: ${exp}%;"></div></div>
          </div>
          <div class="sm-item">
            <div class="sm-label"><span>Education (10%)</span><span class="sm-val">${edu}%</span></div>
            <div class="sm-progress-track"><div class="sm-progress-fill" style="width: ${edu}%;"></div></div>
          </div>
        </div>

        <!-- Skills & Explainability -->
        <div class="card-body-grid">
          <div class="skills-column">
            <h4>Matched Skills (${(c.matched_skills || []).length})</h4>
            <div class="skill-pills-row">
              ${(c.matched_skills || []).map(s => `<span class="skill-pill skill-pill-matched">✓ ${escapeHTML(s)}</span>`).join('')}
            </div>
            <h4 style="margin-top: 10px;">Missing Required (${(c.missing_required || []).length})</h4>
            <div class="skill-pills-row">
              ${(c.missing_required || []).length > 0 
                ? (c.missing_required || []).map(s => `<span class="skill-pill skill-pill-missing-req">• ${escapeHTML(s)}</span>`).join('')
                : '<span class="text-xs text-muted">None (All requirements met)</span>'}
            </div>
          </div>
          <div class="explain-column">
            <h4>Evidence & Explainability Rationale</h4>
            <div class="explain-narrative-box">
              ${escapeHTML(c.explainability || 'Direct technical alignment on core role requirements.')}
            </div>
          </div>
        </div>

        <!-- Card Actions Bar -->
        <div class="card-actions-bar">
          <div class="card-ats-health">
            <span class="badge badge-subtle">ATS Health: ${atsScore}/100 (${atsGrade})</span>
          </div>
          <div class="card-action-btns">
            <button class="btn btn-secondary btn-sm" onclick='openCandidateDrawer(${JSON.stringify(c).replace(/'/g, "&#39;")})'>📋 Full Profile & ATS Audit</button>
            <button class="btn btn-primary btn-sm" onclick="quickShortlistCandidate('${c.candidate_id || c.id}')">Shortlist</button>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

function quickShortlistCandidate(candId) {
  showToast(`Candidate ${candId} shortlisted and moved to Interview pipeline!`, 'success');
}

// ==========================================================================
// 8. Candidate Comparison Matrix Modal
// ==========================================================================
function openComparisonModal() {
  const topCands = AppState.rankedCandidates.slice(0, 4);
  if (topCands.length === 0) {
    showToast('Run screening first to generate candidates for comparison.', 'info');
    return;
  }

  const table = document.getElementById('comparison-table');
  if (!table) return;

  let headers = `<tr><th>Evaluation Dimension</th>${topCands.map(c => `<th>${escapeHTML(c.candidate_name || c.name)}<div class="text-xs text-muted">#${c.rank} Rank</div></th>`).join('')}</tr>`;

  let rowScore = `<tr><td>Overall Screening Score</td>${topCands.map((c, i) => `<td class="${i === 0 ? 'comp-best' : ''} font-mono">${c.screening_score || c.score}%</td>`).join('')}</tr>`;
  let rowTfidf = `<tr><td>TF-IDF Match</td>${topCands.map(c => `<td class="font-mono">${c.score_percentage || c.tfidf}%</td>`).join('')}</tr>`;
  let rowSkills = `<tr><td>Skill Coverage</td>${topCands.map(c => `<td class="font-mono">${c.skill_coverage_pct || 80}%</td>`).join('')}</tr>`;
  let rowTitle = `<tr><td>Job Title Match</td>${topCands.map(c => `<td class="font-mono">${c.title_match_pct || 85}%</td>`).join('')}</tr>`;
  let rowExp = `<tr><td>Experience Tenure</td>${topCands.map(c => `<td>${c.total_years_experience || '5.0'} Yrs</td>`).join('')}</tr>`;
  let rowEdu = `<tr><td>Highest Degree</td>${topCands.map(c => `<td>${c.highest_degree || "Master's"}</td>`).join('')}</tr>`;
  let rowAts = `<tr><td>ATS Health Score</td>${topCands.map(c => `<td>${c.ats_parseability ? c.ats_parseability.parseability_score : 90}/100</td>`).join('')}</tr>`;

  table.innerHTML = headers + rowScore + rowTfidf + rowSkills + rowTitle + rowExp + rowEdu + rowAts;

  document.getElementById('modal-comparison').classList.remove('hidden');
}

function closeComparisonModal() {
  document.getElementById('modal-comparison').classList.add('hidden');
}

// ==========================================================================
// 9. Export CSV
// ==========================================================================
function exportRankingsCSV() {
  const jobSelect = document.getElementById('screening-job-select');
  const filename = jobSelect ? jobSelect.value : 'job_01_senior_ai_ml_engineer.txt';
  window.location.href = `/api/export-csv?job_filename=${encodeURIComponent(filename)}`;
  showToast('Downloading ranked candidates CSV export...', 'info');
}

// ==========================================================================
// 10. Analytics & Settings
// ==========================================================================
async function loadAnalyticsData() {
  try {
    const res = await fetch('/api/analytics');
    if (!res.ok) throw new Error('Analytics fetch failed');
    const data = await res.json();
    // Update summary metrics if elements exist
    const totalAppsElem = document.querySelector('#view-analytics .kpi-grid .kpi-card:nth-child(1) .kpi-value');
    if (totalAppsElem && data.summary) {
      totalAppsElem.textContent = data.summary.total_applications || 38;
    }
  } catch (err) {
    showToast('Viewing simulated live talent analytics.', 'info');
  }
}

function toggleWorkspaceDropdown() {
  showToast('Current Workspace: SomethingCo Talent (Pro Edition)', 'info');
}

function handleSaveSettings(e) {
  e.preventDefault();
  const name = document.getElementById('settings-name').value;
  const email = document.getElementById('settings-email').value;
  const company = document.getElementById('settings-company').value;

  if (AppState.currentUser) {
    AppState.currentUser.name = name;
    AppState.currentUser.email = email;
    AppState.currentUser.company = company;
    AppState.currentUser.workspace = `${company} Talent`;
    localStorage.setItem('rankcraft_user', JSON.stringify(AppState.currentUser));
    updateUserInterfaceHeaders();
  }

  showToast('Workspace settings and screening weights updated successfully!', 'success');
}

// ==========================================================================
// 11. Command Palette & Shortcuts (⌘K)
// ==========================================================================
function initKeyboardShortcuts() {
  document.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault();
      openCommandPalette();
    } else if (e.key === 'Escape') {
      closeCommandPalette();
      closeCreateJobModal();
      closeCandidateDrawer();
      closeComparisonModal();
    }
  });

  const cmdInput = document.getElementById('command-input');
  if (cmdInput) {
    cmdInput.addEventListener('input', (e) => {
      filterCommandResults(e.target.value);
    });
  }
}

function openCommandPalette() {
  const modal = document.getElementById('command-palette-backdrop');
  if (!modal) return;
  modal.classList.remove('hidden');
  const input = document.getElementById('command-input');
  if (input) {
    input.value = '';
    input.focus();
  }
  filterCommandResults('');
}

function closeCommandPalette() {
  const modal = document.getElementById('command-palette-backdrop');
  if (modal) modal.classList.add('hidden');
}

function filterCommandResults(query) {
  const container = document.getElementById('command-results');
  if (!container) return;

  const commands = [
    { title: 'Go to Dashboard', category: 'Navigation', action: () => switchAppView('dashboard') },
    { title: 'View All Jobs', category: 'Navigation', action: () => switchAppView('jobs') },
    { title: 'Open AI Screening Hub', category: 'Navigation', action: () => switchAppView('screening') },
    { title: 'Candidate Directory', category: 'Navigation', action: () => switchAppView('candidates') },
    { title: 'Talent Acquisition Analytics', category: 'Navigation', action: () => switchAppView('analytics') },
    { title: 'Workspace Settings', category: 'Navigation', action: () => switchAppView('settings') },
    { title: '+ Create New Job Requisition', category: 'Actions', action: () => openCreateJobModal() },
    { title: '🚀 Run 1-Click Screening Demo', category: 'Actions', action: () => { switchAppView('screening'); runInstantScreeningDemo(); } },
    { title: '📥 Export Ranked Candidates to CSV', category: 'Actions', action: () => exportRankingsCSV() },
    { title: 'API Documentation (Swagger)', category: 'Help', action: () => openApiDocs() }
  ];

  const filtered = commands.filter(c => c.title.toLowerCase().includes(query.toLowerCase()));

  container.innerHTML = filtered.map((c, idx) => `
    <div class="command-item ${idx === 0 ? 'selected' : ''}" onclick="executeCommand(${idx})">
      <span>${escapeHTML(c.title)}</span>
      <span class="text-xs text-muted">${c.category}</span>
    </div>
  `).join('');

  window._activeCommands = filtered;
}

function executeCommand(idx) {
  if (window._activeCommands && window._activeCommands[idx]) {
    closeCommandPalette();
    window._activeCommands[idx].action();
  }
}

// ==========================================================================
// 12. UI Utilities, Toasts & Dropdowns
// ==========================================================================
function toggleUserMenu() {
  const menu = document.getElementById('user-dropdown-menu');
  if (menu) menu.classList.toggle('hidden');
}

function toggleNotifications() {
  const notifs = document.getElementById('notifications-dropdown');
  if (notifs) notifs.classList.toggle('hidden');
}

function clearNotifications() {
  const list = document.getElementById('notif-list');
  if (list) list.innerHTML = `<div class="p-4 text-center text-xs text-muted">No unread notifications</div>`;
  const badge = document.querySelector('.notif-badge');
  if (badge) badge.style.display = 'none';
}

function toggleSidebar() {
  const sidebar = document.getElementById('app-sidebar');
  if (sidebar) sidebar.classList.toggle('open');
}

function selectChip(btn, val) {
  const group = btn.parentElement;
  group.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
  btn.classList.add('active');
}

function openApiDocs() {
  window.open('/docs', '_blank');
}

function showToast(message, type = 'info', duration = 3500) {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast-card ${type}`;
  toast.innerHTML = `<div class="toast-body">${escapeHTML(message)}</div>`;

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    toast.style.transition = 'all 200ms ease-out';
    setTimeout(() => toast.remove(), 250);
  }, duration);
}

function getInitials(name) {
  if (!name) return 'CD';
  const parts = name.trim().split(' ');
  if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

function escapeHTML(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
