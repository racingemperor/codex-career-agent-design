# Subagent Invocation Contract

This protocol defines how runtime local subagents should be invoked from the static role prompts and secondary prompt injections.

## Core Rule

A specialist role invocation must combine:

```text
static role prompt from .codex/agents/<agent>.toml
  + role-specific secondary_prompt_injection
  + runtime_context_packet reference
  + minimum database subset
  + source, privacy, weight, handoff, and debate rules
```

Do not dispatch a specialist with the static role prompt alone.

## Prompt Composition Order

Compose each runtime subagent prompt in this order:

1. role identity and hard prohibitions from `.codex/agents/<agent>.toml`.
2. `runtime_context_packet_ref` and the smallest role-relevant facts.
3. `secondary_prompt_injection` for the target role.
4. database files to read and exact subsets to prefer.
5. public research tasks and source policy.
6. hard-data weight tasks and required provenance fields.
7. output schema and artifact target.
8. handoff and debate contract.

Do not include irrelevant private user facts. Contact fields should appear only when the role needs them and the user authorized final resume contact fields.

Every invocation must include `universal_runtime_guardrails` in the secondary prompt injection. It is automatically injected by the controller and does not add a user-facing step. Required guardrail fields include `no_file_write_by_default`, `tool_use_requires_explicit_permission`, `blocked_outputs_must_remain_blocked`, `handoff_instead_of_overreach`, and `must_return_structured_json`.

When `no_file_write_by_default` is true, roles must treat file modification as forbidden unless their role-specific authorized operation context explicitly permits it. Ordinary roles should return analysis, blockers, or handoff requests instead of modifying files, websites, repositories, or public profiles.

For file-modifying roles, the secondary prompt injection must carry the exact operation authority:

- `ResumePolisher` may modify local resume artifacts only when the injection includes `authorized_resume_editing.operation_mode = apply_authorized_local_changes`, non-empty `allowed_input_refs`, non-empty `allowed_output_refs`, and `apply_tool_ref = scripts/apply_resume_polish.py`. Otherwise it must return `resume_edit_operation_plan` only. Required outputs include `applied_resume_artifacts` and `file_modification_summary`.
- `PortfolioAssetBuilder` may modify a website, GitHub/Gitee profile repository, README, demo, or portfolio file only when the injection includes `authorized_asset_editing.operation_mode = apply_authorized_local_changes`, `allowed_root`, allowed write action, and `apply_tool_ref = scripts/apply_portfolio_asset_changes.py`. Otherwise it must return `website_or_github_modification_plan` only. Required outputs include `applied_asset_changes` and `file_modification_summary`.

These operation fields belong in the secondary prompt injection and invocation contract; they should not be guessed from the static role prompt or from hidden conversation memory.

## Invocation Packet

Each subagent invocation should be addressable:

```json
{
  "subagent_invocation": {
    "invocation_id": "",
    "run_id": "",
    "target_agent": "",
    "base_prompt_ref": ".codex/agents/<agent>.toml",
    "secondary_prompt_injection_ref": "",
    "runtime_context_packet_ref": "",
    "input_packet_ref": "",
    "allowed_user_facts_ref": "",
    "database_files_to_read": [],
    "source_policy_refs": [],
    "research_tasks": [],
    "hard_data_weight_tasks": [],
    "required_output_fields": [],
    "output_artifact_target": "",
    "privacy_constraints": [],
    "handoff_contract": [],
    "debate_contract": [],
    "expected_artifact_types": [],
    "required_log_events": [],
    "timeout_or_budget_hint": "",
    "retry_allowed": true,
    "on_failure": "return_blocked|rerun_with_more_context|handoff_to_orchestrator",
    "status": "not_started|running|done|blocked|failed|malformed"
  }
}
```

`input_packet_ref` should point to a JSON artifact containing the final composed prompt context, not raw private files unless the role is allowed to read them.

## Role Output Packet

The runtime wrapper should collect each role's response as:

```json
{
  "role_output_packet": {
    "invocation_id": "",
    "target_agent": "",
    "status": "done|done_with_warnings|needs_context|blocked|failed|malformed",
    "role_output_ref": "",
    "evidence_packet_refs": [],
    "runtime_weights_ref": "",
    "artifact_refs": [],
    "blocked_outputs": [],
    "runtime_research_tasks": [],
    "needs_user_confirmation": [],
    "handoff_to": [],
    "errors": [],
    "confidence": "high|medium|low"
  }
}
```

Use `needs_context` only when the missing context is owned by the orchestrator or another subagent. Use `needs_user_confirmation` when the missing fact is user-owned.

## Isolation And Shared Context

- Each subagent should treat its invocation packet as the authoritative context for that role.
- Subagents should not rely on hidden memory from earlier roles.
- Shared state must be passed through `shared_context_refs`, `evidence_packet_refs`, and `artifact_refs`.
- If two roles disagree, the later role should emit `disagreements_with` and a requested resolution instead of overwriting the earlier claim.

## Status Handling

- `done`: output validates and can be merged.
- `done_with_warnings`: output validates but contains weak evidence, stale evidence, or non-blocking gaps.
- `needs_context`: runtime context, another role output, or database subset is missing.
- `blocked`: user-owned facts, consent, required public URL evidence, source permission, or evidence needed for an exact downstream field is missing. Missing JD operational details such as city, onsite days, deadline, headcount, or internship duration should usually become `ask_hr_about`, not a whole-role block.
- `failed`: the role could not complete after allowed retry or recovery.
- `malformed`: output is not parseable or violates required schema.

The orchestrator must convert `needs_context`, `blocked`, `failed`, and `malformed` into an `error_recovery_state`.

## Disjoint Role Scope

Roles may challenge other roles but should not take over their decisions:

- `HRSupervisor` checks readability and presentation readiness, not factual truth.
- `FactualReviewer` checks truthfulness and privacy, not career fit.
- `MatchStrategist` prepares conditional application options when runtime evidence is sufficient for the level of claim being made; `prepare_first` and `explore` need less evidence than exact fit scores or final priority.
- `ResumeArchitect` drafts only from user facts and accepted format gates.
- `LearningPathStrategist` may propose future learning evidence, but must not write unfinished learning as completed resume facts.
- For `target_job_fit`, `MatchStrategist` owns current fit framing, prepare-first/explore options, and application readiness limits from available user and public evidence. It must block exact fit scores, final priority, unsupported weights, and targeted resume tailoring when stronger JD evidence is missing. `LearningPathStrategist` owns evidence-backed skills, projects, proof artifacts, and resume-conversion conditions needed before applying, and should still return a useful learning path when the exact JD is incomplete.
