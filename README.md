# DevSift - Sift the Noise. Surface the Insight.

An AI-powered engineering assistant that converts unstructured software engineering information and suspicious email content into structured, actionable engineering information.

The application provides three AI-assisted workflows:

1. Bug Report Analyzer
2. Meeting-to-Ticket Refiner
3. Phishing Email Investigator

---

## Problem Statement

Software engineering and security teams often receive information in unstructured forms such as:

- Messy bug reports
- Meeting notes
- Informal requirements
- Suspicious emails
- Raw email headers
- Email URLs and attachment metadata

Manually converting this information into structured engineering or security assessments can be time-consuming and may result in missing:

- Reproduction steps
- Acceptance criteria
- Environment information
- Dependencies
- Edge cases
- Open questions
- Important requirements
- Security indicators
- Sender/header evidence
- Suspicious URLs
- Attachment risks

DevSift automates the initial refinement and analysis process using a generative AI model.

AI-generated results are validated using Pydantic models before being displayed in the application.

---

## Features

### 1. Bug Report Analyzer

Converts an unstructured bug report into a structured engineering bug ticket.

The system extracts:

- Title
- Description
- Severity
- Category
- Environment
- Reproduction steps
- Expected behavior
- Actual behavior
- Missing information
- Acceptance criteria

The system is instructed not to invent information that is not present in the original bug report.

Bug reports can be entered as text or provided as PDF files.

---

### 2. Meeting-to-Ticket Refiner

Converts meeting notes or transcripts into one or more structured engineering tickets.

Each ticket contains:

- Title
- User story
- Description
- Acceptance criteria
- Priority
- Edge cases
- Dependencies
- Open questions

The system separates unresolved requirements into open questions instead of making unsupported assumptions.

---

### 3. Phishing Email Investigator

Analyzes suspicious emails and produces a structured security assessment.

The investigator supports:

- Pasting raw email content
- Uploading `.eml` email files

The system extracts and analyzes:

- Sender information
- Sender origin
- Recipients
- Subject
- Date
- Reply-To
- Return-Path
- Email headers
- Authentication results when explicitly available
- URLs
- URL domains
- HTTPS usage
- Suspicious URL indicators
- Social engineering indicators
- Credential-harvesting indicators
- Attachment metadata
- Evidence supporting the assessment
- Missing security information

The assessment includes:

- Verdict
- Risk level
- Confidence
- Security summary
- Recommended defensive actions
- Human/security review requirement

Possible sender-origin classifications are:

- External
- Internal
- Unknown

Possible verdicts are:

- Likely Phishing
- Suspicious
- Likely Legitimate
- Inconclusive

The system is instructed to distinguish observed evidence from interpretation and avoid treating a single indicator as proof of phishing.

---

## Phishing Security Design

The phishing workflow is designed to analyze email content without interacting with potentially malicious content.

The application:

- Parses `.eml` files locally.
- Extracts email content and metadata locally.
- Extracts URLs as strings.
- Does not visit or resolve URLs.
- Does not execute attachments.
- Does not open attachment contents for analysis.
- Analyzes attachments using metadata such as filename and MIME type.
- Treats email content as untrusted data.
- Does not follow instructions contained inside the email.
- Reports missing authentication evidence instead of inventing SPF, DKIM, or DMARC results.

The phishing analyzer is intended as a defensive analysis and triage tool. Human/security review is recommended before taking security-sensitive actions.

---

## Architecture

### General AI Processing Flow

```text
User Input
    |
    v
Streamlit UI
    |
    v
Input Processing
    |
    +--------------------+
    |                    |
    v                    v
PDF Extraction      Email Parsing
    |                    |
    +---------+----------+
              |
              v
        Prompt Template
              |
              v
       OpenRouter AI Model
              |
              v
       Structured JSON
              |
              v
       Pydantic Validation
              |
              v
        Formatted Output
```

### Bug Report Flow

```text
Bug Report / PDF
       |
       v
Input Processing
       |
       v
Bug Prompt
       |
       v
OpenRouter
       |
       v
BugAnalysis
       |
       v
Pydantic Validation
       |
       v
Structured Bug Ticket
```

### Meeting Flow

```text
Meeting Notes / Transcript
       |
       v
Meeting Prompt
       |
       v
OpenRouter
       |
       v
MeetingAnalysis
       |
       v
Pydantic Validation
       |
       v
Structured Engineering Tickets
```

### Phishing Email Flow

```text
Raw Email / .eml
       |
       v
Local Email Parser
       |
       +----------------------+
       |                      |
       v                      v
Email Body              Email Metadata
       |                      |
       +----------+-----------+
                  |
                  v
            URL Extraction
                  |
                  v
        Attachment Metadata
                  |
                  v
          Phishing Prompt
                  |
                  v
              OpenRouter
                  |
                  v
        PhishingAnalysis
                  |
                  v
        Pydantic Validation
                  |
                  v
      Security Assessment
```

---

## Technology Stack

- Python
- Streamlit
- OpenRouter API
- Pydantic
- PyMuPDF
- python-dotenv
- Python standard library `email` package
- Python logging framework

---

## Project Structure

```text
ai-engineering-ticket-assistant/
│
├── assets/
│   └── devsift_logo.png
│
├── models/
│   ├── bug.py
│   ├── meeting.py
│   └── phishing.py
│
├── prompts/
│   ├── bug_prompt.txt
│   ├── meeting_prompt.txt
│   └── phishing_prompt.txt
│
├── services/
│   ├── ai_service.py
│   ├── email_service.py
│   └── pdf_service.py
│
├── tests/
│   └── test_cases.txt
│
├── .env
├── .gitignore
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── architecture.md
├── prompt_design.md
└── ai_assistance.md
```

---

## Setup

### 1. Clone or copy the project

Open the project directory in VS Code.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

Windows:

```bash
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure the OpenRouter API key

Create a `.env` file in the project root:

```text
OPENROUTER_API_KEY=your_api_key_here
```

Do not commit the `.env` file to source control.

### 6. Run the application

```bash
streamlit run app.py
```

The application will open in the browser.

---

## Usage

### Bug Report Analyzer

1. Select `Bug Report Analyzer`.
2. Enter a bug report or upload a PDF containing a bug report.
3. Click `Analyze Bug Report`.
4. Review the generated structured ticket.
5. Verify the generated information against the original report.

---

### Meeting-to-Ticket Refiner

1. Select `Meeting-to-Ticket Refiner`.
2. Enter meeting notes or a transcript.
3. Click `Generate Tickets`.
4. Review the generated engineering tickets.
5. Verify requirements, acceptance criteria, dependencies, and open questions against the original meeting notes.

---

### Phishing Email Investigator

#### Option 1: Paste Raw Email

1. Select `Phishing Email Investigator`.
2. Select the `Paste Raw Email` tab.
3. Paste the raw email content.
4. Click `Investigate Email`.
5. Review the locally extracted email information.
6. Review the generated security assessment.

#### Option 2: Upload `.eml`

1. Select `Phishing Email Investigator`.
2. Select the `Upload .eml` tab.
3. Upload an `.eml` email file.
4. Review the locally extracted email information.
5. Click `Investigate Email`.
6. Review the generated security assessment.

The `.eml` parser extracts attachment metadata without executing or opening the attachment contents.

---

## AI Approach

The application uses dedicated prompt templates for each workflow.

The prompts instruct the model to:

- Extract information from the provided input.
- Avoid unsupported assumptions.
- Identify missing information.
- Generate structured engineering or security information.
- Follow defined severity or priority rules.
- Generate acceptance criteria.
- Preserve unresolved requirements as open questions.
- Distinguish observed security evidence from interpretation.
- Avoid treating individual phishing indicators as conclusive proof.
- Identify sender, header, URL, social-engineering, credential-harvesting, and attachment indicators.
- Provide defensive recommendations for suspicious emails.

The model response is requested as structured JSON using the Pydantic schema for the corresponding workflow.

---

## Prompt Engineering

Separate prompts are maintained for each workflow:

- `bug_prompt.txt`
- `meeting_prompt.txt`
- `phishing_prompt.txt`

This keeps the instructions specific to each task.

The prompts use techniques including:

- Role definition
- Explicit task definition
- Structured output requirements
- Evidence-based analysis
- Missing-information handling
- Rules for severity and priority
- Acceptance-criteria requirements
- Hallucination prevention
- Security-specific analysis rules
- Human-review guidance

---

## Validation

Pydantic models validate the AI-generated structured output before it is displayed by the application.

The models define the expected structure and allowed values for each workflow.

Examples include:

- Bug severity values
- Meeting ticket priority values
- Phishing verdict values
- Phishing risk levels
- Sender-origin classifications
- Confidence range from 0 to 100

This provides a validation layer between the generative AI response and the application UI.

---

## Testing

The project includes realistic test cases covering:

1. Complete bug report
2. Incomplete bug report
3. Meeting notes containing multiple requirements
4. Suspicious phishing email
5. `.eml` phishing email containing a real MIME attachment

The tests include expected behavior and manual verification criteria.

The phishing workflow was additionally tested using:

- A synthetic suspicious email
- An explicit external sender indicator
- A typosquatting domain
- A credential-harvesting URL
- A real MIME executable attachment

The phishing analyzer successfully detected the relevant security indicators during validation.

---

## Error Handling

The application handles common AI service failures including:

- API rate limits
- Temporary service unavailability
- Unavailable model configuration
- Invalid structured responses
- General analysis failures

Errors are logged using Python's logging framework and a user-friendly error message is displayed in the Streamlit interface.

---

## PDF Support

Bug reports can also be provided as PDF files.

PyMuPDF is used to extract text from uploaded PDF documents before sending the extracted content to the AI analysis workflow.

The application does not require the AI model to directly process the PDF file.

---

## Email Processing

The phishing workflow uses Python's standard `email` library to parse `.eml` files.

The parser extracts:

- Sender
- Recipients
- CC
- Subject
- Date
- Reply-To
- Return-Path
- Headers
- Email body
- URLs
- Attachment metadata

URLs are extracted without visiting them.

Attachments are analyzed using metadata such as:

- Filename
- MIME type

Attachment contents are not executed.

---

## Limitations

- Generated engineering tickets require human review before being used in a production engineering workflow.
- Phishing assessments are intended for security triage and require human/security review for security-sensitive decisions.
- The system does not directly create tickets in Jira or another issue-tracking platform.
- AI output quality depends on the quality and completeness of the provided input.
- The system does not determine missing requirements from external sources.
- The phishing analyzer cannot verify the reputation or live behavior of a URL because URLs are not visited.
- The phishing analyzer cannot determine attachment behavior because attachment contents are not executed.
- Missing SPF, DKIM, or DMARC information is reported as missing evidence rather than inferred.
- The application does not guarantee that an AI-generated security assessment is correct.

---

## Privacy and Security Considerations

Email content submitted for AI analysis may be transmitted to the configured OpenRouter API.

Users should avoid submitting confidential information such as:

- Passwords
- One-time passwords
- API keys
- Access tokens
- Financial secrets
- Other sensitive credentials

The `.eml` file is parsed locally before the extracted email information is passed to the AI analysis workflow.

The application does not visit URLs or execute email attachments.

For demonstrations and testing, synthetic emails should be preferred whenever possible.

---

## Human Review

AI-generated results are intended to assist engineering and security workflows rather than replace human decision-making.

For engineering workflows, users should verify:

- Requirements
- Severity
- Priority
- Acceptance criteria
- Dependencies
- Edge cases

For phishing investigations, users should verify:

- Sender identity
- Header evidence
- Authentication results
- URLs
- Attachments
- Security indicators
- Recommended response actions

The final decision remains with the appropriate engineer, analyst, or security team.

---

## Future Improvements

Potential future improvements include:

- Jira integration
- Ticket export
- Additional input formats
- Automated regression testing
- More engineering ticket types
- Human approval workflow
- Persistent ticket history
- Additional email authentication analysis
- More advanced attachment metadata analysis
- Enterprise security integrations
- Automated security incident workflow integration