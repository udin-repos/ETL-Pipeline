# Customer Data Pipeline

A containerised data pipeline consisting of a **Flask mock server**, a **FastAPI ingestion service**, and **PostgreSQL**.

## Quick Start

```bash
# Build and start all services
docker-compose up -d --build

# Check Flask health
curl http://localhost:5000/api/health

# Browse customers (Flask)
curl "http://localhost:5000/api/customers?page=1&limit=5"

# Trigger ingestion into PostgreSQL
curl -X POST http://localhost:8000/api/ingest

# Query customers (FastAPI / DB)
curl "http://localhost:8000/api/customers?page=1&limit=5"

# Single customer
curl http://localhost:8000/api/customers/CUST-001

# Tear down
docker-compose down -v
```

## Architecture

```
┌──────────────┐       ┌───────────────────┐       ┌────────────┐
│  Flask Mock  │──────▶│  FastAPI Pipeline  │──────▶│ PostgreSQL │
│  Server:5000 │  GET  │  Service:8000      │  SQL  │  :5432     │
└──────────────┘       └───────────────────┘       └────────────┘
```

## Endpoints

### Flask Mock Server (`:5000`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/customers?page=1&limit=10` | Paginated customer list |
| GET | `/api/customers/{id}` | Single customer |

### FastAPI Pipeline Service (`:8000`)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/ingest` | Fetch from Flask → upsert into DB |
| GET | `/api/customers?page=1&limit=10` | Paginated query from DB |
| GET | `/api/customers/{id}` | Single customer from DB |
