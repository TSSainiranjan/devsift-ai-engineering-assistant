from pathlib import Path

from openrouter import OpenRouter

from config import OPENROUTER_API_KEY, logger
from models.bug import BugAnalysis
from models.meeting import MeetingAnalysis
from models.phishing import PhishingAnalysis


# ---------------------------------------------------------
# OPENROUTER CLIENT
# ---------------------------------------------------------

client = OpenRouter(
    api_key=OPENROUTER_API_KEY
)


# OpenRouter allows a maximum of 3 models in the
# model-level fallback array.
#
# Nemotron 3 Super has been tested successfully and
# currently provides much better response time than
# Nemotron 3.5 Lightning.
OPENROUTER_MODELS = [
    "nvidia/nemotron-3-super-120b-a12b:free",
    "nvidia/nemotron-3.5-lightning:free",
    "qwen/qwen3.8-27b:free",
]


# ---------------------------------------------------------
# BUG REPORT ANALYZER
# ---------------------------------------------------------

def load_bug_prompt() -> str:
    prompt_path = (
        Path(__file__).parent.parent
        / "prompts"
        / "bug_prompt.txt"
    )

    return prompt_path.read_text(encoding="utf-8")


def analyze_bug_report(bug_report: str) -> BugAnalysis:
    try:
        prompt_template = load_bug_prompt()

        prompt = prompt_template.replace(
            "{BUG_REPORT}",
            bug_report
        )

        logger.info(
            "Starting bug report analysis with OpenRouter."
        )

        response = client.chat.send(
            models=OPENROUTER_MODELS,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "BugAnalysis",
                    "strict": True,
                    "schema": BugAnalysis.model_json_schema(),
                },
            },
        )

        output_text = response.choices[0].message.content

        if not output_text:
            raise ValueError(
                "OpenRouter returned an empty response."
            )

        result = BugAnalysis.model_validate_json(
            output_text
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


# ---------------------------------------------------------
# MEETING-TO-TICKET REFINER
# ---------------------------------------------------------

def load_meeting_prompt() -> str:
    prompt_path = (
        Path(__file__).parent.parent
        / "prompts"
        / "meeting_prompt.txt"
    )

    return prompt_path.read_text(encoding="utf-8")


def generate_meeting_tickets(
    meeting_notes: str,
) -> MeetingAnalysis:

    try:
        prompt_template = load_meeting_prompt()

        prompt = prompt_template.replace(
            "{MEETING_NOTES}",
            meeting_notes
        )

        logger.info(
            "Starting meeting-to-ticket analysis with OpenRouter."
        )

        response = client.chat.send(
            models=OPENROUTER_MODELS,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "MeetingAnalysis",
                    "strict": True,
                    "schema": MeetingAnalysis.model_json_schema(),
                },
            },
        )

        output_text = response.choices[0].message.content

        if not output_text:
            raise ValueError(
                "OpenRouter returned an empty response."
            )

        result = MeetingAnalysis.model_validate_json(
            output_text
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


# ---------------------------------------------------------
# PHISHING EMAIL INVESTIGATOR
# ---------------------------------------------------------

def load_phishing_prompt() -> str:
    prompt_path = (
        Path(__file__).parent.parent
        / "prompts"
        / "phishing_prompt.txt"
    )

    return prompt_path.read_text(encoding="utf-8")


def analyze_phishing_email(
    email_data: dict,
) -> PhishingAnalysis:

    try:
        prompt_template = load_phishing_prompt()

        prompt = prompt_template.replace(
            "{EMAIL_DATA}",
            str(email_data)
        )

        logger.info(
            "Starting phishing email analysis with OpenRouter."
        )

        response = client.chat.send(
            models=OPENROUTER_MODELS,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "PhishingAnalysis",
                    "strict": True,
                    "schema": PhishingAnalysis.model_json_schema(),
                },
            },
        )

        output_text = response.choices[0].message.content

        if not output_text:
            raise ValueError(
                "OpenRouter returned an empty response."
            )

        result = PhishingAnalysis.model_validate_json(
            output_text
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