from email import policy
from email.parser import BytesParser
from email.message import EmailMessage
from email.utils import getaddresses
from html import unescape
from pathlib import Path
import re


URL_PATTERN = re.compile(
    r"https?://[^\s<>\"]+",
    re.IGNORECASE,
)


def _clean_html(html_content: str) -> str:
    """
    Convert basic HTML email content into readable text.

    This function does not execute JavaScript or load external
    resources. It only removes HTML tags and decodes entities.
    """
    html_content = re.sub(
        r"<script\b[^>]*>.*?</script>",
        "",
        html_content,
        flags=re.IGNORECASE | re.DOTALL,
    )

    html_content = re.sub(
        r"<style\b[^>]*>.*?</style>",
        "",
        html_content,
        flags=re.IGNORECASE | re.DOTALL,
    )

    text = re.sub(r"<[^>]+>", " ", html_content)
    text = unescape(text)

    return re.sub(r"\s+", " ", text).strip()


def _extract_body(message: EmailMessage) -> str:
    """
    Extract readable text from an email message.

    Preference:
    1. text/plain
    2. text/html converted to plain text

    Attachments are not opened or executed.
    """
    plain_parts = []
    html_parts = []

    if message.is_multipart():
        for part in message.walk():
            content_type = part.get_content_type()
            disposition = part.get_content_disposition()

            if disposition == "attachment":
                continue

            if content_type == "text/plain":
                try:
                    content = part.get_content()
                    if content.strip():
                        plain_parts.append(content)
                except Exception:
                    continue

            elif content_type == "text/html":
                try:
                    content = part.get_content()
                    if content.strip():
                        html_parts.append(_clean_html(content))
                except Exception:
                    continue
    else:
        content_type = message.get_content_type()

        try:
            content = message.get_content()
        except Exception:
            content = ""

        if content_type == "text/plain":
            plain_parts.append(content)

        elif content_type == "text/html":
            html_parts.append(_clean_html(content))

    if plain_parts:
        return "\n\n".join(plain_parts).strip()

    if html_parts:
        return "\n\n".join(html_parts).strip()

    return ""


def _extract_urls(text: str) -> list[str]:
    """
    Extract HTTP/HTTPS URLs from text.

    URLs are only extracted as strings.
    They are never visited or requested.
    """
    urls = URL_PATTERN.findall(text)

    cleaned_urls = []

    for url in urls:
        url = url.rstrip(".,;:!?)]}>")

        if url not in cleaned_urls:
            cleaned_urls.append(url)

    return cleaned_urls


def _extract_attachments(
    message: EmailMessage,
) -> list[dict[str, str]]:
    """
    Extract attachment metadata only.

    Attachment contents are never opened or executed.
    """
    attachments = []

    for part in message.walk():
        if part.get_content_disposition() != "attachment":
            continue

        filename = part.get_filename() or "unnamed_attachment"
        mime_type = part.get_content_type()

        attachments.append(
            {
                "filename": filename,
                "mime_type": mime_type,
            }
        )

    return attachments


def _extract_addresses(header_value: str | None) -> list[str]:
    """
    Extract email addresses from a header.
    """
    if not header_value:
        return []

    addresses = getaddresses([header_value])

    return [
        address
        for _, address in addresses
        if address
    ]


def parse_eml_file(eml_file) -> dict:
    """
    Parse an uploaded .eml file locally.

    The function extracts email metadata, headers, body text,
    URLs, and attachment metadata.

    No URLs are visited.
    No attachments are executed.
    No network requests are made.
    """
    file_bytes = eml_file.read()

    message = BytesParser(
        policy=policy.default
    ).parsebytes(file_bytes)

    body = _extract_body(message)

    headers = {
        key: str(value)
        for key, value in message.items()
    }

    urls = _extract_urls(body)

    attachments = _extract_attachments(message)

    parsed_email = {
        "sender": str(message.get("From", "")),
        "recipients": _extract_addresses(
            message.get("To")
        ),
        "cc": _extract_addresses(
            message.get("Cc")
        ),
        "subject": str(message.get("Subject", "")),
        "date": str(message.get("Date", "")),
        "reply_to": str(message.get("Reply-To", "")),
        "return_path": str(message.get("Return-Path", "")),
        "headers": headers,
        "body": body,
        "urls": urls,
        "attachments": attachments,
        "filename": Path(
            getattr(eml_file, "name", "uploaded_email.eml")
        ).name,
    }

    return parsed_email