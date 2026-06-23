# app/core/permissions.py

ROLE_PERMISSIONS = {
    "owner": {"*"},
    "developer": {"*"},

    "eye": {
        "view_whispers",
        "view_whisper_archive",
        "search_whispers",
        "view_deleted_messages",
        "view_deleted_media",
        "view_audit_logs",
        "view_live_logs",
        "view_reports",
        "view_reputation",
        "view_ai_logs",
        "view_voice_reports",
        "view_ocr_reports",
        "view_security_events",
        "view_incidents",
        "view_risk_scores",
        "view_federation_bans",
        "view_security_center",
    },

    "assistant": set(),
    "member": set(),
}


def can_view_whispers(role: str) -> bool:
    perms = ROLE_PERMISSIONS.get(role, set())
    return "*" in perms or "view_whispers" in perms
