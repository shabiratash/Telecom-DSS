/* Machine Learning Center JavaScript */
let rocChart = null;
let importanceChart = null;

async function trainModels() {
    const btn = document.getElementById('trainBtn');
    const status = document.getElementById('trainStatus');
    
    btn.disabled = true;
    btn.innerHTML = '<i class="bi bi-hourglass-split"></i> Training...';
    status.innerHTML = '<span class="live-indicator pulsing"><i class="bi bi-circle-fill"></i> Training in progress...</span>';
    
    try {
        const response = await fetch('/api/ml-center/train', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        
        if (data.success) {
            status.innerHTML = '<span class="badge-active"><i class="bi bi-check-circle"></i> Training complete!</span>';
            btn.innerHTML = '<i class="bi bi-play-circle"></i> Train Models';
            btn.disabled = false;
            
            // Refresh all data
            await loadModelComparison();
            await loadConfusionMatrix();
            await loadRocCurve();
            await loadFeatureImportance();
            await loadBestModel();
            await loadModelHistory();
        } else {
            status.innerHTML = '<span class="badge-churn"><i class="bi bi-x-circle"></i> Training failed</span>';
            btn.innerHTML = '<i class="bi bi-play-circle"></i> Train Models';
            btn.disabled = false;
            alert('Training failed: ' + data.error);
        }
    } catch (error) {
        status.innerHTML = '<span class="badge-churn"><i class="bi bi-x-circle"></i> Error</span>';
        btn.innerHTML = '<i class="bi bi-play-circle"></i> Train Models';
        btn.disabled = false;
        alert('Error: ' + error.message);
    }
}

async function loadModelComparison() {
    try {
        const response = await fetch('/api/ml-center/model-comparison');
        const data = await response.json();
        
        if (data.error) {
            document.getElementById('modelComparisonBody').innerHTML = 
                '<tr><td colspan="6" class="text-center muted">Train models to see comparison</td></tr>';
            return;
        }
        
        const tbody = document.getElementById('modelComparisonBody');
        tbody.innerHTML = data.map(m => `
            <tr>
                <td><strong>${m.model}</strong></td>
                <td>${(m.accuracy * 100).toFixed(2)}%</td>
                <td>${(m.precision * 100).toFixed(2)}%</td>
                <td>${(m.recall * 100).toFixed(2)}%</td>
                <td>${(m.f1 * 100).toFixed(2)}%</td>
                <td>${m.roc_auc.toFixed(4)}</td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading model comparison:', error);
    }
}

async function loadConfusionMatrix() {
    try {
        const response = await fetch('/api/ml-center/confusion-matrix');
        const data = await response.json();
        
        if (data.error) {
            document.getElementById('confusionMatrixContainer').innerHTML = `
                <div class="placeholder-panel">
                    <i class="bi bi-grid-3x3 big-icon"></i>
                    <p class="muted">Train models to see confusion matrix</p>
                </div>`;
            return;
        }
        
        const cm = data.confusion_matrix;
        const container = document.getElementById('confusionMatrixContainer');
        container.innerHTML = `
            <div class="confusion">
                <div class="cm-cell cm-tp">
                    <span>${cm[0][0]}</span>
                    <small>True Positive</small>
                </div>
                <div class="cm-cell cm-fp">
                    <span>${cm[0][1]}</span>
                    <small>False Positive</small>
                </div>
                <div class="cm-cell cm-fn">
                    <span>${cm[1][0]}</span>
                    <small>False Negative</small>
                </div>
                <div class="cm-cell cm-tn">
                    <span>${cm[1][1]}</span>
                    <small>True Negative</small>
                </div>
            </div>
            <p class="muted mt-2">Best Model: <strong>${data.best_model}</strong></p>
        `;
    } catch (error) {
        console.error('Error loading confusion matrix:', error);
    }
}

async function loadRocCurve() {
    try {
        const response = await fetch('/api/ml-center/roc-curve');
        const data = await response.json();
        
        if (data.error) {
            document.getElementById('rocCurveContainer').innerHTML = `
                <div class="placeholder-panel">
                    <i class="bi bi-graph-up big-icon"></i>
                    <p class="muted">Train models to see ROC curve</p>
                </div>`;
            return;
        }
        
        const container = document.getElementById('rocCurveContainer');
        container.innerHTML = '<canvas id="rocChart" height="250"></canvas>';
        
        const ctx = document.getElementById('rocChart').getContext('2d');
        
        if (rocChart) {
            rocChart.destroy();
        }
        
        rocChart = new Chart(ctx, {
            type: 'line',
            data: {
                datasets: [{
                    label: 'ROC Curve',
                    data: data.fpr.map((fpr, i) => ({ x: fpr, y: data.tpr[i] })),
                    borderColor: '#6d5dfc',
                    backgroundColor: 'rgba(109, 93, 252, 0.1)',
                    fill: true,
                    tension: 0.4
                }, {
                    label: 'Random',
                    data: [{ x: 0, y: 0 }, { x: 1, y: 1 }],
                    borderColor: '#9aa0c7',
                    borderDash: [5, 5],
                    fill: false,
                    pointRadius: 0
                }]
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        type: 'linear',
                        title: { display: true, text: 'False Positive Rate', color: '#9aa0c7' },
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        ticks: { color: '#9aa0c7' }
                    },
                    y: {
                        type: 'linear',
                        title: { display: true, text: 'True Positive Rate', color: '#9aa0c7' },
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        ticks: { color: '#9aa0c7' }
                    }
                },
                plugins: {
                    legend: { labels: { color: '#9aa0c7' } }
                }
            }
        });
    } catch (error) {
        console.error('Error loading ROC curve:', error);
    }
}

async function loadFeatureImportance() {
    try {
        const response = await fetch('/api/ml-center/feature-importance');
        const data = await response.json();
        
        if (data.error) {
            document.getElementById('featureImportanceContainer').innerHTML = `
                <div class="placeholder-panel">
                    <i class="bi bi-list-stars big-icon"></i>
                    <p class="muted">Train models to see feature importance</p>
                </div>`;
            return;
        }
        
        const container = document.getElementById('featureImportanceContainer');
        const importance = data.feature_importance.slice(0, 10);
        
        container.innerHTML = `
            <canvas id="importanceChart" height="250"></canvas>
            <p class="muted mt-2">Best Model: <strong>${data.best_model}</strong></p>
        `;
        
        const ctx = document.getElementById('importanceChart').getContext('2d');
        
        if (importanceChart) {
            importanceChart.destroy();
        }
        
        importanceChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: importance.map(f => f.feature),
                datasets: [{
                    label: 'Importance',
                    data: importance.map(f => f.importance),
                    backgroundColor: '#6d5dfc',
                    borderRadius: 6
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                scales: {
                    x: {
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        ticks: { color: '#9aa0c7' }
                    },
                    y: {
                        grid: { display: false },
                        ticks: { color: '#9aa0c7' }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    } catch (error) {
        console.error('Error loading feature importance:', error);
    }
}

async function loadBestModel() {
    try {
        const response = await fetch('/api/ml-center/best-model');
        const data = await response.json();
        
        if (data.error) {
            return;
        }
        
        const trainingDateEl = document.getElementById('trainingDate');
        if (trainingDateEl && data.training_date) {
            const date = new Date(data.training_date);
            trainingDateEl.textContent = date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        }
    } catch (error) {
        console.error('Error loading best model:', error);
    }
}

async function loadModelHistory() {
    try {
        const response = await fetch('/api/ml-center/history');
        const data = await response.json();
        
        const tbody = document.getElementById('modelHistoryBody');
        tbody.innerHTML = data.map(h => `
            <tr>
                <td>${h.model_name}</td>
                <td>${(h.accuracy * 100).toFixed(2)}%</td>
                <td>${(h.f1_score * 100).toFixed(2)}%</td>
                <td>${new Date(h.training_date).toLocaleString()}</td>
                <td>
                    ${h.is_best_model ? '<span class="badge-active">Best</span>' : '<span class="muted">-</span>'}
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading model history:', error);
    }
}

// Load data on page load
document.addEventListener('DOMContentLoaded', function() {
    loadModelComparison();
    loadConfusionMatrix();
    loadRocCurve();
    loadFeatureImportance();
    loadBestModel();
    loadModelHistory();
});
