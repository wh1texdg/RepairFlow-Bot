from app.database.models.enums import RequestStatus
from app.services.request_service import ALLOWED_TRANSITIONS


def test_new_can_move_to_in_progress():
    assert RequestStatus.IN_PROGRESS in ALLOWED_TRANSITIONS[RequestStatus.NEW]


def test_completed_is_terminal():
    assert not ALLOWED_TRANSITIONS[RequestStatus.COMPLETED]
