import pytest

from app.services import validate_transition, InvalidStatusTransitionError

# --- 4 valid transitions ---

def test_draft_to_submitted_by_student_is_allowed():
    validate_transition("draft", "submitted", "Student")

def test_submitted_to_approved_by_supervisor_is_allowed():
    validate_transition("submitted", "approved", "Supervisor")

def test_submitted_to_needs_revision_by_supervisor_is_allowed():
    validate_transition("submitted", "needs_revision", "Supervisor")

def test_needs_revision_to_submitted_by_student_is_allowed():
    validate_transition("needs_revision", "submitted", "Student")

# --- 4 invalid transitions (invalid role and status) ---

def test_draft_to_submitted_by_supervisor_is_rejected():
    with pytest.raises(InvalidStatusTransitionError):
        validate_transition("draft", "submitted", "Supervisor")

def test_submitted_to_approved_by_student_is_rejected():
    with pytest.raises(InvalidStatusTransitionError):
        validate_transition("submitted", "approved", "Student")

def test_draft_to_approved_is_rejected():
    with pytest.raises(InvalidStatusTransitionError):
        validate_transition("draft", "approved", "Student")

def test_draft_to_needs_revision_is_rejected():
    with pytest.raises(InvalidStatusTransitionError):
        validate_transition("draft", "needs_revision", "Supervisor")


# --- full 4x4x2 matrix: every status x every target status x every role ---

ALL_STATUSES = ["draft", "submitted", "needs_revision", "approved"]
ALL_ROLES = ["Student", "Supervisor"]

HARDCODED_ALLOWED = {
    ("draft", "submitted", "Student"),
    ("submitted", "approved", "Supervisor"),
    ("submitted", "needs_revision", "Supervisor"),
    ("needs_revision", "submitted", "Student"),
}

MATRIX_CASES = [
    (current, new, role, (current, new, role) in HARDCODED_ALLOWED)
    for current in ALL_STATUSES
    for new in ALL_STATUSES
    for role in ALL_ROLES
]

@pytest.mark.parametrize("current_status, new_status, role, should_be_allowed", MATRIX_CASES)
def test_transition_matrix(current_status, new_status, role, should_be_allowed):
    if should_be_allowed:
        validate_transition(current_status, new_status, role)
    else:
        with pytest.raises(InvalidStatusTransitionError):
            validate_transition(current_status, new_status, role)

# --- approved has no outgoing transitions (explicit, all 4 targets) ---

@pytest.mark.parametrize("new_status", ["draft", "submitted", "needs_revision", "approved"])
@pytest.mark.parametrize("role", ["Student", "Supervisor"])
def test_approved_has_no_outgoing_transitions(role, new_status):
    with pytest.raises(InvalidStatusTransitionError):
        validate_transition("approved", new_status, role)