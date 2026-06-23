// Live prediction for customer portal
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('predictionForm');
    const predictBtn = document.getElementById('predictBtn');
    const resetBtn = document.getElementById('resetBtn');
    const resultsDiv = document.getElementById('predictionResults');
    const spinner = predictBtn.querySelector('.loading-spinner');
    
    let debounceTimer;
    
    // Store initial values for reset
    const initialValues = {};
    form.querySelectorAll('input, select').forEach(input => {
        initialValues[input.name] = input.value;
    });
    
    // Reset button handler
    resetBtn.addEventListener('click', function() {
        form.querySelectorAll('input, select').forEach(input => {
            if (initialValues[input.name] !== undefined) {
                input.value = initialValues[input.name];
            }
        });
        // Trigger prediction after reset
        triggerPrediction();
    });
    
    // Live prediction on any input change
    form.querySelectorAll('input, select').forEach(input => {
        input.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(triggerPrediction, 500);
        });
        input.addEventListener('change', function() {
            clearTimeout(debounceTimer);
            triggerPrediction();
        });
    });
    
    // Form submission handler (manual trigger)
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        triggerPrediction();
    });
    
    // Trigger prediction function
    async function triggerPrediction() {
        if (!predictBtn.disabled) {
            predictBtn.disabled = true;
            spinner.classList.add('active');
            
            // Collect form data
            const formData = {};
            form.querySelectorAll('input, select').forEach(input => {
                formData[input.name] = input.value;
            });
            
            try {
                const response = await fetch('/customer-portal/api/predict', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    updateResults(data);
                } else {
                    showError(data.error || 'Prediction failed');
                }
            } catch (error) {
                showError('Network error: ' + error.message);
            } finally {
                predictBtn.disabled = false;
                spinner.classList.remove('active');
            }
        }
    }
    
    function updateResults(data) {
        const prob = data.probability || 0;
        const riskClass = prob > 70 ? 'danger' : prob > 40 ? 'warning' : 'success';
        const textClass = prob > 70 ? 'text-danger' : prob > 40 ? 'text-warning' : 'text-success';
        
        let reasonsHtml = '';
        if (data.reasons && data.reasons.length > 0) {
            reasonsHtml = data.reasons.slice(0, 5).map(reason => 
                `<li class="list-group-item">
                    <i class="bi bi-dash-circle text-danger"></i> ${reason}
                </li>`
            ).join('');
        }
        
        resultsDiv.innerHTML = `
            <div class="text-center mb-4">
                <h1 class="display-3 ${textClass}">
                    ${prob.toFixed(1)}%
                </h1>
                <p class="text-muted">Churn Probability</p>
            </div>
            <div class="alert alert-${riskClass}">
                <strong>Prediction:</strong> ${data.prediction_label || 'N/A'}
            </div>
            <div class="alert alert-${riskClass}">
                <strong>Risk Level:</strong> ${data.risk_level || 'N/A'}
            </div>
            <h6><i class="bi bi-list-check"></i> Key Factors</h6>
            <ul class="list-group mb-3">
                ${reasonsHtml || '<li class="list-group-item">No specific factors identified</li>'}
            </ul>
            <a href="/customer-portal/recommendations" class="btn btn-success w-100">
                <i class="bi bi-lightbulb"></i> View Recommendations
            </a>
        `;
    }
    
    function showError(message) {
        resultsDiv.innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle"></i>
                <strong>Error:</strong> ${message}
            </div>
        `;
    }
});
