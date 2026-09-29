# DevSift - Sift the Noise. Surface the Insight. — AI Assistance Documentation

## 1. Purpose

AI assistance was used during the development of DevSift to support planning, implementation, debugging, testing, security-analysis design, and documentation.

The AI assistance was used as a development aid while the final application logic, configuration, testing, and validation were reviewed and executed by the developer.

---

## 2. Areas Where AI Assistance Was Used

AI assistance was used in the following development areas:

- Project planning
- Architecture design
- Data-flow planning
- Prompt engineering
- Pydantic schema design
- Streamlit UI development
- Gemini API integration
- Error handling
- Logging
- PDF text extraction
- Email parsing
- Phishing-analysis design
- Security-oriented input handling
- Test-case design
- Manual test validation
- Documentation

---

## 3. Project Planning

AI assistance was used to break the project requirements into smaller implementation steps.

The project was divided into incremental stages so that each component could be implemented and tested before moving to the next component.

The resulting development flow included:

```text
Project Definition
        |
        v
Environment Setup
        |
        v
Dependencies
        |
        v
Streamlit UI
        |
        v
AI API Integration
        |
        v
Structured Output
        |
        v
Bug Analyzer
        |
        v
Meeting-to-Ticket Refiner
        |
        v
PDF Support
        |
        v
Error Handling + Logging
        |
        v
Phishing Email Investigator
        |
        v
Email Parsing + Security Analysis
        |
        v
Testing
        |
        v
Documentation
```

The incremental approach allowed each major feature to be implemented and verified separately.

---

## 4. Architecture Design

AI assistance was used to design the application's overall architecture.

The resulting architecture separates the application into:

- User interface
- Input processing
- Prompt templates
- AI service
- Structured output models
- Validation
- Output presentation

Additional input-processing components were introduced for the new phishing workflow:

- Email parsing
- URL extraction
- Attachment metadata extraction

This separation helps keep the application modular and easier to maintain.

---

## 5. Prompt Engineering

AI assistance was used to design and refine the prompts for the three AI workflows.

Three separate prompt files were created:

```text
prompts/

├── bug_prompt.txt
├── meeting_prompt.txt
└── phishing_prompt.txt
```

The prompts were designed to:

- Define the AI's role.
- Clearly describe the task.
- Restrict the model to information contained in the input.
- Reduce hallucination.
- Identify missing information.
- Apply explicit severity and priority rules.
- Generate acceptance criteria.
- Preserve unresolved requirements as open questions.
- Produce output matching the required schema.
- Distinguish observed evidence from interpretation in security analysis.
- Prevent the model from treating untrusted email instructions as instructions to follow.

The phishing prompt additionally includes rules for:

- Sender-origin classification.
- Header analysis.
- Authentication evidence.
- URL analysis.
- Social-engineering indicators.
- Credential-harvesting indicators.
- Attachment metadata.
- Recommended defensive actions.
- Human/security review.

The prompts were subsequently tested using realistic engineering and security inputs.

---

## 6. Structured Output Design

AI assistance was used to determine the structured information that should be produced by each workflow.

### Bug Analysis

The `BugAnalysis` model contains:

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

### Meeting Analysis

The `MeetingAnalysis` model contains engineering tickets with:

- Title
- User story
- Description
- Acceptance criteria
- Priority
- Edge cases
- Dependencies
- Open questions

### Phishing Analysis

The `PhishingAnalysis` model contains:

- Verdict
- Risk level
- Confidence
- Sender origin
- Summary
- Sender analysis
- Header analysis
- URL analysis
- Social-engineering indicators
- Credential-harvesting indicators
- Attachment analysis
- Evidence
- Missing information
- Recommended actions
- Human-review requirement

The phishing workflow also uses structured nested models for:

```text
EvidenceItem
URLAnalysis
HeaderAnalysis
AttachmentAnalysis
```

Pydantic was used to validate the AI-generated structured output.

---

## 7. Gemini API Integration

AI assistance was used while implementing the integration between the application and the Google Gemini API.

The integration was designed so that:

```text
Application
     |
     v
Prompt
     |
     v
Gemini API
     |
     v
Structured JSON
     |
     v
Pydantic Validation
     |
     v
Application Output
```

The same AI service layer is used for the engineering and phishing workflows.

The Gemini API key is stored in an environment variable rather than being hard-coded into the application.

The final application uses structured response schemas derived from the corresponding Pydantic models.

---

## 8. Debugging and Error Handling

AI assistance was used to diagnose and resolve implementation issues during development.

Examples of issues handled during development included:

- AI provider/API availability issues.
- API rate-limit responses.
- Temporary AI service availability errors.
- Model configuration errors.
- Structured response formatting issues.
- Pydantic validation issues.
- Import and application integration issues.
- Email parsing and attachment-detection behavior.

The final application includes user-facing error handling for common AI service failures.

The application also logs exceptions to support diagnosis during development.

---

## 9. Logging

AI assistance was used to add logging to the AI service layer.

The application logs important processing events such as:

```text
Starting bug report analysis.

Bug report analysis completed successfully.

Starting meeting-to-ticket analysis.

Meeting-to-ticket analysis completed successfully.

Starting phishing email analysis.

Phishing email analysis completed successfully.
```

Exceptions are also logged so that failures can be diagnosed during development.

---

## 10. PDF Processing

AI assistance was used to design the PDF input workflow for bug reports.

The application uses PyMuPDF to:

1. Receive an uploaded PDF.
2. Read the PDF bytes.
3. Extract text from its pages.
4. Combine the extracted text.
5. Pass the extracted content to the bug analysis workflow.

The PDF processing logic is separated into:

```text
services/pdf_service.py
```

The PDF file itself is not directly sent to the AI model. Text is extracted locally first.

---

## 11. Email Parsing and Phishing Analysis

AI assistance was used to design the email-processing workflow for the Phishing Email Investigator.

The application uses Python's standard `email` library to parse `.eml` files.

The parser extracts:

- Sender
- Recipients
- CC
- Subject
- Date
- Reply-To
- Return-Path
- Email headers
- Email body
- URLs
- Attachment metadata

The workflow was designed with defensive handling of potentially malicious email content.

The application:

- Treats email content as untrusted data.
- Does not follow instructions contained in the email.
- Does not visit URLs.
- Does not resolve URLs.
- Does not execute attachments.
- Does not open attachment contents for analysis.
- Uses attachment metadata such as filename and MIME type.
- Passes the extracted information to the phishing-analysis prompt.

This allows an attachment such as:

```text
invoice.exe
```

to be identified as a potentially suspicious executable attachment without executing the file.

---

## 12. Phishing Security Analysis Design

AI assistance was used to design the structured phishing-analysis workflow.

The workflow was designed to analyze multiple categories of evidence independently:

- Sender
- Sender origin
- Headers
- Authentication evidence
- URLs
- Social engineering
- Credential harvesting
- Attachments
- Strongest evidence
- Missing information

The prompt was designed to prevent the AI from treating one indicator as conclusive proof of phishing.

For example:

```text
External sender
        !=
Automatically phishing
```

The sender-origin classification is therefore kept separate from the overall verdict.

The phishing workflow also distinguishes between observed evidence and interpretation.

For example, a lookalike domain can be identified as observed evidence, while the potential impersonation risk is treated as an interpretation based on that evidence.

---

## 13. Testing

AI assistance was used to create realistic test scenarios for the application.

The engineering test suite contains:

### Test Case 1

A complete bug report containing:

- Failure condition
- Environment
- Impact
- Reproduction information

### Test Case 2

An incomplete bug report designed to test whether the AI:

- Detects missing information.
- Avoids inventing environment details.
- Avoids inventing technical causes.
- Avoids unsupported severity classification.

### Test Case 3

Meeting notes containing:

- A feature requirement.
- Authentication failure handling.
- A dependency.
- An existing-login compatibility requirement.
- An unresolved decision.

The phishing workflow was additionally tested using synthetic security inputs.

### Phishing Test

The test email contained:

- An explicit external sender indicator.
- A suspicious lookalike domain.
- A suspicious verification URL.
- A request for username and password.
- A real MIME attachment named `invoice.exe`.

The phishing workflow was tested through both:

- Pasted raw email input.
- `.eml` file upload.

A separate `.eml` test confirmed that the application correctly detects a real MIME attachment rather than treating text such as `Attachment: invoice.exe` in the email body as an actual attachment.

The generated outputs were manually reviewed against the expected behavior defined for each test.

---

## 14. Human Verification

AI-generated content was not treated as automatically correct.

The development process included manual verification of:

### Engineering Workflows

- Generated ticket structure.
- Severity and priority.
- Extracted environment information.
- Reproduction steps.
- Acceptance criteria.
- Missing information.
- Dependencies.
- Open questions.
- Unsupported information.

### Phishing Workflow

- Sender origin.
- Sender analysis.
- Header observations.
- Authentication evidence.
- URL analysis.
- Social-engineering indicators.
- Credential-harvesting indicators.
- Attachment analysis.
- Strongest evidence.
- Missing information.
- Recommended actions.
- Human-review requirement.

The final workflow therefore includes human review:

```text
AI Generation
      |
      v
Schema Validation
      |
      v
Human Verification
      |
      v
Engineering / Security Use
```

---

## 15. Development Responsibility

AI assistance was used as a development support tool.

The developer remained responsible for:

- Selecting the project scope.
- Reviewing generated code and suggestions.
- Configuring the development environment.
- Managing the Gemini API key.
- Running the application.
- Testing the implementation.
- Reviewing AI-generated outputs.
- Validating the final behavior.
- Making implementation decisions.
- Verifying the phishing-analysis workflow.
- Ensuring potentially malicious email content was not executed during testing.

AI-generated suggestions were reviewed and adapted to the requirements of the project rather than being accepted blindly.

---

## 16. Summary

AI assistance contributed to several stages of the project:

```text
Planning
   |
   v
Architecture
   |
   v
Implementation
   |
   v
Prompt Engineering
   |
   v
Security Workflow Design
   |
   v
Debugging
   |
   v
Testing
   |
   v
Documentation
```

The final application combines AI-assisted development with explicit engineering and security controls such as:

- Structured schemas
- Prompt constraints
- Anti-hallucination rules
- Local PDF processing
- Local email parsing
- Safe URL handling
- Safe attachment handling
- Error handling
- Logging
- Testing
- Human verification

AI assistance supported the development process, while the developer remained responsible for implementation, testing, validation, and final project decisions.