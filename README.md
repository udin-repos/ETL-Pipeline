# Acumen Customer Data Pipeline

A containerised data pipeline consisting of a **Flask mock server**, a **FastAPI ingestion service**, and a **PostgreSQL database**.

This project uses the modern **[dlt (Data Load Tool)](https://dlthub.com/)** library to robustly extract, normalize, and load the paginated data directly into PostgreSQL using a reliable merge/upsert strategy.

## Quick Start

Ensure you have [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.

```bash
# 1. Build and start all services in the background
docker-compose up -d --build

# 2. Check Flask mock server health
curl.exe http://localhost:5000/api/health

# 3. Trigger the ingestion pipeline (Flask → dlt → PostgreSQL)
curl.exe -X POST http://localhost:8000/api/ingest

# 4. Query the newly ingested customers from the Database
curl.exe "http://localhost:8000/api/customers?page=1&limit=5"

# 5. Fetch a single customer
curl.exe http://localhost:8000/api/customers/CUST-001

# 6. Shut down and clean up database volumes
docker-compose down -v
```

> **Note for Windows Users:** On Windows PowerShell, use `curl.exe` (with the `.exe` extension) as shown above to avoid clashes with the built-in `Invoke-WebRequest` alias. On Linux/macOS, just use `curl`.

---

## Architecture

```text
┌──────────────┐       ┌────────────────────┐       ┌────────────┐
│  Flask Mock  │──────▶│  FastAPI Pipeline  │──────▶│ PostgreSQL │
│  Server:5000 │  GET  │  (dlt ingest):8000 │ Merge │  :5432     │
└──────────────┘       └────────────────────┘       └────────────┘
```

1. **Flask Mock Server**: Simulates a legacy API by serving raw `.json` dataset via paginated endpoints.
2. **FastAPI Pipeline Service**: Exposes an ingestion endpoint that triggers a `dlt` pipeline. The pipeline handles auto-pagination, normalization, schema generation, and upserts.
3. **PostgreSQL**: Stores the cleaned data safely.

---

## Endpoints Overview

### Flask Mock Server (`:5000`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/customers?page=1&limit=10` | Fetch raw mock customer list (paginated) |
| GET | `/api/customers/{id}` | Fetch a single mock customer |

### FastAPI Pipeline Service (`:8000`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/ingest` | Triggers `dlt` to fetch data from Flask and upsert it into the DB |
| GET | `/api/customers?page=1&limit=10` | Queries the processed, paginated customer list directly from DB |
| GET | `/api/customers/{id}` | Queries a single customer from DB |

## Technology Stack
- **Python 3.10+**
- **Docker & Docker Compose**
- **FastAPI** & **SQLAlchemy** (Pipeline)
- **Flask** (Mock API)
- **dlt (Data Load Tool)** (Ingestion Logic)
- **PostgreSQL 15** 
