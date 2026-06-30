# Provenance Guard

## Overview

Provenance Guard is a Flask-based backend system designed for creative platforms that want to provide transparency about whether submitted writing appears to be AI-generated, human-written, or uncertain. Instead of making absolute claims, the system combines multiple detection signals into a confidence score, presents an easy-to-understand transparency label, allows creators to appeal classifications, and records every decision in a structured audit log.

---

# Features

* Multi-signal AI attribution pipeline
* Confidence scoring using weighted detection signals
* Three transparency label variants
* Appeals workflow
* Rate limiting with Flask-Limiter
* Structured audit log
* REST API built with Flask

---

# Technologies Used

* Python
* Flask
* Groq API (Llama 3.3 70B Versatile)
* Flask-Limiter
* python-dotenv

---

# API Endpoints

## POST /submit

Accepts a text submission and returns an attribution result.

### Example Request

```json
{
  "text": "The sun dipped below the horizon, painting the sky in hues of amber and rose.",
  "creator_id": "test-user-1"
}
```

### Example Response

```json
{
  "content_id": "6cf78b71-da38-4dd9-967f-21a34a1d83af",
  "attribution": "likely_ai",
  "confidence": 0.76,
  "label": "This content shows strong signs of AI generation. This does not prove misuse, but readers should know the platform detected a high likelihood of AI assistance."
}
```

---

## POST /appeal

Allows a creator to contest a previous attribution decision.

### Example Request

```json
{
  "content_id": "6cf78b71-da38-4dd9-967f-21a34a1d83af",
  "creator_reasoning": "I wrote this myself from personal experience."
}
```

---

## GET /log

Returns all audit log entries as JSON.

---

# Detection Signals

## Signal 1 – Stylometric Heuristics

The first signal uses simple stylometric analysis to estimate whether writing resembles AI-generated content.

Metrics used:

* Average sentence length
* Vocabulary diversity (type-token ratio)

I selected these features because they are lightweight to compute and can identify writing patterns that often differ between AI-generated and human-written text.

---

## Signal 2 – Groq Llama 3.3

The second signal uses the Groq API with the Llama 3.3 70B Versatile model.

The model analyzes the submitted writing and returns a score between **0.0 and 1.0**, where higher values indicate the writing appears more likely to be AI-generated.

Using an LLM as a second signal provides contextual understanding that complements the simpler stylometric heuristics.

---

# Confidence Scoring

The final confidence score combines both detection signals.

**Formula**

* Stylometric Score: **40%**
* Groq Score: **60%**

The Groq model receives a higher weight because it evaluates broader linguistic and contextual patterns, while the stylometric signal provides an additional independent indicator.

Confidence thresholds:

| Confidence  | Attribution          |
| ----------- | -------------------- |
| 0.70 – 1.00 | Likely AI-generated  |
| 0.41 – 0.69 | Uncertain            |
| 0.00 – 0.40 | Likely Human-written |

This design intentionally supports uncertainty rather than forcing every submission into a binary classification.

---

# Example Confidence Scores

## Example 1 – High Confidence AI

Input:

> Artificial intelligence represents a transformative paradigm shift in modern society. Furthermore, stakeholders across various sectors must collaborate to ensure responsible deployment.

Example Output:

```json
{
  "attribution": "likely_ai",
  "confidence": 0.76,
  "stylometric_score": 0.70,
  "llm_score": 0.80
}
```

---

## Example 2 – Lower Confidence

Input:

> I went to the park after class and played basketball with my friends.

Example Output:

```json
{
  "attribution": "likely_human",
  "confidence": 0.32,
  "stylometric_score": 0.50,
  "llm_score": 0.20
}
```

These examples demonstrate that the system produces different confidence scores for different writing styles rather than returning a constant value.

---

# Transparency Labels

## High Confidence AI

> This content shows strong signs of AI generation. This does not prove misuse, but readers should know the platform detected a high likelihood of AI assistance.

---

## High Confidence Human

> This content shows strong signs of human authorship. No major AI-generation indicators were detected by the system.

---

## Uncertain

> The system could not confidently determine whether this content was AI-generated or human-written. Readers should treat the attribution as uncertain.

---

# Appeals Workflow

Creators may contest a classification by submitting:

* content_id
* creator_reasoning

When an appeal is received, the system:

1. Locates the matching submission.
2. Updates the submission status to **under_review**.
3. Stores the creator's reasoning.
4. Updates the audit log.

The system does not automatically reclassify content after an appeal.

---

# Rate Limiting

The `/submit` endpoint is protected using Flask-Limiter.

Limits:

* **10 requests per minute**
* **100 requests per day**

These limits allow normal creator activity while reducing automated abuse and spam attempts.

---

# Audit Log

Each submission records:

* Content ID
* Creator ID
* Attribution
* Confidence
* Stylometric score
* Groq score
* Status
* Appeal reasoning

Example:

```json
{
  "content_id": "6cf78b71-da38-4dd9-967f-21a34a1d83af",
  "creator_id": "test-user-1",
  "attribution": "likely_ai",
  "confidence": 0.76,
  "stylometric_score": 0.70,
  "llm_score": 0.80,
  "status": "classified",
  "appeal_reasoning": null
}
```

---

# Known Limitations

One limitation of this system is that highly polished human writing, such as academic papers or professional blog posts, may be classified as AI-generated because the stylometric signal favors longer sentences and higher vocabulary diversity. Likewise, lightly edited AI-generated writing may appear more human and receive a lower confidence score. Because of these limitations, Provenance Guard should be treated as a transparency tool rather than definitive proof of authorship.

---

# Spec Reflection

The project specification helped guide my implementation by emphasizing uncertainty instead of forcing binary classifications. This led me to design a weighted confidence score and three transparency label variants rather than simply labeling every submission as AI or human.

My implementation differs from what a production system would use because the audit log is currently stored in memory instead of SQLite. This simplified development and testing, but a production deployment should use persistent storage so audit records remain available after server restarts.

---

# AI Usage

### Example 1

I used AI assistance to generate the initial Flask application structure and endpoint skeletons. I reviewed and modified the generated code so it matched the project requirements, including using the required `/submit`, `/appeal`, and `/log` endpoints.

### Example 2

I used AI assistance while implementing the confidence scoring and transparency label logic. I revised the generated code to combine two independent detection signals with weighted scoring and ensured the transparency labels matched the project specification.

---

# Testing

The system was tested using Git Bash and `curl`.

Completed tests include:

* Successful submission through `/submit`
* AI-generated writing sample
* Human-written writing sample
* Appeal submission
* Audit log retrieval
* Rate limiting verification (429 responses after exceeding limits)

---

# Future Improvements

Future versions of Provenance Guard could include:

* Persistent SQLite audit logging
* A third detection signal using an ensemble approach
* Analytics dashboard showing submission trends
* Multi-modal support for image or metadata attribution
* Creator verification certificates
