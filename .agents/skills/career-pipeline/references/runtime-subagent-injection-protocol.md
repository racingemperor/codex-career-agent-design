# Runtime Subagent Injection Protocol

This protocol ensures the repository's role frameworks can run as a complete user-side subagent pipeline.

`first_round_user_profile` means the user's first self-described career profile and materials, not system configuration. It includes whatever the user initially provides about personal status, school, major, grade, experience, skills, projects, competitions, target direction, constraints, concerns, links, files, or resume materials.

Read `subagent-invocation-contract.md` before turning a secondary prompt injection into an actual local subagent call.

## Core Flow

Runtime execution must follow this sequence:

```text
raw first-round user input/materials
  -> InputNormalizer
  -> first_round_user_profile
  -> runtime_context_packet
  -> CareerOrchestrator
  -> secondary_prompt_injections
  -> user-side role subagents
  -> shared evidence packet and debate fields
```

Do not dispatch user-side specialist subagents with only the static `.codex/agents/*.toml` prompt. Each specialist must receive a second injected prompt that is tailored to the first-round user profile.

## Runtime Context Packet

`InputNormalizer` must normalize raw first-round user input/materials into `first_round_user_profile`, then create a reusable context packet that references it and carries compact selected facts:

```json
{
  "first_round_user_profile": {
    "identity_and_contact": {
      "resume_contact_fields_authorized": false,
      "redaction_required_for_intermediate_outputs": true
    },
    "education_status": {
      "school_name": "",
      "college_or_department": "",
      "major_name": "",
      "degree_level": "",
      "grade_or_year": "",
      "graduation_window": ""
    },
    "major_and_discipline": {},
    "internship_experience": [],
    "project_competition_research_experience": [],
    "skills_and_tools": [],
    "external_assets": [],
    "target_direction": {
      "target_roles": [],
      "target_companies": [],
      "target_industries": [],
      "target_locations": [],
      "internship_or_full_time": ""
    },
    "preferences_constraints": [],
    "current_concerns": [],
    "materials_provided": []
  },
  "runtime_context_packet": {
    "packet_id": "",
    "created_from": "first_round_user_profile",
    "first_round_user_profile_ref": "",
    "user_goal": "",
    "known_user_facts": [],
    "candidate_stage": "non_graduating|graduating|graduate|unknown",
    "discipline_domain": "",
    "school_context": {},
    "target_context": {
      "target_roles": [],
      "target_companies": [],
      "target_industries": [],
      "target_locations": [],
      "internship_or_full_time": "",
      "has_concrete_target": false,
      "target_job_fit_requested": false,
      "target_job_title": "",
      "target_company": "",
      "current_jd_text_ref": "",
      "current_jd_text_excerpt": "",
      "current_jd_public_retrieval_required": false,
      "current_fit_assessment_status": "",
      "growth_path_assessment_status": "",
      "fit_vs_growth_policy": ""
    },
    "provided_materials": [],
    "missing_user_owned_facts": [],
    "public_research_needed": [],
    "runtime_weight_questions": [],
    "privacy_constraints": [],
    "consent_flags": {},
    "blocked_outputs": [],
    "next_possible_actions": []
  }
}
```

The packet should be compact enough to pass to every user-side subagent, but specific enough to prevent generic advice.

## Secondary Prompt Injection

`CareerOrchestrator` must turn the runtime context packet into role-specific injected prompts:

```json
{
  "secondary_injection_status": "ready|blocked",
  "secondary_injection_blockers": [],
  "secondary_prompt_injections": [
    {
      "target_agent": "",
      "base_prompt_ref": ".codex/agents/<agent>.toml",
      "runtime_context_packet_ref": "",
      "role_specific_context": {},
      "allowed_user_facts": [],
      "research_tasks": [],
      "hard_data_weight_tasks": [],
      "database_files_to_read": [],
      "source_policy_refs": [],
      "invocation_contract": {
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
        "on_failure": "return_blocked|rerun_with_more_context|handoff_to_orchestrator"
      },
      "blocked_outputs": [],
      "required_output_fields": [],
      "handoff_contract": [],
      "debate_contract": []
    }
  ]
}
```

Each injected prompt must include:

- `universal_runtime_guardrails`, automatically injected for every specialist role. This does not add a user-facing step; it is an internal controller guardrail that stabilizes subagent behavior.
- the user's first-round profile, goal, and known facts relevant to that role.
- the role's exact scope and prohibitions from its static prompt.
- the smallest static database subset needed by that role.
- public/official network research tasks the role should run locally.
- missing user-owned facts that must not be fabricated.
- for concrete job or internship requests, target JD/company context, blocked current-fit fields, and the rule that current readiness must be separated from learnable growth path.
- hard-data weight requirements and `weight_provenance` expectations.
- handoff fields for downstream roles.
- debate fields for challenging weak evidence.

## Universal Runtime Guardrails

Every secondary prompt injection must include `role_specific_context.universal_runtime_guardrails`. The controller injects it automatically before any role-specific instructions.

```json
{
  "universal_runtime_guardrails": {
    "must_follow_secondary_injection": true,
    "role_scope_boundary": "perform_assigned_role_only",
    "handoff_instead_of_overreach": true,
    "no_file_write_by_default": true,
    "tool_use_requires_explicit_permission": true,
    "do_not_modify_user_assets_without_authorized_operation_context": true,
    "do_not_publish_push_or_deploy_without_separate_user_authorization": true,
    "no_fabrication": true,
    "source_required_for_weights_scores_rankings": true,
    "blocked_outputs_must_remain_blocked": true,
    "must_return_structured_json": true,
    "if_uncertain_return_needs_context_or_blocked": true,
    "privacy_constraints_are_binding": true
  }
}
```

The guardrails apply to all roles. Ordinary roles must not modify files, publish pages, push repositories, or bypass blocked outputs. They should hand off file or asset modification requests to `resume-polisher` or `portfolio-asset-builder`, and those roles still need their authorized operation context before writing.

## Secondary-Injected File Operations

Static role prompts may describe file-editing capability, but real local modification must be authorized through the secondary prompt injection. The orchestrator must not ask `ResumePolisher` or `PortfolioAssetBuilder` to infer write permissions from chat tone alone.

For `resume-polisher`, include `role_specific_context.authorized_resume_editing`:

```json
{
  "authorized_resume_editing": {
    "requires_explicit_user_authorization": true,
    "operation_mode": "plan_only_until_user_authorizes_paths|apply_authorized_local_changes",
    "authorization_status": "missing_or_planning_only|granted_for_local_edits",
    "allowed_input_refs": [],
    "allowed_output_refs": [],
    "allowed_actions": [],
    "apply_tool_ref": "scripts/apply_resume_polish.py",
    "resume_edit_operation_steps": [],
    "prohibited_operations": []
  }
}
```

Required output fields for this mode: `resume_edit_operation_plan`, `applied_resume_artifacts`, and `file_modification_summary`. If `operation_mode` is `plan_only_until_user_authorizes_paths`, the role returns a plan and asks for path authorization. If `operation_mode` is `apply_authorized_local_changes`, it may call `apply_tool_ref` with an operation packet and must write only to `allowed_output_refs`.

For `portfolio-asset-builder`, include `role_specific_context.authorized_asset_editing`:

```json
{
  "authorized_asset_editing": {
    "requires_explicit_user_authorization": true,
    "operation_mode": "plan_only_until_user_authorizes_root|apply_authorized_local_changes",
    "authorization_status": "missing_or_planning_only|granted_for_local_edits",
    "allowed_root": "",
    "allowed_actions": [],
    "apply_tool_ref": "scripts/apply_portfolio_asset_changes.py",
    "asset_edit_operation_steps": [],
    "prohibited_operations": []
  }
}
```

Required output fields for this mode: `website_or_github_modification_plan`, `applied_asset_changes`, and `file_modification_summary`. If `operation_mode` is `plan_only_until_user_authorizes_root`, the role returns a plan and asks for root/action authorization. If `operation_mode` is `apply_authorized_local_changes`, it may call `apply_tool_ref` with relative-path changes and must write only inside `allowed_root`.

Both roles must hand off applied artifact refs to `FactualReviewer` and `HRSupervisor`; `portfolio-asset-builder` should also hand off resume-facing link changes to `ResumePolisher`.

## Completeness Requirements

Before a specialist subagent runs, the orchestrator should verify:

- `runtime_context_packet_ref` is present.
- role-specific context is non-empty.
- source policy and privacy boundaries are included.
- `universal_runtime_guardrails` is present in `role_specific_context`.
- hard-data weight tasks are explicit when the role may set weights, priorities, rankings, scores, thresholds, or confidence.
- `invocation_contract` can be deterministically transformed into the canonical `subagent_invocation`: it has `invocation_id`, `input_packet_ref`, `allowed_user_facts_ref`, `output_artifact_target`, `privacy_constraints`, `expected_artifact_types`, required log events, retry policy, and `on_failure`.
- blocked outputs are listed when user-owned facts or public evidence are missing.
- the required output contract is named.

If these are missing, do not dispatch the specialist. Return `secondary_injection_status = "blocked"`, list `secondary_injection_blockers`, and request the missing context or research task.

## Prohibitions

- Do not let a user-side subagent rely only on the static role prompt.
- Do not pass all user data to every role. Minimize by role.
- Do not include private contact details in intermediate injections unless the target role needs them and the user authorized them.
- Do not let a subagent set weights without hard-data provenance.
- Do not let a subagent continue a downstream decision when its required injected context is missing.
