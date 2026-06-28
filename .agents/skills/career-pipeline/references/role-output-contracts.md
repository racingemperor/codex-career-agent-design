# Role Output Contracts

All role outputs should be structured enough for the orchestrator to merge.

Role prompts in this repository are frameworks for runtime local subagents. They define what to collect, which evidence is required, how to share context, and when to hand off. They should not make final career, company, market, learning, branding, HR, or resume-positioning judgments from repository priors alone.

## Common Fields

Every role should include:

```json
{
  "role": "",
  "task_summary": "",
  "inputs_used": [],
  "database_files_used": [],
  "source_notes": [],
  "runtime_scope": "evidence_collection|procedural_gate|conditional_runtime_judgment|drafting_from_user_facts|fact_checking",
  "judgment_allowed": "none|procedural_only|conditional_with_runtime_evidence|evidence_bound_only",
  "judgment_status": "framework_only|runtime_evidence_required|ready_for_runtime_judgment|evidence_bound_judgment|blocked",
  "decision_owner": "local_subagent|user|factual_reviewer|hr_supervisor|orchestrator|none",
  "runtime_preconditions": {
    "has_current_jd": false,
    "has_target_company": false,
    "has_user_constraints": false,
    "has_user_consent": false,
    "job_direction_blocked": false
  },
  "evidence_basis": [],
  "artifact_refs": [],
  "execution_log_refs": [],
  "invocation_ref": "",
  "role_output_packet_ref": "",
  "error_recovery_state_ref": "",
  "repository_prior_usage": [],
  "weight_provenance": [],
  "blocked_outputs": [],
  "degraded_outputs": [],
  "conditional_options": [],
  "runtime_research_tasks": [],
  "evidence_requirements": [],
  "shared_context_refs": [],
  "handoff_to": [],
  "confidence": "high|medium|low",
  "needs_user_confirmation": []
}
```

Use `evidence_bound_judgment` only when the judgment is limited to supplied user materials, current JD text, current public evidence gathered by runtime subagents, or a static taxonomy/schema lookup. Use `runtime_evidence_required` or `blocked` when current evidence or user-owned facts are missing.

Use `artifact_refs`, `execution_log_refs`, `invocation_ref`, `role_output_packet_ref`, and `error_recovery_state_ref` for traceability. A role output that cannot be tied to a run, invocation, artifact, or role output packet should not be merged into a final package.

Each `evidence_basis` item should identify the supported claim:

```json
{
  "claim_id": "",
  "field": "",
  "source_type": "user_provided|official_or_primary|recruitment_platform_jd|verified_hr_public_post|candidate_experience_secondary|social_media_weak|repository_prior|inference",
  "source_ref": "",
  "user_owned_or_public": "user_owned|public|repository",
  "evidence_strength": "strong|medium|weak|missing",
  "inference_level": "none|low|medium|high",
  "confidence": "high|medium|low"
}
```

`repository_prior_usage` and `weight_provenance` must state whether a static database was used only as a prior. Repository priors must never be the sole basis for `fit_score`, `priority`, `asset_priority`, `skill_priority_weights`, `external_asset_weights`, `school_signal_weights`, or HR/company judgments.

For concrete job or internship requests, roles should separate:

- `current_fit_assessment`: evidence-bound current suitability for the exact target role.
- `skill_gap_analysis`: must-have, nice-to-have, evidence, and narrative gaps against the current JD.
- `learning_plan_before_application`: skills, projects, proof artifacts, and completion conditions needed before applying.
- `application_readiness_decision`: apply now, prepare first, or skip only when current JD/public evidence and user evidence are sufficient.
- `application_url_candidates`: public URL candidates that let the user inspect official, school, public JD, or verified HR sources.
- `ask_hr_about`: missing operational details the public page does not state, such as opening status, city, onsite days, arrival time, deadline, headcount, or internship duration.
- `blocked_application_targets_without_public_url`: targets that cannot be shown as concrete application recommendations yet.
- `project_recommendations`: concrete project suggestions when the user lacks project evidence or needs prepare-first proof artifacts.
- `hr_real_question_bank`: target or recommended company HR public wording or recruiter screening questions, with source-bound provenance.

If current JD evidence is missing, exact fit score, final priority, targeted resume tailoring, and company-specific skill weights must be blocked or marked `not_available` rather than inferred from repository priors. Safe preparation-first, exploration, learning-path, and public-URL recommendations may still be returned with limitations stated.

For finalization, blocked exact fields may remain in `blocked_outputs` without blocking the whole package when the role status is `done_with_warnings` and the safe outputs are present. Non-exact blockers such as missing user consent, missing public URL evidence for a displayed target, malformed role output, failed factual review, or incomplete resume consent still block final readiness.

Recommended jobs, internships, or application targets must follow `application-url-output-policy.md`. A user-facing concrete target should not appear in `recommended_application_targets` unless it includes a source-policy-valid public URL candidate. Official entrypoints can support exploration, public JD or JD text can support prepare-first, and role-specific `apply_now`, exact fit score, and resume tailoring require stronger current JD plus user evidence.

Every proposed parameter weight, score, priority, ranking, threshold, or confidence adjustment must be supported by hard data. A role must not set weights by intuition, popularity assumptions, or model-only reasoning. If runtime public/official network evidence or user-provided materials are missing, set the weight status to `not_available` or `needs_more_sources`, add `runtime_research_tasks`, and block downstream decisions that depend on that weight.

Concrete project recommendations should use:

```json
{
  "project_selection_rubric": {
    "role_fit": "",
    "completion_speed": "",
    "implementation_cost": "",
    "resume_value": "",
    "interview_depth": "",
    "public_evidence_quality": "",
    "risk_control": ""
  },
  "project_recommendations": [
    {
      "project_name": "",
      "target_role_family": "",
      "recommended_project_mode": "interview-only|smoke-test|local-full-run|remote-full-run",
      "why_this_project": "",
      "implementation_steps": [],
      "proof_artifacts": [],
      "resume_conversion_conditions": [],
      "interview_defensibility_questions": [],
      "candidate_discovery_ref": "",
      "source_audit_ref": "",
      "project_interview_pack_ref": "",
      "source_basis": [],
      "risk_notes": []
    }
  ]
}
```

Project recommendations are preparation guidance, not proof that the user has completed work. Planned work `must not be written as completed resume claims`. When the recommendation depends on an open-source or public project, use `discover_project_candidates.py` or an equivalent candidate-discovery artifact to avoid shallow wrappers and star-count traps, then use `audit_project_repository.py` or equivalent local source audit before treating project claims as source-verified. `build_project_interview_pack.py` can produce the project positioning, existing capability, suggested modifications, resume-ready claims, STAR bullets, interviewer follow-ups, and core-code explanation paths. ResumeArchitect and FactualReviewer may only convert a project into resume content after proof artifacts exist and the user can explain personal contribution, input/output, core modules, and failure boundaries.

HR real questions should use:

```json
{
  "hr_real_question_bank": [
    {
      "company": "",
      "role_family": "",
      "question": "",
      "question_type": "resume_screen|project_depth|motivation|technical_foundation|internship_availability|culture_or_values|other",
      "source_ref": "",
      "source_type": "official_or_primary|verified_hr_public_post|recruitment_platform_jd",
      "source_accuracy_tier": "A|B",
      "verbatim_or_paraphrase": "verbatim_short_excerpt|paraphrase",
      "preparation_focus": "",
      "not_model_generated": true
    }
  ],
  "likely_interview_questions": [
    {
      "company": "",
      "question": "",
      "source_ref": "",
      "source_accuracy_tier": "A|B",
      "not_model_generated": true
    }
  ],
  "resume_defensibility_checks": []
}
```

`hr_real_question_bank` must be target or recommended company-bound. It is an evidence extraction field, not a generic interview-question generation field. do not generate HR wording yourself. Do not borrow questions from unrelated companies, interview-prep blogs, model memory, or candidate-only social posts. Valid direct support includes official/primary recruiting pages, official-listed recruiter posts, enterprise-certified recruiting accounts, public recruitment-platform process notes, and verified HR public posts tied to the target company or recommended company. candidate experience and social media weak signals are preparation only; they must not be presented as company HR wording or final requirements. If target or recommended company public HR wording is unavailable, return an empty question bank, a limitation, and runtime research tasks for that exact company or recommended company.

Each `weight_provenance` item should use:

```json
{
  "parameter": "",
  "proposed_weight": null,
  "weight_status": "verified|needs_more_sources|not_available",
  "source_refs": [],
  "source_types": [
    "current_jd|official_company_page|official_campus_page|recruitment_platform_jd|verified_hr_public_post|official_school_notice|public_report|multi_source_candidate_signal|user_provided|repository_prior"
  ],
  "retrieved_or_published_dates": [],
  "sample_size_or_source_count": "",
  "evidence_strength": "strong|medium|weak|missing",
  "confidence": "high|medium|low",
  "cannot_decide_alone": true
}
```

Use `cannot_decide_alone = true` for repository priors, single weak social posts, stale sources, or model inference.

## Runtime Execution And Artifact Fields

Runtime wrappers should preserve these fields when available:

```json
{
  "execution_manifest": {
    "run_id": "",
    "current_stage": "intake_received|input_normalized|context_packet_created|injection_ready|agents_running|merge_pending|debate_required|hr_review_required|factual_review_required|user_confirmation_required|blocked|final_package_ready",
    "runtime_context_packet_ref": "",
    "secondary_prompt_injection_refs": [],
    "subagent_invocation_refs": [],
    "artifact_manifest_ref": "",
    "artifact_refs": [],
    "evidence_packet_refs": [],
    "runtime_weights_ref": "",
    "error_recovery_state_ref": "",
    "final_package_ref": ""
  },
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
    "expected_artifact_types": [],
    "required_log_events": [],
    "privacy_constraints": [],
    "handoff_contract": [],
    "debate_contract": [],
    "timeout_or_budget_hint": "",
    "retry_allowed": true,
    "on_failure": "return_blocked|rerun_with_more_context|handoff_to_orchestrator",
    "status": "not_started|running|done|blocked|failed|malformed"
  },
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
    "errors": []
  },
  "artifact_refs": [],
  "execution_log_refs": []
}
```

The canonical schemas live in `runtime-execution-layer.md`, `subagent-invocation-contract.md`, and `runtime-artifact-schema.md`. Role prompts may return references instead of embedding entire artifacts.

Artifact references should include `artifact_id`, `run_id`, `artifact_type`, `path`, `created_by`, `privacy_class`, and safety flags when material is persisted locally. Runtime logs should be redacted by default.

Specialist role prompts should return `role_output_packet` and `error_recovery_state` inline when no runtime wrapper is present. When a wrapper is present, the wrapper may persist those objects and the role output may return `role_output_packet_ref` and `error_recovery_state_ref`; the orchestrator must resolve the refs before merging.

## Error Recovery Fields

When a role blocks, fails, returns malformed output, or produces only safe partial output, expose:

```json
{
  "error_recovery_state": {
    "status": "not_applicable|recovered|degraded|needs_user_confirmation|needs_public_research|blocked|failed",
    "errors": [],
    "recovery_actions": [],
    "degraded_outputs": [],
    "blocked_outputs": [],
    "safe_outputs": [],
    "next_action": "continue|ask_user_once|run_public_research|retry_agent|run_debate|run_hr_review|run_factual_review|return_blocked_package"
  }
}
```

If output is degraded, downstream roles may merge safe factual fields, `evidence_basis`, `blocked_outputs`, and `runtime_research_tasks`, but must not merge final fit scores, application priorities, HR pass status, or resume tailoring decisions that depend on the failed evidence.

## Collaboration And Debate Fields

Roles that prepare or challenge fit, learning, branding, resume structure, HR readability, or factual-risk decisions should also include:

```json
{
  "agent_claims": [],
  "evidence_challenges": [],
  "disagreements_with": [
    {
      "agent": "",
      "field": "",
      "reason": "",
      "requested_resolution": ""
    }
  ],
  "handoff_questions": []
}
```

Use these fields when one role challenges another role's claim or when a conclusion depends on missing runtime evidence. Do not silently erase disagreements. If a conflict depends on missing user evidence, return a user-confirmation point instead of forcing a final recommendation. If a conflict depends on public or official evidence, create `runtime_research_tasks` and hand off to the responsible local subagent.

## User-Facing Package Fields

The final user-visible result should be exposed through `user_facing_package`. Internal packages may keep `blocked_outputs`, `degraded_outputs`, run directories, invocation references, execution logs, role packets, and schema details for traceability; `user_facing_package` must translate those internals into concise professional Chinese.

Use this shape:

```json
{
  "user_facing_package": {
    "positioning_conclusion": "",
    "task_type": "",
    "evidence_status": "",
    "recommended_targets": [
      {
        "company": "",
        "title_or_role_family": "",
        "scenario": "apply_now|prepare_first|explore|skip",
        "public_urls": [],
        "why_this_target": "",
        "ask_hr_about": []
      }
    ],
    "public_source_index": [
      {
        "title": "",
        "url": "",
        "source_type": "",
        "source_accuracy_tier": "A|B|C|D",
        "may_support_application_claims": false,
        "note": ""
      }
    ],
    "gaps_to_fix_before_application": [],
    "project_recommendations": [],
    "hr_real_questions": [],
    "likely_interview_questions": [],
    "resume_reverse_design": "",
    "resume_draft": {},
    "growth_resume_preview": {},
    "ask_hr_about": [],
    "currently_unavailable": [],
    "next_three_actions": []
  }
}
```

Rules:

- `recommended_targets` must not include a target with empty `public_urls`.
- translate raw `blocked_outputs` into `currently_unavailable` using user-friendly wording.
- do not include run directories, execution logs, raw role packets, or schema names.
- keep `next_three_actions` to exactly three items when possible.
- planned learning can appear as a gap or proof-artifact task, but not as a completed resume claim.
- `resume_draft` is the current factual resume version. `growth_resume_preview` is optional and must be labeled as an after-learning/project preview; its recommended skills or projects cannot be treated as completed resume facts until proof artifacts exist.
- if no target job exists, use exploration targets, role families, learning gaps, and broad campus resume guidance instead of fake precision.

The final rendered natural-language result should also be available as `user_facing_report_zh`. It must use these exact headings:

```text
## 当前定位
## 推荐方向/岗位池
## 为什么适合
## 还差什么
## 先学什么/做什么项目
## 简历怎么写
## HR/面试可能追问
## 推荐查看的公开 URL
## 需要问 HR 的事项
## 下一步 3 个动作
```

`user_facing_report_zh` is what a normal user should read. It must not mention subagent, JSON, runner, runtime, schema, raw role packets, run directories, or `blocked_outputs` unless the user is explicitly debugging the pipeline.

## Input Normalization Fields

The first stage should expose:

```json
{
  "input_type": "chat_brief|resume_text|markdown_file|pdf_docx|personal_website|github_or_portfolio|jd_text|jd_link|mixed|unknown",
  "first_round_user_profile": {
    "definition": "User-provided first-round self-profile, status, experience, goals, concerns, links, files, and resume materials; not system configuration.",
    "identity_and_contact": {},
    "education_status": {},
    "major_and_discipline": {},
    "internship_experience": [],
    "project_competition_research_experience": [],
    "skills_and_tools": [],
    "external_assets": [],
    "target_direction": {},
    "preferences_constraints": [],
    "current_concerns": [],
    "materials_provided": []
  },
  "runtime_context_packet": {
    "packet_id": "",
    "created_from": "first_round_user_profile",
    "first_round_user_profile_ref": "",
    "known_user_facts": [],
    "missing_user_owned_facts": [],
    "public_research_needed": [],
    "runtime_weight_questions": [],
    "privacy_constraints": [],
    "blocked_outputs": [],
    "next_possible_actions": []
  },
  "known_information_summary": "",
  "next_possible_actions": [],
  "candidate_stage": "non_graduating|graduating|graduate|unknown",
  "school_context": {},
  "application_scenarios": {
    "internship": {},
    "future_full_time": {},
    "current_full_time": {}
  },
  "missing_user_owned_facts": [],
  "one_round_followup_prompt": "",
  "job_direction_blocked": false
}
```

Use these fields to support vague chat introductions, complete files, websites, Markdown, links, and mixed materials without forcing the user into repeated Q&A. `next_possible_actions` should tell the user what can be done with current information before asking for missing facts.

`first_round_user_profile` is the normalized form of what the user initially says or provides about themselves, such as school, major, grade, personal status, internship, projects, competitions, skills, target direction, constraints, and current concerns. Keep private contact details redacted in intermediate outputs unless the resume role explicitly needs them and the user authorized final resume contact fields.

## Runtime Subagent Injection Fields

Before user-side specialist subagents run, the orchestrator should expose:

```json
{
  "runtime_context_packet_ref": "",
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
  ],
  "secondary_injection_status": "ready|blocked",
  "secondary_injection_blockers": []
}
```

Each injected prompt must be derived from `runtime_context_packet`, the target role's static prompt, and the smallest relevant database subset. Do not dispatch a specialist with only the static role prompt. Do not pass all user data to every role; minimize private and irrelevant facts by role.

## Runtime Orchestration Fields

Pipeline-level orchestration should expose:

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

Use `run_state` to prevent silent stage skipping. If a required gate is missing, return `blocked` or keep the current stage with explicit blockers.

## User Interaction Fields

User-facing intake and follow-up steps should expose:

```json
{
  "user_interaction_state": {
    "interaction_mode": "resume_only|direction_analysis|targeted_application|learning_plan|personal_branding|unknown",
    "information_completeness": "sufficient|partial|insufficient",
    "user_followup_policy": "one_round_only",
    "known_information_summary": "",
    "next_possible_actions": [],
    "missing_user_owned_facts": [],
    "subagent_research_not_asked_from_user": [],
    "incomplete_resume_consent_required": false,
    "incomplete_resume_allowed": false,
    "application_direction_allowed": false,
    "blocked_outputs": [],
    "one_round_followup_prompt": ""
  }
}
```

Use this state to keep first responses concise: summarize known facts, explain what can and cannot be done, then ask one compact batch for missing user-owned facts only when needed.

## Parameter Ownership Fields

Roles that ask questions, research public data, or set weights should expose:

```json
{
  "parameter_ownership": {
    "user_required_minimal": [],
    "user_optional": [],
    "subagent_research": [],
    "runtime_weight_config": []
  },
  "runtime_weight_config": {
    "skill_weights": [],
    "external_asset_weights": [],
    "school_signal_weights": []
  },
  "runtime_weights": [
    {
      "parameter": "",
      "weight_scope": "skill_weight|external_asset_weight|school_signal_weight|application_strategy_weight|hr_screening_weight",
      "proposed_weight": null,
      "weight_unit": "0_to_1|percentage|rank|tier|qualitative",
      "weight_status": "verified|needs_more_sources|not_available",
      "evidence_basis": [],
      "source_count": 0,
      "source_mix": [],
      "freshness": "0_6_months|6_12_months|1_3_years|older|unknown",
      "conflict_notes": [],
      "confidence": "high|medium|low",
      "cannot_decide_alone": true,
      "runtime_research_tasks": []
    }
  ]
}
```

Do not hard-code concrete skill or external-display requirements from repository examples alone. Let local subagents research current role, company, school, and discipline evidence from public/official network sources or user-provided materials, then configure weights at runtime only when `weight_provenance` is sufficient.

## HR Supervision Status

HR-supervised steps should expose:

```json
{
  "company_hr_signal_refs": [],
  "target_company_screening_bias": [],
  "big_tech_hr_screening_notes": [],
  "competitive_signal_summary": [],
  "hr_first_screen_risks": [],
  "hr_readability_score": null,
  "positioning_verdict": "pass|revise|required_user_confirmation",
  "pass_to_next_stage": false
}
```

`HRSupervisor` checks whether the pipeline output is understandable, credible, and competitive from a first-screen HR perspective. `positioning_verdict` is a runtime process status for presentation readiness, not a final hiring or career-fit verdict. It cannot override `FactualReviewer` on truthfulness.

When company-specific or big-company screening evidence is missing, `HRSupervisor` should mark `judgment_status = "runtime_evidence_required"` and use company-signal databases only as priors or source-collection guides.

## Evidence Notes

Use `source_notes` to distinguish:

- `official_or_primary`
- `recruitment_platform_jd`
- `verified_hr_public_post`
- `candidate_experience_secondary`
- `social_media_weak`
- `user_provided`
- `inference`

Application URL evidence should use:

```json
{
  "application_url_candidates": [
    {
      "url": "",
      "source_type": "official_or_primary|official_school_notice|recruitment_platform_jd|verified_hr_public_post",
      "source_priority": 1,
      "title": "",
      "company": "",
      "role_family": "",
      "current_or_entrypoint": "current_jd|official_search_entrypoint|campus_entrypoint|school_notice|public_jd",
      "retrieved_or_verified_at": "",
      "requires_login": false,
      "may_support_apply_recommendation": false,
      "confidence": "high|medium|low",
      "notes": ""
    }
  ],
  "blocked_application_targets_without_public_url": []
}
```

## Resume Approval Status

Resume-producing steps must use:

```json
{
  "format_gate_status": "pass|revise_required|user_confirmation_required",
  "format_status": "accepted|rejected|needs_user_confirmation",
  "factual_review_status": "not_reviewed|pass|revise|required_user_confirmation",
  "incomplete_resume_allowed_with_user_consent": false,
  "incomplete_resume": false,
  "job_direction_blocked": false
}
```

`ResumeFormatGate` sets the procedural drafting gate. It checks whether supplied materials satisfy the format and evidence-readiness schema. `ResumeArchitect` cannot mark final approval. Only `FactualReviewer` can mark the final resume as `pass`.

If the user refuses to provide missing information, incomplete resume drafting requires explicit consent. Missing sections must be omitted rather than filled with placeholders, and application direction recommendations must remain blocked.
