#!/usr/bin/env python
import argparse
import json
import sys
from pathlib import Path
from typing import Any


class PromptBundleError(Exception):
    pass


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def unwrap(payload: dict[str, Any], key: str, path: Path) -> dict[str, Any]:
    value = payload.get(key)
    if not isinstance(value, dict):
        raise PromptBundleError(f"{path}: missing `{key}` object")
    return value


def read_repo_text(ref: str) -> str:
    path = repo_root() / ref
    if not path.is_file():
        raise PromptBundleError(f"repository ref not found: {ref}")
    return path.read_text(encoding="utf-8")


def unique_fields(fields: list[str]) -> list[str]:
    result: list[str] = []
    for field in fields:
        if field not in result:
            result.append(field)
    return result


def build_prompt_bundle(run_dir: Path, invocation_ref: str, output_ref: str | None = None) -> dict[str, Any]:
    invocation_path = run_dir / invocation_ref
    invocation_payload = load_json(invocation_path)
    invocation = unwrap(invocation_payload, "subagent_invocation", invocation_path)

    context_ref = invocation["runtime_context_packet_ref"]
    injection_ref = invocation["secondary_prompt_injection_ref"]
    allowed_user_facts_ref = invocation["allowed_user_facts_ref"]
    input_packet_ref = invocation["input_packet_ref"]
    target_agent = invocation["target_agent"]

    context_path = run_dir / context_ref
    injection_path = run_dir / injection_ref
    allowed_facts_path = run_dir / allowed_user_facts_ref
    input_packet_path = run_dir / input_packet_ref

    context = unwrap(load_json(context_path), "runtime_context_packet", context_path)
    injection = unwrap(load_json(injection_path), "secondary_prompt_injection", injection_path)
    allowed_facts = load_json(allowed_facts_path)
    input_packet = load_json(input_packet_path)

    if any(ref.replace("\\", "/").startswith("input/raw_refs") for ref in [context_ref, input_packet_ref, allowed_user_facts_ref]):
        raise PromptBundleError("prompt bundle must not include raw input refs")

    required_output_fields = unique_fields(
        list(invocation.get("required_output_fields", []))
        + list(injection.get("required_output_fields", []))
        + ["role_output_packet", "error_recovery_state"]
    )
    source_policy_refs = invocation.get("source_policy_refs") or injection.get("source_policy_refs") or []
    source_policy_sections = [
        {
            "ref": ref,
            "content": read_repo_text(ref),
        }
        for ref in source_policy_refs
    ]

    bundle_ref = output_ref or f"prompts/{target_agent}.prompt_bundle.json"
    bundle_path = run_dir / bundle_ref
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
                "runtime_context_packet": {
                    "ref": context_ref,
                    "content": context,
                },
                "allowed_user_facts": {
                    "ref": allowed_user_facts_ref,
                    "content": allowed_facts,
                },
                "secondary_prompt_injection": {
                    "ref": injection_ref,
                    "content": injection,
                },
                "input_packet": {
                    "ref": input_packet_ref,
                    "content": input_packet,
                },
                "database_refs": invocation.get("database_files_to_read", []),
                "source_policy": source_policy_sections,
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
        raise PromptBundleError("prompt bundle contains raw input refs")
    write_json(bundle_path, bundle)
    return {
        "prompt_bundle_response": {
            "exit_status": "success",
            "run_id": invocation["run_id"],
            "target_agent": target_agent,
            "prompt_bundle_ref": rel(bundle_path, run_dir),
        }
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a concrete prompt bundle for one runtime subagent invocation.")
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--invocation-ref", required=True)
    parser.add_argument("--output", default="")
    args = parser.parse_args(argv)
    try:
        response = build_prompt_bundle(args.run_dir, args.invocation_ref, args.output or None)
        print(json.dumps(response, ensure_ascii=False, indent=2))
        return 0
    except (OSError, json.JSONDecodeError, KeyError, PromptBundleError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
