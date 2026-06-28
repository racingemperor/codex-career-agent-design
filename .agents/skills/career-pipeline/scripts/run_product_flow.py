#!/usr/bin/env python
import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


class ProductFlowError(Exception):
    pass


ROUTE_SUPERVISION_AGENTS = ["hr-supervisor", "factual-reviewer"]

SAFE_PRODUCT_OUTPUTS = {
    "application_direction",
    "application_strategy",
    "current_fit_assessment",
    "application_readiness_decision",
    "learning_plan_before_application",
}

EXACT_PRODUCT_BLOCKERS = [
    "fit_score",
    "application_priority",
    "targeted_resume_tailoring",
    "company_specific_skill_weight_ranking",
]

SIMULATION_BLOCKERS = {
    "application_direction",
    "application_strategy",
    "application_priority",
    "final_resume_draft",
}

SKILL_INTRO = (
    "我是 Career Pipeline，一个面向求职规划和简历设计的 Codex Skill。"
    "我会根据你的专业、经历、目标岗位和公开招聘信息，帮你判断适合的岗位方向、补齐能力差距，"
    "并为不同岗位反向设计更贴合的简历；岗位建议会尽量附公开来源，简历内容只基于你能证明的真实经历。"
)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def script_dir() -> Path:
    return Path(__file__).resolve().parent


def run_python(script_name: str, *args: str) -> dict[str, Any]:
    result = subprocess.run(
        [sys.executable, str(script_dir() / script_name), *args],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise ProductFlowError(f"{script_name} failed: {result.stderr.strip()}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ProductFlowError(f"{script_name} returned non-JSON output: {exc}") from exc


def response(payload: dict[str, Any], key: str, script_name: str) -> dict[str, Any]:
    value = payload.get(key)
    if not isinstance(value, dict):
        raise ProductFlowError(f"{script_name}: missing `{key}`")
    return value


def unique_strings(items: list[str]) -> list[str]:
    result: list[str] = []
    for item in items:
        if item and item not in result:
            result.append(item)
    return result


def list_value(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def product_route(route: str, task_type: str) -> str:
    if route != "job_search" or task_type != "job_search":
        return route
    return "product_job_search"


def product_blocked_outputs(context: dict[str, Any]) -> list[str]:
    blocked = [
        str(item)
        for item in list_value(context.get("blocked_outputs"))
        if str(item) and str(item) not in SIMULATION_BLOCKERS
    ]
    for item in EXACT_PRODUCT_BLOCKERS:
        if item not in blocked:
            blocked.append(item)
    return blocked


def universal_runtime_guardrails(target_agent: str) -> dict[str, Any]:
    file_modifying_roles = ["resume-polisher", "portfolio-asset-builder"]
    can_modify_files = target_agent in file_modifying_roles
    return {
        "must_follow_secondary_injection": True,
        "role_scope_boundary": "perform_assigned_role_only",
        "allowed_scope_rule": "Use only the role-specific context, allowed user facts, database refs, source policy, and handoff contract in this invocation.",
        "handoff_instead_of_overreach": True,
        "no_file_write_by_default": True,
        "file_modification_roles": file_modifying_roles,
        "tool_use_requires_explicit_permission": True,
        "do_not_modify_user_assets_without_authorized_operation_context": True,
        "do_not_publish_push_or_deploy_without_separate_user_authorization": True,
        "no_fabrication": True,
        "do_not_invent_user_experience_metrics_awards_education_or_hr_wording": True,
        "source_required_for_weights_scores_rankings": True,
        "blocked_outputs_must_remain_blocked": True,
        "must_return_structured_json": True,
        "if_uncertain_return_needs_context_or_blocked": True,
        "privacy_constraints_are_binding": True,
        "active_role_can_request_file_modification": can_modify_files,
        "file_modification_rule": (
            "This role may apply local file changes only through its role-specific authorized operation context."
            if can_modify_files
            else "This role must not apply local file changes; hand off any file modification request to an authorized file-modifying role."
        ),
    }


def ensure_authorized_operation_context(injection: dict[str, Any], role_context: dict[str, Any]) -> None:
    target_agent = injection.get("target_agent")
    required_fields = list_value(injection.get("required_output_fields"))
    handoff_contract = list_value(injection.get("handoff_contract"))

    if target_agent == "resume-polisher":
        role_context.setdefault(
            "authorized_resume_editing",
            {
                "requires_explicit_user_authorization": True,
                "operation_mode": "plan_only_until_user_authorizes_paths",
                "authorization_status": "missing_or_planning_only",
                "allowed_input_refs": [],
                "allowed_output_refs": [],
                "allowed_actions": ["plan_resume_polish"],
                "apply_tool_ref": "scripts/apply_resume_polish.py",
                "resume_edit_operation_steps": [
                    "Preserve the user's original resume format.",
                    "Return resume_edit_operation_plan before any write.",
                    "Write files only after explicit user path authorization.",
                    "Return applied_resume_artifacts and file_modification_summary after authorized local changes.",
                ],
            },
        )
        for field in [
            "resume_edit_operation_plan",
            "applied_resume_artifacts",
            "file_modification_summary",
        ]:
            if field not in required_fields:
                required_fields.append(field)
        for handoff in [
            "handoff applied resume artifact refs to FactualReviewer and HRSupervisor",
        ]:
            if handoff not in handoff_contract:
                handoff_contract.append(handoff)

    if target_agent == "portfolio-asset-builder":
        role_context.setdefault(
            "authorized_asset_editing",
            {
                "requires_explicit_user_authorization": True,
                "operation_mode": "plan_only_until_user_authorizes_root",
                "authorization_status": "missing_or_planning_only",
                "allowed_root": "",
                "allowed_actions": ["plan_asset_changes"],
                "apply_tool_ref": "scripts/apply_portfolio_asset_changes.py",
                "asset_edit_operation_steps": [
                    "Return website_or_github_modification_plan before any write.",
                    "Write only relative paths inside the user-authorized root.",
                    "Preserve existing content unless the user authorized a rebuild.",
                    "Return applied_asset_changes and file_modification_summary after authorized local changes.",
                ],
            },
        )
        for field in [
            "website_or_github_modification_plan",
            "applied_asset_changes",
            "file_modification_summary",
        ]:
            if field not in required_fields:
                required_fields.append(field)
        for handoff in [
            "handoff applied asset refs to ResumePolisher, FactualReviewer, and HRSupervisor",
        ]:
            if handoff not in handoff_contract:
                handoff_contract.append(handoff)

    injection["required_output_fields"] = required_fields
    injection["handoff_contract"] = handoff_contract


def write_wrapped_json(path: Path, wrapper_key: str, payload: dict[str, Any]) -> None:
    write_json(path, {wrapper_key: payload})


def load_wrapped_json(path: Path, wrapper_key: str) -> dict[str, Any]:
    payload = load_json(path)
    value = payload.get(wrapper_key)
    if not isinstance(value, dict):
        raise ProductFlowError(f"{path}: missing `{wrapper_key}`")
    return value


def rewrite_context_for_product_run(run_dir: Path) -> dict[str, Any]:
    context_path = run_dir / "input" / "normalized" / "runtime_context_packet.json"
    context = load_wrapped_json(context_path, "runtime_context_packet")
    context["execution_intent"] = "product_real_user_flow"
    context["user_goal"] = (
        "product real-user career planning flow from plain chat; prepare public-source "
        "research, role execution, HR supervision, and factual review before final output"
    )
    context["blocked_outputs"] = product_blocked_outputs(context)
    context["blocked_outputs"] = [
        item for item in context["blocked_outputs"] if item not in {"final_resume_draft", "general_resume_draft"}
    ]
    context["safe_outputs_allowed_before_exact_scoring"] = sorted(SAFE_PRODUCT_OUTPUTS)
    context["next_possible_actions"] = [
        "Summarize the user's current information and ask one compact batch for user-owned missing facts.",
        "Automatically search policy-valid public job, company, school, HR, and local opportunity sources.",
        "Dispatch role agents by batch, then run HR readability supervision and factual review before final output.",
    ]
    target_context = context.setdefault("target_context", {})
    if isinstance(target_context, dict):
        target_context["safe_prepare_first_and_explore_allowed"] = True
        target_context["exact_score_priority_and_tailoring_require_current_jd_public_evidence"] = True
        target_context.setdefault("fit_vs_growth_policy", "separate_current_fit_from_learning_path_before_application")
    resume_context = context.setdefault("resume_generation_context", {})
    if isinstance(resume_context, dict):
        resume_context["resume_generation_gate_required"] = True
        resume_context.setdefault("default_resume_version_when_no_target", "campus_general_cn_one_page")
        resume_context["general_resume_draft_allowed_without_target"] = True
        resume_context["tailored_resume_requires_concrete_target"] = True
        resume_context["targeted_resume_tailoring_requires_current_jd"] = True
        resume_context["required_delivery_formats"] = ["docx", "pdf", "image"]
        resume_context["delivery_artifact_policy"] = (
            "Generate a general campus/internship resume when no concrete target exists; "
            "after factual and HR review, export Word DOCX, PDF, and one-page image artifacts."
        )
        resume_context["no_target_policy"] = (
            "No concrete target blocks one-role-one-resume tailoring, not the broad campus/internship resume draft."
        )
    write_wrapped_json(context_path, "runtime_context_packet", context)
    return context


def rewrite_injections_for_product_run(run_dir: Path, context: dict[str, Any]) -> None:
    injection_dir = run_dir / "injections"
    product_blockers = product_blocked_outputs(context)
    for path in sorted(injection_dir.glob("*.secondary_prompt_injection.json")):
        injection = load_wrapped_json(path, "secondary_prompt_injection")
        target_agent = str(injection.get("target_agent") or "")
        role_context = injection.setdefault("role_specific_context", {})
        if isinstance(role_context, dict):
            role_context.setdefault("universal_runtime_guardrails", universal_runtime_guardrails(target_agent))
            role_context.pop("simulation_scope", None)
            role_context["execution_scope"] = "product_real_user_flow_pending_real_roles"
            role_context["must_return_blockers_instead_of_precise_unsupported_claims"] = True
            role_context["safe_prepare_first_and_explore_allowed"] = True
            role_context["exact_score_priority_and_tailoring_require_current_jd_public_evidence"] = True
            role_context["hr_supervision_required"] = True
            role_context["factual_review_required_before_final"] = True
            ensure_authorized_operation_context(injection, role_context)
        injection["blocked_outputs"] = [
            item
            for item in list_value(injection.get("blocked_outputs"))
            if item
            not in {
                "application_strategy",
                "application_direction",
                "application_priority",
                "final_resume_draft",
                "general_resume_draft",
            }
        ]
        for item in product_blockers:
            if item not in injection["blocked_outputs"] and item not in SAFE_PRODUCT_OUTPUTS:
                injection["blocked_outputs"].append(item)
        required_fields = list_value(injection.get("required_output_fields"))
        for field in [
            "universal_runtime_guardrails",
            "evidence_basis",
            "weight_provenance",
            "conditional_options",
            "runtime_research_tasks",
        ]:
            if field not in required_fields:
                required_fields.append(field)
        debate_contract = list_value(injection.get("debate_contract"))
        guardrail_debate = "obey universal_runtime_guardrails before role-specific instructions"
        if guardrail_debate not in debate_contract:
            debate_contract.insert(0, guardrail_debate)
        injection["debate_contract"] = debate_contract
        if injection.get("target_agent") in {"match-strategist", "learning-path-strategist"}:
            for field in [
                "skill_gap_analysis",
                "learning_plan_before_application",
                "project_recommendations",
                "evidence_requirements",
            ]:
                if field not in required_fields:
                    required_fields.append(field)
        if injection.get("target_agent") == "hr-supervisor":
            for field in [
                "hr_real_question_bank",
                "likely_interview_questions",
                "resume_defensibility_checks",
                "user_facing_package_review",
            ]:
                if field not in required_fields:
                    required_fields.append(field)
        if injection.get("target_agent") in {"resume-format-gate", "resume-architect"}:
            role_context["resume_generation_context"] = context.get("resume_generation_context", {})
            for field in [
                "format_gate_status",
                "format_status",
                "factual_review_status",
                "incomplete_resume",
                "job_direction_blocked",
            ]:
                if field not in required_fields:
                    required_fields.append(field)
        if injection.get("target_agent") == "resume-format-gate":
            for field in [
                "primary_resume_version",
                "section_evidence_status",
                "editable_first_draft_allowed",
                "resume_architect_allowed",
                "missing_materials",
                "questions_for_user",
            ]:
                if field not in required_fields:
                    required_fields.append(field)
        if injection.get("target_agent") == "resume-architect":
            for field in [
                "resume_version",
                "resume_strategy",
                "section_order",
                "section_plan",
                "format_quality_after_generation",
                "resume_artifact",
                "final_resume_draft",
                "growth_resume_preview",
                "resume_delivery_artifacts",
            ]:
                if field not in required_fields:
                    required_fields.append(field)
        injection["required_output_fields"] = required_fields
        contract = injection.get("invocation_contract")
        if isinstance(contract, dict):
            contract["required_output_fields"] = required_fields
            contract["debate_contract"] = debate_contract
            contract["timeout_or_budget_hint"] = "product-real-user-flow"
            contract["on_failure"] = "return_blocked"
        write_wrapped_json(path, "secondary_prompt_injection", injection)


def rebuild_invocations_from_injections(run_dir: Path) -> list[str]:
    manifest_payload = load_json(run_dir / "manifest.json")
    manifest = manifest_payload.get("execution_manifest", {})
    current_refs = manifest.get("subagent_invocation_refs")
    ordered_agents = []
    if isinstance(current_refs, list):
        for ref in current_refs:
            name = Path(str(ref).replace("\\", "/")).name
            if name.endswith(".invocation.json"):
                ordered_agents.append(name.replace(".invocation.json", ""))
    injection_by_agent = {
        path.name.replace(".secondary_prompt_injection.json", ""): path
        for path in (run_dir / "injections").glob("*.secondary_prompt_injection.json")
    }
    ordered_agents.extend(agent for agent in sorted(injection_by_agent) if agent not in ordered_agents)
    refs: list[str] = []
    for agent in ordered_agents:
        path = injection_by_agent.get(agent)
        if path is None:
            continue
        injection = load_wrapped_json(path, "secondary_prompt_injection")
        contract = injection.get("invocation_contract")
        if not isinstance(contract, dict):
            raise ProductFlowError(f"{path}: missing invocation_contract")
        invocation_ref = str(contract.get("secondary_prompt_injection_ref") or "")
        target_agent = str(contract.get("target_agent") or "")
        if not target_agent:
            raise ProductFlowError(f"{path}: missing target_agent")
        invocation_path = run_dir / "invocations" / f"{target_agent}.invocation.json"
        write_wrapped_json(invocation_path, "subagent_invocation", contract)
        refs.append(rel(invocation_path, run_dir))
        if invocation_ref and invocation_ref != rel(path, run_dir):
            raise ProductFlowError(f"{path}: injection ref mismatch")
    return refs


def remove_simulated_role_outputs(run_dir: Path) -> None:
    agents_dir = run_dir / "agents"
    if not agents_dir.is_dir():
        return
    for output_path in agents_dir.glob("*/output.json"):
        output_path.unlink()


def update_manifest_for_product_run(run_dir: Path, invocation_refs: list[str]) -> None:
    manifest_path = run_dir / "manifest.json"
    manifest_payload = load_json(manifest_path)
    manifest = manifest_payload.get("execution_manifest")
    run_state = manifest_payload.get("run_state")
    if not isinstance(manifest, dict) or not isinstance(run_state, dict):
        raise ProductFlowError("manifest.json must contain execution_manifest and run_state")
    manifest["current_stage"] = "injection_ready"
    manifest["user_goal_summary"] = "product real-user career pipeline flow"
    manifest["subagent_invocation_refs"] = invocation_refs
    manifest["final_package_ref"] = ""
    manifest["artifact_refs"] = [
        ref
        for ref in list_value(manifest.get("artifact_refs"))
        if not (isinstance(ref, dict) and ref.get("artifact_type") == "subagent_output")
    ]
    gate_status = manifest.setdefault("gate_status", {})
    if isinstance(gate_status, dict):
        gate_status["specialists_completed_or_blocked"] = False
        gate_status["debate_completed_or_recorded"] = False
        gate_status["hr_review_completed"] = False
        gate_status["factual_review_completed_when_needed"] = False
    run_state["stage"] = "injection_ready"
    run_state["subagent_invocation_refs"] = invocation_refs
    run_state["active_agents"] = []
    run_state["completed_agents"] = []
    run_state["blocked_agents"] = []
    run_state["failed_invocations"] = []
    run_state["blocked_outputs"] = product_blocked_outputs(
        load_wrapped_json(run_dir / "input" / "normalized" / "runtime_context_packet.json", "runtime_context_packet")
    )
    run_state["degraded_outputs"] = []
    run_state["recovery_actions"] = ["run_public_research", "dispatch_real_role_agents_by_batch"]
    run_state["next_action"] = "dispatch_agents"
    write_json(manifest_path, manifest_payload)


def convert_simulation_to_product_run(run_dir: Path) -> None:
    context = rewrite_context_for_product_run(run_dir)
    rewrite_injections_for_product_run(run_dir, context)
    invocation_refs = rebuild_invocations_from_injections(run_dir)
    remove_simulated_role_outputs(run_dir)
    update_manifest_for_product_run(run_dir, invocation_refs)


def summarize_known(profile: dict[str, Any], context: dict[str, Any]) -> list[str]:
    education = profile.get("education_status", {})
    target = profile.get("target_direction", {})
    known = []
    major = education.get("major_name") or context.get("major_and_discipline", {}).get("normalized_major")
    if major:
        known.append(f"专业方向：{major}")
    degree = education.get("degree_level")
    grade = education.get("grade_or_year")
    if degree or grade:
        known.append("学习阶段：" + "，".join(str(item) for item in [degree, grade] if item))
    skills = list_value(profile.get("skills_and_tools"))
    if skills:
        known.append("已提到技能：" + "、".join(str(skill) for skill in skills[:8]))
    roles = list_value(target.get("target_roles"))
    target_kind = target.get("internship_or_full_time")
    if roles or target_kind:
        parts = [str(item) for item in roles[:4]]
        if target_kind:
            parts.append(str(target_kind))
        known.append("目标倾向：" + "、".join(parts))
    if not known:
        known.append("你已经提供了一段求职相关自我介绍，可以先做初步整理。")
    return known


def can_do_now(context: dict[str, Any]) -> list[str]:
    domain = context.get("discipline_domain", "unknown")
    actions = [
        "先按现有信息判断大致岗位方向和能力补齐顺序。",
        "生成公开岗位信息的搜索计划，优先看官网、公开 JD、学校就业网和地方公开实习渠道。",
        "把简历方向先拆成通用校招/实习版；等有明确岗位后，再做一岗一简历。",
    ]
    if domain != "engineering":
        actions[0] = "当前工程专业数据库最完整，非工科用户只能先做通用框架分析。"
    return actions


def unavailable_now(context: dict[str, Any]) -> list[str]:
    unavailable = [
        "暂时不直接给精确适配分、最终投递优先级或公司定制权重。",
        "没有公开岗位 URL 或 JD 前，不做具体岗位强推荐。",
        "没有项目、实习、竞赛或作品证据前，不把计划中的学习内容写成已完成经历。",
    ]
    if "domain_static_taxonomy" in list_value(context.get("blocked_outputs")):
        unavailable.append("非工科专业的静态专业数据库还没有补齐，不能给同等细度的专业横向对比。")
    return unavailable


def compact_missing_facts(context: dict[str, Any]) -> list[str]:
    labels = {
        "school_name": "学校",
        "degree_level": "学历层次",
        "graduation_window": "毕业时间",
        "project_competition_research_experience": "项目、竞赛或科研经历",
        "internship_experience": "实习经历",
        "target_location_or_company_if_any": "偏好城市、目标公司或暂时不确定",
    }
    missing = []
    for item in list_value(context.get("missing_user_owned_facts")):
        missing.append(labels.get(str(item), str(item)))
    return missing


def next_actions(has_source_results: bool, has_adapter: bool) -> list[str]:
    if has_source_results and has_adapter:
        return [
            "检查公开来源是否能支撑岗位、公司和 HR 信息。",
            "执行各专业角色分析，并保留每一步的证据。",
            "输出最终规划、学习建议、简历方向和公开 URL。",
        ]
    if has_source_results:
        return [
            "先过滤公开 URL，排除登录墙、私有页面和弱来源。",
            "让各专业角色基于这些公开证据分析岗位和能力差距。",
            "确认是否进入具体简历版本设计。",
        ]
    return [
        "补充你愿意一次性提供的个人信息，能提供多少就先提供多少。",
        "系统继续自动查公开岗位和公司信息，不需要你手动列网站。",
        "有了公开岗位证据后，再给具体岗位池、学习路线和简历设计。",
    ]


def markdown_status(status: dict[str, Any]) -> str:
    sections = [
        status["skill_intro"],
        "## 已整理的信息\n" + "\n".join(f"- {item}" for item in status["known_information_summary"]),
        "## 现在可以先做\n" + "\n".join(f"- {item}" for item in status["what_can_be_done_now"]),
        "## 暂时不能做\n" + "\n".join(f"- {item}" for item in status["currently_unavailable"]),
        "## 还缺哪些信息\n" + "\n".join(f"- {item}" for item in status["missing_user_owned_facts"]),
        "## 下一步 3 个动作\n" + "\n".join(f"- {item}" for item in status["next_three_actions"]),
    ]
    return "\n\n".join(sections)


def build_run(args: argparse.Namespace) -> dict[str, Any]:
    route = product_route(args.route, args.task_type)
    simulate_response = response(
        run_python(
            "simulate_runtime_run.py",
            "--task-type",
            args.task_type,
            "--route",
            route,
            "--input-text",
            args.input_text,
            "--run-root",
            str(args.run_root),
        ),
        "runner_response",
        "simulate_runtime_run.py",
    )
    run_id = str(simulate_response.get("run_id") or "")
    if not run_id:
        raise ProductFlowError("simulate_runtime_run.py did not return a run_id")
    run_dir = args.run_root / run_id
    convert_simulation_to_product_run(run_dir)

    plan_response = response(
        run_python("build_subagent_plan.py", "--run-dir", str(run_dir), "--build-prompt-bundles"),
        "planner_response",
        "build_subagent_plan.py",
    )
    source_plan_response = response(
        run_python("build_public_source_plan.py", "--run-dir", str(run_dir)),
        "source_plan_response",
        "build_public_source_plan.py",
    )
    query_plan_response = response(
        run_python("discover_public_sources.py", "--run-dir", str(run_dir), "--generate-query-plan-only"),
        "public_source_discovery_response",
        "discover_public_sources.py",
    )
    work_order_response = response(
        run_python("build_subagent_work_orders.py", "--run-dir", str(run_dir)),
        "work_order_response",
        "build_subagent_work_orders.py",
    )

    collected_ref = ""
    if args.source_notes_md or args.source_url:
        collector_args = ["--run-dir", str(run_dir)]
        if args.source_notes_md:
            collector_args.extend(["--notes-md", str(args.source_notes_md)])
        for url in args.source_url:
            collector_args.extend(["--url", url])
        collection_response = response(
            run_python("collect_public_source_results.py", *collector_args),
            "public_source_result_collection_response",
            "collect_public_source_results.py",
        )
        collected_ref = collection_response.get("search_results_ref", "")

    profile_ref = "input/normalized/first_round_user_profile.json"
    context_ref = "input/normalized/runtime_context_packet.json"
    profile = load_json(run_dir / profile_ref)["first_round_user_profile"]
    context = load_json(run_dir / context_ref)["runtime_context_packet"]

    status = {
        "skill_intro": SKILL_INTRO,
        "known_information_summary": summarize_known(profile, context),
        "what_can_be_done_now": can_do_now(context),
        "currently_unavailable": unavailable_now(context),
        "missing_user_owned_facts": compact_missing_facts(context),
        "public_source_policy": "只使用公开可检查来源；遇到登录墙、验证码、私有页面或无法公开查看的内容，会自动换公开来源，不能验证的结论不会强行给出。",
        "next_three_actions": next_actions(bool(collected_ref), bool(args.adapter_command)),
    }
    status_ref = "final/user_facing_status.md"
    status_json_ref = "final/user_facing_status.json"
    write_text(run_dir / status_ref, markdown_status(status))
    write_json(run_dir / status_json_ref, {"user_facing_status": status})

    handoff = {
        "run_id": run_id,
        "run_dir_ref": str(run_dir),
        "runtime_context_packet_ref": context_ref,
        "subagent_plan_ref": plan_response.get("subagent_plan_ref", ""),
        "work_orders_ref": work_order_response.get("work_orders_ref", ""),
        "dispatch_strategy": "batched_artifact_handoff",
        "public_source_plan_ref": source_plan_response.get("source_plan_ref", ""),
        "public_source_query_plan_ref": query_plan_response.get("discovery_log_ref", ""),
        "controller_collected_search_results_ref": collected_ref,
        "real_role_execution_next": (
            "dispatch work orders by batch with Codex Desktop/Manual Controller or a configured command/API adapter"
        ),
    }
    return {
        "product_flow_response": {
            "exit_status": "needs_real_role_execution",
            "run_id": run_id,
            "user_facing_status": status,
            "user_facing_status_ref": status_ref,
            "user_facing_status_json_ref": status_json_ref,
            "controller_handoff": handoff,
        }
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Start a product-style Career Pipeline flow from plain user text.")
    parser.add_argument("--task-type", default="job_search")
    parser.add_argument("--route", default="job_search")
    parser.add_argument("--input-text", required=True)
    parser.add_argument("--run-root", default=".career-pipeline-runs", type=Path)
    parser.add_argument("--source-notes-md", type=Path)
    parser.add_argument("--source-url", action="append", default=[])
    parser.add_argument("--adapter-command", default="")
    args = parser.parse_args(argv)
    try:
        print(json.dumps(build_run(args), ensure_ascii=False, indent=2))
        return 0
    except (OSError, json.JSONDecodeError, KeyError, ProductFlowError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
