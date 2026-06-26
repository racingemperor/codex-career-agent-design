# Runtime Subagent Injection Protocol

This protocol ensures the repository's role frameworks can run as a complete user-side subagent pipeline.

`first_round_user_profile` means the user's first self-described career profile and materials, not system configuration. It includes whatever the user initially provides about personal status, school, major, grade, experience, skills, projects, competitions, target direction, constraints, concerns, links, files, or resume materials.

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
      "internship_or_full_time": ""
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
      "blocked_outputs": [],
      "required_output_fields": [],
      "handoff_contract": [],
      "debate_contract": []
    }
  ]
}
```

Each injected prompt must include:

- the user's first-round profile, goal, and known facts relevant to that role.
- the role's exact scope and prohibitions from its static prompt.
- the smallest static database subset needed by that role.
- public/official network research tasks the role should run locally.
- missing user-owned facts that must not be fabricated.
- hard-data weight requirements and `weight_provenance` expectations.
- handoff fields for downstream roles.
- debate fields for challenging weak evidence.

## Completeness Requirements

Before a specialist subagent runs, the orchestrator should verify:

- `runtime_context_packet_ref` is present.
- role-specific context is non-empty.
- source policy and privacy boundaries are included.
- hard-data weight tasks are explicit when the role may set weights, priorities, rankings, scores, thresholds, or confidence.
- blocked outputs are listed when user-owned facts or public evidence are missing.
- the required output contract is named.

If these are missing, do not dispatch the specialist. Return `secondary_injection_status = "blocked"`, list `secondary_injection_blockers`, and request the missing context or research task.

## Prohibitions

- Do not let a user-side subagent rely only on the static role prompt.
- Do not pass all user data to every role. Minimize by role.
- Do not include private contact details in intermediate injections unless the target role needs them and the user authorized them.
- Do not let a subagent set weights without hard-data provenance.
- Do not let a subagent continue a downstream decision when its required injected context is missing.
