#!/usr/bin/env python
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class PackError(Exception):
    pass


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def bullet(items: list[Any], fallback: str) -> str:
    cleaned = [str(item).strip() for item in items if str(item).strip()]
    if not cleaned:
        cleaned = [fallback]
    return "\n".join(f"- {item}" for item in cleaned)


def evidence_paths(audit: dict[str, Any]) -> list[str]:
    paths = [str(item.get("path") or "") for item in audit.get("source_evidence_points") or [] if item.get("path")]
    return list(dict.fromkeys(paths))[:12]


def signal_summary(audit: dict[str, Any]) -> list[str]:
    items = []
    for category, paths in (audit.get("signals") or {}).items():
        if paths:
            items.append(f"{category}: {', '.join(paths[:3])}")
    return items[:10]


def build_pack(audit_payload: dict[str, Any], recommendation: dict[str, Any]) -> tuple[dict[str, Any], str]:
    audit = audit_payload.get("project_repo_audit")
    if not isinstance(audit, dict):
        raise PackError("audit JSON must contain project_repo_audit")
    name = recommendation.get("project_name") or audit.get("name") or "project"
    target = recommendation.get("target_role_family") or "target role"
    planned = [str(item) for item in recommendation.get("planned_modifications") or []]
    completed = [str(item) for item in recommendation.get("completed_modifications") or []]
    proof = [str(item) for item in recommendation.get("proof_artifacts") or []]
    evidence = evidence_paths(audit)
    signals = signal_summary(audit)
    resume_ready = completed + [
        f"已通过本地源码审计确认 `{path}` 可作为项目讲解证据" for path in evidence[:3]
    ]
    not_ready = planned
    pack = {
        "project_interview_pack": {
            "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "project_name": name,
            "target_role_family": target,
            "existing_capability": signals,
            "suggested_modifications": planned,
            "resume_ready_claims": resume_ready,
            "not_resume_ready_until_completed": not_ready,
            "proof_artifacts": proof + evidence[:6],
            "source_audit_ref": audit.get("repo_path", ""),
        }
    }
    text = "\n\n".join(
        [
            "# Project Interview Pack",
            f"## 项目定位\n- 项目：{name}\n- 目标方向：{target}\n- JD 摘要：{recommendation.get('target_jd_summary', '待补充目标 JD 摘要')}",
            "## 现有能力\n" + bullet(signals, "当前只完成了基础源码审计，仍需补充可讲清的业务链路。"),
            "## 建议改造\n"
            + bullet(planned, "补一个与目标岗位直接相关的小改造，例如 API、测试、缓存、评估或部署证据。"),
            "## 可写入简历\n"
            + bullet(resume_ready, "只有已经完成并能解释个人贡献的内容可以写入简历。")
            + "\n- 未完成内容不能写成已完成项目；建议改造完成前只能写为学习计划或待补证据。",
            "## STAR 简历项目\n"
            "- S/T：围绕目标岗位问题，说明为什么选择这个项目。\n"
            "- A：说明已完成的源码审计、最小运行路径或已完成改造。\n"
            "- A：说明个人贡献，区分原项目已有能力和自己的改造。\n"
            "- R：用公开证据、测试、截图、日志或复盘支撑结果；没有指标时不要写提升百分比。",
            "## 面试官追问\n"
            + bullet(
                [
                    "这个项目为什么匹配目标 JD？",
                    "原项目已有能力是什么，你自己的改造是什么？",
                    "核心输入输出、状态流转、失败边界是什么？",
                    "如果改造还没完成，下一步怎么验证？",
                    "简历中的每一条项目描述分别由哪些文件或证据支撑？",
                ],
                "准备项目动机、个人贡献、输入输出、失败边界和证据链。",
            ),
            "## 核心代码讲解\n" + bullet(evidence, "先补充本地源码审计，再选择入口文件讲解。"),
            "## 交付证据\n" + bullet(proof + evidence[:6], "README、代码入口、测试、截图、日志或复盘。"),
        ]
    )
    return pack, text + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a resume/interview pack from project audit evidence.")
    parser.add_argument("--audit-json", required=True, type=Path)
    parser.add_argument("--recommendation-json", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        pack, text = build_pack(load_json(args.audit_json), load_json(args.recommendation_json))
        json_path = args.out_dir / "project_interview_pack.json"
        md_path = args.out_dir / "project_interview_pack.md"
        write_json(json_path, pack)
        write_text(md_path, text)
        print(
            json.dumps(
                {
                    "project_interview_pack_response": {
                        "exit_status": "success",
                        "pack_json": json_path.name,
                        "pack_md": md_path.name,
                    }
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    except (OSError, json.JSONDecodeError, PackError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
