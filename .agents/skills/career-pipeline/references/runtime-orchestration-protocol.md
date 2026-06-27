# Runtime Orchestration Protocol

This protocol defines how the user-side Codex pipeline should run after the static role prompts and secondary prompt injections are available.

## Scope

`RuntimeOrchestrator` is a runtime execution protocol, not another career-judgment role. It tracks state, dispatches role subagents, merges outputs, handles blockers, and decides whether the next step is research, debate, HR review, factual review, user confirmation, or final packaging.

Read `runtime-execution-layer.md`, `subagent-invocation-contract.md`, `runtime-artifact-schema.md`, and `error-recovery-protocol.md` when implementing or simulating actual local execution.

## State Machine

Runtime execution should move through these stages:

```text
intake_received
  -> input_normalized
  -> context_packet_created
  -> injection_ready
  -> agents_running
  -> merge_pending
  -> debate_required | hr_review_required | factual_review_required | user_confirmation_required | blocked
  -> final_package_ready
```

Do not skip `input_normalized`, `context_packet_created`, or `injection_ready`. Specialist subagents must not run on static prompts alone.

## Run State Packet

Every orchestration step should expose:

```json
{
  "run_state": {
    "run_id": "",
    "stage": "intake_received|input_normalized|context_packet_created|injection_ready|agents_running|merge_pending|debate_required|hr_review_required|factual_review_required|user_confirmation_required|blocked|final_package_ready",
    "task_type": "resume_review|resume_generation|job_search|jd_analysis|company_research|tailored_resume|major_positioning|personal_branding|learning_plan|target_job_fit",
    "runtime_context_packet_ref": "",
    "secondary_prompt_injection_refs": [],
    "subagent_invocation_refs": [],
    "active_agents": [],
    "completed_agents": [],
    "blocked_agents": [],
    "failed_invocations": [],
    "artifact_manifest_ref": "",
    "shared_context_refs": [],
    "evidence_packet_refs": [],
    "execution_log_refs": [],
    "debate_topics": [],
    "user_confirmation_points": [],
    "blocked_outputs": [],
    "degraded_outputs": [],
    "recovery_actions": [],
    "next_action": "normalize_input|create_injections|dispatch_agents|merge_outputs|run_debate|run_hr_review|run_factual_review|ask_user_once|return_blocked|return_final_package"
  }
}
```

## Execution Planning Fields

The orchestrator may also expose:

```json
{
  "execution_plan": [],
  "dispatch_queue": [],
  "execution_events": [],
  "artifact_manifest_ref": "",
  "artifact_refs": [],
  "retry_policy": {
    "malformed_output_max_retries": 1,
    "subagent_failure_max_retries": 1,
    "retry_requires_new_context_or_narrower_prompt": true
  },
  "merge_policy": {
    "partial_result_policy": "discard|merge_safe_fields_only|ask_user|rerun_agent",
    "safe_partial_fields": [
      "evidence_basis",
      "blocked_outputs",
      "runtime_research_tasks",
      "evidence_requirements",
      "needs_user_confirmation"
    ],
    "never_merge_from_failed_or_malformed": [
      "fit_score",
      "priority",
      "positioning_verdict",
      "pass_to_next_stage",
      "final_resume_draft",
      "application_strategy"
    ]
  }
}
```

`CareerOrchestrator` is the owner of retry, partial merge, blocked package, and final package decisions. Specialist agents may report status, errors, and blockers, but must not skip upstream gates.

## Dispatch Gates

Before dispatching a specialist role, verify:

- `runtime_context_packet_ref` exists.
- the role has a `secondary_prompt_injection`.
- the injected prompt names the static base prompt, allowed user facts, database files, source policy, research tasks, hard-data weight tasks, required output fields, handoff fields, and debate fields.
- privacy constraints are included.
- blocked outputs are listed when user-owned facts or public evidence are missing.
- a `subagent_invocation` can be created with `invocation_id`, input refs, output artifact target, and failure behavior.

If any item is missing, set `stage = "blocked"` or keep `stage = "injection_ready"` with `blocked_agents` and `next_action = "create_injections"`.

## Execution Logging

Each runtime step should write a redacted execution event:

```json
{
  "execution_event": {
    "event_id": "",
    "run_id": "",
    "stage": "",
    "agent_id": "",
    "event_type": "normalize|create_context_packet|create_injection|dispatch|receive_output|validate_output|merge|debate|hr_review|factual_review|ask_user|retry|block|finalize",
    "input_refs": [],
    "output_refs": [],
    "status": "started|done|blocked|failed|malformed|degraded",
    "timestamp_or_sequence": "",
    "redaction_applied": true
  }
}
```

Do not log raw private contact details, IDs, addresses, private chats, or unauthorized source content.

## Merge Rules

When subagent outputs return:

- preserve each role's `evidence_basis`, `weight_provenance`, `blocked_outputs`, `runtime_research_tasks`, and `needs_user_confirmation`.
- preserve each role's `artifact_refs`, `execution_log_refs`, `role_output_packet`, and `error_recovery_state`.
- merge claims only when source policy and confidence are compatible.
- keep disagreements in `debate_topics`; do not erase or average away conflicts.
- if a downstream output depends on missing user-owned facts, set `user_confirmation_required`.
- if a downstream output depends on public evidence, create research tasks instead of asking the user.
- if a subagent failed or returned malformed output, merge only safe partial fields allowed by `merge_policy` and keep final decisions blocked.

## Error Recovery Routing

Use `error-recovery-protocol.md` for categories and recovery fields.

- missing injection: do not dispatch; return to `create_injections`.
- missing user-owned facts: set `user_confirmation_required` and ask once.
- missing public evidence or current JD: create runtime research tasks; block only dependent exact fields such as fit score, final priority, unsupported weights, and targeted resume tailoring.
- target job fit: when a concrete job or internship is present, dispatch JDAnalyzer, CompanyIntelligenceAnalyst, MatchStrategist, LearningPathStrategist, HRSupervisor, and FactualReviewer as needed; allow safe current-fit framing, preparation-first recommendations, learning paths, and public URL targets from available evidence. If the JD is silent on opening status, city, onsite days, arrival time, deadline, headcount, or internship duration, record `ask_hr_about` instead of blocking the recommendation.
- malformed output: retry once with a narrower schema-repair prompt; if still malformed, mark invocation failed.
- subagent failure: retry only if new context or a narrower prompt is available; otherwise degrade or block.
- privacy or factual risk: route to `FactualReviewer` and block final resume approval.
- unsupported weight: set `not_available` or `needs_more_sources`; block downstream scoring, ranking, and priority.

## Debate And Review Routing

Use these routing rules:

- factual support, inflated claims, privacy, or interview defensibility conflicts go to `FactualReviewer`.
- HR readability, first-screen competitiveness, or personal packaging conflicts go to `HRSupervisor`.
- match, learning, branding, and resume claims with weak or conflicting evidence enter `debate_required`.
- missing user-owned facts enter `user_confirmation_required` with one compact question batch.
- missing public/official evidence becomes `runtime_research_tasks`.

## Completion Rules

Set `final_package_ready` only when:

- all required specialist outputs for the requested final output are present.
- unresolved disagreements are either resolved, documented, or converted into user confirmation/research tasks.
- resume drafts have passed `ResumeFormatGate` and `FactualReviewer` when a resume is produced.
- HR-supervised outputs have a `positioning_verdict`.
- all weights used in decisions have `runtime_weights` and/or `weight_provenance`, and unsupported weights are marked `not_available` or `needs_more_sources`.

Blocked required gates do not satisfy final readiness. If completion is impossible, set `stage = "blocked"` and return a `blocked_package` with the minimum missing user facts, missing public research tasks, failed gates, and outputs that cannot be produced. If safe partial outputs exist, list them under `degraded_outputs` or `safe_outputs`, not `final_package_ready`.
