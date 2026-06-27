#!/usr/bin/env python
import argparse
import json
import shutil
import subprocess
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

ROLE_OUTPUT_LIST_FIELDS = [
    "evidence_packet_refs",
    "artifact_refs",
    "blocked_outputs",
    "runtime_research_tasks",
    "needs_user_confirmation",
    "handoff_to",
    "errors",
]

ALLOWED_ROLE_OUTPUT_STATUSES = {
    "done",
    "done_with_warnings",
    "needs_context",
    "blocked",
    "failed",
    "malformed",
}

SUCCESS_ROLE_OUTPUT_STATUSES = {"done", "done_with_warnings"}

FINAL_DECISION_FIELDS = {
    "fit_score",
    "priority",
    "application_priority",
    "application_strategy",
    "positioning_verdict",
    "pass_to_next_stage",
    "final_resume_draft",
    "resume_draft",
    "tailored_resume",
    "hr_pass_status",
    "current_fit_assessment",
    "application_readiness_decision",
    "learning_plan_before_application",
    "targeted_resume_tailoring",
}


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


def require_list(value: Any, field: str) -> None:
    if not isinstance(value, list):
        raise SubagentAdapterError(f"role_output_packet: `{field}` must be a list")


def validate_external_role_output(payload: dict[str, Any], order: dict[str, Any]) -> dict[str, Any]:
    for field in ["invocation_ref", "role_output_packet", "error_recovery_state"]:
        if payload.get(field) in ("", None, [], {}):
            raise SubagentAdapterError(f"adapter output missing required top-level field `{field}`")
    if payload["invocation_ref"] != order["invocation_ref"]:
        raise SubagentAdapterError("adapter output invocation_ref does not match work order")
    packet = payload["role_output_packet"]
    if not isinstance(packet, dict):
        raise SubagentAdapterError("adapter output role_output_packet must be an object")
    for field in ROLE_OUTPUT_PACKET_REQUIRED_FIELDS:
        if field not in packet:
            raise SubagentAdapterError(f"role_output_packet: missing required field `{field}`")
        if field in {"invocation_id", "target_agent", "status", "role_output_ref", "confidence"} and packet[
            field
        ] in ("", None):
            raise SubagentAdapterError(f"role_output_packet: required field `{field}` is empty")
    for field in ROLE_OUTPUT_LIST_FIELDS:
        require_list(packet[field], field)
    if packet["target_agent"] != order["target_agent"]:
        raise SubagentAdapterError("adapter output target_agent does not match work order")
    if packet["role_output_ref"] != order["output_artifact_target"]:
        raise SubagentAdapterError("adapter output role_output_ref must equal output_artifact_target")
    if packet["status"] not in ALLOWED_ROLE_OUTPUT_STATUSES:
        raise SubagentAdapterError(f"role_output_packet: unsupported status `{packet['status']}`")
    if packet["status"] in {"failed", "malformed"}:
        forbidden = sorted(field for field in FINAL_DECISION_FIELDS if field in payload)
        if forbidden:
            raise SubagentAdapterError(
                "failed or malformed role outputs must not include final decision fields: "
                + ", ".join(forbidden)
            )
    recovery = payload["error_recovery_state"]
    if not isinstance(recovery, dict):
        raise SubagentAdapterError("error_recovery_state must be an object")
    for field in [
        "status",
        "errors",
        "recovery_actions",
        "degraded_outputs",
        "blocked_outputs",
        "safe_outputs",
        "next_action",
    ]:
        if field not in recovery:
            raise SubagentAdapterError(f"error_recovery_state: missing required field `{field}`")
    for field in ["errors", "recovery_actions", "degraded_outputs", "blocked_outputs", "safe_outputs"]:
        if not isinstance(recovery[field], list):
            raise SubagentAdapterError(f"error_recovery_state: `{field}` must be a list")
    return packet


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


def build_external_command_input(run_dir: Path, run_id: str, order: dict[str, Any]) -> dict[str, Any]:
    invocation = load_invocation(run_dir, order["invocation_ref"])
    prompt_bundle = load_prompt_bundle(run_dir, order["prompt_bundle_ref"])
    return {
        "adapter_request": {
            "run_id": run_id,
            "adapter_mode": "external-command",
            "created_at": utc_now(),
            "redaction_applied": True,
            "instructions": (
                "Produce a JSON file at --output-json with invocation_ref, role_output_packet, "
                "and error_recovery_state. Do not fabricate unsupported final decisions."
            ),
        },
        "work_order": order,
        "subagent_invocation": invocation,
        "subagent_prompt_bundle": prompt_bundle,
    }


def run_external_command_for_order(
    run_dir: Path,
    run_id: str,
    order: dict[str, Any],
    adapter_command: str,
    adapter_args: list[str],
) -> tuple[str, dict[str, Any]]:
    target_agent = order["target_agent"]
    cache_dir = run_dir / "cache" / "subagent_adapter"
    command_input_path = cache_dir / f"{target_agent}.work_order.json"
    raw_output_path = cache_dir / f"{target_agent}.adapter_output.json"
    write_json(command_input_path, build_external_command_input(run_dir, run_id, order))
    command = [
        adapter_command,
        *adapter_args,
        "--work-order-json",
        str(command_input_path),
        "--output-json",
        str(raw_output_path),
    ]
    started_at = utc_now()
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    finished_at = utc_now()
    if result.returncode != 0:
        raise SubagentAdapterError(
            f"adapter command failed for {target_agent} with exit code {result.returncode}: "
            f"{result.stderr.strip()}"
        )
    if not raw_output_path.is_file():
        raise SubagentAdapterError(f"adapter command did not write output for {target_agent}")
    payload = load_json(raw_output_path)
    packet = validate_external_role_output(payload, order)
    payload.setdefault("adapter_metadata", {})
    payload["adapter_metadata"].update(
        {
            "run_id": run_id,
            "target_agent": target_agent,
            "adapter_mode": "external-command",
            "adapter_kind": "command",
            "adapter_command_ref": adapter_command,
            "adapter_exit_code": result.returncode,
            "adapter_started_at": started_at,
            "adapter_finished_at": finished_at,
            "real_subagent_execution": True,
            "source_work_order_ref": "invocations/subagent_work_orders.json",
            "validation_status": "passed",
            "redaction_applied": True,
            "mock_or_seed_source": False,
        }
    )
    output_path = run_dir / order["output_artifact_target"]
    write_json(output_path, payload)
    return rel(output_path, run_dir), packet


def run_adapter(args: argparse.Namespace) -> dict[str, Any]:
    if not args.mock_blocked and not args.adapter_command:
        raise SubagentAdapterError(
            "no real subagent adapter is configured; rerun with --mock-blocked or provide an external adapter"
        )
    run_dir = args.run_dir
    work_orders = load_work_orders(run_dir, args.work_orders_ref)
    run_id = work_orders["run_id"]
    output_refs = []
    role_statuses = []
    if args.mock_blocked:
        adapter_mode = "mock-blocked"
        real_subagent_execution = False
        exit_status = "blocked"
        next_action = "configure_real_adapter"
        for order in work_orders["orders"]:
            output_payload = build_mock_blocked_output(run_dir, run_id, order)
            output_ref = output_payload["role_output_packet"]["role_output_ref"]
            output_path = run_dir / output_ref
            write_json(output_path, output_payload)
            output_refs.append(rel(output_path, run_dir))
            role_statuses.append(output_payload["role_output_packet"]["status"])
    else:
        adapter_mode = "external-command"
        real_subagent_execution = True
        for order in work_orders["orders"]:
            output_ref, packet = run_external_command_for_order(
                run_dir,
                run_id,
                order,
                args.adapter_command,
                args.adapter_arg,
            )
            output_refs.append(output_ref)
            role_statuses.append(packet["status"])
        if all(status in SUCCESS_ROLE_OUTPUT_STATUSES for status in role_statuses):
            exit_status = "success"
            next_action = "finalize_or_merge_role_outputs"
        else:
            real_subagent_execution = False
            exit_status = "blocked"
            next_action = "repair_or_retry_blocked_role_outputs"
    log_path = run_dir / "logs" / "subagent_adapter_events.json"
    write_json(
        log_path,
        {
            "subagent_adapter_events": {
                "run_id": run_id,
                "adapter_mode": adapter_mode,
                "adapter_kind": "command" if args.adapter_command else "mock",
                "adapter_command_ref": args.adapter_command,
                "real_subagent_execution": real_subagent_execution,
                "created_at": utc_now(),
                "work_orders_ref": args.work_orders_ref,
                "output_refs": output_refs,
                "role_statuses": role_statuses,
                "next_action": next_action,
                "redaction_applied": True,
            }
        },
    )
    blocked_by = [] if real_subagent_execution else ["real_subagent_adapter_not_configured"]
    return {
        "subagent_adapter_response": {
            "exit_status": exit_status,
            "run_id": run_id,
            "adapter_mode": adapter_mode,
            "real_subagent_execution": real_subagent_execution,
            "work_orders_ref": args.work_orders_ref,
            "output_refs": output_refs,
            "adapter_events_ref": rel(log_path, run_dir),
            "blocked_by": blocked_by,
            "next_action": next_action,
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
    parser.add_argument(
        "--adapter-command",
        default="",
        help="External adapter executable. The runner appends --work-order-json and --output-json.",
    )
    parser.add_argument(
        "--adapter-arg",
        action="append",
        default=[],
        help="Argument passed to --adapter-command before generated --work-order-json/--output-json.",
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
