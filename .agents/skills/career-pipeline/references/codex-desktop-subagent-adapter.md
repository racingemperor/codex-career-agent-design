# Codex Desktop Subagent Adapter

Use this reference when a Codex Desktop or Codex app thread has current-session subagent tools available and the career pipeline needs real role execution without a separate API, Codex CLI runner, or external adapter command.

This adapter is a controller-side protocol. Python scripts cannot directly call `multi_agent_v1.spawn_agent`, `multi_agent_v1.wait_agent`, or `multi_agent_v1.close_agent`; only the main Codex controller in the active conversation can use those tools. The scripts build and validate the run artifacts. The main Codex controller performs the live subagent dispatch.

## Preconditions

Before using this adapter:

1. A run directory exists under `.career-pipeline-runs/<run_id>/`.
2. `runtime_context_packet.json` and role `secondary_prompt_injection` files exist.
3. Prompt bundles have been built with `build_subagent_plan.py --build-prompt-bundles`.
4. `invocations/subagent_work_orders.json` exists.
5. The public source plan has been built and the controller has applied `source-policy.md`.
6. Recruitment roles have automatic public source instructions from `data/company_signals/default_recruitment_source_matrix.zh-CN.json`.
7. No role is instructed to use private resumes, login-only pages, private HR messages, recruiter backends, or non-public candidate profiles.

If current JD evidence, public URLs, or user-owned facts are missing, the affected role should return blocked or degraded outputs instead of guessing.

## Execution Algorithm

The main Codex controller must:

1. Read `invocations/subagent_work_orders.json`.
2. Group work orders by the plan's `dispatch_batches`.
3. Run one batch at a time, using each order's `batch_id`.
4. Spawn no more than `max_parallel_subagents` in the current batch.
5. For each order, read its `prompt_bundle_ref` and pass the bounded prompt bundle to a child agent with `multi_agent_v1.spawn_agent`.
6. Require the child agent to return JSON only, containing:
   - `invocation_ref`
   - `role_output_packet`
   - `error_recovery_state`
7. Use `multi_agent_v1.wait_agent` to collect completed child outputs.
8. Validate that each returned JSON includes the required top-level fields and the role output fields from the prompt bundle.
9. Persist each accepted output to the role's `output_artifact_target`.
10. Use `multi_agent_v1.close_agent` after the role output artifact is persisted.
11. Start the next batch only after every required output in the current batch is persisted or explicitly blocked.
12. Pass only artifact refs, evidence refs, and accepted merge fields to later batches; do not rely on closed subagent chat memory.

The child-agent prompt should include the whole prompt bundle content needed for the role, plus this controller instruction:

```text
Return strict JSON only. Do not include Markdown fences, prose, or extra commentary. The JSON must include invocation_ref, role_output_packet, and error_recovery_state. If evidence is missing, return blocked fields and runtime_research_tasks instead of final claims.
```

## Backfill And Finalization

After child outputs are persisted, backfill them through the existing runtime scripts so the same schema, recovery, HR, factual, and final gates remain in force.

Use manual-controller metadata because the real execution happened through the current Codex controller rather than `run_subagent_adapter.py`:

```bash
python scripts/execute_subagent_plan.py --manual-controller-execution --run-dir ../../../.career-pipeline-runs/<run_id> --backfill-output job-scout=C:/path/to/job-scout.output.json
python scripts/finalize_runtime_run.py --execution-mode manual-controller --run-dir ../../../.career-pipeline-runs/<run_id> --real-subagent-execution
```

Backfill every required role output, not only the example role above. Finalization is allowed only after the finalizer accepts the run.

## Failure Handling

- Malformed JSON: ask the same child agent for one schema repair, repeating the required top-level fields and `output_artifact_target`.
- Missing required fields: treat the role as `malformed`; do not merge final decision fields.
- Blocked role output: persist the blocked output and stop dependent finalization unless the error recovery protocol allows a safe partial merge.
- Missing public URLs for recommended jobs or internships: block concrete application recommendations.
- Missing current JD for target-job fit or tailored resume: block apply-now, role-specific fit, and tailored resume claims.
- Weak social evidence only: keep it as preparation or risk signal; do not let it set weights or final decisions alone.
- Tool timeout: wait once more if the child is still progressing; otherwise persist a blocked recovery packet and close the agent.

Do not mark a role as complete from an unstructured summary, private chat excerpt, login-only source, or single-pass prose.

## Real-Execution Rule

Set `real_subagent_execution = true` only when outputs came from separated spawned agents or strictly separated role passes that followed the prompt bundles, source policy, privacy constraints, and role output contracts.

For this Codex Desktop adapter, the expected real path is:

```text
main Codex controller
  -> read subagent_work_orders.json
  -> batch by dispatch_batches
  -> multi_agent_v1.spawn_agent per role order
  -> multi_agent_v1.wait_agent for JSON role output
  -> persist output_artifact_target
  -> multi_agent_v1.close_agent
  -> execute_subagent_plan.py --manual-controller-execution
  -> finalize_runtime_run.py --execution-mode manual-controller
```

Work orders, prompt bundles, mock outputs, or a single controller-written answer are not proof of real subagent execution.
