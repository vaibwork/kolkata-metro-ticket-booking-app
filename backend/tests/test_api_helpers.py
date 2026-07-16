from app.api.routes import get_all_stations, health_check


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
