import json
import os

from flask import Flask, jsonify, request

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Load customer data from JSON file
# ---------------------------------------------------------------------------
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "customers.json")

with open(DATA_PATH, "r") as f:
    CUSTOMERS: list[dict] = json.load(f)

# Build a lookup dict for O(1) access by customer_id
CUSTOMERS_BY_ID: dict[str, dict] = {c["customer_id"]: c for c in CUSTOMERS}


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"})


@app.route("/api/customers", methods=["GET"])
def list_customers():
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)

    # Clamp values
    page = max(1, page)
    limit = max(1, min(limit, 100))

    start = (page - 1) * limit
    end = start + limit

    return jsonify(
        {
            "data": CUSTOMERS[start:end],
            "total": len(CUSTOMERS),
            "page": page,
            "limit": limit,
        }
    )


@app.route("/api/customers/<customer_id>", methods=["GET"])
def get_customer(customer_id: str):
    customer = CUSTOMERS_BY_ID.get(customer_id)
    if customer is None:
        return jsonify({"error": "Customer not found"}), 404
    return jsonify(customer)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
