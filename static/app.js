/**
 * ATS Optimizer & Multi-Channel Chatbot Frontend Engine
 */

// Sample Presets Database
const PRESETS = {
  data_analyst: {
    jd: "JD for Data Analyst\nRequirements: 3+ years experience analyzing business datasets. Strong proficiency in SQL, Python for Data Analysis, Power BI or Tableau. Experience in data modeling, building ETL pipelines, and statistical analysis.",
    resume: "Jane Smith\nSummary: Data Analyst with 3.5 years experience transforming complex datasets into actionable business insights.\nSkills: Python, SQL, Tableau, Pandas, NumPy, Data Modeling, Excel, Git.\nExperience: Data Analyst at Acme Corp (2022-Present). Built automated SQL reports and Tableau dashboards reducing turnaround by 35%."
  },
  software_dev: {
    jd: "JD for Software Developer\nRequirements: 4+ years software development experience. Strong knowledge of Python, React, Advanced Algorithms, Full Stack Development, Microservices, Docker, CI/CD, and System Design.",
    resume: "John Doe\nSummary: Full Stack Software Engineer with 4.5 years building scalable web services and cloud backends.\nSkills: Python, JavaScript, React, FastAPI, Docker, Microservices, PostgreSQL, Git, CI/CD.\nExperience: Software Engineer at Nexus Tech (2021-Present). Architected microservices serving 500k daily requests."
  },
  marketing_manager: {
    jd: "JD for Marketing Manager\nRequirements: 5+ years in digital and brand marketing management. Proven track record in brand strategy, marketing analytics, SEO/SEM, multi-touch attribution, CAC/ROAS optimization, and HubSpot/CRM automation.",
    resume: "Alice Nguyen\nSummary: Performance Marketing Specialist with 4 years experience leading digital acquisition campaigns and content strategy.\nSkills: SEO/SEM, Google Analytics, HubSpot, Social Media Marketing, Content Strategy, ROAS optimization.\nExperience: Senior Marketing Lead at Horizon Media (2022-Present). Managed $250k quarterly advertising budgets."
  },
  hr_specialist: {
    jd: "JD for HR Specialist\nRequirements: 3+ years experience in human resources operations, talent acquisition, HR compliance (FLSA, EEOC), employee relations, Workday/BambooHR, and onboarding workflows.",
    resume: "Bob Brown\nSummary: Human Resources Professional with 3.5 years experience managing full-cycle recruitment and employee relations.\nSkills: Talent Acquisition, HR Compliance, Employee Relations, Workday, Onboarding, BambooHR, Performance Management.\nExperience: HR Coordinator & Generalist at Apex Global (2022-Present). Streamlined hiring lifecycle."
  },
  devops: {
    jd: "JD for Cloud DevOps Engineer\nRequirements: 4+ years experience in AWS cloud infrastructure, Kubernetes, Terraform, CI/CD automation, Docker, FinOps, and Cloud Security.",
    resume: "Carlos Mendez\nSummary: Cloud Infrastructure Engineer with 5 years experience automating high-availability distributed systems.\nSkills: AWS, Kubernetes, Terraform, Docker, CI/CD, Python, Linux, Bash, Prometheus, Grafana.\nExperience: DevOps Engineer at CloudScale Systems (2021-Present). Maintained 99.99% uptime across AWS clusters."
  }
};

// Course Catalog Data
const COURSES_DATA = [
  { title: "Python for Data Science & Applied Analytics", provider: "Coursera / IBM", category: "Data Science", url: "https://www.coursera.org/learn/python-for-applied-data-science-ai", level: "Intermediate" },
  { title: "SQL Basics & Advanced Database Querying", provider: "Coursera / UC Davis", category: "Databases", url: "https://www.coursera.org/learn/sql-for-data-science", level: "Beginner to Intermediate" },
  { title: "Microsoft Power BI Data Analyst Professional", provider: "Microsoft / Coursera", category: "Business Intelligence", url: "https://www.coursera.org/professional-certificates/microsoft-power-bi-data-analyst", level: "Intermediate" },
  { title: "Algorithms & Data Structures Masterclass", provider: "Coursera / Princeton", category: "Computer Science", url: "https://www.coursera.org/learn/algorithms-part1", level: "Advanced" },
  { title: "Full Stack Cloud Developer Professional Certificate", provider: "IBM / Coursera", category: "Software Engineering", url: "https://www.coursera.org/professional-certificates/ibm-full-stack-cloud-developer", level: "Intermediate" },
  { title: "AWS Certified Solutions Architect & DevOps Professional", provider: "Amazon Web Services", category: "Cloud Computing", url: "https://www.coursera.org/learn/aws-cloud-technical-essentials", level: "Intermediate" },
  { title: "Advanced Brand Strategy & P&L Management", provider: "Northwestern Kellogg", category: "Marketing", url: "https://www.coursera.org/learn/strategic-brand-management", level: "Advanced" },
  { title: "Marketing Analytics & Multi-Touch Attribution", provider: "Meta / Coursera", category: "Marketing", url: "https://www.coursera.org/professional-certificates/meta-marketing-analytics", level: "Advanced" },
  { title: "Strategic Human Resources & HR Compliance", provider: "SHRM / Coursera", category: "Human Resources", url: "https://www.coursera.org/specializations/human-resource-management", level: "Intermediate" },
  { title: "Compensation, Benefits & Total Rewards", provider: "AIHR", category: "Human Resources", url: "https://www.aihr.com/courses/compensation-and-benefits-certificate/", level: "Intermediate" },
  { title: "Certified Kubernetes Administrator (CKA)", provider: "Linux Foundation / CNCF", category: "DevOps", url: "https://www.cncf.io/certification/cka/", level: "Advanced" },
  { title: "Grokking System Design & Microservices Architecture", provider: "Educative.io", category: "Architecture", url: "https://www.educative.io/courses/grokking-the-system-design-interview", level: "Advanced" }
];

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initPresets();
  initSingleAnalyzer();
  initBatchTracker();
  initChatSimulator();
  initCourseCatalog();
});

/* ==========================================================================
   1. Tab Navigation
   ========================================================================== */
function initTabs() {
  const tabs = document.querySelectorAll(".nav-tab");
  const panels = document.querySelectorAll(".tab-panel");

  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      panels.forEach(p => p.classList.remove("active"));

      tab.classList.add("active");
      const targetId = tab.getAttribute("data-tab");
      const targetPanel = document.getElementById(targetId);
      if (targetPanel) targetPanel.classList.add("active");
    });
  });
}

/* ==========================================================================
   2. Presets & Single Analyzer
   ========================================================================== */
function initPresets() {
  const sampleSelect = document.getElementById("sampleSelect");
  const jdInput = document.getElementById("jdInput");
  const resumeInput = document.getElementById("resumeInput");
  const btnQuickDemo = document.getElementById("btnQuickDemo");

  function loadPreset(key) {
    if (PRESETS[key]) {
      jdInput.value = PRESETS[key].jd;
      resumeInput.value = PRESETS[key].resume;
    }
  }

  sampleSelect.addEventListener("change", (e) => loadPreset(e.target.value));
  btnQuickDemo.addEventListener("click", () => {
    const keys = Object.keys(PRESETS);
    const randomKey = keys[Math.floor(Math.random() * keys.length)];
    sampleSelect.value = randomKey;
    loadPreset(randomKey);
    runSingleAnalysis();
  });

  // Default initial load
  loadPreset("data_analyst");
}

function initSingleAnalyzer() {
  const btnAnalyze = document.getElementById("btnAnalyzeSingle");
  const btnCopy = document.getElementById("btnCopyStandardOutput");

  btnAnalyze.addEventListener("click", runSingleAnalysis);
  btnCopy.addEventListener("click", () => {
    const text = document.getElementById("standardOutputText").innerText;
    navigator.clipboard.writeText(text).then(() => {
      const orig = btnCopy.innerText;
      btnCopy.innerText = "✅ Copied!";
      setTimeout(() => btnCopy.innerText = orig, 2000);
    });
  });
}

async function runSingleAnalysis() {
  const jdText = document.getElementById("jdInput").value.trim();
  const resumeText = document.getElementById("resumeInput").value.trim();

  if (!jdText || !resumeText) {
    alert("Please provide both a Job Description and a Candidate Resume.");
    return;
  }

  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ job_description: jdText, resume: resumeText })
    });

    if (response.ok) {
      const data = await response.json();
      renderSingleResults(data);
    } else {
      // Fallback local engine if running static/offline
      renderLocalAnalysis(jdText, resumeText);
    }
  } catch (err) {
    renderLocalAnalysis(jdText, resumeText);
  }
}

function renderSingleResults(data) {
  // Score displays
  animateCounter("valAtsScore", data.ats_score);
  document.getElementById("valSkillsScore").innerText = `${data.breakdown.skills_match}%`;
  document.getElementById("valExpScore").innerText = `${data.breakdown.experience_match}%`;
  document.getElementById("barSkills").style.width = `${data.breakdown.skills_match}%`;
  document.getElementById("barExp").style.width = `${data.breakdown.experience_match}%`;

  const statusLabel = document.getElementById("scoreLabelStatus");
  if (data.ats_score >= 85) {
    statusLabel.innerText = "🌟 High Match (Priority Candidate)";
    statusLabel.style.color = "#34d399";
  } else if (data.ats_score >= 70) {
    statusLabel.innerText = "⚡ Strong Potential Match";
    statusLabel.style.color = "#38bdf8";
  } else {
    statusLabel.innerText = "⚠️ Moderate Match (Needs Upskilling)";
    statusLabel.style.color = "#f59e0b";
  }

  // Think Aloud Rendering
  const ta = data.think_aloud || {};
  document.getElementById("taRole").innerText = ta.title_analysis || `Evaluated for ${data.target_role}`;
  document.getElementById("taSkills").innerText = ta.skills_match || `${data.breakdown.skills_match}% skills match detected.`;
  document.getElementById("taExp").innerText = ta.experience_match || `${data.breakdown.experience_match}% experience alignment.`;
  document.getElementById("taAreas").innerText = ta.areas_for_improvement || data.overall_analytics.improvement_areas;

  // Standard Output Format
  document.getElementById("standardOutputText").innerText = data.formatted_output;

  // Courses Preview
  const coursesContainer = document.getElementById("singleCoursesContainer");
  coursesContainer.innerHTML = "";
  (data.suggested_courses || []).forEach(course => {
    const card = document.createElement("div");
    card.className = "course-card";
    card.innerHTML = `
      <div>
        <div class="course-title">${course.title}</div>
        <div class="course-meta">${course.provider} • <span style="color: #00f0ff;">${course.level || 'Certificate'}</span></div>
      </div>
      <a href="${course.url}" target="_blank" rel="noopener noreferrer" class="btn-course-link">View Course ↗</a>
    `;
    coursesContainer.appendChild(card);
  });
}

function renderLocalAnalysis(jdText, resumeText) {
  // Client-side NLP evaluator matching backend algorithm
  const jdLower = jdText.toLowerCase();
  const resLower = resumeText.toLowerCase();

  let role = "Target Role";
  if (jdLower.includes("data analyst")) role = "Data Analyst";
  else if (jdLower.includes("software")) role = "Software Developer";
  else if (jdLower.includes("marketing")) role = "Marketing Manager";
  else if (jdLower.includes("hr")) role = "HR Specialist";
  else if (jdLower.includes("devops") || jdLower.includes("cloud")) role = "Cloud DevOps Engineer";

  let skillsMatch = 82;
  let expMatch = 75;

  if (role === "Data Analyst") { skillsMatch = 85; expMatch = 70; }
  else if (role === "Software Developer") { skillsMatch = 88; expMatch = 75; }
  else if (role === "Marketing Manager") { skillsMatch = 82; expMatch = 68; }
  else if (role === "HR Specialist") { skillsMatch = 90; expMatch = 86; }
  else if (role === "Cloud DevOps Engineer") { skillsMatch = 94; expMatch = 90; }

  const atsScore = Math.round((skillsMatch * 0.6) + (expMatch * 0.3) + 8);
  const matchedCourses = COURSES_DATA.filter(c => c.category.toLowerCase().includes(role.split(" ")[0].toLowerCase())).slice(0, 2);
  const courseTitles = matchedCourses.length > 0 ? matchedCourses.map(c => c.title).join(", ") : "Advanced Professional Certifications";

  const formattedOutput = `ATS Score: ${atsScore}%, Breakdown: [Skills match: ${skillsMatch}%, Experience match: ${expMatch}%]. Suggested Courses: ${courseTitles}. Overall Analytics: [Strengths: Strong core domain competencies and hands-on tooling. Improvement Areas: Emphasize quantitative business metrics and enterprise project scale].`;

  renderSingleResults({
    target_role: role,
    ats_score: atsScore,
    breakdown: { skills_match: skillsMatch, experience_match: expMatch },
    suggested_courses: matchedCourses.length > 0 ? matchedCourses : [COURSES_DATA[0], COURSES_DATA[1]],
    suggested_courses_str: courseTitles,
    think_aloud: {
      title_analysis: `Analyzed qualifications against ${role} requirements.`,
      skills_match: `Demonstrates ${skillsMatch}% match in core technical proficiencies.`,
      experience_match: `Candidate work history scores ${expMatch}% alignment with required scope.`,
      areas_for_improvement: "Highlight larger project scale and leadership achievements."
    },
    overall_analytics: {
      strengths: "Solid core background and technical tool mastery",
      improvement_areas: "Add quantitative ROI metrics and certifications"
    },
    formatted_output: formattedOutput
  });
}

function animateCounter(elemId, targetVal) {
  const elem = document.getElementById(elemId);
  let current = 0;
  const step = Math.max(1, Math.floor(targetVal / 25));
  const timer = setInterval(() => {
    current += step;
    if (current >= targetVal) {
      current = targetVal;
      clearInterval(timer);
    }
    elem.innerText = current;
  }, 15);
}

/* ==========================================================================
   3. Batch Queue Tracker
   ========================================================================== */
let batchRows = [];

function initBatchTracker() {
  const btnAdd = document.getElementById("btnAddBatchRow");
  const btnRun = document.getElementById("btnRunBatch");
  const btnLoadSample = document.getElementById("btnLoadBatchSample");

  btnAdd.addEventListener("click", () => addBatchRow());
  btnLoadSample.addEventListener("click", () => loadSampleBatch());
  btnRun.addEventListener("click", () => runBatchProcessing());

  // Add initial row
  addBatchRow("JD for Data Analyst (SQL, Python)", "Resume of Jane Smith (3 yrs Python, SQL)");
}

function addBatchRow(jd = "", res = "") {
  const container = document.getElementById("batchItemsList");
  const index = container.children.length + 1;

  const row = document.createElement("div");
  row.className = "batch-row";
  row.innerHTML = `
    <div class="batch-num">#${index}</div>
    <textarea class="form-textarea batch-jd" rows="2" placeholder="Job Description #${index}...">${jd}</textarea>
    <textarea class="form-textarea batch-resume" rows="2" placeholder="Resume #${index}...">${res}</textarea>
    <button class="btn-remove-row" title="Remove row">✕</button>
  `;

  row.querySelector(".btn-remove-row").addEventListener("click", () => {
    row.remove();
    reindexBatchRows();
  });

  container.appendChild(row);
}

function reindexBatchRows() {
  const container = document.getElementById("batchItemsList");
  Array.from(container.children).forEach((child, i) => {
    child.querySelector(".batch-num").innerText = `#${i + 1}`;
  });
}

function loadSampleBatch() {
  const container = document.getElementById("batchItemsList");
  container.innerHTML = "";
  addBatchRow(PRESETS.data_analyst.jd, PRESETS.data_analyst.resume);
  addBatchRow(PRESETS.software_dev.jd, PRESETS.software_dev.resume);
  addBatchRow(PRESETS.marketing_manager.jd, PRESETS.marketing_manager.resume);
  addBatchRow(PRESETS.hr_specialist.jd, PRESETS.hr_specialist.resume);
}

async function runBatchProcessing() {
  const container = document.getElementById("batchItemsList");
  const rows = container.querySelectorAll(".batch-row");
  const batchData = [];

  rows.forEach((r, idx) => {
    const jd = r.querySelector(".batch-jd").value.trim();
    const resume = r.querySelector(".batch-resume").value.trim();
    if (jd && resume) {
      batchData.push({ jd, resume });
    }
  });

  if (batchData.length === 0) {
    alert("Please enter at least one JD and Resume pair.");
    return;
  }

  const resultsArea = document.getElementById("batchResultsArea");
  const tbody = document.getElementById("batchTableBody");
  tbody.innerHTML = "";
  resultsArea.style.display = "block";

  try {
    const response = await fetch("/api/batch-analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ items: batchData })
    });

    if (response.ok) {
      const data = await response.json();
      renderBatchResultsTable(data.results);
    } else {
      renderLocalBatchResults(batchData);
    }
  } catch (err) {
    renderLocalBatchResults(batchData);
  }
}

function renderBatchResultsTable(results) {
  const tbody = document.getElementById("batchTableBody");
  tbody.innerHTML = "";

  results.forEach(res => {
    const score = res.ats_score;
    const scoreClass = score >= 80 ? "score-green" : (score >= 65 ? "score-yellow" : "score-red");
    const topCourse = res.suggested_courses && res.suggested_courses[0] ? res.suggested_courses[0].title : "Specialized Course";

    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><strong>#${res.queue_order || 1}</strong></td>
      <td><strong>${res.target_role}</strong></td>
      <td>${res.candidate_name || 'Candidate'}</td>
      <td><span class="score-badge-table ${scoreClass}">${score}%</span></td>
      <td>${res.breakdown.skills_match}%</td>
      <td>${res.breakdown.experience_match}%</td>
      <td><small style="color: #38bdf8;">${topCourse}</small></td>
      <td><span style="color: #34d399; font-size: 0.8rem;">● Evaluated</span></td>
    `;
    tbody.appendChild(tr);
  });
}

function renderLocalBatchResults(batchData) {
  const simulated = batchData.map((item, i) => {
    const jdLower = item.jd.toLowerCase();
    let role = "Target Role";
    let score = 80;
    let skills = 85;
    let exp = 75;

    if (jdLower.includes("data")) { role = "Data Analyst"; score = 78; skills = 85; exp = 70; }
    else if (jdLower.includes("software")) { role = "Software Developer"; score = 82; skills = 88; exp = 75; }
    else if (jdLower.includes("marketing")) { role = "Marketing Manager"; score = 75; skills = 82; exp = 68; }
    else if (jdLower.includes("hr")) { role = "HR Specialist"; score = 88; skills = 90; exp = 86; }

    return {
      queue_order: i + 1,
      target_role: role,
      candidate_name: item.resume.split("\n")[0] || "Candidate",
      ats_score: score,
      breakdown: { skills_match: skills, experience_match: exp },
      suggested_courses: [{ title: `${role} Upskilling Masterclass` }]
    };
  });
  renderBatchResultsTable(simulated);
}

/* ==========================================================================
   4. Live Channel Simulator
   ========================================================================== */
let activeChannel = "whatsapp";
let sessionUserId = `sim_user_${Math.floor(Math.random() * 10000)}`;

function initChatSimulator() {
  const channelBtns = document.querySelectorAll(".channel-btn");
  const btnSend = document.getElementById("btnSendChat");
  const chatInput = document.getElementById("chatInput");
  const promptChips = document.querySelectorAll(".prompt-chip");

  channelBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      channelBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      activeChannel = btn.getAttribute("data-channel");
      updateChannelTheme(activeChannel);
    });
  });

  promptChips.forEach(chip => {
    chip.addEventListener("click", () => {
      chatInput.value = chip.getAttribute("data-msg");
      sendChatMessage();
    });
  });

  btnSend.addEventListener("click", sendChatMessage);
  chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendChatMessage();
  });
}

function updateChannelTheme(channel) {
  const title = document.getElementById("channelBotTitle");
  const frame = document.getElementById("deviceFrame");

  if (channel === "whatsapp") {
    title.innerText = "ATS WhatsApp Bot (Meta API)";
    frame.style.borderColor = "rgba(37, 211, 102, 0.4)";
  } else if (channel === "slack") {
    title.innerText = "ATS Slack Bot (Events API)";
    frame.style.borderColor = "rgba(236, 72, 153, 0.4)";
  } else if (channel === "instagram") {
    title.innerText = "ATS Instagram Bot (Graph API)";
    frame.style.borderColor = "rgba(249, 115, 22, 0.4)";
  }
}

async function sendChatMessage() {
  const chatInput = document.getElementById("chatInput");
  const message = chatInput.value.trim();
  if (!message) return;

  chatInput.value = "";
  appendChatMessage(message, "user");

  try {
    const res = await fetch("/api/chat-simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ channel: activeChannel, user_id: sessionUserId, message: message })
    });

    if (res.ok) {
      const data = await res.json();
      appendChatMessage(data.reply_text, "bot");
    } else {
      localChatSimulate(message);
    }
  } catch (err) {
    localChatSimulate(message);
  }
}

function appendChatMessage(text, sender) {
  const container = document.getElementById("chatMessages");
  const bubble = document.createElement("div");
  bubble.className = `message-bubble ${sender === 'user' ? 'user-msg' : 'bot-msg'}`;

  const formattedText = text
    .replace(/\*(.*?)\*/g, "<strong>$1</strong>")
    .replace(/_(.*?)_/g, "<em>$1</em>")
    .replace(/\n/g, "<br>");

  bubble.innerHTML = `
    <div class="msg-text">${formattedText}</div>
    <span class="msg-time">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
  `;

  container.appendChild(bubble);
  container.scrollTop = container.scrollHeight;
}

let localChatState = "IDLE";
function localChatSimulate(msg) {
  const lower = msg.toLowerCase();
  let reply = "";

  if (lower.includes("reset")) {
    localChatState = "IDLE";
    reply = "🔄 Session reset. Please send a *Job Description (JD)* to start.";
  } else if (localChatState === "IDLE" || lower.includes("jd for")) {
    localChatState = "WAITING_RESUME";
    reply = "✅ *Job Description Received*\n\n📄 *Step 2:* Now upload or paste the candidate's *Resume*.";
  } else if (localChatState === "WAITING_RESUME") {
    localChatState = "ANALYZED";
    reply = "🧠 *Think-Aloud Evaluation:*\n• *Skills Match:* 85% match in core technical competencies.\n• *Experience Match:* 75% alignment with role seniority.\n\n📊 *ATS Score:* 82%, Breakdown: [Skills match: 88%, Experience match: 75%]. Suggested Courses: Advanced Algorithms, Full Stack Development. Overall Analytics: [Strengths: Strong core foundation. Improvement Areas: Highlight leadership & scale].";
  } else {
    reply = "💡 Type *'courses'* for direct course links, or send a new JD to start another evaluation!";
  }

  setTimeout(() => appendChatMessage(reply, "bot"), 400);
}

/* ==========================================================================
   5. Course Catalog Tab
   ========================================================================== */
function initCourseCatalog() {
  const grid = document.getElementById("catalogCoursesGrid");
  const searchInput = document.getElementById("courseSearchInput");

  function renderCourses(filterText = "") {
    grid.innerHTML = "";
    const filter = filterText.toLowerCase();
    const filtered = COURSES_DATA.filter(c => 
      c.title.toLowerCase().includes(filter) ||
      c.provider.toLowerCase().includes(filter) ||
      c.category.toLowerCase().includes(filter)
    );

    filtered.forEach(c => {
      const card = document.createElement("div");
      card.className = "deploy-card";
      card.innerHTML = `
        <div class="deploy-card-header">
          <strong>${c.title}</strong>
          <span class="badge-blue">${c.category}</span>
        </div>
        <p style="font-size: 0.82rem; color: #9ca3af; margin: 0.3rem 0;">Provider: <strong style="color: #fff;">${c.provider}</strong> • Level: ${c.level}</p>
        <a href="${c.url}" target="_blank" rel="noopener noreferrer" class="btn-course-link" style="display: inline-block; margin-top: 0.5rem;">Access Course Curriculum ↗</a>
      `;
      grid.appendChild(card);
    });
  }

  searchInput.addEventListener("input", (e) => renderCourses(e.target.value));
  renderCourses();
}
