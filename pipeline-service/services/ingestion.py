"""Ingestion service – fetches all customers from Flask mock-server and upserts
them into PostgreSQL."""

import os
from datetime import date, datetime

import httpx
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from models.customer import Customer

MOCK_SERVER_URL = os.getenv("MOCK_SERVER_URL", "http://mock-server:5000")
PAGE_SIZE = 50  # fetch in large pages to minimise round-trips


def fetch_all_customers() -> list[dict]:
    """Auto-paginate through the Flask /api/customers endpoint."""
    all_records: list[dict] = []
    page = 1

    with httpx.Client(timeout=30) as client:
        while True:
            resp = client.get(
                f"{MOCK_SERVER_URL}/api/customers",
                params={"page": page, "limit": PAGE_SIZE},
            )
            resp.raise_for_status()
            body = resp.json()

            data = body.get("data", [])
            all_records.extend(data)

            # Stop when we've fetched everything
            if len(all_records) >= body.get("total", 0) or len(data) == 0:
                break

            page += 1

    return all_records


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


def upsert_customers(db: Session, records: list[dict]) -> int:
    """Insert or update customer records using PostgreSQL ON CONFLICT."""
    if not records:
        return 0

    for record in records:
        record["date_of_birth"] = _parse_date(record.get("date_of_birth"))
        record["created_at"] = _parse_datetime(record.get("created_at"))

    stmt = insert(Customer).values(records)
    stmt = stmt.on_conflict_do_update(
        index_elements=["customer_id"],
        set_={
            "first_name": stmt.excluded.first_name,
            "last_name": stmt.excluded.last_name,
            "email": stmt.excluded.email,
            "phone": stmt.excluded.phone,
            "address": stmt.excluded.address,
            "date_of_birth": stmt.excluded.date_of_birth,
            "account_balance": stmt.excluded.account_balance,
            "created_at": stmt.excluded.created_at,
        },
    )

    db.execute(stmt)
    db.commit()

    return len(records)
