## Hackathon Demo Runbook (Primary + Backup)

This runbook is optimized for judging criteria: real-world problem, architecture clarity, working demo, and clear GenAI explanation.

### Primary demo path (recommended)

1. Start local profile:

```powershell
./scripts/run_local_profile.ps1
```

2. Open `http://localhost:8084`.
3. Load sample payload and run investigation.
4. In the result card, point out:
   - diagnosis + probable root cause
   - confidence
   - `Execution Mode`
   - `Dependency Status` (live/fallback per dependency)
5. Save at least one remediation approval decision.

### Backup demo path (if API/UI breaks)

Run backend directly:

```bash
python3 -m src.api.handler --event-file evaluation/api_request.json
```

Show in output:
- `agent_trace`
- `retrieved_documents`
- `dependency_status.overall_mode`

### Presentation narrative (2 minutes)

1. **Problem**: on-call teams lose time correlating alarms, logs, and runbooks.
2. **Solution**: event-driven multi-agent workflow on AWS.
3. **GenAI role**: log summarization + root-cause reasoning.
4. **Deterministic controls**: orchestration, retrieval, persistence, approvals.
5. **Transparency**: output clearly marks live vs fallback dependency modes.

### Demo success criteria checklist

- [ ] Investigation returns a valid JSON response.
- [ ] `dependency_status` exists in response.
- [ ] `overall_mode` is visible in UI.
- [ ] At least one remediation approval can be saved.
- [ ] You can explain one live path and one fallback path.
