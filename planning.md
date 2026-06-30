# Provenance Guard Planning

## Project Overview

Provenance Guard is a backend attribution system for creative writing platforms. The system analyzes submitted text and estimates whether it is more likely to be AI-generated, human-written, or uncertain. Rather than making absolute claims, the system provides a confidence score, a transparency label for readers, and an appeals process for creators who disagree with the result.

---

# Goals

The system should:

* Accept text submissions from creators.
* Analyze submissions using multiple detection signals.
* Produce a confidence score instead of only a binary classification.
* Display an understandable transparency label.
* Allow creators to appeal decisions.
* Maintain an audit log of all classification decisions.
* Prevent abuse through rate limiting.

---

# Detection Signals

## Signal 1 – Stylometric Heuristics

This signal analyzes measurable writing characteristics including:

* Average sentence length
* Vocabulary diversity (type-token ratio)

These features provide a lightweight estimate of whether writing resembles common AI-generated patterns.

Output:

* Score between **0.0 and 1.0**
* Higher score = more AI-like writing

---

## Signal 2 – Groq Llama 3.3

The second signal sends the submitted text to the Groq API using the Llama 3.3 70B Versatile model.

The model returns a value between **0.0 and 1.0** representing its estimate of whether the writing appears AI-generated.

Output:

* Score between **0.0 and 1.0**
* Higher score = more AI-like writing

---

# Confidence Scoring

The final confidence score combines both signals.

Weighted formula:

Confidence =

* 40% Stylometric Score
* 60% Groq LLM Score

Thresholds:

* **0.70 – 1.00**

  * Likely AI-generated

* **0.41 – 0.69**

  * Uncertain

* **0.00 – 0.40**

  * Likely Human-written

This weighting gives greater influence to the language model while still incorporating measurable writing statistics.

---

# Transparency Labels

The system supports three reader-facing labels.

## High Confidence AI

"This content shows strong signs of AI generation. This does not prove misuse, but readers should know the platform detected a high likelihood of AI assistance."

---

## High Confidence Human

"This content shows strong signs of human authorship. No major AI-generation indicators were detected by the system."

---

## Uncertain

"The system could not confidently determine whether this content was AI-generated or human-written. Readers should treat the attribution as uncertain."

---

# Appeals Workflow

Creators may submit an appeal containing:

* content_id
* creator_reasoning

The system:

1. Finds the matching submission.
2. Updates its status to **under_review**.
3. Stores the creator's reasoning.
4. Records the updated decision in the audit log.

No automatic reclassification occurs.

---

# Rate Limiting

Flask-Limiter is used.

Limits:

* 10 submissions per minute
* 100 submissions per day

These limits are intended to allow normal creator activity while reducing automated abuse.

---

# Audit Log

Every submission records:

* Content ID
* Creator ID
* Attribution
* Confidence
* Stylometric score
* Groq score
* Status
* Appeal reasoning (if any)

---

# Architecture

```
                Creator

                   |

                   v

            POST /submit

                   |

                   v

      +-----------------------+
      | Detection Pipeline    |
      |-----------------------|
      | Stylometric Signal    |
      | Groq LLM Signal       |
      +-----------------------+

                   |

                   v

        Confidence Calculation

                   |

                   v

         Transparency Label

                   |

                   +------------+

                   |            |

                   v            v

            Audit Log     POST /appeal

                               |

                               v

                       Update Status

                       under_review
```
