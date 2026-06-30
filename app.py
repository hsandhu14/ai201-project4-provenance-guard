import uuid
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from detector import stylometric_score, llm_score

app = Flask(__name__)

# Rate limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://",
)

# In-memory audit log
audit_log = []


@app.route("/")
def home():
    return {
        "message": "Provenance Guard API is running!"
    }


def get_label(attribution):
    if attribution == "likely_ai":
        return (
            "This content shows strong signs of AI generation. "
            "This does not prove misuse, but readers should know the platform "
            "detected a high likelihood of AI assistance."
        )

    elif attribution == "likely_human":
        return (
            "This content shows strong signs of human authorship. "
            "No major AI-generation indicators were detected by the system."
        )

    return (
        "The system could not confidently determine whether this content was "
        "AI-generated or human-written. Readers should treat the attribution as uncertain."
    )


@app.route("/submit", methods=["POST"])
@limiter.limit("10 per minute;100 per day")
def submit():

    data = request.get_json()

    if not data or "text" not in data or "creator_id" not in data:
        return jsonify({
            "error": "Missing required fields: text and creator_id"
        }), 400

    text = data["text"]
    creator_id = data["creator_id"]
    content_id = str(uuid.uuid4())

    # Detection signals
    stylometric = stylometric_score(text)
    llm = llm_score(text)

    # Weighted confidence
    combined_score = (stylometric * 0.4) + (llm * 0.6)
    confidence = round(combined_score, 2)

    if combined_score >= 0.70:
        attribution = "likely_ai"
    elif combined_score <= 0.40:
        attribution = "likely_human"
    else:
        attribution = "uncertain"

    label = get_label(attribution)

    log_entry = {
        "content_id": content_id,
        "creator_id": creator_id,
        "attribution": attribution,
        "confidence": confidence,
        "stylometric_score": round(stylometric, 2),
        "llm_score": round(llm, 2),
        "status": "classified",
        "appeal_reasoning": None
    }

    audit_log.append(log_entry)

    return jsonify({
        "content_id": content_id,
        "attribution": attribution,
        "confidence": confidence,
        "label": label
    })


@app.route("/appeal", methods=["POST"])
def appeal():

    data = request.get_json()

    if not data or "content_id" not in data or "creator_reasoning" not in data:
        return jsonify({
            "error": "Missing required fields: content_id and creator_reasoning"
        }), 400

    content_id = data["content_id"]
    creator_reasoning = data["creator_reasoning"]

    for entry in audit_log:
        if entry["content_id"] == content_id:

            entry["status"] = "under_review"
            entry["appeal_reasoning"] = creator_reasoning

            return jsonify({
                "message": "Appeal received successfully.",
                "content_id": content_id,
                "status": "under_review"
            })

    return jsonify({
        "error": "Content ID not found."
    }), 404


@app.route("/log", methods=["GET"])
def get_log():
    return jsonify({
        "entries": audit_log
    })


if __name__ == "__main__":
    app.run(debug=True)