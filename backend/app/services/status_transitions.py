class InvalidStatusTransitionError(ValueError):
    """Raised when a status transition is not allowed."""

# (current_status, new_status) -> set of roles allowed to perform it
ALLOWED_TRANSITIONS: dict[tuple[str, str], set[str]] = {
    ("draft", "submitted"): {"student"},
    ("submitted", "approved"): {"supervisor"},
    ("submitted", "needs_revision"): {"supervisor"},
    ("needs_revision", "submitted"): {"student"},
}

def validate_transition(current_status: str, new_status: str, role:str) -> None:
    """
    Validates whether a status transition is allowed for the given role.

    Raises:
        InvalidStatusTransitionError: if the transition is not defined,
            or the role is not permitted to perform it.
    """
    allowed_roles = ALLOWED_TRANSITIONS.get((current_status, new_status))

    if allowed_roles is None:
        raise InvalidStatusTransitionError(
            f"Transition from '{current_status}' to '{new_status}' is not allowed."
        )

    if role not in allowed_roles:
        raise InvalidStatusTransitionError(
            f"Role '{role}' is not allowed to transition "
            f"from '{current_status}' to '{new_status}'."
        )
