# TESTIMONIAL

## Overall approach

I first mapped the application boundaries: React/Vite frontend, FastAPI backend, PostgreSQL for operational state, and SQLite for the static metro graph. I reviewed the SQLite schema documentation before implementing routing, then focused on the smallest changes needed to make the existing API contracts work.

## Understanding the project

The project models each station-line pair as a graph node. Regular train movement is stored in `connections`, while line transfers are stored in `interchanges`. Because interchange stations can share the same public station name across multiple lines, the route finder treats a station name as one or more possible graph nodes and chooses the fastest valid route between any matching source and destination node.

## Bugs encountered during setup

- The SQLite client constructed the database path from the Python file path and looked for `sqlite_client.py/metadatagraph.db`, which prevented SQLite access.
- The `/api/allstations` endpoint was a stub.
- The route calculation service was a stub.
- The frontend API client pointed to `http://localhost:8080/api`, while the documented backend runs on port `8000`.
- The frontend imports `lucide-react`, but the dependency was missing from `package.json`.
- The backend imports SQLAlchemy, but `SQLAlchemy` was missing from `backend/requirements.txt`.
- CORS allowed `localhost:3000` but not Vite's default `localhost:5173`.
- Local PostgreSQL was running, but the configured default credentials `postgres/postgres` were rejected on this machine.

## How I resolved those issues

- Fixed the SQLite path to use the configured `SQLITE_DB_PATH` relative to the repository root.
- Implemented `/api/allstations` using the existing SQLite `stations` table.
- Implemented Dijkstra's algorithm in the existing `get_metro_route` service using `connections` and `interchanges`.
- Preserved the existing `/api/route?source=&destination=` contract and returned the `route_summary` and `ordered_itinerary` shape expected by the frontend.
- Updated the frontend API base URL to port `8000`.
- Added `lucide-react` to frontend dependencies and `SQLAlchemy` to backend requirements.
- Added `localhost:5173` to backend CORS origins.
- Added a visible station directory with loading and error states, while keeping searchable source/destination selectors.

## Challenges faced

The main routing challenge was handling station names that exist on multiple lines, such as Park Street and Esplanade. Since the API accepts station names rather than station IDs, the backend cannot know which line the user intended. I handled that by running a multi-source Dijkstra search across all matching source nodes and stopping at the fastest matching destination node.

## Assumptions made

- Shortest route means minimum total travel time.
- Fare is accumulated only from train `connections`; interchange walking edges add time but no fare.
- Duplicate public station names should be resolved automatically to the fastest valid route.
- The existing endpoint names and response contract should remain unchanged.

## Improvements with more time

- Extend the API contract to optionally accept station IDs for unambiguous routing while keeping station-name compatibility.
- Add automated backend tests for route existence, invalid station names, duplicate station names, and fare/time totals.
- Add frontend tests around loading, route display, and API failure states.
- Improve the route UI with a compact printable/screenshot mode for very long itineraries.
- Provide a Docker Compose setup for PostgreSQL so assessment setup is reproducible.
