from apps.tasks.models import Task

# Statuses a user may set by hand: everything except the system-managed OVERDUE
# (flip_overdue_tasks owns that). Derived from the model so a new lifecycle status
# is manually settable by default instead of silently rejected.
MANUAL_STATUSES = [status for status in Task.Status if status != Task.Status.OVERDUE]

ASSIGNEE_REQUIRED_ERROR_MESSAGE = "assignee_{type} is required when assignee_type is '{type}'."
ASSIGNEE_MISMATCH_ERROR_MESSAGE = "Only assignee_{type} may be set when assignee_type is '{type}'."
NOT_ALLOWED_TO_EDIT_ERROR_MESSAGE = "You are not allowed to edit or delete this task."
NOT_ALLOWED_TO_ASSIGN_ERROR_MESSAGE = "You may only create tasks assigned within your own group."
ATTACHMENT_TOO_LARGE_ERROR_MESSAGE = "Image must be 5 MB or smaller."
ATTACHMENT_INVALID_IMAGE_ERROR_MESSAGE = "Upload a valid image."
ATTACHMENT_UNSUPPORTED_FORMAT_ERROR_MESSAGE = (
    "Unsupported image format; use JPEG, PNG, GIF, or WEBP."
)
ATTACHMENT_DIMENSIONS_ERROR_MESSAGE = "Image dimensions are too large."
