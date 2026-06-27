# Manual Controller Runtime Flow

Use this reference when the user wants a complete user-side run without building a Codex plugin, Codex CLI adapter, or API/Agents SDK adapter yet.

## Core Position

API is not required for the first complete user-side workflow.

The main conversation controller can run the pipeline by reading the repository skill, creating secondary prompt injections, asking Codex-side role subagents or role-separated passes to work from prompt bundles, searching public sources, and merging strict JSON outputs.

This is a Manual Controller MVP. It is less automated than a CLI or API adapter, but it is enough to validate the real workflow with user-side Codex before productizing.

## What This Solves

This mode addresses three current gaps:

- real public-source collection: Codex-side source search gathers public URLs from official and recruitment sources.
- real role execution: the main conversation controller dispatches role-specific prompt bundles instead of using `mock-blocked`.
- end-to-end orchestration: the main conversation controller follows the same run stages, gates, debate rules, HR review, factual review, and final package rules as the scripted runtime.

It does not require a plugin package. It does not require API calls. It does not bypass any source, login, privacy, or platform restrictions.

## Main Conversation Controller Duties

The main conversation controller is the coordinator, not another career-judgment role.

It must:

- load `career-pipeline/SKILL.md` and required references.
- create or use a run directory under `.career-pipeline-runs/<run_id>/`.
- normalize user input into `first_round_user_profile` and `runtime_context_packet`.
- create `secondary_prompt_injections`.
- create or read `subagent_work_orders.json`.
- perform Codex-side source search for source-plan tasks.
- write or request `search_results.json`.
- run source filtering/fetch/backfill scripts when available.
- dispatch each role as a separate subagent, new conversation, or strictly separated role pass according to `dispatch_batches`.
- require strict role output JSON with `role_output_packet` and `error_recovery_state`.
- persist every role output artifact before closing a subagent, then close completed subagents before opening the next batch.
- merge only safe fields.
- run debate, HR review, and factual review before final output.
- block only the final fields that truly require missing evidence, URLs, user facts, or role outputs. Keep safe direction, preparation, public URL targets, and HR confirmation notes visible.

It must not:

- let a role use all private user data when only a subset is needed.
- treat static company priors as current JD evidence.
- treat official entrypoints as concrete open jobs.
- show recommended application targets without a public URL.
- treat missing opening status, city, onsite days, arrival time, deadline, headcount, or internship duration as user-owned facts; these are HR confirmation items when the public page is silent.
- turn planned learning into completed resume evidence.
- mark `real_subagent_execution = true` unless actual role outputs were produced by separated role execution.

## Codex-Side Source Search

Codex-side source search means the user-side Codex instance searches public web sources on behalf of `JobScout`, `JDAnalyzer`, `CompanyIntelligenceAnalyst`, `MarketSentimentAnalyzer`, and `HRSupervisor`.

The user does not need to name websites. The controller should use:

- `data/company_signals/default_recruitment_source_matrix.zh-CN.json`
- `data/company_signals/source_collection_targets.zh-CN.json`
- `data/company_signals/official_application_entrypoints.zh-CN.json`
- the generated `evidence/public_source_research_plan.json`
- `references/source-policy.md`
- `references/application-url-output-policy.md`

Search priority:

1. company official career page, campus page, job detail page, or official job-search page.
2. official school career center, department notice, or school-company channel.
3. public recruitment-platform JD that does not require login.
4. verified HR public recruiting post.
5. public reports and mainstream media.
6. candidate experience and social media only as weak auxiliary preparation signals.

Every collected item must include a public URL:

```json
{
  "task_id": "",
  "url": "",
  "title": "",
  "snippet": "",
  "source_type_hint": "",
  "retrieved_or_verified_at": "",
  "notes": ""
}
```

The controller should collect these into `search_results.json`:

```json
{
  "search_results": [
    {
      "task_id": "target-current-jd-verification",
      "url": "https://careers.example.com/jobs/123",
      "title": "Backend Engineer Intern",
      "snippet": "Java, MySQL, Redis, distributed systems"
    }
  ]
}
```

Then run:

```bash
python scripts/search_public_sources.py --run-dir ../../../.career-pipeline-runs/<run_id> --provider external-json --search-results-json <search_results.json>
python scripts/discover_public_sources.py --run-dir ../../../.career-pipeline-runs/<run_id> --search-results-json <search_results.json>
python scripts/fetch_public_sources.py --run-dir ../../../.career-pipeline-runs/<run_id> --sources-json ../../../.career-pipeline-runs/<run_id>/evidence/allowed_public_sources.generated.json
python scripts/backfill_public_evidence.py --run-dir ../../../.career-pipeline-runs/<run_id> --evidence-json ../../../.career-pipeline-runs/<run_id>/evidence/fetched_public_evidence.json
```

If these scripts cannot fetch a source, the controller may still pass source metadata and short public excerpts as role evidence, but it must mark the output as degraded and keep unsupported final claims blocked.

For dynamic public pages where static fetch returns only a JavaScript shell, the controller may capture a browser-rendered public text snapshot with Codex Browser or Playwright and include it as `rendered_text_ref` in the source item. Keep the inspectable public URL in `source_ref`; `rendered_text_ref` must be a local text file or `file://` URI containing only public rendered text. `fetch_public_sources.py` records `extraction_method = "browser_rendered_text"` and still applies the same source policy.

`source_policy_ack` is recorded internally after the source plan passes policy checks. It is not an extra user question.

## Manual Subagent Execution

The main conversation controller may execute subagents in any of these ways:

- true Codex subagent, if the surface supports it.
- separate Codex conversation per role.
- strictly separated role pass inside the main conversation, only for early manual testing.

API is not required. The important requirement is not the transport. The important requirement is that each role receives a bounded prompt bundle and returns a strict role output.

For every role:

1. Read the relevant `prompts/<agent>.prompt_bundle.json` or build the prompt bundle from the static TOML plus secondary injection.
2. Provide only role-relevant user facts and source refs.
3. Require JSON output matching the role prompt.
4. Save or paste back the role output.
5. Validate that it includes:
   - `invocation_ref`
   - `role_output_packet`
   - `error_recovery_state`
   - `evidence_basis`
   - `runtime_research_tasks`
   - `blocked_outputs`
   - `confidence`

If a role fails, returns malformed JSON, or makes unsupported final claims, the controller should ask for a corrected role output once. If it still fails, merge only safe fields and block dependent final outputs.

After separated role outputs are produced as JSON files, backfill them with:

```bash
python scripts/execute_subagent_plan.py \
  --run-dir ../../../.career-pipeline-runs/<run_id> \
  --manual-controller-execution \
  --backfill-output job-scout=C:/path/to/job-scout.output.json \
  --backfill-output hr-supervisor=C:/path/to/hr-supervisor.output.json
```

Then finalize only if all required role outputs, source gates, HR review, and factual review pass:

```bash
python scripts/finalize_runtime_run.py \
  --run-dir ../../../.career-pipeline-runs/<run_id> \
  --real-subagent-execution \
  --execution-mode manual-controller
```

## Suggested Manual Dispatch Order

Use the route selected by `CareerOrchestrator`. For the full engineering pipeline:

```text
InputNormalizer
  -> CareerOrchestrator
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

Use batched dispatch after the context packet, secondary prompt injections, prompt bundles, and work orders exist. `build_subagent_plan.py` writes `dispatch_strategy = "batched_artifact_handoff"`, `dispatch_batches`, `max_parallel_subagents`, `artifact_handoff_required`, and `close_completed_subagents`.

Default batch pattern:

- `profile_and_taxonomy`: `MajorClusterClassifier`, `ProfileExtractor`.
- `public_role_research`: `JDAnalyzer`, `JobScout`, `CompanyIntelligenceAnalyst`, `MarketSentimentAnalyzer` when present.
- `strategy_match`: `MatchStrategist`.
- `strategy_learning`: `LearningPathStrategist`, after `MatchStrategist` output is persisted.
- `branding_and_resume`: `PersonalBrandingStrategist`, `ResumeFormatGate`, `ResumeArchitect` when present.
- `hr_and_factual_gates`: `HRSupervisor`, `FactualReviewer`.

Run only one batch at a time. Within a batch, do not exceed `max_parallel_subagents` from the plan. For every completed role, persist `agents/<role>/output.json`, append the execution event, and close completed subagents before the next batch starts. Later batches must read `depends_on_artifact_refs`; they must not rely on closed subagent chat memory. If a role lists `depends_on_agents`, those agents must be in earlier batches, never merely earlier within the same parallel batch.

## Debate And Merge

The controller must merge through evidence fields, not prose preference.

Use these fields:

- `agent_claims`
- `evidence_challenges`
- `disagreements_with`
- `handoff_questions`
- `runtime_research_tasks`
- `blocked_outputs`
- `application_url_candidates`
- `blocked_application_targets_without_public_url`
- `weight_provenance`

Debate examples:

- `MatchStrategist` recommends apply-now, but `JobScout` has only an official entrypoint, not a current JD URL: downgrade to explore or prepare-first, keep the public URL visible, and put missing operational fields in `ask_hr_about`.
- `PersonalBrandingStrategist` recommends GitHub, but role evidence does not support external asset priority: ask for hard-data provenance or mark external asset weight unavailable.
- `ResumeArchitect` writes a completed skill from a learning plan: `FactualReviewer` blocks the claim.
- `HRSupervisor` says presentation is clear, but `FactualReviewer` rejects a metric: factual review wins.

## Final Output Conditions

The manual controller may present a final package only when:

- user-owned required facts are sufficient or the user has accepted a documented incomplete-output path.
- source policy has been applied.
- each recommended application target has a public URL.
- JD/public evidence is sufficient for the level of claim being made: exact fit score, apply-now, and tailored resume claims need stronger current JD plus user evidence; prepare-first and explore recommendations may use public JD, official entrypoint, or role-family evidence with limitations stated.
- each runtime weight has hard-data provenance or is marked unavailable.
- required role outputs are present and not blocked for final fields.
- HR review and factual review have passed where applicable.

If not, return a blocked or degraded package with:

- what is known.
- what is safe to say now.
- `blocked_application_targets_without_public_url`.
- `runtime_research_tasks`.
- `ask_hr_about` for missing opening status, city, onsite days, arrival time, deadline, headcount, or internship duration.
- one compact user follow-up for user-owned facts only.
- exact next action for the controller.

## Theoretical User-Side Command Shape

For early manual runs:

```text
Use the career-pipeline skill in this repository.
Act as the main conversation controller.
Normalize my first-round profile.
Create secondary prompt injections for the required roles.
Search public sources yourself using the repository source matrix.
Every job/company/HR/source claim must include a public URL.
Dispatch the role prompts as separated subagents or separated role passes.
Merge only strict JSON outputs.
Run HR and factual gates.
Return a final package or a blocked package.
```

This instruction can live in the user-side first message or in a wrapper prompt for the skill.
