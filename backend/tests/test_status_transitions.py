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

# --- Approved has no outgoing transitions ---
def test_approved_has_no_outgoing_transitions():
    with pytest.raises(InvalidStatusTransitionError):
        validate_transition("approved", "submitted", "Student")

def test_approved_to_needs_revision_is_rejected():
    with pytest.raises(InvalidStatusTransitionError):
        validate_transition("approved", "needs_revision", "Supervisor")