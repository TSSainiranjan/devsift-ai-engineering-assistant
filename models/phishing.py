from typing import Literal

from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    finding: str = Field(
        description="Short name of the observed security finding."
    )

    evidence: str = Field(
        description="Specific evidence observed in the email."
    )

    interpretation: str = Field(
        description="What the observed evidence may indicate."
    )

    risk_contribution: Literal["Low", "Medium", "High"] = Field(
        description="How much this finding contributes to phishing risk."
    )


class URLAnalysis(BaseModel):
    url: str = Field(
        description="The URL exactly as extracted from the email."
    )

    domain: str = Field(
        description="Domain extracted from the URL, or empty if unavailable."
    )

    https: bool = Field(
        description="Whether the URL uses HTTPS."
    )

    suspicious_indicators: list[str] = Field(
        default_factory=list,
        description="Observed suspicious URL characteristics."
    )

    risk_level: Literal["Low", "Medium", "High"] = Field(
        description="Risk level for this URL based only on observed evidence."
    )


class HeaderAnalysis(BaseModel):
    observed: list[str] = Field(
        default_factory=list,
        description="Important header observations."
    )

    inconsistencies: list[str] = Field(
        default_factory=list,
        description="Observed inconsistencies between email headers."
    )

    authentication_results: list[str] = Field(
        default_factory=list,
        description="Explicit SPF, DKIM, or DMARC results found in the input."
    )

    missing_headers: list[str] = Field(
        default_factory=list,
        description="Important headers or authentication evidence not available."
    )


class AttachmentAnalysis(BaseModel):
    filename: str = Field(
        description="Attachment filename."
    )

    mime_type: str = Field(
        description="Attachment MIME type."
    )

    suspicious_indicators: list[str] = Field(
        default_factory=list,
        description="Metadata-based attachment risk indicators."
    )

    risk_level: Literal["Low", "Medium", "High"] = Field(
        description="Risk level based only on attachment metadata."
    )


class PhishingAnalysis(BaseModel):
    verdict: Literal[
        "Likely Phishing",
        "Suspicious",
        "Likely Legitimate",
        "Inconclusive",
    ] = Field(
        description="Overall phishing assessment based on available evidence."
    )

    risk_level: Literal[
        "Low",
        "Medium",
        "High",
        "Critical",
    ] = Field(
        description="Overall security risk level."
    )

    confidence: int = Field(
        ge=0,
        le=100,
        description="Confidence in the assessment from 0 to 100."
    )

    sender_origin: Literal[
        "External",
        "Internal",
        "Unknown",
    ] = Field(
        description=(
            "Whether the available evidence explicitly indicates "
            "that the email is external, internal, or unknown."
        )
    )

    summary: str = Field(
        description="Concise evidence-based summary of the assessment."
    )

    sender_analysis: list[str] = Field(
        default_factory=list,
        description="Observed sender, domain, or impersonation indicators."
    )

    header_analysis: HeaderAnalysis = Field(
        description="Analysis of available email headers and authentication evidence."
    )

    url_analysis: list[URLAnalysis] = Field(
        default_factory=list,
        description="Analysis of URLs extracted from the email."
    )

    social_engineering_indicators: list[EvidenceItem] = Field(
        default_factory=list,
        description="Evidence-backed social engineering indicators."
    )

    credential_harvesting_indicators: list[EvidenceItem] = Field(
        default_factory=list,
        description="Evidence-backed credential harvesting indicators."
    )

    attachment_analysis: list[AttachmentAnalysis] = Field(
        default_factory=list,
        description="Safe metadata-based analysis of attachments."
    )

    evidence: list[EvidenceItem] = Field(
        default_factory=list,
        description="Strongest evidence supporting the assessment."
    )

    missing_information: list[str] = Field(
        default_factory=list,
        description="Important evidence unavailable to the analysis."
    )

    recommended_actions: list[str] = Field(
        default_factory=list,
        description="Safe defensive actions for a user or security analyst."
    )

    human_review_required: bool = Field(
        description="Whether a human/security analyst should review the result."
    )