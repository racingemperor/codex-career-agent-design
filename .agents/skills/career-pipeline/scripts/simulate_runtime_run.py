#!/usr/bin/env python
import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


TASK_TYPES = {
    "resume_review",
    "resume_generation",
    "job_search",
    "jd_analysis",
    "company_research",
    "tailored_resume",
    "major_positioning",
    "personal_branding",
    "learning_plan",
    "target_job_fit",
}

ROUTES = {
    "single_job_scout": ["job-scout"],
    "job_search": [
        "major-cluster-classifier",
        "profile-extractor",
        "job-scout",
        "jd-analyzer",
        "match-strategist",
        "learning-path-strategist",
    ],
    "resume_generation": [
        "major-cluster-classifier",
        "profile-extractor",
        "resume-format-gate",
        "resume-architect",
        "factual-reviewer",
        "hr-supervisor",
    ],
    "resume_review": [
        "profile-extractor",
        "resume-format-gate",
        "resume-architect",
        "factual-reviewer",
        "hr-supervisor",
    ],
    "tailored_resume": [
        "profile-extractor",
        "jd-analyzer",
        "company-intelligence-analyst",
        "resume-format-gate",
        "resume-architect",
        "factual-reviewer",
        "hr-supervisor",
    ],
    "company_research": [
        "jd-analyzer",
        "company-intelligence-analyst",
        "market-sentiment-analyzer",
        "hr-supervisor",
    ],
    "personal_branding": [
        "profile-extractor",
        "personal-branding-strategist",
        "hr-supervisor",
        "factual-reviewer",
    ],
    "major_positioning": [
        "major-cluster-classifier",
        "profile-extractor",
        "match-strategist",
        "learning-path-strategist",
    ],
    "learning_plan": [
        "major-cluster-classifier",
        "profile-extractor",
        "job-scout",
        "learning-path-strategist",
    ],
    "target_job_fit": [
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
}

COMPANY_ALIASES = {
    "ByteDance": ["bytedance", "byte dance", "字节", "抖音"],
    "Tencent": ["tencent", "腾讯"],
    "DJI": ["dji", "大疆"],
    "Zhipu": ["zhipu", "智谱"],
    "CATL": ["catl", "宁德时代"],
    "Alibaba": ["alibaba", "阿里"],
    "Baidu": ["baidu", "百度"],
    "Huawei": ["huawei", "华为"],
}

RECRUITMENT_INFORMATION_AGENTS = {
    "job-scout",
    "jd-analyzer",
    "company-intelligence-analyst",
    "market-sentiment-analyzer",
    "hr-supervisor",
}

DEFAULT_RECRUITMENT_SOURCE_MATRIX_REF = (
    "data/company_signals/default_recruitment_source_matrix.zh-CN.json"
)

DEFAULT_PUBLIC_RECRUITMENT_SOURCE_TARGETS = [
    {
        "group_id": "official_primary",
        "priority": 1,
        "source_type": "official_or_primary",
        "display_sources": [
            "公司官方招聘页",
            "公司官方校招页",
            "公司官方实习生招聘页",
            "公司官方微信公众号/视频号招聘公告",
        ],
        "may_set_weight": True,
        "may_set_final_decision": True,
        "requires_login": False,
    },
    {
        "group_id": "school_primary",
        "priority": 1,
        "source_type": "official_school_notice",
        "display_sources": [
            "学校就业信息网",
            "学院官网就业/实习通知",
            "学校双选会/宣讲会日历",
        ],
        "may_set_weight": True,
        "may_set_final_decision": True,
        "requires_login": False,
    },
    {
        "group_id": "public_recruitment_platform",
        "priority": 2,
        "source_type": "recruitment_platform_jd",
        "display_sources": [
            "BOSS直聘公开页",
            "猎聘公开页",
            "拉勾公开页",
            "牛客企业招聘页",
            "实习僧公开页",
            "LinkedIn public job page",
            "Indeed public job page",
        ],
        "may_set_weight": True,
        "may_set_final_decision": True,
        "requires_login": False,
        "degrade_rule": "Skip login-only, app-only, blocked, or non-public candidate data pages.",
    },
    {
        "group_id": "verified_hr_public",
        "priority": 3,
        "source_type": "verified_hr_public_post",
        "display_sources": [
            "已验证大厂 HR 公开账号",
            "官方列名 HR 或招聘官公开帖",
            "企业认证招聘号公开内容",
        ],
        "may_set_weight": True,
        "may_set_final_decision": False,
        "requires_login": False,
        "verification_required": True,
    },
    {
        "group_id": "candidate_experience_secondary",
        "priority": 4,
        "source_type": "candidate_experience_secondary",
        "display_sources": [
            "牛客面经",
            "OfferShow/看准等公开经验",
            "知乎公开经验帖",
            "公开博客复盘",
        ],
        "may_set_weight": True,
        "may_set_final_decision": False,
        "requires_login": False,
        "privacy_rule": "Aggregate and de-identify candidate signals.",
    },
    {
        "group_id": "social_media_weak",
        "priority": 5,
        "source_type": "social_media_weak",
        "display_sources": [
            "小红书公开帖",
            "脉脉公开讨论",
            "知乎公开讨论",
            "公众号公开评论或复盘",
        ],
        "may_set_weight": False,
        "may_set_final_decision": False,
        "requires_login": False,
        "degrade_rule": "Weak signal only; never final basis.",
    },
    {
        "group_id": "public_report",
        "priority": 3,
        "source_type": "public_report",
        "display_sources": [
            "公司财报/招股书",
            "公开行业报告",
            "主流媒体公开报道",
            "公开投融资信息",
            "监管披露",
        ],
        "may_set_weight": True,
        "may_set_final_decision": True,
        "requires_login": False,
    },
]


def automatic_public_recruitment_research(target_agent: str) -> dict[str, Any]:
    return {
        "enabled": target_agent in RECRUITMENT_INFORMATION_AGENTS,
        "user_instruction_required": False,
        "source_matrix_ref": DEFAULT_RECRUITMENT_SOURCE_MATRIX_REF,
        "default_public_recruitment_source_targets": DEFAULT_PUBLIC_RECRUITMENT_SOURCE_TARGETS,
        "forbidden_source_types": [
            "private_resume",
            "private_chat",
            "private_hr_message",
            "recruiter_backend",
            "login_only_page",
            "non_public_candidate_profile",
        ],
        "degrade_when_network_unavailable": (
            "Return runtime_research_tasks and blocked/degraded outputs. Ask only for user-owned "
            "facts or an optional user-provided JD/link, not for a website list."
        ),
    }


def write_json(path: Path, payload: dict[str, Any]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path.as_posix()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def detect_major(text: str) -> str:
    lowered = text.lower()
    if (
        "电子" in text
        or "通信" in text
        or "electronic information" in lowered
        or "electronics" in lowered
        or "communication" in lowered
        or "chip" in lowered
        or "embedded" in lowered
    ):
        return "电子信息类"
    if (
        "机械" in text
        or "车辆" in text
        or "mechanical" in lowered
        or "vehicle" in lowered
        or "automotive" in lowered
        or "manufacturing" in lowered
        or "bms" in lowered
    ):
        return "机械车辆制造类"
    if (
        "计算机" in text
        or "软件" in text
        or "人工智能" in text
        or "computer science" in lowered
        or "software" in lowered
        or "artificial intelligence" in lowered
    ):
        return "计算机类"
    if (
        "自动化" in text
        or "机器人" in text
        or "automation" in lowered
        or "robotics" in lowered
        or "robot" in lowered
    ):
        return "自动化类"
    if "材料" in text or "materials" in lowered or "battery cathode" in lowered:
        return "材料类"
    if (
        "土木" in text
        or "智能建造" in text
        or "civil engineering" in lowered
        or "construction" in lowered
        or "bim" in lowered
    ):
        return "土木建筑类"
    if (
        "生物医学" in text
        or "biomedical" in lowered
        or "medical device" in lowered
        or "medical image" in lowered
    ):
        return "生物医学工程类"
    if (
        "环境工程" in text
        or "environmental engineering" in lowered
        or "environmental monitoring" in lowered
        or "esg" in lowered
    ):
        return "资源环境安全类"
    if "航空" in text or "航天" in text or "aerospace" in lowered:
        return "航空航天类"
    return ""


def detect_discipline_and_major(text: str, engineering_major: str) -> dict[str, Any]:
    lowered = text.lower()
    if engineering_major:
        return {
            "discipline_domain": "engineering",
            "taxonomy_status": "implemented",
            "normalized_major": engineering_major,
            "major_cluster": engineering_major,
        }
    non_engineering_patterns = [
        ("science", "mathematics", ["mathematics", "math", "数学", "统计", "statistics", "physics", "chemistry", "biology"]),
        ("humanities", "humanities", ["literature", "history", "philosophy", "language", "中文", "文学", "历史", "哲学"]),
        ("social_science", "social science", ["sociology", "psychology", "political science", "社会学", "心理学", "政治学"]),
        ("business", "business", ["finance", "accounting", "marketing", "management", "金融", "会计", "市场营销", "工商管理"]),
        ("arts_design", "arts design", ["design", "visual", "animation", "art", "设计", "动画", "美术"]),
        ("medicine_health", "medicine health", ["medicine", "clinical", "pharmacy", "nursing", "医学", "临床", "药学", "护理"]),
        ("agriculture", "agriculture", ["agriculture", "food science", "horticulture", "农学", "食品", "园艺"]),
        ("law_public_affairs", "law public affairs", ["law", "public affairs", "policy", "法学", "公共管理", "政策"]),
    ]
    for domain, normalized_major, tokens in non_engineering_patterns:
        if any(token in lowered or token in text for token in tokens):
            return {
                "discipline_domain": domain,
                "taxonomy_status": "pending_static_database",
                "normalized_major": normalized_major,
                "major_cluster": "",
            }
    return {
        "discipline_domain": "",
        "taxonomy_status": "pending_static_database",
        "normalized_major": "",
        "major_cluster": "",
    }


def detect_candidate_stage(text: str) -> str:
    lowered = text.lower()
    if any(token in text for token in ["大一", "大二", "大三", "研一", "研二", "非毕业"]) or any(
        token in lowered
        for token in [
            "freshman",
            "sophomore",
            "junior",
            "master year 1",
            "master year 2",
            "phd year 1",
            "phd year 2",
            "phd year 3",
            "non-graduating",
        ]
    ):
        return "non_graduating"
    if any(token in text for token in ["大四", "研三", "应届", "毕业"]) or any(
        token in lowered
        for token in ["senior", "master year 3", "phd final", "graduating", "graduate"]
    ):
        return "graduating"
    return "unknown"


def extract_skills(text: str) -> list[str]:
    candidates = ["Python", "Java", "C++", "Go", "SQL", "LLM", "机器学习", "深度学习"]
    lowered = text.lower()
    skills: list[str] = []
    for skill in candidates:
        if skill.lower() in lowered or skill in text:
            skills.append(skill)
    return skills


def detect_target_companies_from_text(text: str) -> list[str]:
    lowered = text.lower()
    companies: list[str] = []
    for canonical, aliases in COMPANY_ALIASES.items():
        if canonical.lower() in lowered or any(alias.lower() in lowered for alias in aliases):
            companies.append(canonical)
    return companies


def extract_jd_excerpt(text: str) -> str:
    match = re.search(r"\b(?:JD|Job Description|Description|Requirements?)\s*[:：]\s*(.+)", text, re.I | re.S)
    excerpt = match.group(1) if match else ""
    if not excerpt and re.search(r"\b(apply|assess fit|target)\b|岗位|实习|internship", text, re.I):
        excerpt = text
    return excerpt.strip()[:500]


def extract_target_job_title(text: str) -> str:
    lowered = text.lower()
    if "no target company" in lowered and "broad campus recruitment resume" in lowered:
        return ""
    patterns = [
        r"(?:apply for|target|assess fit for)\s+(.+?)(?:\.|。|,|，|\bJD\b|:|：)",
        r"想投(?:递)?(.+?)(?:。|，|,|\bJD\b|:|：)",
        r"目标岗位[:：]\s*(.+?)(?:。|，|,|\bJD\b|:|：)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.I | re.S)
        if match:
            title = match.group(1).strip()
            for company in detect_target_companies_from_text(text):
                title = re.sub(re.escape(company), "", title, flags=re.I).strip()
            title = re.sub(r"\s+", " ", title)
            if title:
                return title[:160]
    if "internship" in text.lower():
        return "target internship"
    if "岗位" in text:
        return "target role"
    return ""


def detect_grade_or_year(text: str) -> str:
    lowered = text.lower()
    chinese_tokens = [
        "大一",
        "大二",
        "大三",
        "大四",
        "研一",
        "研二",
        "研三",
        "博一",
        "博二",
        "博三",
    ]
    for token in chinese_tokens:
        if token in text:
            return token
    english_tokens = [
        ("freshman", "本科大一"),
        ("sophomore", "本科大二"),
        ("junior", "本科大三"),
        ("senior", "本科大四"),
        ("master year 1", "硕士一年级"),
        ("master year 2", "硕士二年级"),
        ("master year 3", "硕士三年级"),
        ("phd year 1", "博士一年级"),
        ("phd year 2", "博士二年级"),
        ("phd year 3", "博士三年级"),
    ]
    for needle, label in english_tokens:
        if needle in lowered:
            return label
    return ""


def detect_degree_level(text: str) -> str:
    lowered = text.lower()
    if "phd" in lowered or "博士" in text:
        return "doctor"
    if "master" in lowered or "硕士" in text or "研究生" in text:
        return "master"
    if (
        "undergraduate" in lowered
        or "bachelor" in lowered
        or "freshman" in lowered
        or "sophomore" in lowered
        or "junior" in lowered
        or "senior" in lowered
        or "本科" in text
        or "大一" in text
        or "大二" in text
        or "大三" in text
        or "大四" in text
    ):
        return "bachelor"
    return ""


def detect_target_kind(text: str) -> str:
    lowered = text.lower()
    if "campus role" in lowered or "campus recruitment" in lowered or "校招" in text:
        return "full_time"
    if "internship" in lowered or "实习" in text:
        return "internship"
    return ""


def build_target_context(input_text: str, base_target: dict[str, Any], task_type: str) -> dict[str, Any]:
    target = dict(base_target)
    companies = detect_target_companies_from_text(input_text)
    jd_excerpt = extract_jd_excerpt(input_text)
    title = extract_target_job_title(input_text)
    concrete_requested = task_type == "target_job_fit" or bool(jd_excerpt and (companies or title))
    target_roles = list(target.get("target_roles") or [])
    if title and title not in target_roles:
        target_roles.append(title)
    target_companies = list(target.get("target_companies") or [])
    for company in companies:
        if company not in target_companies:
            target_companies.append(company)
    target.update(
        {
            "target_roles": target_roles,
            "target_companies": target_companies,
            "has_concrete_target": concrete_requested,
            "target_job_fit_requested": task_type == "target_job_fit",
            "target_job_title": title,
            "target_company": target_companies[0] if target_companies else "",
            "current_jd_text_excerpt": jd_excerpt,
            "current_jd_text_ref": "user_provided_chat_excerpt" if jd_excerpt else "",
            "current_jd_public_retrieval_required": not bool(jd_excerpt),
            "current_fit_assessment_status": "blocked_until_current_jd_and_evidence",
            "growth_path_assessment_status": "blocked_until_current_jd_and_gap_evidence",
            "fit_vs_growth_policy": "separate_current_fit_from_learning_path_before_application",
        }
    )
    return target


def redact_contact_like_text(text: str) -> str:
    text = re.sub(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b", "[redacted-email]", text)
    return re.sub(r"(?<!\d)1[3-9]\d{9}(?!\d)", "[redacted-phone]", text)


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def repository_ref(repo_root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(repo_root),
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except OSError:
        pass
    return str(repo_root)


def artifact_ref(
    run_id: str,
    run_dir: Path,
    path: Path,
    artifact_type: str,
    created_by: str,
    privacy_class: str = "derived",
    safe_roles: list[str] | None = None,
    contains_contact: bool = False,
    contains_private_resume: bool = False,
) -> dict[str, Any]:
    content = path.read_bytes() if path.exists() else b""
    checksum = hashlib.sha256(content).hexdigest() if content else ""
    return {
        "artifact_id": f"{artifact_type}:{path.stem}",
        "run_id": run_id,
        "artifact_type": artifact_type,
        "path": rel(path, run_dir),
        "created_by": created_by,
        "created_at": utc_now(),
        "privacy_class": privacy_class,
        "contains_contact": contains_contact,
        "contains_private_resume": contains_private_resume,
        "safe_to_share_with_roles": safe_roles or [],
        "checksum": checksum,
        "retention": "runtime_only",
        "purge_after_days": None,
    }


def build_profile(input_text: str, task_type: str = "") -> dict[str, Any]:
    major_name = detect_major(input_text)
    discipline = detect_discipline_and_major(input_text, major_name)
    candidate_stage = detect_candidate_stage(input_text)
    skills = extract_skills(input_text)
    target_roles = ["AI 实习"] if re.search(r"AI|人工智能|大模型|LLM", input_text, re.I) else []
    target_kind = detect_target_kind(input_text)
    return {
        "identity_and_contact": {
            "name_or_preferred_label": "",
            "contact_fields_for_final_resume": {},
            "resume_contact_fields_authorized": False,
            "redaction_required_for_intermediate_outputs": True,
        },
        "education_status": {
            "school_name": "",
            "college_or_department": "",
            "major_name": major_name,
            "degree_level": detect_degree_level(input_text),
            "grade_or_year": detect_grade_or_year(input_text),
            "graduation_window": "",
            "education_status": candidate_stage,
        },
        "major_and_discipline": {
            "discipline_domain": discipline["discipline_domain"],
            "taxonomy_status": discipline["taxonomy_status"],
            "normalized_major": discipline["normalized_major"],
            "major_cluster": discipline["major_cluster"],
        },
        "internship_experience": [],
        "project_competition_research_experience": [],
        "skills_and_tools": skills,
        "external_assets": [],
        "target_direction": {
            "target_roles": target_roles,
            "target_companies": [],
            "target_industries": [],
            "target_locations": [],
            "internship_or_full_time": target_kind,
        },
        "preferences_constraints": [],
        "current_concerns": [],
        "materials_provided": [{"type": "chat_brief", "description": "first-round user text"}],
    }


def build_context_packet(
    run_id: str,
    profile_ref: str,
    context_ref: str,
    profile: dict[str, Any],
    task_type: str,
) -> dict[str, Any]:
    known_user_facts = []
    education = profile["education_status"]
    major_and_discipline = profile["major_and_discipline"]
    if education["major_name"]:
        known_user_facts.append({"field": "major_name", "value": education["major_name"]})
    if education["grade_or_year"]:
        known_user_facts.append({"field": "grade_or_year", "value": education["grade_or_year"]})
    for skill in profile["skills_and_tools"]:
        known_user_facts.append({"field": "skill", "value": skill})

    missing_user_owned_facts = [
        "school_name",
        "degree_level",
        "graduation_window",
        "project_competition_research_experience",
        "internship_experience",
        "target_location_or_company_if_any",
    ]
    public_research_needed = [
        {
            "research_question": "Collect current public JD and company evidence before role-specific recommendations.",
            "target_sources": [
                "official company career pages",
                "public recruitment platform JDs",
                "official school career center notices",
            ],
            "needed_for_outputs": ["application_direction", "runtime_weights", "resume_tailoring"],
        }
    ]
    blocked_outputs = [
        "application_direction",
        "final_resume_draft",
        "fit_score",
        "application_strategy",
        "application_priority",
    ]
    if major_and_discipline.get("taxonomy_status") == "pending_static_database":
        blocked_outputs.append("domain_static_taxonomy")
    next_possible_actions = [
        "Ask user once for missing user-owned facts.",
        "Run public research subagents for current JD/company/school evidence.",
        "Keep final recommendations blocked until required evidence exists.",
    ]
    target_context = profile["target_direction"]
    if task_type == "target_job_fit":
        public_research_needed.extend(
            [
                {
                    "research_question": "Verify the concrete target JD from user-provided text or current public JD sources before fit assessment.",
                    "target_sources": [
                        "official company career page",
                        "public recruitment platform JD",
                        "user-provided JD text or link",
                    ],
                    "needed_for_outputs": [
                        "current_fit_assessment",
                        "application_readiness_decision",
                        "resume_tailoring",
                    ],
                },
                {
                    "research_question": "Collect target-role skill and evidence expectations before recommending learning gaps or projects.",
                    "target_sources": [
                        "current JD requirements",
                        "verified HR public posts",
                        "official company campus pages",
                        "public role-family reports",
                    ],
                    "needed_for_outputs": [
                        "skill_gap_analysis",
                        "learning_plan_before_application",
                        "project_evidence_requirements",
                    ],
                },
            ]
        )
        blocked_outputs = [
            "current_fit_assessment",
            "application_readiness_decision",
            "application_direction",
            "learning_plan_before_application",
            "targeted_resume_tailoring",
            "final_resume_draft",
            "fit_score",
            "application_strategy",
            "application_priority",
        ]
        next_possible_actions = [
            "Summarize the candidate facts and concrete target job currently known.",
            "Verify or retrieve the current JD and target-company evidence.",
            "Separate immediate fit from learnable gaps and preparation before application.",
            "Keep application readiness and targeted resume advice blocked until JD evidence exists.",
        ]
    return {
        "packet_id": f"{run_id}-context",
        "artifact_ref": context_ref,
        "context_packet_version": "0.1",
        "created_from": "first_round_user_profile",
        "first_round_user_profile_ref": profile_ref,
        "user_goal": "simulate local runtime contract without network or real subagent execution",
        "task_type": task_type,
        "known_user_facts": known_user_facts,
        "candidate_stage": profile["education_status"]["education_status"],
        "discipline_domain": major_and_discipline.get("discipline_domain", ""),
        "major_and_discipline": major_and_discipline,
        "school_context": {
            "school_name": education["school_name"],
            "major_name": education["major_name"],
            "grade_or_year": education["grade_or_year"],
            "school_signal_research_needed": ["official school-company cooperation evidence"],
        },
        "target_context": target_context,
        "provided_materials": profile["materials_provided"],
        "missing_user_owned_facts": missing_user_owned_facts,
        "public_research_needed": public_research_needed,
        "runtime_weight_questions": [
            "skill_weight",
            "external_asset_weight",
            "school_signal_weight",
            "application_strategy_weight",
            "hr_screening_weight",
        ],
        "privacy_constraints": ["redact_contact_fields", "do_not_copy_private_resume_to_shared_context"],
        "consent_flags": {"incomplete_resume_consent": False},
        "blocked_outputs": blocked_outputs,
        "next_possible_actions": next_possible_actions,
    }


def build_injection(
    run_id: str,
    target_agent: str,
    context_ref: str,
    injection_ref: str,
    input_packet_ref: str,
    allowed_user_facts_ref: str,
    output_ref: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    base_prompt_ref = f".codex/agents/{target_agent}.toml"
    target_context = (context or {}).get("target_context", {})
    target_job_fit_requested = bool(target_context.get("target_job_fit_requested"))
    role_specific_context = {
        "simulation_scope": "contract_only_no_network_no_real_subagent",
        "must_return_blockers_instead_of_final_judgment": True,
        "target_job_fit_assessment_requested": target_job_fit_requested,
        "distinguish_current_fit_from_growth_path": target_job_fit_requested,
        "final_fit_requires_current_jd_public_evidence": target_job_fit_requested,
    }
    auto_recruitment_research = automatic_public_recruitment_research(target_agent)
    if auto_recruitment_research["enabled"]:
        role_specific_context["automatic_public_recruitment_research"] = auto_recruitment_research
    research_tasks = [
        {
            "research_question": "Gather current public JD/company/school evidence before setting fit or priority.",
            "target_sources": [
                "official company career pages",
                "public recruitment platform JDs",
                "official school notices",
            ],
            "required_freshness": "0_6_months preferred; otherwise mark weak or stale",
            "needed_for_outputs": ["runtime_weights", "application_strategy"],
        }
    ]
    if auto_recruitment_research["enabled"]:
        research_tasks.insert(
            0,
            {
                "research_question": "Automatically collect recruitment information from the default public recruitment source matrix; do not wait for the user to name websites.",
                "source_matrix_ref": DEFAULT_RECRUITMENT_SOURCE_MATRIX_REF,
                "user_instruction_required": False,
                "target_sources": [
                    source
                    for group in DEFAULT_PUBLIC_RECRUITMENT_SOURCE_TARGETS
                    for source in group["display_sources"]
                ],
                "source_priority_order": [
                    "official_or_primary",
                    "official_school_notice",
                    "recruitment_platform_jd",
                    "verified_hr_public_post",
                    "candidate_experience_secondary",
                    "social_media_weak",
                    "public_report",
                ],
                "forbidden_source_types": auto_recruitment_research["forbidden_source_types"],
                "required_freshness": "0_6_months preferred; otherwise mark weak or stale",
                "needed_for_outputs": [
                    "current_jd_text",
                    "skill_weight",
                    "company_signal",
                    "hr_screening_signal",
                    "market_sentiment",
                ],
            },
        )
    hard_data_weight_tasks = [
        {
            "parameter": "skill_weight",
            "rule": "verified only with current JD or public official evidence; otherwise not_available",
        }
    ]
    required_output_fields = [
        "role_output_packet",
        "error_recovery_state",
        "blocked_outputs",
        "runtime_research_tasks",
    ]
    blocked_outputs = ["fit_score", "application_strategy", "final_resume_draft"]
    handoff_contract = ["return blockers to CareerOrchestrator"]
    debate_contract = ["challenge unsupported weights instead of creating scores"]

    if target_job_fit_requested:
        research_tasks.extend(
            [
                {
                    "research_question": "Verify the concrete target JD from user text, user link, or current public JD sources before judging current fit.",
                    "target_sources": [
                        "user-provided JD text or link",
                        "official company career page",
                        "public recruitment platform JD",
                    ],
                    "required_freshness": "current JD or mark stale/weak",
                    "needed_for_outputs": [
                        "current_fit_assessment",
                        "application_readiness_decision",
                        "targeted_resume_tailoring",
                    ],
                },
                {
                    "research_question": "Find evidence-backed skill, project, and portfolio gaps needed to improve success for this exact target role.",
                    "target_sources": [
                        "current JD requirements",
                        "verified HR public posts",
                        "official company campus pages",
                        "public role-family reports",
                    ],
                    "required_freshness": "0_6_months preferred; otherwise mark weak or stale",
                    "needed_for_outputs": [
                        "skill_gap_analysis",
                        "learning_plan_before_application",
                        "project_evidence_requirements",
                    ],
                },
            ]
        )
        hard_data_weight_tasks.extend(
            [
                {
                    "parameter": "current_fit_assessment_weight",
                    "rule": "fit/readiness must be supported by current JD plus user evidence; otherwise not_available",
                },
                {
                    "parameter": "learning_gap_priority",
                    "rule": "gap priorities must be grounded in JD/company/HR evidence, not model intuition",
                },
                {
                    "parameter": "application_readiness_decision",
                    "rule": "apply-now, prepare-first, or skip decisions require current JD and public evidence",
                },
            ]
        )
        required_output_fields.extend(
            [
                "current_fit_assessment",
                "skill_gap_analysis",
                "learning_plan_before_application",
                "evidence_requirements",
            ]
        )
        blocked_outputs = [
            "current_fit_assessment",
            "application_readiness_decision",
            "fit_score",
            "application_strategy",
            "learning_plan_before_application",
            "targeted_resume_tailoring",
            "final_resume_draft",
        ]
        handoff_contract.extend(
            [
                "handoff current-fit gaps to LearningPathStrategist",
                "handoff unsupported fit claims to HRSupervisor and FactualReviewer",
            ]
        )
        debate_contract.extend(
            [
                "separate current readiness from future growth potential",
                "challenge any apply-now recommendation without current JD evidence",
            ]
        )

    database_files_to_read = [
        "data/runtime_parameters/parameter_ownership.zh-CN.json",
        "data/major_taxonomy/summary.json",
        "data/company_signals/summary.json",
    ]
    if auto_recruitment_research["enabled"]:
        database_files_to_read.append(DEFAULT_RECRUITMENT_SOURCE_MATRIX_REF)
    return {
        "target_agent": target_agent,
        "base_prompt_ref": base_prompt_ref,
        "runtime_context_packet_ref": context_ref,
        "role_specific_context": role_specific_context,
        "allowed_user_facts": ["major_name", "grade_or_year", "skills_and_tools", "target_direction"],
        "research_tasks": research_tasks,
        "hard_data_weight_tasks": hard_data_weight_tasks,
        "database_files_to_read": database_files_to_read,
        "source_policy_refs": [".agents/skills/career-pipeline/references/source-policy.md"],
        "invocation_contract": {
            "invocation_id": f"{run_id}-{target_agent}",
            "run_id": run_id,
            "target_agent": target_agent,
            "base_prompt_ref": base_prompt_ref,
            "secondary_prompt_injection_ref": injection_ref,
            "runtime_context_packet_ref": context_ref,
            "input_packet_ref": input_packet_ref,
            "allowed_user_facts_ref": allowed_user_facts_ref,
            "database_files_to_read": database_files_to_read,
            "source_policy_refs": [".agents/skills/career-pipeline/references/source-policy.md"],
            "research_tasks": research_tasks,
            "hard_data_weight_tasks": hard_data_weight_tasks,
            "required_output_fields": required_output_fields,
            "output_artifact_target": output_ref,
            "privacy_constraints": ["redact_contact_fields", "share_only_allowed_user_facts"],
            "handoff_contract": handoff_contract,
            "debate_contract": debate_contract,
            "expected_artifact_types": ["subagent_output", "evidence_packet", "redacted_log"],
            "required_log_events": ["dispatch", "receive_output", "validate_output"],
            "timeout_or_budget_hint": "simulation-no-dispatch",
            "retry_allowed": True,
            "on_failure": "return_blocked",
            "status": "not_started",
        },
        "blocked_outputs": blocked_outputs,
        "required_output_fields": required_output_fields,
        "handoff_contract": handoff_contract,
        "debate_contract": debate_contract,
    }


def build_invocation(injection: dict[str, Any]) -> dict[str, Any]:
    contract = dict(injection["invocation_contract"])
    return {"subagent_invocation": contract}


def build_input_packet(
    run_id: str,
    target_agent: str,
    context_ref: str,
    injection_ref: str,
) -> dict[str, Any]:
    return {
        "input_packet": {
            "run_id": run_id,
            "target_agent": target_agent,
            "runtime_context_packet_ref": context_ref,
            "secondary_prompt_injection_ref": injection_ref,
            "prompt_composition_order": [
                "static role prompt",
                "runtime context packet reference",
                "secondary prompt injection",
                "minimum database subset",
                "source/privacy/weight/debate rules",
                "required output schema",
            ],
            "simulation_note": "No real subagent is dispatched by this script.",
        }
    }


def simulate(args: argparse.Namespace) -> dict[str, Any]:
    if args.task_type not in TASK_TYPES:
        raise ValueError(f"unsupported task type: {args.task_type}")

    repo_root = Path(__file__).resolve().parents[4]
    run_id = args.run_id or f"run-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:8]}"
    run_root = Path(args.run_root)
    run_dir = run_root / run_id
    created_at = utc_now()

    profile = build_profile(args.input_text, args.task_type)
    profile["target_direction"] = build_target_context(
        args.input_text,
        profile.get("target_direction", {}),
        args.task_type,
    )

    raw_ref_path = run_dir / "input" / "raw_refs.json"
    profile_path = run_dir / "input" / "normalized" / "first_round_user_profile.json"
    context_path = run_dir / "input" / "normalized" / "runtime_context_packet.json"

    write_json(
        raw_ref_path,
        {
            "raw_input_refs": [
                {
                    "input_id": "first-round-chat",
                    "input_type": "chat_brief",
                    "storage": "inline_excerpt_for_simulation",
                    "redaction_applied": True,
                    "excerpt": redact_contact_like_text(args.input_text[:240]),
                }
            ]
        },
    )
    write_json(profile_path, {"first_round_user_profile": profile})
    context_ref = rel(context_path, run_dir)
    profile_ref = rel(profile_path, run_dir)
    context = build_context_packet(run_id, profile_ref, context_ref, profile, args.task_type)
    write_json(context_path, {"runtime_context_packet": context})

    target_agents = ROUTES[args.route]
    injection_paths: list[Path] = []
    invocation_paths: list[Path] = []
    generated_role_output_paths: list[tuple[str, Path]] = []

    for target_agent in target_agents:
        injection_path = run_dir / "injections" / f"{target_agent}.secondary_prompt_injection.json"
        input_packet_path = run_dir / "invocations" / f"{target_agent}.input_packet.json"
        allowed_facts_path = run_dir / "invocations" / f"{target_agent}.allowed_user_facts.json"
        invocation_path = run_dir / "invocations" / f"{target_agent}.invocation.json"
        role_output_path = run_dir / "agents" / target_agent / "output.json"

        injection = build_injection(
            run_id,
            target_agent,
            context_ref,
            rel(injection_path, run_dir),
            rel(input_packet_path, run_dir),
            rel(allowed_facts_path, run_dir),
            rel(role_output_path, run_dir),
            context,
        )
        write_json(injection_path, {"secondary_prompt_injection": injection})
        write_json(input_packet_path, build_input_packet(run_id, target_agent, context_ref, rel(injection_path, run_dir)))
        write_json(
            allowed_facts_path,
            {
                "allowed_user_facts": [
                    fact
                    for fact in context["known_user_facts"]
                    if fact["field"] in {"major_name", "grade_or_year", "skill"}
                ]
            },
        )
        invocation = build_invocation(injection)
        write_json(invocation_path, invocation)

        role_output = {
            "invocation_ref": rel(invocation_path, run_dir),
            "role_output_packet": {
                "invocation_id": invocation["subagent_invocation"]["invocation_id"],
                "target_agent": target_agent,
                "status": "blocked",
                "role_output_ref": rel(role_output_path, run_dir),
                "evidence_packet_refs": [],
                "runtime_weights_ref": "merge/runtime_weights.json",
                "artifact_refs": [],
                "blocked_outputs": context["blocked_outputs"],
                "runtime_research_tasks": context["public_research_needed"],
                "needs_user_confirmation": context["missing_user_owned_facts"],
                "handoff_to": ["career-orchestrator"],
                "errors": [
                    {
                        "category": "missing_user_fact",
                        "severity": "blocking",
                        "message": "Simulation keeps user-owned facts and public evidence incomplete.",
                    }
                ],
                "confidence": "low",
            },
            "error_recovery_state": {
                "status": "blocked",
                "errors": [
                    {
                        "category": "missing_user_fact",
                        "severity": "blocking",
                        "message": "Simulation keeps user-owned facts and public evidence incomplete.",
                    }
                ],
                "recovery_actions": ["ask_user_once", "run_public_research"],
                "degraded_outputs": ["known_information_summary"],
                "blocked_outputs": context["blocked_outputs"],
                "safe_outputs": ["runtime_research_tasks", "needs_user_confirmation"],
                "next_action": "return_blocked_package",
            },
        }
        write_json(role_output_path, role_output)
        injection_paths.append(injection_path)
        invocation_paths.append(invocation_path)
        generated_role_output_paths.append((target_agent, role_output_path))

    runtime_weights_path = run_dir / "merge" / "runtime_weights.json"
    write_json(
        runtime_weights_path,
        {
            "runtime_weights": [
                {
                    "parameter": "skill_weight",
                    "weight_scope": "skill_weight",
                    "proposed_weight": None,
                    "weight_unit": "qualitative",
                    "weight_status": "not_available",
                    "evidence_basis": [],
                    "source_count": 0,
                    "source_mix": [],
                    "freshness": "unknown",
                    "conflict_notes": ["No network or real subagent research ran in simulation mode."],
                    "confidence": "low",
                    "cannot_decide_alone": True,
                    "runtime_research_tasks": context["public_research_needed"],
                }
            ]
        },
    )

    error_path = run_dir / "merge" / "error_recovery_state.json"
    error_recovery_state = {
        "error_recovery_state": {
            "status": "blocked",
            "errors": [
                {
                    "runtime_error": {
                        "error_id": f"{run_id}-missing-user-facts",
                        "run_id": run_id,
                        "stage": "blocked",
                        "agent": "career-orchestrator",
                        "category": "missing_user_fact",
                        "severity": "blocking",
                        "affected_outputs": [
                            output
                            for output in context["blocked_outputs"]
                            if output in {"final_resume_draft", "application_direction", "targeted_resume_tailoring"}
                        ],
                        "evidence_or_artifact_refs": [context_ref],
                        "message": "Required user-owned facts are missing.",
                        "recovery_action": "ask_user_once",
                        "owner": "user",
                        "retry_count": 0,
                        "resolved": False,
                    }
                },
                {
                    "runtime_error": {
                        "error_id": f"{run_id}-missing-public-evidence",
                        "run_id": run_id,
                        "stage": "blocked",
                        "agent": "job-scout",
                        "category": "unsupported_weight",
                        "severity": "blocking",
                        "affected_outputs": [
                            output
                            for output in context["blocked_outputs"]
                            if output
                            in {
                                "fit_score",
                                "application_strategy",
                                "current_fit_assessment",
                                "application_readiness_decision",
                                "learning_plan_before_application",
                            }
                        ],
                        "evidence_or_artifact_refs": [],
                        "message": "Runtime weights cannot be set without current public or user-provided evidence.",
                        "recovery_action": "research_public_source",
                        "owner": "local_subagent",
                        "retry_count": 0,
                        "resolved": False,
                    }
                },
            ],
            "recovery_actions": ["ask_user_once", "run_public_research"],
            "degraded_outputs": ["known_information_summary"],
            "blocked_outputs": ["missing_user_facts", "public_research_required"] + context["blocked_outputs"],
            "safe_outputs": ["first_round_user_profile", "runtime_context_packet", "subagent_invocation_plan"],
            "next_action": "return_blocked_package",
        }
    }
    write_json(error_path, error_recovery_state)

    blocked_path = run_dir / "final" / "blocked_package.json"
    blocked_package = {
        "blocked_package": {
            "run_id": run_id,
            "blocked_outputs": ["missing_user_facts", "public_research_required"] + context["blocked_outputs"],
            "safe_outputs": [
                "known user facts can be summarized",
                "public research tasks can be handed to runtime subagents",
                "resume draft remains blocked until consent and evidence gates pass",
            ],
            "missing_user_owned_facts": context["missing_user_owned_facts"],
            "public_research_tasks": context["public_research_needed"],
            "consent_requests": ["incomplete_resume_consent if the user refuses missing facts"],
            "failed_agents": [],
            "source_conflicts": [],
            "next_possible_actions": context["next_possible_actions"],
        }
    }
    write_json(blocked_path, blocked_package)

    manifest_path = run_dir / "manifest.json"
    artifact_refs = [
        artifact_ref(
            run_id,
            run_dir,
            raw_ref_path,
            "raw_input_ref",
            "simulate_runtime_run",
            "user_private",
            contains_contact=True,
            contains_private_resume=True,
        ),
        artifact_ref(
            run_id,
            run_dir,
            profile_path,
            "normalized_profile",
            "input-normalizer",
            "user_private",
            contains_private_resume=True,
        ),
        artifact_ref(
            run_id,
            run_dir,
            context_path,
            "runtime_context_packet",
            "input-normalizer",
            "user_private",
            contains_private_resume=True,
        ),
        artifact_ref(run_id, run_dir, runtime_weights_path, "merge_result", "career-orchestrator"),
        artifact_ref(run_id, run_dir, error_path, "merge_result", "career-orchestrator"),
        artifact_ref(run_id, run_dir, blocked_path, "final_package", "career-orchestrator"),
    ]
    for path in injection_paths:
        artifact_refs.append(artifact_ref(run_id, run_dir, path, "secondary_prompt_injection", "career-orchestrator"))
    for path in invocation_paths:
        artifact_refs.append(artifact_ref(run_id, run_dir, path, "subagent_input", "career-orchestrator"))
    for target_agent, path in generated_role_output_paths:
        artifact_refs.append(artifact_ref(run_id, run_dir, path, "subagent_output", target_agent))

    manifest = {
        "execution_manifest": {
            "run_id": run_id,
            "created_at": created_at,
            "updated_at": utc_now(),
            "codex_surface": "desktop",
            "repository_ref": repository_ref(repo_root),
            "skill_ref": ".agents/skills/career-pipeline/SKILL.md",
            "task_type": args.task_type,
            "user_goal_summary": "local simulation of career pipeline runtime contracts",
            "privacy_mode": "redacted_intermediate",
            "run_dir_ref": str(run_dir),
            "current_stage": "blocked",
            "runtime_context_packet_ref": context_ref,
            "secondary_prompt_injection_refs": [rel(path, run_dir) for path in injection_paths],
            "subagent_invocation_refs": [rel(path, run_dir) for path in invocation_paths],
            "artifact_manifest_ref": "manifest.json",
            "artifact_refs": artifact_refs,
            "evidence_packet_refs": [],
            "runtime_weights_ref": rel(runtime_weights_path, run_dir),
            "gate_status": {
                "input_normalized": True,
                "context_packet_created": True,
                "secondary_injections_created": True,
                "specialists_completed_or_blocked": True,
                "debate_completed_or_recorded": False,
                "hr_review_completed": False,
                "factual_review_completed_when_needed": False,
                "user_confirmation_resolved_when_needed": False,
            },
            "error_recovery_state_ref": rel(error_path, run_dir),
            "final_package_ref": "",
        },
        "run_state": {
            "run_id": run_id,
            "stage": "blocked",
            "task_type": args.task_type,
            "runtime_context_packet_ref": context_ref,
            "secondary_prompt_injection_refs": [rel(path, run_dir) for path in injection_paths],
            "subagent_invocation_refs": [rel(path, run_dir) for path in invocation_paths],
            "active_agents": [],
            "completed_agents": [],
            "blocked_agents": target_agents,
            "failed_invocations": [],
            "artifact_manifest_ref": "manifest.json",
            "shared_context_refs": [context_ref],
            "evidence_packet_refs": [],
            "execution_log_refs": [],
            "debate_topics": [],
            "user_confirmation_points": context["missing_user_owned_facts"],
            "blocked_outputs": blocked_package["blocked_package"]["blocked_outputs"],
            "degraded_outputs": ["known_information_summary"],
            "recovery_actions": ["ask_user_once", "run_public_research"],
            "next_action": "return_blocked",
        },
    }
    write_json(manifest_path, manifest)

    return {
        "runner_response": {
            "exit_status": "blocked",
            "run_id": run_id,
            "execution_manifest_ref": str(manifest_path),
            "final_package_ref": "",
            "blocked_package_ref": str(blocked_path),
            "error_recovery_state_ref": str(error_path),
        }
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Simulate a local career-pipeline runtime run.")
    parser.add_argument("--task-type", default="resume_generation", choices=sorted(TASK_TYPES))
    parser.add_argument("--input-text", required=True)
    parser.add_argument("--run-root", default=".career-pipeline-runs")
    parser.add_argument("--run-id", default="")
    parser.add_argument("--route", default="single_job_scout", choices=sorted(ROUTES))
    args = parser.parse_args(argv)
    try:
        response = simulate(args)
        print(json.dumps(response, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
