#!/usr/bin/env python
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SUCCESS_ROLE_OUTPUT_STATUSES = {"done", "done_with_warnings"}


class FinalizerError(Exception):
    pass


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


def load_manifest(run_dir: Path) -> dict[str, Any]:
    payload = load_json(run_dir / "manifest.json")
    if not isinstance(payload.get("execution_manifest"), dict) or not isinstance(payload.get("run_state"), dict):
        raise FinalizerError("manifest.json must contain execution_manifest and run_state")
    return payload


def load_plan(run_dir: Path, plan_ref: str) -> dict[str, Any]:
    payload = load_json(run_dir / plan_ref)
    plan = payload.get("subagent_invocation_plan")
    if not isinstance(plan, dict):
        raise FinalizerError(f"{plan_ref}: missing subagent_invocation_plan")
    queue = plan.get("dispatch_queue")
    if not isinstance(queue, list) or not queue:
        raise FinalizerError(f"{plan_ref}: dispatch_queue must be non-empty")
    return plan


def load_role_output(run_dir: Path, output_ref: str) -> dict[str, Any]:
    path = run_dir / output_ref
    if not path.is_file():
        raise FinalizerError(f"missing role output: {output_ref}")
    payload = load_json(path)
    packet = payload.get("role_output_packet")
    if not isinstance(packet, dict):
        raise FinalizerError(f"{output_ref}: missing role_output_packet")
    return payload


def validate_final_role_output(payload: dict[str, Any], target_agent: str, real_subagent_execution_required: bool) -> None:
    packet = payload["role_output_packet"]
    if packet.get("target_agent") != target_agent:
        raise FinalizerError(f"{target_agent}: role output target_agent mismatch")
    status = packet.get("status")
    if status not in SUCCESS_ROLE_OUTPUT_STATUSES:
        raise FinalizerError(f"{target_agent}: role output status `{status}` blocks final package")
    recovery = payload.get("error_recovery_state")
    if not isinstance(recovery, dict):
        raise FinalizerError(f"{target_agent}: missing error_recovery_state")
    if recovery.get("blocked_outputs"):
        raise FinalizerError(f"{target_agent}: blocked_outputs must be empty before final package")
    metadata = payload.get("adapter_metadata")
    if real_subagent_execution_required:
        if not isinstance(metadata, dict) or metadata.get("real_subagent_execution") is not True:
            raise FinalizerError(f"{target_agent}: real adapter metadata is required before final package")
        if metadata.get("adapter_mode") == "mock-blocked" or metadata.get("mock_or_seed_source") is True:
            raise FinalizerError(f"{target_agent}: mock outputs cannot be finalized")


def evidence_refs_from_manifest(manifest_payload: dict[str, Any]) -> list[str]:
    refs = manifest_payload["execution_manifest"].get("evidence_packet_refs")
    return refs if isinstance(refs, list) else []


def validate_source_discovery(run_dir: Path, search_results_ref: str, allowed_sources_ref: str) -> tuple[bool, list[str]]:
    search_path = run_dir / search_results_ref
    allowed_path = run_dir / allowed_sources_ref
    if not search_path.is_file():
        raise FinalizerError(f"missing search results: {search_results_ref}")
    if not allowed_path.is_file():
        raise FinalizerError(f"missing allowed public sources: {allowed_sources_ref}")
    search_payload = load_json(search_path)
    metadata = search_payload.get("metadata", {})
    if metadata.get("provider") == "seed" or metadata.get("real_time_search") is not True:
        raise FinalizerError("final package requires non-seed real-time public source search metadata")
    allowed_payload = load_json(allowed_path)
    sources = allowed_payload.get("sources")
    if not isinstance(sources, list) or not sources:
        raise FinalizerError("final package requires at least one source-policy-accepted public source")
    return True, [allowed_sources_ref]


def update_manifest_for_final(
    run_dir: Path,
    manifest_payload: dict[str, Any],
    final_ref: str,
    role_output_refs: list[str],
    real_subagent_execution: bool,
) -> None:
    manifest = manifest_payload["execution_manifest"]
    run_state = manifest_payload["run_state"]
    manifest["updated_at"] = utc_now()
    manifest["current_stage"] = "final_package_ready"
    manifest["final_package_ref"] = final_ref
    manifest["artifact_refs"] = manifest.get("artifact_refs", [])
    manifest["gate_status"] = {
        "input_normalized": True,
        "context_packet_created": True,
        "secondary_injections_created": True,
        "specialists_completed_or_blocked": True,
        "required_specialists_completed": True,
        "blocked_specialists_absent_for_final": True,
        "debate_completed_or_recorded": True,
        "hr_review_completed": True,
        "factual_review_completed_when_needed": True,
        "user_confirmation_resolved_when_needed": True,
    }
    run_state["stage"] = "final_package_ready"
    run_state["completed_agents"] = [
        ref.split("/")[-2] if "/" in ref else ref for ref in role_output_refs
    ]
    run_state["blocked_agents"] = []
    run_state["failed_invocations"] = []
    run_state["blocked_outputs"] = []
    run_state["degraded_outputs"] = []
    run_state["recovery_actions"] = []
    run_state["next_action"] = "return_final_package"
    run_state["shared_context_refs"] = list(dict.fromkeys(run_state.get("shared_context_refs", []) + role_output_refs))
    run_state["real_subagent_execution"] = real_subagent_execution
    write_json(run_dir / "manifest.json", manifest_payload)


def finalize(args: argparse.Namespace) -> dict[str, Any]:
    run_dir = args.run_dir
    plan = load_plan(run_dir, args.plan_ref)
    manifest_payload = load_manifest(run_dir)
    source_discovery_ready, source_gate_refs = validate_source_discovery(
        run_dir,
        args.search_results_ref,
        args.allowed_sources_ref,
    )
    role_output_refs = []
    role_packets = []
    for item in plan["dispatch_queue"]:
        output_ref = item["output_artifact_target"]
        payload = load_role_output(run_dir, output_ref)
        validate_final_role_output(payload, item["target_agent"], args.real_subagent_execution)
        role_output_refs.append(output_ref)
        role_packets.append(payload["role_output_packet"])
    final_ref = args.output
    final_path = run_dir / final_ref
    decision_package = {
        "decision_package": {
            "run_id": plan["run_id"],
            "created_at": utc_now(),
            "task_type": manifest_payload["execution_manifest"].get("task_type", ""),
            "real_subagent_execution": args.real_subagent_execution,
            "source_discovery_ready": source_discovery_ready,
            "finalizer_validation_status": "passed",
            "role_output_refs": role_output_refs,
            "role_output_statuses": [
                {
                    "target_agent": packet["target_agent"],
                    "status": packet["status"],
                    "confidence": packet["confidence"],
                }
                for packet in role_packets
            ],
            "evidence_packet_refs": evidence_refs_from_manifest(manifest_payload),
            "runtime_weights_ref": manifest_payload["execution_manifest"].get(
                "runtime_weights_ref",
                "merge/runtime_weights.json",
            ),
            "gate_evidence_refs": role_output_refs + source_gate_refs,
            "blocked_outputs": [],
            "degraded_outputs": [],
            "decision_summary": (
                "All required role outputs passed runtime schema/status checks. "
                "This package records final readiness for the local run; role-specific "
                "career text remains evidence-bound to the accepted role outputs."
            ),
        }
    }
    write_json(final_path, decision_package)
    update_manifest_for_final(
        run_dir,
        manifest_payload,
        final_ref,
        role_output_refs,
        args.real_subagent_execution,
    )
    return {
        "finalizer_response": {
            "exit_status": "success",
            "run_id": plan["run_id"],
            "final_package_ref": rel(final_path, run_dir),
            "role_output_refs": role_output_refs,
            "real_subagent_execution": args.real_subagent_execution,
            "source_discovery_ready": source_discovery_ready,
        }
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Finalize a career-pipeline run after role outputs are complete.")
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--plan-ref", default="invocations/subagent_invocation_plan.json")
    parser.add_argument("--output", default="final/decision_package.json")
    parser.add_argument("--real-subagent-execution", action="store_true")
    parser.add_argument("--search-results-ref", default="evidence/search_results.generated.json")
    parser.add_argument("--allowed-sources-ref", default="evidence/allowed_public_sources.generated.json")
    args = parser.parse_args(argv)
    try:
        print(json.dumps(finalize(args), ensure_ascii=False, indent=2))
        return 0
    except (OSError, json.JSONDecodeError, KeyError, FinalizerError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
