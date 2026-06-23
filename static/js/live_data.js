// Real-Time Data Viewer + Live Database Monitor (Analytics).
(function () {
  "use strict";

  const INTERVAL_MS = 5000;
  let timer = null;
  let paused = false;

  function setText(id, v) { const el = document.getElementById(id); if (el) el.textContent = v; }
  function fmtDate(iso) { return iso ? new Date(iso).toLocaleString() : "-"; }
  function healthClass(s) { return "health-" + (s || "good").toLowerCase(); }
  function riskClass(l) { return "risk-" + (l || "low").toLowerCase(); }

  function renderCustomers(items) {
    const el = document.getElementById("feedCustomers");
    if (!items.length) { el.innerHTML = '<p class="muted">No customers.</p>'; return; }
    el.innerHTML = items.map(c => `
      <div class="live-row">
        <a href="/customers/profile/${c.customer_id}">#${c.customer_id}</a>
        <span>${c.province || '-'} · ${c.network_quality || ''}</span>
        <span class="health-badge ${healthClass(c.health_status)}">${c.health_score}</span>
      </div>`).join("");
  }

  function renderPredictions(items) {
    const el = document.getElementById("feedPredictions");
    if (!items.length) { el.innerHTML = '<p class="muted">No predictions yet.</p>'; return; }
    el.innerHTML = items.map(p => `
      <div class="live-row">
        <span>${p.customer_id ? '#' + p.customer_id : 'ad-hoc'}</span>
        <span>${p.churn_probability}%</span>
        <span class="risk-pill ${riskClass(p.risk_level)}">${p.risk_level || '-'}</span>
        <small class="muted">${fmtDate(p.created_at)}</small>
      </div>`).join("");
  }

  function renderRecs(items) {
    const el = document.getElementById("feedRecs");
    if (!items.length) { el.innerHTML = '<p class="muted">No recommendations yet.</p>'; return; }
    el.innerHTML = items.map(r => `
      <div class="live-row">
        <span><i class="bi ${r.icon || 'bi-lightbulb'}"></i> ${r.title}</span>
        <span class="sev-pill sev-${r.severity || 'low'}">${r.severity || '-'}</span>
        <small class="muted">${fmtDate(r.created_at)}</small>
      </div>`).join("");
  }

  function renderRisk(items) {
    const el = document.getElementById("feedRisk");
    if (!items.length) { el.innerHTML = '<p class="muted">No risk records.</p>'; return; }
    el.innerHTML = items.map(r => `
      <div class="live-row">
        <span>Customer #${r.customer_id}</span>
        <span>Risk: ${Number(r.risk_score).toFixed(1)}</span>
        <small class="muted">${fmtDate(r.recorded_at)}</small>
      </div>`).join("");
  }

  async function refreshData() {
    const res = await fetch("/api/analytics/live-data", { headers: { "X-Requested-With": "fetch" } });
    if (!res.ok) throw new Error("data " + res.status);
    const d = await res.json();
    renderCustomers(d.latest_customers || []);
    renderPredictions(d.latest_predictions || []);
    renderRecs(d.latest_recommendations || []);
    renderRisk(d.latest_risk_scores || []);
  }

  async function refreshMonitor() {
    const res = await fetch("/api/analytics/db-monitor", { headers: { "X-Requested-With": "fetch" } });
    if (!res.ok) throw new Error("monitor " + res.status);
    const m = await res.json();
    setText("mTotalCust", m.total_customers);
    setText("mTotalPred", m.total_predictions);
    setText("mHighRisk", m.total_high_risk);
    setText("mTotalRec", m.total_recommendations);
    setText("mToday", m.records_added_today);
    setText("mWeek", m.records_added_this_week);
  }

  async function refresh() {
    try {
      await Promise.all([refreshData(), refreshMonitor()]);
      setText("ldLast", new Date().toLocaleTimeString());
      const s = document.getElementById("ldStatus");
      if (s && !paused) { s.textContent = "Live"; s.className = "text-success"; }
    } catch (e) {
      const s = document.getElementById("ldStatus");
      if (s) { s.textContent = "Error"; s.className = "text-danger"; }
    }
  }

  function start() {
    if (timer) clearInterval(timer);
    timer = setInterval(() => { if (!paused) refresh(); }, INTERVAL_MS);
  }

  document.addEventListener("DOMContentLoaded", function () {
    const btnRefresh = document.getElementById("btnRefresh");
    if (!btnRefresh) return;
    const btnPause = document.getElementById("btnPause");
    const btnResume = document.getElementById("btnResume");
    const status = document.getElementById("ldStatus");

    btnRefresh.addEventListener("click", refresh);
    btnPause.addEventListener("click", function () {
      paused = true; btnPause.disabled = true; btnResume.disabled = false;
      status.textContent = "Paused"; status.className = "text-warning";
    });
    btnResume.addEventListener("click", function () {
      paused = false; btnPause.disabled = false; btnResume.disabled = true;
      status.textContent = "Live"; status.className = "text-success";
      refresh();
    });

    refresh();
    start();
  });
})();
