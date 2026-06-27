# Runtime Execution Layer

This protocol defines the local execution shell for a Codex-native career pipeline. It is a design contract, not a deployed runner.

## Scope

The execution layer coordinates a local run. It does not make career judgments. It:

- creates a run manifest.
- records input and output artifacts.
- invokes role subagents from `.codex/agents/*.toml`.
- enforces prompt-injection, privacy, source, weight, debate, HR, and factual gates.
- tracks errors, degraded outputs, and blocked outputs.

Do not hide required state in chat history. Any state needed by another role should be written as a structured artifact or referenced by an `artifact_ref`.

## Execution Sequence

Use this sequence for a full user-side run:

```text
create run_id and run directory
  -> capture user input/material references
  -> invoke InputNormalizer
  -> persist first_round_user_profile and runtime_context_packet
  -> invoke CareerOrchestrator to create secondary_prompt_injections
  -> convert each secondary_prompt_injection into a subagent invocation packet
  -> build subagent prompt bundles from static role prompts, runtime context, allowed facts, source policy, and output contracts
  -> build a public-source research plan before any network-enabled research
  -> discover allowed public source URLs from a search adapter
  -> fetch and backfill allowed public evidence when network is enabled
  -> dispatch required role subagents by batch, persisting artifacts and closing completed subagents between batches
  -> validate role outputs against role-output-contracts
  -> merge evidence, blocked outputs, runtime weights, and debate fields
  -> run debate routes when conflicts remain
  -> run HRSupervisor for presentation readiness
  -> run ResumeFormatGate, ResumeArchitect, and FactualReviewer when a resume is produced
  -> produce final decision package or blocked package
```

Specialist subagents must not run before `runtime_context_packet` and `secondary_prompt_injections` exist.

## Execution Manifest

Each run should create a manifest:

```json
{
  "execution_manifest": {
    "run_id": "",
    "created_at": "",
    "updated_at": "",
    "codex_surface": "desktop|cli|plugin|unknown",
    "repository_ref": "",
    "skill_ref": ".agents/skills/career-pipeline/SKILL.md",
    "task_type": "resume_review|resume_generation|job_search|jd_analysis|company_research|tailored_resume|major_positioning|personal_branding|learning_plan|target_job_fit",
    "user_goal_summary": "",
    "privacy_mode": "redacted_intermediate|user_authorized_final_contact|strict_no_contact",
    "run_dir_ref": "",
    "current_stage": "intake_received|input_normalized|context_packet_created|injection_ready|agents_running|merge_pending|debate_required|hr_review_required|factual_review_required|user_confirmation_required|blocked|final_package_ready",
    "runtime_context_packet_ref": "",
    "secondary_prompt_injection_refs": [],
    "subagent_invocation_refs": [],
    "artifact_manifest_ref": "",
    "artifact_refs": [],
    "evidence_packet_refs": [],
    "runtime_weights_ref": "",
    "gate_status": {
      "input_normalized": false,
      "context_packet_created": false,
      "secondary_injections_created": false,
      "specialists_completed_or_blocked": false,
      "debate_completed_or_recorded": false,
      "hr_review_completed": false,
      "factual_review_completed_when_needed": false,
      "user_confirmation_resolved_when_needed": false
    },
    "error_recovery_state_ref": "",
    "final_package_ref": ""
  }
}
```

`repository_ref` may be a git commit hash, branch name, or local path when git metadata is unavailable.

`execution_manifest.current_stage` must equal `run_state.stage` for the same run. If they differ, the orchestrator should mark the run as `schema_validation_failed` and repair the manifest before dispatching more agents.

## Stage Responsibilities

- `InputNormalizer`: normalize free-form user materials, produce `first_round_user_profile`, `runtime_context_packet`, and one compact missing-fact prompt.
- `CareerOrchestrator`: choose route, create `secondary_prompt_injections`, and create the subagent invocation plan.
- role subagents: collect or check role-specific evidence, output structured role packets, and avoid cross-role decisions.
- merge step: combine evidence and conflicts without erasing disagreements.
- HR gate: check first-screen readability, credibility, and competitive signal clarity.
- factual gate: check truthfulness, privacy, overclaiming, and interview defensibility.

## Completion Rules

Return `final_package_ready` only when every required gate for the requested final output is completed or documented as not applicable.

Do not mark a run as `final_package_ready` when a required gate is blocked. If a required gate is blocked, return `blocked` with a `blocked_package`. If safe partial outputs exist, return a degraded or blocked package that names those outputs rather than a final package.

If a required role fails or evidence is missing, return a blocked or degraded package with:

- exact blocked outputs.
- missing user-owned facts, if any.
- public research tasks, if any.
- degraded outputs that remain safe to show.
- next action for the orchestrator or user.

## Local Runner Contract

This repository ships a deterministic local execution shell for contract testing and safe handoff, but it does not yet ship a real Codex subagent adapter. The shell should expose this contract:

```json
{
  "runner_request": {
    "command": "career-pipeline-run",
    "mode": "simulate|execute",
    "task_type": "",
    "input_refs": [],
    "allowed_network": true,
    "run_dir": ".career-pipeline-runs/<run_id>",
    "requested_outputs": []
  },
  "runner_response": {
    "exit_status": "success|blocked|degraded|failed",
    "run_id": "",
    "execution_manifest_ref": "",
    "final_package_ref": "",
    "blocked_package_ref": "",
    "error_recovery_state_ref": ""
  }
}
```

The repository one-command runner returns the same status in a more artifact-rich envelope:

```json
{
  "career_pipeline_run_response": {
    "exit_status": "success|blocked|degraded|failed",
    "run_id": "",
    "run_dir_ref": "",
    "real_subagent_execution": false,
    "source_discovery_ready": false,
    "blocked_by": [],
    "execution_manifest_ref": "manifest.json",
    "blocked_package_ref": "final/blocked_package.json",
    "source_plan_ref": "",
    "query_plan_ref": "",
    "search_results_ref": "",
    "allowed_sources_ref": "",
    "subagent_plan_ref": "",
    "work_orders_ref": "",
    "adapter_output_refs": [],
    "final_package_ref": "",
    "next_action": ""
  }
}
```

Do not set `real_subagent_execution = true` or provide a final package from the one-command runner until a configured adapter has produced role outputs, those outputs pass schema checks, and the required merge, HR, factual, source-policy, and weight-provenance gates have completed.

Suggested exit semantics:

- `success`: final package is ready and required gates passed.
- `blocked`: final package is not produced; blocked package explains missing user facts, public research, consent, or failed gates.
- `degraded`: only safe partial outputs are available.
- `failed`: runner or schema validation failed before a safe package could be produced.

For Codex network configuration, source-policy acknowledgement, and real adapter options, read `runtime-network-and-adapter-setup.md` before moving from simulation to execution.

## Non-Goals

- This protocol does not require a specific CLI command, but the repository provides `career_pipeline_run.py` as a deterministic local runner that follows this contract.
- This protocol does not require network access for every run.
- This protocol does not store private user data in git.
- This protocol does not replace the source policy, weight engine, or role output contracts.

## Current Local Scripts

- `career_pipeline_run.py`: one-command deterministic user-side runner. It chains simulation, prompt-bundle generation, public-source planning, source search, allowed-source discovery, work-order export, subagent adapter execution, and optional finalization. It returns `blocked` for the default seed/mock path and returns `success` only when `--finalize` runs after real adapter outputs validate.
- `simulate_runtime_run.py`: creates a private no-network blocked run with normalized input, runtime context, secondary injections, invocation packets, blocked package, and simulated blocked role outputs.
- `build_subagent_plan.py`: turns invocation packets into a plan-only dispatch queue with `dispatch_strategy = "batched_artifact_handoff"`, `dispatch_batches`, `max_parallel_subagents`, dependency artifact refs, and close-after-output instructions. Plan-only queues are not proof that subagents ran.
- `build_subagent_prompt_bundle.py`: creates one role-specific derived prompt bundle with the static role prompt, runtime context packet, secondary prompt injection, allowed user facts, source policy, research tasks, hard-data weight tasks, and required output contract. Raw input refs must not appear in the bundle.
- `build_public_source_plan.py`: creates a source-policy-bound research plan for official/primary pages, public recruitment-platform JDs, verified HR public posts, candidate experience, and weak social signals. It does not browse, log in, scrape, or cache sources.
- `discover_public_sources.py`: converts search-adapter results into `evidence/allowed_public_sources.generated.json` and `evidence/public_source_discovery_log.json`. It generates search queries from the source plan, rejects login/private/backend/non-public hints, deduplicates URLs, and keeps social media as weak evidence.
- `search_public_sources.py`: adapter entrypoint for executing generated source queries. The built-in `seed` provider is local and deterministic; it emits candidate URLs from repository source-collection targets and generic public-source entrypoints, not live web results. The `external-json` provider accepts externally produced browser/search/API results and marks them as real-time URL candidates, not evidence packets.
- `fetch_public_sources.py`: fetches allowed public `http(s)` sources or user-provided `file://` snapshots into evidence packets. It refuses forbidden source types, login-only pages, and weak social evidence as final-decision proof.
- `build_subagent_work_orders.py`: exports adapter-ready work orders with prompt bundle refs, batch ids, dependency artifact refs, human/source-policy gates, expected output contracts, close-after-output instructions, and backfill requirements. Work orders are not proof of real subagent execution.
- `run_subagent_adapter.py`: subagent adapter runner entrypoint. `--mock-blocked` writes schema-valid blocked role output packets so the pipeline can test handoff and backfill contracts while preserving `real_subagent_execution = false`. `--adapter-command` invokes an external command per work order, validates returned role outputs, and sets `real_subagent_execution = true` only when all required role outputs are `done` or `done_with_warnings`.
- `finalize_runtime_run.py`: final package assembler. It rejects mock, blocked, failed, malformed, or missing role outputs and writes `final/decision_package.json` only after real adapter metadata, role output statuses, and final gates pass.
- `execute_subagent_plan.py`: defaults to dry-run inspection, refuses real execution without human approval, refuses network execution without source-policy acknowledgement, writes redacted execution events, and can backfill externally produced role outputs only after schema checks.
- `backfill_public_evidence.py`: validates externally collected evidence packets against the public-source plan, rejects forbidden/login-only/weak-final-decision evidence, and appends accepted packets to the run evidence index.
- `continue_runtime_run.py`: accepts one compact batch of user-owned facts and updates the same run so dispatch can continue without starting over.

`target_job_fit` runs should include target job/company/JD context in `runtime_context_packet.target_context`, block `current_fit_assessment`, `application_readiness_decision`, `learning_plan_before_application`, `targeted_resume_tailoring`, `fit_score`, and `application_strategy` until current JD and public/company evidence are available, and keep immediate readiness separate from learnable growth path.

Non-engineering domains currently route through `data/discipline_taxonomy/discipline_registry.zh-CN.json` and return `taxonomy_status = "pending_static_database"` when a domain-specific static taxonomy is not yet implemented. This is intentional degradation: engineering can use the implemented major taxonomy, while science, humanities, social science, business, arts/design, medicine/health, agriculture, law/public affairs, and interdisciplinary domains must block domain-specific taxonomy outputs instead of guessing.

Real subagent execution remains blocked until a concrete adapter is configured and tested. See `runtime-network-and-adapter-setup.md` for Codex Desktop manual-controller, Codex CLI, and API adapter patterns. Any adapter must keep the same privacy, source-policy, weight-provenance, role-output, HR, factual-review, and blocked/final gates.
