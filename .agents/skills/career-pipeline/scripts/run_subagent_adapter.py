#!/usr/bin/env python
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class SubagentAdapterError(Exception):
    pass


ROLE_OUTPUT_PACKET_REQUIRED_FIELDS = [
    "invocation_id",
    "target_agent",
    "status",
    "role_output_ref",
    "evidence_packet_refs",
    "runtime_weights_ref",
    "artifact_refs",
    "blocked_outputs",
    "runtime_research_tasks",
    "needs_user_confirmation",
    "handoff_to",
    "errors",
    "confidence",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def load_work_orders(run_dir: Path, work_orders_ref: str) -> dict[str, Any]:
    payload = load_json(run_dir / work_orders_ref)
    work_orders = payload.get("subagent_work_orders")
    if not isinstance(work_orders, dict):
        raise SubagentAdapterError(f"{work_orders_ref}: missing subagent_work_orders")
    orders = work_orders.get("orders")
    if not isinstance(orders, list) or not orders:
        raise SubagentAdapterError(f"{work_orders_ref}: orders must be non-empty")
    return work_orders


def load_invocation(run_dir: Path, invocation_ref: str) -> dict[str, Any]:
    payload = load_json(run_dir / invocation_ref)
    invocation = payload.get("subagent_invocation")
    if not isinstance(invocation, dict):
        raise SubagentAdapterError(f"{invocation_ref}: missing subagent_invocation")
    return invocation


def load_prompt_bundle(run_dir: Path, prompt_bundle_ref: str) -> dict[str, Any]:
    payload = load_json(run_dir / prompt_bundle_ref)
    bundle = payload.get("subagent_prompt_bundle")
    if not isinstance(bundle, dict):
        raise SubagentAdapterError(f"{prompt_bundle_ref}: missing subagent_prompt_bundle")
    return bundle


def list_from_bundle(bundle: dict[str, Any], field: str) -> list[Any]:
    value = bundle.get(field)
    return value if isinstance(value, list) else []


def build_mock_blocked_output(run_dir: Path, run_id: str, order: dict[str, Any]) -> dict[str, Any]:
    target_agent = str(order.get("target_agent") or "")
    invocation_ref = str(order.get("invocation_ref") or "")
    prompt_bundle_ref = str(order.get("prompt_bundle_ref") or "")
    if not target_agent or not invocation_ref or not prompt_bundle_ref:
        raise SubagentAdapterError("each work order needs target_agent, invocation_ref, and prompt_bundle_ref")
    invocation = load_invocation(run_dir, invocation_ref)
    prompt_bundle = load_prompt_bundle(run_dir, prompt_bundle_ref)
    output_ref = str(order.get("output_artifact_target") or f"agents/{target_agent}/output.json")
    runtime_research_tasks = list_from_bundle(prompt_bundle, "research_tasks")
    hard_data_weight_tasks = list_from_bundle(prompt_bundle, "hard_data_weight_tasks")
    packet = {
        "invocation_id": invocation["invocation_id"],
        "target_agent": target_agent,
        "status": "blocked",
        "role_output_ref": output_ref,
        "evidence_packet_refs": [],
        "runtime_weights_ref": "merge/runtime_weights.json",
        "artifact_refs": [prompt_bundle_ref],
        "blocked_outputs": [
            "real_subagent_execution",
            "adapter_produced_role_judgment",
            "final_role_decision",
        ],
        "runtime_research_tasks": runtime_research_tasks + hard_data_weight_tasks,
        "needs_user_confirmation": [],
        "handoff_to": ["career-orchestrator"],
        "errors": [
            {
                "category": "subagent_failed",
                "severity": "blocking",
                "message": (
                    "Mock adapter wrote a schema-valid blocked packet. Configure a real Codex "
                    "Desktop, Codex CLI, API, or Agents SDK adapter before treating this role "
                    "as executed."
                ),
            }
        ],
        "confidence": "low",
    }
    for field in ROLE_OUTPUT_PACKET_REQUIRED_FIELDS:
        if field not in packet:
            raise SubagentAdapterError(f"internal error: missing role_output_packet field {field}")
    return {
        "invocation_ref": invocation_ref,
        "role_output_packet": packet,
        "error_recovery_state": {
            "status": "blocked",
            "errors": packet["errors"],
            "recovery_actions": ["configure_real_adapter", "run_real_subagent_or_backfill_output"],
            "degraded_outputs": ["adapter_handoff_contract"],
            "blocked_outputs": packet["blocked_outputs"],
            "safe_outputs": ["prompt_bundle_ref", "expected_backfill_contract", "runtime_research_tasks"],
            "next_action": "configure_real_adapter",
        },
        "adapter_metadata": {
            "run_id": run_id,
            "target_agent": target_agent,
            "adapter_mode": "mock-blocked",
            "real_subagent_execution": False,
            "created_at": utc_now(),
            "prompt_bundle_ref": prompt_bundle_ref,
            "expected_backfill_contract": order.get("expected_backfill_contract", {}),
            "note": "This output is schema-valid blocked handoff data, not a role judgment.",
        },
    }


def run_adapter(args: argparse.Namespace) -> dict[str, Any]:
    if not args.mock_blocked:
        raise SubagentAdapterError(
            "no real subagent adapter is configured; rerun with --mock-blocked or provide an external adapter"
        )
    run_dir = args.run_dir
    work_orders = load_work_orders(run_dir, args.work_orders_ref)
    run_id = work_orders["run_id"]
    output_refs = []
    for order in work_orders["orders"]:
        output_payload = build_mock_blocked_output(run_dir, run_id, order)
        output_ref = output_payload["role_output_packet"]["role_output_ref"]
        output_path = run_dir / output_ref
        write_json(output_path, output_payload)
        output_refs.append(rel(output_path, run_dir))
    log_path = run_dir / "logs" / "subagent_adapter_events.json"
    write_json(
        log_path,
        {
            "subagent_adapter_events": {
                "run_id": run_id,
                "adapter_mode": "mock-blocked",
                "real_subagent_execution": False,
                "created_at": utc_now(),
                "work_orders_ref": args.work_orders_ref,
                "output_refs": output_refs,
                "next_action": "configure_real_adapter",
            }
        },
    )
    return {
        "subagent_adapter_response": {
            "exit_status": "blocked",
            "run_id": run_id,
            "adapter_mode": "mock-blocked",
            "real_subagent_execution": False,
            "work_orders_ref": args.work_orders_ref,
            "output_refs": output_refs,
            "adapter_events_ref": rel(log_path, run_dir),
            "blocked_by": ["real_subagent_adapter_not_configured"],
            "next_action": "configure_real_adapter",
        }
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run or stub a career-pipeline subagent adapter.")
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--work-orders-ref", default="invocations/subagent_work_orders.json")
    parser.add_argument(
        "--mock-blocked",
        action="store_true",
        help="Write schema-valid blocked role outputs without claiming real subagent execution.",
    )
    args = parser.parse_args(argv)
    try:
        print(json.dumps(run_adapter(args), ensure_ascii=False, indent=2))
        return 0
    except (OSError, json.JSONDecodeError, KeyError, SubagentAdapterError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
