from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile

from .ai import tailor_resume_summary
from .models import JobLead


def _paragraph(text: str) -> str:
    return f"<w:p><w:r><w:t>{escape(text)}</w:t></w:r></w:p>"


def _write_docx(path: Path, paragraphs: list[str]) -> None:
    body = "".join(_paragraph(paragraph) for paragraph in paragraphs)
    document_xml = (
        "<?xml version='1.0' encoding='UTF-8' standalone='yes'?>"
        "<w:document xmlns:w='http://schemas.openxmlformats.org/wordprocessingml/2006/main'>"
        f"<w:body>{body}<w:sectPr/></w:body></w:document>"
    )
    content_types = (
        "<?xml version='1.0' encoding='UTF-8'?>"
        "<Types xmlns='http://schemas.openxmlformats.org/package/2006/content-types'>"
        "<Default Extension='rels' ContentType='application/vnd.openxmlformats-package.relationships+xml'/>"
        "<Default Extension='xml' ContentType='application/xml'/>"
        "<Override PartName='/word/document.xml' ContentType='application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml'/>"
        "</Types>"
    )
    rels = (
        "<?xml version='1.0' encoding='UTF-8'?>"
        "<Relationships xmlns='http://schemas.openxmlformats.org/package/2006/relationships'>"
        "<Relationship Id='rId1' Type='http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument' Target='word/document.xml'/>"
        "</Relationships>"
    )
    with ZipFile(path, "w", ZIP_DEFLATED) as docx:
        docx.writestr("[Content_Types].xml", content_types)
        docx.writestr("_rels/.rels", rels)
        docx.writestr("word/document.xml", document_xml)


def create_tailored_resume(profile: dict, job: JobLead, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_company = "".join(ch for ch in job.company if ch.isalnum() or ch in ("-", "_")).strip() or "company"
    safe_role = "".join(ch for ch in job.category if ch.isalnum() or ch in ("-", "_")).strip() or "role"
    path = output_dir / f"resume_{safe_company}_{safe_role}.docx"

    education = profile.get("education", {})
    paragraphs = [
        profile["name"],
        profile.get("headline", ""),
        "Targeted Summary",
        tailor_resume_summary(profile, job),
        "Skills",
        *[f"• {skill}" for skill in profile.get("skills", [])],
        "Projects",
        *[f"• {project['name']} ({project['category']}): {project['evidence']}" for project in profile.get("projects", [])],
        "Education",
        f"{education.get('degree', 'BTech')} | CGPA: {education.get('cgpa', 'N/A')} | {education.get('graduation_status', '')}",
        "Note: This generated draft only reorganizes truthful profile information. Review before submitting.",
    ]
    _write_docx(path, paragraphs)
    return path
