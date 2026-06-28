#!/usr/bin/env python
import argparse
import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


SHALLOW_TERMS = {
    "awesome",
    "template",
    "boilerplate",
    "demo",
    "example",
    "starter",
    "thin wrapper",
    "wrapper",
    "browser extension",
    "extension",
    "side panel",
    "prompt template",
    "prompt collection",
    "sdk",
    "framework",
    "library",
}

BUSINESS_TERMS = {
    "ticket",
    "workflow",
    "order",
    "payment",
    "inventory",
    "helpdesk",
    "crm",
    "erp",
    "knowledge",
    "report",
    "research",
    "task",
    "state",
    "status",
    "approval",
}

ENGINEERING_TERMS = {
    "api",
    "rest",
    "database",
    "mysql",
    "postgres",
    "redis",
    "cache",
    "queue",
    "docker",
    "test",
    "evaluation",
    "eval",
    "auth",
    "permission",
    "scheduler",
    "migration",
    "spring",
    "fastapi",
    "agent",
    "tool calling",
    "persistence",
}


class DiscoveryError(Exception):
    pass


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def parse_candidates(payload: dict[str, Any]) -> list[dict[str, Any]]:
    if isinstance(payload.get("candidates"), list):
        return [item for item in payload["candidates"] if isinstance(item, dict)]
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    raise DiscoveryError("candidates JSON must be a list or contain `candidates`")


def token_set(text: str) -> set[str]:
    return {item for item in re.split(r"[^A-Za-z0-9+#.\u4e00-\u9fff]+", text.lower()) if item}


def candidate_text(candidate: dict[str, Any]) -> str:
    values = [
        candidate.get("name", ""),
        candidate.get("repo_url", ""),
        candidate.get("bucket", ""),
        candidate.get("language", ""),
        candidate.get("description", ""),
        candidate.get("readme_probe", ""),
        " ".join(str(item) for item in candidate.get("topics") or []),
    ]
    return " ".join(str(value) for value in values).lower()


def candidate_content_text(candidate: dict[str, Any]) -> str:
    values = [
        candidate.get("name", ""),
        candidate.get("bucket", ""),
        candidate.get("language", ""),
        candidate.get("description", ""),
        candidate.get("readme_probe", ""),
        " ".join(str(item) for item in candidate.get("topics") or []),
    ]
    return " ".join(str(value) for value in values).lower()


def star_score(stars: Any) -> int:
    try:
        count = int(stars)
    except (TypeError, ValueError):
        return 0
    if count >= 1000:
        return 10
    if count >= 200:
        return 8
    if count >= 50:
        return 6
    if count > 0:
        return 3
    return 0


def parse_date(raw: Any) -> date | None:
    text = str(raw or "").strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y-%m", "%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def activity_score(raw: Any) -> int:
    parsed = parse_date(raw)
    if parsed is None:
        return 0
    today = datetime.now(timezone.utc).date()
    days = max((today - parsed).days, 0)
    if days <= 180:
        return 10
    if days <= 365:
        return 7
    if days <= 730:
        return 4
    return 1


def mode_fit(candidate: dict[str, Any], mode: str, text: str) -> tuple[int, list[str]]:
    reasons: list[str] = []
    bucket = str(candidate.get("bucket") or "").lower()
    if mode == "backend-only":
        if "agent" in text and not any(term in text for term in ["backend", "spring", "api", "database"]):
            return -8, ["mode_conflict_agent_only"]
        reasons.append("backend_mode")
        return 8, reasons
    if mode == "agent-only":
        agent_signals = ["agent", "tool calling", "workflow", "planner", "evaluation", "persistence"]
        hits = [term for term in agent_signals if term in text]
        if len(hits) < 2:
            return -8, ["mode_conflict_not_business_agent"]
        return 8 + min(6, len(hits)), ["business_agent:" + ",".join(hits[:4])]
    if mode == "mixed":
        if "agent" in text or "智能体" in bucket:
            return 8, ["mixed_agent_bucket"]
        return 8, ["mixed_backend_bucket"]
    if mode == "safe-mode":
        safe_hits = [term for term in ["docker", "test", "readme", "api", "sqlite", "local"] if term in text]
        return 6 + min(6, len(safe_hits)), ["safe:" + ",".join(safe_hits[:4])]
    if mode == "challenge-mode":
        challenge_hits = [term for term in ["queue", "cache", "evaluation", "workflow", "distributed", "state"] if term in text]
        return 6 + min(8, len(challenge_hits) * 2), ["challenge:" + ",".join(challenge_hits[:4])]
    return 4, ["default_mode"]


def score_candidate(candidate: dict[str, Any], jd_text: str, target_role: str, mode: str) -> dict[str, Any]:
    text = candidate_text(candidate)
    content_text = candidate_content_text(candidate)
    jd_tokens = token_set(jd_text + " " + target_role)
    candidate_tokens = token_set(text)
    matched_terms = sorted(jd_tokens & candidate_tokens)
    shallow_hits = sorted(term for term in SHALLOW_TERMS if term in content_text)
    business_hits = sorted(term for term in BUSINESS_TERMS if term in text)
    engineering_hits = sorted(term for term in ENGINEERING_TERMS if term in text)
    mode_points, mode_reasons = mode_fit(candidate, mode, text)
    breakdown = {
        "jd_match_score": min(30, len(matched_terms) * 5),
        "business_closure_score": min(18, len(business_hits) * 4),
        "engineering_depth_score": min(22, len(engineering_hits) * 3),
        "activity_score": activity_score(candidate.get("last_pushed_at") or candidate.get("last_commit")),
        "star_score": star_score(candidate.get("stars")),
        "mode_fit_score": mode_points,
        "shallow_penalty": -25 if shallow_hits else 0,
        "high_star_penalty": -6 if int(candidate.get("stars") or 0) >= 20000 else 0,
    }
    score = sum(breakdown.values())
    excluded_reasons: list[str] = []
    if shallow_hits:
        excluded_reasons.append("shallow_or_wrapper:" + ",".join(shallow_hits[:4]))
    if "iot" in text or "embedded" in text or "hardware" in text:
        excluded_reasons.append("hardware_or_iot_default_excluded")
    if mode_points < 0:
        excluded_reasons.extend(mode_reasons)
    if not str(candidate.get("repo_url") or "").startswith(("http://", "https://")):
        excluded_reasons.append("missing_public_repo_url")
    result = dict(candidate)
    result.update(
        {
            "score": score,
            "score_breakdown": breakdown,
            "matched_jd_terms": matched_terms[:12],
            "business_signals": business_hits[:10],
            "engineering_signals": engineering_hits[:12],
            "mode_reasons": mode_reasons,
            "excluded_reasons": excluded_reasons,
            "recommendation_status": "excluded" if excluded_reasons else "shortlist",
        }
    )
    return result


def render_shortlist(payload: dict[str, Any]) -> str:
    lines = ["# Project Candidate Shortlist", ""]
    lines.append("## Shortlist")
    for item in payload["shortlist"]:
        lines.append(
            f"- {item.get('name')} ({item.get('score')}): {item.get('repo_url')} | "
            f"JD: {', '.join(item.get('matched_jd_terms') or [])}"
        )
    lines.extend(["", "## Excluded"])
    for item in payload["excluded"]:
        lines.append(
            f"- {item.get('name')}: {'; '.join(item.get('excluded_reasons') or [])}"
        )
    return "\n".join(lines) + "\n"


def discover(args: argparse.Namespace) -> dict[str, Any]:
    candidates = parse_candidates(load_json(args.candidates_json))
    scored = [
        score_candidate(candidate, args.jd_text or "", args.target_role or "", args.mode)
        for candidate in candidates
    ]
    shortlist = sorted(
        [item for item in scored if item["recommendation_status"] == "shortlist"],
        key=lambda item: item["score"],
        reverse=True,
    )[: args.limit]
    excluded = sorted(
        [item for item in scored if item["recommendation_status"] == "excluded"],
        key=lambda item: item["score"],
        reverse=True,
    )
    payload = {
        "project_candidate_discovery": {
            "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "target_role": args.target_role,
            "mode": args.mode,
            "source": "user_or_adapter_provided_candidates_json",
            "shortlist": shortlist,
            "excluded": excluded,
            "rules": [
                "star count is capped as a weak community signal",
                "shallow wrappers, browser extensions, templates, and SDK/framework-only projects are excluded",
                "final resume claims still require local source audit",
            ],
        }
    }
    out_dir = args.out_dir
    json_path = out_dir / "project_candidate_discovery.json"
    md_path = out_dir / "project_candidate_shortlist.md"
    write_json(json_path, payload)
    write_text(md_path, render_shortlist(payload["project_candidate_discovery"]))
    return {
        "project_candidate_discovery_response": {
            "exit_status": "success",
            "discovery_json": json_path.name,
            "shortlist_md": md_path.name,
            "shortlist_count": len(shortlist),
            "excluded_count": len(excluded),
        }
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Score public project candidates for career-pipeline project recommendations.")
    parser.add_argument("--candidates-json", required=True, type=Path)
    parser.add_argument("--target-role", default="")
    parser.add_argument("--jd-text", default="")
    parser.add_argument(
        "--mode",
        default="mixed",
        choices=["agent-only", "backend-only", "mixed", "safe-mode", "challenge-mode"],
    )
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--limit", type=int, default=4)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(discover(args), ensure_ascii=False, indent=2))
        return 0
    except (OSError, json.JSONDecodeError, DiscoveryError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
