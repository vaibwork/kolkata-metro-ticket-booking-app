import heapq
from collections import defaultdict
from app.db.sqlite_client import get_sqlite_conn

def get_metro_route(source_name: str, destination_name: str):
    """
    Computes the shortest route (based on travel time) between the source and 
    destination metro stations using Dijkstra's algorithm.
    Reads station, connection, and interchange graphs dynamically from SQLite.
    """
    source_name = source_name.strip()
    destination_name = destination_name.strip()

    if not source_name or not destination_name:
        raise ValueError("Source and destination station names are required.")
    if source_name.casefold() == destination_name.casefold():
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

        source_ids = [
            row["id"]
            for row in conn.execute(
                "SELECT id FROM stations WHERE lower(name) = lower(?)",
                (source_name,),
            )
        ]
        destination_ids = {
            row["id"]
            for row in conn.execute(
                "SELECT id FROM stations WHERE lower(name) = lower(?)",
                (destination_name,),
            )
        }

        if not source_ids:
            raise ValueError(f"Source station not found: {source_name}")
        if not destination_ids:
            raise ValueError(f"Destination station not found: {destination_name}")

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
            "destination": stations[path_ids[-1]]["name"],
            "total_travel_time_minutes": total_time,
            "total_fare_inr": total_fare,
            "interchanges_count": interchanges_count,
            "station_count": len(path_ids),
        },
        "ordered_itinerary": itinerary,
    }
