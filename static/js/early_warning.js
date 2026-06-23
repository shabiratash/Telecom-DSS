/* Early Warning System JavaScript */

async function loadAlerts() {
    try {
        const alerts = await getJSON('/api/early-warning/alerts');
        const body = document.getElementById('alertsBody');
        if (body) {
            if (alerts.length === 0) {
                body.innerHTML = '<tr><td colspan="7" class="text-center muted py-4">No active alerts</td></tr>';
            } else {
                body.innerHTML = alerts.map(a => {
                    const alertClass = a.alert_level === 'Critical' ? 'text-danger' : (a.alert_level === 'High' ? 'text-warning' : 'text-info');
                    const bgClass = a.alert_level === 'Critical' ? 'bg-danger' : (a.alert_level === 'High' ? 'bg-warning' : 'bg-info');
                    return `
                        <tr>
                            <td><a href="/customers/${a.customer_id}" style="color:#9a8cff">#${a.customer_id}</a></td>
                            <td>${a.province}</td>
                            <td>${a.previous_risk}%</td>
                            <td><b style="color:#ff9b9b">${a.current_risk}%</b></td>
                            <td><span class="badge ${bgClass}">+${a.risk_increase}%</span></td>
                            <td><span class="${alertClass} fw-bold">${a.alert_level}</span></td>
                            <td class="muted small">${a.recorded_at}</td>
                        </tr>
                    `;
                }).join('');
            }
        }
    } catch (e) {
        console.error('Error loading alerts:', e);
        document.getElementById('alertsBody').innerHTML = '<tr><td colspan="7" class="text-center text-danger py-4">Error loading alerts</td></tr>';
    }
}

async function loadRecentWarnings() {
    try {
        const warnings = await getJSON('/api/early-warning/recent-warnings');
        const body = document.getElementById('warningsBody');
        if (body) {
            if (warnings.length === 0) {
                body.innerHTML = '<tr><td colspan="4" class="text-center muted py-4">No recent warnings</td></tr>';
            } else {
                body.innerHTML = warnings.map(w => `
                    <tr>
                        <td><a href="/customers/${w.customer_id}" style="color:#9a8cff">#${w.customer_id}</a></td>
                        <td>${w.province}</td>
                        <td><b style="color:${w.risk_score > 50 ? '#ff9b9b' : '#86efac'}">${w.risk_score}</b></td>
                        <td class="muted small">${w.recorded_at}</td>
                    </tr>
                `).join('');
            }
        }
    } catch (e) {
        console.error('Error loading warnings:', e);
        document.getElementById('warningsBody').innerHTML = '<tr><td colspan="4" class="text-center text-danger py-4">Error loading warnings</td></tr>';
    }
}

async function loadTopRisk() {
    try {
        const topRisk = await getJSON('/api/early-warning/top-risk');
        const body = document.getElementById('topRiskBody');
        if (body) {
            if (topRisk.length === 0) {
                body.innerHTML = '<tr><td colspan="4" class="text-center muted py-4">No data available</td></tr>';
            } else {
                body.innerHTML = topRisk.map(r => {
                    const trendData = r.risk_trend || [];
                    const trendDisplay = trendData.length > 0 
                        ? trendData.map(t => `${t.risk}%`).join(' → ')
                        : 'No trend data';
                    return `
                        <tr>
                            <td><a href="/customers/${r.customer_id}" style="color:#9a8cff">#${r.customer_id}</a></td>
                            <td>${r.province}</td>
                            <td><b style="color:#ff9b9b">${r.current_risk}</b></td>
                            <td class="muted small">${trendDisplay}</td>
                        </tr>
                    `;
                }).join('');
            }
        }
    } catch (e) {
        console.error('Error loading top risk:', e);
        document.getElementById('topRiskBody').innerHTML = '<tr><td colspan="4" class="text-center text-danger py-4">Error loading top risk</td></tr>';
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadAlerts();
    loadRecentWarnings();
    loadTopRisk();
});
