#!/usr/bin/env python
import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


class CareerPipelineRunError(Exception):
    pass


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def script_dir() -> Path:
    return Path(__file__).resolve().parent


def run_python(script_name: str, *args: str) -> dict[str, Any]:
    script_path = script_dir() / script_name
    result = subprocess.run(
        [sys.executable, str(script_path), *args],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise CareerPipelineRunError(
            f"{script_name} failed with exit code {result.returncode}: {result.stderr.strip()}"
        )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise CareerPipelineRunError(f"{script_name} returned non-JSON output: {exc}") from exc


def require_response(payload: dict[str, Any], key: str, script_name: str) -> dict[str, Any]:
    value = payload.get(key)
    if not isinstance(value, dict):
        raise CareerPipelineRunError(f"{script_name}: missing `{key}` response")
    return value


def build_blocked_by(adapter_response: dict[str, Any], allowed_sources_path: Path) -> list[str]:
    blocked = []
    if adapter_response.get("real_subagent_execution") is False:
        blocked.append("real_subagent_adapter_not_configured")
    if not allowed_sources_path.is_file():
        blocked.append("public_source_discovery_not_ready")
    else:
        allowed = load_json(allowed_sources_path)
        if not allowed.get("sources"):
            blocked.append("no_allowed_public_sources_found")
    if not blocked:
        blocked.append("role_outputs_blocked_until_real_subagent_execution")
    return blocked


def run_pipeline(args: argparse.Namespace) -> dict[str, Any]:
    if args.source_adapter not in {"seed", "external-json"}:
        raise CareerPipelineRunError("supported source adapters are: seed, external-json")
    if args.subagent_adapter not in {"mock-blocked", "external-command"}:
        raise CareerPipelineRunError("supported subagent adapters are: mock-blocked, external-command")
    if args.source_adapter == "external-json" and not args.search_results_json:
        raise CareerPipelineRunError("--search-results-json is required with --source-adapter external-json")
    if args.subagent_adapter == "external-command" and not args.adapter_command:
        raise CareerPipelineRunError("--adapter-command is required with --subagent-adapter external-command")

    simulate_payload = run_python(
        "simulate_runtime_run.py",
        "--task-type",
        args.task_type,
        "--route",
        args.route,
        "--input-text",
        args.input_text,
        "--run-root",
        str(args.run_root),
    )
    simulate_response = require_response(simulate_payload, "runner_response", "simulate_runtime_run.py")
    run_id = str(simulate_response.get("run_id") or "")
    if not run_id:
        raise CareerPipelineRunError("simulate_runtime_run.py did not return a run_id")
    run_dir = args.run_root / run_id

    plan_response = require_response(
        run_python("build_subagent_plan.py", "--run-dir", str(run_dir), "--build-prompt-bundles"),
        "planner_response",
        "build_subagent_plan.py",
    )
    source_plan_response = require_response(
        run_python("build_public_source_plan.py", "--run-dir", str(run_dir)),
        "source_plan_response",
        "build_public_source_plan.py",
    )
    query_plan_response = require_response(
        run_python("discover_public_sources.py", "--run-dir", str(run_dir), "--generate-query-plan-only"),
        "public_source_discovery_response",
        "discover_public_sources.py",
    )
    source_search_args = ["--run-dir", str(run_dir), "--provider", args.source_adapter]
    if args.search_results_json:
        source_search_args.extend(["--search-results-json", str(args.search_results_json)])
    source_search_response = require_response(
        run_python("search_public_sources.py", *source_search_args),
        "public_source_search_response",
        "search_public_sources.py",
    )
    search_results_ref = source_search_response["search_results_ref"]
    source_discovery_response = require_response(
        run_python(
            "discover_public_sources.py",
            "--run-dir",
            str(run_dir),
            "--search-results-json",
            str(run_dir / search_results_ref),
        ),
        "public_source_discovery_response",
        "discover_public_sources.py",
    )
    work_order_response = require_response(
        run_python("build_subagent_work_orders.py", "--run-dir", str(run_dir)),
        "work_order_response",
        "build_subagent_work_orders.py",
    )
    adapter_args = ["--run-dir", str(run_dir)]
    if args.subagent_adapter == "mock-blocked":
        adapter_args.append("--mock-blocked")
    else:
        adapter_args.extend(["--adapter-command", args.adapter_command])
        for adapter_arg in args.adapter_arg:
            adapter_args.extend(["--adapter-arg", adapter_arg])
    adapter_response = require_response(
        run_python("run_subagent_adapter.py", *adapter_args),
        "subagent_adapter_response",
        "run_subagent_adapter.py",
    )

    finalizer_response: dict[str, Any] = {}
    if args.finalize:
        if adapter_response.get("real_subagent_execution") is not True:
            raise CareerPipelineRunError("--finalize requires real subagent execution")
        finalizer_response = require_response(
            run_python("finalize_runtime_run.py", "--run-dir", str(run_dir), "--real-subagent-execution"),
            "finalizer_response",
            "finalize_runtime_run.py",
        )

    generated_sources_ref = source_discovery_response.get("generated_sources_ref") or ""
    allowed_sources_path = run_dir / generated_sources_ref if generated_sources_ref else run_dir / "missing"
    source_discovery_ready = allowed_sources_path.is_file() and bool(load_json(allowed_sources_path).get("sources"))
    final_package_ref = finalizer_response.get("final_package_ref", "")
    exit_status = "success" if final_package_ref else "blocked"
    return {
        "career_pipeline_run_response": {
            "exit_status": exit_status,
            "run_id": run_id,
            "run_dir_ref": str(run_dir),
            "real_subagent_execution": bool(adapter_response.get("real_subagent_execution")),
            "source_discovery_ready": source_discovery_ready,
            "blocked_by": [] if final_package_ref else build_blocked_by(adapter_response, allowed_sources_path),
            "execution_manifest_ref": rel(run_dir / "manifest.json", run_dir),
            "source_plan_ref": source_plan_response.get("source_plan_ref", ""),
            "query_plan_ref": query_plan_response.get("discovery_log_ref", ""),
            "search_results_ref": search_results_ref,
            "allowed_sources_ref": generated_sources_ref,
            "subagent_plan_ref": plan_response.get("subagent_plan_ref", ""),
            "work_orders_ref": work_order_response.get("work_orders_ref", ""),
            "adapter_output_refs": adapter_response.get("output_refs", []),
            "final_package_ref": final_package_ref,
            "blocked_package_ref": rel(run_dir / "final" / "blocked_package.json", run_dir),
            "next_action": "return_final_package" if final_package_ref else "configure_real_subagent_adapter_or_backfill_role_outputs",
        }
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the deterministic local career-pipeline contract shell.")
    parser.add_argument("--task-type", default="job_search")
    parser.add_argument("--route", default="job_search")
    parser.add_argument("--input-text", required=True)
    parser.add_argument("--run-root", default=".career-pipeline-runs", type=Path)
    parser.add_argument("--source-adapter", default="seed")
    parser.add_argument("--search-results-json", type=Path)
    parser.add_argument("--subagent-adapter", default="mock-blocked")
    parser.add_argument("--adapter-command", default="")
    parser.add_argument("--adapter-arg", action="append", default=[])
    parser.add_argument("--finalize", action="store_true")
    args = parser.parse_args(argv)
    try:
        print(json.dumps(run_pipeline(args), ensure_ascii=False, indent=2))
        return 0
    except (OSError, json.JSONDecodeError, KeyError, CareerPipelineRunError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
