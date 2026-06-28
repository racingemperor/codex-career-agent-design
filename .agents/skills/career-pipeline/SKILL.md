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
- `references/codex-desktop-subagent-adapter.md` before using Codex Desktop current-session subagent tools for real role execution.
- `references/runtime-subagent-injection-protocol.md` before creating user-side subagent prompts.
- `references/subagent-invocation-contract.md` before converting a secondary prompt injection into a concrete local subagent invocation.
- `references/runtime-orchestration-protocol.md` before running or simulating the user-side pipeline state machine.
- `references/runtime-artifact-schema.md` before writing, reading, merging, or exposing runtime artifacts, logs, evidence packets, resume drafts, or final packages.
- `references/error-recovery-protocol.md` before retrying, degrading, blocking, or partially merging a failed run.
- `references/user-interaction-flow.md` before asking the user for missing facts or handling incomplete information.
- `references/runtime-weight-engine.md` before proposing, checking, or merging any runtime weight, score, priority, ranking, threshold, or confidence adjustment.
- `references/role-output-contracts.md` before merging subagent outputs.
- `references/application-url-output-policy.md` before returning recommended jobs, internships, application targets, or target-job fit outputs.
- `references/real-user-deployment-and-use-flow.md` before explaining how a real user installs, invokes, and runs the pipeline end to end.
- `references/manual-controller-runtime-flow.md` before using the main Codex conversation as a manual controller for Codex-side source search, secondary prompt injection, and non-API subagent execution.

## Local Contract Scripts

Use these scripts only for local contract validation and simulation. They do not call real subagents, browse recruitment sites, or make career judgments.

Run the scripts from this skill directory, not from the repository root:

```bash
cd .agents/skills/career-pipeline
python scripts/run_product_flow.py --task-type job_search --route job_search --input-text "computer science junior, Python, looking for internship but unsure which role" --run-root ../../../.career-pipeline-runs
python scripts/career_pipeline_run.py --task-type target_job_fit --route target_job_fit --input-text "computer science senior, assess fit for Tencent backend role. JD: Java and MySQL" --run-root ../../../.career-pipeline-runs --source-adapter seed --subagent-adapter mock-blocked
python scripts/simulate_runtime_run.py --task-type job_search --route job_search --input-text "computer science sophomore, Python, looking for AI internship" --run-root ../../../.career-pipeline-runs
python scripts/build_subagent_plan.py --run-dir ../../../.career-pipeline-runs/<run_id> --build-prompt-bundles
python scripts/build_public_source_plan.py --run-dir ../../../.career-pipeline-runs/<run_id>
python scripts/discover_public_sources.py --run-dir ../../../.career-pipeline-runs/<run_id> --generate-query-plan-only
python scripts/collect_public_source_results.py --run-dir ../../../.career-pipeline-runs/<run_id> --notes-md <public_source_notes.md>
python scripts/search_public_sources.py --run-dir ../../../.career-pipeline-runs/<run_id> --provider seed
python scripts/search_public_sources.py --run-dir ../../../.career-pipeline-runs/<run_id> --provider external-json --search-results-json <search_results.json>
python scripts/discover_public_sources.py --run-dir ../../../.career-pipeline-runs/<run_id> --search-results-json <search_results.json>
python scripts/fetch_public_sources.py --run-dir ../../../.career-pipeline-runs/<run_id> --sources-json ../../../.career-pipeline-runs/<run_id>/evidence/allowed_public_sources.generated.json
python scripts/backfill_public_evidence.py --run-dir ../../../.career-pipeline-runs/<run_id> --evidence-json ../../../.career-pipeline-runs/<run_id>/evidence/fetched_public_evidence.json
python scripts/discover_project_candidates.py --candidates-json <project_candidates.json> --target-role "backend internship" --jd-text "<JD summary>" --mode mixed --out-dir ../../../.career-pipeline-runs/<run_id>/projects
python scripts/audit_project_repository.py --repo <local_project_repo> --name <project-name> --out-dir ../../../.career-pipeline-runs/<run_id>/projects/<project-name>/audit
python scripts/build_project_interview_pack.py --audit-json ../../../.career-pipeline-runs/<run_id>/projects/<project-name>/audit/project_repo_audit.json --recommendation-json <project_recommendation.json> --out-dir ../../../.career-pipeline-runs/<run_id>/projects/<project-name>/pack
python scripts/build_subagent_work_orders.py --run-dir ../../../.career-pipeline-runs/<run_id>
python scripts/build_incomplete_user_manual_outputs.py --run-dir ../../../.career-pipeline-runs/<run_id> --out-dir ../../../.career-pipeline-runs/<run_id>/manual-controller-outputs
python scripts/run_subagent_adapter.py --run-dir ../../../.career-pipeline-runs/<run_id> --mock-blocked
python scripts/run_subagent_adapter.py --run-dir ../../../.career-pipeline-runs/<run_id> --adapter-command <adapter-executable> --adapter-arg <adapter-script-or-config>
python scripts/finalize_runtime_run.py --run-dir ../../../.career-pipeline-runs/<run_id> --real-subagent-execution
python scripts/finalize_runtime_run.py --run-dir ../../../.career-pipeline-runs/<run_id> --real-subagent-execution --execution-mode manual-controller
python scripts/render_resume_artifacts.py --decision-package ../../../.career-pipeline-runs/<run_id>/final/decision_package.json --out-dir ../../../.career-pipeline-runs/<run_id>/final/resume_artifacts --basename general_resume
python scripts/render_resume_artifacts.py --decision-package ../../../.career-pipeline-runs/<run_id>/final/decision_package.json --out-dir ../../../.career-pipeline-runs/<run_id>/final/resume_artifacts --basename general_resume --all-resume-versions
python scripts/render_resume_artifacts.py --draft-md ../../../.career-pipeline-runs/<run_id>/final/resume_draft.md --out-dir ../../../.career-pipeline-runs/<run_id>/final/resume_artifacts --basename general_resume
python scripts/apply_resume_polish.py --plan-json <authorized_resume_polish_operation.json>
python scripts/apply_portfolio_asset_changes.py --plan-json <authorized_portfolio_asset_operation.json>
python scripts/execute_subagent_plan.py --run-dir ../../../.career-pipeline-runs/<run_id> --dry-run
```

Do not run these commands from the repository root as `scripts/*.py`; the `scripts/` path is relative to `.agents/skills/career-pipeline/`. If already at the repository root, use `.agents/skills/career-pipeline/scripts/<script>.py`.

- `scripts/validate_runtime_contracts.py` validates repository role prompts, secondary prompt injections, canonical subagent invocation packets, execution manifests, and blocked/final gate consistency.
- `scripts/run_product_flow.py` is the product-style entrypoint for ordinary chat intake. It introduces the skill, normalizes the first user profile, builds prompt bundles, public-source query plans, and work orders, and writes a concise user-facing status package without exposing adapter/source internals. It does not claim final career judgment until real public sources and real role outputs are supplied.
- `scripts/career_pipeline_run.py` is the one-command deterministic user-side runner. With `--source-adapter seed --subagent-adapter mock-blocked`, it creates a complete blocked run with source-discovery artifacts and subagent work orders, but does not claim real subagent execution. With explicit `external-json`, `external-command`, and `--finalize`, it can produce a final package only after role outputs validate.
- `scripts/simulate_runtime_run.py` creates a private ignored `.career-pipeline-runs/<run_id>/` artifact tree for a no-network blocked run, useful for checking runtime packet shape before building a real runner.
- `scripts/build_subagent_plan.py` creates a plan-only dispatch queue from a simulated run with `dispatch_strategy = "batched_artifact_handoff"`, `dispatch_batches`, `max_parallel_subagents`, `artifact_handoff_required`, and `close_completed_subagents`. It must not be treated as proof that local subagents executed.
- `scripts/build_subagent_prompt_bundle.py` creates the concrete derived prompt bundle for one subagent from the static role prompt, runtime context packet, secondary prompt injection, allowed user facts, source policy, and output contract.
- `scripts/build_public_source_plan.py` creates a policy-bound public-source research task list for official pages, public JDs, verified HR posts, candidate experience, and weak social signals without browsing or logging in.
- `scripts/discover_public_sources.py` converts search-adapter results into `evidence/allowed_public_sources.generated.json`, rejecting login/private/backend sources and preserving weak-source limits so users do not need to name recruitment websites.
- `scripts/collect_public_source_results.py` converts controller/browser-collected public URLs or Markdown notes into `search_results` shape so the main Codex controller can pass public evidence forward without asking users to hand-write shell JSON.
- `scripts/search_public_sources.py` runs a public-source search adapter. The built-in `seed` provider is deterministic and local: it turns query plans into source-candidate URLs from repository collection targets, not live web search. The `external-json` provider accepts browser/search/API results from outside the script and marks them as real-time URL candidates, still requiring discovery, fetch, and backfill checks before evidence use.
- `scripts/fetch_public_sources.py` fetches allowed public `http(s)` or user-provided `file://` sources into evidence packets. It detects common Chinese charsets, refuses forbidden/login-only source types, and does not bypass platform access controls. For dynamic public pages that static fetch sees only as a JavaScript shell, pass a local browser-rendered text snapshot as `rendered_text_ref` while keeping the public URL in `source_ref`.
- `scripts/backfill_public_evidence.py` validates and writes externally collected public evidence packets into the run after checking source policy constraints.
- `scripts/discover_project_candidates.py` scores public project candidates from a user-side search adapter or JSON candidate pool, caps star-count influence, and filters shallow wrappers, templates, browser extensions, SDK/framework-only projects, and missing public repo URLs before project recommendation.
- `scripts/audit_project_repository.py` audits a locally cloned project repository for README, dependencies, Docker/deploy files, tests, API/backend, database/state, async jobs, AI/agent, and source evidence points. Resume project claims should not be treated as source-verified until this audit or an equivalent local-source audit exists.
- `scripts/build_project_interview_pack.py` turns a project audit plus recommendation JSON into a Markdown project interview pack with project positioning, existing capability, suggested modifications, resume-ready claims, STAR bullets, interviewer follow-ups, core-code explanation paths, and proof artifacts.
- `scripts/build_subagent_work_orders.py` exports adapter-ready work orders from a plan with prompt bundle refs, batch ids, dependency artifact refs, close-after-output instructions, and backfill contracts. This is a handoff contract, not proof that subagents ran.
- `scripts/build_incomplete_user_manual_outputs.py` builds conservative Manual Controller role-output fixtures for validating the incomplete-user general-resume delivery path. It is not a live subagent adapter and must not be used as proof of real role judgment beyond this bounded validation scenario.
- `scripts/run_subagent_adapter.py` is the adapter runner entrypoint. `--mock-blocked` writes schema-valid blocked role outputs and always sets `real_subagent_execution = false`; `--adapter-command` runs an external command adapter per work order and sets `real_subagent_execution = true` only when every role output validates and finishes as `done` or `done_with_warnings`.
- `scripts/finalize_runtime_run.py` assembles `final/decision_package.json` only after required role outputs are present, non-blocked, validated, and produced by a real adapter or an explicitly marked Manual Controller MVP run.
- `scripts/render_resume_artifacts.py` exports a validated resume Markdown draft or `final/decision_package.json` resume draft into Word DOCX, PDF, and first-page PNG artifacts. It also writes `final/resume_artifacts/resume_draft.md` when rendering from a decision package so users do not need to hand-edit JSON. With `--all-resume-versions`, it also exports `growth_resume_preview.md` plus DOCX/PDF/PNG when the final package includes a conditional after-learning/project resume preview.
- `scripts/apply_resume_polish.py` applies a ResumePolisher operation packet only after secondary prompt injection supplies explicit user authorization, allowed input refs, and allowed output refs.
- `scripts/apply_portfolio_asset_changes.py` applies PortfolioAssetBuilder file changes only after secondary prompt injection supplies explicit user authorization, an allowed root, and allowed actions; it refuses path traversal outside the authorized root.
- `scripts/execute_subagent_plan.py` inspects a plan-only queue, enforces human/source-policy gates before real execution, writes redacted execution events, and can backfill externally produced role outputs after schema checks. Use `--manual-controller-execution` only when the main Codex controller actually dispatched separated role subagents or separated role passes; it stamps backfilled outputs with manual-controller real-execution metadata for finalizer review.
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
  -> ResumePolisher
  -> PortfolioAssetBuilder
  -> HRSupervisor
  -> ResumeFormatGate
  -> ResumeArchitect
  -> FactualReviewer
  -> HRSupervisor
```

Short routes:

- Major positioning: `InputNormalizer -> MajorClusterClassifier`.
- Resume review: `InputNormalizer -> ProfileExtractor -> ResumeFormatGate -> ResumePolisher -> ResumeArchitect -> FactualReviewer -> HRSupervisor`.
- Job analysis: `InputNormalizer -> JDAnalyzer -> CompanyIntelligenceAnalyst -> MarketSentimentAnalyzer`.
- Job search: `InputNormalizer -> MajorClusterClassifier -> ProfileExtractor -> JobScout -> JDAnalyzer -> MatchStrategist -> LearningPathStrategist`.
- Target job fit: `InputNormalizer -> MajorClusterClassifier -> ProfileExtractor -> JDAnalyzer -> CompanyIntelligenceAnalyst -> JobScout -> MatchStrategist -> LearningPathStrategist -> HRSupervisor -> FactualReviewer`.
- Existing resume polish: `InputNormalizer -> ProfileExtractor -> ResumeFormatGate -> ResumePolisher -> ResumeArchitect -> FactualReviewer -> HRSupervisor`.
- Authorized portfolio asset improvement: `InputNormalizer -> ProfileExtractor -> PersonalBrandingStrategist -> PortfolioAssetBuilder -> FactualReviewer -> HRSupervisor`.

## Operating Rules

- Prefer user-provided materials and official/public sources over memory.
- Treat every `.codex/agents/*.toml` file as a role framework for runtime local subagents, not as a frozen decision engine.
- Normalize vague chats, Markdown, resumes, websites, links, and mixed materials through `InputNormalizer` before specialist agents.
- Convert the user's first-round self-described profile, status, experience, goals, and materials into a `runtime_context_packet`, then have `CareerOrchestrator` create role-specific `secondary_prompt_injections` before any user-side specialist subagent runs.
- `universal_runtime_guardrails` is automatically injected into every role's secondary prompt injection. This is an internal stability layer and does not add a user-facing step. It requires `no_file_write_by_default`, `tool_use_requires_explicit_permission`, `blocked_outputs_must_remain_blocked`, `handoff_instead_of_overreach`, `must_return_structured_json`, no fabrication, and source-backed weights/scores/rankings.
- Convert each `secondary_prompt_injection` into a traceable `subagent_invocation`; record `execution_manifest`, `artifact_refs`, `execution_log_refs`, `role_output_packet`, and `error_recovery_state` for runtime work.
- Track user-side execution with `run_state`; do not skip normalization, context packet creation, secondary injection creation, merge, debate, HR review, factual review, or user-confirmation gates when they are required.
- Do not silently merge blocked, failed, malformed, or partially recovered outputs into the final package. Merge safe partial fields only when the error recovery protocol allows it and the limitation is visible in `blocked_outputs`, `degraded_outputs`, or `runtime_research_tasks`.
- At the start of a real user-side run, introduce Career Pipeline in one simple professional paragraph before asking for information: explain that it analyzes the user's background, target roles, public job evidence, learning gaps, personal branding, and role-specific resume design. Then ask one compact batch of user-owned facts. Use `references/user-interaction-flow.md` for the default opening wording.
- Ask the user for missing user-owned facts once in a compact batch. Do not ask the user for data that local subagents can research from allowed public sources.
- Automatically inject the default public recruitment source matrix into recruitment-information roles (`JobScout`, `JDAnalyzer`, `CompanyIntelligenceAnalyst`, `MarketSentimentAnalyzer`, and `HRSupervisor`). These roles should know which official pages, recruitment platforms, HR public posts, candidate-experience sources, social media weak signals, public reports, small/mid-size company sources, local employer sources, school career notices, industrial-park notices, and local internship channels to search without asking the user to name websites.
- When a recruitment source hits a login wall, CAPTCHA, app-only page, access-denied page, private/backend page, or JavaScript shell without public rendered text, the controller must not ask the user to log in or provide private screenshots. Record a `source_attempt_log`, run automatic source substitution, and use only source-policy-valid public replacements. If no replacement exists, block the affected concrete claim or target instead of guessing.
- Require `source_accuracy_tier` on source-backed job, company, HR, candidate, school, weight, score, priority, and resume-tailoring claims. Tier A/B sources may support strong claims when current and relevant; weak sources may support preparation or risk notes only; login-only/private/dynamic-shell sources must not support final recommendations.
- Do not expose `source_policy_ack` as a separate end-user question; the runtime controller records it internally only after the auto-generated public source plan passes policy checks.
- A manual controller run may use the main Codex conversation to perform Codex-side source search and dispatch separated role prompts. API execution is not required for this MVP path, but role outputs must still use the same strict JSON contracts, public URL requirements, HR review, factual review, and blocked-output gates.
- When current-session `multi_agent_v1.spawn_agent` is available, prefer the Codex Desktop built-in subagent adapter for real role execution. The main Codex controller reads `subagent_work_orders.json`, spawns role agents by `dispatch_batches`, waits for strict JSON role outputs, persists each `output_artifact_target`, closes completed agents, and backfills with manual-controller execution metadata. Python scripts cannot directly call these current-session tools.
- Dispatch local role subagents by `dispatch_batches`, not all at once. Each batch should stay within `max_parallel_subagents`; after every role output is persisted to its `output_artifact_target`, close completed subagents and pass only artifact refs to the next batch.
- Treat concrete skill weights and external-display asset weights as runtime decisions. The repository provides schemas and examples, not universal requirements that every discipline must follow.
- Require hard-data provenance for all weights, scores, priorities, rankings, thresholds, and confidence adjustments. Local subagents must verify them through public/official network sources or user-provided materials; if evidence is missing, return `not_available`, `needs_more_sources`, and runtime research tasks instead of guessing.
- For non-graduating candidates, split current internship analysis from future full-time preparation.
- School-company cooperation and school-specific hiring advantages require official or primary runtime evidence; never infer them from school name alone.
- Treat company-signal data as priors, not current role-specific requirements.
- For a concrete job, require JD text or public JD/application URL evidence before final resume tailoring, exact fit scores, or company-specific skill-weight ranking.
- recommended jobs, internships, or application targets must include source-policy-valid public URL candidates so the user can inspect them. If no public URL exists, block the concrete recommendation and return `blocked_application_targets_without_public_url` plus runtime research tasks.
- When the user gives a concrete job or internship, separate immediate fit from growth path: judge suitability from user evidence plus available JD/public evidence, mark unsupported exact scores or tailored claims as unavailable, and route learnable gaps to `LearningPathStrategist` for specific skills, projects, proof artifacts, and resume-conversion conditions before application.
- When the user lacks project evidence or the target role expects stronger hands-on proof, require `LearningPathStrategist` to produce concrete project recommendations: role-fit rationale, easiest credible completion path, implementation steps, proof artifacts, resume-conversion conditions, and interview-defensibility questions. Planned project work must not be written as completed resume claims.
- For project-backed resume or interview claims, prefer the local project toolchain: discover public candidates, audit a locally cloned repository, then build a project interview pack. Without local source audit evidence, project recommendations remain preparation guidance and cannot become resume-ready project claims.
- When the user provides an existing resume, route through `ResumePolisher` before final resume drafting. Preserve the user's original resume format by default. Use repository resume templates only to strengthen missing section logic or evidence placement; if the template is more specific and persuasive, add supported content into the original resume instead of replacing the user's format.
- When the user wants help with a personal website, GitHub/Gitee account, project README, demo, portfolio, blog, paper page, or other public proof link, route through `PersonalBrandingStrategist` and `PortfolioAssetBuilder`. Planning is allowed without write access, but generating, editing, publishing, pushing, or modifying user-owned assets requires explicit user authorization and a bounded path or asset scope.
- When the output includes HR questions or HR screening wording, require `HRSupervisor` to bind each item to the target company or recommended company and a public source URL from official recruiting pages, enterprise-certified recruiting accounts, verified HR public posts, or public recruitment-platform process notes. Do not generate HR wording yourself; if company-bound public HR wording is unavailable, return a limitation and runtime research tasks. Candidate experience and social media weak signals are preparation only.
- If a public JD or application URL does not state opening status, freshness, city, work location, onsite days, arrival time, deadline, headcount, or internship duration, do not ask the user to fill those details and do not block the recommendation only for that reason. Add them to `ask_hr_about` and tell the user to confirm with HR or the recruiter.
- Use candidate/social media information only as auxiliary preparation or risk signals unless it is verified by official sources.
- If runtime evidence is missing, return research tasks, evidence requirements, blocked outputs, conditional options, and handoff targets instead of a final judgment.
- Do not store or expose private resumes, private chats, IDs, addresses, or non-public HR/candidate information. Intermediate reports and logs should redact phone numbers and personal emails by default; final resume drafts may include user-authorized contact fields when the user explicitly provides them for the resume.
- Resume writing may improve structure, evidence, and wording, but must not create false experience, fake metrics, fake ownership, fake education, or fake awards.
- Complete resume drafts must pass `ResumeFormatGate` before drafting and `FactualReviewer` before being presented as final.
- If the output includes `growth_resume_preview`, present it only as a conditional after-learning/project preview. Recommended skills or projects in that preview must not be used as completed current resume facts until proof artifacts exist and FactualReviewer can verify them.
- If the user refuses to provide missing information, generate an incomplete resume draft only after explicit consent and after `ResumeFormatGate` marks the incomplete-draft exception. Omit missing sections, block application direction recommendations, and warn that targeted advice requires detailed information.
- The whole pipeline should remain under `HRSupervisor` review: personal branding, resume strategy, and final packages must be quickly understandable to HR and show credible competitive signals.
- User-facing final packages should be professional, concise, and resume-like: conclusion first, evidence bullets, recommended public URLs, gaps to fix, HR confirmation items, and next 3 actions. Do not expose raw runtime fields unless the user is debugging the pipeline.
- Agents should debate conflicts through structured fields. If claims conflict, preserve the disagreement, request evidence, or hand back to the relevant agent instead of silently merging incompatible conclusions.

## Role Prompt Files

Role prompt frameworks live in `.codex/agents/*.toml`.

Current role prompt files include `resume-polisher` for existing-resume polishing and `portfolio-asset-builder` for authorized personal website, GitHub/Gitee, README, demo, and portfolio asset improvement.

Each file contains:

- role identity and scope.
- database dependencies.
- professional prompt instructions.
- expected output contract.
- hard prohibitions.

When a role needs static data, read the dependency paths listed in its TOML first.
