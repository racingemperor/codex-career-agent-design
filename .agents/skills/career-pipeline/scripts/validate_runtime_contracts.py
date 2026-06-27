#!/usr/bin/env python
import argparse
import json
import sys
from pathlib import Path
from typing import Any


INJECTION_REQUIRED_FIELDS = [
    "target_agent",
    "base_prompt_ref",
    "runtime_context_packet_ref",
    "role_specific_context",
    "allowed_user_facts",
    "research_tasks",
    "hard_data_weight_tasks",
    "database_files_to_read",
    "source_policy_refs",
    "invocation_contract",
    "required_output_fields",
    "handoff_contract",
    "debate_contract",
]

INVOCATION_REQUIRED_FIELDS = [
    "invocation_id",
    "run_id",
    "target_agent",
    "base_prompt_ref",
    "secondary_prompt_injection_ref",
    "runtime_context_packet_ref",
    "input_packet_ref",
    "allowed_user_facts_ref",
    "output_artifact_target",
    "privacy_constraints",
    "expected_artifact_types",
    "required_log_events",
    "retry_allowed",
    "on_failure",
    "status",
]

LIST_FIELDS = [
    "allowed_user_facts",
    "research_tasks",
    "hard_data_weight_tasks",
    "database_files_to_read",
    "source_policy_refs",
    "required_output_fields",
    "handoff_contract",
    "debate_contract",
]

FINAL_GATE_FIELDS = [
    "input_normalized",
    "context_packet_created",
    "secondary_injections_created",
    "specialists_completed_or_blocked",
    "debate_completed_or_recorded",
    "hr_review_completed",
    "factual_review_completed_when_needed",
    "user_confirmation_resolved_when_needed",
]

ALLOWED_FAILURE_ACTIONS = {
    "return_blocked",
    "rerun_with_more_context",
    "handoff_to_orchestrator",
}

ALLOWED_INVOCATION_STATUSES = {
    "not_started",
    "running",
    "done",
    "blocked",
    "failed",
    "malformed",
}

PLAN_QUEUE_REQUIRED_FIELDS = [
    "queue_index",
    "target_agent",
    "batch_id",
    "depends_on_batches",
    "depends_on_agents",
    "depends_on_artifact_refs",
    "invocation_ref",
    "input_refs",
    "output_artifact_target",
    "close_after_artifact_persisted",
    "dispatch_mode",
    "status",
    "allowed_network",
    "requires_human_approval",
    "privacy_class",
    "blocked_until",
]

SOURCE_PLAN_REQUIRED_FIELDS = [
    "run_id",
    "policy_ref",
    "network_execution_default",
    "research_tasks",
    "blocked_source_types",
]

SOURCE_TASK_REQUIRED_FIELDS = [
    "task_id",
    "agent",
    "claim_field",
    "source_type",
    "source_priority",
    "allowed",
    "requires_login",
    "may_set_weight",
    "may_set_final_decision",
    "evidence_strength_floor",
    "privacy_action",
    "query_template",
    "output_fields",
]

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

ROLE_OUTPUT_FAILURE_STATUSES = {"failed", "malformed"}

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

ERROR_RECOVERY_REQUIRED_FIELDS = [
    "status",
    "errors",
    "recovery_actions",
    "degraded_outputs",
    "blocked_outputs",
    "safe_outputs",
    "next_action",
]


class ValidationError(Exception):
    pass


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def require_non_empty(value: Any, field: str, where: str) -> None:
    if value in ("", None, [], {}):
        raise ValidationError(f"{where}: required field `{field}` is empty")


def require_list(value: Any, field: str, where: str) -> None:
    if not isinstance(value, list):
        raise ValidationError(f"{where}: `{field}` must be a list")


def get_injections(payload: dict[str, Any]) -> list[dict[str, Any]]:
    injections = payload.get("secondary_prompt_injections")
    if injections is None and "secondary_prompt_injection" in payload:
        injections = [payload["secondary_prompt_injection"]]
    if not isinstance(injections, list) or not injections:
        raise ValidationError("root: `secondary_prompt_injections` must be a non-empty list")
    return injections


def validate_injection(injection: dict[str, Any], index: int) -> None:
    where = f"secondary_prompt_injections[{index}]"
    for field in INJECTION_REQUIRED_FIELDS:
        if field not in injection:
            raise ValidationError(f"{where}: missing required field `{field}`")
        require_non_empty(injection[field], field, where)

    for field in LIST_FIELDS:
        require_list(injection[field], field, where)
        require_non_empty(injection[field], field, where)

    if not isinstance(injection["role_specific_context"], dict):
        raise ValidationError(f"{where}: `role_specific_context` must be an object")

    target_agent = injection["target_agent"]
    expected_base = f".codex/agents/{target_agent}.toml"
    if injection["base_prompt_ref"] != expected_base:
        raise ValidationError(
            f"{where}: `base_prompt_ref` must be `{expected_base}` for target `{target_agent}`"
        )

    contract = injection["invocation_contract"]
    if not isinstance(contract, dict):
        raise ValidationError(f"{where}: `invocation_contract` must be an object")
    validate_invocation_contract(injection, contract, where)


def validate_invocation_contract(
    injection: dict[str, Any],
    contract: dict[str, Any],
    where: str,
) -> None:
    for field in INVOCATION_REQUIRED_FIELDS:
        if field not in contract:
            raise ValidationError(f"{where}.invocation_contract: missing required field `{field}`")
        require_non_empty(contract[field], field, f"{where}.invocation_contract")

    for field in [
        "database_files_to_read",
        "source_policy_refs",
        "research_tasks",
        "hard_data_weight_tasks",
        "required_output_fields",
        "privacy_constraints",
        "handoff_contract",
        "debate_contract",
        "expected_artifact_types",
        "required_log_events",
    ]:
        if field in contract:
            require_list(contract[field], field, f"{where}.invocation_contract")

    for field in ["target_agent", "base_prompt_ref", "runtime_context_packet_ref"]:
        if contract[field] != injection[field]:
            raise ValidationError(
                f"{where}.invocation_contract: `{field}` must match secondary injection"
            )

    if contract["on_failure"] not in ALLOWED_FAILURE_ACTIONS:
        raise ValidationError(
            f"{where}.invocation_contract: `on_failure` must be one of {sorted(ALLOWED_FAILURE_ACTIONS)}"
        )
    if contract["status"] not in ALLOWED_INVOCATION_STATUSES:
        raise ValidationError(
            f"{where}.invocation_contract: `status` must be one of {sorted(ALLOWED_INVOCATION_STATUSES)}"
        )


def canonical_invocation(injection: dict[str, Any]) -> dict[str, Any]:
    contract = dict(injection["invocation_contract"])
    for field in [
        "database_files_to_read",
        "source_policy_refs",
        "research_tasks",
        "hard_data_weight_tasks",
        "required_output_fields",
        "privacy_constraints",
        "handoff_contract",
        "debate_contract",
    ]:
        contract[field] = contract.get(field) or injection[field]
    contract.setdefault("timeout_or_budget_hint", "")
    contract.setdefault("retry_allowed", True)
    contract.setdefault("status", "not_started")
    return {"subagent_invocation": contract}


def build_invocations(payload: dict[str, Any]) -> list[dict[str, Any]]:
    injections = get_injections(payload)
    for index, injection in enumerate(injections):
        validate_injection(injection, index)
    return [canonical_invocation(injection) for injection in injections]


def validate_injections(payload: dict[str, Any]) -> None:
    build_invocations(payload)


def validate_manifest(payload: dict[str, Any]) -> None:
    manifest = payload.get("execution_manifest")
    run_state = payload.get("run_state")
    if not isinstance(manifest, dict):
        raise ValidationError("root: missing `execution_manifest` object")
    if not isinstance(run_state, dict):
        raise ValidationError("root: missing `run_state` object")

    current_stage = manifest.get("current_stage")
    run_stage = run_state.get("stage")
    require_non_empty(current_stage, "current_stage", "execution_manifest")
    require_non_empty(run_stage, "stage", "run_state")
    if current_stage != run_stage:
        raise ValidationError(
            "execution_manifest.current_stage must equal run_state.stage before dispatch continues"
        )

    for field in [
        "runtime_context_packet_ref",
        "secondary_prompt_injection_refs",
        "subagent_invocation_refs",
    ]:
        manifest_value = manifest.get(field)
        run_state_value = run_state.get(field)
        if manifest_value != run_state_value:
            raise ValidationError(f"`{field}` must match between execution_manifest and run_state")

    if current_stage == "final_package_ready":
        gate_status = manifest.get("gate_status")
        if not isinstance(gate_status, dict):
            raise ValidationError(
                "execution_manifest: `gate_status` is required for final_package_ready"
            )
        missing_or_false = [
            field for field in FINAL_GATE_FIELDS if gate_status.get(field) is not True
        ]
        if missing_or_false:
            names = ", ".join(missing_or_false)
            raise ValidationError(
                f"final_package_ready is invalid while required gates are blocked or false: {names}"
            )
        require_non_empty(
            manifest.get("final_package_ref"),
            "final_package_ref",
            "execution_manifest",
        )
        for field in [
            "runtime_context_packet_ref",
            "secondary_prompt_injection_refs",
            "subagent_invocation_refs",
        ]:
            require_non_empty(manifest.get(field), field, "execution_manifest")

    if current_stage == "blocked" and manifest.get("final_package_ref"):
        raise ValidationError("blocked runs must not set `final_package_ref`")


def validate_subagent_plan(payload: dict[str, Any]) -> None:
    plan = payload.get("subagent_invocation_plan")
    if not isinstance(plan, dict):
        raise ValidationError("root: missing `subagent_invocation_plan` object")
    require_non_empty(plan.get("run_id"), "run_id", "subagent_invocation_plan")
    if plan.get("plan_status") != "ready":
        raise ValidationError("subagent_invocation_plan: `plan_status` must be `ready`")
    if plan.get("dispatch_strategy") != "batched_artifact_handoff":
        raise ValidationError("subagent_invocation_plan: dispatch_strategy must be batched_artifact_handoff")
    if plan.get("max_parallel_subagents") not in {1, 2, 3, 4}:
        raise ValidationError("subagent_invocation_plan: max_parallel_subagents must be between 1 and 4")
    if plan.get("artifact_handoff_required") is not True:
        raise ValidationError("subagent_invocation_plan: artifact_handoff_required must be true")
    if plan.get("close_completed_subagents") is not True:
        raise ValidationError("subagent_invocation_plan: close_completed_subagents must be true")
    batches = plan.get("dispatch_batches")
    if not isinstance(batches, list) or not batches:
        raise ValidationError("subagent_invocation_plan: dispatch_batches must be a non-empty list")
    batch_ids = []
    for index, batch in enumerate(batches):
        where = f"dispatch_batches[{index}]"
        if not isinstance(batch, dict):
            raise ValidationError(f"{where}: batch must be an object")
        for field in [
            "batch_id",
            "batch_index",
            "target_agents",
            "depends_on_batches",
            "depends_on_artifact_refs",
            "produces_artifact_refs",
            "max_parallel_subagents",
            "close_completed_subagents",
            "artifact_handoff_required",
        ]:
            if field not in batch:
                raise ValidationError(f"{where}: missing required field `{field}`")
        if batch["batch_index"] != index:
            raise ValidationError(f"{where}: batch_index must match list order")
        require_non_empty(batch["batch_id"], "batch_id", where)
        if batch["batch_id"] in batch_ids:
            raise ValidationError(f"{where}: duplicate batch_id `{batch['batch_id']}`")
        batch_ids.append(batch["batch_id"])
        require_list(batch["target_agents"], "target_agents", where)
        require_list(batch["depends_on_batches"], "depends_on_batches", where)
        require_list(batch["depends_on_artifact_refs"], "depends_on_artifact_refs", where)
        require_list(batch["produces_artifact_refs"], "produces_artifact_refs", where)
        if batch["max_parallel_subagents"] not in {1, 2, 3, 4}:
            raise ValidationError(f"{where}: max_parallel_subagents must be between 1 and 4")
        if batch["close_completed_subagents"] is not True:
            raise ValidationError(f"{where}: close_completed_subagents must be true")
        if batch["artifact_handoff_required"] is not True:
            raise ValidationError(f"{where}: artifact_handoff_required must be true")
    queue = plan.get("dispatch_queue")
    if not isinstance(queue, list) or not queue:
        raise ValidationError("subagent_invocation_plan: `dispatch_queue` must be a non-empty list")

    for index, item in enumerate(queue):
        where = f"dispatch_queue[{index}]"
        if not isinstance(item, dict):
            raise ValidationError(f"{where}: queue item must be an object")
        for field in PLAN_QUEUE_REQUIRED_FIELDS:
            if field not in item:
                raise ValidationError(f"{where}: missing required field `{field}`")
            if field not in {
                "depends_on_batches",
                "depends_on_agents",
                "depends_on_artifact_refs",
                "close_after_artifact_persisted",
            }:
                require_non_empty(item[field], field, where)
        if "prompt_bundle_ref" in item and item["prompt_bundle_ref"]:
            if item["prompt_bundle_ref"].replace("\\", "/").startswith("input/raw_refs"):
                raise ValidationError(f"{where}: prompt_bundle_ref must not expose raw input")
        if item["queue_index"] != index:
            raise ValidationError(f"{where}: `queue_index` must match list order")
        if item["dispatch_mode"] != "plan_only":
            raise ValidationError(f"{where}: `dispatch_mode` must be `plan_only`")
        if item["status"] != "planned":
            raise ValidationError(f"{where}: `status` must be `planned`")
        if item["allowed_network"] is not False:
            raise ValidationError(f"{where}: plan-only dispatch must set `allowed_network` to false")
        if item["requires_human_approval"] is not True:
            raise ValidationError(f"{where}: plan-only dispatch must require human approval")
        if item["batch_id"] not in batch_ids:
            raise ValidationError(f"{where}: batch_id must reference dispatch_batches")
        if item["close_after_artifact_persisted"] is not True:
            raise ValidationError(f"{where}: close_after_artifact_persisted must be true")
        require_list(item["input_refs"], "input_refs", where)
        require_list(item["blocked_until"], "blocked_until", where)
        require_list(item["depends_on_batches"], "depends_on_batches", where)
        require_list(item["depends_on_agents"], "depends_on_agents", where)
        require_list(item["depends_on_artifact_refs"], "depends_on_artifact_refs", where)
        if any(ref.replace("\\", "/").startswith("input/raw_refs") for ref in item["input_refs"]):
            raise ValidationError(f"{where}: raw input refs must not be exposed to subagent plans")


def validate_source_plan(payload: dict[str, Any]) -> None:
    plan = payload.get("public_source_research_plan")
    if not isinstance(plan, dict):
        raise ValidationError("root: missing `public_source_research_plan` object")
    for field in SOURCE_PLAN_REQUIRED_FIELDS:
        if field not in plan:
            raise ValidationError(f"public_source_research_plan: missing required field `{field}`")
        if field != "blocked_source_types":
            require_non_empty(plan[field], field, "public_source_research_plan")
    if plan["policy_ref"] != ".agents/skills/career-pipeline/references/source-policy.md":
        raise ValidationError("public_source_research_plan: policy_ref must point to source-policy.md")
    if plan["network_execution_default"] != "disabled_until_controller_source_policy_ack":
        raise ValidationError(
            "public_source_research_plan: network execution must be disabled until controller source-policy acknowledgement"
        )
    require_list(plan["research_tasks"], "research_tasks", "public_source_research_plan")
    require_list(plan["blocked_source_types"], "blocked_source_types", "public_source_research_plan")
    errors = []
    for index, task in enumerate(plan["research_tasks"]):
        where = f"public_source_research_plan.research_tasks[{index}]"
        if not isinstance(task, dict):
            raise ValidationError(f"{where}: task must be an object")
        for field in SOURCE_TASK_REQUIRED_FIELDS:
            if field not in task:
                raise ValidationError(f"{where}: missing required field `{field}`")
            require_non_empty(task[field], field, where)
        require_list(task["output_fields"], "output_fields", where)
        source_type = task["source_type"]
        if source_type in FORBIDDEN_SOURCE_TYPES:
            errors.append(f"{where}: forbidden source_type `{source_type}`")
        elif source_type not in ALLOWED_SOURCE_TYPES:
            errors.append(f"{where}: unsupported source_type `{source_type}`")
        if task["requires_login"] is True:
            errors.append(f"{where}: requires_login sources are not allowed")
        if task["allowed"] is not True:
            errors.append(f"{where}: active research tasks must be explicitly allowed")
        if source_type == "social_media_weak" and task["may_set_final_decision"] is True:
            errors.append(f"{where}: social_media_weak cannot be a final decision basis")
        if source_type == "social_media_weak" and task["may_set_weight"] is True:
            errors.append(f"{where}: social_media_weak cannot set weights alone")
        if source_type == "candidate_experience_secondary" and task["may_set_final_decision"] is True:
            errors.append(f"{where}: candidate_experience_secondary cannot be a final decision basis")
    if errors:
        raise ValidationError("; ".join(errors))


def validate_role_output(payload: dict[str, Any]) -> None:
    missing_top_level = [
        field
        for field in ["invocation_ref", "role_output_packet", "error_recovery_state"]
        if field not in payload or payload[field] in ("", None, [], {})
    ]
    if missing_top_level:
        raise ValidationError(
            "role_output: missing required traceability or recovery fields: "
            + ", ".join(missing_top_level)
        )

    packet = payload["role_output_packet"]
    if not isinstance(packet, dict):
        raise ValidationError("role_output.role_output_packet: must be an object")
    for field in ROLE_OUTPUT_PACKET_REQUIRED_FIELDS:
        if field not in packet:
            raise ValidationError(f"role_output_packet: missing required field `{field}`")
        if field in {"invocation_id", "target_agent", "status", "role_output_ref", "confidence"}:
            require_non_empty(packet[field], field, "role_output_packet")
    for field in ROLE_OUTPUT_LIST_FIELDS:
        require_list(packet[field], field, "role_output_packet")
    if packet["status"] not in ALLOWED_ROLE_OUTPUT_STATUSES:
        raise ValidationError(
            "role_output_packet: `status` must be one of "
            + ", ".join(sorted(ALLOWED_ROLE_OUTPUT_STATUSES))
        )

    recovery = payload["error_recovery_state"]
    if not isinstance(recovery, dict):
        raise ValidationError("role_output.error_recovery_state: must be an object")
    for field in ERROR_RECOVERY_REQUIRED_FIELDS:
        if field not in recovery:
            raise ValidationError(f"error_recovery_state: missing required field `{field}`")
        if field in {
            "errors",
            "recovery_actions",
            "degraded_outputs",
            "blocked_outputs",
            "safe_outputs",
        }:
            require_list(recovery[field], field, "error_recovery_state")
        else:
            require_non_empty(recovery[field], field, "error_recovery_state")

    if packet["status"] in ROLE_OUTPUT_FAILURE_STATUSES:
        forbidden = sorted(field for field in FINAL_DECISION_FIELDS if field in payload)
        if forbidden:
            raise ValidationError(
                "failed or malformed role outputs must not include final decision fields: "
                + ", ".join(forbidden)
            )


def validate_repository(root: Path) -> None:
    agents_dir = root / ".codex" / "agents"
    skill_file = root / ".agents" / "skills" / "career-pipeline" / "SKILL.md"
    if not skill_file.is_file():
        raise ValidationError("repository: missing career-pipeline SKILL.md")
    if not agents_dir.is_dir():
        raise ValidationError("repository: missing .codex/agents directory")
    agent_files = sorted(agents_dir.glob("*.toml"))
    if not agent_files:
        raise ValidationError("repository: no role prompt TOML files found")
    for agent_file in agent_files:
        text = agent_file.read_text(encoding="utf-8")
        for needle in [
            "runtime_context_packet_ref",
            "role_output_packet",
            "error_recovery_state",
            "Hard-data weight rule",
        ]:
            if needle not in text:
                raise ValidationError(f"{agent_file}: missing `{needle}`")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate local career-pipeline runtime contracts."
    )
    parser.add_argument("--injections", type=Path, help="JSON file containing secondary_prompt_injections")
    parser.add_argument("--manifest", type=Path, help="JSON file containing execution_manifest and run_state")
    parser.add_argument("--subagent-plan", type=Path, help="JSON file containing subagent_invocation_plan")
    parser.add_argument("--role-output", type=Path, help="JSON file containing a role_output_packet")
    parser.add_argument("--source-plan", type=Path, help="JSON file containing public_source_research_plan")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repository root to validate")
    parser.add_argument("--emit-invocations", action="store_true", help="Emit canonical subagent_invocations")
    args = parser.parse_args(argv)

    try:
        output: dict[str, Any] = {"status": "ok"}
        if args.injections:
            payload = load_json(args.injections)
            invocations = build_invocations(payload)
            if args.emit_invocations:
                output["subagent_invocations"] = invocations
        if args.manifest:
            validate_manifest(load_json(args.manifest))
        if args.subagent_plan:
            validate_subagent_plan(load_json(args.subagent_plan))
        if args.role_output:
            validate_role_output(load_json(args.role_output))
        if args.source_plan:
            validate_source_plan(load_json(args.source_plan))
        if (
            not args.injections
            and not args.manifest
            and not args.subagent_plan
            and not args.role_output
            and not args.source_plan
        ):
            validate_repository(args.repo_root)
        if args.emit_invocations:
            print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
