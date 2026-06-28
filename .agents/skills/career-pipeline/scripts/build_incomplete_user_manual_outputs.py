#!/usr/bin/env python
import argparse
import json
import sys
from pathlib import Path
from typing import Any


LIMITED_BLOCKED_OUTPUTS = [
    "fit_score",
    "application_priority",
    "targeted_resume_tailoring",
    "company_specific_skill_weight_ranking",
]


class ManualOutputBuilderError(Exception):
    pass


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ManualOutputBuilderError(f"missing required file: {path}")
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ManualOutputBuilderError(f"{path} must be a JSON object")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_plan(run_dir: Path, plan_ref: str) -> dict[str, Any]:
    payload = load_json(run_dir / plan_ref)
    plan = payload.get("subagent_invocation_plan")
    if not isinstance(plan, dict):
        raise ManualOutputBuilderError(f"{plan_ref}: missing subagent_invocation_plan")
    queue = plan.get("dispatch_queue")
    if not isinstance(queue, list) or not queue:
        raise ManualOutputBuilderError(f"{plan_ref}: dispatch_queue must be non-empty")
    return plan


def load_context(run_dir: Path) -> dict[str, Any]:
    manifest = load_json(run_dir / "manifest.json")
    ref = manifest.get("execution_manifest", {}).get("runtime_context_packet_ref")
    if not isinstance(ref, str) or not ref:
        raise ManualOutputBuilderError("manifest missing runtime_context_packet_ref")
    payload = load_json(run_dir / ref)
    context = payload.get("runtime_context_packet")
    if not isinstance(context, dict):
        raise ManualOutputBuilderError(f"{ref}: missing runtime_context_packet")
    return context


def load_sources(run_dir: Path) -> list[dict[str, Any]]:
    path = run_dir / "evidence" / "allowed_public_sources.generated.json"
    if not path.is_file():
        return []
    payload = load_json(path)
    sources = payload.get("sources")
    return [source for source in sources if isinstance(source, dict)] if isinstance(sources, list) else []


def invocation_id(run_dir: Path, item: dict[str, Any]) -> str:
    payload = load_json(run_dir / item["invocation_ref"])
    invocation = payload.get("subagent_invocation")
    if not isinstance(invocation, dict) or not invocation.get("invocation_id"):
        raise ManualOutputBuilderError(f"{item['invocation_ref']}: missing invocation_id")
    return str(invocation["invocation_id"])


def evidence_basis_from_sources(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    evidence = []
    for index, source in enumerate(sources[:4]):
        url = str(source.get("source_ref") or "").strip()
        if not url:
            continue
        evidence.append(
            {
                "claim_id": str(source.get("task_id") or f"source-{index}"),
                "field": str(source.get("field") or "public_source_evidence"),
                "source_type": str(source.get("source_type") or "official_or_primary"),
                "source_ref": url,
                "user_owned_or_public": "public",
                "evidence_strength": "medium",
                "inference_level": "low",
                "confidence": "medium",
            }
        )
    return evidence


def weight_provenance() -> list[dict[str, Any]]:
    return [
        {
            "parameter": "exact_application_weight",
            "proposed_weight": None,
            "weight_status": "not_available",
            "source_refs": [],
            "source_types": [],
            "retrieved_or_published_dates": [],
            "sample_size_or_source_count": "0",
            "evidence_strength": "missing",
            "confidence": "low",
            "cannot_decide_alone": True,
        }
    ]


def public_urls(sources: list[dict[str, Any]]) -> list[str]:
    urls = []
    for source in sources:
        url = str(source.get("source_ref") or "").strip()
        if url.startswith(("http://", "https://")):
            urls.append(url)
    return list(dict.fromkeys(urls))


def base_output(
    run_dir: Path,
    item: dict[str, Any],
    sources: list[dict[str, Any]],
    status: str = "done_with_warnings",
) -> dict[str, Any]:
    return {
        "invocation_ref": item["invocation_ref"],
        "role": item["target_agent"],
        "task_summary": "Manual Controller MVP output for incomplete-user general resume delivery validation.",
        "inputs_used": [item["prompt_bundle_ref"]],
        "database_files_used": [],
        "source_notes": [
            "Public URLs are exploration or role-family sources, not exact apply-now proof.",
            "No target JD was provided, so exact score, final priority, and tailored resume remain unavailable.",
        ],
        "runtime_scope": "conditional_runtime_judgment",
        "judgment_allowed": "conditional_with_runtime_evidence",
        "judgment_status": "evidence_bound_judgment",
        "decision_owner": "local_subagent",
        "runtime_preconditions": {
            "has_current_jd": False,
            "has_target_company": False,
            "has_user_constraints": False,
            "has_user_consent": True,
            "job_direction_blocked": False,
        },
        "evidence_basis": evidence_basis_from_sources(sources),
        "repository_prior_usage": [],
        "weight_provenance": weight_provenance(),
        "conditional_options": [],
        "blocked_outputs": LIMITED_BLOCKED_OUTPUTS,
        "runtime_research_tasks": [
            "Collect a concrete public JD before exact fit score, final application priority, or one-role-one-resume tailoring."
        ],
        "role_output_packet": {
            "invocation_id": invocation_id(run_dir, item),
            "target_agent": item["target_agent"],
            "status": status,
            "role_output_ref": item["output_artifact_target"],
            "evidence_packet_refs": [],
            "runtime_weights_ref": "merge/runtime_weights.json",
            "artifact_refs": [item["prompt_bundle_ref"]],
            "blocked_outputs": LIMITED_BLOCKED_OUTPUTS,
            "runtime_research_tasks": [
                "Collect a concrete public JD before exact fit score, final application priority, or one-role-one-resume tailoring."
            ],
            "needs_user_confirmation": [],
            "handoff_to": [],
            "errors": [],
            "confidence": "medium",
        },
        "error_recovery_state": {
            "status": "degraded",
            "errors": [],
            "recovery_actions": ["continue_with_exploration_and_general_resume"],
            "degraded_outputs": LIMITED_BLOCKED_OUTPUTS,
            "blocked_outputs": LIMITED_BLOCKED_OUTPUTS,
            "safe_outputs": [
                "direction_exploration",
                "learning_plan_before_application",
                "project_recommendations",
                "campus_general_resume_draft",
            ],
            "next_action": "continue",
        },
    }


def add_role_specific_fields(payload: dict[str, Any], context: dict[str, Any], sources: list[dict[str, Any]]) -> None:
    agent = payload["role"]
    urls = public_urls(sources)
    if agent == "major-cluster-classifier":
        payload["major_cluster_result"] = {
            "discipline_domain": "engineering",
            "major_cluster": "computer_science",
            "cross_tags": ["software_development", "data_and_ai_foundation"],
            "evidence": ["user stated computer-related major"],
        }
    elif agent == "profile-extractor":
        payload["profile_summary"] = {
            "known_facts": context.get("known_user_facts", []),
            "missing_user_owned_facts": context.get("missing_user_owned_facts", []),
            "candidate_stage": context.get("candidate_stage", "non_graduating"),
        }
    elif agent == "job-scout":
        payload["recommended_application_targets"] = [
            {
                "company": "ByteDance",
                "title_or_role_family": "campus internship exploration entry",
                "scenario": "explore",
                "public_urls": urls[:1],
                "why_this_target": "The user has only broad computer/Python information, so this is an exploration entrypoint, not an apply-now recommendation.",
                "ask_hr_about": ["Confirm current opening status, city, arrival time, duration, and team-specific requirements with HR if a concrete JD is found."],
            }
        ]
        if len(urls) > 1:
            payload["recommended_application_targets"].append(
                {
                    "company": "Nowcoder public jobs",
                    "title_or_role_family": "internship JD exploration pool",
                    "scenario": "explore",
                    "public_urls": urls[1:2],
                    "why_this_target": "Public job-search entry can help collect concrete internship JDs before ranking or tailoring.",
                    "ask_hr_about": ["Confirm role freshness, location, and interview process with the recruiter."],
                }
            )
    elif agent == "jd-analyzer":
        payload["jd_family_requirements"] = {
            "status": "role_family_only",
            "safe_requirement_themes": ["Python foundation", "basic engineering project evidence", "Git/GitHub or equivalent proof artifact"],
            "blocked_exact_jd_requirements": ["No concrete JD text or public job detail page was provided."],
        }
    elif agent == "match-strategist":
        payload["current_fit_assessment"] = {
            "status": "direction_exploration",
            "summary": "Computer-related junior with Python basics can explore software, testing, data, or AI-application internship directions, but exact ranking needs project and JD evidence.",
        }
        payload["application_readiness_decision"] = {
            "status": "prepare_first",
            "reason": "Project, internship, school, and concrete JD evidence are missing.",
        }
        payload["skill_gap_analysis"] = {
            "must_have_gaps": ["A public, explainable project connected to the chosen internship direction."],
            "nice_to_have_gaps": ["Basic SQL/Linux/Git or role-specific AI application knowledge after a target direction is chosen."],
            "project_evidence_gaps": ["No project responsibility, output, repository, or demo evidence was supplied."],
            "interview_defensibility_gaps": ["Needs concrete examples of problem, implementation, personal contribution, and result."],
        }
    elif agent == "learning-path-strategist":
        payload["skill_gap_analysis"] = {
            "must_have_gaps": ["Choose one role family first: backend, testing, data analysis, or AI application."],
            "project_evidence_gaps": ["Build one small but complete project with code, README, demo screenshot, and personal contribution notes."],
        }
        payload["learning_plan_before_application"] = {
            "status": "prepare_first",
            "skills_to_learn": ["Git/GitHub workflow", "Python project structure", "SQL basics", "one role-family-specific framework or tool"],
            "projects_to_build": ["A small Python API/data/AI-application project selected after choosing a target role family."],
            "proof_artifacts": ["repository", "README", "run screenshot", "short project review"],
            "resume_conversion_conditions": ["Only write the project into the resume after it runs and the user can explain personal contribution and failure boundaries."],
            "ask_hr_about": [],
        }
        payload["project_selection_rubric"] = {
            "role_fit": "match the first target internship family",
            "completion_speed": "finish a minimum credible version in days, then iterate",
            "implementation_cost": "prefer local runnable project with public proof artifacts",
            "resume_value": "must show individual ownership and measurable output",
            "interview_depth": "must support follow-up questions about design and tradeoffs",
            "public_evidence_quality": "repository and README required before resume conversion",
            "risk_control": "planned work is not written as completed experience",
        }
        payload["project_recommendations"] = [
            {
                "project_name": "Python internship direction smoke-test project",
                "target_role_family": "backend/data/AI application internship exploration",
                "recommended_project_mode": "smoke-test",
                "why_this_project": "It is the fastest credible way for a vague Python foundation to become visible resume evidence.",
                "implementation_steps": [
                    "Pick one role family and define a tiny end-to-end use case.",
                    "Implement the core workflow with clear input, output, and error handling.",
                    "Write README with setup, usage, screenshots, and personal contribution.",
                    "Prepare a 60-second explanation of problem, module design, and limitation.",
                ],
                "proof_artifacts": ["GitHub/Gitee repository", "README", "run screenshot", "short review note"],
                "resume_conversion_conditions": [
                    "Project runs locally or has a reproducible demo.",
                    "The user can explain personal contribution and failure boundaries.",
                    "Do not describe planned enhancements as completed outcomes.",
                ],
                "interview_defensibility_questions": [
                    "What problem does the project solve?",
                    "Which module did you implement yourself?",
                    "What would fail under larger data or more users?",
                ],
                "source_basis": ["user_provided_profile", "public role-family exploration sources"],
            }
        ]
    elif agent == "resume-format-gate":
        payload["format_gate_status"] = "pass"
        payload["format_status"] = "accepted"
        payload["factual_review_status"] = "not_reviewed"
        payload["primary_resume_version"] = "campus_general_cn_one_page"
        payload["editable_first_draft_allowed"] = True
        payload["resume_architect_allowed"] = True
        payload["incomplete_resume_allowed_with_user_consent"] = True
        payload["incomplete_resume"] = True
        payload["job_direction_blocked"] = False
        payload["section_evidence_status"] = {
            "school_information": "partial",
            "contact": "missing",
            "skills": "partial",
            "projects": "missing",
            "personality_and_potential": "safe_brief_only",
        }
        payload["missing_materials"] = context.get("missing_user_owned_facts", [])
        payload["questions_for_user"] = [
            "Please provide school, degree, graduation time, projects, internships, and contact fields if you want a stronger resume."
        ]
    elif agent == "resume-architect":
        payload["resume_version"] = "campus_general_cn_one_page"
        payload["resume_strategy"] = (
            "Use only user-provided facts. Keep the draft broad for campus/internship exploration; omit missing school, contact, project, and internship details."
        )
        payload["section_order"] = ["学校信息", "个人联系方式", "掌握技能", "项目竞赛经历", "个人性格和潜力"]
        payload["section_plan"] = {
            "学校信息": "Only write known grade/major; school and graduation time are missing.",
            "个人联系方式": "Omit because no contact fields were authorized.",
            "掌握技能": "Write Python as basic coursework/self-learning foundation, not advanced proficiency.",
            "项目竞赛经历": "Omit completed projects because none were provided.",
            "个人性格和潜力": "Use restrained wording tied to exploration and learning motivation.",
        }
        payload["format_quality_after_generation"] = {"readability": "clear", "information_completeness": "partial"}
        payload["resume_artifact"] = {
            "artifact_type": "resume_draft",
            "resume_version": "campus_general_cn_one_page",
            "privacy_class": "user_private",
        }
        payload["final_resume_draft"] = "\n".join(
            [
                "# 计算机类大三学生",
                "",
                "## 学校信息",
                "- 专业方向：计算机相关专业",
                "- 年级：大三",
                "- 求职阶段：实习方向探索",
                "",
                "## 掌握技能",
                "- Python：具备基础语法和脚本编写基础，可继续补充课程作业、实验或项目中的具体使用场景。",
                "",
                "## 项目竞赛经历",
                "- 暂未提供可写入简历的已完成项目、竞赛或实习经历；建议补充项目名称、个人职责、技术栈、结果和作品链接后再写入。",
                "",
                "## 个人性格和潜力",
                "- 对实习方向处于探索阶段，具备从 Python 基础继续沉淀工程项目证据的空间。",
            ]
        )
        payload["resume_delivery_artifacts"] = [
            {"format": "docx", "artifact_ref": "", "status": "pending_renderer_after_factual_review"},
            {"format": "pdf", "artifact_ref": "", "status": "pending_renderer_after_factual_review"},
            {"format": "image", "artifact_ref": "", "status": "pending_renderer_after_factual_review"},
        ]
        payload["format_gate_status"] = "pass"
        payload["format_status"] = "accepted"
        payload["factual_review_status"] = "pass"
        payload["incomplete_resume"] = True
        payload["job_direction_blocked"] = False
    elif agent == "hr-supervisor":
        payload["hr_real_question_bank"] = []
        payload["likely_interview_questions"] = []
        payload["resume_defensibility_checks"] = [
            "Resume draft does not invent school name, contact, project, internship, awards, or metrics.",
            "Current draft is broad and incomplete; target-specific tailoring waits for public JD evidence.",
        ]
        payload["user_facing_package_review"] = {
            "status": "pass_with_limitations",
            "note": "Professional output should emphasize current positioning, missing facts, learning path, and next actions.",
        }
    elif agent == "factual-reviewer":
        payload["factual_review_status"] = "pass"
        payload["resume_delivery_artifact_review"] = {
            "status": "renderer_required_after_review",
            "required_formats": ["docx", "pdf", "image"],
        }


def build_outputs(args: argparse.Namespace) -> dict[str, Any]:
    run_dir = args.run_dir
    plan = load_plan(run_dir, args.plan_ref)
    context = load_context(run_dir)
    sources = load_sources(run_dir)
    if not sources:
        raise ManualOutputBuilderError("allowed public sources are required before building manual outputs")
    out_dir = args.out_dir
    output_paths: dict[str, str] = {}
    for item in plan["dispatch_queue"]:
        payload = base_output(run_dir, item, sources)
        add_role_specific_fields(payload, context, sources)
        output_path = out_dir / f"{item['target_agent']}.manual-output.json"
        write_json(output_path, payload)
        output_paths[item["target_agent"]] = str(output_path)
    return {
        "manual_output_builder_response": {
            "exit_status": "success",
            "run_id": plan["run_id"],
            "scope": "incomplete_user_general_resume_delivery_validation",
            "not_a_live_subagent_adapter": True,
            "output_paths": output_paths,
        }
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build conservative Manual Controller role outputs for incomplete-user general resume validation."
    )
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--plan-ref", default="invocations/subagent_invocation_plan.json")
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(build_outputs(args), ensure_ascii=False, indent=2))
        return 0
    except (OSError, json.JSONDecodeError, KeyError, ManualOutputBuilderError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
