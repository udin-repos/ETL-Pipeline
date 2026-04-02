from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models.customer import Customer
from services.ingestion import fetch_all_customers, upsert_customers

# ---------------------------------------------------------------------------
# App initialisation
# ---------------------------------------------------------------------------
app = FastAPI(title="Pipeline Service", version="1.0.0")


@app.on_event("startup")
def startup():
    """Create tables if they don't exist yet."""
    Base.metadata.create_all(bind=engine)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.post("/api/ingest")
def ingest(db: Session = Depends(get_db)):
    """Fetch all customers from the mock server and upsert into PostgreSQL."""
    try:
        records = fetch_all_customers()
        count = upsert_customers(db, records)
        return {"status": "success", "records_processed": count}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/customers")
def list_customers(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Return paginated customers from the database."""
    total = db.query(Customer).count()
    offset = (page - 1) * limit
    customers = db.query(Customer).offset(offset).limit(limit).all()

    return {
        "data": [_serialise(c) for c in customers],
        "total": total,
        "page": page,
        "limit": limit,
    }


@app.get("/api/customers/{customer_id}")
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    """Return a single customer or 404."""
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return _serialise(customer)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _serialise(c: Customer) -> dict:
    return {
        "customer_id": c.customer_id,
        "first_name": c.first_name,
        "last_name": c.last_name,
        "email": c.email,
        "phone": c.phone,
        "address": c.address,
        "date_of_birth": str(c.date_of_birth) if c.date_of_birth else None,
        "account_balance": float(c.account_balance) if c.account_balance else None,
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }
