// Live Customer Monitor - auto-refresh feed with pause/resume (Customer Workspace).
(function () {
  "use strict";

  const INTERVAL_MS = 5000;
  let timer = null;
  let paused = false;

  function fmtDate(iso) {
    if (!iso) return "-";
    return new Date(iso).toLocaleString();
  }

  function healthClass(status) {
    return "health-" + (status || "good").toLowerCase();
  }

  function riskClass(level) {
    return "risk-" + (level || "low").toLowerCase();
  }

  function renderNewCustomers(items) {
    const el = document.getElementById("feedNewCustomers");
    if (!items.length) { el.innerHTML = '<p class="muted">No customers.</p>'; return; }
    el.innerHTML = items.map(c => `
      <div class="live-row">
        <a href="/customers/profile/${c.customer_id}">#${c.customer_id}</a>
        <span>${c.province || '-'} · ${c.gender || ''} ${c.age || ''}</span>
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

  function renderHighRisk(items) {
    const el = document.getElementById("feedHighRisk");
    if (!items.length) { el.innerHTML = '<p class="muted">No high-risk customers in latest batch.</p>'; return; }
    el.innerHTML = items.map(c => `
      <div class="live-row">
        <a href="/customers/profile/${c.customer_id}">#${c.customer_id}</a>
        <span>${c.province || '-'}</span>
        <span class="health-badge ${healthClass(c.health_status)}">${c.health_score} · ${c.health_status}</span>
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
    if (!items.length) { el.innerHTML = '<p class="muted">No recent risk records.</p>'; return; }
    el.innerHTML = items.map(r => `
      <div class="live-row">
        <span>Customer #${r.customer_id}</span>
        <span>Risk: ${Number(r.risk_score).toFixed(1)}</span>
        <small class="muted">${fmtDate(r.recorded_at)}</small>
      </div>`).join("");
  }

  async function refresh() {
    try {
      const res = await fetch(LIVE_MONITOR_URL, { headers: { "X-Requested-With": "fetch" } });
      if (!res.ok) throw new Error("status " + res.status);
      const data = await res.json();
      renderNewCustomers(data.new_customers || []);
      renderPredictions(data.recent_predictions || []);
      renderHighRisk(data.high_risk || []);
      renderRecs(data.recent_recommendations || []);
      renderRisk(data.recent_risk || []);
      document.getElementById("monLast").textContent = new Date().toLocaleTimeString();
    } catch (e) {
      const s = document.getElementById("monStatus");
      if (s) { s.textContent = "Error"; s.className = "text-danger"; }
    }
  }

  function start() {
    if (timer) clearInterval(timer);
    timer = setInterval(() => { if (!paused) refresh(); }, INTERVAL_MS);
  }

  document.addEventListener("DOMContentLoaded", function () {
    if (typeof LIVE_MONITOR_URL === "undefined") return;
    const btnRefresh = document.getElementById("btnRefresh");
    const btnPause = document.getElementById("btnPause");
    const btnResume = document.getElementById("btnResume");
    const status = document.getElementById("monStatus");

    btnRefresh.addEventListener("click", refresh);
    btnPause.addEventListener("click", function () {
      paused = true;
      btnPause.disabled = true; btnResume.disabled = false;
      status.textContent = "Paused"; status.className = "text-warning";
    });
    btnResume.addEventListener("click", function () {
      paused = false;
      btnPause.disabled = false; btnResume.disabled = true;
      status.textContent = "Live"; status.className = "text-success";
      refresh();
    });

    refresh();
    start();
  });
})();
