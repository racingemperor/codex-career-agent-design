#!/usr/bin/env python
import argparse
import json
import sys
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def read_invocation(run_dir: Path, invocation_ref: str) -> dict[str, Any]:
    payload = load_json(run_dir / invocation_ref)
    invocation = payload.get("subagent_invocation")
    if not isinstance(invocation, dict):
        raise ValueError(f"{invocation_ref}: missing subagent_invocation")
    return invocation


def repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def read_repo_text(ref: str) -> str:
    path = repo_root() / ref
    if not path.is_file():
        raise ValueError(f"repository ref not found: {ref}")
    return path.read_text(encoding="utf-8")


def unwrap(payload: dict[str, Any], key: str, ref: str) -> dict[str, Any]:
    value = payload.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{ref}: missing {key}")
    return value


def unique_fields(fields: list[str]) -> list[str]:
    result: list[str] = []
    for field in fields:
        if field not in result:
            result.append(field)
    return result


BATCH_ORDER = [
    "profile_and_taxonomy",
    "public_role_research",
    "strategy_match",
    "strategy_learning",
    "branding_and_resume",
    "hr_and_factual_gates",
]

BATCH_DEFINITIONS = {
    "profile_and_taxonomy": {
        "description": "Normalize the candidate's discipline, major cluster, and user-owned profile facts.",
        "depends_on_batches": [],
    },
    "public_role_research": {
        "description": "Collect current JD, company, market, HR, and public-source evidence.",
        "depends_on_batches": ["profile_and_taxonomy"],
    },
    "strategy_match": {
        "description": "Merge user profile and public role evidence into fit, gap, and conditional application strategy.",
        "depends_on_batches": ["profile_and_taxonomy", "public_role_research"],
    },
    "strategy_learning": {
        "description": "Turn matched gaps into learning, proof-artifact, and resume-conversion plans.",
        "depends_on_batches": ["strategy_match"],
    },
    "branding_and_resume": {
        "description": "Prepare personal branding, resume format, and resume drafting artifacts.",
        "depends_on_batches": ["profile_and_taxonomy", "strategy_learning"],
    },
    "hr_and_factual_gates": {
        "description": "Run HR readability, factual, privacy, and final presentation gates.",
        "depends_on_batches": ["strategy_learning", "branding_and_resume"],
    },
}

AGENT_BATCH = {
    "major-cluster-classifier": "profile_and_taxonomy",
    "profile-extractor": "profile_and_taxonomy",
    "jd-analyzer": "public_role_research",
    "job-scout": "public_role_research",
    "company-intelligence-analyst": "public_role_research",
    "market-sentiment-analyzer": "public_role_research",
    "match-strategist": "strategy_match",
    "learning-path-strategist": "strategy_learning",
    "personal-branding-strategist": "branding_and_resume",
    "resume-format-gate": "branding_and_resume",
    "resume-architect": "branding_and_resume",
    "hr-supervisor": "hr_and_factual_gates",
    "factual-reviewer": "hr_and_factual_gates",
}

AGENT_DEPENDENCIES = {
    "match-strategist": [
        "major-cluster-classifier",
        "profile-extractor",
        "jd-analyzer",
        "job-scout",
        "company-intelligence-analyst",
        "market-sentiment-analyzer",
    ],
    "learning-path-strategist": ["match-strategist"],
    "personal-branding-strategist": ["profile-extractor", "match-strategist", "learning-path-strategist"],
    "resume-format-gate": ["profile-extractor"],
    "resume-architect": ["resume-format-gate"],
    "factual-reviewer": [
        "resume-architect",
        "match-strategist",
        "learning-path-strategist",
        "hr-supervisor",
    ],
    "hr-supervisor": [
        "match-strategist",
        "learning-path-strategist",
        "personal-branding-strategist",
        "resume-architect",
        "factual-reviewer",
    ],
}

MAX_PARALLEL_SUBAGENTS = 4


def batch_for_agent(target_agent: str) -> str:
    return AGENT_BATCH.get(target_agent, "strategy_match")


def output_refs_for_batches(queue: list[dict[str, Any]], batch_ids: list[str]) -> list[str]:
    refs = []
    for item in queue:
        if item.get("batch_id") in batch_ids:
            ref = item.get("output_artifact_target")
            if ref and ref not in refs:
                refs.append(ref)
    return refs


def output_refs_for_agents(queue: list[dict[str, Any]], target_agents: list[str]) -> list[str]:
    refs = []
    targets = set(target_agents)
    for item in queue:
        if item.get("target_agent") in targets:
            ref = item.get("output_artifact_target")
            if ref and ref not in refs:
                refs.append(ref)
    return refs


def dependency_batches_for_agent(
    target_agent: str,
    available_dependency_agents: set[str],
    present_batches: set[str],
) -> list[str]:
    batch_id = batch_for_agent(target_agent)
    candidate_batches = list(BATCH_DEFINITIONS[batch_id]["depends_on_batches"])
    for dependency_agent in AGENT_DEPENDENCIES.get(target_agent, []):
        if dependency_agent in available_dependency_agents:
            dependency_batch = batch_for_agent(dependency_agent)
            if dependency_batch != batch_id and dependency_batch not in candidate_batches:
                candidate_batches.append(dependency_batch)
    return [batch for batch in BATCH_ORDER if batch in candidate_batches and batch in present_batches]


def build_dispatch_batches(queue: list[dict[str, Any]]) -> list[dict[str, Any]]:
    batches = []
    for batch_id in BATCH_ORDER:
        items = [item for item in queue if item.get("batch_id") == batch_id]
        if not items:
            continue
        definition = BATCH_DEFINITIONS[batch_id]
        depends_on_batches = [
            dep for dep in definition["depends_on_batches"] if any(item.get("batch_id") == dep for item in queue)
        ]
        batches.append(
            {
                "batch_id": batch_id,
                "batch_index": len(batches),
                "target_agents": [item["target_agent"] for item in items],
                "depends_on_batches": depends_on_batches,
                "depends_on_artifact_refs": output_refs_for_batches(queue, depends_on_batches),
                "produces_artifact_refs": [item["output_artifact_target"] for item in items],
                "max_parallel_subagents": min(MAX_PARALLEL_SUBAGENTS, len(items)),
                "close_completed_subagents": True,
                "artifact_handoff_required": True,
                "description": definition["description"],
            }
        )
    return batches


def build_prompt_bundle(run_dir: Path, invocation_ref: str, invocation: dict[str, Any]) -> str:
    context_ref = invocation["runtime_context_packet_ref"]
    injection_ref = invocation["secondary_prompt_injection_ref"]
    allowed_user_facts_ref = invocation["allowed_user_facts_ref"]
    input_packet_ref = invocation["input_packet_ref"]
    target_agent = invocation["target_agent"]

    refs_to_check = [context_ref, input_packet_ref, allowed_user_facts_ref]
    if any(ref.replace("\\", "/").startswith("input/raw_refs") for ref in refs_to_check):
        raise ValueError("prompt bundle must not include raw input refs")

    context = unwrap(load_json(run_dir / context_ref), "runtime_context_packet", context_ref)
    injection = unwrap(load_json(run_dir / injection_ref), "secondary_prompt_injection", injection_ref)
    allowed_facts = load_json(run_dir / allowed_user_facts_ref)
    input_packet = load_json(run_dir / input_packet_ref)
    source_policy_refs = invocation.get("source_policy_refs") or injection.get("source_policy_refs") or []
    required_output_fields = unique_fields(
        list(invocation.get("required_output_fields", []))
        + list(injection.get("required_output_fields", []))
        + ["role_output_packet", "error_recovery_state"]
    )
    bundle_ref = f"prompts/{target_agent}.prompt_bundle.json"
    bundle = {
        "subagent_prompt_bundle": {
            "bundle_id": f"{invocation['invocation_id']}-prompt-bundle",
            "run_id": invocation["run_id"],
            "target_agent": target_agent,
            "invocation_ref": invocation_ref,
            "base_prompt_ref": invocation["base_prompt_ref"],
            "runtime_context_packet_ref": context_ref,
            "secondary_prompt_injection_ref": injection_ref,
            "input_packet_ref": input_packet_ref,
            "allowed_user_facts_ref": allowed_user_facts_ref,
            "output_artifact_target": invocation["output_artifact_target"],
            "privacy_class": "derived",
            "raw_input_excluded": True,
            "prompt_composition_order": [
                "static_role_prompt",
                "runtime_context_packet",
                "allowed_user_facts",
                "secondary_prompt_injection",
                "database_refs",
                "source_policy",
                "research_tasks",
                "hard_data_weight_tasks",
                "required_output_contract",
                "handoff_and_debate_contract",
            ],
            "prompt_sections": {
                "static_role_prompt": {
                    "ref": invocation["base_prompt_ref"],
                    "content": read_repo_text(invocation["base_prompt_ref"]),
                },
                "runtime_context_packet": {"ref": context_ref, "content": context},
                "allowed_user_facts": {"ref": allowed_user_facts_ref, "content": allowed_facts},
                "secondary_prompt_injection": {"ref": injection_ref, "content": injection},
                "input_packet": {"ref": input_packet_ref, "content": input_packet},
                "database_refs": invocation.get("database_files_to_read", []),
                "source_policy": [
                    {"ref": ref, "content": read_repo_text(ref)} for ref in source_policy_refs
                ],
                "research_tasks": invocation.get("research_tasks", []),
                "hard_data_weight_tasks": invocation.get("hard_data_weight_tasks", []),
                "required_output_contract": {
                    "required_output_fields": required_output_fields,
                    "role_output_packet_required": True,
                    "error_recovery_state_required": True,
                    "forbidden_when_failed_or_malformed": [
                        "fit_score",
                        "priority",
                        "application_strategy",
                        "positioning_verdict",
                        "pass_to_next_stage",
                        "final_resume_draft",
                        "current_fit_assessment",
                        "application_readiness_decision",
                        "learning_plan_before_application",
                        "targeted_resume_tailoring",
                        "growth_resume_preview",
                    ],
                },
                "handoff_and_debate_contract": {
                    "handoff_contract": invocation.get("handoff_contract", []),
                    "debate_contract": invocation.get("debate_contract", []),
                },
            },
            "required_output_fields": required_output_fields,
            "database_files_to_read": invocation.get("database_files_to_read", []),
            "source_policy_refs": source_policy_refs,
            "research_tasks": invocation.get("research_tasks", []),
            "hard_data_weight_tasks": invocation.get("hard_data_weight_tasks", []),
            "privacy_constraints": invocation.get("privacy_constraints", []),
        }
    }
    serialized = json.dumps(bundle, ensure_ascii=False)
    if "input/raw_refs.json" in serialized or "input\\raw_refs.json" in serialized:
        raise ValueError("prompt bundle contains raw input refs")
    write_json(run_dir / bundle_ref, bundle)
    return bundle_ref


def build_plan(run_dir: Path, build_prompt_bundles: bool = False) -> dict[str, Any]:
    manifest_payload = load_json(run_dir / "manifest.json")
    manifest = manifest_payload.get("execution_manifest")
    if not isinstance(manifest, dict):
        raise ValueError("manifest.json: missing execution_manifest")

    invocation_refs = manifest.get("subagent_invocation_refs")
    if not isinstance(invocation_refs, list) or not invocation_refs:
        raise ValueError("manifest.json: missing subagent_invocation_refs")

    queue = []
    invocations = [(ref, read_invocation(run_dir, ref)) for ref in invocation_refs]
    present_agents = {invocation["target_agent"] for _, invocation in invocations}
    present_batches = {batch_for_agent(agent) for agent in present_agents}
    for index, (invocation_ref, invocation) in enumerate(invocations):
        input_packet_ref = invocation["input_packet_ref"]
        allowed_user_facts_ref = invocation["allowed_user_facts_ref"]
        context_ref = invocation["runtime_context_packet_ref"]
        prompt_bundle_ref = ""
        if build_prompt_bundles:
            prompt_bundle_ref = build_prompt_bundle(run_dir, invocation_ref, invocation)
        batch_id = batch_for_agent(invocation["target_agent"])
        available_dependency_agents = {item["target_agent"] for item in queue}
        depends_on_batches = dependency_batches_for_agent(
            invocation["target_agent"],
            available_dependency_agents,
            present_batches,
        )
        depends_on_agents = [
            agent
            for agent in AGENT_DEPENDENCIES.get(invocation["target_agent"], [])
            if agent in available_dependency_agents
            and batch_for_agent(agent) != batch_id
        ]
        batch_artifact_refs = output_refs_for_batches(queue, depends_on_batches)
        agent_artifact_refs = output_refs_for_agents(queue, depends_on_agents)
        depends_on_artifact_refs = list(dict.fromkeys(batch_artifact_refs + agent_artifact_refs))
        queue.append(
            {
                "queue_index": index,
                "target_agent": invocation["target_agent"],
                "batch_id": batch_id,
                "depends_on_batches": depends_on_batches,
                "depends_on_agents": depends_on_agents,
                "depends_on_artifact_refs": depends_on_artifact_refs,
                "invocation_ref": invocation_ref,
                "prompt_bundle_ref": prompt_bundle_ref,
                "input_refs": [context_ref, input_packet_ref, allowed_user_facts_ref],
                "output_artifact_target": invocation["output_artifact_target"],
                "close_after_artifact_persisted": True,
                "dispatch_mode": "plan_only",
                "status": "planned",
                "allowed_network": False,
                "requires_human_approval": True,
                "privacy_class": "derived",
                "blocked_until": [
                    "human_confirms_real_subagent_execution",
                    "allowed_network_policy_resolved",
                    "source_policy_loaded",
                ],
            }
        )

    dispatch_batches = build_dispatch_batches(queue)
    return {
        "subagent_invocation_plan": {
            "run_id": manifest["run_id"],
            "plan_status": "ready",
            "created_from_manifest_ref": "manifest.json",
            "dispatch_strategy": "batched_artifact_handoff",
            "max_parallel_subagents": MAX_PARALLEL_SUBAGENTS,
            "artifact_handoff_required": True,
            "close_completed_subagents": True,
            "dispatch_batches": dispatch_batches,
            "dispatch_queue": queue,
            "execution_note": (
                "Plan only: this file is not proof that subagents ran. Dispatch by batch, "
                "persist each role output artifact, then close completed subagents before the next batch."
            ),
        }
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a plan-only subagent dispatch queue for a simulated run.")
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--output", default="invocations/subagent_invocation_plan.json")
    parser.add_argument("--build-prompt-bundles", action="store_true")
    args = parser.parse_args(argv)
    try:
        plan = build_plan(args.run_dir, args.build_prompt_bundles)
        output_path = args.run_dir / args.output
        write_json(output_path, plan)
        print(
            json.dumps(
                {
                    "planner_response": {
                        "exit_status": "success",
                        "run_id": plan["subagent_invocation_plan"]["run_id"],
                        "subagent_plan_ref": rel(output_path, args.run_dir),
                    }
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    except (OSError, json.JSONDecodeError, KeyError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
