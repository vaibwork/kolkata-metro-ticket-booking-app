import datetime
from types import SimpleNamespace

from app.api.routes import build_ticket_validation_response, get_all_stations, health_check


class FakeDb:
    def execute(self, statement):
        return 1


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
