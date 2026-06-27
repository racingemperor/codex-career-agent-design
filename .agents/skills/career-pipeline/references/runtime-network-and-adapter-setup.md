# Runtime Network And Adapter Setup

Use this reference before enabling real network fetches or real subagent execution for the career pipeline.

The runtime has two separate gates:

- Codex platform permission: whether commands and subagents may use the network at all.
- Career pipeline source permission: whether a specific public source is allowed by `source-policy.md` and the run's public source plan.

Do not treat platform network access as permission to crawl recruitment platforms, login-only pages, private candidate data, private chats, HR backends, or non-public resumes.

## Automatic Recruitment Source Injection

Keep recruitment-source selection inside the role prompt injection. Recruitment-information roles must receive `automatic_public_recruitment_research` in their `secondary_prompt_injection` and must use `data/company_signals/default_recruitment_source_matrix.zh-CN.json` as the default source matrix.

The user does not need to name websites. When the pipeline reaches `JobScout`, `JDAnalyzer`, `CompanyIntelligenceAnalyst`, `MarketSentimentAnalyzer`, or `HRSupervisor`, these roles should automatically create public-source research tasks for official career pages, official campus pages, public recruitment-platform JDs, verified HR public posts, candidate experience sources, social-media weak signals, and public reports.

The injected field should include:

```json
{
  "automatic_public_recruitment_research": {
    "enabled": true,
    "user_instruction_required": false,
    "source_matrix_ref": "data/company_signals/default_recruitment_source_matrix.zh-CN.json",
    "default_public_recruitment_source_targets": [],
    "forbidden_source_types": [
      "private_resume",
      "private_chat",
      "private_hr_message",
      "recruiter_backend",
      "login_only_page",
      "non_public_candidate_profile"
    ]
  }
}
```

The runtime controller or adapter records `source_policy_ack` internally only after the auto-generated public source plan passes policy checks. Do not expose `source_policy_ack` as a separate end-user question.

If Codex platform network permission is unavailable, do not ask the user to edit config as the first response. Return a graceful degraded package: the public-source research plan, what outputs remain blocked, and a compact request for either current JD text, official links, or permission to continue in a network-enabled Codex session.

If a source in the default matrix is login-only, private, blocked by access controls, or exposes non-public candidate or HR data, skip it and explain that only public evidence can be used. Automatic source injection never authorizes login bypass, CAPTCHA bypass, private-message access, backend access, or scraping non-public resumes.

## Codex Network Permission

For repeatable local runs, the user or local administrator may configure Codex command network access in `~/.codex/config.toml` or a trusted project `.codex/config.toml`. This is an installation concern, not a normal end-user question inside the career pipeline:

```toml
[sandbox_workspace_write]
network_access = true

[features.network_proxy]
enabled = true
domains = {
  "**.zhipin.com" = "allow",
  "**.liepin.com" = "allow",
  "**.lagou.com" = "allow",
  "**.nowcoder.com" = "allow",
  "**.linkedin.com" = "allow",
  "**.bytedance.com" = "allow",
  "**.tencent.com" = "allow",
  "**.dji.com" = "allow",
  "**.catl.com" = "allow",
  "**.zhipuai.cn" = "allow"
}
```

Restart Codex after changing config. The domain list is an example allowlist; keep it scoped to the sources needed by the run. Do not use a global `*` allow rule unless the user explicitly accepts broad outbound access risk.

Web search and shell network access are separate. A web search result is not a validated evidence packet until it has been converted into a source-plan-backed evidence packet and passed through the source policy checks.

## Pipeline Source Permission

Before any real source fetch:

1. Build a run with `simulate_runtime_run.py` or the future real runner.
2. Build prompt bundles and the public source plan.
3. Have the controller record `source_policy_ack` internally when recruitment-information roles have received the default source matrix and the auto-generated source plan passes policy checks.
4. Use a search adapter to search the source-plan queries and write public search results.
5. Run `discover_public_sources.py` to filter search results into `allowed_public_sources.generated.json`.
6. Fetch and backfill evidence.

Example:

```bash
cd .agents/skills/career-pipeline
python scripts/build_public_source_plan.py --run-dir ../../../.career-pipeline-runs/<run_id>
python scripts/discover_public_sources.py --run-dir ../../../.career-pipeline-runs/<run_id> --generate-query-plan-only
python scripts/search_public_sources.py --run-dir ../../../.career-pipeline-runs/<run_id> --provider seed
python scripts/search_public_sources.py --run-dir ../../../.career-pipeline-runs/<run_id> --provider external-json --search-results-json <search_results.json>
python scripts/discover_public_sources.py --run-dir ../../../.career-pipeline-runs/<run_id> --search-results-json <search_results.json>
python scripts/fetch_public_sources.py --run-dir ../../../.career-pipeline-runs/<run_id> --sources-json ../../../.career-pipeline-runs/<run_id>/evidence/allowed_public_sources.generated.json
python scripts/backfill_public_evidence.py --run-dir ../../../.career-pipeline-runs/<run_id> --evidence-json ../../../.career-pipeline-runs/<run_id>/evidence/fetched_public_evidence.json
```

`--generate-query-plan-only` writes `evidence/public_source_discovery_log.json`; a browser/search/API adapter should execute those queries and save the resulting public URLs as `search_results.json`.

For local contract tests, `search_public_sources.py --provider seed` can create `evidence/search_results.generated.json` from the query plan. This provider is deterministic and local. It uses `data/company_signals/source_collection_targets.zh-CN.json` plus generic public-source entrypoints to prove the pipeline can discover and filter source URLs automatically, but it is not live web search and should not be treated as fresh recruitment evidence.

For live browsing, browser search, or API search, write results to the minimal search-adapter shape and pass them through `search_public_sources.py --provider external-json --search-results-json <search_results.json>`. This records the external search result file in the run and marks `real_time_search = true`, but the URLs are still only candidates until `discover_public_sources.py`, `fetch_public_sources.py`, and `backfill_public_evidence.py` accept them.

Minimal search adapter result shape:

```json
{
  "search_results": [
    {
      "task_id": "target-current-jd-verification",
      "url": "https://careers.example.com/jobs/123",
      "title": "Backend Engineer Intern",
      "snippet": "Java, MySQL, distributed systems"
    }
  ]
}
```

`discover_public_sources.py` writes `evidence/allowed_public_sources.generated.json` in the same shape accepted by `fetch_public_sources.py`:

```json
{
  "sources": [
    {
      "task_id": "target-current-jd-verification",
      "source_type": "official_or_primary",
      "source_ref": "https://careers.example.com/jobs/123",
      "field": "current_jd_text"
    }
  ]
}
```

If no search results are available, `discover_public_sources.py` still writes a discovery log with generated queries and an empty `sources` list. The pipeline should return blocked/degraded public-research outputs rather than asking the user to name websites.

Allowed source types include `official_or_primary`, `official_school_notice`, `recruitment_platform_jd`, `verified_hr_public_post`, `candidate_experience_secondary`, `social_media_weak`, `public_report`, and `user_provided`.

Forbidden sources include `private_resume`, `private_chat`, `private_hr_message`, `recruiter_backend`, `login_only_page`, and `non_public_candidate_profile`. A login-only page remains forbidden even if the user is personally logged in. Social media weak signals must not set final decisions or weights alone.

When `execute_subagent_plan.py` is used with network execution flags, it must include both human approval and source policy acknowledgement:

```bash
python scripts/execute_subagent_plan.py \
  --run-dir ../../../.career-pipeline-runs/<run_id> \
  --execute \
  --human-approved \
  --allow-network \
  --source-policy-ack \
  --adapter <configured-adapter-name-or-path>
```

Without `source_policy_ack`, network execution must fail.

## Real Subagent Adapter

The repository scripts generate adapter-ready contracts. They do not directly call Codex Desktop subagent tools.

Current handoff flow:

```bash
python scripts/build_subagent_plan.py --run-dir ../../../.career-pipeline-runs/<run_id> --build-prompt-bundles
python scripts/build_subagent_work_orders.py --run-dir ../../../.career-pipeline-runs/<run_id>
python scripts/run_subagent_adapter.py --run-dir ../../../.career-pipeline-runs/<run_id> --mock-blocked
python scripts/run_subagent_adapter.py --run-dir ../../../.career-pipeline-runs/<run_id> --adapter-command <adapter-executable> --adapter-arg <adapter-script-or-config>
python scripts/finalize_runtime_run.py --run-dir ../../../.career-pipeline-runs/<run_id> --real-subagent-execution
```

The adapter reads:

- `invocations/subagent_work_orders.json`
- each order's `prompt_bundle_ref`
- each order's `expected_backfill_contract`
- the run's source and privacy constraints

The adapter must return one JSON file per role with:

- `invocation_ref`
- `role_output_packet`
- `error_recovery_state`

Each `role_output_packet` must include the required fields from `role-output-contracts.md`. Failed or malformed role outputs must not include final decision fields such as `fit_score`, `application_priority`, `application_strategy`, `final_resume_draft`, or `tailored_resume`.

`run_subagent_adapter.py --mock-blocked` is only a schema and handoff harness. It writes one blocked role output per work order, sets `real_subagent_execution = false`, and sets `error_recovery_state.next_action = "configure_real_adapter"`. Use it to test user-side orchestration without wasting tokens, not to produce career judgments.

`run_subagent_adapter.py --adapter-command ...` is the local command-adapter bridge. The runner appends `--work-order-json <file>` and `--output-json <file>` to the command for each work order. The external command must write a role output containing `invocation_ref`, `role_output_packet`, and `error_recovery_state`. The runner validates the output, copies it to the role's `output_artifact_target`, records adapter metadata, and sets `real_subagent_execution = true` only when all required role outputs are `done` or `done_with_warnings`.

`finalize_runtime_run.py` is intentionally stricter than schema validation. It rejects mock outputs, blocked outputs, failed or malformed outputs, missing role outputs, and outputs without real adapter metadata. A final package is allowed only when required roles are complete and final gates can be marked ready.

Backfill role outputs after the real adapter finishes:

```bash
python scripts/execute_subagent_plan.py \
  --run-dir ../../../.career-pipeline-runs/<run_id> \
  --backfill-output job-scout=C:/path/to/job-scout.output.json \
  --backfill-output hr-supervisor=C:/path/to/hr-supervisor.output.json
```

## Adapter Options

Use one of these adapter patterns:

1. Manual Controller MVP.
   - The main Codex conversation acts as the controller.
   - It performs Codex-side source search from the generated source plan and writes or assembles `search_results.json`.
   - It records `source_policy_ack` internally after the source plan passes policy checks.
   - It reads `subagent_work_orders.json` and each prompt bundle.
   - It dispatches each role as a true subagent, separate conversation, or strictly separated role pass.
   - It requires every role to return strict JSON with `role_output_packet` and `error_recovery_state`.
   - API is not required, but source URLs, role output contracts, HR review, factual review, and blocked/final gates still apply.
   - Use `references/manual-controller-runtime-flow.md` for the detailed procedure.

2. Codex Desktop manual controller adapter.
   - The main Codex thread reads `subagent_work_orders.json`.
   - It reads each `prompt_bundle_ref`.
   - It calls the current-session `spawn_agent` tool for each bounded role task.
   - It asks each subagent to return a strict role output JSON.
   - It writes or supplies those JSON files for backfill.
   - This is valid for interactive testing, but normal Python scripts cannot call the conversation's `spawn_agent` tool directly.

3. Codex CLI adapter.
   - A runner reads each work order.
   - It invokes `codex exec` with the prompt bundle content.
   - It stores each final answer as a role output JSON.
   - It backfills validated outputs into the run.
   - Use this for local automation when Codex CLI access and auth are configured.

4. API or Agents SDK adapter.
   - An external runner calls an agent API with each role prompt bundle.
   - It validates the model output against the role output schema.
   - It backfills accepted packets.
   - Use this for productized execution, billing control, and independent observability.

Do not mark a run as real subagent execution merely because work orders exist. Real execution is true only after adapter-produced role output packets are validated and backfilled.

## Completion Checklist

Before returning a final career package:

- Platform network permission is enabled only when needed.
- The public source plan exists.
- `source_policy_ack` is recorded for network execution.
- No login-only, private, backend, or non-public candidate source is used.
- Each runtime weight has hard-data provenance or is marked `not_available` / `needs_more_sources`.
- Each role output has a valid `role_output_packet`.
- HR supervision and factual review gates are complete when required.
- Blocked outputs remain blocked instead of being converted into guessed recommendations.
