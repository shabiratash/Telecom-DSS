// Model Diagnostics: overfitting detector + performance charts (read-only).
(function () {
  "use strict";

  function setText(id, val) {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
  }

  function statusClass(severity) {
    return "status-" + (severity || "success");
  }

  function renderConfusion(cm) {
    const el = document.getElementById("confusionChart");
    if (!el || !cm) return;
    // cm = [[TN, FP], [FN, TP]]
    const data = [
      { x: "Pred: Stay", y: "Actual: Stay", v: cm[0][0] },
      { x: "Pred: Churn", y: "Actual: Stay", v: cm[0][1] },
      { x: "Pred: Stay", y: "Actual: Churn", v: cm[1][0] },
      { x: "Pred: Churn", y: "Actual: Churn", v: cm[1][1] },
    ];
    new Chart(el.getContext("2d"), {
      type: "bar",
      data: {
        labels: ["TN (Stay/Stay)", "FP (Churn/Stay)", "FN (Stay/Churn)", "TP (Churn/Churn)"],
        datasets: [{
          label: "Count",
          data: [cm[0][0], cm[0][1], cm[1][0], cm[1][1]],
          backgroundColor: ["#22c55e", "#ef4444", "#f59e0b", "#8b5cf6"],
        }],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(148,163,184,.1)" } },
          y: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(148,163,184,.1)" }, beginAtZero: true },
        },
      },
    });
  }

  function renderRoc(roc) {
    const el = document.getElementById("rocChart");
    if (!el || !roc) return;
    const points = roc.fpr.map((f, i) => ({ x: f, y: roc.tpr[i] }));
    new Chart(el.getContext("2d"), {
      type: "line",
      data: {
        datasets: [
          {
            label: "ROC Curve",
            data: points,
            borderColor: "#8b5cf6",
            backgroundColor: "rgba(139,92,246,.2)",
            fill: true, tension: 0.2, pointRadius: 0,
          },
          {
            label: "Random",
            data: [{ x: 0, y: 0 }, { x: 1, y: 1 }],
            borderColor: "#64748b",
            borderDash: [6, 6], pointRadius: 0, fill: false,
          },
        ],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { labels: { color: "#cbd5e1" } } },
        scales: {
          x: { type: "linear", min: 0, max: 1, title: { display: true, text: "False Positive Rate", color: "#94a3b8" }, ticks: { color: "#94a3b8" }, grid: { color: "rgba(148,163,184,.1)" } },
          y: { min: 0, max: 1, title: { display: true, text: "True Positive Rate", color: "#94a3b8" }, ticks: { color: "#94a3b8" }, grid: { color: "rgba(148,163,184,.1)" } },
        },
      },
    });
  }

  async function load() {
    const alertBox = document.getElementById("diagAlert");
    try {
      const res = await fetch("/api/analytics/diagnostics", { headers: { "X-Requested-With": "fetch" } });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed");

      setText("diagModel", data.best_model || "-");
      setText("diagNote", data.note || "");

      const o = data.overfitting;
      setText("trainAcc", o.train_accuracy + "%");
      setText("valAcc", o.validation_accuracy + "%");
      setText("testAcc", o.test_accuracy + "%");
      setText("gapVal", o.gap + "%");

      const pill = document.getElementById("statusPill");
      if (pill) {
        pill.textContent = o.status;
        pill.className = "status-pill " + statusClass(o.severity);
      }
      const gapCard = document.getElementById("gapCard");
      if (gapCard) gapCard.classList.add("kpi-" + (o.severity || "success"));

      const p = data.performance;
      setText("mAcc", p.accuracy + "%");
      setText("mPrec", p.precision + "%");
      setText("mRec", p.recall + "%");
      setText("mF1", p.f1 + "%");
      setText("mAuc", p.roc_auc + "%");

      renderConfusion(data.confusion_matrix);
      renderRoc(data.roc_curve);
    } catch (e) {
      if (alertBox) {
        alertBox.innerHTML = '<div class="panel glass"><div class="alert alert-danger glass mb-0">' +
          '<i class="bi bi-x-octagon"></i> ' + (e.message || "Unable to load diagnostics") + '</div></div>';
      }
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    if (document.getElementById("trainAcc")) load();
  });
})();
