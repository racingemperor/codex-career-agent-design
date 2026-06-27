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
ENGINEERING_SMOKE = ROOT / ".agents" / "skills" / "career-pipeline" / "scripts" / "smoke_test_engineering_profiles.py"
WORK_ORDER_BUILDER = ROOT / ".agents" / "skills" / "career-pipeline" / "scripts" / "build_subagent_work_orders.py"
EVIDENCE_BACKFILL = ROOT / ".agents" / "skills" / "career-pipeline" / "scripts" / "backfill_public_evidence.py"
PUBLIC_SOURCE_FETCHER = ROOT / ".agents" / "skills" / "career-pipeline" / "scripts" / "fetch_public_sources.py"
PUBLIC_SOURCE_DISCOVERER = (
    ROOT / ".agents" / "skills" / "career-pipeline" / "scripts" / "discover_public_sources.py"
)
PUBLIC_SOURCE_SEARCHER = ROOT / ".agents" / "skills" / "career-pipeline" / "scripts" / "search_public_sources.py"
SUBAGENT_ADAPTER_RUNNER = ROOT / ".agents" / "skills" / "career-pipeline" / "scripts" / "run_subagent_adapter.py"
CAREER_PIPELINE_RUNNER = ROOT / ".agents" / "skills" / "career-pipeline" / "scripts" / "career_pipeline_run.py"
FINALIZER = ROOT / ".agents" / "skills" / "career-pipeline" / "scripts" / "finalize_runtime_run.py"


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


def test_runtime_execution_layer_points_to_setup_reference():
    text = RUNTIME_EXECUTION_LAYER.read_text(encoding="utf-8")

    assert "runtime-network-and-adapter-setup.md" in text
    assert "Real subagent execution remains blocked until a concrete adapter is configured and tested" in text
    assert "discover_public_sources.py" in text


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
        assert "fit_score" in package["blocked_until_evidence"]
        assert package["hr_supervision_note"]
    md_text = results_md.read_text(encoding="utf-8")
    assert "本科大二 计算机 AI 实习探索" in md_text
    assert "用户端可读包" in md_text
    assert "公开来源研究计划已生成但尚未执行" in md_text
    assert "run_dir" not in user_report.read_text(encoding="utf-8")


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
json.dump(result, open(args.output_json, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
""".lstrip(),
        encoding="utf-8",
    )


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
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["execution_manifest"]["current_stage"] == "final_package_ready"
    assert manifest["run_state"]["stage"] == "final_package_ready"


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

    validation = run_python(VALIDATOR, "--subagent-plan", str(plan_path))
    assert validation.returncode == 0, validation.stderr


def test_validator_rejects_subagent_plan_that_is_not_plan_only(tmp_path):
    plan = {
        "subagent_invocation_plan": {
            "run_id": "run-test",
            "plan_status": "ready",
            "dispatch_queue": [
                {
                    "queue_index": 0,
                    "target_agent": "job-scout",
                    "invocation_ref": "invocations/job-scout.invocation.json",
                    "input_refs": ["input/normalized/runtime_context_packet.json"],
                    "output_artifact_target": "agents/job-scout/output.json",
                    "dispatch_mode": "execute",
                    "status": "running",
                    "allowed_network": True,
                    "requires_human_approval": False,
                    "privacy_class": "derived",
                    "blocked_until": ["human_confirms_real_subagent_execution"],
                }
            ],
        }
    }
    plan_path = tmp_path / "bad-plan.json"
    plan_path.write_text(json.dumps(plan), encoding="utf-8")

    result = run_python(VALIDATOR, "--subagent-plan", str(plan_path))

    assert result.returncode == 1
    assert "plan_only" in result.stderr


def test_validator_rejects_subagent_plan_that_exposes_raw_input(tmp_path):
    plan = {
        "subagent_invocation_plan": {
            "run_id": "run-test",
            "plan_status": "ready",
            "dispatch_queue": [
                {
                    "queue_index": 0,
                    "target_agent": "job-scout",
                    "invocation_ref": "invocations/job-scout.invocation.json",
                    "input_refs": [
                        "input/raw_refs.json",
                        "input/normalized/runtime_context_packet.json",
                    ],
                    "output_artifact_target": "agents/job-scout/output.json",
                    "dispatch_mode": "plan_only",
                    "status": "planned",
                    "allowed_network": False,
                    "requires_human_approval": True,
                    "privacy_class": "derived",
                    "blocked_until": ["human_confirms_real_subagent_execution"],
                }
            ],
        }
    }
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
    assert context["missing_user_owned_facts"] == []
    known_fields = {fact["field"] for fact in context["known_user_facts"]}
    assert {"school_name", "degree_level", "graduation_window"}.issubset(known_fields)


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
    assert "current_fit_assessment" in context["blocked_outputs"]
    assert "learning_plan_before_application" in context["blocked_outputs"]


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


def test_public_source_plan_for_target_job_fit_requires_current_jd_and_gap_evidence(tmp_path):
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
    assert "current_fit_assessment" in source_plan["blocked_outputs_without_current_jd"]
    assert "application_readiness_decision" in source_plan["blocked_outputs_without_current_jd"]
    assert "learning_plan_before_application" in source_plan["blocked_outputs_without_current_jd"]


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
    assert "recommended_application_targets" in match_strategist
    assert "concrete application recommendation" in match_strategist
    assert "public URL" in hr_supervisor
    assert "application_url_review" in hr_supervisor
    assert "application_url_fact_review" in factual_reviewer


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
