#!/usr/bin/env python
import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


POLICY_REF = ".agents/skills/career-pipeline/references/source-policy.md"
NETWORK_DEFAULT = "disabled_until_controller_source_policy_ack"
DEFAULT_RECRUITMENT_SOURCE_MATRIX_REF = (
    "data/company_signals/default_recruitment_source_matrix.zh-CN.json"
)


class SourcePlanError(Exception):
    pass


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def unwrap(payload: dict[str, Any], key: str, path: Path) -> dict[str, Any]:
    value = payload.get(key)
    if not isinstance(value, dict):
        raise SourcePlanError(f"{path}: missing `{key}` object")
    return value


def load_context(run_dir: Path) -> dict[str, Any]:
    manifest = unwrap(load_json(run_dir / "manifest.json"), "execution_manifest", run_dir / "manifest.json")
    context_ref = manifest.get("runtime_context_packet_ref")
    if not context_ref:
        raise SourcePlanError("manifest.json: missing runtime_context_packet_ref")
    context_path = run_dir / context_ref
    return unwrap(load_json(context_path), "runtime_context_packet", context_path)


def load_invocations(run_dir: Path) -> list[dict[str, Any]]:
    manifest = unwrap(load_json(run_dir / "manifest.json"), "execution_manifest", run_dir / "manifest.json")
    invocation_refs = manifest.get("subagent_invocation_refs")
    if not isinstance(invocation_refs, list) or not invocation_refs:
        raise SourcePlanError("manifest.json: missing subagent_invocation_refs")
    invocations = []
    for ref in invocation_refs:
        invocation = unwrap(load_json(run_dir / ref), "subagent_invocation", run_dir / ref)
        invocations.append(invocation)
    return invocations


def repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def load_default_source_matrix() -> dict[str, Any]:
    return load_json(repo_root() / DEFAULT_RECRUITMENT_SOURCE_MATRIX_REF)


def source_display_by_type() -> dict[str, list[str]]:
    source_matrix = load_default_source_matrix()
    matrix_groups = source_matrix["default_public_recruitment_source_targets"]
    return {
        group["source_type"]: group["display_sources"]
        for group in matrix_groups
    }


def target_terms(context: dict[str, Any]) -> list[str]:
    terms: list[str] = []
    target = context.get("target_context", {})
    if isinstance(target, dict):
        for field in ["target_roles", "target_companies", "target_industries", "target_locations"]:
            value = target.get(field)
            if isinstance(value, list):
                terms.extend(str(item) for item in value if item)
            elif value:
                terms.append(str(value))
    for fact in context.get("known_user_facts", []):
        if fact.get("field") in {"major_name", "grade_or_year", "skill"}:
            terms.append(str(fact.get("value", "")))
    normalized = []
    for term in terms:
        if term and term not in normalized:
            normalized.append(term)
    return normalized or ["target role", "target company", "candidate major"]


def task(
    task_id: str,
    agent: str,
    claim_field: str,
    source_type: str,
    source_priority: int,
    query_template: str,
    may_set_weight: bool,
    may_set_final_decision: bool,
    evidence_strength_floor: str,
    privacy_action: str,
) -> dict[str, Any]:
    return {
        "task_id": task_id,
        "agent": agent,
        "claim_field": claim_field,
        "source_type": source_type,
        "source_priority": source_priority,
        "allowed": True,
        "requires_login": False,
        "may_set_weight": may_set_weight,
        "may_set_final_decision": may_set_final_decision,
        "evidence_strength_floor": evidence_strength_floor,
        "privacy_action": privacy_action,
        "query_template": query_template,
        "output_fields": [
            "evidence_basis",
            "weight_provenance",
            "source_notes",
            "runtime_research_tasks",
            "blocked_outputs",
        ],
    }


def build_tasks(invocations: list[dict[str, Any]], terms: list[str]) -> list[dict[str, Any]]:
    query = " ".join(terms[:6])
    agents = {invocation["target_agent"] for invocation in invocations}
    default_agent = "job-scout" if "job-scout" in agents else invocations[0]["target_agent"]
    display_sources_by_type = source_display_by_type()
    tasks = [
        task(
            "official-company-career",
            default_agent,
            "current_company_or_job_requirement",
            "official_or_primary",
            1,
            f"{query} official career campus JD",
            True,
            True,
            "strong",
            "cache_metadata_and_short_excerpt",
        )
        | {
            "source_group_id": "official_primary",
            "source_matrix_ref": DEFAULT_RECRUITMENT_SOURCE_MATRIX_REF,
            "user_instruction_required": False,
            "display_sources": display_sources_by_type["official_or_primary"],
        },
        task(
            "recruitment-platform-public-jd",
            default_agent,
            "current_jd_requirement",
            "recruitment_platform_jd",
            3,
            f"{query} public JD BOSS Lagou Liepin Nowcoder LinkedIn Indeed",
            True,
            True,
            "medium",
            "cache_metadata_only",
        )
        | {
            "source_group_id": "public_recruitment_platform",
            "source_matrix_ref": DEFAULT_RECRUITMENT_SOURCE_MATRIX_REF,
            "user_instruction_required": False,
            "display_sources": display_sources_by_type["recruitment_platform_jd"],
        },
        task(
            "verified-hr-public-post",
            "hr-supervisor" if "hr-supervisor" in agents else default_agent,
            "hr_screening_signal",
            "verified_hr_public_post",
            2,
            f"{query} verified HR public campus recruiting screening",
            True,
            False,
            "medium",
            "cache_metadata_and_short_excerpt",
        )
        | {
            "source_group_id": "verified_hr_public",
            "source_matrix_ref": DEFAULT_RECRUITMENT_SOURCE_MATRIX_REF,
            "user_instruction_required": False,
            "display_sources": display_sources_by_type["verified_hr_public_post"],
        },
        task(
            "candidate-experience-secondary",
            "market-sentiment-analyzer" if "market-sentiment-analyzer" in agents else default_agent,
            "interview_or_hidden_expectation",
            "candidate_experience_secondary",
            4,
            f"{query} interview experience offer review public deidentified",
            False,
            False,
            "weak",
            "aggregate_deidentified_only",
        )
        | {
            "source_group_id": "candidate_experience_secondary",
            "source_matrix_ref": DEFAULT_RECRUITMENT_SOURCE_MATRIX_REF,
            "user_instruction_required": False,
            "display_sources": display_sources_by_type["candidate_experience_secondary"],
        },
        task(
            "social-media-weak-signal",
            "market-sentiment-analyzer" if "market-sentiment-analyzer" in agents else default_agent,
            "preparation_or_risk_signal",
            "social_media_weak",
            5,
            f"{query} public social media discussion weak signal",
            False,
            False,
            "weak",
            "aggregate_deidentified_only",
        )
        | {
            "source_group_id": "social_media_weak",
            "source_matrix_ref": DEFAULT_RECRUITMENT_SOURCE_MATRIX_REF,
            "user_instruction_required": False,
            "display_sources": display_sources_by_type["social_media_weak"],
        },
        task(
            "public-company-development-report",
            "company-intelligence-analyst" if "company-intelligence-analyst" in agents else default_agent,
            "company_development_status",
            "public_report",
            3,
            f"{query} public report financial filing industry trend funding regulation",
            True,
            True,
            "medium",
            "cache_metadata_and_short_excerpt",
        )
        | {
            "source_group_id": "public_report",
            "source_matrix_ref": DEFAULT_RECRUITMENT_SOURCE_MATRIX_REF,
            "user_instruction_required": False,
            "display_sources": display_sources_by_type["public_report"],
        },
        task(
            "official-school-career-signal",
            "job-scout" if "job-scout" in agents else default_agent,
            "school_company_cooperation",
            "official_school_notice",
            1,
            f"{query} official school career center campus notice cooperation internship",
            True,
            True,
            "strong",
            "cache_metadata_and_short_excerpt",
        )
        | {
            "source_group_id": "school_primary",
            "source_matrix_ref": DEFAULT_RECRUITMENT_SOURCE_MATRIX_REF,
            "user_instruction_required": False,
            "display_sources": display_sources_by_type["official_school_notice"],
        },
    ]
    return tasks


def is_target_job_fit_context(context: dict[str, Any]) -> bool:
    target = context.get("target_context", {})
    return bool(
        context.get("task_type") == "target_job_fit"
        or (isinstance(target, dict) and target.get("target_job_fit_requested") is True)
    )


def build_target_job_fit_tasks(
    invocations: list[dict[str, Any]],
    terms: list[str],
) -> list[dict[str, Any]]:
    query = " ".join(terms[:8])
    agents = {invocation["target_agent"] for invocation in invocations}
    jd_agent = "jd-analyzer" if "jd-analyzer" in agents else invocations[0]["target_agent"]
    learning_agent = (
        "learning-path-strategist"
        if "learning-path-strategist" in agents
        else jd_agent
    )
    display_sources_by_type = source_display_by_type()
    return [
        task(
            "target-current-jd-verification",
            jd_agent,
            "current_target_jd_requirement",
            "recruitment_platform_jd",
            2,
            f"{query} current JD target internship job requirements official public",
            True,
            True,
            "medium",
            "cache_metadata_and_short_excerpt",
        )
        | {
            "source_group_id": "public_recruitment_platform",
            "source_matrix_ref": DEFAULT_RECRUITMENT_SOURCE_MATRIX_REF,
            "user_instruction_required": False,
            "display_sources": display_sources_by_type["recruitment_platform_jd"],
        },
        task(
            "target-learning-gap-evidence",
            learning_agent,
            "target_skill_gap_and_project_evidence",
            "verified_hr_public_post",
            2,
            f"{query} verified HR skill gap project expectation campus recruiting",
            True,
            False,
            "medium",
            "cache_metadata_and_short_excerpt",
        )
        | {
            "source_group_id": "verified_hr_public",
            "source_matrix_ref": DEFAULT_RECRUITMENT_SOURCE_MATRIX_REF,
            "user_instruction_required": False,
            "display_sources": display_sources_by_type["verified_hr_public_post"],
        },
    ]


def detect_target_companies(context: dict[str, Any]) -> list[str]:
    text = json.dumps(context, ensure_ascii=False)
    candidates = ["ByteDance", "Tencent", "DJI", "Zhipu", "CATL", "Alibaba", "Baidu", "Huawei"]
    return [candidate for candidate in candidates if re.search(candidate, text, re.I)]


def build_source_plan(run_dir: Path, output_ref: str) -> dict[str, Any]:
    context = load_context(run_dir)
    invocations = load_invocations(run_dir)
    terms = target_terms(context)
    output_path = run_dir / output_ref
    research_tasks = build_tasks(invocations, terms)
    blocked_outputs_without_current_jd: list[str] = []
    if is_target_job_fit_context(context):
        research_tasks.extend(build_target_job_fit_tasks(invocations, terms))
        blocked_outputs_without_current_jd = [
            "targeted_resume_tailoring",
            "fit_score",
            "company_specific_skill_weight_ranking",
        ]
    plan = {
        "public_source_research_plan": {
            "run_id": invocations[0]["run_id"],
            "policy_ref": POLICY_REF,
            "source_matrix_ref": DEFAULT_RECRUITMENT_SOURCE_MATRIX_REF,
            "source_discovery_mode": "auto_injected_by_recruitment_roles",
            "user_instruction_required": False,
            "network_execution_default": NETWORK_DEFAULT,
            "created_from": [
                "runtime_context_packet",
                "subagent_invocations",
                "repository_source_policy",
                DEFAULT_RECRUITMENT_SOURCE_MATRIX_REF,
            ],
            "target_terms": terms,
            "target_companies_detected": detect_target_companies(context),
            "target_job_fit_requested": is_target_job_fit_context(context),
            "blocked_outputs_without_current_jd": blocked_outputs_without_current_jd,
            "missing_jd_fields_policy": "ask_hr_not_user_and_do_not_block_recommendation",
            "hr_confirmation_fields_when_jd_silent": [
                "opening_status",
                "city_or_work_location",
                "onsite_days_or_arrival",
                "deadline",
                "headcount",
                "internship_duration",
            ],
            "research_tasks": research_tasks,
            "blocked_source_types": [
                {
                    "source_type": "private_resume",
                    "reason": "Private candidate resumes cannot be collected or used as market evidence.",
                },
                {
                    "source_type": "private_chat",
                    "reason": "Private chats, screenshots, or recruiter backend data are not allowed.",
                },
                {
                    "source_type": "login_only_page",
                    "reason": "Do not bypass login, anti-scraping, or platform restrictions.",
                },
                {
                    "source_type": "single_anonymous_post_as_final_basis",
                    "reason": "Weak social signals can guide preparation only, not final weights or decisions.",
                },
            ],
            "minimum_weight_evidence_rule": "Weights need current official/JD/verified HR/public multi-source evidence; otherwise not_available or needs_more_sources.",
            "execution_note": "This is a source plan only. It does not browse, log in, scrape, or cache public sources.",
        }
    }
    write_json(output_path, plan)
    return {
        "source_plan_response": {
            "exit_status": "success",
            "run_id": invocations[0]["run_id"],
            "source_plan_ref": rel(output_path, run_dir),
        }
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a policy-bound public source research plan for a run.")
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--output", default="evidence/public_source_research_plan.json")
    args = parser.parse_args(argv)
    try:
        response = build_source_plan(args.run_dir, args.output)
        print(json.dumps(response, ensure_ascii=False, indent=2))
        return 0
    except (OSError, json.JSONDecodeError, KeyError, SourcePlanError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
