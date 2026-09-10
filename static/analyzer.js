/**
 * Analyzer Page Controller
 * Supports: multi-resume PDF upload, text paste, parallel ATS analysis, ranked output
 */
(function () {
  if (typeof pdfjsLib !== 'undefined') {
    pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
  }

  // Resumes registry: [{ name, text, status }]
  const resumes = [];

  // ── Preset Loader ────────────────────────────────────────────────────────────
  const sampleSelect = document.getElementById('sampleSelect');

  function loadPreset(key) {
    const p = PRESETS[key];
    if (!p) return;
    document.getElementById('jdInput').value = p.jd;
    // Add sample resume to the queue
    addResumeToQueue(`Sample: ${key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}`, p.resume);
  }

  sampleSelect.addEventListener('change', e => {
    resumes.length = 0;
    renderQueue();
    loadPreset(e.target.value);
  });

  document.getElementById('btnLoadDemo').addEventListener('click', () => {
    resumes.length = 0;
    renderQueue();
    sampleSelect.value = 'data_analyst';
    loadPreset('data_analyst');
    // Add a few more sample resumes for demo comparison
    addResumeToQueue('Sample: Software Dev', PRESETS.software_dev.resume);
    addResumeToQueue('Sample: HR Specialist', PRESETS.hr_specialist.resume);
    runAnalysis();
  });

  loadPreset('data_analyst');

  // ── File Upload ────────────────────────────────────────────────────────────
  const fileInput = document.getElementById('resumeFiles');
  const uploadZone = document.getElementById('uploadZone');

  uploadZone.addEventListener('dragover', e => { e.preventDefault(); uploadZone.classList.add('drag-over'); });
  uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('drag-over'));
  uploadZone.addEventListener('drop', async e => {
    e.preventDefault();
    uploadZone.classList.remove('drag-over');
    await handleFiles(e.dataTransfer.files);
  });
  fileInput.addEventListener('change', async e => {
    await handleFiles(e.target.files);
    e.target.value = ''; // reset so same file can be re-selected
  });

  async function handleFiles(fileList) {
    for (const file of fileList) {
      const name = file.name.replace(/\.[^.]+$/, '');
      const idx = addResumeToQueue(name, null, 'parsing');
      try {
        let text = '';
        if (file.type === 'application/pdf' || file.name.endsWith('.pdf')) {
          text = await parsePDF(file);
        } else {
          text = await readText(file);
        }
        resumes[idx].text = text;
        resumes[idx].status = 'done';
      } catch (err) {
        resumes[idx].status = 'error';
        resumes[idx].text = '';
      }
      renderQueue();
    }
  }

  async function parsePDF(file) {
    const buf = await file.arrayBuffer();
    const pdf = await pdfjsLib.getDocument({ data: buf }).promise;
    let text = '';
    for (let i = 1; i <= pdf.numPages; i++) {
      const page = await pdf.getPage(i);
      const content = await page.getTextContent();
      text += content.items.map(it => it.str).join(' ') + '\n';
    }
    return text.trim();
  }

  function readText(file) {
    return new Promise((res, rej) => {
      const reader = new FileReader();
      reader.onload = e => res(e.target.result);
      reader.onerror = rej;
      reader.readAsText(file);
    });
  }

  // ── Resume Queue Management ──────────────────────────────────────────────
  function addResumeToQueue(name, text, status = 'done') {
    const idx = resumes.length;
    resumes.push({ name, text: text || '', status });
    renderQueue();
    return idx;
  }

  function removeResume(idx) {
    resumes.splice(idx, 1);
    renderQueue();
  }

  function renderQueue() {
    const queue = document.getElementById('resumeQueue');
    const countBadge = document.getElementById('resumeCount');
    countBadge.textContent = `${resumes.length} loaded`;

    if (resumes.length === 0) {
      queue.innerHTML = '';
      return;
    }

    queue.innerHTML = resumes.map((r, i) => `
      <div class="resume-item">
        <span class="resume-item-icon">📄</span>
        <span class="resume-item-name" title="${r.name}">${r.name}</span>
        <span class="resume-item-status ${r.status}">
          ${r.status === 'parsing' ? '⏳ Parsing...' : r.status === 'done' ? '✅ Ready' : '❌ Error'}
        </span>
        <button class="btn-remove-resume" onclick="removeResume(${i})" title="Remove">✕</button>
      </div>
    `).join('');
  }
  window.removeResume = removeResume;

  // ── Paste Mode ────────────────────────────────────────────────────────────
  const pasteArea = document.getElementById('pasteArea');
  document.getElementById('btnAddPasteResume').addEventListener('click', () => {
    pasteArea.style.display = pasteArea.style.display === 'none' ? 'block' : 'none';
  });
  document.getElementById('btnCancelPaste').addEventListener('click', () => {
    pasteArea.style.display = 'none';
    document.getElementById('pasteResumeInput').value = '';
    document.getElementById('pasteNameInput').value = '';
  });
  document.getElementById('btnConfirmPaste').addEventListener('click', () => {
    const name = document.getElementById('pasteNameInput').value.trim() || `Candidate ${resumes.length + 1}`;
    const text = document.getElementById('pasteResumeInput').value.trim();
    if (!text) { showToast('⚠️ Please paste resume text.'); return; }
    addResumeToQueue(name, text, 'done');
    document.getElementById('pasteResumeInput').value = '';
    document.getElementById('pasteNameInput').value = '';
    pasteArea.style.display = 'none';
    showToast(`✅ "${name}" added to queue.`);
  });

  // ── Analyze All ────────────────────────────────────────────────────────────
  document.getElementById('btnAnalyze').addEventListener('click', runAnalysis);

  function runAnalysis() {
    const jdText = document.getElementById('jdInput').value.trim();
    const readyResumes = resumes.filter(r => r.status === 'done' && r.text.trim());

    if (!jdText) { showToast('⚠️ Please provide a Job Description.'); return; }
    if (readyResumes.length === 0) { showToast('⚠️ Please upload or paste at least one resume.'); return; }

    const btn = document.getElementById('btnAnalyze');
    btn.disabled = true;
    btn.innerHTML = `<span id="spinIcon" style="display:inline-block; animation:spin 1s linear infinite;">⏳</span> Analyzing ${readyResumes.length} resume${readyResumes.length > 1 ? 's' : ''}...`;

    setTimeout(() => {
      // Analyze each resume
      const results = readyResumes.map(r => ({
        ...analyzeATS(jdText, r.text),
        filename: r.name
      }));

      // Sort by ATS score descending
      results.sort((a, b) => b.atsScore - a.atsScore);

      // Render appropriate view
      if (results.length === 1) {
        renderSingleResult(results[0]);
      } else {
        renderMultiResults(results);
      }

      btn.disabled = false;
      btn.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg> Analyze All Resumes`;

      document.getElementById('resultsPanel').scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 500);
  }

  // ── Render: Multi-Resume Ranked View ──────────────────────────────────────
  function renderMultiResults(results) {
    const panel = document.getElementById('resultsPanel');

    const tableRows = results.map((r, i) => {
      const rank = i + 1;
      const rankClass = rank === 1 ? 'rank-1' : rank === 2 ? 'rank-2' : rank === 3 ? 'rank-3' : 'rank-other';
      const scoreChipClass = r.atsScore >= 80 ? 'chip-green' : r.atsScore >= 65 ? 'chip-amber' : 'chip-red';
      const topCourse = r.courses[0];
      return `
        <tr>
          <td><div class="rank-no ${rankClass}">${rank}</div></td>
          <td>
            <strong style="display:block;">${r.candidate}</strong>
            <small style="color:var(--text-muted); font-size:0.75rem;">${r.filename}</small>
          </td>
          <td><span class="chip ${scoreChipClass}" style="font-size:0.88rem; padding: 0.3rem 0.75rem;">${r.atsScore}%</span></td>
          <td>
            <div style="font-size:0.82rem; margin-bottom:0.2rem; color:var(--text-muted);">Skills</div>
            <div class="bar-track" style="width:90px;"><div class="bar-fill bar-indigo" style="width:${r.skillsPct}%"></div></div>
            <div style="font-size:0.75rem; color:#a5b4fc; margin-top:0.15rem;">${r.skillsPct}%</div>
          </td>
          <td>
            <div style="font-size:0.82rem; margin-bottom:0.2rem; color:var(--text-muted);">Experience</div>
            <div class="bar-track" style="width:90px;"><div class="bar-fill bar-emerald" style="width:${r.expPct}%"></div></div>
            <div style="font-size:0.75rem; color:#34d399; margin-top:0.15rem;">${r.expPct}%</div>
          </td>
          <td style="max-width:180px;">
            ${topCourse
              ? `<a href="${topCourse.url}" target="_blank" style="color:#67e8f9; font-size:0.78rem; line-height:1.4; display:block;">${topCourse.title}</a>`
              : '<span style="color:var(--text-dim); font-size:0.78rem;">—</span>'}
          </td>
          <td>
            <button class="btn-sm scorecard-expand" onclick="toggleDetail(${i})">View Details</button>
          </td>
        </tr>
        <tr id="detailRow-${i}" style="display:none;">
          <td colspan="7" style="padding: 0.25rem 1rem 1rem;">
            ${buildDetailCard(r)}
          </td>
        </tr>
      `;
    }).join('');

    panel.innerHTML = `
      <div class="table-wrap-card">
        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:1.25rem;">
          <div class="section-title">
            🏆 Ranked Results
            <span class="count-badge">${results.length} candidates</span>
          </div>
          <button class="btn-sm" onclick="copyAllOutput()">📋 Copy All Outputs</button>
        </div>
        <div class="overflow-x">
          <table class="comparison-table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>Candidate</th>
                <th>ATS Score</th>
                <th>Skills Match</th>
                <th>Experience</th>
                <th>Top Course</th>
                <th></th>
              </tr>
            </thead>
            <tbody>${tableRows}</tbody>
          </table>
        </div>
      </div>

      <!-- Standard outputs for all -->
      <div class="table-wrap-card" style="margin-top:1rem;">
        <div class="section-title" style="margin-bottom:1rem;">📋 Standard ATS Outputs (All Candidates)</div>
        <div id="allOutputs" style="display:flex;flex-direction:column;gap:0.75rem;">
          ${results.map((r, i) => `
            <div style="background:#020408; border:1px solid rgba(255,255,255,0.07); border-radius:10px; padding:0.85rem; position:relative;">
              <div style="font-size:0.72rem; font-weight:700; color:#818cf8; text-transform:uppercase; letter-spacing:0.07em; margin-bottom:0.35rem;">#${i+1} — ${r.candidate} (${r.filename})</div>
              <code style="font-family:monospace; font-size:0.8rem; color:#67e8f9; white-space:pre-wrap; word-break:break-word;">${r.formattedOutput}</code>
            </div>
          `).join('')}
        </div>
      </div>
    `;

    // Store results for copy
    window._allResults = results;
  }

  window.toggleDetail = function (idx) {
    const row = document.getElementById(`detailRow-${idx}`);
    const btn = row.previousElementSibling.querySelector('.scorecard-expand');
    if (row.style.display === 'none') {
      row.style.display = 'table-row';
      btn.textContent = 'Hide Details';
    } else {
      row.style.display = 'none';
      btn.textContent = 'View Details';
    }
  };

  function buildDetailCard(r) {
    return `
      <div class="scorecard-detail">
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:1rem;">
          <div>
            <div class="think-block-title" style="font-size:0.72rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:#818cf8; margin-bottom:0.6rem;">🧠 Think-Aloud</div>
            <div class="mini-think"><strong>Role:</strong> ${r.thinkAloud.role}</div>
            <div class="mini-think" style="margin-top:0.4rem;"><strong>Skills:</strong> ${r.thinkAloud.skills}</div>
            <div class="mini-think" style="margin-top:0.4rem;"><strong>Experience:</strong> ${r.thinkAloud.experience}</div>
            <div class="mini-think" style="margin-top:0.4rem;"><strong>Improve:</strong> ${r.thinkAloud.improve}</div>
          </div>
          <div>
            <div class="think-block-title" style="font-size:0.72rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:#818cf8; margin-bottom:0.6rem;">🎓 Courses</div>
            ${r.courses.map(c => `
              <div style="margin-bottom:0.4rem;">
                <a href="${c.url}" target="_blank" style="color:#67e8f9; font-size:0.82rem; font-weight:600;">${c.title}</a>
                <div style="font-size:0.72rem; color:var(--text-muted);">${c.provider}</div>
              </div>
            `).join('')}
            <div style="margin-top:0.6rem;">
              <div style="font-size:0.72rem; color:var(--text-dim); margin-bottom:0.35rem;">SKILL GAPS</div>
              <div style="display:flex;flex-wrap:wrap;gap:0.3rem;">${r.missing.slice(0,6).map(s=>`<span class="chip chip-red" style="font-size:0.7rem;">${s}</span>`).join('') || '<span style="font-size:0.78rem;color:var(--text-dim);">None critical</span>'}</div>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  window.copyAllOutput = function () {
    if (!window._allResults) return;
    const text = window._allResults.map((r, i) => `[${i+1}] ${r.candidate}\n${r.formattedOutput}`).join('\n\n');
    navigator.clipboard.writeText(text).then(() => showToast('✅ All outputs copied!'));
  };

  // ── Render: Single Resume View ─────────────────────────────────────────────
  function renderSingleResult(r) {
    const circumference = 2 * Math.PI * 37;
    const offset = circumference - (r.atsScore / 100) * circumference;
    const statusClass = r.atsScore >= 80 ? 'chip-green' : r.atsScore >= 65 ? 'chip-amber' : 'chip-red';
    const statusLabel = r.atsScore >= 80 ? '🌟 High Match' : r.atsScore >= 65 ? '⚡ Strong Match' : '⚠️ Moderate Match';

    document.getElementById('resultsPanel').innerHTML = `
      <div style="display:flex;flex-direction:column;gap:1rem;">

        <!-- Scorecard Row -->
        <div class="card">
          <div class="card-title">📊 ATS Scorecard — ${r.candidate}</div>
          <div style="display:flex; align-items:center; gap:1.5rem; margin-bottom:1rem;">
            <div class="score-ring-wrap">
              <div class="score-ring">
                <svg viewBox="0 0 88 88">
                  <defs>
                    <linearGradient id="scoreGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stop-color="#6366f1"/>
                      <stop offset="100%" stop-color="#a855f7"/>
                    </linearGradient>
                  </defs>
                  <circle class="ring-bg" cx="44" cy="44" r="37"/>
                  <circle class="ring-fill" id="ringFill" cx="44" cy="44" r="37" stroke-dasharray="232.5" stroke-dashoffset="${offset}"/>
                </svg>
                <div class="ring-value">${r.atsScore}</div>
              </div>
              <div class="ring-label">ATS Score</div>
            </div>
            <div style="flex:1;">
              <span class="chip ${statusClass}" style="margin-bottom:0.5rem; display:inline-block;">${statusLabel}</span>
              <div style="font-size:0.8rem; color:var(--text-muted);">${r.role} · ${r.candidate}</div>
              <div class="progress-bar-row" style="margin-top:0.75rem; margin-bottom:0.5rem;">
                <div class="bar-meta"><span style="color:var(--text-muted);font-size:0.8rem;">Skills</span><strong style="font-size:0.8rem;">${r.skillsPct}%</strong></div>
                <div class="bar-track"><div class="bar-fill bar-indigo" style="width:${r.skillsPct}%"></div></div>
              </div>
              <div class="progress-bar-row">
                <div class="bar-meta"><span style="color:var(--text-muted);font-size:0.8rem;">Experience</span><strong style="font-size:0.8rem;">${r.expPct}%</strong></div>
                <div class="bar-track"><div class="bar-fill bar-emerald" style="width:${r.expPct}%"></div></div>
              </div>
            </div>
          </div>

          <!-- Standard Output -->
          <div style="background:#020408; border:1px solid rgba(255,255,255,0.07); border-radius:10px; padding:0.85rem; position:relative;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.35rem;">
              <span style="font-size:0.72rem;font-weight:700;color:#818cf8;text-transform:uppercase;letter-spacing:0.07em;">Standard Output</span>
              <button class="btn-sm" onclick="navigator.clipboard.writeText(document.getElementById('stdOut').textContent).then(()=>showToast('✅ Copied!'))">📋 Copy</button>
            </div>
            <code id="stdOut" style="font-family:monospace;font-size:0.8rem;color:#67e8f9;white-space:pre-wrap;word-break:break-word;">${r.formattedOutput}</code>
          </div>
        </div>

        <div class="single-result-grid">
          <!-- Think Aloud -->
          <div class="card">
            <div class="card-title">🧠 Think-Aloud Analysis</div>
            <div class="think-block">
              <div class="think-block-title">Step-by-Step Reasoning</div>
              <div class="think-item"><div class="think-dot"></div><div><strong>Role:</strong> ${r.thinkAloud.role}</div></div>
              <div class="think-item"><div class="think-dot"></div><div><strong>Skills:</strong> ${r.thinkAloud.skills}</div></div>
              <div class="think-item"><div class="think-dot"></div><div><strong>Experience:</strong> ${r.thinkAloud.experience}</div></div>
              <div class="think-item"><div class="think-dot"></div><div><strong>Strategy:</strong> ${r.thinkAloud.improve}</div></div>
            </div>
          </div>

          <!-- Skill Gaps -->
          <div class="card">
            <div class="card-title">📊 Skill Analysis</div>
            <div class="section-label">✅ Matched Skills</div>
            <div class="skill-chips-wrap">${r.matched.slice(0,10).map(s=>`<span class="chip chip-green">${s}</span>`).join('') || '<span style="color:var(--text-dim);font-size:0.8rem;">None</span>'}</div>
            <div class="divider"></div>
            <div class="section-label">❌ Missing Skills (Gaps)</div>
            <div class="skill-chips-wrap">${r.missing.slice(0,8).map(s=>`<span class="chip chip-red">${s}</span>`).join('') || '<span style="color:var(--text-dim);font-size:0.8rem;">No critical gaps</span>'}</div>
          </div>
        </div>

        <!-- Courses -->
        <div class="card">
          <div class="card-title">🎓 Recommended Upskilling Courses</div>
          <div style="display:flex;flex-direction:column;gap:0.6rem;">
            ${r.courses.map(c => `
              <div class="course-card">
                <div class="course-card-info">
                  <div class="course-card-title">${c.title}</div>
                  <div class="course-card-meta">${c.provider} · ${c.category}</div>
                </div>
                <a href="${c.url}" target="_blank" rel="noopener" class="btn-course">View ↗</a>
              </div>
            `).join('')}
          </div>
        </div>
      </div>
    `;
  }

  // ── Spin animation ─────────────────────────────────────────────────────────
  const style = document.createElement('style');
  style.textContent = '@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }';
  document.head.appendChild(style);

})();
