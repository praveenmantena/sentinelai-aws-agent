from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import streamlit as st

from src.api.handler import process_incident
from src.services.approval_store import ApprovalStore


def _load_default_incident() -> dict[str, Any]:
    sample_path = Path("evaluation/api_request.json")
    if sample_path.exists():
        return json.loads(sample_path.read_text(encoding="utf-8"))
    return {
        "source": "aws.cloudwatch",
        "detail-type": "CloudWatch Alarm State Change",
        "detail": {
            "alarmName": "HighApi5xxRate",
            "severity": "SEV2",
            "description": "API Gateway 5xx error rate exceeded threshold",
            "state": {"value": "ALARM", "reason": "5xx error rate exceeded 5% for 5 minutes"},
        },
    }


def _render_incident_summary(result: dict[str, Any]) -> None:
    incident = result.get("incident", {})
    st.subheader("Incident Summary")
    cols = st.columns(4)
    cols[0].metric("Incident ID", incident.get("incident_id", "N/A"))
    cols[1].metric("Severity", incident.get("severity", "N/A"))
    cols[2].metric("Confidence", str(result.get("confidence", "N/A")))
    cols[3].metric("Source", incident.get("source", "N/A"))
    st.write("Root Cause:")
    st.info(result.get("probable_root_cause", "No root cause available"))
    st.write("Diagnosis:")
    st.write(result.get("diagnosis", "No diagnosis available"))


def _render_remediation_approvals(result: dict[str, Any], store: ApprovalStore) -> None:
    incident = result.get("incident", {})
    incident_id = incident.get("incident_id", "unknown")
    incident_title = incident.get("title", "Untitled incident")

    st.subheader("Remediation Approvals")
    st.caption("Approve or reject each remediation suggestion and persist the decision.")

    existing = store.get_incident_approvals(incident_id)
    existing_map = {
        item.get("step"): item for item in existing.get("approvals", [])
    } if existing else {}

    reviewer = st.text_input("Reviewer", value="oncall.engineer")
    decisions: list[dict[str, Any]] = []

    for index, step in enumerate(result.get("remediation_plan", []), start=1):
        st.markdown(f"**Step {index}**")
        st.write(step)

        default_decision = existing_map.get(step, {}).get("decision", "pending")
        decision = st.radio(
            f"Decision for step {index}",
            options=["approve", "reject", "pending"],
            index=["approve", "reject", "pending"].index(default_decision) if default_decision in ["approve", "reject", "pending"] else 2,
            horizontal=True,
            key=f"decision_{index}",
        )
        reason = st.text_input(
            f"Reason for step {index}",
            value=existing_map.get(step, {}).get("reason", ""),
            key=f"reason_{index}",
        )
        decisions.append({"step": step, "decision": decision, "reason": reason})

    if st.button("Save approvals", type="primary"):
        store.save_incident_approvals(
            incident_id=incident_id,
            title=incident_title,
            approvals=decisions,
            approved_by=reviewer,
        )
        st.success(f"Saved approvals for incident {incident_id}.")

    with st.expander("Stored approvals for this incident"):
        st.json(store.get_incident_approvals(incident_id) or {"message": "No approvals saved yet."})


def main() -> None:
    st.set_page_config(page_title="SentinelAI AWS Agent", layout="wide")
    st.title("SentinelAI AWS Agent UI")
    st.caption("Run incident investigations and manage remediation approvals from one dashboard.")

    store = ApprovalStore()
    default_event = _load_default_incident()

    with st.sidebar:
        st.header("Controls")
        run_now = st.button("Run investigation", type="primary")
        st.download_button(
            label="Download sample event",
            data=json.dumps(default_event, indent=2),
            file_name="incident_event.json",
            mime="application/json",
        )

    event_input = st.text_area(
        "Incident Event JSON",
        value=json.dumps(default_event, indent=2),
        height=320,
    )

    if "latest_result" not in st.session_state:
        st.session_state.latest_result = None

    if run_now:
        try:
            event = json.loads(event_input)
            result = process_incident(event)
            st.session_state.latest_result = result
            st.success("Investigation completed.")
        except json.JSONDecodeError as error:
            st.error(f"Invalid JSON input: {error}")
        except Exception as error:
            st.error(f"Investigation failed: {error}")

    result = st.session_state.latest_result
    if result:
        _render_incident_summary(result)

        tabs = st.tabs(["Remediation", "Retrieved Documents", "Agent Trace", "Raw JSON", "Approval History"])

        with tabs[0]:
            _render_remediation_approvals(result, store)

        with tabs[1]:
            st.json(result.get("retrieved_documents", []))

        with tabs[2]:
            st.json(result.get("agent_trace", []))

        with tabs[3]:
            st.json(result)

        with tabs[4]:
            st.json(store.all())
    else:
        st.info("Click 'Run investigation' to generate a response and start approvals.")


if __name__ == "__main__":
    main()
