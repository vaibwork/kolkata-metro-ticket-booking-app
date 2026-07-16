import heapq
from collections import defaultdict
from app.db.sqlite_client import get_sqlite_conn

def _clean_station_name(value):
    return value.strip() if value else None

def _resolve_station_ids(conn, station_name=None, station_id=None, label="Station"):
    if station_id is not None:
        row = conn.execute(
            "SELECT id FROM stations WHERE id = ?",
            (station_id,),
        ).fetchone()
        if not row:
            raise ValueError(f"{label} station not found: {station_id}")
        return [row["id"]]

    station_name = _clean_station_name(station_name)
    if not station_name:
        raise ValueError(f"{label} station name or id is required.")

    station_ids = [
        row["id"]
        for row in conn.execute(
            "SELECT id FROM stations WHERE lower(name) = lower(?)",
            (station_name,),
        )
    ]
    if not station_ids:
        raise ValueError(f"{label} station not found: {station_name}")

    return station_ids

def get_metro_route(source_name=None, destination_name=None, source_id=None, destination_id=None):
    """
    Computes the shortest route (based on travel time) between the source and 
    destination metro stations using Dijkstra's algorithm.
    Reads station, connection, and interchange graphs dynamically from SQLite.
    """
    source_name = _clean_station_name(source_name)
    destination_name = _clean_station_name(destination_name)

    if source_id is not None and destination_id is not None and source_id == destination_id:
        raise ValueError("Source and destination stations cannot be the same.")
    if source_id is None and destination_id is None and source_name and destination_name and source_name.casefold() == destination_name.casefold():
        raise ValueError("Source and destination stations cannot be the same.")

    with get_sqlite_conn() as conn:
        stations = {
            row["id"]: {
                "id": row["id"],
                "name": row["name"],
                "line": row["line"],
            }
            for row in conn.execute("SELECT id, name, line FROM stations")
        }

        source_ids = _resolve_station_ids(conn, source_name, source_id, "Source")
        destination_ids = set(_resolve_station_ids(conn, destination_name, destination_id, "Destination"))

        graph = defaultdict(list)
        for row in conn.execute(
            """
            SELECT station_a_id, station_b_id, travel_time_minutes, fare_inr
            FROM connections
            """
        ):
            graph[row["station_a_id"]].append(
                {
                    "to": row["station_b_id"],
                    "time": row["travel_time_minutes"],
                    "fare": row["fare_inr"],
                    "type": "train",
                }
            )

        for row in conn.execute(
            """
            SELECT station_from_id, station_to_id, transfer_time_minutes
            FROM interchanges
            """
        ):
            graph[row["station_from_id"]].append(
                {
                    "to": row["station_to_id"],
                    "time": row["transfer_time_minutes"],
                    "fare": 0,
                    "type": "interchange",
                }
            )

    distances = {}
    previous = {}
    queue = []

    for source_id in source_ids:
        distances[source_id] = (0, 0)
        heapq.heappush(queue, (0, 0, source_id))

    destination_id = None
    while queue:
        current_time, current_fare, station_id = heapq.heappop(queue)
        if distances.get(station_id) != (current_time, current_fare):
            continue

        if station_id in destination_ids:
            destination_id = station_id
            break

        for edge in graph.get(station_id, []):
            next_id = edge["to"]
            candidate = (
                current_time + edge["time"],
                current_fare + edge["fare"],
            )
            if candidate < distances.get(next_id, (float("inf"), float("inf"))):
                distances[next_id] = candidate
                previous[next_id] = (station_id, edge)
                heapq.heappush(queue, (candidate[0], candidate[1], next_id))

    if destination_id is None:
        raise ValueError(f"No route found between {source_name} and {destination_name}.")

    path_ids = []
    cursor = destination_id
    while cursor is not None:
        path_ids.append(cursor)
        cursor = previous.get(cursor, (None, None))[0]
    path_ids.reverse()

    itinerary = []
    route_legs = []
    interchanges_count = 0
    for index, station_id in enumerate(path_ids):
        station = stations[station_id]
        next_edge = None
        next_station = None
        if index < len(path_ids) - 1:
            _, next_edge = previous[path_ids[index + 1]]
            next_station = stations[path_ids[index + 1]]
            if next_edge["type"] == "interchange":
                interchanges_count += 1
            route_legs.append(
                {
                    "from_station_id": station["id"],
                    "from_station_name": station["name"],
                    "from_line": station["line"],
                    "to_station_id": next_station["id"],
                    "to_station_name": next_station["name"],
                    "to_line": next_station["line"],
                    "edge_type": next_edge["type"],
                    "travel_time_minutes": next_edge["time"],
                    "fare_inr": next_edge["fare"],
                }
            )

        itinerary.append(
            {
                "station_id": station["id"],
                "station_name": station["name"],
                "line": station["line"],
                "is_interchange": bool(next_edge and next_edge["type"] == "interchange"),
                "transfer_to": next_station["line"] if next_edge and next_edge["type"] == "interchange" else None,
            }
        )

    total_time, total_fare = distances[destination_id]
    return {
        "route_summary": {
            "source": stations[path_ids[0]]["name"],
            "source_station_id": stations[path_ids[0]]["id"],
            "source_line": stations[path_ids[0]]["line"],
            "destination": stations[path_ids[-1]]["name"],
            "destination_station_id": stations[path_ids[-1]]["id"],
            "destination_line": stations[path_ids[-1]]["line"],
            "total_travel_time_minutes": total_time,
            "total_fare_inr": total_fare,
            "interchanges_count": interchanges_count,
            "station_count": len(path_ids),
            "leg_count": len(route_legs),
        },
        "ordered_itinerary": itinerary,
        "route_legs": route_legs,
    }
