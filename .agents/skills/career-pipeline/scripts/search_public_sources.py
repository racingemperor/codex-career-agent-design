#!/usr/bin/env python
import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


SOURCE_COLLECTION_TARGETS_REF = "data/company_signals/source_collection_targets.zh-CN.json"


class PublicSourceSearchError(Exception):
    pass


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def load_discovery_log(run_dir: Path, discovery_log_ref: str) -> dict[str, Any]:
    payload = load_json(run_dir / discovery_log_ref)
    discovery = payload.get("public_source_discovery")
    if not isinstance(discovery, dict):
        raise PublicSourceSearchError(f"{discovery_log_ref}: missing public_source_discovery")
    queries = discovery.get("search_queries")
    if not isinstance(queries, list) or not queries:
        raise PublicSourceSearchError(f"{discovery_log_ref}: search_queries must be non-empty")
    return discovery


def load_source_targets() -> list[dict[str, Any]]:
    payload = load_json(repo_root() / SOURCE_COLLECTION_TARGETS_REF)
    targets = payload.get("company_targets")
    if not isinstance(targets, list):
        raise PublicSourceSearchError(f"{SOURCE_COLLECTION_TARGETS_REF}: missing company_targets")
    return targets


def matches_company(query: str, target: dict[str, Any]) -> bool:
    haystack = query.lower()
    candidates = [target.get("company_id", ""), target.get("company_name", "")]
    candidates.extend(target.get("aliases", []))
    return any(str(candidate).lower() in haystack for candidate in candidates if candidate)


def generic_result_for_query(query: dict[str, Any]) -> dict[str, Any]:
    task_id = query["task_id"]
    source_type = query.get("source_type") or "official_or_primary"
    url_by_type = {
        "official_or_primary": "https://careers.example.com/",
        "official_school_notice": "https://career.example.edu.cn/",
        "recruitment_platform_jd": "https://www.nowcoder.com/jobs",
        "verified_hr_public_post": "https://mp.weixin.qq.com/",
        "candidate_experience_secondary": "https://www.nowcoder.com/discuss",
        "social_media_weak": "https://www.zhihu.com/",
        "public_report": "https://www.sec.gov/",
    }
    return {
        "task_id": task_id,
        "url": url_by_type.get(str(source_type), "https://careers.example.com/"),
        "title": f"Public source seed for {task_id}",
        "snippet": query.get("query", ""),
        "source_type": source_type,
        "provider": "seed",
    }


def seed_results_for_query(query: dict[str, Any], company_targets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    query_text = str(query.get("query") or "")
    task_id = query.get("task_id")
    source_type = str(query.get("source_type") or "")
    results: list[dict[str, Any]] = []
    for target in company_targets:
        if not matches_company(query_text, target):
            continue
        if source_type in {"official_or_primary", "recruitment_platform_jd"}:
            for source in target.get("official_source_candidates", []):
                url = source.get("url")
                if url:
                    results.append(
                        {
                            "task_id": task_id,
                            "url": url,
                            "title": f"{target.get('company_name', target.get('company_id'))} official recruiting source",
                            "snippet": query_text,
                            "source_type": "official_or_primary",
                            "provider": "seed",
                        }
                    )
        if source_type == "public_report":
            results.append(
                {
                    "task_id": task_id,
                    "url": "https://www.sec.gov/",
                    "title": f"{target.get('company_name', target.get('company_id'))} public report search entry",
                    "snippet": query_text,
                    "source_type": "public_report",
                    "provider": "seed",
                }
            )
        if source_type == "candidate_experience_secondary":
            encoded_company = re.sub(r"\s+", "+", str(target.get("company_name") or target.get("company_id")))
            results.append(
                {
                    "task_id": task_id,
                    "url": f"https://www.nowcoder.com/search?query={encoded_company}",
                    "title": f"{target.get('company_name', target.get('company_id'))} public interview experience search",
                    "snippet": query_text,
                    "source_type": "candidate_experience_secondary",
                    "provider": "seed",
                }
            )
    if not results:
        results.append(generic_result_for_query(query))
    return results


def search_sources(args: argparse.Namespace) -> dict[str, Any]:
    if args.provider != "seed":
        raise PublicSourceSearchError("only the deterministic `seed` provider is implemented in this repository")
    run_dir = args.run_dir
    discovery = load_discovery_log(run_dir, args.discovery_log_ref)
    company_targets = load_source_targets()
    results: list[dict[str, Any]] = []
    seen = set()
    for query in discovery["search_queries"]:
        for result in seed_results_for_query(query, company_targets):
            key = (result.get("task_id"), result.get("url"))
            if key in seen:
                continue
            seen.add(key)
            results.append(result)
    output_path = run_dir / args.output
    write_json(
        output_path,
        {
            "metadata": {
                "run_id": discovery["run_id"],
                "provider": args.provider,
                "user_instruction_required": False,
                "source": SOURCE_COLLECTION_TARGETS_REF,
                "note": "Deterministic seed provider. Replace with browser/search/API provider for live discovery.",
            },
            "search_results": results,
        },
    )
    return {
        "public_source_search_response": {
            "exit_status": "success",
            "run_id": discovery["run_id"],
            "provider": args.provider,
            "user_instruction_required": False,
            "search_results_ref": rel(output_path, run_dir),
            "result_count": len(results),
        }
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a public-source search adapter for generated query plans.")
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--provider", default="seed")
    parser.add_argument("--discovery-log-ref", default="evidence/public_source_discovery_log.json")
    parser.add_argument("--output", default="evidence/search_results.generated.json")
    args = parser.parse_args(argv)
    try:
        print(json.dumps(search_sources(args), ensure_ascii=False, indent=2))
        return 0
    except (OSError, json.JSONDecodeError, KeyError, PublicSourceSearchError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
