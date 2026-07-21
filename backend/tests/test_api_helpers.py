import datetime
from types import SimpleNamespace

import pytest

from app.api.routes import build_ticket_validation_response, delete_ticket_record, get_all_stations, health_check


class FakeDb:
    def execute(self, statement):
        return 1


class FakeTicketQuery:
    def __init__(self, ticket):
        self.ticket = ticket

    def filter(self, expression):
        return self

    def first(self):
        return self.ticket


class FakeTicketDeleteDb:
    def __init__(self, ticket):
        self.ticket = ticket
        self.deleted_ticket = None
        self.committed = False

    def query(self, model):
        return FakeTicketQuery(self.ticket)

    def delete(self, ticket):
        self.deleted_ticket = ticket

    def commit(self):
        self.committed = True


def test_get_all_stations_returns_sqlite_station_directory():
    stations = get_all_stations()

    assert len(stations) >= 90
    assert {"id": 1, "name": "Dakshineswar", "line": "Blue"} in stations


def test_health_check_reports_available_dependencies():
    health = health_check(FakeDb())

    assert health == {
        "api": "ok",
        "sqlite": "ok",
        "postgres": "ok",
    }


def test_ticket_validation_grants_active_unexpired_ticket():
    now = datetime.datetime(2026, 7, 17, 12, 0, tzinfo=datetime.timezone.utc)
    ticket = SimpleNamespace(
        ticket_number="KMETRO-TEST1234",
        source_station="Park Street",
        destination_station="Howrah",
        fare=15,
        status="ACTIVE",
        expires_at=now + datetime.timedelta(minutes=10),
    )

    validation = build_ticket_validation_response(ticket, now)

    assert validation["gate_access"] == "GRANTED"
    assert validation["ticket_status"] == "ACTIVE"
    assert validation["reason"] == "Ticket is active and within the validity window."


def test_ticket_validation_denies_expired_ticket():
    now = datetime.datetime(2026, 7, 17, 12, 0, tzinfo=datetime.timezone.utc)
    ticket = SimpleNamespace(
        ticket_number="KMETRO-TEST1234",
        source_station="Park Street",
        destination_station="Howrah",
        fare=15,
        status="ACTIVE",
        expires_at=now - datetime.timedelta(seconds=1),
    )

    validation = build_ticket_validation_response(ticket, now)

    assert validation["gate_access"] == "DENIED"
    assert validation["ticket_status"] == "EXPIRED"
    assert validation["reason"] == "Ticket has expired."


def test_delete_ticket_record_deletes_existing_ticket():
    ticket = SimpleNamespace(ticket_number="KMETRO-DELETE1")
    db = FakeTicketDeleteDb(ticket)

    result = delete_ticket_record("KMETRO-DELETE1", db)

    assert result == {
        "deleted": True,
        "ticket_number": "KMETRO-DELETE1",
    }
    assert db.deleted_ticket is ticket
    assert db.committed is True


def test_delete_ticket_record_raises_for_missing_ticket():
    db = FakeTicketDeleteDb(None)

    with pytest.raises(ValueError, match="Ticket not found"):
        delete_ticket_record("KMETRO-MISSING", db)
