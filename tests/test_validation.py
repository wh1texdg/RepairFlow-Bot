from datetime import date, timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.api.schemas import RequestCreate


def valid_payload():
    return {
        "user_id": 1,
        "object_type": "apartment",
        "repair_type": "capital",
        "area": Decimal("60"),
        "city": "Moscow",
        "address": "Test street 1",
        "budget": Decimal("500000"),
        "desired_start_date": date.today() + timedelta(days=10),
    }


def test_area_must_be_positive():
    data = valid_payload()
    data["area"] = 0
    with pytest.raises(ValidationError):
        RequestCreate(**data)


def test_budget_cannot_be_negative():
    data = valid_payload()
    data["budget"] = -1
    with pytest.raises(ValidationError):
        RequestCreate(**data)


def test_start_date_cannot_be_in_past():
    data = valid_payload()
    data["desired_start_date"] = date.today() - timedelta(days=1)
    with pytest.raises(ValidationError):
        RequestCreate(**data)
