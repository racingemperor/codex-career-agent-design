import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / ".agents" / "skills" / "career-pipeline" / "scripts" / "validate_runtime_contracts.py"
SIMULATOR = ROOT / ".agents" / "skills" / "career-pipeline" / "scripts" / "simulate_runtime_run.py"
PLAN_BUILDER = ROOT / ".agents" / "skills" / "career-pipeline" / "scripts" / "build_subagent_plan.py"
PLAN_EXECUTOR = ROOT / ".agents" / "skills" / "career-pipeline" / "scripts" / "execute_subagent_plan.py"
RUN_CONTINUER = ROOT / ".agents" / "skills" / "career-pipeline" / "scripts" / "continue_runtime_run.py"
PROMPT_BUNDLE_BUILDER = ROOT / ".agents" / "skills" / "career-pipeline" / "scripts" / "build_subagent_prompt_bundle.py"
SOURCE_PLAN_BUILDER = ROOT / ".agents" / "skills" / "career-pipeline" / "scripts" / "build_public_source_plan.py"
SKILL_MD = ROOT / ".agents" / "skills" / "career-pipeline" / "SKILL.md"
RUNTIME_EXECUTION_LAYER = (
    ROOT / ".agents" / "skills" / "career-pipeline" / "references" / "runtime-execution-layer.md"
)
RUNTIME_NETWORK_ADAPTER_SETUP = (
    ROOT
    / ".agents"
    / "skills"
    / "career-pipeline"
    / "references"
    / "runtime-network-and-adapter-setup.md"
)
CODEX_DESKTOP_SUBAGENT_ADAPTER = (
    ROOT
    / ".agents"
    / "skills"
    / "career-pipeline"
    / "references"
    / "codex-desktop-subagent-adapter.md"
)
ENGINEERING_SMOKE = ROOT / ".agents" / "skills" / "career-pipeline" / "scripts" / "smoke_test_engineering_profiles.py"
WORK_ORDER_BUILDER = ROOT / ".agents" / "skills" / "career-pipeline" / "scripts" / "build_subagent_work_orders.py"
EVIDENCE_BACKFILL = ROOT / ".agents" / "skills" / "career-pipeline" / "scripts" / "backfill_public_evidence.py"
PUBLIC_SOURCE_FETCHER = ROOT / ".agents" / "skills" / "career-pipeline" / "scripts" / "fetch_public_sources.py"
PUBLIC_SOURCE_DISCOVERER = (
    ROOT / ".agents" / "skills" / "career-pipeline" / "scripts" / "discover_public_sources.py"
)
PUBLIC_SOURCE_SEARCHER = ROOT / ".agents" / "skills" / "career-pipeline" / "scripts" / "search_public_sources.py"
PUBLIC_SOURCE_RESULT_COLLECTOR = (
    ROOT / ".agents" / "skills" / "career-pipeline" / "scripts" / "collect_public_source_results.py"
)
SUBAGENT_ADAPTER_RUNNER = ROOT / ".agents" / "skills" / "career-pipeline" / "scripts" / "run_subagent_adapter.py"
CAREER_PIPELINE_RUNNER = ROOT / ".agents" / "skills" / "career-pipeline" / "scripts" / "career_pipeline_run.py"
PRODUCT_FLOW_RUNNER = ROOT / ".agents" / "skills" / "career-pipeline" / "scripts" / "run_product_flow.py"
FINALIZER = ROOT / ".agents" / "skills" / "career-pipeline" / "scripts" / "finalize_runtime_run.py"
RESUME_RENDERER = ROOT / ".agents" / "skills" / "career-pipeline" / "scripts" / "render_resume_artifacts.py"
INCOMPLETE_USER_MANUAL_OUTPUTS = (
    ROOT
    / ".agents"
    / "skills"
    / "career-pipeline"
    / "scripts"
    / "build_incomplete_user_manual_outputs.py"
)
PROJECT_CANDIDATE_DISCOVERER = (
    ROOT / ".agents" / "skills" / "career-pipeline" / "scripts" / "discover_project_candidates.py"
)
PROJECT_REPO_AUDITOR = (
    ROOT / ".agents" / "skills" / "career-pipeline" / "scripts" / "audit_project_repository.py"
)
PROJECT_INTERVIEW_PACK_BUILDER = (
    ROOT / ".agents" / "skills" / "career-pipeline" / "scripts" / "build_project_interview_pack.py"
)
REAL_USER_DEPLOYMENT_FLOW = (
    ROOT
    / ".agents"
    / "skills"
    / "career-pipeline"
    / "references"
    / "real-user-deployment-and-use-flow.md"
)


def run_python(script: Path, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=str(cwd or ROOT),
        text=True,
        capture_output=True,
        check=False,
    )


def test_skill_md_names_skill_relative_script_commands():
    text = SKILL_MD.read_text(encoding="utf-8")

    assert "cd .agents/skills/career-pipeline" in text
    assert "python scripts/run_product_flow.py" in text
    assert "python scripts/collect_public_source_results.py" in text
    assert "python scripts/build_incomplete_user_manual_outputs.py" in text
    assert "python scripts/render_resume_artifacts.py --decision-package" in text
    assert "python scripts/simulate_runtime_run.py" in text
    assert "python scripts/discover_public_sources.py" in text
    assert "Do not run these commands from the repository root as `scripts/*.py`" in text


def test_skill_md_links_runtime_network_and_adapter_setup():
    text = SKILL_MD.read_text(encoding="utf-8")

    assert "references/runtime-network-and-adapter-setup.md" in text
    assert "before enabling real network fetches or real subagent execution" in text


def test_runtime_setup_reference_documents_real_execution_gates():
    text = RUNTIME_NETWORK_ADAPTER_SETUP.read_text(encoding="utf-8")

    assert "[sandbox_workspace_write]" in text
    assert "network_access = true" in text
    assert "Automatic Recruitment Source Injection" in text
    assert "discover_public_sources.py" in text
    assert "allowed_public_sources.generated.json" in text
    assert "default_public_recruitment_source_targets" in text
    assert "user_instruction_required" in text
    assert "source_policy_ack" in text
    assert "subagent_work_orders.json" in text
    assert "Codex Desktop" in text
    assert "spawn_agent" in text
    assert "role_output_packet" in text
    assert "login-only" in text


def test_skill_documents_codex_desktop_subagent_adapter_protocol():
    skill_text = SKILL_MD.read_text(encoding="utf-8")
    network_text = RUNTIME_NETWORK_ADAPTER_SETUP.read_text(encoding="utf-8")
    adapter_text = CODEX_DESKTOP_SUBAGENT_ADAPTER.read_text(encoding="utf-8")

    assert "references/codex-desktop-subagent-adapter.md" in skill_text
    assert "before using Codex Desktop current-session subagent tools" in skill_text
    assert "Codex Desktop built-in subagent adapter" in network_text
    assert "preferred built-in path" in network_text
    assert "references/codex-desktop-subagent-adapter.md" in network_text

    required_terms = [
        "multi_agent_v1.spawn_agent",
        "multi_agent_v1.wait_agent",
        "multi_agent_v1.close_agent",
        "dispatch_batches",
        "batch_id",
        "output_artifact_target",
        "role_output_packet",
        "error_recovery_state",
        "execute_subagent_plan.py --manual-controller-execution",
        "finalize_runtime_run.py --execution-mode manual-controller",
        "Python scripts cannot directly call",
        "main Codex controller",
        "UTF-8",
        "Do not ask the child agent to inspect Chinese JSON through PowerShell terminal rendering",
        "pass the serialized prompt bundle content",
    ]
    for term in required_terms:
        assert term in adapter_text


def test_real_user_flow_prefers_codex_desktop_adapter_when_available():
    flow_text = REAL_USER_DEPLOYMENT_FLOW.read_text(encoding="utf-8")
    readme_text = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "Codex Desktop built-in subagent adapter" in flow_text
    assert "references/codex-desktop-subagent-adapter.md" in flow_text
    assert "multi_agent_v1.spawn_agent" in flow_text
    assert "subagent_work_orders.json" in flow_text
    assert "execute_subagent_plan.py --manual-controller-execution" in flow_text
    assert "finalize_runtime_run.py --execution-mode manual-controller" in flow_text
    assert "Codex Desktop 内置 subagent adapter" in readme_text
    assert "mock-blocked" in readme_text


def test_runtime_execution_layer_points_to_setup_reference():
    text = RUNTIME_EXECUTION_LAYER.read_text(encoding="utf-8")

    assert "runtime-network-and-adapter-setup.md" in text
    assert "Real subagent execution remains blocked until a concrete adapter is configured and tested" in text
    assert "discover_public_sources.py" in text
    assert "run_product_flow.py" in text
    assert "collect_public_source_results.py" in text


def test_readme_documents_product_flow_and_public_source_collection_helpers():
    readme_text = (ROOT / "README.md").read_text(encoding="utf-8")
    network_text = RUNTIME_NETWORK_ADAPTER_SETUP.read_text(encoding="utf-8")

    assert "scripts/run_product_flow.py" in readme_text
    assert "scripts/collect_public_source_results.py" in readme_text
    assert "不需要手写 JSON" in readme_text
    assert "main Codex controller has already gathered public URLs" in network_text
    assert "browser search or visible web results" in network_text
    assert "title=" in network_text
    assert "snippet=" in network_text
    assert "类似 YAML" in readme_text
    assert "source_type_hint" in readme_text
    assert "YAML-like" in network_text
    assert "source_type_hint" in network_text
    assert "探索入口" in readme_text
    assert "generic_entrypoint_only" in network_text


def test_job_scout_injection_contains_default_recruitment_source_matrix(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "job_search",
        "--input-text",
        "Computer science sophomore, Python, looking for AI internship",
        "--run-root",
        str(run_root),
        "--route",
        "job_search",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id

    injection = json.loads(
        (run_dir / "injections" / "job-scout.secondary_prompt_injection.json").read_text(
            encoding="utf-8"
        )
    )["secondary_prompt_injection"]

    auto = injection["role_specific_context"]["automatic_public_recruitment_research"]
    assert auto["enabled"] is True
    assert auto["user_instruction_required"] is False
    assert auto["source_matrix_ref"] == "data/company_signals/default_recruitment_source_matrix.zh-CN.json"
    serialized = json.dumps(auto, ensure_ascii=False)
    assert "public_recruitment_platform" in serialized
    assert "recruitment_platform_jd" in serialized
    assert "official_primary" in serialized
    assert "official_or_primary" in serialized
    assert "login_only_page" in serialized

    research_tasks = json.dumps(injection["research_tasks"], ensure_ascii=False)
    assert "Automatically collect recruitment information" in research_tasks
    assert "user_instruction_required" in research_tasks


def test_source_plan_uses_auto_injected_recruitment_source_matrix(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "target_job_fit",
        "--input-text",
        "Computer science senior. Assess fit for Tencent backend role. JD: Java and MySQL.",
        "--run-root",
        str(run_root),
        "--route",
        "target_job_fit",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id

    result = run_python(SOURCE_PLAN_BUILDER, "--run-dir", str(run_dir))

    assert result.returncode == 0, result.stderr
    source_plan_ref = json.loads(result.stdout)["source_plan_response"]["source_plan_ref"]
    source_plan = json.loads((run_dir / source_plan_ref).read_text(encoding="utf-8"))[
        "public_source_research_plan"
    ]
    assert source_plan["source_matrix_ref"] == "data/company_signals/default_recruitment_source_matrix.zh-CN.json"
    assert source_plan["source_discovery_mode"] == "auto_injected_by_recruitment_roles"
    assert source_plan["user_instruction_required"] is False
    task_payload = json.dumps(source_plan["research_tasks"], ensure_ascii=False)
    assert "public_recruitment_platform" in task_payload
    assert "recruitment_platform_jd" in task_payload
    assert "official_primary" in task_payload
    assert "official_or_primary" in task_payload
    assert "public_report" in task_payload
    target_tasks = {
        task["task_id"]: task
        for task in source_plan["research_tasks"]
        if task["task_id"] in {"target-current-jd-verification", "target-learning-gap-evidence"}
    }
    assert target_tasks["target-current-jd-verification"]["display_sources"]
    assert target_tasks["target-learning-gap-evidence"]["display_sources"]


def test_target_job_fit_injections_require_project_and_hr_question_outputs(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "target_job_fit",
        "--input-text",
        (
            "Computer science junior. Python and Java basics, no strong project. "
            "Target: backend or AI application internship. JD: Python, Java, SQL, LLM app."
        ),
        "--run-root",
        str(run_root),
        "--route",
        "target_job_fit",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id

    learning = json.loads(
        (run_dir / "injections" / "learning-path-strategist.secondary_prompt_injection.json").read_text(
            encoding="utf-8"
        )
    )["secondary_prompt_injection"]
    hr = json.loads(
        (run_dir / "injections" / "hr-supervisor.secondary_prompt_injection.json").read_text(
            encoding="utf-8"
        )
    )["secondary_prompt_injection"]

    learning_required = set(learning["required_output_fields"])
    assert "project_recommendations" in learning_required
    assert "project_selection_rubric" in learning_required
    assert "resume_conversion_conditions" in learning_required
    assert "interview_defensibility_questions" in learning_required
    learning_payload = json.dumps(learning, ensure_ascii=False)
    assert "concrete project recommendation" in learning_payload
    assert "GitHub" in learning_payload
    assert "must not be written as completed resume claims" in learning_payload

    hr_required = set(hr["required_output_fields"])
    assert "hr_real_question_bank" in hr_required
    assert "likely_interview_questions" in hr_required
    assert "resume_defensibility_checks" in hr_required
    hr_payload = json.dumps(hr, ensure_ascii=False)
    assert "verified HR public posts" in hr_payload
    assert "candidate experience" in hr_payload
    assert "social media weak signals" in hr_payload
    assert "preparation only" in hr_payload


def test_project_candidate_discovery_filters_shallow_projects_and_keeps_mid_star_business_candidates(tmp_path):
    candidates_path = tmp_path / "project_candidates.json"
    candidates_path.write_text(
        json.dumps(
            {
                "candidates": [
                    {
                        "name": "ticket-flow-service",
                        "repo_url": "https://github.com/example/ticket-flow-service",
                        "bucket": "工单客服",
                        "stars": 1800,
                        "last_pushed_at": "2026-05-01",
                        "language": "Java",
                        "topics": ["spring-boot", "helpdesk", "mysql", "redis"],
                        "description": "Helpdesk ticket workflow with Spring Boot, MySQL, Redis, Docker.",
                        "readme_probe": "Ticket status flow, REST API, database migration, Docker compose, tests.",
                    },
                    {
                        "name": "thin-llm-wrapper",
                        "repo_url": "https://github.com/example/thin-llm-wrapper",
                        "bucket": "业务型 Agent",
                        "stars": 42000,
                        "last_pushed_at": "2026-04-10",
                        "language": "TypeScript",
                        "topics": ["llm", "wrapper", "browser-extension"],
                        "description": "Simple browser extension wrapper around a single LLM call.",
                        "readme_probe": "Prompt template and browser extension side panel.",
                    },
                    {
                        "name": "agent-research-workflow",
                        "repo_url": "https://github.com/example/agent-research-workflow",
                        "bucket": "业务型 Agent",
                        "stars": 2600,
                        "last_pushed_at": "2026-03-20",
                        "language": "Python",
                        "topics": ["ai-agent", "workflow", "evaluation", "postgres"],
                        "description": "Research workflow agent with task state, tools, persistence, and evaluation.",
                        "readme_probe": "Planner, tool calling, task queue, Postgres persistence, eval traces.",
                    },
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    out_dir = tmp_path / "discovery"

    result = run_python(
        PROJECT_CANDIDATE_DISCOVERER,
        "--candidates-json",
        str(candidates_path),
        "--target-role",
        "backend or AI application internship",
        "--jd-text",
        "Java Spring Boot MySQL Redis ticket workflow LLM agent evaluation",
        "--mode",
        "mixed",
        "--out-dir",
        str(out_dir),
    )

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)["project_candidate_discovery_response"]
    payload = json.loads((out_dir / response["discovery_json"]).read_text(encoding="utf-8"))[
        "project_candidate_discovery"
    ]
    shortlist_names = [item["name"] for item in payload["shortlist"]]
    excluded_names = [item["name"] for item in payload["excluded"]]
    assert "ticket-flow-service" in shortlist_names
    assert "agent-research-workflow" in shortlist_names
    assert "thin-llm-wrapper" in excluded_names
    assert payload["shortlist"][0]["score_breakdown"]["star_score"] <= 10
    assert "shallow_or_wrapper" in json.dumps(payload["excluded"], ensure_ascii=False)
    assert (out_dir / response["shortlist_md"]).is_file()


def test_project_tools_accept_utf8_bom_json_from_windows_clients(tmp_path):
    candidates_path = tmp_path / "project_candidates_bom.json"
    candidates_path.write_text(
        "\ufeff"
        + json.dumps(
            {
                "candidates": [
                    {
                        "name": "ticket-flow-service",
                        "repo_url": "https://github.com/example/ticket-flow-service",
                        "bucket": "工单客服",
                        "stars": 1800,
                        "last_pushed_at": "2026-05-01",
                        "language": "Java",
                        "topics": ["spring-boot", "helpdesk", "mysql", "redis"],
                        "description": "Helpdesk ticket workflow with Spring Boot, MySQL, Redis, Docker.",
                        "readme_probe": "Ticket status flow, REST API, database migration, Docker compose, tests.",
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    discovery_dir = tmp_path / "discovery"

    discovery = run_python(
        PROJECT_CANDIDATE_DISCOVERER,
        "--candidates-json",
        str(candidates_path),
        "--target-role",
        "backend internship",
        "--jd-text",
        "Java Spring Boot MySQL Redis ticket workflow",
        "--mode",
        "mixed",
        "--out-dir",
        str(discovery_dir),
    )

    assert discovery.returncode == 0, discovery.stderr

    repo = make_tiny_project_repo(tmp_path)
    audit_dir = tmp_path / "audit"
    audit_result = run_python(
        PROJECT_REPO_AUDITOR,
        "--repo",
        str(repo),
        "--name",
        "tiny-ticket-project",
        "--out-dir",
        str(audit_dir),
    )
    assert audit_result.returncode == 0, audit_result.stderr
    recommendation_path = tmp_path / "recommendation_bom.json"
    recommendation_path.write_text(
        "\ufeff"
        + json.dumps(
            {
                "project_name": "tiny-ticket-project",
                "target_role_family": "backend internship",
                "planned_modifications": ["add ticket search API"],
                "completed_modifications": ["read source structure"],
                "proof_artifacts": ["local source audit"],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    pack = run_python(
        PROJECT_INTERVIEW_PACK_BUILDER,
        "--audit-json",
        str(audit_dir / "project_repo_audit.json"),
        "--recommendation-json",
        str(recommendation_path),
        "--out-dir",
        str(tmp_path / "pack"),
    )

    assert pack.returncode == 0, pack.stderr


def make_tiny_project_repo(root: Path) -> Path:
    repo = root / "tiny_ticket_project"
    (repo / "routes").mkdir(parents=True)
    (repo / "tests").mkdir()
    (repo / "migrations").mkdir()
    (repo / "README.md").write_text(
        "# Tiny Ticket Project\n\nREST API for ticket creation, status updates, MySQL persistence, and Redis cache.\n",
        encoding="utf-8",
    )
    (repo / "requirements.txt").write_text("fastapi\nredis\npymysql\npytest\n", encoding="utf-8")
    (repo / "Dockerfile").write_text("FROM python:3.12-slim\n", encoding="utf-8")
    (repo / "docker-compose.yml").write_text("services:\n  db:\n    image: mysql:8\n", encoding="utf-8")
    (repo / "app.py").write_text(
        "from routes.tickets import router\n\napp = router\n",
        encoding="utf-8",
    )
    (repo / "routes" / "tickets.py").write_text(
        "def create_ticket(payload):\n    return {'status': 'created', 'payload': payload}\n",
        encoding="utf-8",
    )
    (repo / "migrations" / "001_init.sql").write_text(
        "create table tickets(id int primary key, status varchar(32));\n",
        encoding="utf-8",
    )
    (repo / "tests" / "test_smoke.py").write_text(
        "def test_smoke():\n    assert True\n",
        encoding="utf-8",
    )
    return repo


def test_project_repo_auditor_extracts_source_evidence_points(tmp_path):
    repo = make_tiny_project_repo(tmp_path)
    out_dir = tmp_path / "audit"

    result = run_python(
        PROJECT_REPO_AUDITOR,
        "--repo",
        str(repo),
        "--name",
        "tiny-ticket-project",
        "--out-dir",
        str(out_dir),
    )

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)["project_repo_audit_response"]
    audit = json.loads((out_dir / response["audit_json"]).read_text(encoding="utf-8"))["project_repo_audit"]
    assert audit["name"] == "tiny-ticket-project"
    assert "requirements.txt" in audit["dependency_files"]
    assert "docker-compose.yml" in audit["docker_files"]
    assert "tests/test_smoke.py" in audit["test_files"]
    assert "api_backend" in audit["signals"]
    assert "database_state" in audit["signals"]
    assert len(audit["source_evidence_points"]) >= 5
    assert audit["resume_claim_gate"]["source_verified"] is True


def test_project_interview_pack_separates_existing_capability_modification_and_resume_ready_claims(tmp_path):
    repo = make_tiny_project_repo(tmp_path)
    audit_dir = tmp_path / "audit"
    audit_result = run_python(
        PROJECT_REPO_AUDITOR,
        "--repo",
        str(repo),
        "--name",
        "tiny-ticket-project",
        "--out-dir",
        str(audit_dir),
    )
    assert audit_result.returncode == 0, audit_result.stderr
    audit_ref = audit_dir / json.loads(audit_result.stdout)["project_repo_audit_response"]["audit_json"]
    recommendation_path = tmp_path / "recommendation.json"
    recommendation_path.write_text(
        json.dumps(
            {
                "project_name": "tiny-ticket-project",
                "target_role_family": "backend internship",
                "target_jd_summary": "Java/Python backend internship requiring API, database, cache, Docker, and tests.",
                "planned_modifications": [
                    "add ticket search API",
                    "add Redis cache invalidation notes",
                    "add API smoke test",
                ],
                "completed_modifications": ["read source structure and verified existing smoke test"],
                "proof_artifacts": ["local source audit", "README", "tests/test_smoke.py"],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    out_dir = tmp_path / "pack"

    result = run_python(
        PROJECT_INTERVIEW_PACK_BUILDER,
        "--audit-json",
        str(audit_ref),
        "--recommendation-json",
        str(recommendation_path),
        "--out-dir",
        str(out_dir),
    )

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)["project_interview_pack_response"]
    pack_text = (out_dir / response["pack_md"]).read_text(encoding="utf-8")
    for heading in [
        "## 项目定位",
        "## 现有能力",
        "## 建议改造",
        "## 可写入简历",
        "## STAR 简历项目",
        "## 面试官追问",
        "## 核心代码讲解",
    ]:
        assert heading in pack_text
    assert "add ticket search API" in pack_text
    assert "未完成内容不能写成已完成项目" in pack_text
    assert "tests/test_smoke.py" in pack_text


def test_engineering_smoke_test_writes_results_for_ten_profiles(tmp_path):
    output_dir = tmp_path / "manual-skill-reliability-test"
    result = run_python(
        ENGINEERING_SMOKE,
        "--output-dir",
        str(output_dir),
        "--run-root",
        str(output_dir / "runs"),
        "--run-id-prefix",
        "test-smoke",
    )

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)["smoke_test_response"]
    assert response["exit_status"] == "success"
    results_md = output_dir / "results.md"
    results_json = output_dir / "results.json"
    user_report = output_dir / "user_report.md"
    assert results_md.is_file()
    assert results_json.is_file()
    assert user_report.is_file()

    payload = json.loads(results_json.read_text(encoding="utf-8"))
    assert payload["scope"] == "engineering_only"
    assert payload["network"] == "disabled"
    assert payload["real_subagent_execution"] is False
    assert len(payload["profiles"]) == 10
    assert payload["overall"]["fail"] == 0
    assert payload["overall"]["partial"] == 0
    assert all(profile["blocked_outputs"] for profile in payload["profiles"])
    assert all(profile["discipline_domain"] == "engineering" for profile in payload["profiles"])
    for profile in payload["profiles"]:
        package = profile["user_facing_package"]
        assert package["evidence_status"] == "research_plan_created_not_executed"
        assert package["execution_status"] == "dry_run_no_real_subagent"
        assert len(package["next_three_actions"]) == 3
        assert "精确适配评分" in package["blocked_until_evidence"]
        assert "current_fit_assessment" not in package["blocked_until_evidence"]
        assert "application_strategy" not in package["blocked_until_evidence"]
        assert package["hr_supervision_note"]
    md_text = results_md.read_text(encoding="utf-8")
    assert "本科大二 计算机 AI 实习探索" in md_text
    assert "用户端可读包" in md_text
    assert "公开来源研究计划已生成但尚未执行" in md_text
    user_report_text = user_report.read_text(encoding="utf-8")
    assert "run_dir" not in user_report_text
    assert "fit_score" not in user_report_text
    assert "current_fit_assessment" not in user_report_text
    assert "application_strategy" not in user_report_text
    assert "blocked_outputs" not in user_report_text
    assert "下一步建议" in user_report_text
    assert "HR 确认项" in user_report_text


def test_work_order_builder_exports_subagent_ready_orders(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "job_search",
        "--input-text",
        "Computer science sophomore, Python, looking for AI internship",
        "--run-root",
        str(run_root),
        "--route",
        "job_search",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id
    assert run_python(PLAN_BUILDER, "--run-dir", str(run_dir), "--build-prompt-bundles").returncode == 0

    result = run_python(WORK_ORDER_BUILDER, "--run-dir", str(run_dir))

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)["work_order_response"]
    orders_path = run_dir / response["work_orders_ref"]
    orders = json.loads(orders_path.read_text(encoding="utf-8"))["subagent_work_orders"]
    assert orders["adapter_status"] == "not_configured"
    assert orders["real_execution_ready"] is False
    assert len(orders["orders"]) == 6
    first = orders["orders"][0]
    assert first["prompt_bundle_ref"].startswith("prompts/")
    assert "input/raw_refs.json" not in json.dumps(orders, ensure_ascii=False)
    assert first["expected_backfill_contract"]["required_top_level_fields"] == [
        "invocation_ref",
        "role_output_packet",
        "error_recovery_state",
    ]
    assert "batch_id" in first
    assert first["close_after_artifact_persisted"] is True


def test_public_evidence_backfill_accepts_safe_public_evidence(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "target_job_fit",
        "--input-text",
        "Computer science senior. Assess fit for Tencent backend role. JD: Java and MySQL.",
        "--run-root",
        str(run_root),
        "--route",
        "target_job_fit",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id
    assert run_python(SOURCE_PLAN_BUILDER, "--run-dir", str(run_dir)).returncode == 0

    evidence = {
        "evidence_packets": [
            {
                "evidence_packet": {
                    "evidence_id": "ev-official-jd",
                    "claim_id": "target-current-jd-verification",
                    "field": "current_jd_text",
                    "source_type": "official_or_primary",
                    "source_ref": "https://careers.example.com/jobs/1",
                    "artifact_ref": "",
                    "retrieved_or_published_date": "2026-06-27",
                    "freshness": "0_6_months",
                    "evidence_strength": "strong",
                    "inference_level": "none",
                    "privacy_class": "public",
                    "confidence": "high",
                    "may_set_final_decision": True,
                    "may_set_weight": True,
                }
            }
        ]
    }
    evidence_path = tmp_path / "evidence.json"
    evidence_path.write_text(json.dumps(evidence), encoding="utf-8")

    result = run_python(EVIDENCE_BACKFILL, "--run-dir", str(run_dir), "--evidence-json", str(evidence_path))

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)["evidence_backfill_response"]
    assert response["accepted_count"] == 1
    evidence_jsonl = run_dir / response["evidence_packets_ref"]
    assert evidence_jsonl.is_file()
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert response["evidence_packets_ref"] in manifest["execution_manifest"]["evidence_packet_refs"]


def test_public_evidence_backfill_rejects_weak_social_as_final_basis(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "job_search",
        "--input-text",
        "Computer science sophomore, Python, looking for AI internship",
        "--run-root",
        str(run_root),
        "--route",
        "job_search",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id
    assert run_python(SOURCE_PLAN_BUILDER, "--run-dir", str(run_dir)).returncode == 0

    evidence = {
        "evidence_packets": [
            {
                "evidence_packet": {
                    "evidence_id": "ev-weak-social",
                    "claim_id": "social-media-weak-signal",
                    "field": "company_reputation",
                    "source_type": "social_media_weak",
                    "source_ref": "https://example.com/post",
                    "artifact_ref": "",
                    "retrieved_or_published_date": "2026-06-27",
                    "freshness": "0_6_months",
                    "evidence_strength": "weak",
                    "inference_level": "medium",
                    "privacy_class": "public",
                    "confidence": "low",
                    "may_set_final_decision": True,
                    "may_set_weight": False,
                }
            }
        ]
    }
    evidence_path = tmp_path / "weak-evidence.json"
    evidence_path.write_text(json.dumps(evidence), encoding="utf-8")

    result = run_python(EVIDENCE_BACKFILL, "--run-dir", str(run_dir), "--evidence-json", str(evidence_path))

    assert result.returncode == 1
    assert "social_media_weak" in result.stderr
    assert "final decision" in result.stderr


def test_public_source_fetcher_collects_allowed_public_html_and_backfills(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "target_job_fit",
        "--input-text",
        "Computer science senior. Assess fit for Tencent backend role. JD: Java and MySQL.",
        "--run-root",
        str(run_root),
        "--route",
        "target_job_fit",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id
    assert run_python(SOURCE_PLAN_BUILDER, "--run-dir", str(run_dir)).returncode == 0

    html = tmp_path / "official-career.html"
    html.write_text(
        "<html><title>Backend Engineer Intern</title><body>"
        "<h1>Backend Engineer Intern</h1><p>Requirements: Java, MySQL, distributed systems.</p>"
        "</body></html>",
        encoding="utf-8",
    )
    sources = {
        "sources": [
            {
                "task_id": "target-current-jd-verification",
                "source_type": "official_or_primary",
                "source_ref": html.as_uri(),
                "field": "current_jd_text",
            }
        ]
    }
    sources_path = tmp_path / "sources.json"
    sources_path.write_text(json.dumps(sources), encoding="utf-8")

    fetch = run_python(PUBLIC_SOURCE_FETCHER, "--run-dir", str(run_dir), "--sources-json", str(sources_path))

    assert fetch.returncode == 0, fetch.stderr
    response = json.loads(fetch.stdout)["public_source_fetch_response"]
    assert response["accepted_count"] == 1
    evidence_path = run_dir / response["evidence_json_ref"]
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))["evidence_packets"][0]["evidence_packet"]
    assert evidence["source_type"] == "official_or_primary"
    assert evidence["claim_id"] == "target-current-jd-verification"
    assert evidence["may_set_final_decision"] is True

    backfill = run_python(EVIDENCE_BACKFILL, "--run-dir", str(run_dir), "--evidence-json", str(evidence_path))
    assert backfill.returncode == 0, backfill.stderr


def test_public_source_fetcher_decodes_chinese_charset_html(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "target_job_fit",
        "--input-text",
        "Computer science senior. Assess fit for Tencent backend role. JD: Java and MySQL.",
        "--run-root",
        str(run_root),
        "--route",
        "target_job_fit",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id
    assert run_python(SOURCE_PLAN_BUILDER, "--run-dir", str(run_dir)).returncode == 0

    html = tmp_path / "gbk-official-career.html"
    html.write_bytes(
        (
            '<html><head><meta charset="gb2312"><title>后端开发实习生</title></head>'
            "<body><h1>后端开发实习生</h1><p>岗位要求：计算机基础、Java、MySQL、Redis。</p></body></html>"
        ).encode("gbk")
    )
    sources = {
        "sources": [
            {
                "task_id": "target-current-jd-verification",
                "source_type": "official_or_primary",
                "source_ref": html.as_uri(),
                "field": "current_jd_text",
            }
        ]
    }
    sources_path = tmp_path / "sources.json"
    sources_path.write_text(json.dumps(sources), encoding="utf-8")

    fetch = run_python(PUBLIC_SOURCE_FETCHER, "--run-dir", str(run_dir), "--sources-json", str(sources_path))

    assert fetch.returncode == 0, fetch.stderr
    response = json.loads(fetch.stdout)["public_source_fetch_response"]
    evidence_path = run_dir / response["evidence_json_ref"]
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))["evidence_packets"][0]["evidence_packet"]
    assert "后端开发实习生" in evidence["excerpt"]
    assert "岗位要求" in evidence["excerpt"]
    assert "璁" not in evidence["excerpt"]


def test_public_source_fetcher_accepts_browser_rendered_text_snapshot_for_dynamic_pages(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "target_job_fit",
        "--input-text",
        "Computer science senior. Assess fit for ByteDance LLM backend internship.",
        "--run-root",
        str(run_root),
        "--route",
        "target_job_fit",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id
    assert run_python(SOURCE_PLAN_BUILDER, "--run-dir", str(run_dir)).returncode == 0

    rendered = tmp_path / "bytedance-rendered.txt"
    rendered.write_text(
        "大数据大模型应用后端开发实习生-音视频技术。职责：LLM 上下文工程、智能诊断、指标监控。"
        "要求：计算机基础、Go/Python、MySQL、Redis、消息队列、RAG 或 Agent 经验优先。",
        encoding="utf-8",
    )
    sources = {
        "sources": [
            {
                "task_id": "target-current-jd-verification",
                "source_type": "official_or_primary",
                "source_ref": "https://jobs.bytedance.com/campus/position/detail/7594472256522357045",
                "field": "current_jd_text",
                "rendered_text_ref": str(rendered),
            }
        ]
    }
    sources_path = tmp_path / "sources.json"
    sources_path.write_text(json.dumps(sources), encoding="utf-8")

    fetch = run_python(PUBLIC_SOURCE_FETCHER, "--run-dir", str(run_dir), "--sources-json", str(sources_path))

    assert fetch.returncode == 0, fetch.stderr
    response = json.loads(fetch.stdout)["public_source_fetch_response"]
    evidence_path = run_dir / response["evidence_json_ref"]
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))["evidence_packets"][0]["evidence_packet"]
    assert "大数据大模型应用后端开发实习生" in evidence["excerpt"]
    assert evidence["source_ref"] == "https://jobs.bytedance.com/campus/position/detail/7594472256522357045"
    assert evidence["extraction_method"] == "browser_rendered_text"
    source_index = json.loads((run_dir / response["fetched_source_index_ref"]).read_text(encoding="utf-8"))
    assert source_index["fetched_source_index"][0]["extraction_method"] == "browser_rendered_text"


def test_public_source_fetcher_rejects_dynamic_shell_without_rendered_snapshot(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "target_job_fit",
        "--input-text",
        "Computer science senior. Assess fit for ByteDance LLM backend internship.",
        "--run-root",
        str(run_root),
        "--route",
        "target_job_fit",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id
    assert run_python(SOURCE_PLAN_BUILDER, "--run-dir", str(run_dir)).returncode == 0

    shell = tmp_path / "dynamic-shell.html"
    shell.write_text(
        "<html><body><noscript>Please enable JavaScript to continue.</noscript>"
        "<div id='root'></div><script src='app.js'></script></body></html>",
        encoding="utf-8",
    )
    sources = {
        "sources": [
            {
                "task_id": "target-current-jd-verification",
                "source_type": "official_or_primary",
                "source_ref": shell.as_uri(),
                "field": "current_jd_text",
            }
        ]
    }
    sources_path = tmp_path / "sources.json"
    sources_path.write_text(json.dumps(sources), encoding="utf-8")

    fetch = run_python(PUBLIC_SOURCE_FETCHER, "--run-dir", str(run_dir), "--sources-json", str(sources_path))

    assert fetch.returncode == 1
    assert "dynamic page shell" in fetch.stderr
    assert "rendered_text_ref" in fetch.stderr


def test_public_source_fetcher_can_degrade_single_source_fetch_failures(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "job_search",
        "--input-text",
        "Computer science junior, Python, looking for backend or AI application internship.",
        "--run-root",
        str(run_root),
        "--route",
        "job_search",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id
    assert run_python(SOURCE_PLAN_BUILDER, "--run-dir", str(run_dir)).returncode == 0

    local_source = tmp_path / "public-jd.html"
    local_source.write_text(
        "<html><body><h1>Python backend intern</h1><p>Python, SQL, API, Linux, project evidence.</p></body></html>",
        encoding="utf-8",
    )
    sources = {
        "sources": [
            {
                "task_id": "recruitment-platform-public-jd",
                "source_type": "recruitment_platform_jd",
                "source_ref": local_source.as_uri(),
                "field": "current_jd_requirement",
            },
            {
                "task_id": "recruitment-platform-public-jd",
                "source_type": "recruitment_platform_jd",
                "source_ref": "https://127.0.0.1:9/unreachable-public-jd",
                "field": "current_jd_requirement",
            },
        ]
    }
    sources_path = tmp_path / "mixed-sources.json"
    sources_path.write_text(json.dumps(sources), encoding="utf-8")

    fetch = run_python(
        PUBLIC_SOURCE_FETCHER,
        "--run-dir",
        str(run_dir),
        "--sources-json",
        str(sources_path),
        "--degrade-on-source-error",
        "--timeout-seconds",
        "1",
    )

    assert fetch.returncode == 0, fetch.stderr
    response = json.loads(fetch.stdout)["public_source_fetch_response"]
    assert response["exit_status"] == "degraded"
    assert response["accepted_count"] == 1
    assert response["failed_count"] == 1
    evidence = json.loads((run_dir / response["evidence_json_ref"]).read_text(encoding="utf-8"))
    assert len(evidence["evidence_packets"]) == 1
    attempt_log = json.loads((run_dir / response["source_attempt_log_ref"]).read_text(encoding="utf-8"))
    assert attempt_log["source_attempt_log"][0]["failure_type"] == "source_fetch_failed"
    assert "replacement_public_url_required" in attempt_log["source_attempt_log"][0]["recovery_action"]


def test_public_source_discoverer_generates_allowed_sources_from_search_results(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "target_job_fit",
        "--input-text",
        (
            "Computer science senior. Assess fit for Tencent backend development internship. "
            "JD: Java, Spring, MySQL, Redis, distributed systems."
        ),
        "--run-root",
        str(run_root),
        "--route",
        "target_job_fit",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id
    assert run_python(SOURCE_PLAN_BUILDER, "--run-dir", str(run_dir)).returncode == 0

    search_results = {
        "search_results": [
            {
                "task_id": "target-current-jd-verification",
                "url": "https://join.qq.com/post/backend-intern",
                "title": "Tencent backend development internship",
                "snippet": "Java Spring MySQL Redis distributed systems internship.",
            },
            {
                "task_id": "target-learning-gap-evidence",
                "url": "https://careers.tencent.com/hr/backend-campus-guide",
                "title": "Tencent HR campus backend interview guide",
                "snippet": "HR public guide for backend preparation and project expectations.",
            },
            {
                "task_id": "social-media-weak-signal",
                "url": "https://www.xiaohongshu.com/explore/tencent-backend",
                "title": "Tencent backend internship discussion",
                "snippet": "Public candidate discussion. Treat as weak signal.",
            },
            {
                "task_id": "target-current-jd-verification",
                "url": "https://example.com/login?next=/private-job",
                "title": "Login required private job",
                "snippet": "Please log in to view private candidate data.",
            },
        ]
    }
    search_results_path = tmp_path / "search-results.json"
    search_results_path.write_text(json.dumps(search_results), encoding="utf-8")

    result = run_python(
        PUBLIC_SOURCE_DISCOVERER,
        "--run-dir",
        str(run_dir),
        "--search-results-json",
        str(search_results_path),
    )

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)["public_source_discovery_response"]
    assert response["exit_status"] == "success"
    assert response["user_instruction_required"] is False
    assert response["accepted_count"] == 3
    assert response["rejected_count"] == 1

    generated = json.loads((run_dir / response["generated_sources_ref"]).read_text(encoding="utf-8"))
    serialized = json.dumps(generated, ensure_ascii=False)
    assert "https://join.qq.com/post/backend-intern" in serialized
    assert "https://example.com/login?next=/private-job" not in serialized
    assert "target-current-jd-verification" in serialized
    official = [
        source
        for source in generated["sources"]
        if source["source_ref"] == "https://join.qq.com/post/backend-intern"
    ][0]
    assert official["source_type"] == "official_or_primary"
    weak = [
        source
        for source in generated["sources"]
        if source["source_type"] == "social_media_weak"
    ][0]
    assert weak["may_set_final_decision"] is False
    assert weak["may_set_weight"] is False

    log = json.loads((run_dir / response["discovery_log_ref"]).read_text(encoding="utf-8"))
    assert log["public_source_discovery"]["source_discovery_mode"] == "auto_search_adapter"
    query_payload = json.dumps(log["public_source_discovery"]["search_queries"], ensure_ascii=False)
    assert "BOSS" in query_payload or "牛客" in query_payload
    assert "user_instruction_required" in query_payload


def test_public_source_discoverer_outputs_search_queries_when_no_results(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "job_search",
        "--input-text",
        "Computer science sophomore, Python, looking for AI internship at ByteDance or DJI",
        "--run-root",
        str(run_root),
        "--route",
        "job_search",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id
    assert run_python(SOURCE_PLAN_BUILDER, "--run-dir", str(run_dir)).returncode == 0
    empty_results = tmp_path / "empty-search-results.json"
    empty_results.write_text(json.dumps({"search_results": []}), encoding="utf-8")

    result = run_python(
        PUBLIC_SOURCE_DISCOVERER,
        "--run-dir",
        str(run_dir),
        "--search-results-json",
        str(empty_results),
    )

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)["public_source_discovery_response"]
    assert response["accepted_count"] == 0
    generated = json.loads((run_dir / response["generated_sources_ref"]).read_text(encoding="utf-8"))
    assert generated["sources"] == []
    log = json.loads((run_dir / response["discovery_log_ref"]).read_text(encoding="utf-8"))
    queries = log["public_source_discovery"]["search_queries"]
    assert queries
    assert all(query["user_instruction_required"] is False for query in queries)
    query_payload = json.dumps(queries, ensure_ascii=False)
    assert "ByteDance" in query_payload or "DJI" in query_payload


def test_public_source_discoverer_can_generate_query_plan_without_results(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "job_search",
        "--input-text",
        "Computer science sophomore, Python, looking for AI internship at ByteDance or DJI",
        "--run-root",
        str(run_root),
        "--route",
        "job_search",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id
    assert run_python(SOURCE_PLAN_BUILDER, "--run-dir", str(run_dir)).returncode == 0

    result = run_python(PUBLIC_SOURCE_DISCOVERER, "--run-dir", str(run_dir), "--generate-query-plan-only")

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)["public_source_discovery_response"]
    assert response["exit_status"] == "needs_search_results"
    assert response["accepted_count"] == 0
    assert response["generated_sources_ref"] == ""
    log = json.loads((run_dir / response["discovery_log_ref"]).read_text(encoding="utf-8"))
    discovery = log["public_source_discovery"]
    assert discovery["search_queries"]
    assert discovery["next_action"] == "run_search_adapter"


def test_public_source_discoverer_accepts_bom_encoded_search_results(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "target_job_fit",
        "--input-text",
        "Computer science senior. Assess fit for Tencent backend role. JD: Java and MySQL.",
        "--run-root",
        str(run_root),
        "--route",
        "target_job_fit",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id
    assert run_python(SOURCE_PLAN_BUILDER, "--run-dir", str(run_dir)).returncode == 0

    search_results_path = tmp_path / "bom-search-results.json"
    search_results_path.write_text(
        json.dumps(
            {
                "search_results": [
                    {
                        "task_id": "target-current-jd-verification",
                        "url": "https://join.qq.com/post/backend-intern",
                        "title": "Tencent backend intern",
                        "snippet": "Java MySQL",
                    }
                ]
            }
        ),
        encoding="utf-8-sig",
    )

    result = run_python(
        PUBLIC_SOURCE_DISCOVERER,
        "--run-dir",
        str(run_dir),
        "--search-results-json",
        str(search_results_path),
    )

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)["public_source_discovery_response"]
    assert response["accepted_count"] == 1


def test_public_source_searcher_generates_seed_search_results_from_query_plan(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "target_job_fit",
        "--input-text",
        "Computer science senior. Assess fit for Tencent backend role. JD: Java and MySQL.",
        "--run-root",
        str(run_root),
        "--route",
        "target_job_fit",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id
    assert run_python(SOURCE_PLAN_BUILDER, "--run-dir", str(run_dir)).returncode == 0
    assert run_python(PUBLIC_SOURCE_DISCOVERER, "--run-dir", str(run_dir), "--generate-query-plan-only").returncode == 0

    result = run_python(PUBLIC_SOURCE_SEARCHER, "--run-dir", str(run_dir), "--provider", "seed")

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)["public_source_search_response"]
    assert response["exit_status"] == "success"
    assert response["provider"] == "seed"
    assert response["user_instruction_required"] is False
    results = json.loads((run_dir / response["search_results_ref"]).read_text(encoding="utf-8"))
    serialized = json.dumps(results, ensure_ascii=False)
    assert "join.qq.com" in serialized
    assert all(item["task_id"] for item in results["search_results"])

    discover = run_python(
        PUBLIC_SOURCE_DISCOVERER,
        "--run-dir",
        str(run_dir),
        "--search-results-json",
        str(run_dir / response["search_results_ref"]),
    )
    assert discover.returncode == 0, discover.stderr
    generated_ref = json.loads(discover.stdout)["public_source_discovery_response"]["generated_sources_ref"]
    generated = json.loads((run_dir / generated_ref).read_text(encoding="utf-8"))
    assert generated["sources"]


def test_public_source_searcher_accepts_external_json_adapter_results(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "target_job_fit",
        "--input-text",
        "Computer science senior. Assess fit for Tencent backend role. JD: Java and MySQL.",
        "--run-root",
        str(run_root),
        "--route",
        "target_job_fit",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id
    assert run_python(SOURCE_PLAN_BUILDER, "--run-dir", str(run_dir)).returncode == 0
    assert run_python(PUBLIC_SOURCE_DISCOVERER, "--run-dir", str(run_dir), "--generate-query-plan-only").returncode == 0
    external_results = tmp_path / "external-search-results.json"
    external_results.write_text(
        json.dumps(
            {
                "search_results": [
                    {
                        "task_id": "target-current-jd-verification",
                        "url": "https://join.qq.com/post/backend-intern",
                        "title": "Tencent backend intern",
                        "snippet": "Java MySQL Redis",
                        "source_type": "recruitment_platform_jd",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    result = run_python(
        PUBLIC_SOURCE_SEARCHER,
        "--run-dir",
        str(run_dir),
        "--provider",
        "external-json",
        "--search-results-json",
        str(external_results),
    )

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)["public_source_search_response"]
    assert response["exit_status"] == "success"
    assert response["provider"] == "external-json"
    assert response["real_time_search"] is True
    results = json.loads((run_dir / response["search_results_ref"]).read_text(encoding="utf-8"))
    assert results["search_results"][0]["url"] == "https://join.qq.com/post/backend-intern"
    discover = run_python(
        PUBLIC_SOURCE_DISCOVERER,
        "--run-dir",
        str(run_dir),
        "--search-results-json",
        str(run_dir / response["search_results_ref"]),
    )
    assert discover.returncode == 0, discover.stderr
    assert json.loads(discover.stdout)["public_source_discovery_response"]["accepted_count"] == 1


def test_public_source_result_collector_converts_plain_markdown_urls_to_search_results(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "target_job_fit",
        "--input-text",
        (
            "Computer science junior. Target: Tencent backend or AI application internship. "
            "JD: Python, Java, SQL, LLM app."
        ),
        "--run-root",
        str(run_root),
        "--route",
        "target_job_fit",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id
    assert run_python(SOURCE_PLAN_BUILDER, "--run-dir", str(run_dir)).returncode == 0
    assert run_python(PUBLIC_SOURCE_DISCOVERER, "--run-dir", str(run_dir), "--generate-query-plan-only").returncode == 0

    notes_md = tmp_path / "public-source-notes.md"
    notes_md.write_text(
        "\n".join(
            [
                "- https://careers.tencent.com/ title=Tencent official careers source_type=official_or_primary snippet=Official recruiting entry.",
                "- https://www.nowcoder.com/jobs/backend-intern title=Backend intern public JD source_type=recruitment_platform_jd snippet=Python Java SQL internship.",
                "- https://mp.weixin.qq.com/s/tencent-campus-hr title=Tencent HR public recruiting post source_type=verified_hr_public_post snippet=HR screening project experience.",
            ]
        ),
        encoding="utf-8",
    )

    result = run_python(
        PUBLIC_SOURCE_RESULT_COLLECTOR,
        "--run-dir",
        str(run_dir),
        "--notes-md",
        str(notes_md),
    )

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)["public_source_result_collection_response"]
    assert response["exit_status"] == "success"
    assert response["user_instruction_required"] is False
    assert response["result_count"] == 3
    payload = json.loads((run_dir / response["search_results_ref"]).read_text(encoding="utf-8"))
    assert payload["metadata"]["provider"] == "controller-collected"
    assert payload["metadata"]["real_time_search"] is True
    assert payload["metadata"]["user_instruction_required"] is False
    task_ids = {item["task_id"] for item in payload["search_results"]}
    assert "target-current-jd-verification" in task_ids
    assert "company-bound-hr-real-questions" in task_ids
    assert all(item["url"].startswith("https://") for item in payload["search_results"])

    source_search = run_python(
        PUBLIC_SOURCE_SEARCHER,
        "--run-dir",
        str(run_dir),
        "--provider",
        "external-json",
        "--search-results-json",
        str(run_dir / response["search_results_ref"]),
    )
    assert source_search.returncode == 0, source_search.stderr
    search_ref = json.loads(source_search.stdout)["public_source_search_response"]["search_results_ref"]
    discover = run_python(
        PUBLIC_SOURCE_DISCOVERER,
        "--run-dir",
        str(run_dir),
        "--search-results-json",
        str(run_dir / search_ref),
    )
    assert discover.returncode == 0, discover.stderr
    assert json.loads(discover.stdout)["public_source_discovery_response"]["accepted_count"] == 3


def write_external_adapter_script(path: Path) -> None:
    path.write_text(
        """
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument("--work-order-json", required=True)
parser.add_argument("--output-json", required=True)
args = parser.parse_args()

payload = json.load(open(args.work_order_json, encoding="utf-8"))
order = payload["work_order"]
invocation = payload["subagent_invocation"]
output_ref = order["output_artifact_target"]
target_agent = order["target_agent"]
result = {
    "invocation_ref": order["invocation_ref"],
    "role": target_agent,
    "task_summary": "External command adapter smoke output.",
    "inputs_used": [order["prompt_bundle_ref"]],
    "database_files_used": [],
    "source_notes": [],
    "runtime_scope": "evidence_collection",
    "judgment_allowed": "evidence_bound_only",
    "judgment_status": "evidence_bound_judgment",
    "decision_owner": "local_subagent",
    "runtime_preconditions": {
        "has_current_jd": True,
        "has_target_company": True,
        "has_user_constraints": False,
        "has_user_consent": False,
        "job_direction_blocked": False
    },
    "evidence_basis": [],
    "repository_prior_usage": [],
    "weight_provenance": [
        {
            "parameter": "adapter_smoke_weight",
            "proposed_weight": None,
            "weight_status": "not_available",
            "source_refs": [],
            "source_types": [],
            "retrieved_or_published_dates": [],
            "sample_size_or_source_count": "0",
            "evidence_strength": "missing",
            "confidence": "low",
            "cannot_decide_alone": True
        }
    ],
    "role_output_packet": {
        "invocation_id": invocation["invocation_id"],
        "target_agent": target_agent,
        "status": "done",
        "role_output_ref": output_ref,
        "evidence_packet_refs": [],
        "runtime_weights_ref": "merge/runtime_weights.json",
        "artifact_refs": [order["prompt_bundle_ref"]],
        "blocked_outputs": [],
        "runtime_research_tasks": [],
        "needs_user_confirmation": [],
        "handoff_to": [],
        "errors": [],
        "confidence": "medium"
    },
    "error_recovery_state": {
        "status": "not_applicable",
        "errors": [],
        "recovery_actions": [],
        "degraded_outputs": [],
        "blocked_outputs": [],
        "safe_outputs": ["role_output_packet"],
        "next_action": "continue"
    }
}
if target_agent == "learning-path-strategist":
    result["skill_gap_analysis"] = {
        "must_have_gaps": ["缺少可验证的岗位相关项目经历"],
        "nice_to_have_gaps": [],
        "project_evidence_gaps": ["需要一个能公开展示、能被追问的项目证据"],
        "interview_defensibility_gaps": []
    }
    result["learning_plan_before_application"] = {
        "status": "prepare_first",
        "skills_to_learn": ["按目标岗位补齐核心工具链和基础概念"],
        "projects_to_build": ["完成一个岗位相关的最小可运行项目，并保留 README、运行截图和代码链接"],
        "proof_artifacts": ["GitHub 仓库", "README", "demo 截图或录屏", "复盘文档"],
        "resume_conversion_conditions": ["项目跑通并能解释输入、输出、核心模块和失败边界后，才能写入简历"],
        "ready_to_apply_conditions": ["项目证据可公开检查，且简历中不把计划内容写成已完成成果"],
        "ask_hr_about": []
    }
    result["project_recommendations"] = [
        {
            "project_name": "岗位反向设计的最小可运行项目",
            "target_role_family": "AI 应用或后端实习",
            "recommended_mode": "smoke-test",
            "why_this_project": "适合项目经历不足的候选人，能在短周期内补出可验证证据。",
            "implementation_steps": [
                "选一个公开可运行仓库或自建最小业务闭环",
                "跑通核心流程并记录命令",
                "补一个岗位相关改造点",
                "整理 README、截图、代码入口和复盘"
            ],
            "proof_artifacts": ["GitHub 仓库", "README", "demo 截图", "技术复盘"],
            "resume_conversion_conditions": [
                "必须完成并能解释个人贡献后才能写成简历项目",
                "未完成内容只能写为学习计划或待补证据"
            ],
            "source_basis": ["current JD", "verified HR public post", "public GitHub repository"]
        }
    ]
if target_agent == "hr-supervisor":
    result["hr_real_question_bank"] = [
        {
            "company": "Tencent",
            "role_family": "backend or AI application internship",
            "question": "请准备说明项目经历和目标岗位要求的对应关系。",
            "question_type": "project_depth",
            "source_ref": "https://careers.tencent.com/",
            "source_type": "official_or_primary",
            "source_tier": "A",
            "source_accuracy_tier": "A",
            "source_basis": ["official company recruiting page"],
            "verbatim_or_paraphrase": "paraphrase",
            "preparation_focus": "用岗位要求、项目模块、个人贡献和可验证证据串起来回答。",
            "not_model_generated": True
        },
        {
            "company": "ByteDance",
            "role_family": "backend internship",
            "question": "这条非目标公司题目不应进入腾讯目标岗位结果。",
            "question_type": "project_depth",
            "source_ref": "https://jobs.bytedance.com/",
            "source_type": "official_or_primary",
            "source_tier": "A",
            "source_accuracy_tier": "A",
            "source_basis": ["official company recruiting page"],
            "verbatim_or_paraphrase": "paraphrase",
            "preparation_focus": "用于验证公司绑定过滤。",
            "not_model_generated": True
        }
    ]
    result["likely_interview_questions"] = [
        {
            "company": "Tencent",
            "question": "请准备说明项目经历和目标岗位要求的对应关系。",
            "source_ref": "https://careers.tencent.com/",
            "source_type": "official_or_primary",
            "source_accuracy_tier": "A",
            "not_model_generated": True
        },
        {
            "company": "ByteDance",
            "question": "这条非目标公司可能追问不应进入腾讯目标岗位结果。",
            "source_ref": "https://jobs.bytedance.com/",
            "source_type": "official_or_primary",
            "source_accuracy_tier": "A",
            "not_model_generated": True
        }
    ]
    result["resume_defensibility_checks"] = [
        "简历中的项目、技能和指标必须能被公开材料或用户经历证明。",
        "未完成的学习计划不能写成已掌握技能。"
    ]
json.dump(result, open(args.output_json, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
""".lstrip(),
        encoding="utf-8",
    )


def prepare_run_with_external_public_source(
    tmp_path: Path,
    task_type: str = "job_search",
    route: str = "job_search",
    input_text: str = "Computer science sophomore, Python, looking for AI internship",
    task_id: str = "recruitment-platform-public-jd",
) -> tuple[Path, str]:
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        task_type,
        "--input-text",
        input_text,
        "--run-root",
        str(run_root),
        "--route",
        route,
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id
    assert run_python(PLAN_BUILDER, "--run-dir", str(run_dir), "--build-prompt-bundles").returncode == 0
    assert run_python(SOURCE_PLAN_BUILDER, "--run-dir", str(run_dir)).returncode == 0
    assert run_python(PUBLIC_SOURCE_DISCOVERER, "--run-dir", str(run_dir), "--generate-query-plan-only").returncode == 0
    external_results = tmp_path / f"{run_id}-external-search-results.json"
    external_results.write_text(
        json.dumps(
            {
                "search_results": [
                    {
                        "task_id": task_id,
                        "url": "https://www.nowcoder.com/jobs/backend-intern",
                        "title": "Backend intern public JD",
                        "snippet": "Python Java internship",
                        "source_type": "recruitment_platform_jd",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    source_search = run_python(
        PUBLIC_SOURCE_SEARCHER,
        "--run-dir",
        str(run_dir),
        "--provider",
        "external-json",
        "--search-results-json",
        str(external_results),
    )
    assert source_search.returncode == 0, source_search.stderr
    search_ref = json.loads(source_search.stdout)["public_source_search_response"]["search_results_ref"]
    discover = run_python(
        PUBLIC_SOURCE_DISCOVERER,
        "--run-dir",
        str(run_dir),
        "--search-results-json",
        str(run_dir / search_ref),
    )
    assert discover.returncode == 0, discover.stderr
    return run_dir, run_id


def test_subagent_adapter_runner_executes_external_command_outputs(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "job_search",
        "--input-text",
        "Computer science sophomore, Python, looking for AI internship",
        "--run-root",
        str(run_root),
        "--route",
        "job_search",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id
    assert run_python(PLAN_BUILDER, "--run-dir", str(run_dir), "--build-prompt-bundles").returncode == 0
    assert run_python(WORK_ORDER_BUILDER, "--run-dir", str(run_dir)).returncode == 0
    adapter_script = tmp_path / "external_adapter.py"
    write_external_adapter_script(adapter_script)

    result = run_python(
        SUBAGENT_ADAPTER_RUNNER,
        "--run-dir",
        str(run_dir),
        "--adapter-command",
        sys.executable,
        "--adapter-arg",
        str(adapter_script),
    )

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)["subagent_adapter_response"]
    assert response["exit_status"] == "success"
    assert response["real_subagent_execution"] is True
    assert response["adapter_mode"] == "external-command"
    first_output = run_dir / response["output_refs"][0]
    packet = json.loads(first_output.read_text(encoding="utf-8"))["role_output_packet"]
    assert packet["status"] == "done"
    assert run_python(VALIDATOR, "--role-output", str(first_output)).returncode == 0


def test_finalizer_writes_final_package_when_role_outputs_are_done(tmp_path):
    run_dir, run_id = prepare_run_with_external_public_source(
        tmp_path,
        task_type="target_job_fit",
        route="target_job_fit",
        input_text=(
            "Computer science junior. Python and Java basics, no strong project. "
            "Target: Tencent backend or AI application internship. "
            "JD: Python, Java, SQL, LLM app."
        ),
        task_id="target-current-jd-verification",
    )
    assert run_python(WORK_ORDER_BUILDER, "--run-dir", str(run_dir)).returncode == 0
    adapter_script = tmp_path / "external_adapter.py"
    write_external_adapter_script(adapter_script)
    adapter = run_python(
        SUBAGENT_ADAPTER_RUNNER,
        "--run-dir",
        str(run_dir),
        "--adapter-command",
        sys.executable,
        "--adapter-arg",
        str(adapter_script),
    )
    assert adapter.returncode == 0, adapter.stderr

    result = run_python(FINALIZER, "--run-dir", str(run_dir), "--real-subagent-execution")

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)["finalizer_response"]
    assert response["exit_status"] == "success"
    assert response["final_package_ref"] == "final/decision_package.json"
    assert response["source_discovery_ready"] is True
    final_package = json.loads((run_dir / response["final_package_ref"]).read_text(encoding="utf-8"))
    assert final_package["decision_package"]["run_id"] == run_id
    assert final_package["decision_package"]["real_subagent_execution"] is True
    assert final_package["decision_package"]["source_discovery_ready"] is True
    assert final_package["decision_package"]["role_output_refs"]
    user_package = final_package["decision_package"]["user_facing_package"]
    assert user_package["positioning_conclusion"]
    assert user_package["public_source_index"][0]["url"].startswith("https://")
    assert len(user_package["next_three_actions"]) == 3
    assert user_package["project_recommendations"][0]["project_name"] == "岗位反向设计的最小可运行项目"
    assert "GitHub 仓库" in user_package["project_recommendations"][0]["proof_artifacts"]
    assert "必须完成并能解释个人贡献后才能写成简历项目" in user_package["project_recommendations"][0]["resume_conversion_conditions"]
    assert user_package["hr_real_questions"][0]["company"] == "Tencent"
    assert user_package["hr_real_questions"][0]["not_model_generated"] is True
    assert user_package["hr_real_questions"][0]["source_ref"].startswith("https://")
    assert user_package["hr_real_questions"][0]["source_accuracy_tier"] in {"A", "B"}
    assert user_package["likely_interview_questions"][0]["not_model_generated"] is True
    assert [item["company"] for item in user_package["hr_real_questions"]] == ["Tencent"]
    assert [item["company"] for item in user_package["likely_interview_questions"]] == ["Tencent"]
    assert "ByteDance" not in json.dumps(user_package, ensure_ascii=False)
    user_report = final_package["decision_package"]["user_facing_report_zh"]
    for heading in [
        "当前定位",
        "推荐方向/岗位池",
        "为什么适合",
        "还差什么",
        "先学什么/做什么项目",
        "简历怎么写",
        "HR/面试可能追问",
        "推荐查看的公开 URL",
        "需要问 HR 的事项",
        "下一步 3 个动作",
    ]:
        assert f"## {heading}" in user_report
    assert "岗位反向设计的最小可运行项目" in user_report
    assert "Tencent" in user_report
    assert "https://careers.tencent.com/" in user_report
    user_package_text = json.dumps(user_package, ensure_ascii=False)
    assert "blocked_outputs" not in user_package_text
    assert "run_dir" not in user_package_text
    assert "execution_log" not in user_package_text
    assert "blocked_outputs" not in user_report
    assert "runtime" not in user_report.lower()
    assert "schema" not in user_report.lower()
    assert "subagent" not in user_report.lower()
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["execution_manifest"]["current_stage"] == "final_package_ready"
    assert manifest["run_state"]["stage"] == "final_package_ready"


def test_finalizer_uses_fetched_evidence_quality_for_public_source_index(tmp_path):
    run_dir, _run_id = prepare_run_with_external_public_source(
        tmp_path,
        task_type="job_search",
        route="job_search",
        input_text="Computer science junior, Python, looking for internship.",
        task_id="official-company-career",
    )
    assert run_python(WORK_ORDER_BUILDER, "--run-dir", str(run_dir)).returncode == 0

    allowed_sources = json.loads((run_dir / "evidence" / "allowed_public_sources.generated.json").read_text(encoding="utf-8"))
    source_ref = allowed_sources["sources"][0]["source_ref"]
    fetched = {
        "evidence_packets": [
            {
                "evidence_packet": {
                    "evidence_id": "ev-generic-entrypoint",
                    "claim_id": "official-company-career",
                    "field": "current_company_or_job_requirement",
                    "source_type": "official_or_primary",
                    "source_ref": source_ref,
                    "artifact_ref": "",
                    "retrieved_or_published_date": "2026-06-28",
                    "freshness": "0_6_months",
                    "evidence_strength": "weak",
                    "inference_level": "none",
                    "privacy_class": "public",
                    "confidence": "low",
                    "may_set_final_decision": False,
                    "may_set_weight": False,
                    "short_text_entrypoint_only": False,
                    "generic_entrypoint_only": True,
                    "extraction_method": "static_fetch",
                    "excerpt": "Campus recruiting search entrypoint with filters and application links only.",
                }
            }
        ]
    }
    fetched_path = tmp_path / "fetched-entrypoint-evidence.json"
    fetched_path.write_text(json.dumps(fetched), encoding="utf-8")
    backfill = run_python(EVIDENCE_BACKFILL, "--run-dir", str(run_dir), "--evidence-json", str(fetched_path))
    assert backfill.returncode == 0, backfill.stderr

    adapter_script = tmp_path / "external_adapter.py"
    write_external_adapter_script(adapter_script)
    adapter = run_python(
        SUBAGENT_ADAPTER_RUNNER,
        "--run-dir",
        str(run_dir),
        "--adapter-command",
        sys.executable,
        "--adapter-arg",
        str(adapter_script),
    )
    assert adapter.returncode == 0, adapter.stderr

    result = run_python(FINALIZER, "--run-dir", str(run_dir), "--real-subagent-execution")

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)["finalizer_response"]
    final_package = json.loads((run_dir / response["final_package_ref"]).read_text(encoding="utf-8"))
    public_source = final_package["decision_package"]["user_facing_package"]["public_source_index"][0]
    assert public_source["may_support_application_claims"] is False
    assert public_source["evidence_strength"] == "weak"
    assert public_source["confidence"] == "low"
    assert public_source["generic_entrypoint_only"] is True


def test_finalizer_excludes_hr_questions_not_bound_to_target_or_recommended_company(tmp_path):
    run_dir, _run_id = prepare_run_with_external_public_source(
        tmp_path,
        task_type="target_job_fit",
        route="target_job_fit",
        input_text=(
            "Computer science junior. Target: Tencent backend internship. "
            "JD: Java, SQL, backend project depth."
        ),
        task_id="target-current-jd-verification",
    )
    assert run_python(WORK_ORDER_BUILDER, "--run-dir", str(run_dir)).returncode == 0
    adapter_script = tmp_path / "external_adapter.py"
    write_external_adapter_script(adapter_script)
    adapter = run_python(
        SUBAGENT_ADAPTER_RUNNER,
        "--run-dir",
        str(run_dir),
        "--adapter-command",
        sys.executable,
        "--adapter-arg",
        str(adapter_script),
    )
    assert adapter.returncode == 0, adapter.stderr

    plan = json.loads((run_dir / "invocations" / "subagent_invocation_plan.json").read_text(encoding="utf-8"))[
        "subagent_invocation_plan"
    ]
    hr_output_ref = next(
        item["output_artifact_target"]
        for item in plan["dispatch_queue"]
        if item["target_agent"] == "hr-supervisor"
    )
    hr_output_path = run_dir / hr_output_ref
    hr_output = json.loads(hr_output_path.read_text(encoding="utf-8"))
    hr_output["hr_real_question_bank"] = [
        item for item in hr_output["hr_real_question_bank"] if item["company"] == "ByteDance"
    ]
    hr_output["likely_interview_questions"] = [
        item for item in hr_output["likely_interview_questions"] if item["company"] == "ByteDance"
    ]
    hr_output_path.write_text(
        json.dumps(hr_output, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    result = run_python(FINALIZER, "--run-dir", str(run_dir), "--real-subagent-execution")

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)["finalizer_response"]
    final_package = json.loads((run_dir / response["final_package_ref"]).read_text(encoding="utf-8"))
    user_package = final_package["decision_package"]["user_facing_package"]
    assert user_package["hr_real_questions"] == []
    assert user_package["likely_interview_questions"] == []
    assert any("暂未找到目标公司或推荐岗位公司的可靠公开 HR 话术" in item for item in user_package["currently_unavailable"])
    assert "ByteDance" not in json.dumps(user_package, ensure_ascii=False)


def test_finalizer_allows_limited_final_package_with_only_exact_fields_blocked(tmp_path):
    run_dir, run_id = prepare_run_with_external_public_source(
        tmp_path,
        task_type="target_job_fit",
        route="target_job_fit",
        input_text=(
            "Computer science sophomore, Python and Java. "
            "Target: Tencent backend development internship. "
            "JD: Java, Spring, MySQL, Redis, distributed systems."
        ),
        task_id="target-current-jd-verification",
    )
    plan = json.loads((run_dir / "invocations" / "subagent_invocation_plan.json").read_text(encoding="utf-8"))[
        "subagent_invocation_plan"
    ]
    exact_blocked = [
        "fit_score",
        "application_priority",
        "targeted_resume_tailoring",
        "company_specific_skill_weight_ranking",
    ]
    for item in plan["dispatch_queue"]:
        invocation = json.loads((run_dir / item["invocation_ref"]).read_text(encoding="utf-8"))[
            "subagent_invocation"
        ]
        output = {
            "invocation_ref": item["invocation_ref"],
            "role": item["target_agent"],
            "task_summary": "Prepared safe target-job fit output with exact fields unavailable.",
            "inputs_used": [item["prompt_bundle_ref"]],
            "database_files_used": [],
            "source_notes": [],
            "runtime_scope": "conditional_runtime_judgment",
            "judgment_allowed": "conditional_with_runtime_evidence",
            "judgment_status": "evidence_bound_judgment",
            "decision_owner": "local_subagent",
            "runtime_preconditions": {
                "has_current_jd": True,
                "has_target_company": True,
                "has_user_constraints": False,
                "has_user_consent": False,
                "job_direction_blocked": False,
            },
            "evidence_basis": [],
            "repository_prior_usage": [],
            "weight_provenance": [
                {
                    "parameter": "exact_fit_score",
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
            ],
            "role_output_packet": {
                "invocation_id": invocation["invocation_id"],
                "target_agent": item["target_agent"],
                "status": "done_with_warnings",
                "role_output_ref": item["output_artifact_target"],
                "evidence_packet_refs": [],
                "runtime_weights_ref": "merge/runtime_weights.json",
                "artifact_refs": [item["prompt_bundle_ref"]],
                "blocked_outputs": exact_blocked,
                "runtime_research_tasks": [],
                "needs_user_confirmation": [],
                "handoff_to": [],
                "errors": [],
                "confidence": "medium",
            },
            "error_recovery_state": {
                "status": "degraded",
                "errors": [],
                "recovery_actions": ["continue_with_prepare_first_package"],
                "degraded_outputs": exact_blocked,
                "blocked_outputs": exact_blocked,
                "safe_outputs": [
                    "current_fit_assessment",
                    "application_readiness_decision",
                    "learning_plan_before_application",
                    "recommended_application_targets",
                ],
                "next_action": "continue",
            },
            "current_fit_assessment": {"status": "evidence_bound"},
            "application_readiness_decision": {"status": "prepare_first"},
            "learning_plan_before_application": {"status": "prepare_first"},
        }
        output_path = run_dir / item["output_artifact_target"]
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output["adapter_metadata"] = {
            "run_id": run_id,
            "target_agent": item["target_agent"],
            "adapter_mode": "external-command",
            "real_subagent_execution": True,
            "mock_or_seed_source": False,
        }
        output_path.write_text(json.dumps(output), encoding="utf-8")

    result = run_python(FINALIZER, "--run-dir", str(run_dir), "--real-subagent-execution")

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)["finalizer_response"]
    final_package = json.loads((run_dir / response["final_package_ref"]).read_text(encoding="utf-8"))[
        "decision_package"
    ]
    assert final_package["run_id"] == run_id
    assert set(final_package["blocked_outputs"]) == set(exact_blocked)
    assert "current_fit_assessment" not in final_package["blocked_outputs"]
    assert "learning_plan_before_application" not in final_package["blocked_outputs"]
    assert final_package["degraded_outputs"]


def test_finalizer_rejects_limited_package_with_non_exact_blockers(tmp_path):
    run_dir, run_id = prepare_run_with_external_public_source(tmp_path)
    plan = json.loads((run_dir / "invocations" / "subagent_invocation_plan.json").read_text(encoding="utf-8"))[
        "subagent_invocation_plan"
    ]
    for index, item in enumerate(plan["dispatch_queue"]):
        invocation = json.loads((run_dir / item["invocation_ref"]).read_text(encoding="utf-8"))[
            "subagent_invocation"
        ]
        blockers = ["blocked_application_targets_without_public_url"] if index == 0 else []
        output = {
            "invocation_ref": item["invocation_ref"],
            "role_output_packet": {
                "invocation_id": invocation["invocation_id"],
                "target_agent": item["target_agent"],
                "status": "done_with_warnings",
                "role_output_ref": item["output_artifact_target"],
                "evidence_packet_refs": [],
                "runtime_weights_ref": "merge/runtime_weights.json",
                "artifact_refs": [item["prompt_bundle_ref"]],
                "blocked_outputs": blockers,
                "runtime_research_tasks": [],
                "needs_user_confirmation": [],
                "handoff_to": [],
                "errors": [],
                "confidence": "medium",
            },
            "error_recovery_state": {
                "status": "degraded" if blockers else "not_applicable",
                "errors": [],
                "recovery_actions": [],
                "degraded_outputs": blockers,
                "blocked_outputs": blockers,
                "safe_outputs": ["role_output_packet"],
                "next_action": "continue",
            },
            "adapter_metadata": {
                "run_id": run_id,
                "target_agent": item["target_agent"],
                "adapter_mode": "external-command",
                "real_subagent_execution": True,
                "mock_or_seed_source": False,
            },
        }
        output_path = run_dir / item["output_artifact_target"]
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(output), encoding="utf-8")

    result = run_python(FINALIZER, "--run-dir", str(run_dir), "--real-subagent-execution")

    assert result.returncode == 1
    assert "final-package blockers" in result.stderr
    assert "blocked_application_targets_without_public_url" in result.stderr


def test_manual_controller_backfill_can_finalize_with_explicit_execution_metadata(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "job_search",
        "--input-text",
        "Computer science sophomore, Python, looking for AI internship",
        "--run-root",
        str(run_root),
        "--route",
        "job_search",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id
    assert run_python(PLAN_BUILDER, "--run-dir", str(run_dir), "--build-prompt-bundles").returncode == 0
    assert run_python(SOURCE_PLAN_BUILDER, "--run-dir", str(run_dir)).returncode == 0
    assert run_python(PUBLIC_SOURCE_DISCOVERER, "--run-dir", str(run_dir), "--generate-query-plan-only").returncode == 0
    external_results = tmp_path / "external-search-results.json"
    external_results.write_text(
        json.dumps(
            {
                "search_results": [
                    {
                        "task_id": "recruitment-platform-public-jd",
                        "url": "https://www.nowcoder.com/jobs/backend-intern",
                        "title": "Backend intern public JD",
                        "snippet": "Python Java internship",
                        "source_type": "recruitment_platform_jd",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    source_search = run_python(
        PUBLIC_SOURCE_SEARCHER,
        "--run-dir",
        str(run_dir),
        "--provider",
        "external-json",
        "--search-results-json",
        str(external_results),
    )
    assert source_search.returncode == 0, source_search.stderr
    search_ref = json.loads(source_search.stdout)["public_source_search_response"]["search_results_ref"]
    discover = run_python(
        PUBLIC_SOURCE_DISCOVERER,
        "--run-dir",
        str(run_dir),
        "--search-results-json",
        str(run_dir / search_ref),
    )
    assert discover.returncode == 0, discover.stderr

    plan = json.loads((run_dir / "invocations" / "subagent_invocation_plan.json").read_text(encoding="utf-8"))[
        "subagent_invocation_plan"
    ]
    backfill_args = []
    for item in plan["dispatch_queue"]:
        invocation = json.loads((run_dir / item["invocation_ref"]).read_text(encoding="utf-8"))[
            "subagent_invocation"
        ]
        output_path = tmp_path / f"{item['target_agent']}.manual-output.json"
        output = {
            "invocation_ref": item["invocation_ref"],
            "role": item["target_agent"],
            "task_summary": "Manual controller separated subagent output.",
            "inputs_used": [item["prompt_bundle_ref"]],
            "database_files_used": [],
            "source_notes": [],
            "runtime_scope": "evidence_collection",
            "judgment_allowed": "evidence_bound_only",
            "judgment_status": "evidence_bound_judgment",
            "decision_owner": "local_subagent",
            "runtime_preconditions": {
                "has_current_jd": True,
                "has_target_company": True,
                "has_user_constraints": False,
                "has_user_consent": False,
                "job_direction_blocked": False,
            },
            "evidence_basis": [],
            "repository_prior_usage": [],
            "weight_provenance": [],
            "role_output_packet": {
                "invocation_id": invocation["invocation_id"],
                "target_agent": item["target_agent"],
                "status": "done_with_warnings",
                "role_output_ref": item["output_artifact_target"],
                "evidence_packet_refs": [],
                "runtime_weights_ref": "merge/runtime_weights.json",
                "artifact_refs": [item["prompt_bundle_ref"]],
                "blocked_outputs": [],
                "runtime_research_tasks": [],
                "needs_user_confirmation": [],
                "handoff_to": [],
                "errors": [],
                "confidence": "medium",
            },
            "error_recovery_state": {
                "status": "not_applicable",
                "errors": [],
                "recovery_actions": [],
                "degraded_outputs": [],
                "blocked_outputs": [],
                "safe_outputs": ["role_output_packet"],
                "next_action": "continue",
            },
        }
        output_path.write_text(json.dumps(output), encoding="utf-8")
        backfill_args.extend(["--backfill-output", f"{item['target_agent']}={output_path}"])

    backfill = run_python(
        PLAN_EXECUTOR,
        "--run-dir",
        str(run_dir),
        "--manual-controller-execution",
        *backfill_args,
    )
    assert backfill.returncode == 0, backfill.stderr
    first_output = json.loads((run_dir / plan["dispatch_queue"][0]["output_artifact_target"]).read_text(encoding="utf-8"))
    assert first_output["adapter_metadata"]["adapter_mode"] == "manual-controller"
    assert first_output["adapter_metadata"]["real_subagent_execution"] is True

    result = run_python(
        FINALIZER,
        "--run-dir",
        str(run_dir),
        "--real-subagent-execution",
        "--execution-mode",
        "manual-controller",
    )

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)["finalizer_response"]
    final_package = json.loads((run_dir / response["final_package_ref"]).read_text(encoding="utf-8"))
    assert final_package["decision_package"]["real_subagent_execution"] is True
    assert final_package["decision_package"]["execution_mode"] == "manual-controller"


def test_manual_controller_backfill_overwrites_mock_blocked_outputs(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "job_search",
        "--input-text",
        "Software engineering junior, Python and C++, looking for backend internship",
        "--run-root",
        str(run_root),
        "--route",
        "job_search",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id
    assert run_python(PLAN_BUILDER, "--run-dir", str(run_dir), "--build-prompt-bundles").returncode == 0
    assert run_python(WORK_ORDER_BUILDER, "--run-dir", str(run_dir)).returncode == 0
    mock = run_python(SUBAGENT_ADAPTER_RUNNER, "--run-dir", str(run_dir), "--mock-blocked")
    assert mock.returncode == 0, mock.stderr

    plan = json.loads((run_dir / "invocations" / "subagent_invocation_plan.json").read_text(encoding="utf-8"))[
        "subagent_invocation_plan"
    ]
    first = plan["dispatch_queue"][0]
    first_output_path = run_dir / first["output_artifact_target"]
    mock_output = json.loads(first_output_path.read_text(encoding="utf-8"))
    assert mock_output["adapter_metadata"]["adapter_mode"] == "mock-blocked"

    invocation = json.loads((run_dir / first["invocation_ref"]).read_text(encoding="utf-8"))[
        "subagent_invocation"
    ]
    manual_output_path = tmp_path / "manual-output.json"
    manual_output = {
        "invocation_ref": first["invocation_ref"],
        "role_output_packet": {
            "invocation_id": invocation["invocation_id"],
            "target_agent": first["target_agent"],
            "status": "done_with_warnings",
            "role_output_ref": first["output_artifact_target"],
            "evidence_packet_refs": [],
            "runtime_weights_ref": "merge/runtime_weights.json",
            "artifact_refs": [first["prompt_bundle_ref"]],
            "blocked_outputs": ["fit_score"],
            "runtime_research_tasks": [],
            "needs_user_confirmation": [],
            "handoff_to": [],
            "errors": [],
            "confidence": "medium",
        },
        "error_recovery_state": {
            "status": "degraded",
            "errors": [],
            "recovery_actions": ["continue_with_safe_partial_output"],
            "degraded_outputs": ["fit_score"],
            "blocked_outputs": ["fit_score"],
            "safe_outputs": ["role_output_packet"],
            "next_action": "continue",
        },
    }
    manual_output_path.write_text(json.dumps(manual_output), encoding="utf-8")

    backfill = run_python(
        PLAN_EXECUTOR,
        "--run-dir",
        str(run_dir),
        "--manual-controller-execution",
        "--backfill-output",
        f"{first['target_agent']}={manual_output_path}",
    )

    assert backfill.returncode == 0, backfill.stderr
    final_output = json.loads(first_output_path.read_text(encoding="utf-8"))
    assert final_output["role_output_packet"]["status"] == "done_with_warnings"
    assert final_output["adapter_metadata"]["adapter_mode"] == "manual-controller"
    assert final_output["adapter_metadata"]["real_subagent_execution"] is True
    assert final_output["adapter_metadata"]["mock_or_seed_source"] is False


def test_manual_controller_backfill_rejects_existing_mock_output_as_source(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "job_search",
        "--input-text",
        "Software engineering junior, Python and C++, looking for backend internship",
        "--run-root",
        str(run_root),
        "--route",
        "job_search",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id
    assert run_python(PLAN_BUILDER, "--run-dir", str(run_dir), "--build-prompt-bundles").returncode == 0
    assert run_python(WORK_ORDER_BUILDER, "--run-dir", str(run_dir)).returncode == 0
    mock = run_python(SUBAGENT_ADAPTER_RUNNER, "--run-dir", str(run_dir), "--mock-blocked")
    assert mock.returncode == 0, mock.stderr

    plan = json.loads((run_dir / "invocations" / "subagent_invocation_plan.json").read_text(encoding="utf-8"))[
        "subagent_invocation_plan"
    ]
    first = plan["dispatch_queue"][0]
    existing_mock_output = run_dir / first["output_artifact_target"]

    backfill = run_python(
        PLAN_EXECUTOR,
        "--run-dir",
        str(run_dir),
        "--manual-controller-execution",
        "--backfill-output",
        f"{first['target_agent']}={existing_mock_output}",
    )

    assert backfill.returncode == 1
    assert "mock" in backfill.stderr.lower()
    assert "manual-controller" in backfill.stderr


def test_subagent_adapter_runner_writes_schema_valid_mock_outputs(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "job_search",
        "--input-text",
        "Computer science sophomore, Python, looking for AI internship",
        "--run-root",
        str(run_root),
        "--route",
        "job_search",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id
    assert run_python(PLAN_BUILDER, "--run-dir", str(run_dir), "--build-prompt-bundles").returncode == 0
    assert run_python(WORK_ORDER_BUILDER, "--run-dir", str(run_dir)).returncode == 0

    result = run_python(SUBAGENT_ADAPTER_RUNNER, "--run-dir", str(run_dir), "--mock-blocked")

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)["subagent_adapter_response"]
    assert response["exit_status"] == "blocked"
    assert response["real_subagent_execution"] is False
    assert response["output_refs"]
    first_output = json.loads((run_dir / response["output_refs"][0]).read_text(encoding="utf-8"))
    packet = first_output["role_output_packet"]
    assert packet["status"] == "blocked"
    assert packet["target_agent"]
    assert first_output["error_recovery_state"]["next_action"] == "configure_real_adapter"


def test_one_command_runner_creates_blocked_user_side_run(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    result = run_python(
        CAREER_PIPELINE_RUNNER,
        "--task-type",
        "target_job_fit",
        "--route",
        "target_job_fit",
        "--input-text",
        "Computer science senior. Assess fit for Tencent backend role. JD: Java and MySQL.",
        "--run-root",
        str(run_root),
        "--source-adapter",
        "seed",
        "--subagent-adapter",
        "mock-blocked",
    )

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)["career_pipeline_run_response"]
    assert response["exit_status"] == "blocked"
    assert response["real_subagent_execution"] is False
    assert response["source_discovery_ready"] is True
    assert response["run_id"]
    run_dir = run_root / response["run_id"]
    assert (run_dir / "evidence" / "public_source_research_plan.json").is_file()
    assert (run_dir / "evidence" / "search_results.generated.json").is_file()
    assert (run_dir / "evidence" / "allowed_public_sources.generated.json").is_file()
    assert (run_dir / "invocations" / "subagent_work_orders.json").is_file()
    assert response["blocked_by"]


def test_product_flow_runner_returns_user_facing_status_without_internal_adapter_terms(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    result = run_python(
        PRODUCT_FLOW_RUNNER,
        "--task-type",
        "job_search",
        "--route",
        "job_search",
        "--input-text",
        "我是计算机相关专业大三，会一点 Python，想找实习但不知道投什么。",
        "--run-root",
        str(run_root),
    )

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)["product_flow_response"]
    assert response["exit_status"] == "needs_real_role_execution"
    assert response["run_id"]
    assert response["user_facing_status"]["skill_intro"].startswith("我是 Career Pipeline")
    assert response["user_facing_status"]["known_information_summary"]
    assert response["user_facing_status"]["what_can_be_done_now"]
    assert response["user_facing_status"]["missing_user_owned_facts"]
    assert len(response["user_facing_status"]["next_three_actions"]) == 3
    assert response["controller_handoff"]["work_orders_ref"] == "invocations/subagent_work_orders.json"
    assert response["controller_handoff"]["public_source_query_plan_ref"] == "evidence/public_source_discovery_log.json"
    assert response["controller_handoff"]["dispatch_strategy"] == "batched_artifact_handoff"
    text = json.dumps(response["user_facing_status"], ensure_ascii=False).lower()
    for forbidden in ["mock-blocked", "external-json", "adapter", "subagent", "runner", "schema", "run_dir"]:
        assert forbidden not in text

    user_report = run_root / response["run_id"] / response["user_facing_status_ref"]
    assert user_report.is_file()
    report_text = user_report.read_text(encoding="utf-8").lower()
    assert "我是 career pipeline" in report_text
    for forbidden in ["mock-blocked", "external-json", "adapter", "schema", "run_dir"]:
        assert forbidden not in report_text


def test_product_flow_runner_prepares_real_user_run_instead_of_contract_simulation(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    result = run_python(
        PRODUCT_FLOW_RUNNER,
        "--task-type",
        "job_search",
        "--route",
        "job_search",
        "--input-text",
        "Computer science junior, a little Python, course project only, looking for an internship but no target role.",
        "--run-root",
        str(run_root),
    )

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)["product_flow_response"]
    run_dir = run_root / response["run_id"]

    context = json.loads(
        (run_dir / "input" / "normalized" / "runtime_context_packet.json").read_text(encoding="utf-8")
    )["runtime_context_packet"]
    assert context["execution_intent"] == "product_real_user_flow"
    assert "simulate local runtime contract" not in context["user_goal"]
    for safe_output in [
        "application_direction",
        "application_strategy",
        "learning_plan_before_application",
    ]:
        assert safe_output not in context["blocked_outputs"]
    for exact_output in [
        "fit_score",
        "application_priority",
        "targeted_resume_tailoring",
        "company_specific_skill_weight_ranking",
    ]:
        assert exact_output in context["blocked_outputs"]

    plan = json.loads((run_dir / response["controller_handoff"]["subagent_plan_ref"]).read_text(encoding="utf-8"))[
        "subagent_invocation_plan"
    ]
    agents = [item["target_agent"] for item in plan["dispatch_queue"]]
    assert agents == [
        "major-cluster-classifier",
        "profile-extractor",
        "job-scout",
        "jd-analyzer",
        "match-strategist",
        "learning-path-strategist",
        "resume-format-gate",
        "resume-architect",
        "hr-supervisor",
        "factual-reviewer",
    ]
    assert plan["dispatch_batches"][-1]["batch_id"] == "hr_and_factual_gates"

    job_scout_injection = json.loads(
        (run_dir / "injections" / "job-scout.secondary_prompt_injection.json").read_text(encoding="utf-8")
    )["secondary_prompt_injection"]
    role_context = job_scout_injection["role_specific_context"]
    assert role_context["execution_scope"] == "product_real_user_flow_pending_real_roles"
    assert "simulation_scope" not in role_context
    assert role_context["safe_prepare_first_and_explore_allowed"] is True
    assert role_context["exact_score_priority_and_tailoring_require_current_jd_public_evidence"] is True
    assert "application_strategy" not in job_scout_injection["blocked_outputs"]


def test_product_flow_without_target_includes_general_resume_generation_gate(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    result = run_python(
        PRODUCT_FLOW_RUNNER,
        "--task-type",
        "job_search",
        "--route",
        "job_search",
        "--input-text",
        "我是计算机相关专业大三，会一点 Python，想找实习但不知道投什么。",
        "--run-root",
        str(run_root),
    )

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)["product_flow_response"]
    run_dir = run_root / response["run_id"]

    context = json.loads(
        (run_dir / "input" / "normalized" / "runtime_context_packet.json").read_text(encoding="utf-8")
    )["runtime_context_packet"]
    resume_context = context["resume_generation_context"]
    assert resume_context["default_resume_version_when_no_target"] == "campus_general_cn_one_page"
    assert resume_context["general_resume_draft_allowed_without_target"] is True
    assert resume_context["tailored_resume_requires_concrete_target"] is True
    assert resume_context["required_delivery_formats"] == ["docx", "pdf", "image"]
    assert "general_resume_draft" not in context["blocked_outputs"]
    assert "final_resume_draft" not in context["blocked_outputs"]
    assert "targeted_resume_tailoring" in context["blocked_outputs"]

    plan = json.loads((run_dir / response["controller_handoff"]["subagent_plan_ref"]).read_text(encoding="utf-8"))[
        "subagent_invocation_plan"
    ]
    agents = [item["target_agent"] for item in plan["dispatch_queue"]]
    assert agents == [
        "major-cluster-classifier",
        "profile-extractor",
        "job-scout",
        "jd-analyzer",
        "match-strategist",
        "learning-path-strategist",
        "resume-format-gate",
        "resume-architect",
        "hr-supervisor",
        "factual-reviewer",
    ]
    assert plan["dispatch_batches"][-2]["batch_id"] == "branding_and_resume"
    assert plan["dispatch_batches"][-1]["batch_id"] == "hr_and_factual_gates"

    gate_injection = json.loads(
        (run_dir / "injections" / "resume-format-gate.secondary_prompt_injection.json").read_text(encoding="utf-8")
    )["secondary_prompt_injection"]
    architect_injection = json.loads(
        (run_dir / "injections" / "resume-architect.secondary_prompt_injection.json").read_text(encoding="utf-8")
    )["secondary_prompt_injection"]
    assert "resume_generation_context" in gate_injection["role_specific_context"]
    assert "final_resume_draft" in architect_injection["required_output_fields"]
    assert "growth_resume_preview" in architect_injection["required_output_fields"]
    assert "resume_delivery_artifacts" in architect_injection["required_output_fields"]
    assert "general_resume_draft" not in architect_injection["blocked_outputs"]


def test_product_flow_removes_simulated_role_outputs_from_manifest(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    result = run_python(
        PRODUCT_FLOW_RUNNER,
        "--task-type",
        "job_search",
        "--route",
        "job_search",
        "--input-text",
        "Computer science junior, Python, looking for internship but no target role.",
        "--run-root",
        str(run_root),
    )

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)["product_flow_response"]
    run_dir = run_root / response["run_id"]
    assert not list((run_dir / "agents").glob("*/output.json"))
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    artifact_types = [
        ref["artifact_type"]
        for ref in manifest["execution_manifest"]["artifact_refs"]
        if isinstance(ref, dict)
    ]
    assert "subagent_output" not in artifact_types
    assert manifest["run_state"]["completed_agents"] == []
    assert manifest["run_state"]["blocked_agents"] == []


def test_public_source_fetcher_downgrades_tiny_entrypoint_text(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "job_search",
        "--input-text",
        "Computer science junior, Python, looking for internship.",
        "--run-root",
        str(run_root),
        "--route",
        "job_search",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id
    assert run_python(SOURCE_PLAN_BUILDER, "--run-dir", str(run_dir)).returncode == 0

    tiny_source = tmp_path / "tiny-entrypoint.html"
    tiny_source.write_text("<html><body>招聘</body></html>", encoding="utf-8")
    sources_path = tmp_path / "sources.json"
    sources_path.write_text(
        json.dumps(
            {
                "sources": [
                    {
                        "task_id": "official-company-career",
                        "source_type": "official_or_primary",
                        "source_ref": tiny_source.as_uri(),
                        "field": "current_company_or_job_requirement",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    fetch = run_python(
        PUBLIC_SOURCE_FETCHER,
        "--run-dir",
        str(run_dir),
        "--sources-json",
        str(sources_path),
    )

    assert fetch.returncode == 0, fetch.stderr
    response = json.loads(fetch.stdout)["public_source_fetch_response"]
    evidence = json.loads((run_dir / response["evidence_json_ref"]).read_text(encoding="utf-8"))
    packet = evidence["evidence_packets"][0]["evidence_packet"]
    assert packet["evidence_strength"] == "weak"
    assert packet["confidence"] == "low"
    assert packet["may_set_final_decision"] is False
    assert packet["may_set_weight"] is False
    assert packet["short_text_entrypoint_only"] is True or packet["generic_entrypoint_only"] is True


def test_public_source_fetcher_downgrades_long_generic_recruiting_entrypoint(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "job_search",
        "--input-text",
        "Computer science junior, Python, looking for internship.",
        "--run-root",
        str(run_root),
        "--route",
        "job_search",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id
    assert run_python(SOURCE_PLAN_BUILDER, "--run-dir", str(run_dir)).returncode == 0

    entrypoint_source = tmp_path / "long-entrypoint.html"
    entrypoint_source.write_text(
        "<html><body><h1>Campus Recruiting</h1>"
        "<p>Search jobs, filter city, choose category, submit application, join talent community.</p>"
        "<p>Campus recruiting internship full-time school hiring campus talk job list apply now.</p>"
        "<p>Open positions page for students. Explore companies, locations, and events.</p>"
        "</body></html>",
        encoding="utf-8",
    )
    sources_path = tmp_path / "sources.json"
    sources_path.write_text(
        json.dumps(
            {
                "sources": [
                    {
                        "task_id": "official-company-career",
                        "source_type": "official_or_primary",
                        "source_ref": entrypoint_source.as_uri(),
                        "field": "current_company_or_job_requirement",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    fetch = run_python(
        PUBLIC_SOURCE_FETCHER,
        "--run-dir",
        str(run_dir),
        "--sources-json",
        str(sources_path),
    )

    assert fetch.returncode == 0, fetch.stderr
    response = json.loads(fetch.stdout)["public_source_fetch_response"]
    evidence = json.loads((run_dir / response["evidence_json_ref"]).read_text(encoding="utf-8"))
    packet = evidence["evidence_packets"][0]["evidence_packet"]
    assert packet["evidence_strength"] == "weak"
    assert packet["confidence"] == "low"
    assert packet["may_set_final_decision"] is False
    assert packet["may_set_weight"] is False
    assert packet["generic_entrypoint_only"] is True


def test_public_source_fetcher_downgrades_metadata_marked_entrypoint(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "job_search",
        "--input-text",
        "Computer science junior, Python, looking for internship.",
        "--run-root",
        str(run_root),
        "--route",
        "job_search",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id
    assert run_python(SOURCE_PLAN_BUILDER, "--run-dir", str(run_dir)).returncode == 0

    source_html = tmp_path / "campus-entrypoint-with-loaded-content.html"
    source_html.write_text(
        "<html><body><h1>Campus Recruiting</h1>"
        "<p>AI application internship, backend engineer, Python, Java, SQL, project practice.</p>"
        "<p>This homepage links to many job detail pages and campus events.</p>"
        "</body></html>",
        encoding="utf-8",
    )
    sources_path = tmp_path / "sources.json"
    sources_path.write_text(
        json.dumps(
            {
                "sources": [
                    {
                        "task_id": "official-company-career",
                        "source_type": "official_or_primary",
                        "source_ref": source_html.as_uri(),
                        "field": "current_company_or_job_requirement",
                        "title": "ByteDance campus recruiting public entry",
                        "snippet": "Official campus recruitment entrypoint for internship and campus positions.",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    fetch = run_python(
        PUBLIC_SOURCE_FETCHER,
        "--run-dir",
        str(run_dir),
        "--sources-json",
        str(sources_path),
    )

    assert fetch.returncode == 0, fetch.stderr
    response = json.loads(fetch.stdout)["public_source_fetch_response"]
    evidence = json.loads((run_dir / response["evidence_json_ref"]).read_text(encoding="utf-8"))
    packet = evidence["evidence_packets"][0]["evidence_packet"]
    assert packet["evidence_strength"] == "weak"
    assert packet["confidence"] == "low"
    assert packet["may_set_final_decision"] is False
    assert packet["may_set_weight"] is False
    assert packet["generic_entrypoint_only"] is True


def test_public_source_result_collector_parses_multiline_notes_metadata(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "job_search",
        "--input-text",
        "Computer science junior, Python, looking for internship.",
        "--run-root",
        str(run_root),
        "--route",
        "job_search",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id
    assert run_python(SOURCE_PLAN_BUILDER, "--run-dir", str(run_dir)).returncode == 0

    notes = tmp_path / "source-notes.md"
    notes.write_text(
        """
- task_id: recruitment-platform-public-jd
  url: https://www.nowcoder.com/jobs/detail/123
  title: Python 后端实习公开 JD
  source_type_hint: recruitment_platform_jd
  snippet: Python、SQL、API、Linux。
""".strip(),
        encoding="utf-8",
    )

    collect = run_python(
        PUBLIC_SOURCE_RESULT_COLLECTOR,
        "--run-dir",
        str(run_dir),
        "--notes-md",
        str(notes),
    )

    assert collect.returncode == 0, collect.stderr
    response = json.loads(collect.stdout)["public_source_result_collection_response"]
    results = json.loads((run_dir / response["search_results_ref"]).read_text(encoding="utf-8"))["search_results"]
    assert results[0]["title"] == "Python 后端实习公开 JD"
    assert results[0]["snippet"] == "Python、SQL、API、Linux。"
    assert results[0]["source_type"] == "recruitment_platform_jd"
    assert results[0]["task_id"] == "recruitment-platform-public-jd"


def test_one_command_runner_finalizes_with_external_adapters(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    external_results = tmp_path / "external-search-results.json"
    external_results.write_text(
        json.dumps(
            {
                "search_results": [
                    {
                        "task_id": "recruitment-platform-public-jd",
                        "url": "https://www.nowcoder.com/jobs/backend-intern",
                        "title": "Backend intern public JD",
                        "snippet": "Python Java internship",
                        "source_type": "recruitment_platform_jd",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    adapter_script = tmp_path / "external_adapter.py"
    write_external_adapter_script(adapter_script)

    result = run_python(
        CAREER_PIPELINE_RUNNER,
        "--task-type",
        "job_search",
        "--route",
        "job_search",
        "--input-text",
        "Computer science sophomore, Python, looking for AI internship",
        "--run-root",
        str(run_root),
        "--source-adapter",
        "external-json",
        "--search-results-json",
        str(external_results),
        "--subagent-adapter",
        "external-command",
        "--adapter-command",
        sys.executable,
        "--adapter-arg",
        str(adapter_script),
        "--finalize",
    )

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)["career_pipeline_run_response"]
    assert response["exit_status"] == "success"
    assert response["real_subagent_execution"] is True
    assert response["source_discovery_ready"] is True
    assert response["final_package_ref"] == "final/decision_package.json"
    run_dir = run_root / response["run_id"]
    assert (run_dir / response["final_package_ref"]).is_file()


def test_simulator_routes_non_engineering_major_to_pending_domain(tmp_path):
    result = run_python(
        SIMULATOR,
        "--task-type",
        "major_positioning",
        "--input-text",
        "I am a mathematics junior with Python and statistics, considering AI algorithm roles.",
        "--run-root",
        str(tmp_path / ".career-pipeline-runs"),
        "--route",
        "major_positioning",
    )

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)
    run_dir = tmp_path / ".career-pipeline-runs" / response["runner_response"]["run_id"]
    context = json.loads(
        (run_dir / "input" / "normalized" / "runtime_context_packet.json").read_text(encoding="utf-8")
    )["runtime_context_packet"]
    assert context["discipline_domain"] == "science"
    assert context["major_and_discipline"]["taxonomy_status"] == "pending_static_database"
    assert context["major_and_discipline"]["normalized_major"] == "mathematics"
    assert "domain_static_taxonomy" in context["blocked_outputs"]


def test_public_source_fetcher_rejects_login_only_sources(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "job_search",
        "--input-text",
        "Computer science sophomore, Python, looking for AI internship",
        "--run-root",
        str(run_root),
        "--route",
        "job_search",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id
    assert run_python(SOURCE_PLAN_BUILDER, "--run-dir", str(run_dir)).returncode == 0

    sources = {
        "sources": [
            {
                "task_id": "recruitment-platform-public-jd",
                "source_type": "login_only_page",
                "source_ref": "https://example.com/login-only",
                "field": "jd_requirement",
            }
        ]
    }
    sources_path = tmp_path / "bad-sources.json"
    sources_path.write_text(json.dumps(sources), encoding="utf-8")

    result = run_python(PUBLIC_SOURCE_FETCHER, "--run-dir", str(run_dir), "--sources-json", str(sources_path))

    assert result.returncode == 1
    assert "login_only_page" in result.stderr


def test_validator_rejects_injection_without_runtime_context_packet(tmp_path):
    packet = {
        "secondary_prompt_injections": [
            {
                "target_agent": "job-scout",
                "base_prompt_ref": ".codex/agents/job-scout.toml",
                "runtime_context_packet_ref": "",
                "role_specific_context": {"goal": "find internship options"},
                "allowed_user_facts": ["major_name"],
                "research_tasks": [{"question": "collect current public JDs"}],
                "hard_data_weight_tasks": [{"parameter": "skill_weight"}],
                "database_files_to_read": ["data/major_taxonomy/summary.json"],
                "source_policy_refs": [".agents/skills/career-pipeline/references/source-policy.md"],
                "invocation_contract": {
                    "invocation_id": "inv-001",
                    "run_id": "run-test",
                    "target_agent": "job-scout",
                    "base_prompt_ref": ".codex/agents/job-scout.toml",
                    "secondary_prompt_injection_ref": "injections/job-scout.secondary_prompt_injection.json",
                    "runtime_context_packet_ref": "",
                    "input_packet_ref": "invocations/job-scout.input_packet.json",
                    "allowed_user_facts_ref": "invocations/job-scout.allowed_user_facts.json",
                    "output_artifact_target": "agents/job-scout/output.json",
                    "privacy_constraints": ["redact_contact_fields"],
                    "expected_artifact_types": ["subagent_output"],
                    "required_log_events": ["dispatch", "receive_output"],
                    "on_failure": "return_blocked",
                },
                "required_output_fields": ["role_output_packet"],
                "handoff_contract": ["return blockers to orchestrator"],
                "debate_contract": ["preserve weak evidence challenges"],
            }
        ]
    }
    packet_path = tmp_path / "missing-context.json"
    packet_path.write_text(json.dumps(packet), encoding="utf-8")

    result = run_python(VALIDATOR, "--injections", str(packet_path))

    assert result.returncode == 1
    assert "runtime_context_packet_ref" in result.stderr


def test_validator_converts_secondary_injection_to_invocation_packet(tmp_path):
    packet = {
        "secondary_prompt_injections": [
            {
                "target_agent": "job-scout",
                "base_prompt_ref": ".codex/agents/job-scout.toml",
                "runtime_context_packet_ref": "input/normalized/runtime_context_packet.json",
                "role_specific_context": {"goal": "find internship options"},
                "allowed_user_facts": ["major_name", "grade_or_year"],
                "research_tasks": [{"question": "collect current public JDs"}],
                "hard_data_weight_tasks": [{"parameter": "skill_weight"}],
                "database_files_to_read": ["data/major_taxonomy/summary.json"],
                "source_policy_refs": [".agents/skills/career-pipeline/references/source-policy.md"],
                "invocation_contract": {
                    "invocation_id": "inv-001",
                    "run_id": "run-test",
                    "target_agent": "job-scout",
                    "base_prompt_ref": ".codex/agents/job-scout.toml",
                    "secondary_prompt_injection_ref": "injections/job-scout.secondary_prompt_injection.json",
                    "runtime_context_packet_ref": "input/normalized/runtime_context_packet.json",
                    "input_packet_ref": "invocations/job-scout.input_packet.json",
                    "allowed_user_facts_ref": "invocations/job-scout.allowed_user_facts.json",
                    "database_files_to_read": ["data/major_taxonomy/summary.json"],
                    "source_policy_refs": [".agents/skills/career-pipeline/references/source-policy.md"],
                    "research_tasks": [{"question": "collect current public JDs"}],
                    "hard_data_weight_tasks": [{"parameter": "skill_weight"}],
                    "required_output_fields": ["role_output_packet"],
                    "output_artifact_target": "agents/job-scout/output.json",
                    "privacy_constraints": ["redact_contact_fields"],
                    "handoff_contract": ["return blockers to orchestrator"],
                    "debate_contract": ["preserve weak evidence challenges"],
                    "expected_artifact_types": ["subagent_output"],
                    "required_log_events": ["dispatch", "receive_output"],
                    "retry_allowed": True,
                    "on_failure": "return_blocked",
                    "status": "not_started",
                },
                "required_output_fields": ["role_output_packet"],
                "handoff_contract": ["return blockers to orchestrator"],
                "debate_contract": ["preserve weak evidence challenges"],
            }
        ]
    }
    packet_path = tmp_path / "ready.json"
    packet_path.write_text(json.dumps(packet), encoding="utf-8")

    result = run_python(VALIDATOR, "--injections", str(packet_path), "--emit-invocations")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    invocation = payload["subagent_invocations"][0]["subagent_invocation"]
    assert invocation["target_agent"] == "job-scout"
    assert invocation["runtime_context_packet_ref"] == "input/normalized/runtime_context_packet.json"
    assert invocation["status"] == "not_started"
    assert invocation["on_failure"] == "return_blocked"


def test_validator_rejects_final_package_when_required_gate_is_blocked(tmp_path):
    manifest = {
        "execution_manifest": {
            "run_id": "run-test",
            "current_stage": "final_package_ready",
            "runtime_context_packet_ref": "input/normalized/runtime_context_packet.json",
            "secondary_prompt_injection_refs": ["injections/job-scout.secondary_prompt_injection.json"],
            "subagent_invocation_refs": ["invocations/job-scout.invocation.json"],
            "gate_status": {
                "input_normalized": True,
                "context_packet_created": True,
                "secondary_injections_created": True,
                "specialists_completed_or_blocked": True,
                "debate_completed_or_recorded": True,
                "hr_review_completed": False,
                "factual_review_completed_when_needed": False,
                "user_confirmation_resolved_when_needed": True,
            },
            "final_package_ref": "final/decision_package.json",
        },
        "run_state": {
            "run_id": "run-test",
            "stage": "final_package_ready",
            "task_type": "resume_generation",
            "runtime_context_packet_ref": "input/normalized/runtime_context_packet.json",
            "secondary_prompt_injection_refs": ["injections/job-scout.secondary_prompt_injection.json"],
            "subagent_invocation_refs": ["invocations/job-scout.invocation.json"],
            "blocked_outputs": [],
            "next_action": "return_final_package",
        },
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    result = run_python(VALIDATOR, "--manifest", str(manifest_path))

    assert result.returncode == 1
    assert "hr_review_completed" in result.stderr
    assert "final_package_ready" in result.stderr


def test_validator_rejects_final_package_without_traceable_runtime_refs(tmp_path):
    manifest = {
        "execution_manifest": {
            "run_id": "run-test",
            "current_stage": "final_package_ready",
            "runtime_context_packet_ref": "",
            "secondary_prompt_injection_refs": [],
            "subagent_invocation_refs": [],
            "gate_status": {
                "input_normalized": True,
                "context_packet_created": True,
                "secondary_injections_created": True,
                "specialists_completed_or_blocked": True,
                "debate_completed_or_recorded": True,
                "hr_review_completed": True,
                "factual_review_completed_when_needed": True,
                "user_confirmation_resolved_when_needed": True,
            },
            "final_package_ref": "final/decision_package.json",
        },
        "run_state": {
            "run_id": "run-test",
            "stage": "final_package_ready",
            "task_type": "resume_generation",
            "runtime_context_packet_ref": "",
            "secondary_prompt_injection_refs": [],
            "subagent_invocation_refs": [],
            "blocked_outputs": [],
            "next_action": "return_final_package",
        },
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    result = run_python(VALIDATOR, "--manifest", str(manifest_path))

    assert result.returncode == 1
    assert "runtime_context_packet_ref" in result.stderr


def test_simulator_creates_private_blocked_run_artifacts(tmp_path):
    result = run_python(
        SIMULATOR,
        "--task-type",
        "resume_generation",
        "--input-text",
        "Computer science sophomore, Python, looking for AI internship.",
        "--run-root",
        str(tmp_path / ".career-pipeline-runs"),
    )

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)
    assert response["runner_response"]["exit_status"] == "blocked"

    run_dir = tmp_path / ".career-pipeline-runs" / response["runner_response"]["run_id"]
    assert run_dir.is_dir()
    assert (run_dir / "manifest.json").is_file()
    assert (run_dir / "input" / "normalized" / "runtime_context_packet.json").is_file()
    assert (run_dir / "injections" / "job-scout.secondary_prompt_injection.json").is_file()
    assert (run_dir / "invocations" / "job-scout.invocation.json").is_file()
    assert (run_dir / "final" / "blocked_package.json").is_file()

    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["execution_manifest"]["current_stage"] == "blocked"
    assert manifest["run_state"]["stage"] == "blocked"
    assert manifest["execution_manifest"]["final_package_ref"] == ""
    assert "missing_user_facts" in json.loads((run_dir / "final" / "blocked_package.json").read_text(encoding="utf-8"))["blocked_package"]["blocked_outputs"]


def test_simulator_redacts_contact_like_input_from_raw_refs(tmp_path):
    result = run_python(
        SIMULATOR,
        "--task-type",
        "resume_generation",
        "--input-text",
        "Computer science sophomore, phone 13812345678, email test@example.com, Python.",
        "--run-root",
        str(tmp_path / ".career-pipeline-runs"),
    )

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)
    run_dir = tmp_path / ".career-pipeline-runs" / response["runner_response"]["run_id"]
    raw_refs = (run_dir / "input" / "raw_refs.json").read_text(encoding="utf-8")
    assert "13812345678" not in raw_refs
    assert "test@example.com" not in raw_refs
    assert "[redacted-phone]" in raw_refs
    assert "[redacted-email]" in raw_refs


def test_simulator_marks_user_derived_artifacts_as_private(tmp_path):
    result = run_python(
        SIMULATOR,
        "--task-type",
        "resume_generation",
        "--input-text",
        "Computer science sophomore, Python, looking for AI internship.",
        "--run-root",
        str(tmp_path / ".career-pipeline-runs"),
    )

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)
    run_dir = tmp_path / ".career-pipeline-runs" / response["runner_response"]["run_id"]
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    refs = {
        ref["path"]: ref
        for ref in manifest["execution_manifest"]["artifact_refs"]
    }

    for path in [
        "input/raw_refs.json",
        "input/normalized/first_round_user_profile.json",
        "input/normalized/runtime_context_packet.json",
    ]:
        assert refs[path]["privacy_class"] == "user_private"
        assert refs[path]["contains_private_resume"] is True

    assert refs["input/raw_refs.json"]["contains_contact"] is True
    assert refs["injections/job-scout.secondary_prompt_injection.json"]["privacy_class"] == "derived"


def test_repository_role_prompts_satisfy_runtime_traceability_contract():
    result = run_python(VALIDATOR)

    assert result.returncode == 0, result.stderr


def test_plan_builder_creates_plan_only_dispatch_queue(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "job_search",
        "--input-text",
        "Computer science sophomore, Python, looking for AI internship.",
        "--run-root",
        str(run_root),
        "--route",
        "job_search",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id

    result = run_python(PLAN_BUILDER, "--run-dir", str(run_dir))

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)
    assert response["planner_response"]["exit_status"] == "success"
    plan_path = run_dir / response["planner_response"]["subagent_plan_ref"]
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    queue = plan["subagent_invocation_plan"]["dispatch_queue"]
    agents = [item["target_agent"] for item in queue]
    assert agents == [
        "major-cluster-classifier",
        "profile-extractor",
        "job-scout",
        "jd-analyzer",
        "match-strategist",
        "learning-path-strategist",
    ]
    assert all(item["dispatch_mode"] == "plan_only" for item in queue)
    assert all(item["status"] == "planned" for item in queue)
    assert not any("input/raw_refs.json" in item["input_refs"] for item in queue)
    assert plan["subagent_invocation_plan"]["max_parallel_subagents"] == 4
    assert plan["subagent_invocation_plan"]["artifact_handoff_required"] is True
    assert plan["subagent_invocation_plan"]["close_completed_subagents"] is True
    assert [batch["batch_id"] for batch in plan["subagent_invocation_plan"]["dispatch_batches"]] == [
        "profile_and_taxonomy",
        "public_role_research",
        "strategy_match",
        "strategy_learning",
    ]
    batch_by_id = {
        batch["batch_id"]: batch
        for batch in plan["subagent_invocation_plan"]["dispatch_batches"]
    }
    assert batch_by_id["strategy_match"]["target_agents"] == ["match-strategist"]
    assert batch_by_id["strategy_learning"]["target_agents"] == ["learning-path-strategist"]
    assert batch_by_id["strategy_learning"]["depends_on_batches"] == ["strategy_match"]
    assert "agents/match-strategist/output.json" in batch_by_id["strategy_learning"]["depends_on_artifact_refs"]
    assert all(item["batch_id"] for item in queue)
    assert all(item["close_after_artifact_persisted"] is True for item in queue)

    validation = run_python(VALIDATOR, "--subagent-plan", str(plan_path))
    assert validation.returncode == 0, validation.stderr


def test_target_job_fit_plan_batches_agents_for_limited_subagent_concurrency(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "target_job_fit",
        "--input-text",
        (
            "Computer science junior, Python and Java, wants ByteDance LLM backend internship. "
            "JD: backend, RAG, Redis, message queue, Agent."
        ),
        "--run-root",
        str(run_root),
        "--route",
        "target_job_fit",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id

    result = run_python(PLAN_BUILDER, "--run-dir", str(run_dir), "--build-prompt-bundles")

    assert result.returncode == 0, result.stderr
    plan_ref = json.loads(result.stdout)["planner_response"]["subagent_plan_ref"]
    plan = json.loads((run_dir / plan_ref).read_text(encoding="utf-8"))["subagent_invocation_plan"]
    batches = {batch["batch_id"]: batch for batch in plan["dispatch_batches"]}
    assert list(batches) == [
        "profile_and_taxonomy",
        "public_role_research",
        "strategy_match",
        "strategy_learning",
        "hr_and_factual_gates",
    ]
    assert batches["profile_and_taxonomy"]["target_agents"] == [
        "major-cluster-classifier",
        "profile-extractor",
    ]
    assert batches["public_role_research"]["target_agents"] == [
        "jd-analyzer",
        "company-intelligence-analyst",
        "job-scout",
    ]
    assert batches["strategy_match"]["depends_on_batches"] == [
        "profile_and_taxonomy",
        "public_role_research",
    ]
    assert batches["strategy_match"]["target_agents"] == ["match-strategist"]
    assert batches["strategy_learning"]["target_agents"] == ["learning-path-strategist"]
    assert batches["strategy_learning"]["depends_on_batches"] == ["strategy_match"]
    assert "agents/match-strategist/output.json" in batches["strategy_learning"]["depends_on_artifact_refs"]
    assert batches["hr_and_factual_gates"]["target_agents"] == [
        "hr-supervisor",
        "factual-reviewer",
    ]
    assert all(batch["max_parallel_subagents"] <= 4 for batch in batches.values())

    queue_by_agent = {item["target_agent"]: item for item in plan["dispatch_queue"]}
    assert queue_by_agent["match-strategist"]["depends_on_batches"] == [
        "profile_and_taxonomy",
        "public_role_research",
    ]
    assert "agents/profile-extractor/output.json" in queue_by_agent["match-strategist"]["depends_on_artifact_refs"]
    assert "agents/jd-analyzer/output.json" in queue_by_agent["match-strategist"]["depends_on_artifact_refs"]
    assert queue_by_agent["learning-path-strategist"]["depends_on_batches"] == [
        "strategy_match",
    ]
    assert queue_by_agent["learning-path-strategist"]["depends_on_agents"] == [
        "match-strategist",
    ]
    assert queue_by_agent["hr-supervisor"]["depends_on_batches"] == [
        "strategy_match",
        "strategy_learning",
    ]
    batch_by_agent = {item["target_agent"]: item["batch_id"] for item in plan["dispatch_queue"]}
    for item in plan["dispatch_queue"]:
        for dependency_agent in item["depends_on_agents"]:
            assert batch_by_agent[dependency_agent] != item["batch_id"]
    assert all(item["close_after_artifact_persisted"] is True for item in plan["dispatch_queue"])

    work_orders = run_python(WORK_ORDER_BUILDER, "--run-dir", str(run_dir))
    assert work_orders.returncode == 0, work_orders.stderr
    orders_ref = json.loads(work_orders.stdout)["work_order_response"]["work_orders_ref"]
    orders = json.loads((run_dir / orders_ref).read_text(encoding="utf-8"))["subagent_work_orders"]
    assert orders["dispatch_strategy"] == "batched_artifact_handoff"
    assert orders["max_parallel_subagents"] == 4
    first_order = orders["orders"][0]
    assert first_order["batch_id"] == "profile_and_taxonomy"
    assert first_order["close_after_artifact_persisted"] is True
    assert "persist_role_output_before_close" in first_order["execution_instruction"]


def minimal_batched_subagent_plan(queue_overrides: dict[str, object]) -> dict:
    queue_item = {
        "queue_index": 0,
        "target_agent": "job-scout",
        "batch_id": "public_role_research",
        "depends_on_batches": [],
        "depends_on_agents": [],
        "depends_on_artifact_refs": [],
        "invocation_ref": "invocations/job-scout.invocation.json",
        "input_refs": ["input/normalized/runtime_context_packet.json"],
        "output_artifact_target": "agents/job-scout/output.json",
        "close_after_artifact_persisted": True,
        "dispatch_mode": "plan_only",
        "status": "planned",
        "allowed_network": False,
        "requires_human_approval": True,
        "privacy_class": "derived",
        "blocked_until": ["human_confirms_real_subagent_execution"],
    }
    queue_item.update(queue_overrides)
    return {
        "subagent_invocation_plan": {
            "run_id": "run-test",
            "plan_status": "ready",
            "created_from_manifest_ref": "manifest.json",
            "dispatch_strategy": "batched_artifact_handoff",
            "max_parallel_subagents": 4,
            "artifact_handoff_required": True,
            "close_completed_subagents": True,
            "dispatch_batches": [
                {
                    "batch_id": "public_role_research",
                    "batch_index": 0,
                    "target_agents": ["job-scout"],
                    "depends_on_batches": [],
                    "depends_on_artifact_refs": [],
                    "produces_artifact_refs": ["agents/job-scout/output.json"],
                    "max_parallel_subagents": 1,
                    "close_completed_subagents": True,
                    "artifact_handoff_required": True,
                }
            ],
            "dispatch_queue": [queue_item],
        }
    }


def test_validator_rejects_same_batch_agent_dependencies(tmp_path):
    plan = {
        "subagent_invocation_plan": {
            "run_id": "run-test",
            "plan_status": "ready",
            "created_from_manifest_ref": "manifest.json",
            "dispatch_strategy": "batched_artifact_handoff",
            "max_parallel_subagents": 2,
            "artifact_handoff_required": True,
            "close_completed_subagents": True,
            "dispatch_batches": [
                {
                    "batch_id": "strategy_and_learning",
                    "batch_index": 0,
                    "target_agents": ["match-strategist", "learning-path-strategist"],
                    "depends_on_batches": [],
                    "depends_on_artifact_refs": [],
                    "produces_artifact_refs": [
                        "agents/match-strategist/output.json",
                        "agents/learning-path-strategist/output.json",
                    ],
                    "max_parallel_subagents": 2,
                    "close_completed_subagents": True,
                    "artifact_handoff_required": True,
                }
            ],
            "dispatch_queue": [
                {
                    "queue_index": 0,
                    "target_agent": "match-strategist",
                    "batch_id": "strategy_and_learning",
                    "depends_on_batches": [],
                    "depends_on_agents": [],
                    "depends_on_artifact_refs": [],
                    "invocation_ref": "invocations/match-strategist.invocation.json",
                    "prompt_bundle_ref": "prompts/match-strategist.prompt_bundle.json",
                    "input_refs": ["input/normalized/runtime_context_packet.json"],
                    "output_artifact_target": "agents/match-strategist/output.json",
                    "close_after_artifact_persisted": True,
                    "dispatch_mode": "plan_only",
                    "status": "planned",
                    "allowed_network": False,
                    "requires_human_approval": True,
                    "privacy_class": "derived",
                    "blocked_until": ["human_confirms_real_subagent_execution"],
                },
                {
                    "queue_index": 1,
                    "target_agent": "learning-path-strategist",
                    "batch_id": "strategy_and_learning",
                    "depends_on_batches": [],
                    "depends_on_agents": ["match-strategist"],
                    "depends_on_artifact_refs": ["agents/match-strategist/output.json"],
                    "invocation_ref": "invocations/learning-path-strategist.invocation.json",
                    "prompt_bundle_ref": "prompts/learning-path-strategist.prompt_bundle.json",
                    "input_refs": ["input/normalized/runtime_context_packet.json"],
                    "output_artifact_target": "agents/learning-path-strategist/output.json",
                    "close_after_artifact_persisted": True,
                    "dispatch_mode": "plan_only",
                    "status": "planned",
                    "allowed_network": False,
                    "requires_human_approval": True,
                    "privacy_class": "derived",
                    "blocked_until": ["human_confirms_real_subagent_execution"],
                },
            ],
        }
    }
    plan_path = tmp_path / "same-batch-dependency-plan.json"
    plan_path.write_text(json.dumps(plan), encoding="utf-8")

    result = run_python(VALIDATOR, "--subagent-plan", str(plan_path))

    assert result.returncode == 1
    assert "must be in an earlier batch" in result.stderr


def test_validator_rejects_subagent_plan_that_is_not_plan_only(tmp_path):
    plan = minimal_batched_subagent_plan(
        {
            "dispatch_mode": "execute",
            "status": "running",
            "allowed_network": True,
            "requires_human_approval": False,
        }
    )
    plan_path = tmp_path / "bad-plan.json"
    plan_path.write_text(json.dumps(plan), encoding="utf-8")

    result = run_python(VALIDATOR, "--subagent-plan", str(plan_path))

    assert result.returncode == 1
    assert "plan_only" in result.stderr


def test_validator_rejects_subagent_plan_that_exposes_raw_input(tmp_path):
    plan = minimal_batched_subagent_plan(
        {
            "input_refs": [
                "input/raw_refs.json",
                "input/normalized/runtime_context_packet.json",
            ],
        }
    )
    plan_path = tmp_path / "raw-plan.json"
    plan_path.write_text(json.dumps(plan), encoding="utf-8")

    result = run_python(VALIDATOR, "--subagent-plan", str(plan_path))

    assert result.returncode == 1
    assert "raw input" in result.stderr


def test_executor_dry_run_preserves_plan_and_invocation_statuses(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "job_search",
        "--input-text",
        "computer science sophomore, Python, looking for AI internship",
        "--run-root",
        str(run_root),
        "--route",
        "job_search",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id
    plan = run_python(PLAN_BUILDER, "--run-dir", str(run_dir))
    assert plan.returncode == 0, plan.stderr

    result = run_python(PLAN_EXECUTOR, "--run-dir", str(run_dir))

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)
    assert response["executor_response"]["exit_status"] == "dry_run"
    event_log = run_dir / response["executor_response"]["execution_events_ref"]
    assert event_log.is_file()

    plan_path = run_dir / "invocations" / "subagent_invocation_plan.json"
    plan_payload = json.loads(plan_path.read_text(encoding="utf-8"))
    assert all(
        item["status"] == "planned"
        for item in plan_payload["subagent_invocation_plan"]["dispatch_queue"]
    )
    first_invocation_ref = plan_payload["subagent_invocation_plan"]["dispatch_queue"][0]["invocation_ref"]
    first_invocation = json.loads((run_dir / first_invocation_ref).read_text(encoding="utf-8"))
    assert first_invocation["subagent_invocation"]["status"] == "not_started"
    assert "dry_run" in event_log.read_text(encoding="utf-8")


def test_executor_execute_requires_human_approval(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "job_search",
        "--input-text",
        "computer science sophomore, Python, looking for AI internship",
        "--run-root",
        str(run_root),
        "--route",
        "job_search",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id
    assert run_python(PLAN_BUILDER, "--run-dir", str(run_dir)).returncode == 0

    result = run_python(PLAN_EXECUTOR, "--run-dir", str(run_dir), "--execute")

    assert result.returncode == 1
    assert "human approval" in result.stderr.lower()


def test_executor_network_execution_requires_source_policy_ack(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "job_search",
        "--input-text",
        "computer science sophomore, Python, looking for AI internship",
        "--run-root",
        str(run_root),
        "--route",
        "job_search",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id
    assert run_python(PLAN_BUILDER, "--run-dir", str(run_dir)).returncode == 0

    result = run_python(
        PLAN_EXECUTOR,
        "--run-dir",
        str(run_dir),
        "--execute",
        "--human-approved",
        "--allow-network",
    )

    assert result.returncode == 1
    assert "source policy" in result.stderr.lower()


def test_executor_network_execution_requires_source_plan(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "job_search",
        "--input-text",
        "computer science sophomore, Python, looking for AI internship",
        "--run-root",
        str(run_root),
        "--route",
        "job_search",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id
    assert run_python(PLAN_BUILDER, "--run-dir", str(run_dir)).returncode == 0

    result = run_python(
        PLAN_EXECUTOR,
        "--run-dir",
        str(run_dir),
        "--execute",
        "--human-approved",
        "--allow-network",
        "--source-policy-ack",
    )

    assert result.returncode == 1
    assert "source plan" in result.stderr.lower()


def test_executor_network_execution_rejects_invalid_source_plan(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "job_search",
        "--input-text",
        "computer science sophomore, Python, looking for AI internship",
        "--run-root",
        str(run_root),
        "--route",
        "job_search",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id
    assert run_python(PLAN_BUILDER, "--run-dir", str(run_dir)).returncode == 0
    source_plan_path = run_dir / "evidence" / "public_source_research_plan.json"
    source_plan_path.parent.mkdir(parents=True, exist_ok=True)
    source_plan_path.write_text(
        json.dumps(
            {
                "public_source_research_plan": {
                    "run_id": run_id,
                    "policy_ref": ".agents/skills/career-pipeline/references/source-policy.md",
                    "network_execution_default": "disabled_until_controller_source_policy_ack",
                    "research_tasks": [
                        {
                            "task_id": "login-only-jd",
                            "agent": "job-scout",
                            "claim_field": "jd_requirement",
                            "source_type": "recruitment_platform_jd",
                            "source_priority": 3,
                            "allowed": True,
                            "requires_login": True,
                            "may_set_weight": True,
                            "may_set_final_decision": True,
                            "evidence_strength_floor": "medium",
                            "privacy_action": "cache_metadata_only",
                            "query_template": "login-only JD",
                            "output_fields": ["evidence_basis"],
                        }
                    ],
                    "blocked_source_types": [],
                }
            }
        ),
        encoding="utf-8",
    )

    result = run_python(
        PLAN_EXECUTOR,
        "--run-dir",
        str(run_dir),
        "--execute",
        "--human-approved",
        "--allow-network",
        "--source-policy-ack",
    )

    assert result.returncode == 1
    assert "requires_login" in result.stderr


def test_validator_rejects_role_output_without_traceability(tmp_path):
    output = {
        "role_output_packet": {
            "invocation_id": "run-test-job-scout",
            "target_agent": "job-scout",
            "status": "done",
            "role_output_ref": "agents/job-scout/output.json",
            "evidence_packet_refs": [],
            "runtime_weights_ref": "merge/runtime_weights.json",
            "artifact_refs": [],
            "blocked_outputs": [],
            "runtime_research_tasks": [],
            "needs_user_confirmation": [],
            "handoff_to": [],
            "errors": [],
            "confidence": "medium",
        }
    }
    output_path = tmp_path / "role-output.json"
    output_path.write_text(json.dumps(output), encoding="utf-8")

    result = run_python(VALIDATOR, "--role-output", str(output_path))

    assert result.returncode == 1
    assert "invocation_ref" in result.stderr
    assert "error_recovery_state" in result.stderr


def test_validator_rejects_failed_role_output_with_final_decision_fields(tmp_path):
    output = {
        "invocation_ref": "invocations/job-scout.invocation.json",
        "role_output_packet": {
            "invocation_id": "run-test-job-scout",
            "target_agent": "job-scout",
            "status": "failed",
            "role_output_ref": "agents/job-scout/output.json",
            "evidence_packet_refs": [],
            "runtime_weights_ref": "merge/runtime_weights.json",
            "artifact_refs": [],
            "blocked_outputs": ["application_strategy"],
            "runtime_research_tasks": [],
            "needs_user_confirmation": [],
            "handoff_to": [],
            "errors": [{"category": "subagent_failed"}],
            "confidence": "low",
        },
        "error_recovery_state": {
            "status": "failed",
            "errors": [],
            "recovery_actions": ["return_blocked_package"],
            "degraded_outputs": [],
            "blocked_outputs": ["application_strategy"],
            "safe_outputs": [],
            "next_action": "return_blocked_package",
        },
        "application_strategy": {"priority": "apply now"},
    }
    output_path = tmp_path / "failed-output.json"
    output_path.write_text(json.dumps(output), encoding="utf-8")

    result = run_python(VALIDATOR, "--role-output", str(output_path))

    assert result.returncode == 1
    assert "failed or malformed" in result.stderr


def test_validator_rejects_failed_role_output_with_target_job_fit_decision_fields(tmp_path):
    output = {
        "invocation_ref": "invocations/match-strategist.invocation.json",
        "role_output_packet": {
            "invocation_id": "run-test-match-strategist",
            "target_agent": "match-strategist",
            "status": "failed",
            "role_output_ref": "agents/match-strategist/output.json",
            "evidence_packet_refs": [],
            "runtime_weights_ref": "merge/runtime_weights.json",
            "artifact_refs": [],
            "blocked_outputs": ["current_fit_assessment"],
            "runtime_research_tasks": [],
            "needs_user_confirmation": [],
            "handoff_to": [],
            "errors": [{"category": "subagent_failed"}],
            "confidence": "low",
        },
        "error_recovery_state": {
            "status": "failed",
            "errors": [],
            "recovery_actions": ["return_blocked_package"],
            "degraded_outputs": [],
            "blocked_outputs": ["current_fit_assessment"],
            "safe_outputs": [],
            "next_action": "return_blocked_package",
        },
        "current_fit_assessment": {"status": "evidence_bound"},
    }
    output_path = tmp_path / "failed-target-fit-output.json"
    output_path.write_text(json.dumps(output), encoding="utf-8")

    result = run_python(VALIDATOR, "--role-output", str(output_path))

    assert result.returncode == 1
    assert "current_fit_assessment" in result.stderr


def test_executor_rejects_malformed_backfill_output(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "job_search",
        "--input-text",
        "computer science sophomore, Python, looking for AI internship",
        "--run-root",
        str(run_root),
        "--route",
        "job_search",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id
    assert run_python(PLAN_BUILDER, "--run-dir", str(run_dir)).returncode == 0
    bad_output = tmp_path / "bad-output.json"
    bad_output.write_text(json.dumps({"not_role_output_packet": {}}), encoding="utf-8")

    result = run_python(
        PLAN_EXECUTOR,
        "--run-dir",
        str(run_dir),
        "--backfill-output",
        f"job-scout={bad_output}",
    )

    assert result.returncode == 1
    assert "role_output_packet" in result.stderr


def test_continue_runtime_run_accepts_user_facts_and_updates_same_run(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "resume_generation",
        "--input-text",
        "computer science sophomore, Python, looking for AI internship",
        "--run-root",
        str(run_root),
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id
    facts = {
        "school_name": "Example University",
        "major_name": "Software Engineering",
        "grade_or_year": "junior",
        "degree_level": "bachelor",
        "graduation_window": "2028",
        "project_competition_research_experience": [
            {"name": "LLM resume parser", "evidence": "course project"}
        ],
        "internship_experience": [{"company": "Example Lab", "role": "assistant"}],
        "target_location_or_company_if_any": "Shanghai AI internship",
    }

    result = run_python(
        RUN_CONTINUER,
        "--run-dir",
        str(run_dir),
        "--user-facts-json",
        json.dumps(facts),
    )

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)
    assert response["continuation_response"]["run_id"] == run_id
    assert response["continuation_response"]["exit_status"] == "ready_for_dispatch"

    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["execution_manifest"]["run_id"] == run_id
    assert manifest["execution_manifest"]["current_stage"] == "injection_ready"
    assert manifest["run_state"]["next_action"] == "dispatch_agents"
    assert manifest["run_state"]["blocked_agents"] == []

    context = json.loads(
        (run_dir / "input" / "normalized" / "runtime_context_packet.json").read_text(encoding="utf-8")
    )["runtime_context_packet"]
    assert context["school_context"]["school_name"] == "Example University"
    assert context["school_context"]["major_name"] == "Software Engineering"
    assert context["school_context"]["grade_or_year"] == "junior"
    assert {"field": "major_name", "value": "Software Engineering"} in context["known_user_facts"]
    assert {"field": "grade_or_year", "value": "junior"} in context["known_user_facts"]
    assert context["missing_user_owned_facts"] == []
    known_fields = {fact["field"] for fact in context["known_user_facts"]}
    assert {
        "school_name",
        "major_name",
        "grade_or_year",
        "degree_level",
        "graduation_window",
    }.issubset(known_fields)


def test_continue_runtime_run_accepts_user_facts_json_file(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "job_search",
        "--input-text",
        "engineering undergraduate, Python and C++, looking for software internship",
        "--run-root",
        str(run_root),
        "--route",
        "job_search",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id
    facts_path = tmp_path / "user-facts.json"
    facts_path.write_text(
        json.dumps(
            {
                "major_name": "Software Engineering",
                "grade_or_year": "junior",
                "school_name": "Example University",
            }
        ),
        encoding="utf-8",
    )

    result = run_python(
        RUN_CONTINUER,
        "--run-dir",
        str(run_dir),
        "--user-facts-json-file",
        str(facts_path),
    )

    assert result.returncode == 0, result.stderr
    context = json.loads(
        (run_dir / "input" / "normalized" / "runtime_context_packet.json").read_text(encoding="utf-8")
    )["runtime_context_packet"]
    assert context["school_context"]["major_name"] == "Software Engineering"
    assert context["school_context"]["grade_or_year"] == "junior"


def test_simulator_supports_resume_generation_route(tmp_path):
    result = run_python(
        SIMULATOR,
        "--task-type",
        "resume_generation",
        "--input-text",
        "computer science senior, Python, Java, resume generation",
        "--run-root",
        str(tmp_path / ".career-pipeline-runs"),
        "--route",
        "resume_generation",
    )

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)
    run_dir = tmp_path / ".career-pipeline-runs" / response["runner_response"]["run_id"]
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    agents = [
        Path(ref).name.replace(".invocation.json", "")
        for ref in manifest["execution_manifest"]["subagent_invocation_refs"]
    ]
    assert agents == [
        "major-cluster-classifier",
        "profile-extractor",
        "resume-format-gate",
        "resume-architect",
        "factual-reviewer",
        "hr-supervisor",
    ]


def test_resume_generation_gate_uses_lower_threshold_and_candidate_information_focus():
    resume_db = json.loads(
        (ROOT / "data" / "resume_formats" / "resume_format_database.zh-CN.json").read_text(
            encoding="utf-8"
        )
    )
    summary = json.loads(
        (ROOT / "data" / "resume_formats" / "summary.json").read_text(encoding="utf-8")
    )
    gate_prompt = (ROOT / ".codex" / "agents" / "resume-format-gate.toml").read_text(
        encoding="utf-8"
    )
    architect_prompt = (ROOT / ".codex" / "agents" / "resume-architect.toml").read_text(
        encoding="utf-8"
    )

    assert summary["gate_pass_threshold"] == 60
    rubric = resume_db["hr_trust_score_rubric"]
    assert rubric["pass_threshold"] == 60
    assert rubric["revise_threshold"] == 45
    weights = {dimension["id"]: dimension["weight"] for dimension in rubric["dimensions"]}
    assert weights == {
        "information_completeness": 35,
        "evidence_strength": 25,
        "role_relevance": 30,
        "truthfulness_risk": 10,
    }
    assert "readability_format_stability" not in weights
    assert "format_quality_after_generation" in resume_db
    assert "format readability is generated by ResumeArchitect" in gate_prompt
    assert "heavy user-material threshold" in gate_prompt
    assert "major-target mismatch" in gate_prompt
    assert "recommended_role_adjustment" in gate_prompt
    assert "major-target mismatch" in architect_prompt
    assert "generate an editable first draft" in architect_prompt


def test_resume_prompts_require_general_resume_and_delivery_artifacts_without_target():
    gate_prompt = (ROOT / ".codex" / "agents" / "resume-format-gate.toml").read_text(
        encoding="utf-8"
    )
    architect_prompt = (ROOT / ".codex" / "agents" / "resume-architect.toml").read_text(
        encoding="utf-8"
    )
    factual_prompt = (ROOT / ".codex" / "agents" / "factual-reviewer.toml").read_text(
        encoding="utf-8"
    )
    hr_prompt = (ROOT / ".codex" / "agents" / "hr-supervisor.toml").read_text(
        encoding="utf-8"
    )
    interaction_flow = (
        ROOT / ".agents" / "skills" / "career-pipeline" / "references" / "user-interaction-flow.md"
    ).read_text(encoding="utf-8")

    assert "do not block resume generation only for that reason" in gate_prompt
    assert "general_resume_draft_allowed_without_target" in gate_prompt
    assert "campus_general_cn_one_page" in architect_prompt
    assert "resume_delivery_artifacts" in architect_prompt
    assert "growth_resume_preview" in architect_prompt
    assert "after recommended learning and project work" in architect_prompt
    assert "must not be used as completed current experience" in architect_prompt
    assert "growth_resume_preview" in interaction_flow
    for text in [architect_prompt, factual_prompt, hr_prompt, interaction_flow]:
        assert "DOCX" in text or "docx" in text
        assert "PDF" in text or "pdf" in text
        assert "image" in text or "图片" in text
    assert "resume generation gate" in interaction_flow
    assert "Lack of target blocks company-specific tailoring, not the general resume" in interaction_flow


def test_resume_renderer_exports_docx_pdf_png_from_markdown(tmp_path):
    draft_path = tmp_path / "resume.md"
    draft_path.write_text(
        "\n".join(
            [
                "# 计算机类大三学生",
                "",
                "## 学校信息",
                "- 专业：计算机类",
                "- 年级：大三",
                "",
                "## 掌握技能",
                "- Python：课程作业和脚本基础",
                "",
                "## 项目竞赛经历",
                "- 课程项目：已完成课程作业，具体职责和结果待补充。",
                "",
                "## 个人性格和潜力",
                "- 对工程实践和实习方向有探索意愿。",
            ]
        ),
        encoding="utf-8",
    )
    out_dir = tmp_path / "rendered"

    result = run_python(
        RESUME_RENDERER,
        "--draft-md",
        str(draft_path),
        "--out-dir",
        str(out_dir),
        "--basename",
        "general_resume",
    )

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)["resume_render_response"]
    assert response["exit_status"] == "success"
    artifact_refs = {item["format"]: Path(item["artifact_ref"]) for item in response["resume_delivery_artifacts"]}
    assert set(artifact_refs) == {"docx", "pdf", "image"}
    for path in artifact_refs.values():
        assert path.is_file()
        assert path.stat().st_size > 100
    assert artifact_refs["docx"].suffix == ".docx"
    assert artifact_refs["pdf"].suffix == ".pdf"
    assert artifact_refs["image"].suffix == ".png"
    assert response["page_count"] >= 1


def test_resume_renderer_extracts_resume_from_decision_package(tmp_path):
    decision_package_path = tmp_path / "decision_package.json"
    decision_package_path.write_text(
        json.dumps(
            {
                "decision_package": {
                    "user_facing_package": {
                        "resume_draft": {
                            "final_resume_draft": "\n".join(
                                [
                                    "# Software Engineering Junior",
                                    "",
                                    "## School Information",
                                    "- Major: Software Engineering",
                                    "- Grade: Junior",
                                    "",
                                    "## Skills",
                                    "- Python: basic scripting and coursework.",
                                    "",
                                    "## Projects",
                                    "- Course project: details and ownership pending user supplement.",
                                ]
                            )
                        }
                    }
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    out_dir = tmp_path / "rendered"

    result = run_python(
        RESUME_RENDERER,
        "--decision-package",
        str(decision_package_path),
        "--out-dir",
        str(out_dir),
        "--basename",
        "general_resume",
    )

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)["resume_render_response"]
    assert response["source_decision_package_ref"] == str(decision_package_path)
    assert Path(response["source_draft_ref"]).is_file()
    assert (out_dir / "resume_draft.md").read_text(encoding="utf-8").startswith("# Software")
    artifact_refs = {item["format"]: Path(item["artifact_ref"]) for item in response["resume_delivery_artifacts"]}
    assert set(artifact_refs) == {"docx", "pdf", "image"}
    assert all(path.is_file() for path in artifact_refs.values())


def test_resume_renderer_exports_all_resume_versions_from_decision_package(tmp_path):
    decision_package_path = tmp_path / "decision_package.json"
    decision_package_path.write_text(
        json.dumps(
            {
                "decision_package": {
                    "user_facing_package": {
                        "resume_draft": {
                            "resume_version": "campus_general_cn_one_page",
                            "final_resume_draft": "\n".join(
                                [
                                    "# Current Factual Resume",
                                    "",
                                    "## Skills",
                                    "- Python: basic scripting and coursework.",
                                ]
                            ),
                        },
                        "growth_resume_preview": {
                            "resume_version": "after_learning_project_preview",
                            "preview_type": "after_recommended_learning_and_projects",
                            "truthfulness_notice": (
                                "Preview only. Do not use these learning or project items as completed "
                                "resume claims until proof artifacts exist."
                            ),
                            "final_resume_draft": "\n".join(
                                [
                                    "# After-Learning Resume Preview",
                                    "",
                                    "## Skills",
                                    "- Python, Git/GitHub, SQL: shown only after completion evidence exists.",
                                    "",
                                    "## Projects",
                                    "- Python internship smoke-test project: shown only after demo and README exist.",
                                ]
                            ),
                        },
                    }
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    out_dir = tmp_path / "rendered"

    result = run_python(
        RESUME_RENDERER,
        "--decision-package",
        str(decision_package_path),
        "--out-dir",
        str(out_dir),
        "--basename",
        "general_resume",
        "--all-resume-versions",
    )

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)["resume_render_response"]
    version_artifacts = {
        item["version_key"]: item for item in response["resume_version_artifacts"]
    }
    assert set(version_artifacts) == {"resume_draft", "growth_resume_preview"}
    assert (out_dir / "resume_draft.md").read_text(encoding="utf-8").startswith("# Current")
    assert (out_dir / "growth_resume_preview.md").read_text(encoding="utf-8").startswith("# After-Learning")
    for item in version_artifacts.values():
        refs = {artifact["format"]: Path(artifact["artifact_ref"]) for artifact in item["resume_delivery_artifacts"]}
        assert set(refs) == {"docx", "pdf", "image"}
        assert all(path.is_file() and path.stat().st_size > 100 for path in refs.values())


def test_incomplete_user_product_flow_reaches_general_resume_artifacts(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    product = run_python(
        PRODUCT_FLOW_RUNNER,
        "--task-type",
        "job_search",
        "--route",
        "job_search",
        "--input-text",
        "我是计算机相关专业大三，会一点 Python，想找实习但不知道投什么。",
        "--run-root",
        str(run_root),
    )
    assert product.returncode == 0, product.stderr
    run_id = json.loads(product.stdout)["product_flow_response"]["run_id"]
    run_dir = run_root / run_id

    notes_path = tmp_path / "public-source-notes.md"
    notes_path.write_text(
        "\n".join(
            [
                "- task_id: official-company-career",
                "  url: https://jobs.bytedance.com/campus",
                "  title: ByteDance campus recruiting public entry",
                "  source_type_hint: official_or_primary",
                "  snippet: Campus recruiting and internship search entrypoint.",
                "",
                "- task_id: recruitment-platform-public-jd",
                "  url: https://www.nowcoder.com/jobs",
                "  title: Nowcoder public jobs entry",
                "  source_type_hint: recruitment_platform_jd",
                "  snippet: Public jobs search entry for interns and campus candidates.",
            ]
        ),
        encoding="utf-8",
    )
    collected = run_python(
        PUBLIC_SOURCE_RESULT_COLLECTOR,
        "--run-dir",
        str(run_dir),
        "--notes-md",
        str(notes_path),
        "--output",
        "evidence/search_results.generated.json",
    )
    assert collected.returncode == 0, collected.stderr
    discovered = run_python(
        PUBLIC_SOURCE_DISCOVERER,
        "--run-dir",
        str(run_dir),
        "--search-results-json",
        str(run_dir / "evidence" / "search_results.generated.json"),
    )
    assert discovered.returncode == 0, discovered.stderr

    manual_outputs = run_python(
        INCOMPLETE_USER_MANUAL_OUTPUTS,
        "--run-dir",
        str(run_dir),
        "--out-dir",
        str(tmp_path / "manual-outputs"),
    )
    assert manual_outputs.returncode == 0, manual_outputs.stderr
    output_refs = json.loads(manual_outputs.stdout)["manual_output_builder_response"]["output_paths"]
    backfill_args: list[str] = []
    for target_agent, output_path in output_refs.items():
        backfill_args.extend(["--backfill-output", f"{target_agent}={output_path}"])
    backfill = run_python(
        PLAN_EXECUTOR,
        "--run-dir",
        str(run_dir),
        "--manual-controller-execution",
        *backfill_args,
    )
    assert backfill.returncode == 0, backfill.stderr

    finalized = run_python(
        FINALIZER,
        "--run-dir",
        str(run_dir),
        "--real-subagent-execution",
        "--execution-mode",
        "manual-controller",
    )
    assert finalized.returncode == 0, finalized.stderr
    final_ref = json.loads(finalized.stdout)["finalizer_response"]["final_package_ref"]
    package = json.loads((run_dir / final_ref).read_text(encoding="utf-8"))["decision_package"]
    user_package = package["user_facing_package"]
    assert user_package["resume_draft"]["resume_version"] == "campus_general_cn_one_page"
    assert user_package["resume_draft"]["incomplete_resume"] is True
    growth_preview = user_package["growth_resume_preview"]
    assert growth_preview["preview_type"] == "after_recommended_learning_and_projects"
    assert "Do not use" in growth_preview["truthfulness_notice"]
    assert "Git/GitHub" in growth_preview["final_resume_draft"]
    assert "Python internship smoke-test project" in growth_preview["final_resume_draft"]
    assert user_package["recommended_targets"]
    assert all(target["public_urls"] for target in user_package["recommended_targets"])
    assert "fit_score" in package["blocked_outputs"]

    rendered = run_python(
        RESUME_RENDERER,
        "--decision-package",
        str(run_dir / final_ref),
        "--out-dir",
        str(run_dir / "final" / "resume_artifacts"),
        "--basename",
        "general_resume",
        "--all-resume-versions",
    )
    assert rendered.returncode == 0, rendered.stderr
    render_response = json.loads(rendered.stdout)["resume_render_response"]
    artifact_refs = {
        item["format"]: Path(item["artifact_ref"]) for item in render_response["resume_delivery_artifacts"]
    }
    assert set(artifact_refs) == {"docx", "pdf", "image"}
    assert all(path.is_file() and path.stat().st_size > 100 for path in artifact_refs.values())
    assert (run_dir / "final" / "resume_artifacts" / "resume_draft.md").is_file()
    assert (run_dir / "final" / "resume_artifacts" / "growth_resume_preview.md").is_file()
    version_artifacts = {
        item["version_key"]: item for item in render_response["resume_version_artifacts"]
    }
    assert set(version_artifacts) == {"resume_draft", "growth_resume_preview"}


def test_simulator_supports_target_job_fit_route_with_target_context(tmp_path):
    result = run_python(
        SIMULATOR,
        "--task-type",
        "target_job_fit",
        "--input-text",
        (
            "Computer science sophomore, Python and Java. "
            "I want to apply for ByteDance LLM application engineer internship. "
            "JD: build RAG applications, evaluate LLM outputs, use Python, SQL, APIs, "
            "and deploy demos. I lack LLM project experience."
        ),
        "--run-root",
        str(tmp_path / ".career-pipeline-runs"),
        "--route",
        "target_job_fit",
    )

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)
    run_dir = tmp_path / ".career-pipeline-runs" / response["runner_response"]["run_id"]
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    agents = [
        Path(ref).name.replace(".invocation.json", "")
        for ref in manifest["execution_manifest"]["subagent_invocation_refs"]
    ]
    assert agents == [
        "major-cluster-classifier",
        "profile-extractor",
        "jd-analyzer",
        "company-intelligence-analyst",
        "job-scout",
        "match-strategist",
        "learning-path-strategist",
        "hr-supervisor",
        "factual-reviewer",
    ]

    context = json.loads(
        (run_dir / "input" / "normalized" / "runtime_context_packet.json").read_text(encoding="utf-8")
    )["runtime_context_packet"]
    target = context["target_context"]
    assert target["has_concrete_target"] is True
    assert target["target_job_fit_requested"] is True
    assert target["target_company"] == "ByteDance"
    assert "LLM application engineer internship" in target["target_job_title"]
    assert "RAG applications" in target["current_jd_text_excerpt"]
    assert target["current_fit_assessment_status"] == "safe_framing_allowed_exact_score_blocked"
    assert target["growth_path_assessment_status"] == "prepare_first_allowed_with_evidence_limits"
    for safe_output in [
        "current_fit_assessment",
        "application_readiness_decision",
        "learning_plan_before_application",
        "application_strategy",
    ]:
        assert safe_output not in context["blocked_outputs"]
    for exact_output in [
        "fit_score",
        "application_priority",
        "targeted_resume_tailoring",
        "company_specific_skill_weight_ranking",
    ]:
        assert exact_output in context["blocked_outputs"]


def test_target_job_fit_prompt_bundle_requires_fit_and_learning_gap_fields(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "target_job_fit",
        "--input-text",
        (
            "Computer science sophomore, Python and Java. "
            "Target: DJI robotics algorithm internship. "
            "JD: C++, Python, perception, sensor fusion, deployment, robotics projects."
        ),
        "--run-root",
        str(run_root),
        "--route",
        "target_job_fit",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id

    for invocation_ref in [
        "invocations/match-strategist.invocation.json",
        "invocations/learning-path-strategist.invocation.json",
    ]:
        result = run_python(PROMPT_BUNDLE_BUILDER, "--run-dir", str(run_dir), "--invocation-ref", invocation_ref)
        assert result.returncode == 0, result.stderr
        bundle_ref = json.loads(result.stdout)["prompt_bundle_response"]["prompt_bundle_ref"]
        bundle = json.loads((run_dir / bundle_ref).read_text(encoding="utf-8"))["subagent_prompt_bundle"]
        required = set(bundle["required_output_fields"])
        assert "current_fit_assessment" in required
        assert "skill_gap_analysis" in required
        assert "learning_plan_before_application" in required
        assert "evidence_requirements" in required
        role_context = bundle["prompt_sections"]["secondary_prompt_injection"]["content"]["role_specific_context"]
        assert role_context["target_job_fit_assessment_requested"] is True
        assert role_context["distinguish_current_fit_from_growth_path"] is True
        injection = bundle["prompt_sections"]["secondary_prompt_injection"]["content"]
        for safe_output in [
            "current_fit_assessment",
            "application_readiness_decision",
            "learning_plan_before_application",
            "application_strategy",
        ]:
            assert safe_output not in injection["blocked_outputs"]
        for exact_output in [
            "fit_score",
            "targeted_resume_tailoring",
            "company_specific_skill_weight_ranking",
        ]:
            assert exact_output in injection["blocked_outputs"]


def test_prompt_bundle_builder_creates_subagent_ready_context(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "job_search",
        "--input-text",
        "computer science sophomore, Python, looking for AI internship",
        "--run-root",
        str(run_root),
        "--route",
        "job_search",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id
    invocation_ref = "invocations/job-scout.invocation.json"

    result = run_python(PROMPT_BUNDLE_BUILDER, "--run-dir", str(run_dir), "--invocation-ref", invocation_ref)

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)
    bundle_ref = response["prompt_bundle_response"]["prompt_bundle_ref"]
    bundle_path = run_dir / bundle_ref
    assert bundle_path.is_file()
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))["subagent_prompt_bundle"]
    assert bundle["target_agent"] == "job-scout"
    assert bundle["invocation_ref"] == invocation_ref
    assert bundle["base_prompt_ref"] == ".codex/agents/job-scout.toml"
    assert bundle["runtime_context_packet_ref"] == "input/normalized/runtime_context_packet.json"
    assert bundle["secondary_prompt_injection_ref"] == "injections/job-scout.secondary_prompt_injection.json"
    assert "static_role_prompt" in bundle["prompt_sections"]
    assert "runtime_context_packet" in bundle["prompt_sections"]
    assert "secondary_prompt_injection" in bundle["prompt_sections"]
    assert "source_policy" in bundle["prompt_sections"]
    assert "required_output_contract" in bundle["prompt_sections"]
    assert "role_output_packet" in bundle["required_output_fields"]
    assert "error_recovery_state" in bundle["required_output_fields"]
    assert "input/raw_refs.json" not in json.dumps(bundle, ensure_ascii=False)


def test_plan_builder_attaches_prompt_bundle_refs(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "job_search",
        "--input-text",
        "computer science sophomore, Python, looking for AI internship",
        "--run-root",
        str(run_root),
        "--route",
        "job_search",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id

    result = run_python(PLAN_BUILDER, "--run-dir", str(run_dir), "--build-prompt-bundles")

    assert result.returncode == 0, result.stderr
    plan_ref = json.loads(result.stdout)["planner_response"]["subagent_plan_ref"]
    plan = json.loads((run_dir / plan_ref).read_text(encoding="utf-8"))["subagent_invocation_plan"]
    first = plan["dispatch_queue"][0]
    assert first["prompt_bundle_ref"].startswith("prompts/")
    assert (run_dir / first["prompt_bundle_ref"]).is_file()
    validation = run_python(VALIDATOR, "--subagent-plan", str(run_dir / plan_ref))
    assert validation.returncode == 0, validation.stderr


def test_public_source_plan_builder_creates_policy_bound_tasks(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "job_search",
        "--input-text",
        "computer science sophomore, Python, looking for AI internship at ByteDance or DJI",
        "--run-root",
        str(run_root),
        "--route",
        "job_search",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id

    result = run_python(SOURCE_PLAN_BUILDER, "--run-dir", str(run_dir))

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)
    source_plan_ref = response["source_plan_response"]["source_plan_ref"]
    source_plan = json.loads((run_dir / source_plan_ref).read_text(encoding="utf-8"))[
        "public_source_research_plan"
    ]
    assert source_plan["run_id"] == run_id
    assert source_plan["policy_ref"] == ".agents/skills/career-pipeline/references/source-policy.md"
    assert source_plan["network_execution_default"] == "disabled_until_controller_source_policy_ack"
    source_types = {task["source_type"] for task in source_plan["research_tasks"]}
    assert "official_or_primary" in source_types
    assert "recruitment_platform_jd" in source_types
    assert "verified_hr_public_post" in source_types
    assert "social_media_weak" in source_types
    assert "public_report" in source_types
    assert all(task["allowed"] is True for task in source_plan["research_tasks"])
    assert source_plan["blocked_source_types"]


def test_public_source_plan_for_target_job_fit_keeps_incomplete_jd_fields_as_hr_questions(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "target_job_fit",
        "--input-text",
        (
            "Computer science sophomore with Python and Java. "
            "Assess fit for Tencent backend development internship. "
            "JD: Java, Spring, MySQL, Redis, distributed systems, internship availability."
        ),
        "--run-root",
        str(run_root),
        "--route",
        "target_job_fit",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id

    result = run_python(SOURCE_PLAN_BUILDER, "--run-dir", str(run_dir))

    assert result.returncode == 0, result.stderr
    source_plan_ref = json.loads(result.stdout)["source_plan_response"]["source_plan_ref"]
    source_plan = json.loads((run_dir / source_plan_ref).read_text(encoding="utf-8"))[
        "public_source_research_plan"
    ]
    task_ids = {task["task_id"] for task in source_plan["research_tasks"]}
    assert "target-current-jd-verification" in task_ids
    assert "target-learning-gap-evidence" in task_ids
    assert "current_fit_assessment" not in source_plan["blocked_outputs_without_current_jd"]
    assert "application_readiness_decision" not in source_plan["blocked_outputs_without_current_jd"]
    assert "learning_plan_before_application" not in source_plan["blocked_outputs_without_current_jd"]
    assert "application_strategy" not in source_plan["blocked_outputs_without_current_jd"]
    assert "fit_score" in source_plan["blocked_outputs_without_current_jd"]
    assert "targeted_resume_tailoring" in source_plan["blocked_outputs_without_current_jd"]
    assert "company_specific_skill_weight_ranking" in source_plan["blocked_outputs_without_current_jd"]
    assert source_plan["missing_jd_fields_policy"] == "ask_hr_not_user_and_do_not_block_recommendation"
    assert {
        "opening_status",
        "city_or_work_location",
        "onsite_days_or_arrival",
    }.issubset(set(source_plan["hr_confirmation_fields_when_jd_silent"]))


def test_source_policy_validator_rejects_login_only_and_private_sources(tmp_path):
    source_plan = {
        "public_source_research_plan": {
            "run_id": "run-test",
            "policy_ref": ".agents/skills/career-pipeline/references/source-policy.md",
            "network_execution_default": "disabled_until_controller_source_policy_ack",
            "research_tasks": [
                {
                    "task_id": "bad-private-resume",
                    "agent": "job-scout",
                    "claim_field": "candidate_condition",
                    "source_type": "private_resume",
                    "source_priority": 0,
                    "allowed": True,
                    "requires_login": False,
                    "may_set_weight": True,
                    "may_set_final_decision": True,
                    "evidence_strength_floor": "strong",
                    "privacy_action": "none",
                    "query_template": "collect private resumes",
                    "output_fields": ["weight_provenance"],
                },
                {
                    "task_id": "bad-login",
                    "agent": "job-scout",
                    "claim_field": "jd_requirement",
                    "source_type": "recruitment_platform_jd",
                    "source_priority": 3,
                    "allowed": True,
                    "requires_login": True,
                    "may_set_weight": True,
                    "may_set_final_decision": True,
                    "evidence_strength_floor": "medium",
                    "privacy_action": "cache_metadata_only",
                    "query_template": "crawl login-only JD",
                    "output_fields": ["evidence_basis"],
                },
            ],
            "blocked_source_types": [],
        }
    }
    plan_path = tmp_path / "bad-source-plan.json"
    plan_path.write_text(json.dumps(source_plan), encoding="utf-8")

    result = run_python(VALIDATOR, "--source-plan", str(plan_path))

    assert result.returncode == 1
    assert "private_resume" in result.stderr
    assert "requires_login" in result.stderr


def test_source_policy_validator_rejects_weak_social_media_as_final_basis(tmp_path):
    source_plan = {
        "public_source_research_plan": {
            "run_id": "run-test",
            "policy_ref": ".agents/skills/career-pipeline/references/source-policy.md",
            "network_execution_default": "disabled_until_controller_source_policy_ack",
            "research_tasks": [
                {
                    "task_id": "weak-social",
                    "agent": "market-sentiment-analyzer",
                    "claim_field": "company_reputation",
                    "source_type": "social_media_weak",
                    "source_priority": 5,
                    "allowed": True,
                    "requires_login": False,
                    "may_set_weight": True,
                    "may_set_final_decision": True,
                    "evidence_strength_floor": "weak",
                    "privacy_action": "aggregate_deidentified_only",
                    "query_template": "single anonymous post",
                    "output_fields": ["weight_provenance"],
                }
            ],
            "blocked_source_types": [],
        }
    }
    plan_path = tmp_path / "weak-source-plan.json"
    plan_path.write_text(json.dumps(source_plan), encoding="utf-8")

    result = run_python(VALIDATOR, "--source-plan", str(plan_path))

    assert result.returncode == 1
    assert "social_media_weak" in result.stderr
    assert "final" in result.stderr.lower()


def test_skill_documents_require_public_application_urls():
    skill_text = (
        ROOT / ".agents" / "skills" / "career-pipeline" / "SKILL.md"
    ).read_text(encoding="utf-8")
    policy_text = (
        ROOT
        / ".agents"
        / "skills"
        / "career-pipeline"
        / "references"
        / "application-url-output-policy.md"
    ).read_text(encoding="utf-8")
    data_catalog = (
        ROOT
        / ".agents"
        / "skills"
        / "career-pipeline"
        / "references"
        / "data-catalog.md"
    ).read_text(encoding="utf-8")

    assert "application-url-output-policy.md" in skill_text
    assert "recommended jobs, internships, or application targets" in skill_text
    assert "application_url_candidates" in policy_text
    assert "blocked_application_targets_without_public_url" in policy_text
    assert "ask_hr_about" in policy_text
    assert "If the JD or URL does not state opening status, freshness, city, work location, arrival time, onsite days, deadline, or headcount, do not block the recommendation" in policy_text
    assert "official_application_entrypoints.zh-CN.json" in data_catalog


def test_role_prompts_gate_application_recommendations_on_public_urls():
    job_scout = (ROOT / ".codex" / "agents" / "job-scout.toml").read_text(
        encoding="utf-8"
    )
    match_strategist = (
        ROOT / ".codex" / "agents" / "match-strategist.toml"
    ).read_text(encoding="utf-8")
    hr_supervisor = (ROOT / ".codex" / "agents" / "hr-supervisor.toml").read_text(
        encoding="utf-8"
    )
    factual_reviewer = (
        ROOT / ".codex" / "agents" / "factual-reviewer.toml"
    ).read_text(encoding="utf-8")

    assert "application_url_candidates" in job_scout
    assert "blocked_application_targets_without_public_url" in job_scout
    assert "ask_hr_about" in job_scout
    assert "recommended_application_targets" in match_strategist
    assert "concrete application recommendation" in match_strategist
    assert "Do not turn missing opening status, freshness, city, work location, onsite days, arrival time, deadline, or headcount into a blocker" in match_strategist
    assert "public URL" in hr_supervisor
    assert "application_url_review" in hr_supervisor
    assert "professional, concise, resume-like user-facing summary" in hr_supervisor
    assert "application_url_fact_review" in factual_reviewer
    assert "missing HR-operational fields" in factual_reviewer


def test_role_prompts_cover_hr_questions_and_concrete_project_recommendations():
    learning_prompt = (
        ROOT / ".codex" / "agents" / "learning-path-strategist.toml"
    ).read_text(encoding="utf-8")
    hr_supervisor = (ROOT / ".codex" / "agents" / "hr-supervisor.toml").read_text(
        encoding="utf-8"
    )
    role_contracts = (
        ROOT
        / ".agents"
        / "skills"
        / "career-pipeline"
        / "references"
        / "role-output-contracts.md"
    ).read_text(encoding="utf-8")
    user_flow = (
        ROOT
        / ".agents"
        / "skills"
        / "career-pipeline"
        / "references"
        / "user-interaction-flow.md"
    ).read_text(encoding="utf-8")

    for term in [
        "project_recommendations",
        "project_selection_rubric",
        "recommended_project_mode",
        "implementation_steps",
        "proof_artifacts",
        "resume_conversion_conditions",
        "discover_project_candidates.py",
        "audit_project_repository.py",
        "build_project_interview_pack.py",
        "must not be written as completed resume claims",
    ]:
        assert term in learning_prompt
        assert term in role_contracts

    for term in [
        "hr_real_question_bank",
        "likely_interview_questions",
        "target or recommended company",
        "not_model_generated",
        "source_ref",
        "verified HR public posts",
        "candidate experience",
        "social media weak signals",
        "resume_defensibility_checks",
        "preparation only",
        "do not generate HR wording yourself",
    ]:
        assert term in hr_supervisor
        assert term in role_contracts

    assert "HR/面试可能追问" in user_flow
    assert "具体项目建议" in user_flow


def test_project_toolchain_is_documented_in_skill_entrypoint():
    skill_text = SKILL_MD.read_text(encoding="utf-8")

    for term in [
        "discover_project_candidates.py",
        "audit_project_repository.py",
        "build_project_interview_pack.py",
        "local source audit",
        "project interview pack",
    ]:
        assert term in skill_text


def test_user_facing_package_rules_are_documented_across_runtime_layers():
    user_flow = (
        ROOT
        / ".agents"
        / "skills"
        / "career-pipeline"
        / "references"
        / "user-interaction-flow.md"
    ).read_text(encoding="utf-8")
    deployment_flow = REAL_USER_DEPLOYMENT_FLOW.read_text(encoding="utf-8")
    role_contracts = (
        ROOT
        / ".agents"
        / "skills"
        / "career-pipeline"
        / "references"
        / "role-output-contracts.md"
    ).read_text(encoding="utf-8")
    orchestrator = (ROOT / ".codex" / "agents" / "career-orchestrator.toml").read_text(
        encoding="utf-8"
    )
    hr_supervisor = (ROOT / ".codex" / "agents" / "hr-supervisor.toml").read_text(
        encoding="utf-8"
    )

    for text in [user_flow, deployment_flow, role_contracts, orchestrator, hr_supervisor]:
        assert "user_facing_package" in text
        assert "blocked_outputs" in text
        assert "run directories" in text or "run_dir" in text
        assert "next_three_actions" in text


def test_standard_real_user_flow_is_documented_without_internal_terms():
    user_flow = (
        ROOT
        / ".agents"
        / "skills"
        / "career-pipeline"
        / "references"
        / "user-interaction-flow.md"
    ).read_text(encoding="utf-8")
    deployment_flow = REAL_USER_DEPLOYMENT_FLOW.read_text(encoding="utf-8")
    orchestrator = (ROOT / ".codex" / "agents" / "career-orchestrator.toml").read_text(
        encoding="utf-8"
    )
    hr_supervisor = (ROOT / ".codex" / "agents" / "hr-supervisor.toml").read_text(
        encoding="utf-8"
    )
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    for text in [user_flow, deployment_flow, orchestrator, hr_supervisor]:
        assert "Standard Real User Flow" in text
        for phrase in [
            "first user sentence",
            "skill opening",
            "one compact information request",
            "job-source search",
            "match judgment",
            "learning advice",
            "resume direction",
            "final user-facing report",
        ]:
            assert phrase in text
        assert "用户不需要了解 subagent、JSON、runner" in text

    assert "自然聊天" in readme
    assert "用户不需要理解 subagent、JSON、runner 或 adapter" in readme


def test_incomplete_user_flow_pressure_case_is_documented_as_standard_case():
    manual_test = (
        ROOT / "docs" / "manual-tests" / "incomplete-undergrad-user-flow-2026-06-28.md"
    ).read_text(encoding="utf-8")

    for phrase in [
        "先介绍 skill",
        "不问太多问题",
        "基于已有信息先给方向",
        "明确缺什么",
        "不乱推荐具体岗位",
        "学习路径",
        "简历包装建议",
    ]:
        assert phrase in manual_test


def test_target_job_fit_policy_does_not_overblock_when_current_jd_details_are_missing():
    orchestrator = (ROOT / ".codex" / "agents" / "career-orchestrator.toml").read_text(
        encoding="utf-8"
    )
    runtime_execution = (
        ROOT
        / ".agents"
        / "skills"
        / "career-pipeline"
        / "references"
        / "runtime-execution-layer.md"
    ).read_text(encoding="utf-8")
    invocation_contract = (
        ROOT
        / ".agents"
        / "skills"
        / "career-pipeline"
        / "references"
        / "subagent-invocation-contract.md"
    ).read_text(encoding="utf-8")
    readme_text = (ROOT / "README.md").read_text(encoding="utf-8")

    for text in [orchestrator, runtime_execution, invocation_contract, readme_text]:
        assert "prepare-first" in text or "prepare_first" in text
        assert "ask_hr_about" in text

    forbidden_fragments = [
        "block final readiness without current JD/public evidence",
        "requires current JD text or current public JD retrieval before final resume tailoring",
        "block `current_fit_assessment`, `application_readiness_decision`, `learning_plan_before_application`",
        "Both must return blockers instead of final judgments when current JD evidence is missing",
        "apply-now decisions, role-specific fit claims, and tailored resume advice require current JD text or a current public JD URL",
    ]
    for fragment in forbidden_fragments:
        assert fragment not in orchestrator
        assert fragment not in runtime_execution
        assert fragment not in invocation_contract
        assert fragment not in readme_text


def test_target_job_fit_prepare_first_policy_is_consistent_across_role_docs():
    learning_prompt = (
        ROOT / ".codex" / "agents" / "learning-path-strategist.toml"
    ).read_text(encoding="utf-8")
    data_catalog = (
        ROOT
        / ".agents"
        / "skills"
        / "career-pipeline"
        / "references"
        / "data-catalog.md"
    ).read_text(encoding="utf-8")
    interaction_flow = (
        ROOT
        / ".agents"
        / "skills"
        / "career-pipeline"
        / "references"
        / "user-interaction-flow.md"
    ).read_text(encoding="utf-8")
    manual_flow = (
        ROOT
        / ".agents"
        / "skills"
        / "career-pipeline"
        / "references"
        / "manual-controller-runtime-flow.md"
    ).read_text(encoding="utf-8")

    for text in [learning_prompt, data_catalog, interaction_flow, manual_flow]:
        assert "prepare-first" in text or "prepare_first" in text
        assert "ask_hr_about" in text

    forbidden_fragments = [
        "Learning priorities, project choices, and ready-to-apply conditions require current JD/company/HR evidence or user-provided materials.",
        "specific role analysis still requires current JD text or a current public JD URL",
        "allow targeted analysis only after current JD/company evidence is available",
        "treat missing opening status, city, onsite days, arrival time, deadline, headcount, or internship duration as user-owned facts",
    ]
    for fragment in forbidden_fragments:
        assert fragment not in learning_prompt
        assert fragment not in data_catalog
        assert fragment not in interaction_flow
        assert fragment not in manual_flow


def test_factual_reviewer_prompt_requires_controller_evidence_correction():
    factual_reviewer = (
        ROOT / ".codex" / "agents" / "factual-reviewer.toml"
    ).read_text(encoding="utf-8")

    assert "controller_public_evidence" in factual_reviewer
    assert "controller evidence wins" in factual_reviewer
    assert "stale role claim" in factual_reviewer
    assert "evidence_challenges" in factual_reviewer
    assert "disagreements_with" in factual_reviewer


def test_real_user_deployment_flow_documents_subagent_sources_and_judgment_basis():
    flow_text = (
        ROOT
        / ".agents"
        / "skills"
        / "career-pipeline"
        / "references"
        / "real-user-deployment-and-use-flow.md"
    ).read_text(encoding="utf-8")
    required_roles = [
        "InputNormalizer",
        "CareerOrchestrator",
        "MajorClusterClassifier",
        "ProfileExtractor",
        "JDAnalyzer",
        "JobScout",
        "CompanyIntelligenceAnalyst",
        "MarketSentimentAnalyzer",
        "MatchStrategist",
        "LearningPathStrategist",
        "PersonalBrandingStrategist",
        "HRSupervisor",
        "ResumeFormatGate",
        "ResumeArchitect",
        "FactualReviewer",
    ]

    assert "Install And Enable" in flow_text
    assert "Role-by-Role Runtime Work" in flow_text
    assert "Data Sources" in flow_text
    assert "Judgment Basis" in flow_text
    assert "application_url_candidates" in flow_text
    for role in required_roles:
        assert role in flow_text


def test_manual_controller_flow_documents_codex_side_search_and_subagents():
    flow_text = (
        ROOT
        / ".agents"
        / "skills"
        / "career-pipeline"
        / "references"
        / "manual-controller-runtime-flow.md"
    ).read_text(encoding="utf-8")
    network_text = (
        ROOT
        / ".agents"
        / "skills"
        / "career-pipeline"
        / "references"
        / "runtime-network-and-adapter-setup.md"
    ).read_text(encoding="utf-8")
    skill_text = (
        ROOT / ".agents" / "skills" / "career-pipeline" / "SKILL.md"
    ).read_text(encoding="utf-8")

    assert "manual-controller-runtime-flow.md" in skill_text
    assert "Codex-side source search" in flow_text
    assert "API is not required" in flow_text
    assert "main conversation controller" in flow_text
    assert "search_results.json" in flow_text
    assert "subagent_work_orders.json" in flow_text
    assert "source_policy_ack" in flow_text
    assert "public URL" in flow_text
    assert "Manual Controller MVP" in network_text
    assert "batched_artifact_handoff" in flow_text
    assert "dispatch_batches" in flow_text
    assert "close completed subagents" in flow_text
    assert "close_completed_subagents" in network_text
    assert "artifact_handoff_required" in skill_text


def test_work_orders_require_serialized_utf8_prompt_bundle_content(tmp_path):
    run_root = tmp_path / ".career-pipeline-runs"
    simulate = run_python(
        SIMULATOR,
        "--task-type",
        "job_search",
        "--input-text",
        "软件工程大三，Python 和 C++，想找上海后端开发实习",
        "--run-root",
        str(run_root),
        "--route",
        "job_search",
    )
    assert simulate.returncode == 0, simulate.stderr
    run_id = json.loads(simulate.stdout)["runner_response"]["run_id"]
    run_dir = run_root / run_id

    plan = run_python(PLAN_BUILDER, "--run-dir", str(run_dir), "--build-prompt-bundles")
    assert plan.returncode == 0, plan.stderr
    orders_result = run_python(WORK_ORDER_BUILDER, "--run-dir", str(run_dir))
    assert orders_result.returncode == 0, orders_result.stderr

    orders = json.loads((run_dir / "invocations" / "subagent_work_orders.json").read_text(encoding="utf-8"))[
        "subagent_work_orders"
    ]["orders"]
    assert orders
    instruction = orders[0]["execution_instruction"]
    assert "serialized UTF-8 prompt_bundle_ref content" in instruction
    assert "Do not rely on PowerShell terminal rendering for Chinese JSON" in instruction


def test_source_policy_documents_access_wall_recovery_and_accuracy_tiers():
    source_policy = (
        ROOT
        / ".agents"
        / "skills"
        / "career-pipeline"
        / "references"
        / "source-policy.md"
    ).read_text(encoding="utf-8")
    url_policy = (
        ROOT
        / ".agents"
        / "skills"
        / "career-pipeline"
        / "references"
        / "application-url-output-policy.md"
    ).read_text(encoding="utf-8")
    network_setup = RUNTIME_NETWORK_ADAPTER_SETUP.read_text(encoding="utf-8")

    required_source_policy_terms = [
        "Access-Wall And Dynamic-Page Recovery",
        "login wall",
        "CAPTCHA",
        "JavaScript shell",
        "automatic source substitution",
        "Accuracy Tiers",
        "Accuracy Tier A",
        "Accuracy Tier B",
        "Accuracy Tier C",
        "Accuracy Tier D",
        "cannot support role requirements",
    ]
    for term in required_source_policy_terms:
        assert term in source_policy

    required_url_policy_terms = [
        "Access-Wall Handling",
        "login wall",
        "do not show that URL as a recommended target",
        "replacement_public_url_required",
        "source_accuracy_tier",
    ]
    for term in required_url_policy_terms:
        assert term in url_policy

    assert "Access-Wall Runtime Recovery" in network_setup
    assert "source_attempt_log" in network_setup
    assert "replace the source automatically" in network_setup


def test_recruitment_role_prompts_avoid_login_walls_and_require_accuracy_tiers():
    role_paths = [
        ROOT / ".codex" / "agents" / "job-scout.toml",
        ROOT / ".codex" / "agents" / "jd-analyzer.toml",
        ROOT / ".codex" / "agents" / "company-intelligence-analyst.toml",
        ROOT / ".codex" / "agents" / "market-sentiment-analyzer.toml",
        ROOT / ".codex" / "agents" / "hr-supervisor.toml",
        ROOT / ".codex" / "agents" / "factual-reviewer.toml",
    ]

    for path in role_paths:
        text = path.read_text(encoding="utf-8")
        assert "Access-wall recovery" in text
        assert "login wall" in text
        assert "CAPTCHA" in text
        assert "automatic source substitution" in text
        assert "source_accuracy_tier" in text
        assert "weak sources" in text

    job_scout = (ROOT / ".codex" / "agents" / "job-scout.toml").read_text(
        encoding="utf-8"
    )
    assert "replacement_public_url_required" in job_scout
    assert "source_attempt_log" in job_scout

    factual_reviewer = (
        ROOT / ".codex" / "agents" / "factual-reviewer.toml"
    ).read_text(encoding="utf-8")
    assert "reject final wording" in factual_reviewer
    assert "Accuracy Tier C or D" in factual_reviewer
