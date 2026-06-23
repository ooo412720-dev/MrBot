from app.core.permissions import (
    can_view_whispers
)

def can_read_whisper(
        viewer_role,
        sender_id,
        target_id,
        viewer_id
):

    if viewer_id == sender_id:
        return True

    if viewer_id == target_id:
        return True

    if can_view_whispers(viewer_role):
        return True

    return False