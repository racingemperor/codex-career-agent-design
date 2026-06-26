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
  "repository_prior_usage": [],
  "weight_provenance": [],
  "blocked_outputs": [],
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

`repository_prior_usage` and `weight_provenance` must state whether a static database was used only as a prior. Repository priors must never be the sole basis for `fit_score`, `priority`, `asset_priority`, `skill_priority_weights`, or HR/company judgments.

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

## Input Normalization Fields

The first stage should expose:

```json
{
  "input_type": "chat_brief|resume_text|markdown_file|pdf_docx|personal_website|github_or_portfolio|jd_text|jd_link|mixed|unknown",
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
  }
}
```

Do not hard-code concrete skill or external-display requirements from repository examples alone. Let local subagents research current role, company, school, and discipline evidence, then configure weights at runtime.

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
