const sampleEvent = {
  source: "aws.cloudwatch",
  "detail-type": "CloudWatch Alarm State Change",
  detail: {
    alarmName: "HighApi5xxRate",
    severity: "SEV2",
    description: "API Gateway 5xx error rate exceeded threshold",
    state: {
      value: "ALARM",
      reason: "5xx error rate exceeded 5% for 5 minutes"
    },
    logGroupName: "/aws/lambda/sentinelai-aws-agent"
  }
};

let latestResponse = null;

const endpointInput = document.getElementById("api-endpoint");
const jsonInput = document.getElementById("incident-json");
const statusEl = document.getElementById("status");
const resultCard = document.getElementById("result-card");
const severityChipEl = document.getElementById("severity-chip");

const incidentIdEl = document.getElementById("incident-id");
const severityEl = document.getElementById("severity");
const confidenceEl = document.getElementById("confidence");
const incidentSourceEl = document.getElementById("incident-source");
const rootCauseEl = document.getElementById("root-cause");
const diagnosisEl = document.getElementById("diagnosis");
const remediationsEl = document.getElementById("remediations");
const rawJsonEl = document.getElementById("raw-json");
const timelineEl = document.getElementById("timeline");
const approvalSummaryEl = document.getElementById("approval-summary");
const approvalStatusEl = document.getElementById("approval-status");
const retrievedDocsEl = document.getElementById("retrieved-docs");
const agentTraceEl = document.getElementById("agent-trace");
const dependencyStatusEl = document.getElementById("dependency-status");
const approvalHistoryEl = document.getElementById("approval-history");
const executionModeEl = document.getElementById("execution-mode");

const reviewerEl = document.getElementById("reviewer");
const navInvestigationBtn = document.getElementById("nav-investigation");
const navApprovalBtn = document.getElementById("nav-approval");
const investigationSection = document.getElementById("investigation-section");
const approvalSection = document.getElementById("approval-section");

function profileConfig(name) {
  const config = window.APP_CONFIG || {};
  const profiles = config.PROFILES || {};
  return profiles[name] || { API_BASE_URL: config.API_BASE_URL || "", APPROVALS_API_URL: "" };
}

function localConfig() {
  const cfg = profileConfig("local");
  return {
    API_BASE_URL: cfg.API_BASE_URL || "http://localhost:9000",
    APPROVALS_API_URL: cfg.APPROVALS_API_URL || "http://localhost:9000/approvals"
  };
}

function mockResult(eventPayload) {
  const incidentId = crypto?.randomUUID ? crypto.randomUUID() : `local-${Date.now()}`;
  const detail = eventPayload?.detail || {};
  const title = detail.alarmName || eventPayload?.title || "Local Mock Incident";
  const severity = detail.severity || "SEV2";
  return {
    incident: {
      incident_id: incidentId,
      source: eventPayload?.source || "local.mock",
      severity,
      title,
      description: detail.description || "Mock incident generated from local UI",
      observed_at: new Date().toISOString()
    },
    diagnosis:
      "Mock diagnosis: request failures are correlated with latency spikes and downstream connection pressure.",
    probable_root_cause: "Connection pool saturation during traffic burst",
    remediation_plan: [
      "Temporarily reduce non-critical concurrency to stabilize downstream resources.",
      "Enable or tune connection pooling and validate max connection thresholds.",
      "Review the latest deployment and rollback if regressions align with incident start time.",
      "Create an action item for joint API latency and DB connection dashboard alerts."
    ],
    confidence: 0.81,
    dependency_status: {
      cloudwatch_logs: "fallback",
      bedrock_runtime: "fallback",
      bedrock_knowledge_base: "fallback",
      overall_mode: "fallback"
    },
    retrieved_documents: [
      {
        title: "Connection Pool Runbook",
        uri: "s3://local-mock/runbooks/connection-pool.md",
        excerpt: "Throttle concurrency and verify pooled connection limits.",
        score: 0.93
      },
      {
        title: "API 5xx Troubleshooting",
        uri: "s3://local-mock/runbooks/api-5xx.md",
        excerpt: "Correlate response codes with dependency latency and deployment timeline.",
        score: 0.88
      }
    ],
    agent_trace: [
      { agent_name: "incident-detection-agent", summary: "Incident payload normalized.", latency_ms: 1.2 },
      { agent_name: "memory-agent", summary: "No prior local history found.", latency_ms: 1.8 },
      { agent_name: "log-analysis-agent", summary: "Detected latency and connection saturation signatures.", latency_ms: 3.2 },
      { agent_name: "knowledge-retrieval-agent", summary: "Retrieved relevant runbooks for pool tuning and 5xx triage.", latency_ms: 0.9 },
      { agent_name: "reasoning-agent", summary: "Inferred likely bottleneck and confidence score.", latency_ms: 1.1 },
      { agent_name: "remediation-agent", summary: "Generated prioritized remediation sequence.", latency_ms: 0.8 }
    ]
  };
}

function renderApprovalHistory(incidentId) {
  const key = `sentinelai_approvals_${incidentId}`;
  const localRecord = localStorage.getItem(key);
  approvalHistoryEl.textContent = localRecord || '{ "message": "No local approval history for this incident yet." }';
}

function init() {
  const cfg = localConfig();
  endpointInput.textContent = `${cfg.API_BASE_URL}/incidents`;
  jsonInput.value = JSON.stringify(sampleEvent, null, 2);

  document.getElementById("sample-btn").addEventListener("click", () => {
    jsonInput.value = JSON.stringify(sampleEvent, null, 2);
  });

  document.getElementById("run-btn").addEventListener("click", runInvestigation);
  document.getElementById("save-approvals").addEventListener("click", saveApprovals);

  navInvestigationBtn.addEventListener("click", () => {
    investigationSection.scrollIntoView({ behavior: "smooth", block: "start" });
    jsonInput.focus();
    statusEl.textContent = "Ready to run autonomous investigation.";
  });

  navApprovalBtn.addEventListener("click", () => {
    if (resultCard.hidden || !latestResponse) {
      statusEl.textContent = "Run investigation first to access approval workflow.";
      investigationSection.scrollIntoView({ behavior: "smooth", block: "start" });
      return;
    }

    approvalSection.scrollIntoView({ behavior: "smooth", block: "start" });
    reviewerEl.focus();
    statusEl.textContent = "Approval workflow ready.";
  });
}

function severityClass(value) {
  const normalized = String(value || "unknown").toLowerCase();
  return `sev-${normalized}`;
}

function updateApprovalSummary() {
  const decisions = Array.from(document.querySelectorAll(".decision")).map((item) => item.value);
  const approved = decisions.filter((item) => item === "approve").length;
  const rejected = decisions.filter((item) => item === "reject").length;
  const pending = decisions.filter((item) => item === "pending").length;
  approvalSummaryEl.textContent = `Approvals: ${approved} approved, ${rejected} rejected, ${pending} pending`;
}

async function runInvestigation() {
  statusEl.textContent = "Running investigation...";

  const endpoint = localConfig().API_BASE_URL;

  let payload;
  try {
    payload = JSON.parse(jsonInput.value);
  } catch (error) {
    statusEl.textContent = `Invalid JSON: ${error.message}`;
    return;
  }

  try {
    const response = await fetch(`${endpoint.replace(/\/$/, "")}/incidents`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const responseBody = await response.json();
    if (!response.ok) {
      const errorMessage = responseBody?.error || responseBody?.details?.reason || `API request failed (${response.status})`;
      throw new Error(errorMessage);
    }
    const result = responseBody.body ? JSON.parse(responseBody.body) : responseBody;

    latestResponse = result;
    renderResult(result);
    statusEl.textContent = "Investigation completed via local API.";
  } catch (error) {
    const fallback = mockResult(payload);
    latestResponse = fallback;
    renderResult(fallback);
    statusEl.textContent = `Local API unavailable, showing full mock response (${error.message}).`;
  }
}

function renderResult(result) {
  const incident = result.incident || {};
  incidentIdEl.textContent = incident.incident_id || "-";
  const severityValue = incident.severity || "-";
  severityEl.textContent = severityValue;
  confidenceEl.textContent = result.confidence ?? "-";
  incidentSourceEl.textContent = incident.source || "-";
  rootCauseEl.textContent = result.probable_root_cause || "N/A";
  diagnosisEl.textContent = result.diagnosis || "N/A";
  const overallMode = result.dependency_status?.overall_mode || "unknown";
  executionModeEl.textContent = overallMode;

  severityChipEl.className = "severity-chip";
  severityChipEl.classList.add(severityClass(severityValue));
  severityChipEl.textContent = severityValue;

  timelineEl.innerHTML = "";
  (result.agent_trace || []).forEach((item) => {
    const node = document.createElement("div");
    node.className = "timeline-item";
    node.innerHTML = `
      <div class="timeline-agent">${item.agent_name || "agent"}</div>
      <div class="timeline-summary">${item.summary || "No summary available."}</div>
    `;
    timelineEl.appendChild(node);
  });

  remediationsEl.innerHTML = "";
  (result.remediation_plan || []).forEach((step, index) => {
    const item = document.createElement("div");
    item.className = "remediation-item";
    item.innerHTML = `
      <p><strong>Step ${index + 1}</strong><br>${step}</p>
      <label>Decision</label>
      <select data-step-index="${index}" class="decision">
        <option value="pending">Pending</option>
        <option value="approve">Approve</option>
        <option value="reject">Reject</option>
      </select>
      <label>Reason</label>
      <input type="text" data-step-index="${index}" class="reason" placeholder="Reason for decision" />
    `;
    remediationsEl.appendChild(item);
  });

  Array.from(document.querySelectorAll(".decision")).forEach((select) => {
    select.addEventListener("change", updateApprovalSummary);
  });
  updateApprovalSummary();

  rawJsonEl.textContent = JSON.stringify(result, null, 2);
  retrievedDocsEl.textContent = JSON.stringify(result.retrieved_documents || [], null, 2);
  agentTraceEl.textContent = JSON.stringify(result.agent_trace || [], null, 2);
  dependencyStatusEl.textContent = JSON.stringify(result.dependency_status || {}, null, 2);
  renderApprovalHistory(incident.incident_id || "unknown");
  resultCard.hidden = false;
}

function saveApprovals() {
  if (!latestResponse) {
    statusEl.textContent = "Run investigation first.";
    return;
  }

  const decisions = Array.from(document.querySelectorAll(".decision"));
  const reasons = Array.from(document.querySelectorAll(".reason"));

  const approvals = (latestResponse.remediation_plan || []).map((step, index) => ({
    step,
    decision: decisions[index]?.value || "pending",
    reason: reasons[index]?.value || ""
  }));

  const incidentId = latestResponse.incident?.incident_id || "unknown";
  const key = `sentinelai_approvals_${incidentId}`;

  const payload = {
    incident_id: incidentId,
    reviewer: reviewerEl.value || "oncall.engineer",
    updated_at: new Date().toISOString(),
    approvals
  };

  const selectedCfg = localConfig();
  const approvalsApiUrl = selectedCfg.APPROVALS_API_URL || "";

  if (approvalsApiUrl) {
    fetch(approvalsApiUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Approval API returned ${response.status}`);
        }
        approvalStatusEl.textContent = `Approvals saved to backend for incident ${incidentId}.`;
        localStorage.setItem(key, JSON.stringify(payload));
        renderApprovalHistory(incidentId);
      })
      .catch((error) => {
        localStorage.setItem(key, JSON.stringify(payload));
        approvalStatusEl.textContent = `Backend save failed (${error.message}); saved locally instead.`;
        renderApprovalHistory(incidentId);
      });
    return;
  }

  localStorage.setItem(key, JSON.stringify(payload));
  approvalStatusEl.textContent = `Approvals saved locally for incident ${incidentId}.`;
  renderApprovalHistory(incidentId);
}

init();
