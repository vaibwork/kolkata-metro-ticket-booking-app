import pytest

from app.services.graph_engine import get_metro_route


def test_route_by_name_returns_required_summary_and_legs():
    route = get_metro_route("Park Street", "Howrah")

    assert route["route_summary"]["total_travel_time_minutes"] == 13
    assert route["route_summary"]["total_fare_inr"] == 15
    assert route["route_summary"]["interchanges_count"] == 1
    assert route["route_summary"]["station_count"] == 5
    assert route["route_summary"]["leg_count"] == 4
    assert len(route["route_legs"]) == 4
    assert route["route_legs"][1]["edge_type"] == "interchange"


def test_route_by_station_id_disambiguates_duplicate_names():
    route = get_metro_route(source_id=51, destination_id=28)

    assert route["route_summary"]["source"] == "Park Street"
    assert route["route_summary"]["source_line"] == "Purple"
    assert route["route_summary"]["destination"] == "Howrah"
    assert route["ordered_itinerary"][0]["station_id"] == 51


def test_unknown_station_raises_clear_error():
    with pytest.raises(ValueError, match="Source station not found"):
        get_metro_route("Not A Station", "Howrah")


def test_same_station_id_is_rejected():
    with pytest.raises(ValueError, match="cannot be the same"):
        get_metro_route(source_id=13, destination_id=13)


def test_required_assessment_routes_are_available():
    cases = [
        ("Dakshineswar", "VIP Bazar", 60, 115),
        ("Park Street", "Howrah", 13, 15),
        ("Thakurpukur", "Eco Park", 66, 130),
    ]

    for source, destination, minutes, fare in cases:
        route = get_metro_route(source, destination)
        assert route["route_summary"]["total_travel_time_minutes"] == minutes
        assert route["route_summary"]["total_fare_inr"] == fare
        assert route["ordered_itinerary"][0]["station_name"] == source
        assert route["ordered_itinerary"][-1]["station_name"] == destination
