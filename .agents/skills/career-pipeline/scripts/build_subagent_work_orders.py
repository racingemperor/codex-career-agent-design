#!/usr/bin/env python
import argparse
import json
import sys
from pathlib import Path
from typing import Any


class WorkOrderError(Exception):
    pass


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def load_plan(run_dir: Path, plan_ref: str) -> dict[str, Any]:
    payload = load_json(run_dir / plan_ref)
    plan = payload.get("subagent_invocation_plan")
    if not isinstance(plan, dict):
        raise WorkOrderError(f"{plan_ref}: missing subagent_invocation_plan")
    queue = plan.get("dispatch_queue")
    if not isinstance(queue, list) or not queue:
        raise WorkOrderError(f"{plan_ref}: dispatch_queue must be non-empty")
    return plan


def build_orders(run_dir: Path, plan_ref: str, output_ref: str) -> dict[str, Any]:
    plan = load_plan(run_dir, plan_ref)
    orders = []
    for item in plan["dispatch_queue"]:
        prompt_bundle_ref = item.get("prompt_bundle_ref") or ""
        if not prompt_bundle_ref:
            raise WorkOrderError(
                "prompt_bundle_ref is required; rebuild the plan with --build-prompt-bundles"
            )
        if any(ref.replace("\\", "/").startswith("input/raw_refs") for ref in item["input_refs"]):
            raise WorkOrderError("work orders must not expose raw input refs")
        prompt_bundle = load_json(run_dir / prompt_bundle_ref).get("subagent_prompt_bundle")
        if not isinstance(prompt_bundle, dict):
            raise WorkOrderError(f"{prompt_bundle_ref}: missing subagent_prompt_bundle")
        orders.append(
            {
                "order_id": f"{plan['run_id']}-{item['queue_index']}-{item['target_agent']}",
                "target_agent": item["target_agent"],
                "batch_id": item.get("batch_id", ""),
                "depends_on_batches": item.get("depends_on_batches", []),
                "depends_on_agents": item.get("depends_on_agents", []),
                "depends_on_artifact_refs": item.get("depends_on_artifact_refs", []),
                "close_after_artifact_persisted": item.get("close_after_artifact_persisted") is True,
                "invocation_ref": item["invocation_ref"],
                "prompt_bundle_ref": prompt_bundle_ref,
                "output_artifact_target": item["output_artifact_target"],
                "allowed_network": False,
                "requires_human_approval": True,
                "source_policy_ack_required": True,
                "privacy_class": item["privacy_class"],
                "dispatch_status": "ready_for_external_adapter",
                "execution_instruction": (
                    "Dispatch according to batch_id and depends_on_artifact_refs. Pass the "
                    "prompt_bundle_ref content to a real Codex subagent only after human approval "
                    "and source-policy acknowledgement. Return a role output matching "
                    "expected_backfill_contract, persist_role_output_before_close, then close the "
                    "completed subagent when close_after_artifact_persisted is true."
                ),
                "expected_backfill_contract": {
                    "required_top_level_fields": [
                        "invocation_ref",
                        "role_output_packet",
                        "error_recovery_state",
                    ],
                    "required_role_output_fields": prompt_bundle["required_output_fields"],
                    "forbidden_without_evidence": [
                        "fit_score",
                        "application_priority",
                        "application_strategy",
                        "final_resume_draft",
                    ],
                },
            }
        )
    payload = {
        "subagent_work_orders": {
            "run_id": plan["run_id"],
            "created_from_plan_ref": plan_ref,
            "adapter_status": "not_configured",
            "real_execution_ready": False,
            "dispatch_strategy": plan.get("dispatch_strategy", "batched_artifact_handoff"),
            "dispatch_batches": plan.get("dispatch_batches", []),
            "max_parallel_subagents": plan.get("max_parallel_subagents", 4),
            "artifact_handoff_required": plan.get("artifact_handoff_required") is True,
            "close_completed_subagents": plan.get("close_completed_subagents") is True,
            "orders": orders,
            "notes": [
                "This file is a handoff contract, not proof of execution.",
                "Network and source-policy gates stay closed until an adapter is configured.",
                "Run one dispatch batch at a time, persist role outputs as artifacts, then close completed subagents before opening the next batch.",
            ],
        }
    }
    output_path = run_dir / output_ref
    write_json(output_path, payload)
    return {
        "work_order_response": {
            "exit_status": "success",
            "run_id": plan["run_id"],
            "work_orders_ref": rel(output_path, run_dir),
            "order_count": len(orders),
        }
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build real-subagent handoff work orders.")
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--plan-ref", default="invocations/subagent_invocation_plan.json")
    parser.add_argument("--output", default="invocations/subagent_work_orders.json")
    args = parser.parse_args(argv)
    try:
        print(json.dumps(build_orders(args.run_dir, args.plan_ref, args.output), ensure_ascii=False, indent=2))
        return 0
    except (OSError, json.JSONDecodeError, KeyError, WorkOrderError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
