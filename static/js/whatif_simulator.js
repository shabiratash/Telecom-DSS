/* What-If Simulator JavaScript */
let currentCustomer = null;
let originalFeatures = {};

async function loadCustomer() {
    const select = document.getElementById('customerSelect');
    const customerId = select.value;
    
    if (!customerId) {
        alert('Please select a customer first.');
        return;
    }
    
    try {
        const response = await fetch(`/api/whatif/customer/${customerId}`);
        const data = await response.json();
        
        if (data.error) {
            alert(data.error);
            return;
        }
        
        currentCustomer = data;
        originalFeatures = data.features;
        
        // Show simulation area
        document.getElementById('simulationArea').style.display = 'flex';
        
        // Populate current customer info
        const infoDiv = document.getElementById('currentCustomerInfo');
        infoDiv.innerHTML = `
            <div class="detail-grid">
                <div><small class="muted">Customer ID</small><strong>#${data.customer_id}</strong></div>
                <div><small class="muted">Province</small><strong>${data.features.province_name}</strong></div>
                <div><small class="muted">Age</small><strong>${data.features.age}</strong></div>
                <div><small class="muted">Gender</small><strong>${data.features.gender}</strong></div>
            </div>
        `;
        
        // Set current prediction
        const currentProb = data.current_prediction.probability;
        document.getElementById('currentProb').textContent = currentProb + '%';
        document.getElementById('currentGauge').style.setProperty('--p', currentProb);
        
        const currentRisk = data.current_prediction.risk_level;
        const currentRiskEl = document.getElementById('currentRisk');
        currentRiskEl.textContent = currentRisk;
        currentRiskEl.className = `risk-pill risk-${currentRisk.toLowerCase()}`;
        
        // Set form controls to original values
        document.getElementById('rechargeFrequency').value = originalFeatures.recharge_frequency;
        document.getElementById('rechargeFreqValue').textContent = originalFeatures.recharge_frequency;
        
        document.getElementById('complaintCount').value = originalFeatures.complaint_count;
        document.getElementById('complaintCountValue').textContent = originalFeatures.complaint_count;
        
        document.getElementById('networkQuality').value = originalFeatures.network_quality;
        
        document.getElementById('inactiveDays').value = originalFeatures.inactive_days;
        document.getElementById('inactiveDaysValue').textContent = originalFeatures.inactive_days;
        
        document.getElementById('callDropRate').value = originalFeatures.call_drop_rate;
        document.getElementById('callDropRateValue').textContent = originalFeatures.call_drop_rate + '%';
        
        document.getElementById('discountUsage').value = originalFeatures.discount_usage;
        document.getElementById('competitorOffer').value = originalFeatures.competitor_offer_exposure;
        
        // Initial simulation
        updateSimulation();
        
    } catch (error) {
        console.error('Error loading customer:', error);
        alert('Error loading customer data');
    }
}

async function updateSimulation() {
    if (!currentCustomer) return;
    
    // Update value displays
    document.getElementById('rechargeFreqValue').textContent = document.getElementById('rechargeFrequency').value;
    document.getElementById('complaintCountValue').textContent = document.getElementById('complaintCount').value;
    document.getElementById('inactiveDaysValue').textContent = document.getElementById('inactiveDays').value;
    document.getElementById('callDropRateValue').textContent = document.getElementById('callDropRate').value + '%';
    
    // Get modified features
    const modifiedFeatures = {
        recharge_frequency: parseInt(document.getElementById('rechargeFrequency').value),
        complaint_count: parseInt(document.getElementById('complaintCount').value),
        network_quality: document.getElementById('networkQuality').value,
        inactive_days: parseInt(document.getElementById('inactiveDays').value),
        call_drop_rate: parseFloat(document.getElementById('callDropRate').value),
        discount_usage: document.getElementById('discountUsage').value,
        competitor_offer_exposure: document.getElementById('competitorOffer').value,
    };
    
    try {
        const response = await fetch('/api/whatif/simulate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                customer_id: currentCustomer.customer_id,
                features: modifiedFeatures,
            }),
        });
        
        const data = await response.json();
        
        if (data.error) {
            alert(data.error);
            return;
        }
        
        // Update new probability
        const newProb = data.new_probability;
        document.getElementById('newProb').textContent = newProb + '%';
        document.getElementById('newGauge').style.setProperty('--p', newProb);
        
        const newRisk = data.new_risk;
        const newRiskEl = document.getElementById('newRisk');
        newRiskEl.textContent = newRisk;
        newRiskEl.className = `risk-pill risk-${newRisk.toLowerCase()}`;
        
        // Update improvement
        const improvement = data.improvement;
        const improvementValue = document.getElementById('improvementValue');
        const improvementLabel = document.getElementById('improvementLabel');
        
        improvementValue.textContent = (improvement > 0 ? '+' : '') + improvement + '%';
        
        if (improvement > 0) {
            improvementValue.className = 'display-4 fw-bold text-success';
            improvementLabel.textContent = 'Risk Reduced';
        } else if (improvement < 0) {
            improvementValue.className = 'display-4 fw-bold text-danger';
            improvementLabel.textContent = 'Risk Increased';
        } else {
            improvementValue.className = 'display-4 fw-bold';
            improvementLabel.textContent = 'No Change';
        }
        
        // Update impact cards
        const impactPanel = document.getElementById('impactPanel');
        const impactCards = document.getElementById('impactCards');
        
        if (data.impacts && data.impacts.length > 0) {
            impactPanel.style.display = 'block';
            impactCards.innerHTML = data.impacts.map(impact => {
                const impactClass = impact.impact > 0 ? 'text-success' : (impact.impact < 0 ? 'text-danger' : 'text-muted');
                const impactIcon = impact.impact > 0 ? 'bi-arrow-down' : (impact.impact < 0 ? 'bi-arrow-up' : 'bi-dash');
                return `
                    <div class="col-md-3">
                        <div class="panel glass">
                            <small class="muted">${formatFeatureName(impact.feature)}</small>
                            <div class="mt-1">
                                <span class="fw-bold ${impactClass}">
                                    <i class="bi ${impactIcon}"></i> ${impact.impact > 0 ? '+' : ''}${impact.impact}%
                                </span>
                            </div>
                            <div class="small muted mt-1">
                                ${impact.original} → ${impact.new}
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        } else {
            impactPanel.style.display = 'none';
        }
        
    } catch (error) {
        console.error('Error simulating:', error);
    }
}

function resetSimulation() {
    if (!currentCustomer) return;
    
    document.getElementById('rechargeFrequency').value = originalFeatures.recharge_frequency;
    document.getElementById('complaintCount').value = originalFeatures.complaint_count;
    document.getElementById('networkQuality').value = originalFeatures.network_quality;
    document.getElementById('inactiveDays').value = originalFeatures.inactive_days;
    document.getElementById('callDropRate').value = originalFeatures.call_drop_rate;
    document.getElementById('discountUsage').value = originalFeatures.discount_usage;
    document.getElementById('competitorOffer').value = originalFeatures.competitor_offer_exposure;
    
    updateSimulation();
}

function formatFeatureName(name) {
    return name
        .replace(/_/g, ' ')
        .replace(/\b\w/g, l => l.toUpperCase());
}
