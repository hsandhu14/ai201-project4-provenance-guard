# ai201-project4-provenance-guard
# Provenance Guard

## Overview

Provenance Guard is a Flask-based backend system that helps creative platforms provide transparency about whether submitted writing appears to be AI-generated, human-written, or uncertain. The system combines multiple detection signals into a confidence score, generates a reader-friendly transparency label, allows creators to appeal classifications, and records every decision in a structured audit log.

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

# Technologies

* Python
* Flask
* Groq API (Llama 3.3 70B Versatile)
* Flask-Limiter
* python-dotenv

---

# API Endpoints

## POST /submit

Submits writing for attribution analysis.

Example request:

```json
{
  "text": "The sun dipped below the horizon, painting the sky in hues of amber and rose.",
  "creator_id": "test-user-1"
}
```

Example response:

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

Allows a creator to contest a classification.

Example request:

```json
{
  "content_id": "6cf78b71-da38-4dd9-967f-21a34a1d83af",
  "creator_reasoning": "I wrote this myself from personal experience."
}
```

---

## GET /log

Returns the current audit log entries.

---

# Detection Signals

## Signal 1 — Stylometric Heuristics

The first signal measures:

* Average sentence length
* Vocabulary diversity (type-token ratio)

These characteristics are commonly used in stylometric analysis to identify writing patterns.

---

## Signal 2 — Groq Llama 3.3

The second signal uses the Groq API with the Llama 3.3 70B Versatile model.

The model returns a value between **0.0 and 1.0** indicating how AI-generated the writing appears.

---

# Confidence Scoring

The final confidence score is computed using:

* 40% Stylometric Score
* 60% Groq Score

Thresholds:

| Confidence  | Attribution          |
| ----------- | -------------------- |
| 0.70 – 1.00 | Likely AI-generated  |
| 0.41 – 0.69 | Uncertain            |
| 0.00 – 0.40 | Likely Human-written |

The language model receives a higher weight because it captures broader contextual patterns than the handcrafted stylometric features.

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

Creators may appeal a classification by submitting:

* content_id
* creator_reasoning

The system:

1. Finds the original submission.
2. Updates the submission status to **under_review**.
3. Stores the creator's reasoning.
4. Records the updated information in the audit log.

No automatic reclassification is performed.

---

# Rate Limiting

The submission endpoint is protected with Flask-Limiter.

Configured limits:

* 10 requests per minute
* 100 requests per day

These values were selected because they allow normal creator activity while reducing automated abuse and spam.

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

# Testing

The API was tested using Git Bash and `curl`.

Tests performed:

* Successful content submission
* Human-written examples
* AI-generated examples
* Appeal submission
* Audit log retrieval
* Rate limiting (429 responses after exceeding limits)

---

# Future Improvements

* Add a third detection signal for an ensemble model.
* Store the audit log in SQLite instead of memory.
* Build a web dashboard for analytics.
* Support additional content types such as images.
