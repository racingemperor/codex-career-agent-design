#!/usr/bin/env python
import argparse
import html
import json
import re
import sys
import zipfile
from pathlib import Path
from typing import Any


class ResumeRenderError(Exception):
    pass


def read_text(path: Path) -> str:
    if not path.is_file():
        raise ResumeRenderError(f"draft markdown not found: {path}")
    return path.read_text(encoding="utf-8-sig")


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ResumeRenderError(f"decision package not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ResumeRenderError("decision package must be a JSON object")
    return payload


def write_json_stdout(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def parse_markdown(markdown: str) -> list[dict[str, str]]:
    blocks: list[dict[str, str]] = []
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("# "):
            blocks.append({"type": "title", "text": line[2:].strip()})
        elif line.startswith("## "):
            blocks.append({"type": "section", "text": line[3:].strip()})
        elif line.startswith(("- ", "* ")):
            blocks.append({"type": "bullet", "text": line[2:].strip()})
        else:
            blocks.append({"type": "paragraph", "text": line})
    if not blocks:
        raise ResumeRenderError("draft markdown is empty")
    return blocks


def sanitize_basename(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip())
    return cleaned.strip("._") or "resume"


def user_facing_package_from_decision_package(payload: dict[str, Any]) -> dict[str, Any]:
    decision_package = payload.get("decision_package")
    if not isinstance(decision_package, dict):
        raise ResumeRenderError("decision package JSON must contain decision_package")
    user_facing_package = decision_package.get("user_facing_package")
    if not isinstance(user_facing_package, dict):
        raise ResumeRenderError("decision_package.user_facing_package is missing")
    return user_facing_package


def extract_resume_markdown_from_decision_package(payload: dict[str, Any]) -> str:
    user_facing_package = user_facing_package_from_decision_package(payload)
    resume_draft = user_facing_package.get("resume_draft")
    if not isinstance(resume_draft, dict):
        raise ResumeRenderError("decision_package.user_facing_package.resume_draft is missing")
    draft = str(resume_draft.get("final_resume_draft") or "").strip()
    if not draft:
        raise ResumeRenderError("resume_draft.final_resume_draft is empty")
    return draft


def extract_resume_versions_from_decision_package(payload: dict[str, Any], include_all: bool) -> list[dict[str, str]]:
    user_facing_package = user_facing_package_from_decision_package(payload)
    resume_draft = user_facing_package.get("resume_draft")
    if not isinstance(resume_draft, dict):
        raise ResumeRenderError("decision_package.user_facing_package.resume_draft is missing")
    current_draft = str(resume_draft.get("final_resume_draft") or "").strip()
    if not current_draft:
        raise ResumeRenderError("resume_draft.final_resume_draft is empty")
    versions = [
        {
            "version_key": "resume_draft",
            "markdown_filename": "resume_draft.md",
            "basename": "resume_draft",
            "markdown": current_draft,
        }
    ]
    if include_all:
        growth_preview = user_facing_package.get("growth_resume_preview")
        if isinstance(growth_preview, dict):
            preview_draft = str(growth_preview.get("final_resume_draft") or "").strip()
            if preview_draft:
                versions.append(
                    {
                        "version_key": "growth_resume_preview",
                        "markdown_filename": "growth_resume_preview.md",
                        "basename": "growth_resume_preview",
                        "markdown": preview_draft,
                    }
                )
    return versions


def resolve_draft_source(args: argparse.Namespace) -> tuple[Path, str | None]:
    if args.draft_md and args.decision_package:
        raise ResumeRenderError("use either --draft-md or --decision-package, not both")
    if args.draft_md:
        return args.draft_md, None
    if args.decision_package:
        draft = extract_resume_markdown_from_decision_package(load_json(args.decision_package))
        args.out_dir.mkdir(parents=True, exist_ok=True)
        draft_path = args.out_dir / "resume_draft.md"
        draft_path.write_text(draft + "\n", encoding="utf-8")
        return draft_path, str(args.decision_package)
    raise ResumeRenderError("provide either --draft-md or --decision-package")


def docx_paragraph(text: str, style: str = "") -> str:
    style_xml = f'<w:pStyle w:val="{style}"/>' if style else ""
    return (
        "<w:p>"
        f"<w:pPr>{style_xml}</w:pPr>"
        "<w:r>"
        "<w:rPr><w:rFonts w:ascii=\"Microsoft YaHei\" w:hAnsi=\"Microsoft YaHei\" "
        "w:eastAsia=\"Microsoft YaHei\"/></w:rPr>"
        f"<w:t>{html.escape(text)}</w:t>"
        "</w:r>"
        "</w:p>"
    )


def write_docx(blocks: list[dict[str, str]], path: Path) -> None:
    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>
"""
    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
"""
    styles = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:styleId="Title">
    <w:name w:val="Title"/>
    <w:rPr><w:b/><w:sz w:val="32"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="Heading 1"/>
    <w:rPr><w:b/><w:sz w:val="24"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="ListParagraph">
    <w:name w:val="List Paragraph"/>
  </w:style>
</w:styles>
"""
    body_parts: list[str] = []
    for block in blocks:
        text = block["text"]
        block_type = block["type"]
        if block_type == "title":
            body_parts.append(docx_paragraph(text, "Title"))
        elif block_type == "section":
            body_parts.append(docx_paragraph(text, "Heading1"))
        elif block_type == "bullet":
            body_parts.append(docx_paragraph(f"- {text}", "ListParagraph"))
        else:
            body_parts.append(docx_paragraph(text))
    document = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:body>"
        + "".join(body_parts)
        + '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1134" w:right="1134" '
        'w:bottom="1134" w:left="1134" w:header="708" w:footer="708" w:gutter="0"/></w:sectPr>'
        "</w:body></w:document>"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as docx:
        docx.writestr("[Content_Types].xml", content_types)
        docx.writestr("_rels/.rels", rels)
        docx.writestr("word/document.xml", document)
        docx.writestr("word/styles.xml", styles)


def require_fitz():
    try:
        import fitz  # type: ignore
    except ImportError as exc:
        raise ResumeRenderError("PyMuPDF (`fitz`) is required to render PDF and image artifacts") from exc
    return fitz


def wrap_text(text: str, max_chars: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    lines: list[str] = []
    current = ""
    for char in text:
        current += char
        if len(current) >= max_chars:
            lines.append(current)
            current = ""
    if current:
        lines.append(current)
    return lines


def write_pdf_and_png(blocks: list[dict[str, str]], pdf_path: Path, image_path: Path) -> int:
    fitz = require_fitz()
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    doc = fitz.open()
    page_width, page_height = 595, 842
    margin = 48
    y = margin
    page = doc.new_page(width=page_width, height=page_height)

    def add_page_if_needed(extra: float) -> None:
        nonlocal page, y
        if y + extra > page_height - margin:
            page = doc.new_page(width=page_width, height=page_height)
            y = margin

    for block in blocks:
        block_type = block["type"]
        text = block["text"]
        if block_type == "title":
            size = 20
            color = (0.05, 0.09, 0.16)
            lines = wrap_text(text, 24)
            spacing = 27
        elif block_type == "section":
            size = 13
            color = (0.10, 0.25, 0.45)
            lines = wrap_text(text, 32)
            spacing = 20
            add_page_if_needed(24)
            page.draw_line((margin, y + 4), (page_width - margin, y + 4), color=(0.75, 0.80, 0.86), width=0.6)
            y += 12
        elif block_type == "bullet":
            size = 10.5
            color = (0.12, 0.16, 0.22)
            lines = wrap_text(f"- {text}", 44)
            spacing = 16
        else:
            size = 10.5
            color = (0.12, 0.16, 0.22)
            lines = wrap_text(text, 46)
            spacing = 16
        add_page_if_needed(spacing * len(lines) + 8)
        for line in lines:
            page.insert_text((margin, y), line, fontsize=size, fontname="china-s", color=color)
            y += spacing
        y += 4

    doc.save(pdf_path)
    page_count = doc.page_count
    first_page = doc.load_page(0)
    pix = first_page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
    pix.save(image_path)
    doc.close()
    return page_count


def render_one_resume(draft_path: Path, basename: str, out_dir: Path) -> tuple[list[dict[str, str]], int]:
    blocks = parse_markdown(read_text(draft_path))
    safe_basename = sanitize_basename(basename)
    docx_path = out_dir / f"{safe_basename}.docx"
    pdf_path = out_dir / f"{safe_basename}.pdf"
    image_path = out_dir / f"{safe_basename}.png"
    write_docx(blocks, docx_path)
    page_count = write_pdf_and_png(blocks, pdf_path, image_path)
    artifacts = [
        {"format": "docx", "artifact_ref": str(docx_path), "status": "ready", "notes": "Editable Word document."},
        {"format": "pdf", "artifact_ref": str(pdf_path), "status": "ready", "notes": "Printable PDF."},
        {"format": "image", "artifact_ref": str(image_path), "status": "ready", "notes": "First-page PNG preview."},
    ]
    return artifacts, page_count


def render_all_resume_versions(args: argparse.Namespace) -> dict[str, Any]:
    if not args.decision_package:
        raise ResumeRenderError("--all-resume-versions requires --decision-package")
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    versions = extract_resume_versions_from_decision_package(load_json(args.decision_package), include_all=True)
    rendered_versions: list[dict[str, Any]] = []
    page_count = 0
    for index, version in enumerate(versions):
        draft_path = out_dir / version["markdown_filename"]
        draft_path.write_text(version["markdown"].rstrip() + "\n", encoding="utf-8")
        basename = args.basename if version["version_key"] == "resume_draft" else version["basename"]
        artifacts, version_page_count = render_one_resume(draft_path, basename, out_dir)
        if index == 0:
            page_count = version_page_count
        rendered_versions.append(
            {
                "version_key": version["version_key"],
                "source_draft_ref": str(draft_path),
                "resume_delivery_artifacts": artifacts,
                "page_count": version_page_count,
            }
        )
    primary = rendered_versions[0]
    return {
        "resume_render_response": {
            "exit_status": "success",
            "source_draft_ref": primary["source_draft_ref"],
            "source_decision_package_ref": str(args.decision_package),
            "out_dir_ref": str(out_dir),
            "resume_delivery_artifacts": primary["resume_delivery_artifacts"],
            "resume_version_artifacts": rendered_versions,
            "page_count": page_count,
        }
    }


def render(args: argparse.Namespace) -> dict[str, Any]:
    if args.all_resume_versions:
        return render_all_resume_versions(args)
    draft_path, source_decision_package_ref = resolve_draft_source(args)
    basename = sanitize_basename(args.basename)
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    artifacts, page_count = render_one_resume(draft_path, basename, out_dir)
    return {
        "resume_render_response": {
            "exit_status": "success",
            "source_draft_ref": str(draft_path),
            "source_decision_package_ref": source_decision_package_ref,
            "out_dir_ref": str(out_dir),
            "resume_delivery_artifacts": artifacts,
            "page_count": page_count,
        }
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render a resume Markdown draft to DOCX, PDF, and PNG artifacts.")
    parser.add_argument("--draft-md", type=Path)
    parser.add_argument("--decision-package", type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--basename", default="resume")
    parser.add_argument("--all-resume-versions", action="store_true")
    args = parser.parse_args(argv)
    try:
        write_json_stdout(render(args))
        return 0
    except (OSError, ResumeRenderError, RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
