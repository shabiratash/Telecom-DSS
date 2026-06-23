/* Financial Impact JavaScript */

async function loadFinancialSummary() {
    try {
        const data = await getJSON('/api/financial/summary');
        
        // Update KPI cards
        document.getElementById('highRiskCustomers').textContent = data.high_risk_customers.toLocaleString();
        document.getElementById('avgRecharge').textContent = data.avg_recharge.toLocaleString() + ' AFN';
        document.getElementById('monthlyLoss').textContent = data.monthly_loss.toLocaleString() + ' AFN';
        document.getElementById('yearlyLoss').textContent = data.yearly_loss.toLocaleString() + ' AFN';
        
        // Load province breakdown
        loadProvinceBreakdown();
    } catch (e) {
        console.error('Error loading financial summary:', e);
    }
}

async function loadProvinceBreakdown() {
    try {
        const data = await getJSON('/api/financial/province-breakdown');
        const body = document.getElementById('provinceBody');
        if (body) {
            body.innerHTML = data.map(p => `
                <tr>
                    <td>${p.province}</td>
                    <td>${p.total_customers}</td>
                    <td>${p.active_customers}</td>
                    <td>${p.churned_customers}</td>
                    <td><b style="color:${p.churn_rate > 30 ? '#ff9b9b' : '#86efac'}">${p.churn_rate}%</b></td>
                    <td>${p.avg_recharge.toLocaleString()} AFN</td>
                    <td><b style="color:#ff9b9b">${p.yearly_risk.toLocaleString()} AFN</b></td>
                </tr>
            `).join('');
        }
        
        // Render risk chart
        renderRiskChart(data);
    } catch (e) {
        console.error('Error loading province breakdown:', e);
        document.getElementById('provinceBody').innerHTML = '<tr><td colspan="7" class="text-center text-danger py-4">Error loading data</td></tr>';
    }
}

function renderRiskChart(data) {
    const ctx = document.getElementById('riskChart');
    if (!ctx) return;
    
    // Destroy existing chart if it exists
    if (window.riskChartInstance) {
        window.riskChartInstance.destroy();
    }
    
    // Take top 10 provinces by yearly risk
    const topProvinces = data.slice(0, 10);
    
    window.riskChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: topProvinces.map(p => p.province),
            datasets: [{
                data: topProvinces.map(p => p.yearly_risk),
                backgroundColor: [
                    '#6d5dfc', '#2f6bff', '#c44dff', '#22c55e', '#f59e0b',
                    '#14b8a6', '#ef4444', '#9a8cff', '#5b8cff', '#2dd4bf'
                ],
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
                        padding: 10,
                        font: { size: 10 }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.label + ': ' + context.parsed.toLocaleString() + ' AFN';
                        }
                    }
                }
            }
        }
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadFinancialSummary();
});
