# Kolkata Metro Booking & Verification System

A full-stack technical assessment solution for a fictional Kolkata Metro route planner and ticket booking system.

The project uses:

- React + Vite frontend
- FastAPI backend
- PostgreSQL for tickets, system configuration, and worker heartbeat state
- SQLite for static metro graph metadata and vault key fragments

## Live Deployment

- Frontend: https://frontend-production-9fb5.up.railway.app
- Backend: https://backend-production-15ec.up.railway.app
- API docs: https://backend-production-15ec.up.railway.app/docs
- Public repository: https://github.com/vaibwork/kolkata-metro-ticket-booking-app

Verification code:

```text
HI-U-PASSED-THE-DEV-CHALLENGE
```

## Implemented Assessment Tasks

- Integrated the existing all-stations backend API with the frontend.
- Displayed the full metro station directory with loading and error states.
- Implemented shortest-path route finding in the existing `/api/route` endpoint.
- Preserved the original station-name API contract.
- Added optional station ID routing for unambiguous duplicate station names.
- Used the existing SQLite graph tables: `stations`, `connections`, and `interchanges`.
- Added route summaries, ordered itineraries, transfer markers, and leg-level route details.
- Added a `/api/health` endpoint for API, SQLite, and PostgreSQL readiness.
- Added focused backend tests for routing, invalid inputs, station listing, and health checks.
- Deployed the backend, frontend, and PostgreSQL database on Railway.

## Screenshots

Required assessment route screenshots are included in the repository workspace:

![Dakshineswar to VIP Bazar](screenshot-dakshineswar-vip-bazar.png)

![Park Street to Howrah](screenshot-park-street-howrah.png)

![Thakurpukur to Eco Park](screenshot-thakurpukur-eco-park.png)

## API Examples

Fetch all stations:

```bash
curl https://backend-production-15ec.up.railway.app/api/allstations
```

Find a route by station name:

```bash
curl "https://backend-production-15ec.up.railway.app/api/route?source=Park%20Street&destination=Howrah"
```

Find a route by station ID:

```bash
curl "https://backend-production-15ec.up.railway.app/api/route?source_id=51&destination_id=28"
```

Health check:

```bash
curl https://backend-production-15ec.up.railway.app/api/health
```

System verification:

```bash
curl https://backend-production-15ec.up.railway.app/api/status
```

## Route Response Shape

The route endpoint returns:

- `route_summary`: total fare, time, station count, interchange count, and resolved station IDs/lines
- `ordered_itinerary`: station-by-station display sequence for the UI
- `route_legs`: edge-level details, including train versus interchange segments

Example route leg:

```json
{
  "from_station_name": "Esplanade",
  "from_line": "Blue",
  "to_station_name": "Esplanade",
  "to_line": "Green",
  "edge_type": "interchange",
  "travel_time_minutes": 5,
  "fare_inr": 0
}
```

## Local Setup

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python -m uvicorn app.main:app --reload --port 8000
```

The backend defaults to:

```text
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/kolkata_metro
SQLITE_DB_PATH=backend/app/db/metadata_graph.db
```

If your local PostgreSQL credentials differ, create a root `.env` file and override `DATABASE_URL`.

The backend creates required operational PostgreSQL tables and seed rows at startup. The SQLite graph database is already included.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend defaults to:

```text
VITE_API_URL=http://127.0.0.1:8000/api
```

For a deployed backend, set `VITE_API_URL` before building.

## Tests

Run backend tests:

```bash
cd backend
.venv\Scripts\python -m pytest -q
```

Current coverage focuses on:

- required assessment routes
- route totals and leg counts
- duplicate station-name disambiguation through station IDs
- invalid station handling
- all-stations retrieval
- health check behavior

## Deployment Notes

Railway services:

- `backend`: FastAPI service
- `frontend`: Vite preview service serving the production build
- `Postgres`: managed Railway PostgreSQL database

The backend is configured with:

```text
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

The frontend is configured with:

```text
VITE_API_URL=https://backend-production-15ec.up.railway.app/api
```

## Important Design Notes

The SQLite schema stores each station-line pair as a distinct graph node. This is important for stations such as Park Street or Esplanade, where the same public station name can exist on multiple lines.

The API therefore supports two routing modes:

- name-based routing for backward compatibility with the assessment contract
- ID-based routing for precise production behavior

Interchange edges add walking time but do not add fare. Train connection edges add both travel time and fare.

## Documentation

See [TESTIMONIAL.md](TESTIMONIAL.md) for the implementation approach, setup issues, assumptions, and engineering tradeoffs.
