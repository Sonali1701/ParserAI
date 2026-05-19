/* ── Tab switching ──────────────────────────────────────── */
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', e => {
        e.preventDefault();
        switchTab(btn.getAttribute('data-tab'));
    });
});

function switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.getElementById(tabName).classList.add('active');
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
}

/* ── File input labels ──────────────────────────────────── */
document.getElementById('resume').addEventListener('change', e => {
    const name = e.target.files[0]?.name || '';
    document.getElementById('resumeFilename').textContent = name;
    document.getElementById('resumeZone').classList.toggle('has-file', !!name);
});

document.getElementById('jd').addEventListener('change', e => {
    const name = e.target.files[0]?.name || '';
    document.getElementById('jdFilename').textContent = name;
});

/* ── Loading steps animation ────────────────────────────── */
let stepTimer = null;

function startLoadingSteps() {
    const steps = document.querySelectorAll('.loading-step');
    let current = 0;

    steps.forEach(s => s.className = 'loading-step pending');

    function advance() {
        if (current < steps.length) {
            if (current > 0) steps[current - 1].className = 'loading-step done';
            steps[current].className = 'loading-step active';
            current++;
            const delays = [0, 2000, 5000, 10000];
            if (current < steps.length) {
                stepTimer = setTimeout(advance, delays[current] || 3000);
            }
        }
    }
    advance();
}

function stopLoadingSteps() {
    clearTimeout(stepTimer);
    document.querySelectorAll('.loading-step').forEach(s => s.className = 'loading-step done');
}

/* ── Section visibility ─────────────────────────────────── */
function showSection(id) {
    ['uploadSection', 'loading', 'results'].forEach(s => {
        document.getElementById(s).classList.add('hidden');
    });
    document.getElementById(id).classList.remove('hidden');
}

/* ── Form submit ────────────────────────────────────────── */
document.getElementById('analyzeForm').addEventListener('submit', async e => {
    e.preventDefault();

    const resumeFile = document.getElementById('resume').files[0];
    const jdFile     = document.getElementById('jd').files[0];
    const jdText     = document.getElementById('jdText').value.trim();

    if (!resumeFile) { showError('Please upload a resume.'); return; }
    if (!jdFile && !jdText) { showError('Please upload or paste a job description.'); return; }

    hideError();
    showSection('loading');
    startLoadingSteps();

    const formData = new FormData();
    formData.append('resume', resumeFile);
    if (jdFile) {
        formData.append('jd', jdFile);
    } else {
        formData.append('jd', new Blob([jdText], { type: 'text/plain' }), 'job_description.txt');
    }

    try {
        const response = await fetch('/api/analyze', { method: 'POST', body: formData });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Analysis failed');
        stopLoadingSteps();
        displayResults(data);
    } catch (err) {
        stopLoadingSteps();
        showSection('uploadSection');
        showError(err.message);
    }
});

/* ── Main display ───────────────────────────────────────── */
function displayResults(data) {
    const score        = data.score;
    const candidate    = data.candidate_profile;
    const jdReqs       = data.jd_requirements;
    const domain       = data.domain;
    const fitCategory  = data.fit_category;
    const skillAnalysis = data.skill_analysis;
    const expAnalysis  = data.experience_analysis;
    const smartAnalysis = data.smart_analysis;

    /* Banner */
    document.getElementById('fitSummary').textContent =
        candidate.name || 'Candidate';
    document.getElementById('fitLevel').textContent =
        `${candidate.job_title || ''} · ${candidate.years_relevant_experience || 0} years`;

    /* Score ring */
    const pct = Math.round(score.overall_score);
    document.getElementById('scoreValue').textContent = pct;
    animateRing(pct, fitCategory.color);

    /* Verdict badge */
    const verdictEl = document.getElementById('fitBadgeSection');
    verdictEl.innerHTML = `
        <div class="verdict-badge ${fitCategory.color}">${fitCategory.level}</div>
        <div class="verdict-rec">${fitCategory.recommendation}</div>
    `;

    /* Metric tiles */
    setMetric('skill',  Math.round(score.skill_match.score),
        `${score.skill_match.exact_matches}/${score.skill_match.total_required} exact`);
    setMetric('exp',    Math.round(score.experience_match.score),
        `${score.experience_match.candidate_years} yrs · req ${score.experience_match.required_years}`);
    setMetric('edu',    Math.round(score.education_match.score),
        `${score.education_match.field_matches} field match${score.education_match.field_matches !== 1 ? 'es' : ''}`);
    const certMatch = score.certification_match || {};
    setMetric('cert',   Math.round(certMatch.score || 0),
        certMatch.missing?.length ? `${certMatch.missing.length} missing` : 'All present');

    /* Skills chips */
    renderChips('matchedSkills', score.skill_match.matched || [], 'matched');
    renderChips('missingSkills', score.skill_match.missing || [], 'missing');

    /* Cert chips */
    renderChips('matchedCerts', certMatch.matched || [], 'matched');
    renderChips('missingCerts', certMatch.missing || [], 'missing');

    /* Education fields */
    renderChips('matchedFields', [
        ...(score.education_match.field_matches > 0 ? ['Nursing'] : []),
        ...(score.education_match.degree_matches > 0 ? ['BSN / Degree'] : []),
    ], 'neutral');

    /* Experience recency */
    const recencyEl = document.getElementById('expRecency');
    if (recencyEl && score.experience_match.recency_note) {
        recencyEl.textContent = score.experience_match.recency_note;
    }

    /* Intelligent analysis */
    displayIntelligentAnalysis(candidate, jdReqs, domain, skillAnalysis, expAnalysis, smartAnalysis, score);

    showSection('results');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/* ── Score ring animation ───────────────────────────────── */
function animateRing(score, colorClass) {
    const arc = document.getElementById('scoreArc');
    if (!arc) return;
    const circumference = 326.73;
    const offset = circumference * (1 - score / 100);
    arc.style.strokeDashoffset = circumference; // reset
    arc.className = 'score-arc';
    if (colorClass) arc.classList.add(colorClass + '-arc');
    requestAnimationFrame(() => {
        requestAnimationFrame(() => { arc.style.strokeDashoffset = offset; });
    });
}

/* ── Metric tile setter ─────────────────────────────────── */
function setMetric(prefix, score, subText) {
    const el = document.getElementById(prefix + 'Score');
    const bar = document.getElementById(prefix + 'Bar');
    const sub = document.getElementById(prefix + 'Explanation') ||
                document.getElementById(prefix + 'Insight');

    if (el)  el.textContent = score + '%';
    if (sub) sub.textContent = subText || '';

    if (bar) {
        bar.className = 'metric-bar-fill';
        if (score >= 85) bar.classList.add('fill-green');
        else if (score < 50) bar.classList.add('fill-red');
        else if (score < 70) bar.classList.add('fill-orange');
        setTimeout(() => { bar.style.width = score + '%'; }, 60);
    }
}

/* ── Chip renderer ──────────────────────────────────────── */
function renderChips(elementId, items, type) {
    const container = document.getElementById(elementId);
    if (!container) return;
    container.innerHTML = '';
    if (!items || items.length === 0) {
        const span = document.createElement('span');
        span.style.cssText = 'color:var(--text-light);font-size:.8rem;';
        span.textContent = type === 'missing' ? 'None' : '—';
        container.appendChild(span);
        return;
    }
    items.forEach(item => {
        const span = document.createElement('span');
        span.className = `chip-${type}`;
        span.textContent = item;
        container.appendChild(span);
    });
}

/* ── Intelligent analysis ───────────────────────────────── */
function displayIntelligentAnalysis(candidate, jdReqs, domain, skillAnalysis, expAnalysis, smartAnalysis, scoreData) {
    const section = document.getElementById('intelligentAnalysisSection');

    /* Domain tag */
    document.getElementById('domainInfo').textContent =
        `${domain} · ${jdReqs.role_level || '—'} · ${jdReqs.required_experience_years || 0} yrs req.`;

    /* Candidate profile */
    const profileDiv = document.getElementById('candidateProfile');
    profileDiv.innerHTML = `
        <div class="profile-grid">
            <div class="profile-row">
                <span class="profile-key">Name</span>
                <span class="profile-val">${candidate.name || '—'}</span>
            </div>
            <div class="profile-row">
                <span class="profile-key">Level</span>
                <span class="profile-val">${capitalize(candidate.current_role_level || '—')}</span>
            </div>
            <div class="profile-row full">
                <span class="profile-key">Current Title</span>
                <span class="profile-val">${candidate.job_title || '—'}</span>
            </div>
            <div class="profile-row">
                <span class="profile-key">Experience</span>
                <span class="profile-val">${candidate.years_relevant_experience || 0} years</span>
            </div>
            <div class="profile-row">
                <span class="profile-key">Trajectory</span>
                <span class="profile-val">${capitalize(candidate.career_trajectory || '—')}</span>
            </div>
            <div class="profile-row full">
                <span class="profile-key">Industries</span>
                <span class="profile-val">${(candidate.industries_experience || []).slice(0, 3).join(', ') || '—'}</span>
            </div>
        </div>
    `;

    /* Smart assessment */
    const smartDiv = document.getElementById('smartAnalysisDetails');
    smartDiv.innerHTML = '';

    const header = document.createElement('div');
    header.className = 'smart-header';
    header.innerHTML = `
        <span class="fit-badge-inline ${fitBadgeClass(smartAnalysis.overall_fit)}">${smartAnalysis.overall_fit || 'N/A'}</span>
        <span class="confidence-tag">Confidence: ${smartAnalysis.confidence || '—'}</span>
        <span class="career-fit-tag">Career Fit: ${smartAnalysis.career_fit || '—'}</span>
    `;
    smartDiv.appendChild(header);

    renderBulletBlock(smartDiv, 'Strengths', smartAnalysis.strengths || [], 'matched-label', '✓');
    renderBulletBlock(smartDiv, 'Gaps', smartAnalysis.gaps || [], 'missing-label', '✗');
    renderBulletBlock(smartDiv, 'Risk Flags', smartAnalysis.risk_flags || [], 'risk-label', '⚠');

    if (smartAnalysis.recent_domain_experience) {
        const note = document.createElement('p');
        note.className = 'recency-note';
        note.style.marginTop = '12px';
        note.textContent = smartAnalysis.recent_domain_experience;
        smartDiv.appendChild(note);
    }

    /* Skill analysis breakdown (LLM) */
    const skillDiv = document.getElementById('skillAnalysisDetails');
    skillDiv.innerHTML = '';
    renderBulletBlock(skillDiv, 'Exact Matches',   skillAnalysis.exact_matches       || [], 'matched-label', '✓');
    renderBulletBlock(skillDiv, 'Equivalent',       skillAnalysis.equivalent_matches  || [], 'matched-label', '~');
    renderBulletBlock(skillDiv, 'Transferable',     skillAnalysis.transferable_skills || [], null, '→');
    renderBulletBlock(skillDiv, 'Missing Critical', skillAnalysis.missing_critical    || [], 'missing-label', '✗');
    if (skillAnalysis.analysis) {
        const note = document.createElement('p');
        note.style.cssText = 'font-size:.82rem;color:var(--text-secondary);margin-top:10px;font-style:italic;';
        note.textContent = skillAnalysis.analysis;
        skillDiv.appendChild(note);
    }

    /* Experience fit details */
    const expDiv = document.getElementById('experienceAnalysisDetails');
    expDiv.innerHTML = '';
    const expItems = [
        expAnalysis.years_assessment,
        expAnalysis.progression_fit,
        expAnalysis.domain_knowledge,
        expAnalysis.role_readiness ? `Role Readiness: ${expAnalysis.role_readiness}` : null,
    ].filter(Boolean);
    expItems.forEach(item => {
        const row = document.createElement('div');
        row.className = 'exp-bullet';
        row.innerHTML = `<span class="exp-bullet-dot"></span><span>${item}</span>`;
        expDiv.appendChild(row);
    });
    if (expAnalysis.recommendation) {
        const rec = document.createElement('p');
        rec.style.cssText = 'font-size:.82rem;color:var(--text-secondary);margin-top:10px;font-style:italic;';
        rec.textContent = expAnalysis.recommendation;
        expDiv.appendChild(rec);
    }

    /* Improvements */
    const improvEl = document.getElementById('improvements');
    if (improvEl) {
        improvEl.innerHTML = '';

        const certs  = (scoreData?.certification_match?.missing || []);
        const skills = (scoreData?.skill_match?.missing || []);

        const items = [];
        if (certs.length)  items.push({ area: 'Certifications', text: `Obtain: ${certs.slice(0,3).join(', ')}`, priority: 'High' });
        if (skills.length) items.push({ area: 'Skills', text: `Address gaps: ${skills.slice(0,3).join(', ')}`, priority: 'Medium' });
        if (!items.length) items.push({ area: 'No major gaps', text: 'Candidate meets all key requirements.', priority: 'N/A' });

        items.forEach(imp => {
            const div = document.createElement('div');
            div.className = 'improvement-item';
            div.innerHTML = `
                <span class="improvement-priority ${imp.priority.toLowerCase()}">${imp.priority}</span>
                <div class="improvement-body">
                    <div class="improvement-area">${imp.area}</div>
                    <div class="improvement-text">${imp.text}</div>
                </div>
            `;
            improvEl.appendChild(div);
        });
    }

    section.classList.remove('hidden');
}

/* ── Helpers ────────────────────────────────────────────── */
function renderBulletBlock(container, label, items, labelClass, prefix) {
    if (!items || items.length === 0) return;
    const heading = document.createElement('strong');
    heading.className = `bullet-section-label ${labelClass || ''}`;
    heading.textContent = label;
    container.appendChild(heading);
    items.slice(0, 8).forEach(item => {
        const row = document.createElement('div');
        row.className = 'bullet-item';
        row.innerHTML = `<span class="bullet-icon">${prefix}</span><span>${item}</span>`;
        container.appendChild(row);
    });
}

function fitBadgeClass(fit) {
    if (!fit) return 'grey';
    const f = fit.toLowerCase();
    if (f.includes('strong yes')) return 'green';
    if (f.includes('yes'))        return 'blue';
    if (f.includes('maybe'))      return 'orange';
    return 'red';
}

function capitalize(str) {
    return str ? str.charAt(0).toUpperCase() + str.slice(1) : str;
}

/* ── Reset ──────────────────────────────────────────────── */
function resetForm() {
    document.getElementById('analyzeForm').reset();
    document.getElementById('jdText').value = '';
    document.getElementById('resumeFilename').textContent = '';
    document.getElementById('jdFilename').textContent = '';
    document.getElementById('resumeZone').classList.remove('has-file');
    switchTab('jd-upload');
    showSection('uploadSection');
    hideError();
}

/* ── Error handling ─────────────────────────────────────── */
function showError(msg) {
    const el = document.getElementById('errorMessage');
    el.textContent = msg;
    el.classList.remove('hidden');
    setTimeout(() => el.classList.add('hidden'), 6000);
}

function hideError() {
    document.getElementById('errorMessage').classList.add('hidden');
}

