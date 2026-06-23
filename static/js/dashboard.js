/* Shared UI behaviour: sidebar toggle + theme toggle + fetch helper + chart theme */
(function () {
    const toggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');
    if (toggle && sidebar) {
        toggle.addEventListener('click', () => sidebar.classList.toggle('open'));
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 992 && !sidebar.contains(e.target) && !toggle.contains(e.target)) {
                sidebar.classList.remove('open');
            }
        });
    }

    // Theme toggle with localStorage persistence
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        // Load saved theme or default to dark
        const savedTheme = localStorage.getItem('theme') || 'dark';
        document.documentElement.setAttribute('data-theme', savedTheme);
        updateThemeIcon(savedTheme);

        themeToggle.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
        });
    }

    function updateThemeIcon(theme) {
        const icon = themeToggle?.querySelector('i');
        if (icon) {
            icon.className = theme === 'dark' ? 'bi bi-moon' : 'bi bi-sun';
        }
    }
})();

const CHART_COLORS = {
    purple: '#6d5dfc', blue: '#2f6bff', pink: '#c44dff', green: '#22c55e',
    red: '#ef4444', orange: '#f59e0b', teal: '#14b8a6', muted: '#9aa0c7',
};
const PALETTE = ['#6d5dfc', '#2f6bff', '#c44dff', '#22c55e', '#f59e0b',
    '#14b8a6', '#ef4444', '#9a8cff', '#5b8cff', '#2dd4bf', '#fbbf77', '#ff7a7a',
    '#4ade80', '#9cc0ff', '#ffd28a'];

if (window.Chart) {
    Chart.defaults.color = '#9aa0c7';
    Chart.defaults.borderColor = 'rgba(255,255,255,.08)';
    Chart.defaults.font.family = "'Poppins', sans-serif";
}

async function getJSON(url) {
    const r = await fetch(url, { headers: { 'X-Requested-With': 'fetch' } });
    if (!r.ok) throw new Error('Request failed: ' + url);
    return r.json();
}

/* ============ LIVE CHURN PREDICTION ============ */
function initLivePrediction(modelReady) {
    const form = document.getElementById('predictForm');
    const container = document.getElementById('resultContainer');
    if (!form || !container) return;

    const btn = document.getElementById('predictBtn');
    const indicator = document.getElementById('liveIndicator');
    let timer = null;
    let controller = null;

    function collect() {
        const data = {};
        new FormData(form).forEach((v, k) => { data[k] = v; });
        return data;
    }

    async function run() {
        if (!modelReady) {
            container.innerHTML = placeholderCard(
                'Model not trained yet. Train it on the Analytics page first.');
            return;
        }
        if (controller) controller.abort();
        controller = new AbortController();
        if (indicator) indicator.classList.add('pulsing');
        try {
            const res = await fetch('/api/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(collect()),
                signal: controller.signal,
            });
            if (!res.ok) throw new Error('predict failed');
            const data = await res.json();
            renderPrediction(container, data);
        } catch (e) {
            if (e.name !== 'AbortError') console.error(e);
        } finally {
            if (indicator) indicator.classList.remove('pulsing');
        }
    }

    function schedule() {
        clearTimeout(timer);
        timer = setTimeout(run, 350);
    }

    // live triggers
    form.addEventListener('input', schedule);
    form.addEventListener('change', schedule);
    // manual button: immediate prediction, no page reload
    form.addEventListener('submit', (e) => { e.preventDefault(); clearTimeout(timer); run(); });

    // initial prediction from default values
    run();
}

function placeholderCard(msg) {
    return `<div class="panel glass placeholder-panel">
        <i class="bi bi-graph-up-arrow big-icon"></i>
        <p class="muted">${msg}</p></div>`;
}

function renderPrediction(container, data) {
    const risk = (data.risk_level || 'Low').toLowerCase();
    const recs = (data.recommendations || []).map(r => `
        <div class="rec-card sev-${r.severity}">
            <i class="bi ${r.icon}"></i>
            <div><b>${r.title}</b><p>${r.action}</p></div>
        </div>`).join('');
    
    const reasons = (data.reasons || []).map(r => `
        <li><i class="bi bi-arrow-right text-info"></i> ${r}</li>
    `).join('');

    // Feature contributions for AI Explainability
    const contributions = (data.feature_contributions || []).map((c, i) => `
        <div class="d-flex justify-content-between align-items-center mb-2">
            <div>
                <small class="muted">${i + 1}. ${c.feature}</small>
                <div class="small text-muted">${c.value}</div>
            </div>
            <div class="text-end">
                <strong>${c.contribution}%</strong>
            </div>
        </div>
        <div class="progress mb-3" style="height: 6px;">
            <div class="progress-bar" style="width: ${c.contribution}%; background: var(--purple);"></div>
        </div>
    `).join('');

    // Health score display
    const healthScore = data.health_score || 0;
    const healthStatus = data.health_status || 'Unknown';
    const healthClass = healthStatus.toLowerCase();

    container.innerHTML = `
        <div class="panel glass result-panel risk-${risk} animate-up">
            <h3 class="panel-title">Prediction Result</h3>
            <div class="gauge-big" style="--p:${data.probability}">
                <div class="gauge-inner">
                    <div class="gauge-pct">${data.probability}%</div>
                    <div class="gauge-sub">churn probability</div>
                </div>
            </div>
            <div class="text-center mt-3">
                <div class="pred-label-big">${data.prediction_label}</div>
                <span class="risk-pill risk-${risk}">${data.risk_level} Risk</span>
            </div>
        </div>
        <div class="panel glass mt-3">
            <h3 class="panel-title"><i class="bi bi-heart-pulse"></i> Customer Health Score</h3>
            <div class="text-center">
                <div class="display-4 fw-bold health-${healthClass}">${healthScore}</div>
                <div class="muted">Health Score (0-100)</div>
                <span class="health-badge health-${healthClass}">${healthStatus}</span>
            </div>
        </div>
        <div class="panel glass mt-3">
            <h3 class="panel-title"><i class="bi bi-info-circle"></i> Key Risk Factors</h3>
            <ul class="reasons-list">${reasons || '<li class="muted">No specific risk factors identified</li>'}</ul>
        </div>
        <div class="panel glass mt-3">
            <h3 class="panel-title"><i class="bi bi-lightbulb"></i> Retention Recommendations</h3>
            <div class="rec-grid">${recs}</div>
        </div>
        <div class="panel glass mt-3">
            <h3 class="panel-title"><i class="bi bi-pie-chart"></i> AI Explainability - Risk Factor Breakdown</h3>
            <div class="row g-3">
                <div class="col-md-6">
                    <div id="contributionChart" style="height: 250px;"></div>
                </div>
                <div class="col-md-6">
                    ${contributions || '<p class="muted text-center">No contribution data available</p>'}
                </div>
            </div>
        </div>`;

    // animate the gauge fill
    const gauge = container.querySelector('.gauge-big');
    if (gauge) {
        gauge.style.setProperty('--p', '0');
        requestAnimationFrame(() => requestAnimationFrame(() => {
            gauge.style.setProperty('--p', data.probability);
        }));
    }

    // Render contribution chart
    if (data.feature_contributions && data.feature_contributions.length > 0) {
        renderContributionChart(data.feature_contributions);
    }
}

function renderContributionChart(contributions) {
    const ctx = document.getElementById('contributionChart');
    if (!ctx) return;

    const labels = contributions.map(c => c.feature);
    const data = contributions.map(c => c.contribution);
    const colors = [
        '#6d5dfc', '#2f6bff', '#c44dff', '#22c55e', '#f59e0b',
        '#14b8a6', '#ef4444', '#9a8cff'
    ];

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors.slice(0, labels.length),
                borderWidth: 0,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#9aa0c7',
                        padding: 15,
                        font: { size: 11 }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.label + ': ' + context.parsed + '%';
                        }
                    }
                }
            }
        }
    });
}
