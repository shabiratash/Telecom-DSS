// Customer profile timelines + history tables (Customer Workspace).
(function () {
  "use strict";

  function fmtDate(iso) {
    if (!iso) return "-";
    const d = new Date(iso);
    return d.toLocaleString();
  }

  async function getJSON(url) {
    const res = await fetch(url, { headers: { "X-Requested-With": "fetch" } });
    if (!res.ok) throw new Error("Request failed: " + res.status);
    return res.json();
  }

  function lineChart(canvasId, labels, data, label, color) {
    const el = document.getElementById(canvasId);
    if (!el) return;
    new Chart(el.getContext("2d"), {
      type: "line",
      data: {
        labels: labels,
        datasets: [{
          label: label,
          data: data,
          borderColor: color,
          backgroundColor: color + "33",
          fill: true,
          tension: 0.3,
          pointRadius: 3,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { labels: { color: "#cbd5e1" } } },
        scales: {
          x: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(148,163,184,.1)" } },
          y: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(148,163,184,.1)" } },
        },
      },
    });
  }

  async function loadPredictionHistory() {
    const body = document.getElementById("predHistoryBody");
    try {
      const rows = await getJSON(`/api/customers/${CUSTOMER_ID}/prediction-history`);
      // Timeline chart
      const labels = rows.map(r => fmtDate(r.created_at));
      const probs = rows.map(r => r.churn_probability);
      lineChart("churnTimeline", labels, probs, "Churn Probability %", "#8b5cf6");

      if (!rows.length) {
        body.innerHTML = '<tr><td colspan="4" class="muted text-center py-3">No prediction history yet.</td></tr>';
        return;
      }
      body.innerHTML = rows.slice().reverse().map(r => `
        <tr>
          <td>${fmtDate(r.created_at)}</td>
          <td>${r.churn_probability}%</td>
          <td><span class="risk-pill risk-${(r.risk_level||'').toLowerCase()}">${r.risk_level || '-'}</span></td>
          <td>${r.source || '-'}</td>
        </tr>`).join("");
    } catch (e) {
      body.innerHTML = '<tr><td colspan="4" class="muted text-center py-3">Unable to load history.</td></tr>';
    }
  }

  async function loadRiskHistory() {
    try {
      const rows = await getJSON(`/api/customers/${CUSTOMER_ID}/risk-history`);
      const labels = rows.map(r => fmtDate(r.recorded_at));
      const scores = rows.map(r => r.risk_score);
      lineChart("riskTimeline", labels, scores, "Risk Score", "#f59e0b");
    } catch (e) { /* guarded */ }
  }

  async function loadRecHistory() {
    const body = document.getElementById("recHistoryBody");
    try {
      const rows = await getJSON(`/api/customers/${CUSTOMER_ID}/recommendation-history`);
      if (!rows.length) {
        body.innerHTML = '<tr><td colspan="3" class="muted text-center py-3">No recommendation history yet.</td></tr>';
        return;
      }
      body.innerHTML = rows.map(r => `
        <tr>
          <td>${fmtDate(r.created_at)}</td>
          <td><i class="bi ${r.icon || 'bi-lightbulb'}"></i> ${r.title}</td>
          <td><span class="sev-pill sev-${r.severity || 'low'}">${r.severity || '-'}</span></td>
        </tr>`).join("");
    } catch (e) {
      body.innerHTML = '<tr><td colspan="3" class="muted text-center py-3">Unable to load history.</td></tr>';
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    if (typeof CUSTOMER_ID === "undefined") return;
    loadPredictionHistory();
    loadRiskHistory();
    loadRecHistory();
  });
})();
