const payloadUrl = "analysis/outputs/app_payload.json";

const currency = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

const decimal = new Intl.NumberFormat("en-US", {
  maximumFractionDigits: 1,
});

const integer = new Intl.NumberFormat("en-US");

function shortMoney(value) {
  const numeric = Number(value);
  if (Math.abs(numeric) >= 1_000_000) return `$${(numeric / 1_000_000).toFixed(1)}M`;
  if (Math.abs(numeric) >= 1_000) return `$${Math.round(numeric / 1_000)}K`;
  return currency.format(numeric);
}

function pct(value) {
  return `${decimal.format(Number(value))}%`;
}

function scoreClass(score) {
  if (Number(score) >= 76) return "high";
  if (Number(score) >= 62) return "medium";
  return "watch";
}

function severityClass(severity) {
  return String(severity).toLowerCase();
}

function setActiveView(viewId) {
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.classList.toggle("is-active", tab.dataset.view === viewId);
  });
  document.querySelectorAll(".view").forEach((view) => {
    view.classList.toggle("is-active", view.id === viewId);
  });
}

function renderSummary(summary) {
  const cards = [
    ["Modeled cohorts", integer.format(summary.campus_count), "campus and newcomer segments"],
    ["Activated users", integer.format(summary.activated_users), `${integer.format(summary.applications)} applications`],
    ["Blended CAC", shortMoney(summary.blended_cac), `${shortMoney(summary.modeled_spend)} modeled spend`],
    ["Launch tests", integer.format(summary.launch_experiments), `${integer.format(summary.high_readiness_risks)} readiness risks`],
  ];

  document.querySelector("#summaryCards").innerHTML = cards.map(([label, value, note]) => `
    <article class="kpi-card">
      <span>${label}</span>
      <strong>${value}</strong>
      <em>${note}</em>
    </article>
  `).join("");
}

function renderTopFocus(data) {
  const cohort = data.cohort_queue[0];
  const experiment = data.experiments[0];
  const readiness = data.readiness_queue[0];

  document.querySelector("#topFocus").innerHTML = `
    <div class="focus-main">
      <span class="score-ring">${cohort.priority_score}</span>
      <div>
        <h3>${cohort.campus_name}</h3>
        <p>${cohort.student_segment}, ${cohort.region}. Focus on ${cohort.recommended_focus} during ${cohort.primary_start_window}.</p>
      </div>
    </div>
    <div class="focus-stack">
      <article>
        <b>${integer.format(cohort.activated_users)}</b>
        <span>modeled activated users</span>
      </article>
      <article>
        <b>${shortMoney(cohort.cac)}</b>
        <span>cohort CAC</span>
      </article>
      <article>
        <b>${pct(cohort.activation_rate_pct)}</b>
        <span>application to activation</span>
      </article>
    </div>
    <div class="decision-strip">
      <span>Best next test</span>
      <strong>${experiment.channel_name}</strong>
      <em>${experiment.expected_activations} activations at ${experiment.campus_name}</em>
    </div>
    <div class="decision-strip muted">
      <span>Blocker to clear</span>
      <strong>${readiness.issue}</strong>
      <em>${readiness.owner}, ${readiness.affected_stage}</em>
    </div>
  `;
}

function renderChannelBars(rows) {
  const maxActivations = Math.max(...rows.map((row) => row.activated_users));
  document.querySelector("#channelBars").innerHTML = rows.map((row) => {
    const width = Math.max(8, row.activated_users / maxActivations * 100);
    return `
      <article class="bar-row">
        <div>
          <strong>${row.channel_name}</strong>
          <span>${integer.format(row.activated_users)} activations, ${pct(row.activation_rate_pct)} activation, ${shortMoney(row.cac)} CAC</span>
        </div>
        <div class="bar-track" aria-hidden="true"><i style="width:${width}%"></i></div>
        <b>${integer.format(row.ops_load)}</b>
      </article>
    `;
  }).join("");
}

function renderWeekly(rows) {
  const peak = Math.max(...rows.map((row) => row.activated_users));
  const last = rows[rows.length - 1];
  document.querySelector("#weeklyPill").textContent = `Week 9 CAC ${shortMoney(last.cac)}`;
  document.querySelector("#weeklyGrid").innerHTML = rows.map((row, index) => {
    const height = Math.max(12, row.activated_users / peak * 100);
    return `
      <article class="week-card">
        <div class="week-bar" style="height:${height}%"></div>
        <span>W${index + 1}</span>
        <strong>${integer.format(row.activated_users)}</strong>
        <em>${integer.format(row.ops_cases)} ops cases</em>
      </article>
    `;
  }).join("");
}

function populateRegionFilter(rows) {
  const regions = [...new Set(rows.map((row) => row.region))].sort();
  const select = document.querySelector("#regionFilter");
  regions.forEach((region) => {
    const option = document.createElement("option");
    option.value = region;
    option.textContent = region;
    select.appendChild(option);
  });
}

function renderCohortRows(rows, filter = "all") {
  const filtered = rows.filter((row) => filter === "all" || row.region === filter);
  document.querySelector("#cohortRows").innerHTML = filtered.map((row) => `
    <tr>
      <td>
        <strong>${row.campus_name}</strong>
        <span>${row.region}, ${row.primary_start_window}</span>
      </td>
      <td>${row.student_segment}<span>${row.recommended_focus}</span></td>
      <td>${integer.format(row.activated_users)}<span>${integer.format(row.applications)} applications</span></td>
      <td>${shortMoney(row.cac)}<span>${shortMoney(row.spend)} spend</span></td>
      <td>${pct(row.activation_rate_pct)}<span>${pct(row.approval_rate_pct)} approval</span></td>
      <td>${pct(row.readiness_score)}<span>${pct(row.lead_to_apply_pct)} apply rate</span></td>
      <td><mark class="${scoreClass(row.priority_score)}">${row.decision}</mark><span>${row.priority_score} score</span></td>
    </tr>
  `).join("");
}

function renderExperiments(rows) {
  document.querySelector("#experimentPill").textContent = `${rows.filter((row) => row.decision === "Launch in week 1").length} launch candidates`;
  document.querySelector("#experimentGrid").innerHTML = rows.map((row) => `
    <article class="experiment-card">
      <header>
        <mark class="${scoreClass(row.priority_score)}">${row.priority_score}</mark>
        <span>${row.decision}</span>
      </header>
      <h3>${row.channel_name}</h3>
      <p>${row.hypothesis}</p>
      <dl>
        <div><dt>Cohort</dt><dd>${row.campus_name}</dd></div>
        <div><dt>Expected activations</dt><dd>${integer.format(row.expected_activations)}</dd></div>
        <div><dt>Expected CAC</dt><dd>${shortMoney(row.expected_cac)}</dd></div>
        <div><dt>Incentive</dt><dd>${row.incentive}</dd></div>
      </dl>
    </article>
  `).join("");
}

function renderReadiness(rows) {
  document.querySelector("#readinessList").innerHTML = rows.map((row) => `
    <article class="readiness-card">
      <div>
        <mark class="${severityClass(row.severity)}">${row.severity}</mark>
        <strong>${row.issue}</strong>
        <span>${row.campus_name}, ${row.affected_stage}</span>
      </div>
      <footer>
        <b>${integer.format(row.estimated_impacted_users)} users</b>
        <em>${row.owner}, ${row.status}</em>
      </footer>
    </article>
  `).join("");
}

function renderActions(rows) {
  document.querySelector("#actionList").innerHTML = rows.map((row) => `
    <article class="action-card">
      <b>${row.sprint_week}</b>
      <div>
        <strong>${row.action}</strong>
        <span>${row.workstream}, ${row.owner}, ${row.effort_hours} hours</span>
      </div>
      <em>${row.status}</em>
    </article>
  `).join("");
}

async function init() {
  const response = await fetch(payloadUrl);
  const data = await response.json();

  renderSummary(data.summary);
  renderTopFocus(data);
  renderChannelBars(data.channel_summary);
  renderWeekly(data.weekly_focus);
  populateRegionFilter(data.cohort_queue);
  renderCohortRows(data.cohort_queue);
  renderExperiments(data.experiments);
  renderReadiness(data.readiness_queue);
  renderActions(data.actions);

  document.querySelectorAll(".tab").forEach((tab) => {
    tab.addEventListener("click", () => setActiveView(tab.dataset.view));
  });

  document.querySelector("#regionFilter").addEventListener("change", (event) => {
    renderCohortRows(data.cohort_queue, event.target.value);
  });
}

init();
