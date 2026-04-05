import os
from datetime import date, datetime

import dlt
import httpx

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
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return None


def upsert_customers(records: list[dict]) -> int:
    """Insert or update customer records using dlt merging."""
    if not records:
        return 0

    # Ensure dates/datetimes are parsed before ingestion
    for record in records:
        record["date_of_birth"] = _parse_date(record.get("date_of_birth"))
        record["created_at"] = _parse_datetime(record.get("created_at"))

    # Configure dlt with the existing DATABASE_URL
    # dlt will look for DESTINATION__POSTGRES__CREDENTIALS by default.
    # We can inject it into the environment here for simplicity.
    if os.getenv("DATABASE_URL") and not os.getenv("DESTINATION__POSTGRES__CREDENTIALS"):
        os.environ["DESTINATION__POSTGRES__CREDENTIALS"] = os.getenv("DATABASE_URL")

    pipeline = dlt.pipeline(
        pipeline_name="customer_ingestion",
        destination="postgres",
        dataset_name="public",
    )

    pipeline.run(
        records,
        table_name="customers",
        write_disposition="merge",
        primary_key="customer_id",
    )

    return len(records)
