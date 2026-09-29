from pathlib import Path

from google import genai

from config import GEMINI_API_KEY, logger
from models.bug import BugAnalysis
from models.meeting import MeetingAnalysis
from models.phishing import PhishingAnalysis


client = genai.Client(api_key=GEMINI_API_KEY)


# ============================================================
# BUG REPORT ANALYZER
# ============================================================

def load_bug_prompt() -> str:
    prompt_path = (
        Path(__file__).parent.parent
        / "prompts"
        / "bug_prompt.txt"
    )

    return prompt_path.read_text(
        encoding="utf-8"
    )


def analyze_bug_report(
    bug_report: str,
) -> BugAnalysis:

    try:

        prompt_template = load_bug_prompt()

        prompt = prompt_template.replace(
            "{BUG_REPORT}",
            bug_report,
        )

        logger.info(
            "Starting bug report analysis."
        )

        response = client.interactions.create(
            model="gemini-3.1-flash-lite",
            input=prompt,
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": BugAnalysis.model_json_schema(),
            },
        )

        if not response.output_text:

            raise ValueError(
                "Gemini returned an empty response."
            )

        result = BugAnalysis.model_validate_json(
            response.output_text
        )

        logger.info(
            "Bug report analysis completed successfully."
        )

        return result

    except Exception:

        logger.exception(
            "Bug report analysis failed."
        )

        raise


# ============================================================
# MEETING-TO-TICKET REFINER
# ============================================================

def load_meeting_prompt() -> str:
    prompt_path = (
        Path(__file__).parent.parent
        / "prompts"
        / "meeting_prompt.txt"
    )

    return prompt_path.read_text(
        encoding="utf-8"
    )

def load_phishing_prompt() -> str:
    prompt_path = (
        Path(__file__).parent.parent
        / "prompts"
        / "phishing_prompt.txt"
    )
    return prompt_path.read_text(encoding="utf-8")


def generate_meeting_tickets(
    meeting_notes: str,
) -> MeetingAnalysis:

    try:

        prompt_template = load_meeting_prompt()

        prompt = prompt_template.replace(
            "{MEETING_NOTES}",
            meeting_notes,
        )

        logger.info(
            "Starting meeting-to-ticket analysis."
        )

        response = client.interactions.create(
            model="gemini-3.1-flash-lite",
            input=prompt,
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": MeetingAnalysis.model_json_schema(),
            },
        )

        if not response.output_text:

            raise ValueError(
                "Gemini returned an empty response."
            )

        result = MeetingAnalysis.model_validate_json(
            response.output_text
        )

        logger.info(
            "Meeting-to-ticket analysis completed successfully."
        )

        return result

    except Exception:

        logger.exception(
            "Meeting-to-ticket analysis failed."
        )

        raise

def analyze_phishing_email(
    email_data: dict,
) -> PhishingAnalysis:
    try:
        prompt_template = load_phishing_prompt()

        prompt = prompt_template.replace(
            "{EMAIL_DATA}",
            str(email_data),
        )

        logger.info("Starting phishing email analysis.")

        response = client.interactions.create(
            model="gemini-3.1-flash-lite",
            input=prompt,
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": PhishingAnalysis.model_json_schema(),
            },
        )

        if not response.output_text:
            raise ValueError(
                "Gemini returned an empty response."
            )

        result = PhishingAnalysis.model_validate_json(
            response.output_text
        )

        logger.info(
            "Phishing email analysis completed successfully."
        )

        return result

    except Exception:
        logger.exception(
            "Phishing email analysis failed."
        )
        raise