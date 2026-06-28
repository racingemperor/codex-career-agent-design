#!/usr/bin/env python
import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


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

ALLOWED_SOURCE_TYPES = {
    "user_provided",
    "official_or_primary",
    "official_school_notice",
    "recruitment_platform_jd",
    "verified_hr_public_post",
    "candidate_experience_secondary",
    "social_media_weak",
    "repository_prior",
    "public_report",
}

FORBIDDEN_SOURCE_TYPES = {
    "private_resume",
    "private_chat",
    "private_hr_message",
    "recruiter_backend",
    "login_only_page",
    "non_public_candidate_profile",
}

FINAL_DECISION_FIELDS = {
    "fit_score",
    "priority",
    "application_priority",
    "application_strategy",
    "positioning_verdict",
    "pass_to_next_stage",
    "final_resume_draft",
    "growth_resume_preview",
    "resume_draft",
    "tailored_resume",
    "hr_pass_status",
}


class ExecutionError(Exception):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_jsonl(path: Path, payloads: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for payload in payloads:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def require_list(value: Any, field: str) -> None:
    if not isinstance(value, list):
        raise ExecutionError(f"role_output_packet: `{field}` must be a list")


def validate_role_output(payload: dict[str, Any]) -> dict[str, Any]:
    packet = payload.get("role_output_packet")
    if not isinstance(packet, dict):
        raise ExecutionError("role_output_packet is required")
    for field in ROLE_OUTPUT_PACKET_REQUIRED_FIELDS:
        if field not in packet:
            raise ExecutionError(f"role_output_packet: missing required field `{field}`")
        if field in {"invocation_id", "target_agent", "status", "role_output_ref", "confidence"} and packet[field] in (
            "",
            None,
        ):
            raise ExecutionError(f"role_output_packet: required field `{field}` is empty")
    for field in ROLE_OUTPUT_LIST_FIELDS:
        require_list(packet[field], field)
    if packet["status"] not in ALLOWED_ROLE_OUTPUT_STATUSES:
        raise ExecutionError(f"role_output_packet: unsupported status `{packet['status']}`")
    if packet["status"] in {"failed", "malformed"}:
        forbidden = sorted(field for field in FINAL_DECISION_FIELDS if field in payload)
        if forbidden:
            raise ExecutionError(
                "failed or malformed role outputs must not include final decision fields: "
                + ", ".join(forbidden)
            )
    return packet


def load_plan(run_dir: Path, plan_ref: str) -> dict[str, Any]:
    plan_path = run_dir / plan_ref
    payload = load_json(plan_path)
    plan = payload.get("subagent_invocation_plan")
    if not isinstance(plan, dict):
        raise ExecutionError(f"{plan_ref}: missing subagent_invocation_plan")
    queue = plan.get("dispatch_queue")
    if not isinstance(queue, list) or not queue:
        raise ExecutionError(f"{plan_ref}: dispatch_queue must be non-empty")
    return plan


def load_source_plan(run_dir: Path, source_plan_ref: str) -> dict[str, Any]:
    path = run_dir / source_plan_ref
    if not path.is_file():
        raise ExecutionError(f"source plan is required before network execution: {source_plan_ref}")
    payload = load_json(path)
    plan = payload.get("public_source_research_plan")
    if not isinstance(plan, dict):
        raise ExecutionError(f"{source_plan_ref}: missing public_source_research_plan")
    if plan.get("network_execution_default") != "disabled_until_controller_source_policy_ack":
        raise ExecutionError(f"{source_plan_ref}: invalid network execution default")
    errors = []
    tasks = plan.get("research_tasks")
    if not isinstance(tasks, list) or not tasks:
        raise ExecutionError(f"{source_plan_ref}: research_tasks must be non-empty")
    for index, task in enumerate(tasks):
        where = f"{source_plan_ref}.research_tasks[{index}]"
        if not isinstance(task, dict):
            raise ExecutionError(f"{where}: task must be an object")
        source_type = task.get("source_type")
        if source_type in FORBIDDEN_SOURCE_TYPES:
            errors.append(f"{where}: forbidden source_type `{source_type}`")
        elif source_type not in ALLOWED_SOURCE_TYPES:
            errors.append(f"{where}: unsupported source_type `{source_type}`")
        if task.get("requires_login") is True:
            errors.append(f"{where}: requires_login sources are not allowed")
        if source_type == "social_media_weak" and task.get("may_set_final_decision") is True:
            errors.append(f"{where}: social_media_weak cannot be a final decision basis")
        if source_type == "social_media_weak" and task.get("may_set_weight") is True:
            errors.append(f"{where}: social_media_weak cannot set weights alone")
        if source_type == "candidate_experience_secondary" and task.get("may_set_final_decision") is True:
            errors.append(f"{where}: candidate_experience_secondary cannot be a final decision basis")
    if errors:
        raise ExecutionError("; ".join(errors))
    return plan


def validate_plan_only(plan: dict[str, Any]) -> None:
    for index, item in enumerate(plan["dispatch_queue"]):
        where = f"dispatch_queue[{index}]"
        if item.get("dispatch_mode") != "plan_only":
            raise ExecutionError(f"{where}: only plan_only dispatch queues are supported by this shell")
        if item.get("status") != "planned":
            raise ExecutionError(f"{where}: status must remain planned before a real adapter runs")
        if item.get("requires_human_approval") is not True:
            raise ExecutionError(f"{where}: human approval is required")


def enforce_execution_gates(args: argparse.Namespace) -> None:
    if args.execute and not args.human_approved:
        raise ExecutionError("human approval is required before --execute can run")
    if args.allow_network and not args.source_policy_ack:
        raise ExecutionError("source policy acknowledgement is required before network execution")
    if args.allow_network:
        load_source_plan(args.run_dir, args.source_plan_ref)
    if args.execute and not args.dry_run and not args.adapter:
        raise ExecutionError("a real subagent adapter is not configured; omit --execute or provide --adapter")


def build_events(run_id: str, plan: dict[str, Any], mode: str, status: str) -> list[dict[str, Any]]:
    events = []
    for item in plan["dispatch_queue"]:
        events.append(
            {
                "execution_event": {
                    "event_id": f"{run_id}-{item['queue_index']}-{mode}",
                    "run_id": run_id,
                    "stage": "agents_running" if mode == "execute" else "injection_ready",
                    "agent_id": item["target_agent"],
                    "event_type": "dispatch",
                    "input_refs": item["input_refs"],
                    "output_refs": [item["output_artifact_target"]],
                    "status": status,
                    "timestamp_or_sequence": utc_now(),
                    "redaction_applied": True,
                    "execution_mode": mode,
                    "network_allowed": item.get("allowed_network") is True,
                    "note": "plan_only queue inspected; no real subagent call is made by default",
                }
            }
        )
    return events


def parse_backfill_args(items: list[str]) -> dict[str, Path]:
    mapping: dict[str, Path] = {}
    for item in items:
        if "=" not in item:
            raise ExecutionError("--backfill-output must use target-agent=path")
        agent, raw_path = item.split("=", 1)
        if not agent:
            raise ExecutionError("--backfill-output target agent is empty")
        mapping[agent] = Path(raw_path)
    return mapping


def attach_manual_controller_metadata(payload: dict[str, Any]) -> None:
    metadata = payload.get("adapter_metadata")
    if isinstance(metadata, dict):
        if metadata.get("adapter_mode") == "mock-blocked" or metadata.get("mock_or_seed_source") is True:
            raise ExecutionError(
                "manual-controller backfill source is a mock/seed adapter output; "
                "provide the real separated subagent JSON output instead"
            )
    payload.setdefault("adapter_metadata", {})
    payload["adapter_metadata"].update(
        {
            "adapter_kind": "manual-controller",
            "adapter_mode": "manual-controller",
            "real_subagent_execution": True,
            "manual_controller_execution": True,
            "created_at": utc_now(),
            "mock_or_seed_source": False,
            "note": (
                "Role output was produced by an explicit Manual Controller MVP run "
                "using separated subagents or separated role passes, then backfilled "
                "through execute_subagent_plan.py."
            ),
        }
    )


def backfill_outputs(
    run_dir: Path,
    plan: dict[str, Any],
    backfills: dict[str, Path],
    manual_controller_execution: bool = False,
) -> list[dict[str, Any]]:
    queue_by_agent = {item["target_agent"]: item for item in plan["dispatch_queue"]}
    events = []
    for agent, source_path in backfills.items():
        if agent not in queue_by_agent:
            raise ExecutionError(f"backfill target `{agent}` is not in the dispatch queue")
        if not source_path.is_file():
            raise ExecutionError(f"backfill output not found: {source_path}")
        payload = load_json(source_path)
        packet = validate_role_output(payload)
        if packet["target_agent"] != agent:
            raise ExecutionError(
                f"backfill output target_agent `{packet['target_agent']}` does not match `{agent}`"
            )
        if manual_controller_execution:
            attach_manual_controller_metadata(payload)
        target = run_dir / queue_by_agent[agent]["output_artifact_target"]
        target.parent.mkdir(parents=True, exist_ok=True)
        if manual_controller_execution:
            write_json(target, payload)
        else:
            shutil.copyfile(source_path, target)
        events.append(
            {
                "execution_event": {
                    "event_id": f"{plan['run_id']}-{agent}-backfill",
                    "run_id": plan["run_id"],
                    "stage": "merge_pending",
                    "agent_id": agent,
                    "event_type": "receive_output",
                    "input_refs": [str(source_path)],
                    "output_refs": [rel(target, run_dir)],
                    "status": packet["status"],
                    "timestamp_or_sequence": utc_now(),
                    "redaction_applied": True,
                    "execution_mode": "manual-controller" if manual_controller_execution else "backfill",
                }
            }
        )
    return events


def execute(args: argparse.Namespace) -> dict[str, Any]:
    run_dir = args.run_dir
    plan = load_plan(run_dir, args.plan_ref)
    validate_plan_only(plan)
    enforce_execution_gates(args)

    mode = "execute" if args.execute else "dry_run"
    status = "blocked" if args.execute else "dry_run"
    events = build_events(plan["run_id"], plan, mode, status)

    backfills = parse_backfill_args(args.backfill_output)
    if backfills:
        events.extend(backfill_outputs(run_dir, plan, backfills, args.manual_controller_execution))

    event_log_path = run_dir / "logs" / "subagent_execution_events.jsonl"
    append_jsonl(event_log_path, events)

    return {
        "executor_response": {
            "exit_status": "dry_run" if not args.execute else "blocked",
            "run_id": plan["run_id"],
            "dispatch_count": len(plan["dispatch_queue"]),
            "backfilled_outputs": sorted(backfills),
            "execution_events_ref": rel(event_log_path, run_dir),
            "real_subagent_execution": bool(args.manual_controller_execution and backfills),
            "execution_mode": "manual-controller" if args.manual_controller_execution else mode,
            "next_action": "configure_real_adapter" if args.execute else "review_plan_or_backfill_outputs",
        }
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Inspect or safely execute a career-pipeline subagent plan."
    )
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--plan-ref", default="invocations/subagent_invocation_plan.json")
    parser.add_argument("--execute", action="store_true", help="Request real execution through an adapter")
    parser.add_argument("--dry-run", action="store_true", help="Explicitly keep plan inspection mode")
    parser.add_argument("--human-approved", action="store_true")
    parser.add_argument("--allow-network", action="store_true")
    parser.add_argument("--source-policy-ack", action="store_true")
    parser.add_argument("--source-plan-ref", default="evidence/public_source_research_plan.json")
    parser.add_argument("--adapter", default="", help="Reserved name/path for a future real subagent adapter")
    parser.add_argument(
        "--manual-controller-execution",
        action="store_true",
        help=(
            "Mark backfilled role outputs as produced by an explicit Manual Controller MVP "
            "run with separated subagents or separated role passes."
        ),
    )
    parser.add_argument(
        "--backfill-output",
        action="append",
        default=[],
        help="Copy an externally produced role output into the run: target-agent=path",
    )
    args = parser.parse_args(argv)
    try:
        response = execute(args)
        print(json.dumps(response, ensure_ascii=False, indent=2))
        return 0
    except (OSError, json.JSONDecodeError, KeyError, ExecutionError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
