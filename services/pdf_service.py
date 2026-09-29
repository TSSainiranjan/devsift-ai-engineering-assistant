from io import BytesIO
from xml.sax.saxutils import escape

import fitz
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

from models.bug import BugAnalysis
from models.meeting import MeetingAnalysis
from models.phishing import PhishingAnalysis


def _text(value) -> str:
    """Convert model values to escaped PDF-safe text."""

    return escape(str(value))


def _build_report(title: str, sections: list[tuple[str, object]]) -> bytes:
    """Build a readable A4 report from titled scalar or list sections."""

    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=title,
        author="DevSift",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=21,
        leading=26,
        textColor=colors.HexColor("#111827"),
        alignment=TA_LEFT,
        spaceAfter=16,
    )
    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#2563eb"),
        spaceBefore=10,
        spaceAfter=5,
    )
    body_style = ParagraphStyle(
        "BodyText",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#27303f"),
        spaceAfter=4,
    )
    empty_style = ParagraphStyle(
        "EmptyText",
        parent=body_style,
        textColor=colors.HexColor("#6b7280"),
        italic=True,
    )

    story = [Paragraph(_text(title), title_style)]

    for heading, value in sections:
        story.append(Paragraph(_text(heading).upper(), heading_style))

        if isinstance(value, list):
            if value:
                story.append(
                    ListFlowable(
                        [
                            ListItem(Paragraph(_text(item), body_style))
                            for item in value
                        ],
                        bulletType="bullet",
                        start="circle",
                        leftIndent=16,
                    )
                )
            else:
                story.append(Paragraph("None identified.", empty_style))
        else:
            story.append(Paragraph(_text(value), body_style))

        story.append(Spacer(1, 3 * mm))

    document.build(story)
    return buffer.getvalue()


def generate_bug_analysis_pdf(analysis: BugAnalysis) -> bytes:
    """Generate a PDF report for a validated bug analysis."""

    return _build_report(
        "DevSift Bug Analysis",
        [
            ("Title", analysis.title),
            ("Description", analysis.description),
            ("Severity", analysis.severity),
            ("Category", analysis.category),
            ("Environment", analysis.environment),
            ("Reproduction Steps", analysis.reproduction_steps),
            ("Expected Behavior", analysis.expected_behavior),
            ("Actual Behavior", analysis.actual_behavior),
            ("Missing Information", analysis.missing_information),
            ("Acceptance Criteria", analysis.acceptance_criteria),
        ],
    )


def generate_meeting_analysis_pdf(analysis: MeetingAnalysis) -> bytes:
    """Generate a PDF report for validated meeting tickets."""

    sections: list[tuple[str, object]] = []

    for index, ticket in enumerate(analysis.tickets, start=1):
        sections.extend(
            [
                (f"Ticket {index}: Title", ticket.title),
                ("User Story", ticket.user_story),
                ("Description", ticket.description),
                ("Priority", ticket.priority),
                ("Acceptance Criteria", ticket.acceptance_criteria),
                ("Edge Cases", ticket.edge_cases),
                ("Dependencies", ticket.dependencies),
                ("Open Questions", ticket.open_questions),
            ]
        )

    if not sections:
        sections.append(("Result", "No actionable requirements were identified."))

    return _build_report("DevSift Meeting Tickets", sections)


def generate_phishing_analysis_pdf(analysis: PhishingAnalysis) -> bytes:
    """Generate a PDF report for a validated phishing analysis."""

    sections: list[tuple[str, object]] = [
        ("Verdict", analysis.verdict),
        ("Risk Level", analysis.risk_level),
        ("Confidence", f"{analysis.confidence}%"),
        ("Sender Origin", analysis.sender_origin),
        ("Summary", analysis.summary),
        ("Human Review Required", "Yes" if analysis.human_review_required else "No"),
        ("Sender Analysis", analysis.sender_analysis),
        ("Observed Headers", analysis.header_analysis.observed),
        ("Header Inconsistencies", analysis.header_analysis.inconsistencies),
        ("Authentication Results", analysis.header_analysis.authentication_results),
        ("Missing Header Evidence", analysis.header_analysis.missing_headers),
    ]

    for index, item in enumerate(analysis.url_analysis, start=1):
        sections.extend(
            [
                (f"URL {index}", item.url),
                (f"URL {index} Domain", item.domain or "Unavailable"),
                (f"URL {index} HTTPS", "Yes" if item.https else "No"),
                (f"URL {index} Risk", item.risk_level),
                (f"URL {index} Suspicious Indicators", item.suspicious_indicators),
            ]
        )

    for heading, items in (
        ("Social Engineering Indicators", analysis.social_engineering_indicators),
        ("Credential Harvesting Indicators", analysis.credential_harvesting_indicators),
        ("Strongest Evidence", analysis.evidence),
    ):
        sections.append(
            (
                heading,
                [
                    f"{item.finding}: {item.evidence} "
                    f"Interpretation: {item.interpretation} "
                    f"Risk contribution: {item.risk_contribution}"
                    for item in items
                ],
            )
        )

    sections.extend(
        [
            (
                "Attachment Analysis",
                [
                    f"{item.filename} ({item.mime_type}) - "
                    f"Risk: {item.risk_level}. "
                    f"Indicators: {', '.join(item.suspicious_indicators) or 'None'}"
                    for item in analysis.attachment_analysis
                ],
            ),
            ("Missing Information", analysis.missing_information),
            ("Recommended Actions", analysis.recommended_actions),
        ]
    )

    return _build_report("DevSift Phishing Investigation", sections)


def extract_text_from_pdf(pdf_file) -> str:
    """
    Extract text from an uploaded PDF file.

    Parameters:
        pdf_file: Streamlit UploadedFile object.

    Returns:
        Extracted text from all pages of the PDF.
    """

    pdf_bytes = pdf_file.read()

    document = fitz.open(
        stream=pdf_bytes,
        filetype="pdf",
    )

    extracted_text = []

    for page in document:
        page_text = page.get_text()

        if page_text.strip():
            extracted_text.append(page_text)

    document.close()

    return "\n".join(extracted_text)