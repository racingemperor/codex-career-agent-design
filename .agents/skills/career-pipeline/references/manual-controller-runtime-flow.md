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
- dispatch each role as a separate subagent, new conversation, or strictly separated role pass.
- require strict role output JSON with `role_output_packet` and `error_recovery_state`.
- merge only safe fields.
- run debate, HR review, and factual review before final output.
- block final outputs when required evidence, URLs, user facts, or role outputs are missing.

It must not:

- let a role use all private user data when only a subset is needed.
- treat static company priors as current JD evidence.
- treat official entrypoints as concrete open jobs.
- show recommended application targets without a public URL.
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

Parallel execution is allowed after the context packet and secondary prompt injections exist:

- `MajorClusterClassifier` and `ProfileExtractor` can run in parallel.
- `JDAnalyzer`, `JobScout`, `CompanyIntelligenceAnalyst`, and `MarketSentimentAnalyzer` can run after source tasks are ready.
- `MatchStrategist` waits for profile, JD/job, company, and market signals.
- `LearningPathStrategist` and `PersonalBrandingStrategist` wait for match gaps and evidence needs.
- `ResumeArchitect` waits for `ResumeFormatGate`.
- final `HRSupervisor` waits for `FactualReviewer` when a resume or recommendation claim is produced.

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

- `MatchStrategist` recommends apply-now, but `JobScout` has only an official entrypoint, not a current JD URL: downgrade to explore or prepare-first and request current JD evidence.
- `PersonalBrandingStrategist` recommends GitHub, but role evidence does not support external asset priority: ask for hard-data provenance or mark external asset weight unavailable.
- `ResumeArchitect` writes a completed skill from a learning plan: `FactualReviewer` blocks the claim.
- `HRSupervisor` says presentation is clear, but `FactualReviewer` rejects a metric: factual review wins.

## Final Output Conditions

The manual controller may present a final package only when:

- user-owned required facts are sufficient or the user has accepted a documented incomplete-output path.
- source policy has been applied.
- each recommended application target has a public URL.
- current JD evidence exists for role-specific fit, apply-now, or tailored resume claims.
- each runtime weight has hard-data provenance or is marked unavailable.
- required role outputs are present and not blocked for final fields.
- HR review and factual review have passed where applicable.

If not, return a blocked or degraded package with:

- what is known.
- what is safe to say now.
- `blocked_application_targets_without_public_url`.
- `runtime_research_tasks`.
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

