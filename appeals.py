from audit_log import find_entry


def submit_appeal(content_id, creator_reasoning):
    entry = find_entry(content_id)

    if entry is None:
        return None

    entry["status"] = "under_review"
    entry["appeal_reasoning"] = creator_reasoning

    return entry
