/* Chart.js initializers for dashboard & analytics pages */

function baseLegend() {
    return { labels: { color: '#e8e9ff', usePointStyle: true, padding: 16 } };
}

/* ============ DASHBOARD ============ */
async function initDashboardCharts() {
    try {
        const [split, prov, trend, stats, topRisk, activities] = await Promise.all([
            getJSON('/api/dashboard/churn-split'),
            getJSON('/api/dashboard/province-customers'),
            getJSON('/api/dashboard/monthly-trend'),
            getJSON('/api/dashboard/province-stats'),
            getJSON('/api/dashboard/top-risk-customers'),
            getJSON('/api/dashboard/recent-activities'),
        ]);

        new Chart(document.getElementById('churnPie'), {
            type: 'doughnut',
            data: {
                labels: split.labels,
                datasets: [{ data: split.values, backgroundColor: [CHART_COLORS.green, CHART_COLORS.red], borderWidth: 0 }],
            },
            options: { cutout: '65%', plugins: { legend: { position: 'bottom', ...baseLegend() } } },
        });

        new Chart(document.getElementById('provinceBar'), {
            type: 'bar',
            data: {
                labels: prov.labels,
                datasets: [{ label: 'Customers', data: prov.values, backgroundColor: gradientBars(prov.values.length), borderRadius: 6 }],
            },
            options: { plugins: { legend: { display: false } }, scales: gridScales() },
        });

        new Chart(document.getElementById('trendLine'), {
            type: 'line',
            data: {
                labels: trend.labels,
                datasets: [{
                    label: 'Churned', data: trend.values, borderColor: CHART_COLORS.pink,
                    backgroundColor: 'rgba(196,77,255,.15)', fill: true, tension: .4, pointRadius: 3,
                }],
            },
            options: { plugins: { legend: baseLegend() }, scales: gridScales() },
        });

        const body = document.getElementById('provinceStatsBody');
        if (body) {
            body.innerHTML = stats.slice(0, 12).map(s => `
                <tr>
                    <td>${s.province}</td>
                    <td><span class="chip chip-${secClass(s.security_level)}">${s.security_level}</span></td>
                    <td><b style="color:${s.churn_rate > 50 ? '#ff9b9b' : '#86efac'}">${s.churn_rate}%</b></td>
                </tr>`).join('');
        }

        // Top risk customers table
        const riskBody = document.getElementById('topRiskBody');
        if (riskBody) {
            riskBody.innerHTML = topRisk.map(r => `
                <tr>
                    <td><a href="/customers/${r.customer_id}" style="color:#9a8cff">#${r.customer_id}</a></td>
                    <td>${r.province}</td>
                    <td><b style="color:${r.complaints > 5 ? '#ff9b9b' : '#86efac'}">${r.complaints}</b></td>
                    <td><b style="color:${r.inactive_days > 30 ? '#ff9b9b' : '#86efac'}">${r.inactive_days}</b></td>
                    <td><b style="color:#ff9b9b">${r.risk_score}</b></td>
                    <td><span class="health-badge health-${r.health_status?.toLowerCase() || 'unknown'}">${r.health_score || 0}</span></td>
                </tr>`).join('');
        }

        // Recent activities table
        const actBody = document.getElementById('activitiesBody');
        if (actBody) {
            const actIcons = {
                'churn': 'bi-person-dash text-danger',
                'add': 'bi-person-plus text-success',
                'train': 'bi-cpu text-info',
                'complaint': 'bi-chat-dots text-warning',
                'recharge': 'bi-wallet2 text-success'
            };
            actBody.innerHTML = activities.map(a => `
                <tr>
                    <td><i class="bi ${actIcons[a.type] || 'bi-info-circle'}"></i></td>
                    <td>${a.message}</td>
                    <td class="muted small">${a.time}</td>
                </tr>`).join('');
        }
    } catch (e) { console.error(e); }
}

function gradientBars(n) {
    return Array.from({ length: n }, (_, i) => PALETTE[i % PALETTE.length]);
}
function gridScales() {
    return {
        x: { grid: { color: 'rgba(255,255,255,.06)' }, ticks: { color: '#9aa0c7' } },
        y: { grid: { color: 'rgba(255,255,255,.06)' }, ticks: { color: '#9aa0c7' }, beginAtZero: true },
    };
}
function secClass(level) {
    return level === 'High' ? 'good' : (level === 'Medium' ? 'average' : 'poor');
}

/* ============ ANALYTICS ============ */
async function initAnalytics(meta) {
    if (meta) {
        // model comparison
        const names = Object.keys(meta.metrics);
        new Chart(document.getElementById('modelCompare'), {
            type: 'bar',
            data: {
                labels: names,
                datasets: [
                    { label: 'ROC-AUC', data: names.map(n => meta.metrics[n].roc_auc), backgroundColor: CHART_COLORS.purple, borderRadius: 6 },
                    { label: 'F1', data: names.map(n => meta.metrics[n].f1), backgroundColor: CHART_COLORS.teal, borderRadius: 6 },
                ],
            },
            options: { plugins: { legend: baseLegend() }, scales: gridScales() },
        });

        // ROC curve
        new Chart(document.getElementById('rocCurve'), {
            type: 'line',
            data: {
                labels: meta.roc_curve.fpr,
                datasets: [
                    { label: 'ROC', data: meta.roc_curve.fpr.map((f, i) => ({ x: f, y: meta.roc_curve.tpr[i] })), borderColor: CHART_COLORS.purple, backgroundColor: 'rgba(109,93,252,.15)', fill: true, tension: .3, pointRadius: 0 },
                    { label: 'Random', data: [{ x: 0, y: 0 }, { x: 1, y: 1 }], borderColor: CHART_COLORS.muted, borderDash: [6, 6], pointRadius: 0 },
                ],
            },
            options: {
                parsing: false,
                plugins: { legend: baseLegend() },
                scales: {
                    x: { type: 'linear', min: 0, max: 1, title: { display: true, text: 'False Positive Rate', color: '#9aa0c7' }, grid: { color: 'rgba(255,255,255,.06)' } },
                    y: { type: 'linear', min: 0, max: 1, title: { display: true, text: 'True Positive Rate', color: '#9aa0c7' }, grid: { color: 'rgba(255,255,255,.06)' } },
                },
            },
        });

        // feature importance
        const fi = meta.feature_importance.slice(0, 12);
        new Chart(document.getElementById('featureImp'), {
            type: 'bar',
            data: {
                labels: fi.map(x => x.feature),
                datasets: [{ label: 'Importance', data: fi.map(x => x.importance), backgroundColor: gradientBars(fi.length), borderRadius: 6 }],
            },
            options: { indexAxis: 'y', plugins: { legend: { display: false } }, scales: gridScales() },
        });
    }

    // complaints & segmentation (always available from DB)
    try {
        const [comp, seg] = await Promise.all([
            getJSON('/api/analytics/complaints'),
            getJSON('/api/analytics/segmentation'),
        ]);
        new Chart(document.getElementById('complaintChart'), {
            type: 'bar',
            data: { labels: comp.labels, datasets: [{ label: 'Churn %', data: comp.values, backgroundColor: CHART_COLORS.orange, borderRadius: 6 }] },
            options: { plugins: { legend: { display: false } }, scales: gridScales() },
        });
        new Chart(document.getElementById('segmentChart'), {
            type: 'polarArea',
            data: { labels: seg.labels, datasets: [{ data: seg.values, backgroundColor: PALETTE.slice(0, seg.labels.length) }] },
            options: { plugins: { legend: { position: 'right', ...baseLegend() } }, scales: { r: { grid: { color: 'rgba(255,255,255,.1)' }, ticks: { display: false } } } },
        });
    } catch (e) { console.error(e); }

    loadHeatmap();
    loadTopRisk();
    loadInsights();
}

async function loadHeatmap() {
    try {
        const d = await getJSON('/api/analytics/heatmap');
        let html = '<table class="heat-table"><thead><tr><th></th>' +
            d.networks.map(n => `<th>${n}</th>`).join('') + '</tr></thead><tbody>';
        d.provinces.forEach((p, i) => {
            html += `<tr><th style="text-align:left">${p}</th>`;
            d.matrix[i].forEach(v => {
                html += `<td><span class="heat-cell" style="background:${heatColor(v)}">${v}%</span></td>`;
            });
            html += '</tr>';
        });
        html += '</tbody></table>';
        document.getElementById('heatmap').innerHTML = html;
    } catch (e) { console.error(e); }
}

function heatColor(v) {
    const t = Math.min(v, 100) / 100;
    const r = Math.round(47 + t * (239 - 47));
    const g = Math.round(107 + t * (68 - 107));
    const b = Math.round(255 + t * (68 - 255));
    return `rgba(${r},${g},${b},.75)`;
}

async function loadTopRisk() {
    try {
        const rows = await getJSON('/api/analytics/top-risk');
        const body = document.getElementById('topRiskBody');
        if (body) {
            body.innerHTML = rows.map(r => `
                <tr>
                    <td><a href="/customers/${r.customer_id}" style="color:#9a8cff">#${r.customer_id}</a></td>
                    <td>${r.province}</td>
                    <td><b style="color:#ff9b9b">${r.risk_score}</b></td>
                    <td><a class="btn btn-icon" href="/customers/${r.customer_id}"><i class="bi bi-eye"></i></a></td>
                </tr>`).join('');
        }
    } catch (e) { console.error(e); }
}

async function loadInsights() {
    try {
        const insights = await getJSON('/api/analytics/ai-insights');
        document.getElementById('aiInsights').innerHTML = insights.map(i =>
            `<div class="insight insight-${i.severity}"><i class="bi ${i.icon}"></i><div><b>${i.title}</b><p>${i.text}</p></div></div>`).join('');
    } catch (e) {
        document.getElementById('aiInsights').innerHTML = '<span class="muted">Insights unavailable.</span>';
    }
}

/* ============ LIVE POLLING ============ */
let analyticsTimer = null;

function startLiveAnalytics() {
    if (analyticsTimer) clearInterval(analyticsTimer);
    analyticsTimer = setInterval(() => {
        const indicator = document.getElementById('analyticsLive');
        if (indicator) indicator.classList.add('pulsing');
        Promise.all([
            loadHeatmap(),
            loadTopRisk(),
            loadInsights(),
            loadLiveCharts(),
        ]).finally(() => {
            if (indicator) indicator.classList.remove('pulsing');
        });
    }, 30000); // poll every 30 seconds
}

async function loadLiveCharts() {
    try {
        const [comp, seg, prov] = await Promise.all([
            getJSON('/api/analytics/complaints'),
            getJSON('/api/analytics/segmentation'),
            getJSON('/api/analytics/province'),
        ]);
        // update complaint chart
        const compChart = Chart.getChart('complaintChart');
        if (compChart) {
            compChart.data.labels = comp.labels;
            compChart.data.datasets[0].data = comp.values;
            compChart.update('none');
        }
        // update segmentation chart
        const segChart = Chart.getChart('segmentChart');
        if (segChart) {
            segChart.data.labels = seg.labels;
            segChart.data.datasets[0].data = seg.values;
            segChart.update('none');
        }
        // update province stats table (dashboard)
        const provBody = document.getElementById('provinceStatsBody');
        if (provBody) {
            provBody.innerHTML = prov.slice(0, 12).map(s => `
                <tr>
                    <td>${s.province}</td>
                    <td><span class="chip chip-${secClass(s.security_level)}">${s.security_level}</span></td>
                    <td><b style="color:${s.churn_rate > 50 ? '#ff9b9b' : '#86efac'}">${s.churn_rate}%</b></td>
                </tr>`).join('');
        }
    } catch (e) { console.error(e); }
}
