#!/usr/bin/env python
import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[4]


@dataclass(frozen=True)
class Profile:
    profile_id: str
    label: str
    task_type: str
    route: str
    input_text: str
    expected_agents: list[str]
    expected_major_cluster: str
    expected_candidate_stage: str
    needs_hr_guard: bool
    user_next_steps: list[str]
    concise_result: str


PROFILES = [
    Profile(
        profile_id="P01",
        label="本科大二 计算机 AI 实习探索",
        task_type="job_search",
        route="job_search",
        input_text=(
            "Computer science sophomore at a 211 university. Skills: Python, Java, SQL. "
            "Course project: campus RAG FAQ demo. No internship. Looking for AI application "
            "engineer internship, no concrete JD, GitHub has two small repos."
        ),
        expected_agents=[
            "major-cluster-classifier",
            "profile-extractor",
            "job-scout",
            "jd-analyzer",
            "match-strategist",
            "learning-path-strategist",
        ],
        expected_major_cluster="计算机类",
        expected_candidate_stage="non_graduating",
        needs_hr_guard=True,
        user_next_steps=[
            "补一个可演示的 RAG/LLM 小项目，README 写清问题、数据、评测和个人贡献。",
            "整理 Python/Java/SQL 与项目证据，先生成宽口径 AI 应用实习简历。",
            "让用户端 subagent 检索当前 AI 应用实习 JD 后，再决定投递公司和优先级。",
        ],
        concise_result=(
            "可安全给出计算机/AI 软件方向的候选路线和 LLM/RAG 学习补强任务；"
            "具体公司、优先级和 fit score 因缺少当前 JD 与公开证据阻塞。"
        ),
    ),
    Profile(
        profile_id="P02",
        label="本科大四 软件工程 后端校招",
        task_type="target_job_fit",
        route="target_job_fit",
        input_text=(
            "Software engineering senior at a provincial key university. Skills: Java, Spring, "
            "MySQL, Redis, Docker. Internship: local SaaS backend assistant. Assess fit for "
            "Tencent backend development campus role. JD: Java, distributed systems, MySQL, "
            "Redis, high concurrency, engineering practice."
        ),
        expected_agents=[
            "major-cluster-classifier",
            "profile-extractor",
            "jd-analyzer",
            "company-intelligence-analyst",
            "job-scout",
            "match-strategist",
            "learning-path-strategist",
            "hr-supervisor",
            "factual-reviewer",
        ],
        expected_major_cluster="计算机类",
        expected_candidate_stage="graduating",
        needs_hr_guard=True,
        user_next_steps=[
            "把 Java 后端实习拆成接口、数据库、缓存、并发或稳定性四类证据。",
            "补一个可复盘的 Spring/MySQL/Redis 项目指标，避免只写技术名词。",
            "用当前腾讯公开 JD 校验后再做定向简历和投递 readiness 判断。",
        ],
        concise_result=(
            "可把已有 Java 后端证据转成目标岗位准备清单；当前适配、投递时机、"
            "针对腾讯的简历改写仍需当前公开 JD/公司证据验证。"
        ),
    ),
    Profile(
        profile_id="P03",
        label="硕士 电子信息 嵌入式/芯片软件",
        task_type="job_search",
        route="job_search",
        input_text=(
            "Electronic information master year 2 at a double-first-class university. Skills: "
            "C, C++, Python, Linux, STM32, signal processing. Research: edge sensor board. "
            "Target: embedded software or chip software internship. No concrete JD."
        ),
        expected_agents=[
            "major-cluster-classifier",
            "profile-extractor",
            "job-scout",
            "jd-analyzer",
            "match-strategist",
            "learning-path-strategist",
        ],
        expected_major_cluster="电子信息类",
        expected_candidate_stage="non_graduating",
        needs_hr_guard=True,
        user_next_steps=[
            "补 Linux/RTOS/驱动调试记录，把板级项目转成可面试的证据链。",
            "准备嵌入式软件和芯片软件两个方向的关键词版本。",
            "检索目标公司当前嵌入式 JD 后再设置 C/C++、Linux、硬件理解的权重。",
        ],
        concise_result=(
            "可归入电子信息/嵌入式交叉方向，建议补齐 Linux 驱动、RTOS、调试证据；"
            "具体企业要求和权重需要公开 JD 与 HR/候选人公开信号。"
        ),
    ),
    Profile(
        profile_id="P04",
        label="本科大三 自动化 机器人算法",
        task_type="target_job_fit",
        route="target_job_fit",
        input_text=(
            "Automation junior at a strong engineering university. Skills: C++, Python, ROS2, "
            "OpenCV, control basics. Competition: RoboMaster vision module. Target: DJI "
            "robotics algorithm internship. JD: C++, perception, sensor fusion, deployment, "
            "robotics projects."
        ),
        expected_agents=[
            "major-cluster-classifier",
            "profile-extractor",
            "jd-analyzer",
            "company-intelligence-analyst",
            "job-scout",
            "match-strategist",
            "learning-path-strategist",
            "hr-supervisor",
            "factual-reviewer",
        ],
        expected_major_cluster="自动化类",
        expected_candidate_stage="non_graduating",
        needs_hr_guard=True,
        user_next_steps=[
            "把 RoboMaster 视觉模块整理成感知、部署、调参、失败案例四段证据。",
            "补 ROS2/传感器融合或部署 demo，区分当前会什么和准备学什么。",
            "用 DJI 当前公开 JD 验证后再判断适配度和是否现在投递。",
        ],
        concise_result=(
            "可输出自动化/机器人/计算机视觉交叉准备路线；是否适合 DJI 当前实习和"
            "投递优先级必须等待当前 JD 真实性与项目深度证据验证。"
        ),
    ),
    Profile(
        profile_id="P05",
        label="本科大三 机械工程 智能制造转型",
        task_type="learning_plan",
        route="learning_plan",
        input_text=(
            "Mechanical engineering junior at an ordinary undergraduate university. Skills: "
            "SolidWorks, MATLAB, Python basics. Project: fixture design course project. "
            "Wants smart manufacturing, equipment automation, or process engineer internship."
        ),
        expected_agents=[
            "major-cluster-classifier",
            "profile-extractor",
            "job-scout",
            "learning-path-strategist",
        ],
        expected_major_cluster="机械车辆制造类",
        expected_candidate_stage="non_graduating",
        needs_hr_guard=True,
        user_next_steps=[
            "把夹具设计项目补成设计约束、计算/仿真、工艺结果和可视化图纸。",
            "选择 PLC/传感器/数据采集中的一个方向做小型设备自动化 demo。",
            "检索智能制造实习 JD 后再决定机械设计、自动化、数据技能的权重。",
        ],
        concise_result=(
            "可给机械到智能制造的成长型路径，重点是 PLC/传感器/数据采集/工艺项目证据；"
            "不应直接判定岗位优先级。"
        ),
    ),
    Profile(
        profile_id="P06",
        label="硕士 车辆工程 新能源三电",
        task_type="job_search",
        route="job_search",
        input_text=(
            "Vehicle engineering master year 1 at a 985 university. Skills: MATLAB/Simulink, "
            "Python, battery modeling, CAN basics. Research: battery thermal simulation. "
            "Target: new energy vehicle battery or BMS internship at CATL or BYD, no JD."
        ),
        expected_agents=[
            "major-cluster-classifier",
            "profile-extractor",
            "job-scout",
            "jd-analyzer",
            "match-strategist",
            "learning-path-strategist",
        ],
        expected_major_cluster="机械车辆制造类",
        expected_candidate_stage="non_graduating",
        needs_hr_guard=True,
        user_next_steps=[
            "把电池热仿真研究整理成模型假设、参数、验证方式和工程价值。",
            "补 CAN/BMS 或电池数据分析 demo，形成投前证据。",
            "检索 CATL/BYD 当前公开 JD 与学校合作信号后再判断投递策略。",
        ],
        concise_result=(
            "可形成车辆/新能源/BMS 方向研究任务和项目证据建议；目标企业当前要求、"
            "学校合作信号和投递策略需要公开来源。"
        ),
    ),
    Profile(
        profile_id="P07",
        label="博士 材料 成像与电池材料",
        task_type="personal_branding",
        route="personal_branding",
        input_text=(
            "Materials science PhD year 3. Skills: Python data analysis, SEM/TEM, electrochemistry. "
            "Research: battery cathode characterization, two papers under review. Target: battery "
            "materials R&D roles. Has Google Scholar but no personal website."
        ),
        expected_agents=[
            "profile-extractor",
            "personal-branding-strategist",
            "hr-supervisor",
            "factual-reviewer",
        ],
        expected_major_cluster="材料类",
        expected_candidate_stage="non_graduating",
        needs_hr_guard=True,
        user_next_steps=[
            "把论文和表征方法整理成研究问题、方法、结果、个人贡献四块。",
            "完善 Scholar/主页或项目页，只展示已公开、可面试自证的内容。",
            "检索材料 R&D 岗位公开要求后再决定个人网站、论文页、数据分析权重。",
        ],
        concise_result=(
            "可建议把论文、表征方法、数据分析与材料 R&D 证据结构化展示；个人网站/"
            "Scholar 权重必须由目标学科和岗位公开证据决定。"
        ),
    ),
    Profile(
        profile_id="P08",
        label="本科大四 土木 智能建造/BIM",
        task_type="resume_generation",
        route="resume_generation",
        input_text=(
            "Civil engineering senior focused on intelligent construction. Skills: BIM, Revit, "
            "Python basics, project management course. Internship: construction site assistant. "
            "Needs broad campus recruitment resume, no target company."
        ),
        expected_agents=[
            "major-cluster-classifier",
            "profile-extractor",
            "resume-format-gate",
            "resume-architect",
            "factual-reviewer",
            "hr-supervisor",
        ],
        expected_major_cluster="土木建筑类",
        expected_candidate_stage="graduating",
        needs_hr_guard=True,
        user_next_steps=[
            "先生成宽口径校招简历，突出 BIM、现场实习、项目管理和智能建造课程证据。",
            "缺少目标公司时不写定向投递方向，只保留土木/智能建造候选方向。",
            "补学校、毕业时间、项目成果后再进入 ResumeFormatGate 生成正式草稿。",
        ],
        concise_result=(
            "可走宽口径校招简历框架，突出 BIM/现场实习/智能建造证据；因目标公司未知，"
            "不生成定向投递方向。"
        ),
    ),
    Profile(
        profile_id="P09",
        label="硕士 生物医学工程 医疗器械算法",
        task_type="target_job_fit",
        route="target_job_fit",
        input_text=(
            "Biomedical engineering master year 2. Skills: Python, PyTorch, medical image "
            "segmentation, statistics. Research: ultrasound image segmentation. Target: medical "
            "device AI algorithm internship. JD: Python, deep learning, image segmentation, "
            "medical device documentation awareness."
        ),
        expected_agents=[
            "major-cluster-classifier",
            "profile-extractor",
            "jd-analyzer",
            "company-intelligence-analyst",
            "job-scout",
            "match-strategist",
            "learning-path-strategist",
            "hr-supervisor",
            "factual-reviewer",
        ],
        expected_major_cluster="生物医学工程类",
        expected_candidate_stage="non_graduating",
        needs_hr_guard=True,
        user_next_steps=[
            "把超声分割研究整理成数据来源、模型、指标、医学限制和个人贡献。",
            "补医疗器械文档/合规意识的学习证据，避免只写算法。",
            "拿到当前医疗器械算法 JD 和公司公开信息后再判断当前适配与投递时机。",
        ],
        concise_result=(
            "可输出医工/AI 算法交叉学习差距和合规文档意识提示；是否能投具体岗位"
            "还需当前 JD、目标公司和项目证据核验。"
        ),
    ),
    Profile(
        profile_id="P10",
        label="本科大三 环境工程 转 ESG/数据分析",
        task_type="major_positioning",
        route="major_positioning",
        input_text=(
            "Environmental engineering junior. Skills: Python basics, Excel, GIS, environmental "
            "monitoring experiment. Wants to explore ESG data analyst, environmental consulting, "
            "or smart environmental monitoring internship. No internship, no JD."
        ),
        expected_agents=[
            "major-cluster-classifier",
            "profile-extractor",
            "match-strategist",
            "learning-path-strategist",
        ],
        expected_major_cluster="资源环境安全类",
        expected_candidate_stage="non_graduating",
        needs_hr_guard=True,
        user_next_steps=[
            "把环境监测实验转成数据采集、清洗、可视化和业务解释小项目。",
            "在 ESG 数据分析、环保咨询、智慧环保三条方向中各找 3 条公开 JD 做对比。",
            "根据 JD 再决定 Python/GIS/Excel/报告写作的学习权重和简历表达。",
        ],
        concise_result=(
            "可定位环境工程到咨询/ESG/智慧环保的横向比较和补课路线；岗位要求、"
            "数据技能权重、外部展示形式都需用户端 subagent 调研。"
        ),
    ),
]


def run_python(script: str, *args: str) -> dict[str, Any]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / script), *args],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"{script} failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    return json.loads(result.stdout or "{}")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def summarize_profile(profile: Profile, run_dir: Path) -> dict[str, Any]:
    manifest = load_json(run_dir / "manifest.json")
    context = load_json(run_dir / "input" / "normalized" / "runtime_context_packet.json")[
        "runtime_context_packet"
    ]
    blocked = load_json(run_dir / "final" / "blocked_package.json")["blocked_package"]
    plan = load_json(run_dir / "invocations" / "subagent_invocation_plan.json")[
        "subagent_invocation_plan"
    ]
    source_plan = load_json(run_dir / "evidence" / "public_source_research_plan.json")[
        "public_source_research_plan"
    ]
    events_path = run_dir / "logs" / "subagent_execution_events.jsonl"

    agents = [item["target_agent"] for item in plan["dispatch_queue"]]
    missing_expected = [agent for agent in profile.expected_agents if agent not in agents]
    unexpected_agents = [agent for agent in agents if agent not in profile.expected_agents]
    has_prompt_bundles = all(item.get("prompt_bundle_ref") for item in plan["dispatch_queue"])
    blocked_outputs = blocked["blocked_outputs"]
    source_task_count = len(source_plan["research_tasks"])
    major_fact = next(
        (fact["value"] for fact in context["known_user_facts"] if fact["field"] == "major_name"),
        "",
    )
    candidate_stage = context["candidate_stage"]
    has_explicit_hr_supervisor = "hr-supervisor" in agents
    has_factual_reviewer = "factual-reviewer" in agents
    hr_guard_status = (
        "explicit_hr_and_factual"
        if has_explicit_hr_supervisor and has_factual_reviewer
        else "lightweight_hr_guard_required"
        if profile.needs_hr_guard
        else "not_applicable"
    )

    status = "pass"
    issues: list[str] = []
    if missing_expected or unexpected_agents:
        status = "fail"
        issues.append(f"agent route mismatch: missing={missing_expected}, unexpected={unexpected_agents}")
    if manifest["execution_manifest"]["current_stage"] != "blocked":
        status = "fail"
        issues.append("simulation should stay blocked without public evidence")
    if "fit_score" not in blocked_outputs and profile.task_type in {"job_search", "target_job_fit"}:
        status = "partial" if status == "pass" else status
        issues.append("fit_score was not explicitly blocked")
    if not has_prompt_bundles:
        status = "partial" if status == "pass" else status
        issues.append("not all dispatch items have prompt_bundle_ref")
    if source_task_count == 0:
        status = "fail"
        issues.append("public source research plan is empty")
    if not events_path.is_file():
        status = "fail"
        issues.append("dry-run execution log missing")
    if major_fact != profile.expected_major_cluster:
        status = "fail"
        issues.append(
            f"major cluster mismatch: expected={profile.expected_major_cluster}, actual={major_fact}"
        )
    if candidate_stage != profile.expected_candidate_stage:
        status = "fail"
        issues.append(
            f"candidate stage mismatch: expected={profile.expected_candidate_stage}, actual={candidate_stage}"
        )
    if len(profile.user_next_steps) != 3:
        status = "fail"
        issues.append("user-facing next steps must contain exactly three actions")
    user_facing_package = {
        "safe_summary": profile.concise_result,
        "can_do_now": [
            "整理已知经历与缺失材料",
            "给出专业大类、候选方向和成长型准备路线",
            "生成可继续检索的公开来源任务",
        ],
        "blocked_until_evidence": [
            "current_fit_assessment",
            "fit_score",
            "application_priority",
            "application_strategy",
            "company-specific resume tailoring",
        ],
        "not_ready_for_user_output": [
            "精确适配评分",
            "最终投递优先级",
            "公司定制版简历",
        ],
        "ask_hr_about": [
            "岗位是否仍开放",
            "工作城市和到岗方式",
            "实习周期、每周到岗天数和最早到岗时间",
        ],
        "next_three_actions": profile.user_next_steps,
        "hr_supervision_note": (
            "当前结论只基于用户已提供材料和本地规划结果，可用于整理经历与准备方向；不得生成虚假经历、假指标或无证据的强投递结论。"
            f"监督状态：{hr_guard_status}。"
        ),
        "evidence_status": "research_plan_created_not_executed",
        "execution_status": "dry_run_no_real_subagent",
    }

    return {
        "profile_id": profile.profile_id,
        "label": profile.label,
        "task_type": profile.task_type,
        "route": profile.route,
        "run_id": manifest["execution_manifest"]["run_id"],
        "run_dir": str(run_dir),
        "known_user_facts": context["known_user_facts"],
        "missing_user_owned_facts": context["missing_user_owned_facts"],
        "candidate_stage": candidate_stage,
        "discipline_domain": context["discipline_domain"],
        "major_cluster": major_fact,
        "expected_major_cluster": profile.expected_major_cluster,
        "expected_candidate_stage": profile.expected_candidate_stage,
        "target_context": context["target_context"],
        "agents": agents,
        "hr_guard_status": hr_guard_status,
        "research_plan_executed": False,
        "blocked_outputs": blocked_outputs,
        "public_research_task_count": source_task_count,
        "dry_run_events_ref": str(events_path),
        "output_result": profile.concise_result,
        "user_facing_package": user_facing_package,
        "user_next_steps": profile.user_next_steps,
        "status": status,
        "issues": issues,
        "blocked_conclusions": [
            "current fit assessment",
            "fit score",
            "application priority",
            "company-specific resume tailoring",
        ],
        "public_evidence_tasks": [
            task["task_id"] for task in source_plan["research_tasks"][:8]
        ],
    }


def render_markdown(
    summaries: list[dict[str, Any]],
    output_json_path: Path,
    first_thread_note: str,
) -> str:
    pass_count = sum(1 for item in summaries if item["status"] == "pass")
    partial_count = sum(1 for item in summaries if item["status"] == "partial")
    fail_count = sum(1 for item in summaries if item["status"] == "fail")
    lines = [
        "# career-pipeline 工科可靠性烟测",
        "",
        "## 测试方法",
        "",
        "- 本测试只覆盖工科本科生/研究生画像。",
        "- 每个画像均运行 `simulate_runtime_run.py`、`build_subagent_plan.py --build-prompt-bundles`、`build_public_source_plan.py`、`execute_subagent_plan.py --dry-run`。",
        "- 本测试不联网、不登录招聘平台、不爬取真实简历，也不声称真实 subagent 已完成职业判断。",
        "- 公开来源 fetcher 已具备；本烟测默认不联网，只生成研究计划和 work orders，因此这不是最终职业建议报告。",
        "- 没有当前 JD 或公开证据时，fit score、申请优先级、定向简历改写和最终岗位判断必须保持 blocked / needs_more_sources。",
        f"- 后台新对话测试记录：{first_thread_note}",
        f"- 结构化结果：`{output_json_path}`",
        "",
        "## 总览",
        "",
        f"- 画像数：{len(summaries)}",
        f"- pass：{pass_count}",
        f"- partial：{partial_count}",
        f"- fail：{fail_count}",
        "",
        "## 每个画像输出结果",
        "",
    ]
    for item in summaries:
        lines.extend(
            [
                f"### {item['profile_id']} {item['label']}",
                "",
                f"- 状态：`{item['status']}`",
                f"- 任务/路线：`{item['task_type']}` / `{item['route']}`",
                f"- 已知信息：{', '.join(fact['field'] for fact in item['known_user_facts']) or '无可抽取字段'}",
                f"- 缺失信息：{', '.join(item['missing_user_owned_facts'])}",
                f"- 专业域：`{item['discipline_domain'] or 'unknown'}`；大类：`{item['major_cluster'] or 'unknown'}`；阶段：`{item['candidate_stage']}`",
                f"- 用户端可读包：{item['user_facing_package']['safe_summary']}",
                f"- 当前能做：{'; '.join(item['user_facing_package']['can_do_now'])}",
                f"- 当前不能做：{', '.join(item['user_facing_package']['blocked_until_evidence'])}，因为公开来源研究计划已生成但尚未执行。",
                f"- 下一步 1：{item['user_facing_package']['next_three_actions'][0]}",
                f"- 下一步 2：{item['user_facing_package']['next_three_actions'][1]}",
                f"- 下一步 3：{item['user_facing_package']['next_three_actions'][2]}",
                f"- HR/Factual 监督：{item['user_facing_package']['hr_supervision_note']}",
                f"- 调用角色：{', '.join(item['agents'])}",
                f"- 公开证据任务样例：{', '.join(item['public_evidence_tasks'])}",
                f"- run_dir：`{item['run_dir']}`",
                f"- 问题：{'; '.join(item['issues']) if item['issues'] else '未发现契约级问题'}",
                "",
            ]
        )
    lines.extend(
        [
            "## 暴露的问题",
            "",
            "- `career-pipeline` 目前仍是本地契约执行壳，不是真实招聘事实采集器；真实用户端还需要 subagent adapter 和网络来源执行门禁。",
            "- 后台新对话可能在长报告生成前不落盘，可靠性测试应优先使用本脚本做命令级烟测，再用新对话做人工体验测试。",
            "- 若 Codex Desktop 未重启，新增/链接的 user skill 不一定立刻出现在可用技能列表。",
            "- 中文终端在部分 PowerShell 输出里可能显示乱码，但 JSON/Markdown 文件按 UTF-8 写入。",
            "",
        ]
    )
    return "\n".join(lines)


def render_user_report(summaries: list[dict[str, Any]]) -> str:
    lines = [
        "# 工科职业规划测试报告",
        "",
        "这份报告按真实用户视角展示：先给定位结论，再给准备重点和下一步建议。岗位页面未写清的开放状态、城市或到岗要求，统一作为 HR 确认项，不作为推荐阻塞。",
        "",
    ]
    for item in summaries:
        package = item["user_facing_package"]
        lines.extend(
            [
                f"## {item['profile_id']} {item['label']}",
                "",
                f"- 定位结论：{item['major_cluster']}，{item['candidate_stage']}。",
                f"- 推荐判断：{package['safe_summary']}",
                f"- 当前可做：{'; '.join(package['can_do_now'])}。",
                f"- 暂不输出：{'; '.join(package['not_ready_for_user_output'])}。",
                f"- HR 确认项：{'; '.join(package['ask_hr_about'])}。",
                f"- 下一步建议：{package['next_three_actions'][0]}",
                f"- 下一步建议：{package['next_three_actions'][1]}",
                f"- 下一步建议：{package['next_three_actions'][2]}",
                f"- 风险控制：{package['hr_supervision_note']}",
                "",
            ]
        )
    return "\n".join(lines)


def smoke_test(args: argparse.Namespace) -> dict[str, Any]:
    output_dir = Path(args.output_dir)
    run_root = Path(args.run_root) if args.run_root else output_dir / "runs"
    summaries: list[dict[str, Any]] = []

    for profile in PROFILES:
        run_id = f"{args.run_id_prefix}-{profile.profile_id.lower()}"
        run_python(
            "simulate_runtime_run.py",
            "--task-type",
            profile.task_type,
            "--input-text",
            profile.input_text,
            "--run-root",
            str(run_root),
            "--run-id",
            run_id,
            "--route",
            profile.route,
        )
        run_dir = run_root / run_id
        run_python("build_subagent_plan.py", "--run-dir", str(run_dir), "--build-prompt-bundles")
        run_python("build_public_source_plan.py", "--run-dir", str(run_dir))
        run_python("build_subagent_work_orders.py", "--run-dir", str(run_dir))
        run_python("execute_subagent_plan.py", "--run-dir", str(run_dir), "--dry-run")
        summaries.append(summarize_profile(profile, run_dir))

    first_thread_note = (
        "线程 019f0730-ca93-7a33-b736-1d7f366ffc7e 已归档；该线程曾误判脚本目录并长时间未落盘，"
        "因此本烟测改为命令级复现。"
    )
    output = {
        "test_name": "manual-skill-reliability-test-2026-06-27",
        "scope": "engineering_only",
        "network": "disabled",
        "real_subagent_execution": False,
        "profiles": summaries,
        "first_thread_note": first_thread_note,
        "overall": {
            "pass": sum(1 for item in summaries if item["status"] == "pass"),
            "partial": sum(1 for item in summaries if item["status"] == "partial"),
            "fail": sum(1 for item in summaries if item["status"] == "fail"),
        },
    }
    results_json = output_dir / "results.json"
    results_md = output_dir / "results.md"
    user_report = output_dir / "user_report.md"
    write_json(results_json, output)
    write_text(results_md, render_markdown(summaries, results_json, first_thread_note))
    write_text(user_report, render_user_report(summaries))
    return {
        "smoke_test_response": {
            "exit_status": "success" if output["overall"]["fail"] == 0 else "failed",
            "output_dir": str(output_dir),
            "results_md": str(results_md),
            "results_json": str(results_json),
            "user_report": str(user_report),
            "overall": output["overall"],
        }
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run a no-network engineering-only reliability smoke test for career-pipeline."
    )
    parser.add_argument(
        "--output-dir",
        default=str(REPO_ROOT / ".career-pipeline-runs" / "manual-skill-reliability-test-2026-06-27"),
    )
    parser.add_argument("--run-root", default="")
    parser.add_argument("--run-id-prefix", default="engineering-smoke")
    args = parser.parse_args(argv)
    try:
        response = smoke_test(args)
        print(json.dumps(response, ensure_ascii=False, indent=2))
        return 0 if response["smoke_test_response"]["exit_status"] == "success" else 1
    except (OSError, json.JSONDecodeError, KeyError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
