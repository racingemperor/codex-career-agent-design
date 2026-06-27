---
name: career-pipeline
description: Use when Codex needs to analyze Chinese majors or discipline domains, career direction, target companies, job descriptions, learning gaps, personal branding, or resumes for campus recruitment and early-career job search.
---

# Career Pipeline

This skill is the main entrypoint for the Codex-native career and resume agent design.

Use it to route user requests across specialized subagents, read the bundled static databases, and return a source-aware decision package. Do not deploy anything from this repository automatically; this repository is the design and prompt source of truth.

## Required References

Read these references as needed:

- `references/data-catalog.md` before using any static database.
- `references/source-policy.md` before analyzing job, company, HR, candidate, or social media information.
- `references/runtime-collaboration-protocol.md` before dispatching or merging role prompts.
- `references/runtime-execution-layer.md` before running, simulating, or implementing the local user-side execution shell.
- `references/runtime-network-and-adapter-setup.md` before enabling real network fetches or real subagent execution.
- `references/runtime-subagent-injection-protocol.md` before creating user-side subagent prompts.
- `references/subagent-invocation-contract.md` before converting a secondary prompt injection into a concrete local subagent invocation.
- `references/runtime-orchestration-protocol.md` before running or simulating the user-side pipeline state machine.
- `references/runtime-artifact-schema.md` before writing, reading, merging, or exposing runtime artifacts, logs, evidence packets, resume drafts, or final packages.
- `references/error-recovery-protocol.md` before retrying, degrading, blocking, or partially merging a failed run.
- `references/user-interaction-flow.md` before asking the user for missing facts or handling incomplete information.
- `references/runtime-weight-engine.md` before proposing, checking, or merging any runtime weight, score, priority, ranking, threshold, or confidence adjustment.
- `references/role-output-contracts.md` before merging subagent outputs.

## Local Contract Scripts

Use these scripts only for local contract validation and simulation. They do not call real subagents, browse recruitment sites, or make career judgments.

Run the scripts from this skill directory, not from the repository root:

```bash
cd .agents/skills/career-pipeline
python scripts/career_pipeline_run.py --task-type target_job_fit --route target_job_fit --input-text "computer science senior, assess fit for Tencent backend role. JD: Java and MySQL" --run-root ../../../.career-pipeline-runs --source-adapter seed --subagent-adapter mock-blocked
python scripts/simulate_runtime_run.py --task-type job_search --route job_search --input-text "computer science sophomore, Python, looking for AI internship" --run-root ../../../.career-pipeline-runs
python scripts/build_subagent_plan.py --run-dir ../../../.career-pipeline-runs/<run_id> --build-prompt-bundles
python scripts/build_public_source_plan.py --run-dir ../../../.career-pipeline-runs/<run_id>
python scripts/discover_public_sources.py --run-dir ../../../.career-pipeline-runs/<run_id> --generate-query-plan-only
python scripts/search_public_sources.py --run-dir ../../../.career-pipeline-runs/<run_id> --provider seed
python scripts/search_public_sources.py --run-dir ../../../.career-pipeline-runs/<run_id> --provider external-json --search-results-json <search_results.json>
python scripts/discover_public_sources.py --run-dir ../../../.career-pipeline-runs/<run_id> --search-results-json <search_results.json>
python scripts/fetch_public_sources.py --run-dir ../../../.career-pipeline-runs/<run_id> --sources-json ../../../.career-pipeline-runs/<run_id>/evidence/allowed_public_sources.generated.json
python scripts/backfill_public_evidence.py --run-dir ../../../.career-pipeline-runs/<run_id> --evidence-json ../../../.career-pipeline-runs/<run_id>/evidence/fetched_public_evidence.json
python scripts/build_subagent_work_orders.py --run-dir ../../../.career-pipeline-runs/<run_id>
python scripts/run_subagent_adapter.py --run-dir ../../../.career-pipeline-runs/<run_id> --mock-blocked
python scripts/run_subagent_adapter.py --run-dir ../../../.career-pipeline-runs/<run_id> --adapter-command <adapter-executable> --adapter-arg <adapter-script-or-config>
python scripts/finalize_runtime_run.py --run-dir ../../../.career-pipeline-runs/<run_id> --real-subagent-execution
python scripts/execute_subagent_plan.py --run-dir ../../../.career-pipeline-runs/<run_id> --dry-run
```

Do not run these commands from the repository root as `scripts/*.py`; the `scripts/` path is relative to `.agents/skills/career-pipeline/`. If already at the repository root, use `.agents/skills/career-pipeline/scripts/<script>.py`.

- `scripts/validate_runtime_contracts.py` validates repository role prompts, secondary prompt injections, canonical subagent invocation packets, execution manifests, and blocked/final gate consistency.
- `scripts/career_pipeline_run.py` is the one-command deterministic user-side runner. With `--source-adapter seed --subagent-adapter mock-blocked`, it creates a complete blocked run with source-discovery artifacts and subagent work orders, but does not claim real subagent execution. With explicit `external-json`, `external-command`, and `--finalize`, it can produce a final package only after role outputs validate.
- `scripts/simulate_runtime_run.py` creates a private ignored `.career-pipeline-runs/<run_id>/` artifact tree for a no-network blocked run, useful for checking runtime packet shape before building a real runner.
- `scripts/build_subagent_plan.py` creates a plan-only dispatch queue from a simulated run. It must not be treated as proof that local subagents executed.
- `scripts/build_subagent_prompt_bundle.py` creates the concrete derived prompt bundle for one subagent from the static role prompt, runtime context packet, secondary prompt injection, allowed user facts, source policy, and output contract.
- `scripts/build_public_source_plan.py` creates a policy-bound public-source research task list for official pages, public JDs, verified HR posts, candidate experience, and weak social signals without browsing or logging in.
- `scripts/discover_public_sources.py` converts search-adapter results into `evidence/allowed_public_sources.generated.json`, rejecting login/private/backend sources and preserving weak-source limits so users do not need to name recruitment websites.
- `scripts/search_public_sources.py` runs a public-source search adapter. The built-in `seed` provider is deterministic and local: it turns query plans into source-candidate URLs from repository collection targets, not live web search. The `external-json` provider accepts browser/search/API results from outside the script and marks them as real-time URL candidates, still requiring discovery, fetch, and backfill checks before evidence use.
- `scripts/fetch_public_sources.py` fetches allowed public `http(s)` or user-provided `file://` sources into evidence packets. It refuses forbidden/login-only source types and does not bypass platform access controls.
- `scripts/backfill_public_evidence.py` validates and writes externally collected public evidence packets into the run after checking source policy constraints.
- `scripts/build_subagent_work_orders.py` exports adapter-ready work orders from a plan with prompt bundle refs and backfill contracts. This is a handoff contract, not proof that subagents ran.
- `scripts/run_subagent_adapter.py` is the adapter runner entrypoint. `--mock-blocked` writes schema-valid blocked role outputs and always sets `real_subagent_execution = false`; `--adapter-command` runs an external command adapter per work order and sets `real_subagent_execution = true` only when every role output validates and finishes as `done` or `done_with_warnings`.
- `scripts/finalize_runtime_run.py` assembles `final/decision_package.json` only after required role outputs are present, non-blocked, validated, and produced by a real adapter.
- `scripts/execute_subagent_plan.py` inspects a plan-only queue, enforces human/source-policy gates before real execution, writes redacted execution events, and can backfill externally produced role outputs after schema checks.
- `scripts/continue_runtime_run.py` updates the same run with one compact batch of user-owned facts, refreshes the runtime context packet, and returns the run to `injection_ready`.

These scripts are a local deterministic execution shell. The `seed` source adapter is not live web search, and `--mock-blocked` is not real subagent execution. Read `references/runtime-network-and-adapter-setup.md` before enabling real network fetches or real subagent execution.

## Built-In Databases

Use repository-relative paths:

- `data/discipline_taxonomy/` for discipline-domain routing across engineering, science, humanities, social science, business, arts/design, medicine/health, agriculture, law/public affairs, and interdisciplinary backgrounds.
- `data/major_taxonomy/` for the currently implemented engineering major taxonomy, employment clusters, cross-tags, and major lookup.
- `data/runtime_parameters/` for deciding which parameters are user-owned, optional, researched by local subagents, or weighted at runtime.
- `data/school_signals/` for source policy and schema for school-company cooperation, campus recruiting, internship, and full-time opportunity signals.
- `data/company_signals/` for company-level hiring signals, source evidence, and company x major-cluster priors.
- `data/resume_formats/` for reusable resume section logic, format variants, and format accept/reject rules.

Never paste an entire database into the prompt. Load the smallest file and subset needed for the active role.

## Pipeline

Default full route:

```text
InputNormalizer
  -> Career Orchestrator
  -> MajorClusterClassifier
  -> ProfileExtractor
  -> JDAnalyzer
  -> JobScout
  -> CompanyIntelligenceAnalyst
  -> MarketSentimentAnalyzer
  -> MatchStrategist
  -> LearningPathStrategist
  -> PersonalBrandingStrategist
  -> HRSupervisor
  -> ResumeFormatGate
  -> ResumeArchitect
  -> FactualReviewer
  -> HRSupervisor
```

Short routes:

- Major positioning: `InputNormalizer -> MajorClusterClassifier`.
- Resume review: `InputNormalizer -> ProfileExtractor -> ResumeFormatGate -> ResumeArchitect -> FactualReviewer -> HRSupervisor`.
- Job analysis: `InputNormalizer -> JDAnalyzer -> CompanyIntelligenceAnalyst -> MarketSentimentAnalyzer`.
- Job search: `InputNormalizer -> MajorClusterClassifier -> ProfileExtractor -> JobScout -> JDAnalyzer -> MatchStrategist -> LearningPathStrategist`.
- Target job fit: `InputNormalizer -> MajorClusterClassifier -> ProfileExtractor -> JDAnalyzer -> CompanyIntelligenceAnalyst -> JobScout -> MatchStrategist -> LearningPathStrategist -> HRSupervisor -> FactualReviewer`.

## Operating Rules

- Prefer user-provided materials and official/public sources over memory.
- Treat every `.codex/agents/*.toml` file as a role framework for runtime local subagents, not as a frozen decision engine.
- Normalize vague chats, Markdown, resumes, websites, links, and mixed materials through `InputNormalizer` before specialist agents.
- Convert the user's first-round self-described profile, status, experience, goals, and materials into a `runtime_context_packet`, then have `CareerOrchestrator` create role-specific `secondary_prompt_injections` before any user-side specialist subagent runs.
- Convert each `secondary_prompt_injection` into a traceable `subagent_invocation`; record `execution_manifest`, `artifact_refs`, `execution_log_refs`, `role_output_packet`, and `error_recovery_state` for runtime work.
- Track user-side execution with `run_state`; do not skip normalization, context packet creation, secondary injection creation, merge, debate, HR review, factual review, or user-confirmation gates when they are required.
- Do not silently merge blocked, failed, malformed, or partially recovered outputs into the final package. Merge safe partial fields only when the error recovery protocol allows it and the limitation is visible in `blocked_outputs`, `degraded_outputs`, or `runtime_research_tasks`.
- Ask the user for missing user-owned facts once in a compact batch. Do not ask the user for data that local subagents can research from allowed public sources.
- Automatically inject the default public recruitment source matrix into recruitment-information roles (`JobScout`, `JDAnalyzer`, `CompanyIntelligenceAnalyst`, `MarketSentimentAnalyzer`, and `HRSupervisor`). These roles should know which official pages, recruitment platforms, HR public posts, candidate-experience sources, social media weak signals, and public reports to search without asking the user to name websites.
- Do not expose `source_policy_ack` as a separate end-user question; the runtime controller records it internally only after the auto-generated public source plan passes policy checks.
- Treat concrete skill weights and external-display asset weights as runtime decisions. The repository provides schemas and examples, not universal requirements that every discipline must follow.
- Require hard-data provenance for all weights, scores, priorities, rankings, thresholds, and confidence adjustments. Local subagents must verify them through public/official network sources or user-provided materials; if evidence is missing, return `not_available`, `needs_more_sources`, and runtime research tasks instead of guessing.
- For non-graduating candidates, split current internship analysis from future full-time preparation.
- School-company cooperation and school-specific hiring advantages require official or primary runtime evidence; never infer them from school name alone.
- Treat company-signal data as priors, not current role-specific requirements.
- For a concrete job, require fresh JD text or current public JD retrieval before final resume tailoring.
- When the user gives a concrete job or internship, separate immediate fit from growth path: judge current suitability only with user evidence plus current JD/public evidence, and route learnable gaps to `LearningPathStrategist` for specific skills, projects, proof artifacts, and resume-conversion conditions before application.
- Use candidate/social media information only as auxiliary preparation or risk signals unless it is verified by official sources.
- If runtime evidence is missing, return research tasks, evidence requirements, blocked outputs, conditional options, and handoff targets instead of a final judgment.
- Do not store or expose private resumes, private chats, IDs, addresses, or non-public HR/candidate information. Intermediate reports and logs should redact phone numbers and personal emails by default; final resume drafts may include user-authorized contact fields when the user explicitly provides them for the resume.
- Resume writing may improve structure, evidence, and wording, but must not create false experience, fake metrics, fake ownership, fake education, or fake awards.
- Complete resume drafts must pass `ResumeFormatGate` before drafting and `FactualReviewer` before being presented as final.
- If the user refuses to provide missing information, generate an incomplete resume draft only after explicit consent and after `ResumeFormatGate` marks the incomplete-draft exception. Omit missing sections, block application direction recommendations, and warn that targeted advice requires detailed information.
- The whole pipeline should remain under `HRSupervisor` review: personal branding, resume strategy, and final packages must be quickly understandable to HR and show credible competitive signals.
- Agents should debate conflicts through structured fields. If claims conflict, preserve the disagreement, request evidence, or hand back to the relevant agent instead of silently merging incompatible conclusions.

## Role Prompt Files

Role prompt frameworks live in `.codex/agents/*.toml`.

Each file contains:

- role identity and scope.
- database dependencies.
- professional prompt instructions.
- expected output contract.
- hard prohibitions.

When a role needs static data, read the dependency paths listed in its TOML first.
