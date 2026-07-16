import datetime
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db.postgres_client import get_db, Ticket
from app.db.sqlite_client import get_sqlite_conn
from app.services.unlock_service import verify_and_unlock_system
from app.services.graph_engine import get_metro_route
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional

router = APIRouter()

# --- Request/Response Pydantic Schemas ---

class StationResponseSchema(BaseModel):
    id: int
    name: str
    line: str

@router.get("/allstations", response_model=List[StationResponseSchema])
def get_all_stations():
    """
    Fetches all metro stations and their line colors from the SQLite static database.
    """
    try:
       with get_sqlite_conn() as conn:
           rows = conn.execute(
               """
               SELECT id, name, line
               FROM stations
               ORDER BY name COLLATE NOCASE, line COLLATE NOCASE
               """
           ).fetchall()
           return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch stations from database: {str(e)}")


class SystemStatusResponse(BaseModel):
    status: str
    secret_code: Optional[str] = None
    error_message: Optional[str] = None
    checks: dict
    time_diff_seconds: Optional[float] = None

class HealthResponse(BaseModel):
    api: str
    sqlite: str
    postgres: str

class TicketCreateSchema(BaseModel):
    source: str = Field(..., description="Source metro station name")
    destination: str = Field(..., description="Destination metro station name")
    fare: float = Field(..., description="Calculated ticket fare in INR")
    expires_in_minutes: int = Field(60, description="Lifespan of the ticket in minutes")

class TicketResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_number: str
    source_station: str
    destination_station: str
    fare: float
    status: str
    created_at: datetime.datetime
    expires_at: datetime.datetime

# --- API Endpoints ---

@router.get("/status", response_model=SystemStatusResponse)
def get_system_status(db: Session = Depends(get_db)):
    """
    Evaluates the metro system security check and decrypts the clearance code if database
    vault values and the background thread heartbeats are valid.
    """
    res = verify_and_unlock_system(db)
    return res

@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """
    Lightweight health check for the API, SQLite graph database, and PostgreSQL.
    """
    sqlite_status = "ok"
    postgres_status = "ok"

    try:
        with get_sqlite_conn() as conn:
            conn.execute("SELECT 1 FROM stations LIMIT 1").fetchone()
    except Exception:
        sqlite_status = "error"

    try:
        db.execute(text("SELECT 1"))
    except Exception:
        postgres_status = "error"

    return {
        "api": "ok",
        "sqlite": sqlite_status,
        "postgres": postgres_status,
    }

@router.get("/route")
def calculate_route(
    source: Optional[str] = Query(None, description="Starting station name"),
    destination: Optional[str] = Query(None, description="Destination station name"),
    source_id: Optional[int] = Query(None, description="Starting station id"),
    destination_id: Optional[int] = Query(None, description="Destination station id"),
):
    """
    Calculates the shortest metro route, fares, and travel time itinerary using Dijkstra's algorithm.
    """
    try:
        route_info = get_metro_route(source, destination, source_id, destination_id)
        return route_info
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph routing service error: {str(e)}")

@router.get("/tickets", response_model=List[TicketResponseSchema])
def list_tickets(db: Session = Depends(get_db)):
    """
    Lists all tickets registered in the database, ordered by creation date descending.
    """
    try:
        tickets = db.query(Ticket).order_by(Ticket.created_at.desc()).all()
        return tickets
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch tickets: {str(e)}")

@router.post("/tickets", response_model=TicketResponseSchema, status_code=201)
def purchase_ticket(ticket_data: TicketCreateSchema, db: Session = Depends(get_db)):
    """
    Creates a new metro ticket. Computes expiration timestamp and generates a unique ID.
    """
    try:
        now = datetime.datetime.now(datetime.timezone.utc)
        expires_at = now + datetime.timedelta(minutes=ticket_data.expires_in_minutes)
        
        # Generate clean ticket number prefixing KMETRO-
        ticket_num = f"KMETRO-{uuid.uuid4().hex[:8].upper()}"
        
        new_ticket = Ticket(
            ticket_number=ticket_num,
            source_station=ticket_data.source,
            destination_station=ticket_data.destination,
            fare=ticket_data.fare,
            status="ACTIVE",
            created_at=now,
            expires_at=expires_at
        )
        
        db.add(new_ticket)
        db.commit()
        db.refresh(new_ticket)
        return new_ticket
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to book ticket: {str(e)}")
