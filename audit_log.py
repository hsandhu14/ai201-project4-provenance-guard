audit_log = []


def add_entry(entry):
    audit_log.append(entry)


def get_entries():
    return audit_log


def find_entry(content_id):
    for entry in audit_log:
        if entry["content_id"] == content_id:
            return entry
    return None
